"""
Planner Agent - Infrastructure Requirements Decomposition

This module implements a meta-agent that analyzes user infrastructure requests
and breaks them down into specific, ordered component requirements before code
generation begins.

The Problem:
- Users request complex infrastructure in simple terms ("create a K8s cluster")
- LLMs jump straight to code generation without planning
- Result: Missing components, wrong dependencies, incomplete infrastructure

The Solution:
- Analyze user request for complexity and requirements
- Identify all needed components (networking, security, compute, etc.)
- Determine execution order based on dependencies
- Create structured plan that guides code generation

Design Philosophy:
- Think before acting (planning phase before code generation)
- Make dependencies explicit (VPC must come before subnets)
- Capture assumptions (default to AWS if not specified)
- Provide detailed component specifications
"""

import logging
import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


# System prompt for the planner agent
PLANNER_SYSTEM_PROMPT = """You are an **Infrastructure Planning Specialist** with expertise in cloud architecture and resource dependencies.

Your job is to analyze infrastructure requests and create a **detailed execution plan** before any code is generated.

## YOUR TASK

Given a user's infrastructure request, you must:

1. **Identify the cloud provider** (AWS, Azure, GCP, or "unspecified" if unclear)
2. **Classify the complexity**: "simple" (1-3 resources), "medium" (4-9 resources), or "complex" (10+ resources)
3. **List all required components** with:
   - Component name (e.g., "VPC", "EKS Cluster", "IAM Roles")
   - Resource type (e.g., "networking", "compute", "identity", "security")
   - Brief description of purpose
   - Dependencies (which other components must exist first)
4. **Determine execution order** (respecting dependencies)
5. **Document assumptions** (region, instance sizes, etc.)

## OUTPUT FORMAT

You MUST output valid JSON in this exact structure:

```json
{
  "infrastructure_type": "simple" | "medium" | "complex",
  "cloud_provider": "aws" | "azure" | "gcp" | "unspecified",
  "components": [
    {
      "name": "Component Name",
      "resource_type": "networking" | "compute" | "identity" | "security" | "storage" | "database",
      "description": "Brief purpose description",
      "dependencies": ["Other Component Name", ...]
    }
  ],
  "execution_order": ["Component 1", "Component 2", ...],
  "assumptions": {
    "region": "us-east-1",
    "instance_type": "t3.micro",
    ...
  }
}
```

## EXAMPLES

### Example 1: Simple EC2 Instance
**User Request**: "Create an EC2 instance"

**Your Response**:
```json
{
  "infrastructure_type": "simple",
  "cloud_provider": "aws",
  "components": [
    {
      "name": "Security Group",
      "resource_type": "security",
      "description": "Firewall rules for instance access",
      "dependencies": []
    },
    {
      "name": "SSH Key Pair",
      "resource_type": "security",
      "description": "SSH key for instance access",
      "dependencies": []
    },
    {
      "name": "EC2 Instance",
      "resource_type": "compute",
      "description": "Virtual machine",
      "dependencies": ["Security Group", "SSH Key Pair"]
    }
  ],
  "execution_order": ["Security Group", "SSH Key Pair", "EC2 Instance"],
  "assumptions": {
    "region": "us-east-1",
    "instance_type": "t3.micro",
    "ami": "Ubuntu 22.04 LTS"
  }
}
```

### Example 2: Kubernetes Cluster (Complex)
**User Request**: "Create a Kubernetes cluster"

**Your Response**:
```json
{
  "infrastructure_type": "complex",
  "cloud_provider": "aws",
  "components": [
    {
      "name": "VPC",
      "resource_type": "networking",
      "description": "Virtual private cloud for cluster isolation",
      "dependencies": []
    },
    {
      "name": "Subnets",
      "resource_type": "networking",
      "description": "Public and private subnets across availability zones",
      "dependencies": ["VPC"]
    },
    {
      "name": "Internet Gateway",
      "resource_type": "networking",
      "description": "Internet access for public subnets",
      "dependencies": ["VPC"]
    },
    {
      "name": "NAT Gateway",
      "resource_type": "networking",
      "description": "Outbound internet for private subnets",
      "dependencies": ["VPC", "Subnets"]
    },
    {
      "name": "Route Tables",
      "resource_type": "networking",
      "description": "Routing configuration for subnets",
      "dependencies": ["VPC", "Internet Gateway", "NAT Gateway"]
    },
    {
      "name": "IAM Cluster Role",
      "resource_type": "identity",
      "description": "Permissions for EKS cluster management",
      "dependencies": []
    },
    {
      "name": "IAM Node Group Role",
      "resource_type": "identity",
      "description": "Permissions for worker nodes",
      "dependencies": []
    },
    {
      "name": "Security Groups",
      "resource_type": "security",
      "description": "Network access control for cluster and nodes",
      "dependencies": ["VPC"]
    },
    {
      "name": "EKS Cluster",
      "resource_type": "compute",
      "description": "Managed Kubernetes control plane",
      "dependencies": ["VPC", "Subnets", "IAM Cluster Role", "Security Groups"]
    },
    {
      "name": "EKS Node Group",
      "resource_type": "compute",
      "description": "Worker nodes for running pods",
      "dependencies": ["EKS Cluster", "IAM Node Group Role", "Subnets"]
    }
  ],
  "execution_order": [
    "VPC",
    "Subnets",
    "Internet Gateway",
    "NAT Gateway",
    "Route Tables",
    "IAM Cluster Role",
    "IAM Node Group Role",
    "Security Groups",
    "EKS Cluster",
    "EKS Node Group"
  ],
  "assumptions": {
    "region": "us-east-1",
    "kubernetes_version": "1.27",
    "node_instance_type": "t3.medium",
    "node_count": "2",
    "availability_zones": "2"
  }
}
```

## CRITICAL RULES

1. **Always output valid JSON** - no markdown code fences, no explanations outside JSON
2. **Be comprehensive** - include ALL necessary components for complete infrastructure
3. **Respect dependencies** - networking before compute, IAM before resources that use roles
4. **Make reasonable assumptions** - default to AWS us-east-1, cost-effective instance types
5. **Match complexity to request**:
   - Simple: Basic single-resource setups (EC2, S3 bucket)
   - Medium: Multi-resource setups (RDS with networking, load balanced app)
   - Complex: Distributed systems (Kubernetes, multi-tier apps, high-availability setups)

## COMMON PATTERNS

### Database (Medium)
- VPC, Subnets, Security Group, DB Subnet Group, RDS Instance

### Load Balanced Web App (Medium)
- VPC, Subnets, Security Groups, EC2 Instances, Target Group, Application Load Balancer

### Serverless API (Simple to Medium)
- Lambda Function, API Gateway, IAM Role, (optionally) DynamoDB Table

### Container Application (Complex)
- VPC, Subnets, ECS Cluster, Task Definition, Service, Load Balancer, IAM Roles

Remember: Your plan guides the code generation process. Be thorough but realistic!
"""


