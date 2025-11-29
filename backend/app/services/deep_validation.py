"""
Deep Terraform Validation Service

This module performs comprehensive validation beyond syntax checking by
actually running 'terraform plan' to verify infrastructure dependencies,
resource counts, and provider configurations.

Why Deep Validation?
- Syntax validation catches parse errors but not logic errors
- terraform plan validates resource dependencies and provider compatibility
- Resource counting prevents incomplete infrastructure (e.g., VPC without cluster)
"""

import subprocess
import tempfile
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def deep_validate_terraform(terraform_code: str, user_prompt: str) -> Dict[str, Any]:
    """
    Perform deep validation using terraform plan to check infrastructure completeness.
    
    This function:
    1. Creates a temporary directory
    2. Writes Terraform code to main.tf
    3. Runs terraform init
    4. Runs terraform validate (syntax)
    5. Runs terraform plan (dependencies + resource count)
    6. Verifies resource counts against complexity thresholds
    
    Args:
        terraform_code: Generated Terraform HCL code
        user_prompt: Original user request for context
        
    Returns:
        Dictionary with:
            - error: None if validation passed, error message if failed
            - planned_resources: Number of resources that would be created
            - resource_details: List of resources from plan
    """
    temp_dir = None
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="infragenie_deep_validation_")
        logger.info(f"Created temp directory: {temp_dir}")
        
        # Write Terraform code
        main_tf_path = os.path.join(temp_dir, "main.tf")
        with open(main_tf_path, "w") as f:
            f.write(terraform_code)
        
        logger.info("Wrote Terraform code to main.tf")
        
        # Step 1: terraform init
        logger.info("Running terraform init...")
        init_result = subprocess.run(
            ["terraform", "init", "-no-color"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if init_result.returncode != 0:
            error_msg = f"terraform init failed: {init_result.stderr[:500]}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "planned_resources": 0,
                "resource_details": []
            }
        
        logger.info("✓ terraform init succeeded")
        
        # Step 2: terraform validate (JSON output)
        logger.info("Running terraform validate...")
        validate_result = subprocess.run(
            ["terraform", "validate", "-json"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if validate_result.returncode != 0:
            try:
                validate_json = json.loads(validate_result.stdout)
                error_msg = validate_json.get("error_message", validate_result.stderr[:500])
            except:
                error_msg = f"terraform validate failed: {validate_result.stderr[:500]}"
            
            logger.error(error_msg)
            return {
                "error": error_msg,
                "planned_resources": 0,
                "resource_details": []
            }
        
        logger.info("✓ terraform validate succeeded")
        
        # Step 3: terraform plan
        logger.info("Running terraform plan...")
        plan_file = os.path.join(temp_dir, "tfplan")
        
        plan_result = subprocess.run(
            ["terraform", "plan", "-out", plan_file, "-no-color"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if plan_result.returncode != 0:
            error_msg = f"terraform plan failed: {plan_result.stderr[:500]}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "planned_resources": 0,
                "resource_details": []
            }
        
        logger.info("✓ terraform plan succeeded")
        
        # Step 4: Parse plan output to count resources
        logger.info("Parsing plan output...")
        show_result = subprocess.run(
            ["terraform", "show", "-json", plan_file],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if show_result.returncode != 0:
            logger.warning("Failed to parse plan JSON, using fallback counting")
            planned_resources = _count_resources_from_text(plan_result.stdout)
            resource_details = []
        else:
            try:
                plan_json = json.loads(show_result.stdout)
                resource_changes = plan_json.get("resource_changes", [])
                
                # Count resources that will be created
                create_actions = [r for r in resource_changes if "create" in r.get("change", {}).get("actions", [])]
                planned_resources = len(create_actions)
                
                # Extract resource details
                resource_details = [
                    {
                        "type": r.get("type", "unknown"),
                        "name": r.get("name", "unknown"),
                        "address": r.get("address", "unknown")
                    }
                    for r in create_actions
                ]
                
                logger.info(f"Plan will create {planned_resources} resources")
                for detail in resource_details[:10]:  # Log first 10
                    logger.debug(f"  - {detail['type']}.{detail['name']}")
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse plan JSON")
                planned_resources = _count_resources_from_text(plan_result.stdout)
                resource_details = []
        
        # Step 5: Sanity check resource counts against user intent
        error = _validate_resource_count(user_prompt, planned_resources)
        
        if error:
            logger.warning(f"Resource count validation failed: {error}")
            return {
                "error": error,
                "planned_resources": planned_resources,
                "resource_details": resource_details
            }
        
        # All validations passed
        logger.info(f"✓ Deep validation passed: {planned_resources} resources will be created")
        return {
            "error": None,
            "planned_resources": planned_resources,
            "resource_details": resource_details
        }
    
    except subprocess.TimeoutExpired as e:
        error_msg = f"Terraform command timed out: {e.cmd}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "planned_resources": 0,
            "resource_details": []
        }
    
    except Exception as e:
        error_msg = f"Deep validation error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "planned_resources": 0,
            "resource_details": []
        }
    
    finally:
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")


def _count_resources_from_text(plan_output: str) -> int:
    """
    Fallback method to count resources from plan text output.
    
    Looks for lines like "Plan: 5 to add, 0 to change, 0 to destroy."
    """
    import re
    
    match = re.search(r'Plan:\s*(\d+)\s*to add', plan_output)
    if match:
        count = int(match.group(1))
        logger.info(f"Extracted resource count from text: {count}")
        return count
    
    logger.warning("Could not extract resource count from plan output")
    return 0


def _validate_resource_count(user_prompt: str, resource_count: int) -> Optional[str]:
    """
    Validate that resource count is reasonable for the requested infrastructure.
    
    Args:
        user_prompt: Original user request
        resource_count: Number of resources from terraform plan
        
    Returns:
        Error message if count is too low, None if acceptable
    """
    prompt_lower = user_prompt.lower()
    
    # Kubernetes cluster should have many resources
    if any(keyword in prompt_lower for keyword in ["kubernetes", "k8s", "eks", "aks", "gke"]):
        if resource_count < 8:
            return f"Incomplete Kubernetes infrastructure: Only {resource_count} resources (need 8+ for cluster with networking, IAM, and node groups)"
    
    # Database infrastructure
    elif any(keyword in prompt_lower for keyword in ["database", "rds", "postgresql", "mysql", "sql"]):
        if resource_count < 3:
            return f"Incomplete database infrastructure: Only {resource_count} resources (need 3+ for DB instance, subnet group, and security group)"
    
    # Load balancer
    elif any(keyword in prompt_lower for keyword in ["load balancer", "alb", "nlb", "elb"]):
        if resource_count < 4:
            return f"Incomplete load balancer setup: Only {resource_count} resources (need 4+ for LB, target groups, listeners, and health checks)"
    
    # Generic check: any infrastructure should have at least 2 resources
    if resource_count < 2:
        return f"Infrastructure appears incomplete: Only {resource_count} resource(s)"
    
    # Passed all checks
    return None


def deep_validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node wrapper for deep Terraform validation.
    
    This is the entry point called by the workflow graph.
    """
    from app.core.state import AgentState
    
    logger.info("=" * 60)
    logger.info("DEEP VALIDATOR NODE: Running terraform plan validation")
    
    terraform_code = state.get("terraform_code", "")
    user_prompt = state.get("user_prompt", "")
    
    if not terraform_code:
        return {
            "validation_error": "No Terraform code to validate",
            "planned_resources": 0,
            "logs": state.get("logs", []) + ["❌ Deep validation skipped: No code"]
        }
    
    # Run deep validation
    result = deep_validate_terraform(terraform_code, user_prompt)
    
    error = result.get("error")
    planned_resources = result.get("planned_resources", 0)
    
    if error:
        logger.error(f"Deep validation failed: {error}")
        # Truncate error message to avoid overwhelming the LLM
        truncated_error = error[:500] + "..." if len(error) > 500 else error
        
        return {
            "validation_error": truncated_error,
            "planned_resources": planned_resources,
            "logs": state.get("logs", []) + [f"❌ Deep validation failed: {truncated_error}"]
        }
    else:
        logger.info(f"✓ Deep validation passed: {planned_resources} resources planned")
        return {
            "validation_error": None,
            "planned_resources": planned_resources,
            "logs": state.get("logs", []) + [f"✅ Deep validation passed: {planned_resources} resources will be created"]
        }
