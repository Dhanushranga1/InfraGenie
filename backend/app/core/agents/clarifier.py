"""
Requirement Clarifier Agent - Ambiguity Resolution

This module implements an agent that identifies missing critical information
in user requests and makes explicit assumptions to proceed with infrastructure
generation.

The Problem:
- Users make vague requests ("create a cluster", "set up database")
- Missing critical details (cloud provider, region, sizing, etc.)
- System makes implicit assumptions without transparency
- Results may not match user expectations

The Solution:
- Analyze request completeness
- Identify specific missing information
- Make reasonable default assumptions
- Document all assumptions clearly
- Optionally ask clarifying questions for critical gaps

Design Philosophy:
- Prefer proceeding with documented assumptions over blocking
- Make assumptions explicit and visible
- Use industry-standard defaults (AWS, us-east-1, t3.micro, etc.)
- Only block on truly ambiguous requests
"""

import logging
import os
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.model_config import create_lightweight_llm  # Use lightweight model for analysis

logger = logging.getLogger(__name__)


# System prompt for the clarifier agent
CLARIFIER_SYSTEM_PROMPT = """You are a **Requirements Clarifier** specializing in infrastructure specifications.

Your job is to analyze user infrastructure requests and identify missing information, then make **explicit assumptions** to proceed.

## YOUR TASK

Given a user's infrastructure request, determine:

1. **What critical information is specified** (cloud provider, region, sizing, etc.)
2. **What information is missing** (ambiguous or unspecified)
3. **Whether we can proceed** with reasonable assumptions
4. **What assumptions to make** for missing details
5. **What questions to ask** if truly ambiguous

## INFORMATION CHECKLIST

Check for these critical details:
- **Cloud Provider**: AWS, Azure, GCP, or multi-cloud?
- **Region/Location**: Which data center region?
- **Environment**: Production, staging, development, test?
- **Sizing**: Instance types, node counts, storage sizes?
- **Networking**: VPC details, IP ranges, connectivity requirements?
- **Security**: Access control, encryption, compliance needs?
- **High Availability**: Single-AZ or multi-AZ deployment?

## OUTPUT FORMAT

You MUST output valid JSON in this exact structure:

```json
{
  "proceed": true | false,
  "missing_info": ["List of missing details"],
  "assumptions": {
    "cloud_provider": "aws | azure | gcp",
    "region": "us-east-1 | etc",
    "environment": "development | staging | production",
    "instance_type": "t3.micro | etc",
    ...
  },
  "clarification_questions": ["Question 1?", "Question 2?"]
}
```

**proceed**: Set to `false` ONLY if request is so vague we can't determine what to build.

**missing_info**: List what wasn't specified (for transparency).

**assumptions**: Concrete defaults we'll use for missing information.

**clarification_questions**: User-friendly questions to ask (empty if proceed=true).

## EXAMPLES

### Example 1: Specific Request
**User Request**: "Create an EKS cluster in us-west-2 with 3 t3.large nodes"

**Your Response**:
```json
{
  "proceed": true,
  "missing_info": ["environment type", "networking details", "storage requirements"],
  "assumptions": {
    "cloud_provider": "aws",
    "region": "us-west-2",
    "environment": "development",
    "kubernetes_version": "1.27",
    "node_count": "3",
    "node_instance_type": "t3.large",
    "networking": "new VPC with public and private subnets",
    "high_availability": "single availability zone"
  },
  "clarification_questions": []
}
```

### Example 2: Moderate Ambiguity
**User Request**: "Create a Kubernetes cluster"

**Your Response**:
```json
{
  "proceed": true,
  "missing_info": ["cloud provider", "region", "sizing", "environment"],
  "assumptions": {
    "cloud_provider": "aws",
    "region": "us-east-1",
    "environment": "development",
    "kubernetes_version": "1.27",
    "node_count": "2",
    "node_instance_type": "t3.medium",
    "networking": "new VPC with public and private subnets across 2 availability zones",
    "high_availability": "multi-AZ for production-readiness"
  },
  "clarification_questions": []
}
```

### Example 3: High Ambiguity
**User Request**: "Create something"

**Your Response**:
```json
{
  "proceed": false,
  "missing_info": ["what to create", "infrastructure type", "purpose", "requirements"],
  "assumptions": {},
  "clarification_questions": [
    "What type of infrastructure do you want to create? (e.g., web server, database, Kubernetes cluster, storage bucket)",
    "What cloud provider would you like to use? (AWS, Azure, or Google Cloud)",
    "What is the purpose of this infrastructure? (development, testing, or production)"
  ]
}
```

### Example 4: Vague but Inferrable
**User Request**: "Set up a database"

**Your Response**:
```json
{
  "proceed": true,
  "missing_info": ["database type", "cloud provider", "region", "sizing"],
  "assumptions": {
    "cloud_provider": "aws",
    "region": "us-east-1",
    "database_type": "postgresql",
    "database_version": "15",
    "instance_class": "db.t3.micro",
    "storage": "20GB",
    "environment": "development",
    "multi_az": false,
    "backup_retention": "7 days"
  },
  "clarification_questions": []
}
```

## DECISION RULES

**Proceed = TRUE** (make assumptions) when:
- Infrastructure type is clear (even if details are missing)
- Request can be fulfilled with industry-standard defaults
- Assumptions are reasonable and documented

**Proceed = FALSE** (ask questions) when:
- Completely vague ("create something", "help me")
- Multiple contradictory interpretations possible
- Critical information affects architecture significantly

## DEFAULT ASSUMPTIONS (Use These)

- **Cloud Provider**: AWS (most popular)
- **Region**: us-east-1 (AWS default)
- **Environment**: development (safe default)
- **Instance Sizes**: t3.micro for compute, db.t3.micro for databases (cost-effective)
- **Availability**: Single-AZ for dev, multi-AZ for inferred production
- **Networking**: New VPC with standard CIDR (10.0.0.0/16)
- **Security**: Minimal access (no public exposure unless required)
- **Storage**: 20GB for databases, 8GB for EBS volumes (reasonable starting points)

## CRITICAL RULES

1. **Always output valid JSON** - no markdown, no explanations outside JSON
2. **Prefer proceeding over blocking** - if in doubt, assume and document
3. **Make explicit assumptions** - never leave assumptions implicit
4. **Be conservative with sizing** - default to smaller/cheaper resources
5. **Prioritize security** - never assume public access unless explicitly requested
6. **Document everything** - transparency builds trust

Remember: Your goal is to enable infrastructure generation by filling gaps, not to block progress!
"""


