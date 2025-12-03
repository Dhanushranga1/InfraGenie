"""
Completeness Validation Service

This module validates that generated Terraform code contains ALL required
resources to fulfill the user's intent, not just syntactically correct fragments.

The Problem:
- LLMs often generate partial infrastructure (e.g., just VPC for "K8s cluster")
- Syntax validation passes (VPC code is valid)
- Security scan passes (VPC has no violations)
- User gets incomplete infrastructure

The Solution:
- Analyze user intent (keywords, patterns)
- Define required resource types for each infrastructure pattern
- Verify ALL required resources are present in generated code
- Fail validation if components are missing
"""

import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


# Infrastructure pattern definitions
INFRASTRUCTURE_PATTERNS = {
    "kubernetes": {
        "keywords": ["kubernetes", "k8s", "eks", "aks", "gke", "cluster"],
        "aws": {
            "required_resources": [
                {"type": "aws_eks_cluster", "name": "EKS cluster"},
                {"type": "aws_eks_node_group", "name": "EKS node group"},
                {"type": "aws_vpc", "name": "VPC"},
                {"type": "aws_subnet", "name": "Subnets", "min_count": 2},
                {"type": "aws_iam_role", "name": "IAM roles", "min_count": 2},
            ],
            "min_total_resources": 10
        },
        "azure": {
            "required_resources": [
                {"type": "azurerm_kubernetes_cluster", "name": "AKS cluster"},
                {"type": "azurerm_resource_group", "name": "Resource group"},
                {"type": "azurerm_virtual_network", "name": "Virtual network"},
            ],
            "min_total_resources": 5
        },
        "gcp": {
            "required_resources": [
                {"type": "google_container_cluster", "name": "GKE cluster"},
                {"type": "google_compute_network", "name": "VPC network"},
                {"type": "google_compute_subnetwork", "name": "Subnetwork"},
            ],
            "min_total_resources": 5
        }
    },
    
    "database": {
        "keywords": ["database", "db", "rds", "postgres", "mysql", "mariadb", "sql"],
        "aws": {
            "required_resources": [
                {"type": "aws_db_instance", "name": "RDS instance"},
                {"type": "aws_db_subnet_group", "name": "DB subnet group"},
                {"type": "aws_security_group", "name": "Security group"},
            ],
            "min_total_resources": 4
        },
        "azure": {
            "required_resources": [
                {"type": "azurerm_postgresql_server|azurerm_mysql_server|azurerm_mssql_server", "name": "Database server"},
                {"type": "azurerm_resource_group", "name": "Resource group"},
            ],
            "min_total_resources": 3
        }
    },
    
    "web_server": {
        "keywords": ["web server", "nginx", "apache", "http server"],
        "aws": {
            "required_resources": [
                {"type": "aws_instance", "name": "EC2 instance"},
                # Security group is optional - can be inline or default
                # {"type": "aws_security_group", "name": "Security group"},
                {"type": "aws_key_pair", "name": "SSH key pair"},
                {"type": "tls_private_key", "name": "TLS private key"},
            ],
            "min_total_resources": 3  # Reduced from 4 since security group is optional
        }
    },
    
    "load_balancer": {
        "keywords": ["load balancer", "alb", "nlb", "elb", "application load balancer"],
        "aws": {
            "required_resources": [
                {"type": "aws_lb|aws_alb", "name": "Load balancer"},
                {"type": "aws_lb_target_group", "name": "Target group"},
                {"type": "aws_lb_listener", "name": "Listener"},
                {"type": "aws_security_group", "name": "Security group"},
            ],
            "min_total_resources": 4
        }
    },
    
    "container": {
        "keywords": ["ecs", "fargate", "container", "docker"],
        "aws": {
            "required_resources": [
                {"type": "aws_ecs_cluster", "name": "ECS cluster"},
                {"type": "aws_ecs_task_definition", "name": "Task definition"},
                {"type": "aws_ecs_service", "name": "ECS service"},
            ],
            "min_total_resources": 5
        }
    }
}


def detect_cloud_provider(code: str) -> str:
    """
    Detect which cloud provider is being used based on resource prefixes.
    
    Args:
        code: Terraform HCL code
        
    Returns:
        "aws", "azure", "gcp", or "unknown"
    """
    if 'provider "aws"' in code or 'aws_' in code:
        return "aws"
    elif 'provider "azurerm"' in code or 'azurerm_' in code:
        return "azure"
    elif 'provider "google"' in code or 'google_' in code:
        return "gcp"
    else:
        return "unknown"


def detect_infrastructure_pattern(user_prompt: str) -> Optional[str]:
    """
    Identify what type of infrastructure the user is requesting.
    
    Args:
        user_prompt: Original user request
        
    Returns:
        Pattern key from INFRASTRUCTURE_PATTERNS or None
    """
    prompt_lower = user_prompt.lower()
    
    for pattern_name, pattern_def in INFRASTRUCTURE_PATTERNS.items():
        for keyword in pattern_def["keywords"]:
            if keyword in prompt_lower:
                logger.info(f"Detected infrastructure pattern: {pattern_name} (keyword: {keyword})")
                return pattern_name
    
    logger.info("No specific infrastructure pattern detected (generic request)")
    return None


