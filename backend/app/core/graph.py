"""
LangGraph Workflow Orchestration

This module defines the stateful workflow graph that coordinates multiple agents
and tools to generate validated, secure infrastructure-as-code. The graph
implements a cyclic workflow with self-correction loops.

Workflow Architecture:
    User Prompt → Architect → Validator → Security → [Success/Retry]
                      ↑           |            |
                      └───────────┴────────────┘
                         (Retry loop if errors)

The graph uses conditional edges to route execution based on validation results,
security scan outcomes, and retry limits. This enables autonomous error
correction without human intervention.

Key Features:
- Automatic retry with exponential backoff
- Maximum retry limit to prevent infinite loops
- Structured state management via TypedDict
- Comprehensive logging for debugging
- Clean separation between LLM and tool nodes
"""

import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.core.state import AgentState
from app.core.agents.architect import architect_node
from app.services.sandbox import validate_terraform, run_checkov

logger = logging.getLogger(__name__)

# Maximum number of retry attempts before failing
MAX_RETRIES = 3


def validator_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that validates Terraform code syntax and configuration.
    
    This node executes `terraform validate` on the generated code and updates
    the state based on the results. It does not call the LLM - it's a pure
    deterministic tool node.
    
    Args:
        state (AgentState): Current workflow state with terraform_code
    
    Returns:
        Dict[str, Any]: Updated state fields:
            - validation_error: Error message if validation failed, None otherwise
    
    Behavior:
        1. Extract terraform_code from state
        2. Call sandbox.validate_terraform()
        3. If error returned, store in validation_error
        4. If None returned, validation passed
    
    Example:
        ```python
        # Invalid code
        state = {"terraform_code": "resource aws_instance {"}
        result = validator_node(state)
        # result = {"validation_error": "Error: Missing required argument..."}
        
        # Valid code
        state = {"terraform_code": "provider \"aws\" {...}"}
        result = validator_node(state)
        # result = {"validation_error": None}
        ```
    """
    logger.info("=" * 60)
    logger.info("VALIDATOR NODE: Running Terraform validation")
    
    terraform_code = state.get("terraform_code", "")
    
    if not terraform_code:
        logger.warning("No Terraform code to validate")
        return {
            "validation_error": "No Terraform code generated"
        }
    
    # Run validation
    error = validate_terraform(terraform_code)
    
    if error:
        logger.warning(f"Validation failed: {error[:100]}...")
        return {
            "validation_error": error
        }
    else:
        logger.info("✓ Validation passed successfully")
        return {
            "validation_error": None
        }


def security_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that scans Terraform code for security violations.
    
    This node executes Checkov security scanning on the validated code and
    updates the state with any policy violations found. Like the validator,
    this is a deterministic tool node.
    
    Args:
        state (AgentState): Current workflow state with validated terraform_code
    
    Returns:
        Dict[str, Any]: Updated state fields:
            - security_errors: List of failed Checkov check IDs
            - is_clean: True if no violations, False otherwise
    
    Behavior:
        1. Extract terraform_code from state
        2. Call sandbox.run_checkov()
        3. Store list of failed check IDs
        4. Set is_clean flag based on results
    
    Example:
        ```python
        # Code with security issues
        state = {"terraform_code": "resource aws_s3_bucket {...}"}
        result = security_node(state)
        # result = {
        #     "security_errors": ["CKV_AWS_18", "CKV_AWS_21"],
        #     "is_clean": False
        # }
        
        # Secure code
        state = {"terraform_code": "resource aws_s3_bucket {...encrypted...}"}
        result = security_node(state)
        # result = {"security_errors": [], "is_clean": True}
        ```
    """
    logger.info("=" * 60)
    logger.info("SECURITY NODE: Running Checkov security scan")
    
    terraform_code = state.get("terraform_code", "")
    
    if not terraform_code:
        logger.warning("No Terraform code to scan")
        return {
            "security_errors": [],
            "is_clean": False
        }
    
    # Run security scan
    violations = run_checkov(terraform_code)
    
    if violations:
        logger.warning(f"✗ Found {len(violations)} security violations")
        return {
            "security_errors": violations,
            "is_clean": False
        }
    else:
        logger.info("✓ Security scan passed - no violations found")
        return {
            "security_errors": [],
            "is_clean": True
        }


