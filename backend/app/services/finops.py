"""
FinOps Service - Cloud Cost Estimation

This module provides cost estimation for Terraform infrastructure using Infracost.
Infracost analyzes Terraform code and calculates the monthly cloud costs by
querying actual cloud provider pricing APIs.

Key Features:
- Real-time cost estimation without deploying resources
- Support for AWS, Azure, GCP pricing
- Usage-based cost calculations
- Detailed cost breakdowns per resource

Integration: Works with the validated Terraform code to provide cost visibility
before deployment, enabling FinOps best practices.
"""

import subprocess
import tempfile
import json
import os
import shutil
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_cost_estimate(hcl_code: str) -> str:
    """
    Calculate monthly cost estimate for Terraform infrastructure using Infracost.
    
    This function performs complete cost analysis:
    1. Creates isolated temporary workspace
    2. Writes HCL code to main.tf
    3. Executes Infracost CLI with JSON output
    4. Parses cost breakdown and extracts total monthly cost
    5. Returns formatted cost string
    
    Infracost connects to cloud provider pricing APIs to get real-time costs
    based on the resources defined in the Terraform code.
    
    Args:
        hcl_code (str): Validated Terraform HCL code. Should include provider
            configuration and resource definitions. Example:
            ```hcl
            provider "aws" {
              region = "us-east-1"
            }
            
            resource "aws_instance" "web" {
              ami           = "ami-0c55b159cbfafe1f0"
              instance_type = "t3.micro"
            }
            ```
    
    Returns:
        str: Formatted monthly cost estimate. Examples:
            - "$24.50/mo" - Standard cost
            - "$0.00/mo" - Free tier resources
            - "Unable to estimate cost" - If Infracost fails
    
    Environment Requirements:
        - INFRACOST_API_KEY must be set in environment variables
        - Infracost CLI must be installed (already in Docker image)
    
    Raises:
        Exception: Logged but not raised. Returns error message string instead.
    
    Example:
        ```python
        code = '''
        provider "aws" { region = "us-east-1" }
        resource "aws_instance" "app" {
          ami           = "ami-0c55b159cbfafe1f0"
          instance_type = "t3.medium"
        }
        resource "aws_db_instance" "db" {
          instance_class = "db.t3.micro"
          engine        = "postgres"
        }
        '''
        
        cost = get_cost_estimate(code)
        print(cost)  # "$45.60/mo"
        ```
    
    Implementation Notes:
        - Uses temporary directory for isolation
        - Runs infracost in breakdown mode
        - Parses JSON output for totalMonthlyCost
        - Handles missing API key gracefully
        - Automatic cleanup even on errors
        - 60 second timeout for API calls
    
    Cost Accuracy:
        - Based on on-demand pricing (no reserved instances)
        - Assumes standard usage patterns
        - May not include all costs (data transfer, etc.)
        - Updated monthly by Infracost
    """
    temp_dir = None
    
    try:
        # Check for Infracost API key
        api_key = os.environ.get("INFRACOST_API_KEY")
        if not api_key:
            logger.warning(
                "INFRACOST_API_KEY not set. Cost estimation unavailable."
            )
            return "Cost estimation unavailable (API key missing)"
        
        # Create isolated workspace
        temp_dir = tempfile.mkdtemp(prefix="infragenie_cost_")
        logger.info(f"Created temporary Infracost workspace: {temp_dir}")
        
        # Write HCL code to main.tf
        main_tf_path = Path(temp_dir) / "main.tf"
        main_tf_path.write_text(hcl_code, encoding="utf-8")
        logger.debug(f"Wrote {len(hcl_code)} bytes for cost analysis")
        
        # Run Infracost breakdown
        logger.info("Running Infracost cost analysis...")
        
        result = subprocess.run(
            [
                "infracost",
                "breakdown",
                "--path", ".",
                "--format", "json"
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60,  # Infracost API calls can be slow
            check=False,
            env={**os.environ, "INFRACOST_API_KEY": api_key}
        )
        
        # Check if command executed successfully
        if result.returncode != 0:
            logger.error(f"Infracost failed with exit code {result.returncode}")
            logger.error(f"Stderr: {result.stderr[:300]}")
            return "Unable to estimate cost (Infracost error)"
        
        # Parse JSON output
        try:
            cost_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Infracost JSON: {str(e)}")
            logger.debug(f"Raw output: {result.stdout[:500]}")
            return "Unable to estimate cost (parse error)"
        
        # Extract total monthly cost
        # Infracost JSON structure: { "projects": [{ "breakdown": { "totalMonthlyCost": "24.50" } }] }
        try:
            projects = cost_data.get("projects", [])
            if not projects:
                logger.warning("Infracost returned no projects")
                return "$0.00/mo"
            
            breakdown = projects[0].get("breakdown", {})
            total_cost = breakdown.get("totalMonthlyCost")
            
            if total_cost is None:
                logger.warning("No totalMonthlyCost in Infracost output")
                return "$0.00/mo"
            
            # Format the cost
            # totalMonthlyCost is returned as a string like "24.50"
            try:
                cost_float = float(total_cost)
                formatted_cost = f"${cost_float:.2f}/mo"
            except (ValueError, TypeError):
                formatted_cost = f"${total_cost}/mo"
            
            logger.info(f"Cost estimate calculated: {formatted_cost}")
            
            # Log cost breakdown summary
            total_resources = breakdown.get("totalDetectedResources", 0)
            logger.info(f"Total resources analyzed: {total_resources}")
            
            return formatted_cost
        
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Infracost JSON structure: {str(e)}")
            logger.debug(f"Full JSON: {json.dumps(cost_data, indent=2)[:500]}")
            return "Unable to estimate cost (structure error)"
    
    except subprocess.TimeoutExpired:
        logger.error("Infracost command timed out after 60 seconds")
        return "Unable to estimate cost (timeout)"
    
    except Exception as e:
        logger.error(f"Unexpected error during cost estimation: {str(e)}")
        logger.exception("Full traceback:")
        return "Unable to estimate cost (system error)"
    
    finally:
        # Cleanup: Remove temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")


def parse_cost_details(hcl_code: str) -> dict:
    """
    Get detailed cost breakdown per resource (optional extended function).
    
    This function provides granular cost information for each resource,
    useful for detailed FinOps analysis and cost optimization.
    
    Args:
        hcl_code (str): Validated Terraform HCL code
    
    Returns:
        dict: Detailed cost breakdown with per-resource costs
    
    Note:
        This is an extended feature. Currently returns basic summary.
        Can be expanded to provide per-resource cost details.
    """
    # This is a placeholder for future enhancement
    # Could parse the full Infracost breakdown to show per-resource costs
    cost = get_cost_estimate(hcl_code)
    
    return {
        "total_monthly_cost": cost,
        "currency": "USD",
        "resources": []  # Future: parse individual resource costs
    }
