"""
LangGraph Workflow Orchestration

This module defines the stateful workflow graph that coordinates multiple agents
and tools to generate validated, secure infrastructure-as-code. The graph
implements a cyclic workflow with self-correction loops.
"""

import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.core.state import AgentState
from app.core.agents.architect import architect_node
from app.core.agents.config import config_node
from app.services.sandbox import validate_terraform, run_checkov
from app.services.finops import get_cost_estimate
# Assuming parser is available here or inside the function as originally written
# from app.services.parser import parse_hcl_to_graph 

logger = logging.getLogger(__name__)

# Maximum number of retry attempts before failing
MAX_RETRIES = 3


def validator_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that validates Terraform code syntax and configuration.
    executes `terraform validate` on the generated code.
    """
    logger.info("VALIDATOR NODE: Running Terraform validation")
    terraform_code = state.get("terraform_code", "")

    if not terraform_code:
        return {"validation_error": "No Terraform code generated"}

    # Run validation tool
    error = validate_terraform(terraform_code)

    if error:
        logger.warning(f"Validation failed: {error[:100]}...")
        return {
            "validation_error": error,
            "logs": state.get("logs", []) + ["❌ Terraform validation failed: Syntax error detected"]
        }
    else:
        logger.info("✓ Validation passed successfully")
        return {
            "validation_error": None,
            "logs": state.get("logs", []) + ["✅ Terraform syntax validation passed"]
        }


def parser_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that parses Terraform HCL code into a structured graph for visualization.
    """
    hcl_code = state.get("terraform_code", "")
    
    # Import inside function to avoid potential circular imports if necessary
    try:
        from app.services.parser import parse_hcl_to_graph
        graph_data = parse_hcl_to_graph(hcl_code) if hcl_code else {"nodes": [], "edges": []}
    except ImportError as e:
        logger.warning(f"Parser service import failed: {e}")
        graph_data = {"nodes": [], "edges": []}
    except Exception as e:
        logger.error(f"Parser execution failed: {e}")
        graph_data = {"nodes": [], "edges": []}
        
    return {"graph_data": graph_data}