def route_after_validator(
    state: AgentState
) -> Literal["architect", "security", "end"]:
    """
    Conditional edge function that routes flow after validation.
    
    This function determines the next node based on validation results and
    retry count. It implements the core retry logic of the workflow.
    
    Args:
        state (AgentState): Current state with validation results
    
    Returns:
        Literal["architect", "security", "end"]: Next node to execute
    
    Routing Logic:
        1. If validation passed → Go to "security" node
        2. If validation failed AND retry_count < MAX_RETRIES → Go to "architect"
        3. If validation failed AND retry_count >= MAX_RETRIES → Go to "end"
    
    Example:
        ```python
        # Pass: continue to security
        state = {"validation_error": None, "retry_count": 1}
        route_after_validator(state)  # → "security"
        
        # Fail: retry with architect
        state = {"validation_error": "Missing argument", "retry_count": 1}
        route_after_validator(state)  # → "architect"
        
        # Fail: max retries exceeded
        state = {"validation_error": "Missing argument", "retry_count": 3}
        route_after_validator(state)  # → "end"
        ```
    """
    validation_error = state.get("validation_error")
    retry_count = state.get("retry_count", 0)
    
    if validation_error is None:
        # Validation passed - proceed to security scan
        logger.info("→ Routing to SECURITY node")
        return "security"
    
    if retry_count < MAX_RETRIES:
        # Validation failed but retries available
        logger.warning(
            f"→ Routing back to ARCHITECT for retry "
            f"({retry_count}/{MAX_RETRIES})"
        )
        return "architect"
    
    # Max retries exceeded - fail workflow
    logger.error(
        f"✗ Max retries ({MAX_RETRIES}) exceeded. Workflow failed."
    )
    return "end"