def count_resources(code: str, resource_type: str) -> int:
    """
    Count how many resources of a given type exist in the code.
    Handles regex patterns for multiple types (e.g., "aws_lb|aws_alb").
    
    Args:
        code: Terraform HCL code
        resource_type: Resource type or regex pattern
        
    Returns:
        Count of matching resources
    """
    # If resource_type contains |, treat as regex
    if '|' in resource_type:
        pattern = rf'resource\s+"({resource_type})"\s+"'
    else:
        pattern = rf'resource\s+"{re.escape(resource_type)}"\s+"'
    
    matches = re.findall(pattern, code)
    return len(matches)


def count_total_resources(code: str) -> int:
    """
    Count total number of resource blocks in code.
    
    Args:
        code: Terraform HCL code
        
    Returns:
        Total resource count
    """
    matches = re.findall(r'resource\s+"[^"]+"\s+"[^"]+"\s*{', code)
    return len(matches)


def validate_completeness(user_prompt: str, terraform_code: str) -> Optional[str]:
    """
    Validate that generated Terraform code contains all required resources
    to fulfill the user's intent.
    
    This is the main entry point for completeness validation.
    
    Args:
        user_prompt: Original user request
        terraform_code: Generated Terraform HCL code
        
    Returns:
        None if complete, error message string if incomplete
        
    Example:
        >>> error = validate_completeness(
        ...     "Create a Kubernetes cluster",
        ...     "resource 'aws_vpc' 'main' {...}"  # Only VPC, no cluster!
        ... )
        >>> print(error)
        "Incomplete infrastructure: Missing EKS cluster, Missing EKS node group (5/10 required resources)"
    """
    # Detect what pattern the user is requesting
    pattern = detect_infrastructure_pattern(user_prompt)
    
    if not pattern:
        # No specific pattern detected - skip completeness validation
        # (Simple requests like "EC2 instance" will pass)
        logger.info("No specific pattern detected - skipping completeness validation")
        return None
    
    # Detect cloud provider from generated code
    provider = detect_cloud_provider(terraform_code)
    
    if provider == "unknown":
        logger.warning("Could not detect cloud provider in generated code")
        return "Could not determine cloud provider (no provider block found)"
    
    # Get requirements for this pattern + provider
    pattern_def = INFRASTRUCTURE_PATTERNS[pattern]
    
    if provider not in pattern_def:
        logger.warning(f"No requirements defined for {pattern} on {provider}")
        return None  # Let it pass if we don't have requirements
    
    requirements = pattern_def[provider]
    
    # Check each required resource
    missing_resources = []
    present_count = 0
    
    for req in requirements["required_resources"]:
        resource_type = req["type"]
        resource_name = req["name"]
        min_count = req.get("min_count", 1)
        
        actual_count = count_resources(terraform_code, resource_type)
        
        if actual_count < min_count:
            if min_count > 1:
                missing_resources.append(f"{resource_name} ({actual_count}/{min_count})")
            else:
                missing_resources.append(resource_name)
            logger.warning(
                f"Missing required resource: {resource_name} "
                f"(found {actual_count}, need {min_count})"
            )
        else:
            present_count += 1
            logger.info(f"✓ Found {actual_count}x {resource_name}")
    
    # Check total resource count (sanity check)
    total_resources = count_total_resources(terraform_code)
    min_total = requirements["min_total_resources"]
    
    logger.info(
        f"Resource count: {total_resources} total "
        f"(minimum: {min_total} for {pattern} on {provider})"
    )
    
    # Build error message if incomplete
    if missing_resources or total_resources < min_total:
        error_parts = []
        
        if missing_resources:
            error_parts.append(f"Missing required components: {', '.join(missing_resources)}")
        
        if total_resources < min_total:
            error_parts.append(
                f"Only {total_resources} resources generated "
                f"(need at least {min_total} for a complete {pattern})"
            )
        
        error_message = "; ".join(error_parts)
        logger.error(f"Completeness validation failed: {error_message}")
        return error_message
    
    # All checks passed
    logger.info(
        f"✓ Completeness validation passed: "
        f"{len(requirements['required_resources'])} required components present, "
        f"{total_resources} total resources"
    )
    return None


def get_completion_advice(user_prompt: str, missing_components: str) -> str:
    """
    Generate specific advice for the Architect on what to add.
    
    Args:
        user_prompt: Original user request
        missing_components: Error message from validate_completeness
        
    Returns:
        Detailed instructions for what to add
    """
    pattern = detect_infrastructure_pattern(user_prompt)
    
    advice = f"""
COMPLETENESS VALIDATION FAILED
==============================

User requested: {user_prompt}
Infrastructure pattern: {pattern}

{missing_components}

WHAT YOU NEED TO DO:
1. Keep ALL existing resources you already generated (don't remove them)
2. Add the missing components listed above
3. Ensure proper dependencies between resources (use depends_on if needed)
4. Return COMPLETE code with both old and new resources

CRITICAL: You are not starting over - you're ADDING to what you already have!
"""
    
    return advice