def security_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that runs security checks (Checkov) and returns detailed violations.
    """
    logger.info("SECURITY NODE: Running security scan")
    terraform_code = state.get("terraform_code", "")
    
    if not terraform_code:
        logger.warning("No Terraform code to scan")
        return {
            "security_errors": [],
            "security_violations": [],
            "is_clean": False
        }
    
    # Run Checkov and get detailed violations
    violations = run_checkov(terraform_code)
    
    if violations:
        logger.warning(f"Security checks failed: {len(violations)} violations found")
        
        # Extract IDs for backward compatibility
        check_ids = [v["check_id"] for v in violations]
        
        # Log each violation
        for v in violations:
            logger.warning(
                f"  → [{v['check_id']}] {v['check_name']} "
                f"on {v['resource']}"
            )
        
        return {
            "security_errors": check_ids,  # Legacy support
            "security_violations": violations,  # Detailed info for remediation
            "is_clean": False,
            "logs": state.get("logs", []) + [f"❌ Security scan found {len(violations)} violation(s)"]
        }
    else:
        logger.info("✓ Security scan passed - no violations found")
        return {
            "security_errors": [],
            "security_violations": [],
            "is_clean": True,
            "logs": state.get("logs", []) + ["✅ Security scan passed - no violations"]
        }


def route_after_validator(state: AgentState) -> Literal["architect", "end"]:
    """
    Conditional edge function that routes flow after validation FAILED.
    (Success case is handled by the lambda in the graph definition).
    """
    retry_count = state.get("retry_count", 0)
    
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


def route_after_security(state: AgentState) -> Literal["architect", "parser"]:
    """
    Conditional edge function that routes flow after security scanning.
    If clean, proceed to parser (to visualize final secure code).
    If violations, retry with architect.
    """
    is_clean = state.get("is_clean", False)
    retry_count = state.get("retry_count", 0)
    
    if is_clean:
        logger.info("→ Routing to PARSER node (code is secure)")
        return "parser"
        
    # If we are here, there are security errors
    if retry_count < MAX_RETRIES:
        logger.warning(
            f"→ Security violations found. Routing back to ARCHITECT for retry "
            f"({retry_count}/{MAX_RETRIES})"
        )
        return "architect"

    # Max retries exceeded - proceed to parser anyway (user can decide)
    logger.warning(
        f"⚠ Max retries ({MAX_RETRIES}) exceeded. "
    )
    logger.info("→ Proceeding to Parser despite security issues")
    return "parser"


def finops_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that estimates infrastructure costs using Infracost.
    """
    logger.info("=" * 60)
    logger.info("FINOPS NODE: Calculating cost estimate")
    
    terraform_code = state.get("terraform_code", "")
    
    if not terraform_code:
        logger.warning("No Terraform code for cost estimation")
        return {
            "cost_estimate": "Unable to estimate (no code)",
            "logs": state.get("logs", []) + ["⚠️  Cost estimation skipped - no code available"]
        }
    
    # Call FinOps service
    cost = get_cost_estimate(terraform_code)
    
    logger.info(f"✓ Cost estimate: {cost}")
    
    return {
        "cost_estimate": cost,
        "logs": state.get("logs", []) + [f"💰 Cost calculated: {cost}"]
    }


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.
    """
    logger.info("Initializing LangGraph workflow")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("parser", parser_node)
    workflow.add_node("security", security_node)
    workflow.add_node("finops", finops_node)
    workflow.add_node("ansible", config_node)
    
    # Set entry point
    workflow.set_entry_point("architect")
    
    # Add edges
    workflow.add_edge("architect", "validator")
    
    # validator → [conditional routing]
    # If no validation error, go to security. Else, check retries.
    def route_from_validator(state: AgentState):
        validation_error = state.get("validation_error")
        route = "security" if validation_error is None else route_after_validator(state)
        logger.info(f"ROUTING: validator → {route} (validation_error={validation_error})")
        return route
    
    workflow.add_conditional_edges(
        "validator",
        route_from_validator,
        {
            "security": "security",    # Validation passed → security scan
            "architect": "architect",  # Retry
            "end": END                 # Fail
        }
    )
    
    # security → [conditional routing]
    # If clean, go to parser. If violations, retry with architect.
    workflow.add_conditional_edges(
        "security",
        route_after_security,
        {
            "architect": "architect",  # Fix security issues
            "parser": "parser"         # Clean → parse for visualization
        }
    )
    
    # parser → finops (always)
    # Parser now runs on final, secured code
    workflow.add_edge("parser", "finops")
    
    # finops → ansible (always)
    workflow.add_edge("finops", "ansible")
    
    # ansible → END (always - workflow complete)
    workflow.add_edge("ansible", END)
    
    # Compile the graph with recursion limit
    app = workflow.compile()
    logger.info("✓ LangGraph workflow compiled successfully")
    return app


# Create the compiled workflow (singleton)
workflow_app = create_workflow()


def run_workflow(user_prompt: str) -> AgentState:
    """
    Execute the complete workflow for a user prompt.
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
        "security_violations": [],
        "retry_count": 0,
        "is_clean": False,
        "cost_estimate": "",
        "ansible_playbook": "",
        "graph_data": {"nodes": [], "edges": []},
        "logs": []  # Real-time event tracking
    }
    
    try:
        # Run the workflow with increased recursion limit for self-healing
        final_state = workflow_app.invoke(
            initial_state,
            config={"recursion_limit": 100}
        )
        
        # Log results
        logger.info("=" * 70)
        if final_state.get("is_clean"):
            logger.info("✓ WORKFLOW SUCCESS")
        elif final_state.get("validation_error"):
            logger.error("✗ WORKFLOW FAILED (Validation Error)")
        else:
            logger.warning("! WORKFLOW COMPLETED WITH WARNINGS")
        logger.info("=" * 70)
        
        return final_state
        
    except Exception as e:
        logger.exception("Unhandled exception in workflow execution")
        # Return state with error info for frontend handling
        initial_state["validation_error"] = f"Workflow Execution Error: {str(e)}"
        return initial_state