def route_after_security(
    state: AgentState
) -> Literal["architect", "end"]:
    """
    Conditional edge function that routes flow after security scanning.
    
    This function determines whether to proceed to completion or loop back
    for security remediation based on scan results and retry count.
    
    Args:
        state (AgentState): Current state with security scan results
    
    Returns:
        Literal["architect", "end"]: Next node to execute
    
    Routing Logic:
        1. If is_clean=True → Go to "end" (success)
        2. If security_errors AND retry_count < MAX_RETRIES → Go to "architect"
        3. If security_errors AND retry_count >= MAX_RETRIES → Go to "end" (fail)
    
    Example:
        ```python
        # Clean: workflow complete
        state = {"is_clean": True, "security_errors": []}
        route_after_security(state)  # → "end"
        
        # Violations: retry with architect
        state = {
            "is_clean": False,
            "security_errors": ["CKV_AWS_8"],
            "retry_count": 1
        }
        route_after_security(state)  # → "architect"
        
        # Violations: max retries exceeded
        state = {
            "is_clean": False,
            "security_errors": ["CKV_AWS_8"],
            "retry_count": 3
        }
        route_after_security(state)  # → "end"
        ```
    """
    is_clean = state.get("is_clean", False)
    security_errors = state.get("security_errors", [])
    retry_count = state.get("retry_count", 0)
    
    if is_clean:
        # All checks passed - workflow complete
        logger.info("✓ Workflow complete - code is clean and validated")
        return "end"
    
    if security_errors and retry_count < MAX_RETRIES:
        # Security violations found but retries available
        logger.warning(
            f"→ Routing back to ARCHITECT for security fixes "
            f"({retry_count}/{MAX_RETRIES})"
        )
        return "architect"
    
    # Max retries exceeded - end workflow with violations
    logger.error(
        f"✗ Max retries ({MAX_RETRIES}) exceeded. "
        f"Security violations remain: {security_errors}"
    )
    return "end"


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.
    
    This function constructs the complete stateful graph with all nodes and
    conditional edges. The resulting compiled graph can be invoked with an
    initial state to execute the workflow.
    
    Returns:
        CompiledGraph: Executable LangGraph workflow
    
    Graph Structure:
        ```
        START
          ↓
        architect (LLM Node)
          ↓
        validator (Tool Node)
          ↓
        [Conditional]
          ├─→ security (if valid)
          ├─→ architect (if invalid, retry < max)
          └─→ END (if invalid, retry >= max)
        
        security (Tool Node)
          ↓
        [Conditional]
          ├─→ END (if clean)
          ├─→ architect (if violations, retry < max)
          └─→ END (if violations, retry >= max)
        ```
    
    Usage:
        ```python
        # Create the workflow
        workflow = create_workflow()
        
        # Define initial state
        initial_state: AgentState = {
            "user_prompt": "Create an EC2 instance",
            "terraform_code": "",
            "validation_error": None,
            "security_errors": [],
            "retry_count": 0,
            "is_clean": False
        }
        
        # Execute the workflow
        final_state = workflow.invoke(initial_state)
        
        # Check results
        if final_state["is_clean"]:
            print("Success!")
            print(final_state["terraform_code"])
        else:
            print("Failed after retries")
        ```
    
    Configuration:
        - Entry point: "architect" node
        - Max retries: 3 (defined by MAX_RETRIES constant)
        - State type: AgentState TypedDict
    """
    logger.info("Initializing LangGraph workflow")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("security", security_node)
    
    # Set entry point
    workflow.set_entry_point("architect")
    
    # Add edges
    # architect → validator (always)
    workflow.add_edge("architect", "validator")
    
    # validator → [conditional routing]
    workflow.add_conditional_edges(
        "validator",
        route_after_validator,
        {
            "architect": "architect",  # Retry
            "security": "security",     # Continue
            "end": END                  # Fail
        }
    )
    
    # security → [conditional routing]
    workflow.add_conditional_edges(
        "security",
        route_after_security,
        {
            "architect": "architect",  # Fix security issues
            "end": END                 # Success or fail
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("✓ LangGraph workflow compiled successfully")
    
    return app


# Create the compiled workflow (singleton)
workflow_app = create_workflow()


def run_workflow(user_prompt: str) -> AgentState:
    """
    Execute the complete workflow for a user prompt.
    
    This is the main entry point for external callers (like API endpoints).
    It initializes the state, runs the workflow, and returns the final result.
    
    Args:
        user_prompt (str): User's infrastructure request
            Example: "Create a VPC with public and private subnets"
    
    Returns:
        AgentState: Final state after workflow completion, containing:
            - terraform_code: Generated HCL code (may be invalid if failed)
            - is_clean: Whether code passed all checks
            - validation_error: Last validation error (if any)
            - security_errors: Remaining security violations (if any)
            - retry_count: Number of attempts made
    
    Example:
        ```python
        result = run_workflow("Create an S3 bucket with encryption")
        
        if result["is_clean"]:
            # Success - use the code
            terraform_code = result["terraform_code"]
            save_to_file(terraform_code)
        else:
            # Failure - check errors
            if result["validation_error"]:
                print(f"Validation failed: {result['validation_error']}")
            if result["security_errors"]:
                print(f"Security issues: {result['security_errors']}")
        ```
    
    Raises:
        Exception: Any unhandled errors during workflow execution
            (logged with full traceback)
    """
    logger.info("=" * 70)
    logger.info(f"WORKFLOW START: {user_prompt[:50]}...")
    logger.info("=" * 70)
    
    # Initialize state
    initial_state: AgentState = {
        "user_prompt": user_prompt,
        "terraform_code": "",
        "validation_error": None,
        "security_errors": [],
        "retry_count": 0,
        "is_clean": False
    }
    
    try:
        # Run the workflow
        final_state = workflow_app.invoke(initial_state)
        
        # Log results
        logger.info("=" * 70)
        if final_state["is_clean"]:
            logger.info("✓ WORKFLOW SUCCESS")
        else:
            logger.warning("✗ WORKFLOW FAILED")
            
        logger.info(f"Total retries: {final_state['retry_count']}")
        logger.info(f"Final code length: {len(final_state['terraform_code'])} chars")
        
        if final_state.get("validation_error"):
            logger.warning(f"Validation error: {final_state['validation_error'][:100]}")
        
        if final_state.get("security_errors"):
            logger.warning(f"Security errors: {final_state['security_errors']}")
        
        logger.info("=" * 70)
        
        return final_state
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        logger.exception("Full traceback:")
        raise
