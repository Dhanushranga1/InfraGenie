"""
API Routes - Infrastructure Generation Endpoints

This module defines the public API endpoints for InfraGenie, including
infrastructure generation and deployment kit download functionality.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.graph import run_workflow
from app.core.state import AgentState
from app.services.bundler import create_deployment_kit

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["Infrastructure"])


# Request/Response models
class GenerateRequest(BaseModel):
    """Request model for infrastructure generation."""
    prompt: str = Field(
        ...,
        description="Natural language description of desired infrastructure",
        example="Create a secure EC2 instance with SSH access and automatic backups",
        min_length=10,
        max_length=1000
    )


class GenerateResponse(BaseModel):
    """Response model for infrastructure generation.
    
    Phase 9 Enhancement: Added planning and metrics fields from enhanced state schema.
    """
    success: bool = Field(description="Whether generation completed successfully")
    terraform_code: str = Field(description="Generated Terraform HCL code")
    ansible_playbook: str = Field(description="Generated Ansible playbook YAML")
    cost_estimate: str = Field(description="Monthly cost estimate")
    validation_error: str | None = Field(description="Validation error if any")
    security_errors: list[str] = Field(description="List of security violation IDs")
    retry_count: int = Field(description="Number of retry attempts made")
    is_clean: bool = Field(description="Whether code passed all validations")
    user_prompt: str = Field(description="Original user request")
    graph_data: dict = Field(description="Structured graph data for frontend visualization")
    
    # Phase 9: New fields from enhanced state schema
    completeness_score: float = Field(
        default=1.0,
        description="Infrastructure completeness score (0.0 to 1.0)"
    )
    missing_components: list[str] = Field(
        default_factory=list,
        description="List of components that are required but missing"
    )
    infrastructure_type: str = Field(
        default="unknown",
        description="Infrastructure complexity: simple, medium, complex, or unknown"
    )
    planned_resources: int = Field(
        default=0,
        description="Expected number of resources from terraform plan"
    )
    assumptions: dict[str, str] = Field(
        default_factory=dict,
        description="Assumptions made by clarifier for missing information"
    )


class DownloadRequest(BaseModel):
    """Request model for deployment kit download."""
    project_id: str = Field(
        ...,
        description="Project identifier (currently used for naming)",
        example="my-infrastructure",
        pattern="^[a-zA-Z0-9_-]+$"
    )
    # For now, we'll use the state from the last generation
    # In production, this would query a database
    terraform_code: str = Field(..., description="Terraform code to bundle")
    ansible_playbook: str = Field(..., description="Ansible playbook to bundle")
    cost_estimate: str = Field(..., description="Cost estimate")
    user_prompt: str = Field(..., description="Original user request")


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate Infrastructure Code",
    description="Takes a natural language prompt and generates complete infrastructure-as-code with Terraform and Ansible",
    responses={
        200: {
            "description": "Infrastructure generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "terraform_code": "provider \"aws\" { ... }",
                        "ansible_playbook": "---\n- name: Configure...",
                        "cost_estimate": "$24.50/mo",
                        "validation_error": None,
                        "security_errors": [],
                        "retry_count": 1,
                        "is_clean": True,
                        "user_prompt": "Create an EC2 instance"
                    }
                }
            }
        },
        500: {"description": "Workflow execution failed"}
    }
)
async def generate_infrastructure(request: GenerateRequest) -> GenerateResponse:
    """
    Generate complete infrastructure-as-code from natural language.
    
    This endpoint orchestrates the complete LangGraph workflow:
    1. Architect generates Terraform code
    2. Validator checks syntax
    3. Security scanner checks compliance
    4. FinOps estimates costs
    5. Config agent generates Ansible playbook
    
    The workflow includes automatic error correction with up to 3 retry attempts.
    
    Args:
        request (GenerateRequest): Contains the user's infrastructure prompt
    
    Returns:
        GenerateResponse: Complete workflow state with all generated artifacts
    
    Raises:
        HTTPException: 500 if workflow execution fails
    
    Example:
        ```bash
        curl -X POST http://localhost:8000/api/v1/generate \
          -H "Content-Type: application/json" \
          -d '{
            "prompt": "Create a secure S3 bucket with versioning"
          }'
        ```
    
    Note:
        - Execution time: 30-90 seconds depending on complexity
        - Requires OPENAI_API_KEY environment variable
        - Requires INFRACOST_API_KEY for cost estimation
    """
    logger.info(f"Generate request received: {request.prompt[:50]}...")
    
    try:
        # Execute the workflow
        logger.info("Starting workflow execution...")
        result = run_workflow(request.prompt)
        
        # Format response (Phase 9: Added new metrics fields)
        response = GenerateResponse(
            success=result["is_clean"],
            terraform_code=result["terraform_code"],
            ansible_playbook=result.get("ansible_playbook", ""),
            cost_estimate=result.get("cost_estimate", "Unknown"),
            validation_error=result.get("validation_error"),
            security_errors=result.get("security_errors", []),
            retry_count=result["retry_count"],
            is_clean=result["is_clean"],
            user_prompt=result["user_prompt"],
            graph_data=result.get("graph_data", {"nodes": [], "edges": []}),
            # Phase 9: Map new state fields to response
            completeness_score=result.get("completeness_score", 1.0),
            missing_components=result.get("missing_components", []),
            infrastructure_type=result.get("infrastructure_type", "unknown"),
            planned_resources=result.get("planned_resources", 0),
            assumptions=result.get("assumptions", {})
        )
        
        # Log response data for debugging
        logger.info(f"Workflow completed. Success: {response.success}")
        logger.info(f"📦 Sending response with: terraform_code={len(response.terraform_code)} chars, "
                   f"graph_data={len(response.graph_data.get('nodes', []))} nodes, "
                   f"{len(response.graph_data.get('edges', []))} edges")
        
        return response
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Infrastructure generation failed: {str(e)}"
        )


@router.post(
    "/download",
    summary="Download Deployment Kit",
    description="Generate and download a complete deployment kit ZIP archive",
    responses={
        200: {
            "description": "ZIP file containing deployment kit",
            "content": {
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        500: {"description": "Bundle creation failed"}
    }
)
async def download_deployment_kit(request: DownloadRequest):
    """
    Download a complete deployment kit as a ZIP archive.
    
    The ZIP includes:
    - main.tf - Terraform infrastructure definition
    - playbook.yml - Ansible configuration
    - deploy.sh - Automated deployment script
    - README.md - Complete documentation
                graph_data=result.get("graph_data", {"nodes": [], "edges": []}),
    - inventory.ini - Ansible inventory template
    
    Args:
        request (DownloadRequest): Contains the project state and metadata
    
    Returns:
        StreamingResponse: ZIP file download
    
    Raises:
        HTTPException: 500 if bundle creation fails
    
    Example:
        ```bash
        # First generate infrastructure
        RESPONSE=$(curl -X POST http://localhost:8000/api/v1/generate \
          -H "Content-Type: application/json" \
          -d '{"prompt": "Create EC2 instance"}')
        
        # Then download the kit
        curl -X POST http://localhost:8000/api/v1/download \
          -H "Content-Type: application/json" \
          -d "$RESPONSE" \
          --output deployment-kit.zip
        ```
    
    Note:
        - ZIP file is generated on-the-fly
        - File size typically 10-50 KB
        - All files have proper permissions
    """
    logger.info(f"Download request for project: {request.project_id}")
    
    try:
        # Reconstruct state from request
        state: AgentState = {
            "user_prompt": request.user_prompt,
            "terraform_code": request.terraform_code,
            "ansible_playbook": request.ansible_playbook,
            "cost_estimate": request.cost_estimate,
            "validation_error": None,
            "security_errors": [],
            "retry_count": 0,
            "is_clean": True
        }
        
        # Create the deployment kit
        logger.info("Creating deployment kit bundle...")
        zip_buffer = create_deployment_kit(state)
        
        # Reset buffer position for reading
        zip_buffer.seek(0)
        
        # Generate filename
        filename = f"{request.project_id}-deployment-kit.zip"
        
        logger.info(f"✓ Deployment kit created: {filename}")
        
        # Return as streaming response
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "application/zip"
            }
        )
    
    except Exception as e:
        logger.error(f"Bundle creation failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create deployment kit: {str(e)}"
        )