def create_clarifier_chain():
    """
    Create the LangChain LLM chain for the Clarifier agent.
    Uses lightweight model for fast, efficient analysis.
    
    Returns:
        Runnable: A LangChain chain that can be invoked with user requests
    """
    # Use lightweight model for analysis tasks (8b model - 70% fewer tokens)
    llm = create_lightweight_llm(
        temperature=0.3,  # Slightly higher for creative assumption-making
        max_tokens=1000   # Analysis doesn't need many tokens
    )
    
    return llm


def clarify_requirements(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node that analyzes user requests for completeness and makes assumptions.
    
    This agent runs FIRST in the workflow to ensure we have enough information
    to proceed with infrastructure generation.
    
    Args:
        state: Current workflow state containing user_prompt
        
    Returns:
        Updated state with:
            - assumptions: Dictionary of assumptions made
            - validation_error: Set if request is too vague to proceed
    """
    logger.info("=" * 60)
    logger.info("CLARIFIER AGENT: Analyzing request completeness")
    
    user_prompt = state.get("user_prompt", "")
    
    if not user_prompt:
        logger.error("No user prompt provided to clarifier")
        return {
            "assumptions": {},
            "validation_error": "No infrastructure request provided",
            "logs": state.get("logs", []) + ["❌ Clarification failed: Empty request"]
        }
    
    try:
        # Create the LLM chain
        llm = create_clarifier_chain()
        
        # Build messages
        messages = [
            SystemMessage(content=CLARIFIER_SYSTEM_PROMPT),
            HumanMessage(content=f"Analyze this infrastructure request and determine if we can proceed:\n\n{user_prompt}")
        ]
        
        logger.info(f"Invoking clarifier LLM for: {user_prompt[:100]}...")
        
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
            clarification = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clarifier JSON response: {e}")
            logger.debug(f"Response text: {response_text[:500]}")
            
            # Fallback: proceed with basic assumptions
            return {
                "assumptions": {
                    "cloud_provider": "aws",
                    "region": "us-east-1",
                    "environment": "development"
                },
                "validation_error": None,
                "logs": state.get("logs", []) + ["⚠️  Clarification parse error - using defaults"]
            }
        
        # Extract fields
        proceed = clarification.get("proceed", True)
        missing_info = clarification.get("missing_info", [])
        assumptions = clarification.get("assumptions", {})
        clarification_questions = clarification.get("clarification_questions", [])
        
        # Check if we should proceed
        if not proceed:
            # Request is too vague - need user clarification
            questions_text = "\n".join(f"- {q}" for q in clarification_questions)
            error_message = f"Request needs clarification:\n\n{questions_text}"
            
            logger.warning(f"Request too vague: {clarification_questions}")
            
            return {
                "assumptions": {},
                "validation_error": error_message,
                "logs": state.get("logs", []) + ["❌ Request too vague - clarification needed"]
            }
        
        # We can proceed - log assumptions
        logger.info(f"✓ Proceeding with {len(assumptions)} assumptions")
        logger.info(f"  Missing info: {', '.join(missing_info)}")
        
        # Format assumptions for logging
        assumptions_summary = ", ".join(f"{k}={v}" for k, v in list(assumptions.items())[:5])
        if len(assumptions) > 5:
            assumptions_summary += f", +{len(assumptions)-5} more"
        
        log_message = f"✅ Requirements clarified: {len(missing_info)} assumptions made ({assumptions_summary})"
        
        return {
            "assumptions": assumptions,
            "validation_error": None,
            "logs": state.get("logs", []) + [log_message]
        }
    
    except Exception as e:
        logger.error(f"Error in Clarifier Agent: {str(e)}", exc_info=True)
        
        # Fallback: proceed with minimal assumptions
        return {
            "assumptions": {
                "cloud_provider": "aws",
                "region": "us-east-1",
                "environment": "development"
            },
            "validation_error": None,
            "logs": state.get("logs", []) + [f"⚠️  Clarifier error - using fallback defaults"]
        }
