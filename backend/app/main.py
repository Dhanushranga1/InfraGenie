"""
InfraGenie Backend - FastAPI Application Entry Point

This module initializes the FastAPI application and provides a health check
endpoint that verifies the installation of critical DevOps CLI tools within
the Docker container.

The health endpoint executes subprocess calls to:
- Terraform (Infrastructure as Code)
- Checkov (Security and Compliance Scanner)
- Ansible (Configuration Management)
- Infracost (Cloud Cost Estimation)

This validates that the "DevOps Toolbox" container is correctly configured.
"""

import subprocess
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="InfraGenie Backend API",
    description="AI-powered DevOps orchestration platform with embedded Terraform, Ansible, Checkov, and Infracost",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get allowed origins from environment variable or use defaults
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://infra-genie.vercel.app",
    "https://infra-genie-git-main-dhanushranga1s-projects.vercel.app",
]

# Log CORS origins for debugging
logger.info(f"CORS configured for origins: {CORS_ORIGINS}")

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
from app.api.routes import router
app.include_router(router)


def     check_tool_version(command: list[str], tool_name: str) -> Dict[str, Any]:
    """
    Execute a CLI tool version check command and capture its output.

    This function runs a subprocess to verify that a DevOps tool is installed
    and accessible. It captures both stdout and stderr to provide detailed
    diagnostic information.

    Args:
        command (list[str]): The command to execute as a list of arguments.
                            Example: ["terraform", "--version"]
        tool_name (str): Human-readable name of the tool being checked.
                        Example: "Terraform"

    Returns:
        Dict[str, Any]: A dictionary containing:
            - installed (bool): Whether the tool executed successfully
            - version (str): The version string output by the tool
            - error (str, optional): Error message if the tool failed

    Example:
        >>> check_tool_version(["terraform", "--version"], "Terraform")
        {
            "installed": True,
            "version": "Terraform v1.7.0\non linux_amd64"
        }
    """
    try:
        logger.info(f"Checking {tool_name} installation: {' '.join(command)}")
        
        # Execute the command and capture output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,  # Prevent hanging processes
            check=False   # Don't raise exception on non-zero exit codes
        )
        
        # Check if command executed successfully
        if result.returncode == 0:
            # Prefer stdout, fallback to stderr (some tools output to stderr)
            version_output = result.stdout.strip() or result.stderr.strip()
            logger.info(f"{tool_name} check successful: {version_output.split(chr(10))[0]}")
            
            return {
                "installed": True,
                "version": version_output
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            logger.error(f"{tool_name} check failed: {error_msg}")
            
            return {
                "installed": False,
                "version": None,
                "error": error_msg
            }
    
    except subprocess.TimeoutExpired:
        error_msg = f"{tool_name} command timed out after 10 seconds"
        logger.error(error_msg)
        return {
            "installed": False,
            "version": None,
            "error": error_msg
        }
    
    except FileNotFoundError:
        error_msg = f"{tool_name} executable not found in PATH"
        logger.error(error_msg)
        return {
            "installed": False,
            "version": None,
            "error": error_msg
        }
    
    except Exception as e:
        error_msg = f"Unexpected error checking {tool_name}: {str(e)}"
        logger.error(error_msg)
        return {
            "installed": False,
            "version": None,
            "error": error_msg
        }


@app.get(
    "/health",
    summary="Health Check & Tool Verification",
    description="Verifies that the FastAPI service is running and all DevOps CLI tools are correctly installed",
    response_description="Service status and tool version information",
    tags=["Health"]
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint that verifies the operational status of the backend
    service and validates the installation of all required DevOps tools.

    This endpoint performs subprocess calls to check the following tools:
    1. **Terraform** - Infrastructure as Code provisioning
    2. **Checkov** - Security and compliance policy scanner
    3. **Ansible** - Configuration management and automation
    4. **Infracost** - Cloud cost estimation and analysis

    The endpoint will return a 200 OK status if the service is running,
    regardless of individual tool statuses. This allows for diagnostic
    information even if some tools fail.

    Returns:
        JSONResponse: A JSON object containing:
            - status (str): Overall service health ("healthy")
            - service (str): Service name
            - version (str): API version
            - tools (dict): Status of each DevOps tool with version info

    Raises:
        HTTPException: Only raised if there's a critical failure preventing
                      the endpoint from executing (rare).

    Example Response:
        ```json
        {
            "status": "healthy",
            "service": "InfraGenie Backend",
            "version": "1.0.0",
            "tools": {
                "terraform": {
                    "installed": true,
                    "version": "Terraform v1.7.0"
                },
                "checkov": {
                    "installed": true,
                    "version": "3.2.1"
                },
                "ansible": {
                    "installed": true,
                    "version": "ansible [core 2.16.2]"
                },
                "infracost": {
                    "installed": true,
                    "version": "Infracost v0.10.35"
                }
            }
        }
        ```

    Usage:
        ```bash
        curl http://localhost:8000/health
        ```
    """
    logger.info("Health check endpoint called")
    
    # Define the tools to check with their respective commands
    tools_to_check = {
        "terraform": {
            "command": ["terraform", "--version"],
            "name": "Terraform"
        },
        "checkov": {
            "command": ["checkov", "--version"],
            "name": "Checkov"
        },
        "ansible": {
            "command": ["ansible", "--version"],
            "name": "Ansible"
        },
        "infracost": {
            "command": ["infracost", "--version"],
            "name": "Infracost"
        }
    }
    
    # Check each tool
    tools_status = {}
    all_tools_installed = True
    
    for tool_key, tool_info in tools_to_check.items():
        tool_status = check_tool_version(
            command=tool_info["command"],
            tool_name=tool_info["name"]
        )
        tools_status[tool_key] = tool_status
        
        if not tool_status["installed"]:
            all_tools_installed = False
            logger.warning(f"{tool_info['name']} is not properly installed")
    
    # Prepare response
    response_data = {
        "status": "healthy" if all_tools_installed else "degraded",
        "service": "InfraGenie Backend",
        "version": "1.0.0",
        "tools": tools_status
    }
    
    # Log overall status
    if all_tools_installed:
        logger.info("Health check passed: All tools are operational")
    else:
        logger.warning("Health check passed with warnings: Some tools are not available")
    
    return JSONResponse(
        status_code=200,
        content=response_data
    )


@app.get(
    "/",
    summary="Root Endpoint",
    description="Returns basic API information",
    tags=["Root"]
)
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information.

    Returns:
        Dict[str, str]: Welcome message and documentation links.
    """
    return {
        "message": "Welcome to InfraGenie Backend API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "test_workflow": "/test/generate"
    }


# Pydantic model for test generation request
class TestGenerateRequest(BaseModel):
    """Request model for test workflow execution."""
    prompt: str = Field(
        ...,
        description="Infrastructure request in natural language",
        example="Create an EC2 instance with SSH access"
    )


class TestGenerateResponse(BaseModel):
    """Response model for test workflow execution."""
    success: bool
    terraform_code: str
    validation_error: str | None
    security_errors: list[str]
    retry_count: int
    is_clean: bool


@app.post(
    "/test/generate",
    response_model=TestGenerateResponse,
    summary="Test Workflow Execution",
    description="Test endpoint to manually trigger the LangGraph workflow for development and debugging",
    tags=["Testing"]
)
async def test_generate(request: TestGenerateRequest) -> TestGenerateResponse:
    """
    Test endpoint for manually executing the infrastructure generation workflow.
    
    This endpoint is designed for Phase 1.2 testing and debugging. It allows
    you to test the complete LangGraph workflow without setting up the full
    API infrastructure.
    
    **WARNING**: This endpoint requires a valid OPENAI_API_KEY in your environment.
    
    Args:
        request (TestGenerateRequest): Contains the user's infrastructure prompt
    
    Returns:
        TestGenerateResponse: Complete workflow state including generated code
            and any errors encountered
    
    Example Request:
        ```bash
        curl -X POST http://localhost:8000/test/generate \
          -H "Content-Type: application/json" \
          -d '{"prompt": "Create a secure S3 bucket"}'
        ```
    
    Example Response:
        ```json
        {
            "success": true,
            "terraform_code": "provider \"aws\" {...}",
            "validation_error": null,
            "security_errors": [],
            "retry_count": 1,
            "is_clean": true
        }
        ```
    
    Note:
        - This endpoint may take 30-60 seconds to complete
        - Multiple retries may occur if validation or security checks fail
        - The workflow will automatically attempt to fix errors up to 3 times
    """
    logger.info(f"Test generation request received: {request.prompt[:50]}...")
    
    try:
        # Import here to avoid startup errors if dependencies not installed
        from app.core.graph import run_workflow
        
        # Execute the workflow
        logger.info("Starting workflow execution...")
        result = run_workflow(request.prompt)
        
        # Format response
        response = TestGenerateResponse(
            success=result["is_clean"],
            terraform_code=result["terraform_code"],
            validation_error=result.get("validation_error"),
            security_errors=result.get("security_errors", []),
            retry_count=result["retry_count"],
            is_clean=result["is_clean"]
        )
        
        logger.info(f"Workflow completed. Success: {response.success}")
        return response
    
    except ImportError as e:
        logger.error(f"Failed to import workflow: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow system not available. Missing dependencies: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution error: {str(e)}"
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Logs application startup and performs any necessary initialization.
    """
    logger.info("=" * 60)
    logger.info("InfraGenie Backend API starting up...")
    logger.info("FastAPI application initialized successfully")
    logger.info("Documentation available at /docs")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Performs cleanup tasks before the application terminates.
    """
    logger.info("InfraGenie Backend API shutting down...")
    logger.info("Cleanup completed successfully")


if __name__ == "__main__":
    # This block is used for local development without Docker
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
