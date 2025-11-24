"""
Architect Agent - Terraform Code Generation

This module implements the core "Architect" agent, an LLM-powered system that
generates and iteratively improves Terraform infrastructure-as-code based on
user requirements, validation feedback, and security scan results.

The Architect operates as a Senior Cloud Architect persona, applying best
practices for AWS infrastructure while maintaining cost efficiency and security.

Design Philosophy:
- Generate minimal, production-ready code
- Prefer managed services over manual configuration
- Default to cost-effective instance types
- Self-correct based on validation and security feedback
"""

import logging
import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.state import AgentState

logger = logging.getLogger(__name__)


# System prompt defining the Architect's persona and rules
ARCHITECT_SYSTEM_PROMPT = """You are a **Senior Cloud Architect** specializing in AWS infrastructure.

Your job is to generate **valid, production-ready Terraform HCL code** for AWS based on user requirements.

## CRITICAL RULES:

1. **Output Format:**
   - Output ONLY raw Terraform HCL code
   - DO NOT use markdown code blocks (no ```)
   - DO NOT include explanations or comments outside the code
   - DO NOT add any text before or after the code

2. **AWS Provider Standards:**
   - Always include the AWS provider configuration
   - Use provider "aws" with region "us-east-1" unless specified otherwise
   - Include required_providers block for Terraform >= 0.13

3. **Cost Optimization:**
   - Use 't3.micro' for EC2 instances unless user specifies otherwise
   - Use 'db.t3.micro' for RDS instances in dev/test scenarios
   - Minimize data transfer costs by keeping resources in same region

4. **Security Best Practices:**
   - Never allow 0.0.0.0/0 on port 22 (SSH) or 3389 (RDP)
   - Enable encryption at rest for storage resources (EBS, S3, RDS)
   - Use security groups with least-privilege access
   - Enable versioning and logging for S3 buckets

5. **Error Handling:**
   - If validation_error is present, you MUST fix that specific error
   - Read the error message carefully and address the root cause
   - Do not add unnecessary resources to fix an error
   - Maintain the original user intent while fixing issues

6. **Security Remediation:**
   - If security_errors list is present, you MUST fix those specific violations
   - Each error is a Checkov check ID (e.g., CKV_AWS_8)
   - Research the requirement and apply the minimal fix
   - Common fixes:
     * CKV_AWS_8: Add 'encrypted = true' to aws_ebs_volume
     * CKV_AWS_23: Restrict security group ingress CIDR blocks
     * CKV_AWS_46: Add 'monitoring = true' to aws_instance

7. **Code Quality:**
   - Use meaningful resource names (no 'foo', 'bar', 'test')
   - Add concise inline comments for complex logic
   - Use variables for repeated values
   - Follow HashiCorp's style guide

## Example Output Format:

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  
  tags = {
    Name = "WebServer"
  }
}

Remember: Output ONLY the code, nothing else.
"""


def create_architect_chain():
    """
    Create the LangChain LLM chain for the Architect agent.
    
    This function initializes the ChatOpenAI model with GPT-4 and constructs
    a prompt template that includes the system message and user context.
    
    Returns:
        Runnable: A LangChain chain that can be invoked with state parameters
    
    Configuration:
    Configuration:
        - Model: llama-3.3-70b-versatile (via Groq Cloud)
        - Temperature: 0.1 (low randomness for consistent code generation)
        - Max tokens: 2000 (sufficient for most infrastructure definitions)
    """
    # Initialize the LLM via Groq Cloud
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,  # Low temperature for deterministic code generation
        max_tokens=2000,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=ARCHITECT_SYSTEM_PROMPT),
        HumanMessage(content="{user_input}")
    ])
    
    # Chain the prompt and LLM
    chain = prompt | llm
    
    return chain


