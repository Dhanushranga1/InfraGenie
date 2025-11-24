# InfraGenie Backend - DevOps Toolbox API

> **Phase 1.1**: Foundation & Tools - A containerized FastAPI application with embedded DevOps CLI tools (Terraform, Ansible, Checkov, Infracost).

## 🎯 Overview

The InfraGenie backend serves as an intelligent DevOps orchestration layer. It provides a REST API that coordinates multiple AI agents (via LangChain/LangGraph) to generate, validate, secure, and cost-optimize infrastructure-as-code artifacts.

This service runs entirely within a Docker container that bundles:
- **FastAPI** - Modern Python web framework
- **Terraform** - Infrastructure provisioning
- **Ansible** - Configuration management
- **Checkov** - Security and compliance scanning
- **Infracost** - Cost estimation for cloud resources

## 📋 Prerequisites

Before running this application, ensure you have:

1. **Docker** (v20.10+)
   ```bash
   docker --version
   ```

2. **API Keys** (Required for full functionality)
   - OpenAI API Key (for GPT-4 LLM operations)
   - Infracost API Key (optional, for cost estimation)
   - AWS Credentials (optional, for actual deployments)

## 🚀 Quick Start

### 1. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
nano .env
```

### 2. Build the Docker Image

Build the container image (this may take 3-5 minutes on first run):

```bash
docker build -t infragenie-backend ./backend
```

**Expected Output:**
```
[+] Building 180.5s (15/15) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.23kB
 => [internal] load .dockerignore
 ...
 => exporting to image
 => => naming to docker.io/library/infragenie-backend
```

### 3. Run the Container

Start the FastAPI server in detached mode:

```bash
docker run -d \
  --name infragenie-backend \
  -p 8000:8000 \
  --env-file backend/.env \
  infragenie-backend
```

**With interactive logs:**
```bash
docker run --rm \
  --name infragenie-backend \
  -p 8000:8000 \
  --env-file backend/.env \
  infragenie-backend
```

### 4. Verify Installation

Check that all DevOps tools are correctly installed:

```bash
curl http://localhost:8000/health
```

**Expected Response:**
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
      "version": "Infracost v0.10.x"
    }
  }
}
```

## 🧪 Testing

### Health Check Endpoint

The `/health` endpoint verifies that all CLI tools are operational:

```bash
# Basic health check
curl -X GET http://localhost:8000/health | jq

# Check HTTP status
curl -I http://localhost:8000/health
```

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Commands Reference

### Container Management

```bash
# View running containers
docker ps

# View logs
docker logs infragenie-backend

# Follow logs in real-time
docker logs -f infragenie-backend

# Stop the container
docker stop infragenie-backend

# Remove the container
docker rm infragenie-backend

# Restart the container
docker restart infragenie-backend
```

### Image Management

```bash
# List images
docker images | grep infragenie

# Remove the image
docker rmi infragenie-backend

# Rebuild without cache
docker build --no-cache -t infragenie-backend ./backend
```

### Enter Container Shell (Debugging)

```bash
docker exec -it infragenie-backend /bin/bash
```

Inside the container, you can manually test tools:
```bash
terraform --version
checkov --version
ansible --version
infracost --version
```

## 📁 Project Structure

```
backend/
├── Dockerfile              # Multi-stage container definition
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
└── app/
    ├── main.py            # FastAPI application entry point
    ├── core/              # Core business logic (future: state, graph)
    │   └── __init__.py
    └── api/               # API route handlers (future: endpoints)
        └── __init__.py
```

## 🔧 Development Workflow

### Local Development (Without Docker)

If you prefer running without Docker:

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Note: You'll need to manually install Terraform, Checkov, Ansible, Infracost

# Run the server
uvicorn app.main:app --reload
```

### Hot Reload

The Dockerfile uses `--reload` flag for development. Changes to Python files will automatically restart the server (when mounting volumes).

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Docker Build Fails
- Ensure you have stable internet (downloads Terraform, Infracost binaries)
- Check Docker has sufficient disk space: `docker system df`
- Clean up old builds: `docker system prune -a`

### Tools Not Found in Container
```bash
# Verify tool paths inside container
docker exec infragenie-backend which terraform
docker exec infragenie-backend which checkov
```

## 📚 Next Steps (Phase 1.2)

After verifying this foundation:

1. Implement the LangChain/LangGraph orchestration (`app/core/state.py`, `app/core/graph.py`)
2. Add the Architect Agent (GPT-4 Terraform generation)
3. Implement validation, security, and cost estimation nodes
4. Create the artifact bundler and download endpoint

## 📝 License

This project is part of the InfraGenie platform. See the root LICENSE file for details.

---

**Built with ❤️ by Nexora Development Team**
