"""
Agent State Schema

This module defines the shared state structure that flows through the LangGraph
workflow. The AgentState serves as the "memory" of the multi-agent system,
tracking the evolution of infrastructure code through generation, validation,
and security scanning phases.

Design Pattern: TypedDict provides compile-time type checking while maintaining
runtime flexibility for the LangGraph state machine.
"""

from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict):
    """
    Shared state object passed between all nodes in the LangGraph workflow.
    
    This state represents the complete context of an infrastructure generation
    request, tracking code evolution, errors, and retry logic across multiple
    agent invocations.
    
    Attributes:
        user_prompt (str): The original high-level infrastructure request
        
        terraform_code (str): Current version of generated Terraform HCL code
            
        validation_error (Optional[str]): Human-readable error from terraform validate
            or completeness check. Set by both validator_node and completeness_validator_node.
        
        completion_advice (Optional[str]): Detailed advice from completeness validator
            explaining which resources are missing and how to add them. Used by Architect
            for targeted remediation of incomplete infrastructure.
            
        security_errors (List[str]): Legacy list of Checkov check IDs (deprecated)
        
        security_violations (List[Dict[str, str]]): Detailed security violations:
            [
                {
                    "check_id": "CKV_AWS_24",
                    "check_name": "Ensure no security groups allow ingress...",
                    "resource": "aws_security_group.allow_ssh",
                    "file_path": "main.tf",
                    "severity": "HIGH",
                    "guideline": "https://...",
                }
            ]
            
        retry_count (int): Counter tracking fix attempts (max 5)
            
        is_clean (bool): Flag indicating all checks passed
            
        cost_estimate (str): Monthly cost estimate from Infracost in formatted
            string. Example: "$24.50/mo". Empty string if not yet calculated.
            
        ansible_playbook (str): Generated Ansible YAML configuration for server
            setup and the "Cost Assassin" cron job. Empty string initially.
        
        logs (List[str]): Ordered list of workflow events for real-time observability.
            Each node appends success/failure messages. Enables streaming progress to UI.
            Example: ["✅ Terraform syntax validation passed", "❌ Security scan found 2 violations"]
    
    Lifecycle:
        1. Initialize with user_prompt
        2. Architect generates terraform_code
        3. Validator sets validation_error if syntax issues found
        4. Completeness validator checks if infrastructure is complete:
           - Sets validation_error + completion_advice if missing resources
           - Routes back to Architect with specific missing component list
        5. Security sets security_errors if vulnerabilities detected
        6. Architect fixes errors, increments retry_count
        7. Loop until is_clean=True or retry_count exceeds limit (max 5)
        8. FinOps calculates cost_estimate
        9. Config agent generates ansible_playbook
    
    Example:
        ```python
        initial_state: AgentState = {
            "user_prompt": "Deploy a PostgreSQL RDS instance",
            "terraform_code": "",
            "validation_error": None,
            "completion_advice": None,
            "security_errors": [],
            "retry_count": 0,
            "is_clean": False,
            "cost_estimate": "",
            "ansible_playbook": ""
        }
        ```
    """
    user_prompt: str
    terraform_code: str
    validation_error: Optional[str]
    completion_advice: Optional[str]  # New: advice from completeness validator
    security_errors: List[str]  # Legacy: List of check IDs
    security_violations: List[Dict[str, str]]  # Detailed violation info
    retry_count: int
    is_clean: bool
    cost_estimate: str
    ansible_playbook: str
    graph_data: dict  # Structured graph representation of parsed HCL
    logs: List[str]  # Real-time workflow event log
