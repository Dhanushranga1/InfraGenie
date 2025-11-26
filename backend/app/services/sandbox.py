"""
Sandbox Service - Secure CLI Tool Execution

This module provides isolated execution of DevOps CLI tools (Terraform, Checkov)
within temporary filesystem contexts. All operations are sandboxed to prevent
interference between concurrent requests.

Security Considerations:
- Temporary directories are automatically cleaned up
- Subprocess execution is time-limited to prevent hangs
- All outputs are captured to prevent shell injection
- Working directories are isolated per execution

Design Pattern: Each function creates its own ephemeral workspace, ensuring
thread-safety and preventing state pollution.
"""

import subprocess
import tempfile
import json
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def run_tool(
    directory: str,
    command: List[str],
    timeout: int = 60,
    capture_output: bool = True
) -> subprocess.CompletedProcess:
    """
    Execute a CLI command in a specified directory with safety constraints.
    
    This is the foundational function for all CLI tool interactions. It provides
    consistent error handling, timeout management, and output capturing across
    Terraform, Checkov, and other DevOps tools.
    
    Args:
        directory (str): Absolute path to the working directory where the
            command should execute. Must exist before calling.
        command (List[str]): Command and arguments as a list.
            Example: ["terraform", "validate", "-json"]
        timeout (int, optional): Maximum execution time in seconds. Prevents
            runaway processes. Default: 60 seconds.
        capture_output (bool, optional): Whether to capture stdout/stderr.
            Set to False for streaming output. Default: True.
    
    Returns:
        subprocess.CompletedProcess: Object containing:
            - returncode (int): Exit code (0 = success)
            - stdout (str): Standard output as text
            - stderr (str): Standard error as text
            - args (List[str]): The executed command
    
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout duration
        FileNotFoundError: If the command executable is not found
        PermissionError: If insufficient permissions to execute
    
    Example:
        ```python
        result = run_tool(
            directory="/tmp/tf-workspace",
            command=["terraform", "init", "-no-color"],
            timeout=120
        )
        if result.returncode == 0:
            print("Success:", result.stdout)
        ```
    
    Note:
        - Always use absolute paths for the directory parameter
        - The function does NOT change the current working directory globally
        - Timeout only applies to subprocess execution, not setup/cleanup
    """
    logger.info(f"Executing command in {directory}: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            cwd=directory,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=False  # We handle non-zero exit codes manually
        )
        
        logger.debug(f"Command exit code: {result.returncode}")
        if result.returncode != 0:
            logger.warning(f"Command failed with stderr: {result.stderr[:200]}")
        
        return result
    
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error running command: {str(e)}")
        raise


def validate_terraform(hcl_code: str) -> Optional[str]:
    """
    Validate Terraform HCL code syntax and configuration correctness.
    
    This function performs a complete Terraform validation cycle:
    1. Creates isolated temporary workspace
    2. Writes HCL code to main.tf
    3. Initializes Terraform (downloads providers)
    4. Runs validation with JSON output
    5. Parses diagnostics and returns human-readable error summary
    
    The validation process does NOT connect to any cloud providers or create
    real resources. It only checks syntax and logical consistency.
    
    Args:
        hcl_code (str): Raw Terraform HCL code to validate. Should be complete
            and include provider configuration. Example:
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
        Optional[str]: 
            - None if validation passed successfully
            - Error message string if validation failed, formatted for LLM
              consumption. Example: "Error at line 5: Missing required 
              argument 'vpc_id' in resource 'aws_security_group.main'"
    
    Raises:
        subprocess.TimeoutExpired: If terraform commands hang
        Exception: For unexpected errors (logged with full context)
    
    Example:
        ```python
        code = '''
        provider "aws" { region = "us-west-2" }
        resource "aws_instance" "test" {
          # Missing required 'ami' argument
          instance_type = "t3.micro"
        }
        '''
        
        error = validate_terraform(code)
        if error:
            print(f"Validation failed: {error}")
            # Send back to Architect Agent for fixing
        else:
            print("Code is valid!")
        ```
    
    Implementation Notes:
        - Uses a temporary directory that is automatically cleaned up
        - Terraform init is run silently (output suppressed)
        - Validation output is JSON-parsed for structured error extraction
        - Only the first error is returned to avoid overwhelming the LLM
        - The temp directory is deleted even if errors occur
    """
    temp_dir = None
    
    try:
        # Create isolated workspace
        temp_dir = tempfile.mkdtemp(prefix="infragenie_tf_")
        logger.info(f"Created temporary Terraform workspace: {temp_dir}")
        
        # Write HCL code to main.tf
        main_tf_path = Path(temp_dir) / "main.tf"
        main_tf_path.write_text(hcl_code, encoding="utf-8")
        logger.debug(f"Wrote {len(hcl_code)} bytes to {main_tf_path}")
        
        # Initialize Terraform (download providers, modules)
        logger.info("Running terraform init...")
        init_result = run_tool(
            directory=temp_dir,
            command=["terraform", "init", "-no-color"],
            timeout=120  # Provider downloads can be slow
        )
        
        if init_result.returncode != 0:
            error_msg = f"Terraform initialization failed: {init_result.stderr}"
            logger.error(error_msg)
            return error_msg
        
        # Validate configuration
        logger.info("Running terraform validate...")
        validate_result = run_tool(
            directory=temp_dir,
            command=["terraform", "validate", "-json"],
            timeout=30
        )
        
        # Parse JSON output
        try:
            validation_output = json.loads(validate_result.stdout)
        except json.JSONDecodeError:
            logger.error("Failed to parse terraform validate JSON output")
            return f"Validation error (unparseable): {validate_result.stderr}"
        
        # Check validation status
        if validation_output.get("valid", False):
            logger.info("Terraform validation passed successfully")
            return None
        
        # Extract error diagnostics
        diagnostics = validation_output.get("diagnostics", [])
        if not diagnostics:
            logger.warning("Validation failed but no diagnostics provided")
            return "Validation failed with unknown error"
        
        # Format the first error for LLM consumption
        first_error = diagnostics[0]
        error_summary = first_error.get("summary", "Unknown error")
        error_detail = first_error.get("detail", "")
        
        # Include line/column information if available
        if "range" in first_error:
            range_info = first_error["range"]
            start_line = range_info.get("start", {}).get("line", "?")
            error_message = (
                f"Error at line {start_line}: {error_summary}. "
                f"{error_detail}"
            )
        else:
            error_message = f"{error_summary}. {error_detail}"
        
        logger.warning(f"Validation failed: {error_message}")
        return error_message
    
    except Exception as e:
        logger.error(f"Unexpected error during Terraform validation: {str(e)}")
        return f"Validation system error: {str(e)}"
    
    finally:
        # Cleanup: Remove temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")