def build_architect_input(state: AgentState) -> str:
    """
    Construct the input message for the Architect based on current state.
    
    This function intelligently formats the user prompt along with any error
    feedback from validation or security scans. It provides the LLM with
    complete context needed to generate or fix code.
    
    Args:
        state (AgentState): Current workflow state containing prompt and errors
    
    Returns:
        str: Formatted input string for the LLM
    
    Logic:
        - First generation: Use original user prompt
        - After validation error: Include error details
        - After security scan: Include specific check IDs to fix
        - After multiple errors: Include all context
    """
    user_prompt = state["user_prompt"]
    validation_error = state.get("validation_error")
    security_errors = state.get("security_errors", [])
    retry_count = state.get("retry_count", 0)
    
    # Build the message parts
    message_parts = []
    
    # Always include the base requirement
    if retry_count == 0:
        # First attempt - use original prompt
        message_parts.append(f"User Request: {user_prompt}")
    else:
        # Retry attempt - emphasize fixing
        message_parts.append(
            f"Original Request: {user_prompt}\n\n"
            f"This is retry attempt {retry_count}. You MUST fix the errors below."
        )
    
    # Add validation error context
    if validation_error:
        message_parts.append(
            f"\n**VALIDATION ERROR TO FIX:**\n{validation_error}\n\n"
            "Analyze this error carefully and fix the exact issue. "
            "Do not add unnecessary resources."
        )
    
    # Add security error context
    if security_errors:
        errors_list = ", ".join(security_errors)
        message_parts.append(
            f"\n**SECURITY VIOLATIONS TO FIX:**\n"
            f"Failed Checkov checks: {errors_list}\n\n"
            "For each check ID, apply the specific fix required by that policy. "
            "Do not break existing functionality while fixing security issues."
        )
    
    # Add previous code context if this is a retry
    if retry_count > 0 and state.get("terraform_code"):
        message_parts.append(
            f"\n**PREVIOUS CODE (has errors):**\n"
            f"```hcl\n{state['terraform_code']}\n```\n\n"
            "Fix the errors in the code above. Output the corrected version."
        )
    
    return "\n".join(message_parts)


def architect_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that generates or fixes Terraform code using GPT-4.
    
    This is the main entry point for the Architect Agent in the workflow graph.
    It takes the current state, builds the appropriate prompt, invokes the LLM,
    and returns updated state values.
    
    Args:
        state (AgentState): Current state of the workflow
    
    Returns:
        Dict[str, Any]: Updated state fields to merge:
            - terraform_code: The generated/fixed HCL code
            - retry_count: Incremented counter
            - validation_error: Reset to None
            - security_errors: Reset to empty list
    
    Behavior:
        1. Increment retry counter
        2. Build context-aware prompt
        3. Invoke LLM to generate code
        4. Clean up output (remove markdown fencing if present)
        5. Reset error fields for next validation cycle
        6. Log generation metadata
    
    Error Handling:
        - Catches LLM API errors and logs them
        - Returns partial state update on failure
        - Workflow can continue with previous code if needed
    
    Example State Transition:
        ```python
        # Input state
        {
            "user_prompt": "Create EC2 instance",
            "terraform_code": "",
            "validation_error": None,
            "retry_count": 0,
            ...
        }
        
        # Output state update
        {
            "terraform_code": "provider \"aws\" { ... }",
            "retry_count": 1,
            "validation_error": None,
            "security_errors": []
        }
        ```
    """
    logger.info("=" * 60)
    logger.info("ARCHITECT AGENT: Starting code generation")
    logger.info(f"Retry count: {state.get('retry_count', 0)}")
    
    try:
        # Create the LLM chain
        chain = create_architect_chain()
        
        # Build input with context
        user_input = build_architect_input(state)
        
        logger.debug(f"Architect input:\n{user_input[:300]}...")
        
        # Invoke the LLM
        logger.info("Invoking GPT-4 for code generation...")
        response = chain.invoke({"user_input": user_input})
        
        # Extract the generated code
        generated_code = response.content.strip()
        
        # Clean up the output (remove markdown fencing if present)
        if generated_code.startswith("```"):
            # Remove markdown code blocks
            lines = generated_code.split("\n")
            # Remove first line (```hcl or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            generated_code = "\n".join(lines).strip()
        
        logger.info(f"Generated {len(generated_code)} characters of Terraform code")
        logger.debug(f"Code preview:\n{generated_code[:200]}...")
        
        # Increment retry count
        new_retry_count = state.get("retry_count", 0) + 1
        
        # Return updated state
        return {
            "terraform_code": generated_code,
            "retry_count": new_retry_count,
            "validation_error": None,  # Reset for next validation
            "security_errors": [],      # Reset for next scan
        }
    
    except Exception as e:
        logger.error(f"Error in Architect Agent: {str(e)}")
        logger.exception("Full traceback:")
        
        # Return minimal update to allow workflow to continue
        return {
            "retry_count": state.get("retry_count", 0) + 1,
            "validation_error": f"Code generation error: {str(e)}"
        }
