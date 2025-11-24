"""
Agent State Schema

This module defines the shared state structure that flows through the LangGraph
workflow. The AgentState serves as the "memory" of the multi-agent system,
tracking the evolution of infrastructure code through generation, validation,
and security scanning phases.

Design Pattern: TypedDict provides compile-time type checking while maintaining
runtime flexibility for the LangGraph state machine.
"""

from typing import TypedDict, Optional, List


class AgentState(TypedDict):
    """
    Shared state object passed between all nodes in the LangGraph workflow.
    
    This state represents the complete context of an infrastructure generation
    request, tracking code evolution, errors, and retry logic across multiple
    agent invocations.
    
    Attributes:
        user_prompt (str): The original high-level infrastructure request from
            the user. Example: "Create a secure EC2 instance with SSH access"
            
        terraform_code (str): The current version of generated Terraform HCL code.
            This field is updated by the Architect Agent and validated by
            downstream nodes. Initially empty.
            
        validation_error (Optional[str]): Human-readable error message from
            `terraform validate`. If None, validation passed successfully.
            Example: "Error: Missing required argument 'ami' in aws_instance.web"
            
        security_errors (List[str]): List of Checkov check IDs that failed
            security/compliance scans. Each ID represents a specific policy
            violation that must be addressed.
            Example: ['CKV_AWS_8', 'CKV_AWS_23'] for unencrypted EBS and
            unrestricted security groups.
            
        retry_count (int): Counter tracking how many times the Architect Agent
            has attempted to fix errors. Used to prevent infinite loops in the
            graph. Default: 0. Maximum: 3.
            
        is_clean (bool): Flag indicating whether the code has passed all
            validation and security checks. When True, the workflow proceeds
            to cost estimation and artifact generation. Default: False.
    
    Lifecycle:
        1. Initialize with user_prompt
        2. Architect generates terraform_code
        3. Validator sets validation_error if issues found
        4. Security sets security_errors if vulnerabilities detected
        5. Architect fixes errors, increments retry_count
        6. Loop until is_clean=True or retry_count exceeds limit
    
    Example:
        ```python
        initial_state: AgentState = {
            "user_prompt": "Deploy a PostgreSQL RDS instance",
            "terraform_code": "",
            "validation_error": None,
            "security_errors": [],
            "retry_count": 0,
            "is_clean": False
        }
        ```
    """
    user_prompt: str
    terraform_code: str
    validation_error: Optional[str]
    security_errors: List[str]
    retry_count: int
    is_clean: bool