def run_checkov(hcl_code: str) -> List[Dict[str, str]]:
    """
    Scan Terraform code for security and compliance violations using Checkov.
    Returns detailed violation information for intelligent remediation.
    
    Args:
        hcl_code (str): Terraform HCL code to scan
    
    Returns:
        List[Dict[str, str]]: List of detailed violation dictionaries:
        [
            {
                "check_id": "CKV_AWS_24",
                "check_name": "Ensure no security groups allow ingress from 0.0.0.0:0 to port 22",
                "resource": "aws_security_group.allow_ssh",
                "file_path": "main.tf",
                "severity": "HIGH",
                "guideline": "https://docs.bridgecrew.io/docs/...",
            }
        ]
    
    Example:
        violations = run_checkov(code)
        for v in violations:
            print(f"{v['check_id']} on {v['resource']}: {v['check_name']}")
    """
    temp_dir = None
    
    try:
        # Create isolated workspace
        temp_dir = tempfile.mkdtemp(prefix="infragenie_checkov_")
        logger.info(f"Created temporary Checkov workspace: {temp_dir}")
        
        # Write HCL code to main.tf
        main_tf_path = Path(temp_dir) / "main.tf"
        main_tf_path.write_text(hcl_code, encoding="utf-8")
        
        # Run Checkov with JSON output
        logger.info("Running Checkov security scan...")
        checkov_result = run_tool(
            directory=temp_dir,
            command=[
                "checkov",
                "-f", "main.tf",
                "--output", "json",
                "--quiet",
                "--compact"
            ],
            timeout=60
        )
        
        # Parse JSON output
        try:
            checkov_output = json.loads(checkov_result.stdout)
        except json.JSONDecodeError:
            logger.error("Failed to parse Checkov JSON output")
            return []
        
        # Extract detailed violation information
        violations: List[Dict[str, str]] = []
        
        results = checkov_output.get("results", {})
        failed_checks = results.get("failed_checks", [])
        
        for check in failed_checks:
            violation = {
                "check_id": check.get("check_id", "UNKNOWN"),
                "check_name": check.get("check_name", "Unknown security check"),
                "resource": check.get("resource", "Unknown resource"),
                "file_path": check.get("file_path", "main.tf"),
                "severity": check.get("check_result", {}).get("result", "MEDIUM"),
                "guideline": check.get("guideline", ""),
                "description": check.get("description", ""),
            }
            violations.append(violation)
            
            # Log detailed information
            logger.info(
                f"Security violation: [{violation['check_id']}] "
                f"{violation['check_name']} on {violation['resource']}"
            )
        
        if violations:
            logger.warning(f"Checkov found {len(violations)} security violations")
        else:
            logger.info("✓ Checkov scan passed: No security violations found")
        
        return violations
    
    except Exception as e:
        logger.error(f"Unexpected error during Checkov scan: {str(e)}")
        return []
    
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup {temp_dir}: {str(e)}")