def create_planner_chain():
    """
    Create the LangChain LLM chain for the Planner agent.
    
    Returns:
        Runnable: A LangChain chain that can be invoked with user requests
    """
    # Initialize the LLM via Groq Cloud
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,  # Slightly higher for creative planning
        max_tokens=2000,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    return llm


def planner_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node that analyzes user requests and creates infrastructure plans.
    
    This agent runs BEFORE the architect to decompose complex requests into
    specific, ordered component requirements.
    
    Args:
        state: Current workflow state containing user_prompt
        
    Returns:
        Updated state with planning fields populated:
            - planned_components: List of component dictionaries
            - execution_order: List of component names in dependency order
            - assumptions: Dictionary of assumptions made
            - infrastructure_type: Complexity classification
    """
    logger.info("=" * 60)
    logger.info("PLANNER AGENT: Analyzing infrastructure request")
    
    user_prompt = state.get("user_prompt", "")
    
    if not user_prompt:
        logger.error("No user prompt provided to planner")
        return {
            "planned_components": [],
            "execution_order": [],
            "assumptions": {},
            "infrastructure_type": "unknown",
            "logs": state.get("logs", []) + ["⚠️  Planning skipped: No user prompt"]
        }
    
    try:
        # Create the LLM chain
        llm = create_planner_chain()
        
        # Build messages
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Create an execution plan for this infrastructure request:\n\n{user_prompt}")
        ]
        
        logger.info(f"Invoking planner LLM for: {user_prompt[:100]}...")
        
        # Invoke the LLM
        response = llm.invoke(messages)
        
        # Parse JSON response (handle potential markdown fencing)
        response_text = response.content.strip()
        
        # Remove markdown code fences if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            plan = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse planner JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            
            # Fallback: basic plan
            return {
                "planned_components": [],
                "execution_order": [],
                "assumptions": {"region": "us-east-1"},
                "infrastructure_type": "unknown",
                "logs": state.get("logs", []) + ["⚠️  Planning failed: JSON parse error"]
            }
        
        # Extract fields from plan
        planned_components = plan.get("components", [])
        execution_order = plan.get("execution_order", [])
        assumptions = plan.get("assumptions", {})
        infrastructure_type = plan.get("infrastructure_type", "unknown")
        cloud_provider = plan.get("cloud_provider", "aws")
        
        # Log the plan
        logger.info(f"✓ Plan created: {infrastructure_type} infrastructure on {cloud_provider}")
        logger.info(f"  Components: {len(planned_components)}")
        logger.info(f"  Execution order: {', '.join(execution_order[:5])}...")
        logger.info(f"  Assumptions: {assumptions}")
        
        # Create log message
        log_message = (
            f"📋 Plan created: {infrastructure_type} infrastructure with "
            f"{len(planned_components)} components"
        )
        
        return {
            "planned_components": planned_components,
            "execution_order": execution_order,
            "assumptions": assumptions,
            "infrastructure_type": infrastructure_type,
            "logs": state.get("logs", []) + [log_message]
        }
    
    except Exception as e:
        logger.error(f"Error in Planner Agent: {str(e)}", exc_info=True)
        
        # Return minimal planning state to allow workflow to continue
        return {
            "planned_components": [],
            "execution_order": [],
            "assumptions": {"region": "us-east-1"},
            "infrastructure_type": "unknown",
            "logs": state.get("logs", []) + [f"⚠️  Planning error: {str(e)}"]
        }
