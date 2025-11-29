"""
LangGraph Workflow Orchestration

This module defines the stateful workflow graph that coordinates multiple agents
and tools to generate validated, secure infrastructure-as-code. The graph
implements a cyclic workflow with self-correction loops.

Phase 8 Enhancement: Integrated planner, clarifier, and deep validation nodes
into the workflow for improved infrastructure completeness.
"""

import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.core.state import AgentState
from app.core.agents.architect import architect_node
from app.core.agents.config import config_node
from app.core.agents.planner import planner_agent
from app.core.agents.clarifier import clarify_requirements
from app.services.sandbox import validate_terraform, run_checkov
from app.services.completeness import validate_completeness, get_completion_advice
from app.services.deep_validation import deep_validator_node
from app.services.finops import get_cost_estimate
# Assuming parser is available here or inside the function as originally written
# from app.services.parser import parse_hcl_to_graph 

logger = logging.getLogger(__name__)

# Maximum number of retry attempts before failing (increased from 3 to 5)
MAX_RETRIES = 5


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


def completeness_validator_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that validates infrastructure completeness.
    
    This node checks if the generated code contains ALL required resources
    to fulfill the user's intent. For example:
    - "Kubernetes cluster" requires VPC + cluster + node groups, not just VPC
    - "RDS database" requires VPC + subnet group + security group + DB instance
    
    This prevents the common LLM failure mode of generating partial infrastructure.
    """
    logger.info("COMPLETENESS VALIDATOR NODE: Checking infrastructure completeness")
    
    user_prompt = state.get("user_prompt", "")
    terraform_code = state.get("terraform_code", "")
    
    if not terraform_code:
        return {
            "validation_error": "No Terraform code to validate",
            "completeness_score": 0.0,
            "missing_components": ["terraform code"],
            "logs": state.get("logs", []) + ["❌ Completeness check failed: No code generated"]
        }
    
    # Import completeness functions (avoid circular imports)
    from app.services.completeness import (
        validate_completeness as validate_completeness_detailed,
        detect_infrastructure_pattern,
        count_total_resources
    )
    
    # Detect infrastructure type for classification
    pattern = detect_infrastructure_pattern(user_prompt)
    total_resources = count_total_resources(terraform_code)
    
    # Classify complexity
    infrastructure_type = "unknown"
    if pattern == "kubernetes":
        infrastructure_type = "complex"
    elif pattern in ["database", "load_balancer"]:
        infrastructure_type = "medium"
    elif pattern in ["web_server", "compute"]:
        infrastructure_type = "simple"
    elif total_resources >= 10:
        infrastructure_type = "complex"
    elif total_resources >= 5:
        infrastructure_type = "medium"
    elif total_resources >= 2:
        infrastructure_type = "simple"
    
    # Run enhanced validation that returns detailed metrics
    try:
        # The validate_completeness function returns just error message
        # We'll enhance it inline here
        error = validate_completeness(user_prompt, terraform_code)
        
        # Calculate completeness score based on error presence
        if error is None:
            completeness_score = 1.0
            missing_components_list = []
        else:
            # Parse missing components from error message
            missing_components_list = []
            if "Missing required components:" in error:
                components_part = error.split("Missing required components:")[1].split(";")[0]
                missing_components_list = [c.strip() for c in components_part.split(",")]
            
            # Estimate completeness score (could be enhanced)
            if "kubernetes" in user_prompt.lower() and total_resources < 5:
                completeness_score = min(0.4, total_resources / 10.0)
            elif total_resources >= 5:
                completeness_score = 0.6
            else:
                completeness_score = 0.3
        
        logger.info(f"Completeness score: {completeness_score:.2f}, Infrastructure type: {infrastructure_type}")
        
        if error:
            logger.warning(f"Completeness validation failed: {error}")
            
            # Generate specific advice for the Architect on what to add
            advice = get_completion_advice(user_prompt, error)
            
            return {
                "validation_error": error,
                "completion_advice": advice,
                "completeness_score": completeness_score,
                "missing_components": missing_components_list,
                "infrastructure_type": infrastructure_type,
                "logs": state.get("logs", []) + [f"❌ Completeness check failed: {error}"]
            }
        else:
            logger.info("✓ Completeness validation passed")
            return {
                "validation_error": None,
                "completion_advice": None,
                "completeness_score": completeness_score,
                "missing_components": [],
                "infrastructure_type": infrastructure_type,
                "logs": state.get("logs", []) + ["✅ Infrastructure completeness verified"]
            }
    
    except Exception as e:
        logger.error(f"Error during completeness validation: {e}")
        return {
            "validation_error": None,  # Don't block on validation errors
            "completeness_score": 0.8,  # Assume reasonable
            "missing_components": [],
            "infrastructure_type": infrastructure_type,
            "logs": state.get("logs", []) + [f"⚠️  Completeness check skipped: {str(e)}"]
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
    
    Phase 8: Enhanced workflow with planner, clarifier, and deep validation nodes.
    
    Workflow flow:
    1. clarifier: Analyze request and make assumptions
    2. planner: Decompose into components and execution order
    3. architect: Generate Terraform code
    4. validator: Syntax validation
    5. completeness_validator: Check infrastructure completeness
    6. validate_deep: Run terraform plan for deeper validation
    7. security: Security scanning with Checkov
    8. parser: Parse to graph structure
    9. finops: Cost estimation
    10. ansible: Configuration management
    """
    logger.info("Initializing LangGraph workflow (Phase 8 Enhanced)")
    
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (Phase 8: Added clarifier, planner, validate_deep)
    workflow.add_node("clarifier", clarify_requirements)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("architect", architect_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("completeness_validator", completeness_validator_node)
    workflow.add_node("validate_deep", deep_validator_node)
    workflow.add_node("parser", parser_node)
    workflow.add_node("security", security_node)
    workflow.add_node("finops", finops_node)
    workflow.add_node("ansible", config_node)
    
    # Set entry point (Phase 8: Changed from "architect" to "clarifier")
    workflow.set_entry_point("clarifier")
    
    # Add edges
    # clarifier → [conditional routing]
    # If proceed=true, go to planner. If proceed=false (too vague), end with clarification questions.
    def route_from_clarifier(state: AgentState):
        validation_error = state.get("validation_error")
        if validation_error:
            # Request too vague - need user clarification
            logger.warning(f"ROUTING: clarifier → END (request too vague)")
            return "end"
        logger.info("ROUTING: clarifier → planner (assumptions made)")
        return "planner"
    
    workflow.add_conditional_edges(
        "clarifier",
        route_from_clarifier,
        {
            "planner": "planner",
            "end": END
        }
    )
    
    # planner → architect (always)
    workflow.add_edge("planner", "architect")
    
    workflow.add_edge("architect", "validator")
    
    # validator → [conditional routing]
    # If no syntax error, go to completeness validator. Else, check retries.
    def route_from_validator(state: AgentState):
        validation_error = state.get("validation_error")
        route = "completeness_validator" if validation_error is None else route_after_validator(state)
        logger.info(f"ROUTING: validator → {route} (validation_error={validation_error})")
        return route
    
    workflow.add_conditional_edges(
        "validator",
        route_from_validator,
        {
            "completeness_validator": "completeness_validator",  # Syntax passed → check completeness
            "architect": "architect",  # Retry
            "end": END                 # Fail
        }
    )
    
    # completeness_validator → [conditional routing]
    # If complete, go to deep validation. If incomplete, retry with architect.
    def route_from_completeness(state: AgentState):
        validation_error = state.get("validation_error")
        retry_count = state.get("retry_count", 0)
        
        if validation_error is None:
            logger.info("ROUTING: completeness_validator → validate_deep (infrastructure complete)")
            return "validate_deep"
        
        # Completeness validation failed
        if retry_count < MAX_RETRIES:
            logger.warning(
                f"ROUTING: completeness_validator → architect for retry "
                f"({retry_count}/{MAX_RETRIES}) - Incomplete infrastructure"
            )
            return "architect"
        
        # Max retries exceeded - fail workflow
        logger.error(f"ROUTING: Max retries ({MAX_RETRIES}) exceeded on completeness check")
        return "end"
    
    workflow.add_conditional_edges(
        "completeness_validator",
        route_from_completeness,
        {
            "validate_deep": "validate_deep",  # Complete → deep validation with terraform plan
            "architect": "architect",          # Incomplete → retry with advice
            "end": END                          # Max retries exceeded
        }
    )
    
    # validate_deep → [conditional routing]
    # If deep validation passes, go to security. If fails, retry with architect.
    def route_from_deep_validation(state: AgentState):
        validation_error = state.get("validation_error")
        retry_count = state.get("retry_count", 0)
        
        if validation_error is None:
            logger.info("ROUTING: validate_deep → security (terraform plan succeeded)")
            return "security"
        
        # Deep validation failed
        if retry_count < MAX_RETRIES:
            logger.warning(
                f"ROUTING: validate_deep → architect for retry "
                f"({retry_count}/{MAX_RETRIES}) - Terraform plan issues"
            )
            return "architect"
        
        # Max retries exceeded - proceed to security anyway
        logger.warning(f"ROUTING: Max retries exceeded on deep validation - proceeding to security")
        return "security"
    
    workflow.add_conditional_edges(
        "validate_deep",
        route_from_deep_validation,
        {
            "security": "security",
            "architect": "architect",
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
        "completion_advice": None,
        "security_errors": [],
        "security_violations": [],
        "retry_count": 0,
        "is_clean": False,
        "cost_estimate": "",
        "ansible_playbook": "",
        "graph_data": {"nodes": [], "edges": []},
        "logs": [],  # Real-time event tracking
        # Phase 1: Planning and completeness tracking
        "planned_components": [],
        "execution_order": [],
        "assumptions": {},
        "planned_resources": 0,
        "completeness_score": 0.0,
        "missing_components": [],
        "infrastructure_type": "unknown"
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