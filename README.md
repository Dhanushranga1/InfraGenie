# InfraGenie

A production-ready AI-powered infrastructure automation platform that transforms natural language descriptions into complete cloud infrastructure using LangGraph orchestration and multi-agent workflows.

## Overview

InfraGenie combines the power of large language models with DevOps best practices to automatically generate, validate, and configure cloud infrastructure. The platform uses a sophisticated multi-agent architecture where specialized AI agents collaborate to produce secure, cost-optimized infrastructure code.

## Key Features

- **Natural Language to Infrastructure**: Describe your infrastructure requirements in plain English and receive production-ready Terraform code
- **Multi-Agent Workflow**: Specialized agents for architecture design, validation, security scanning, cost analysis, and configuration management
- **Real-Time Cost Estimation**: Integration with Infracost provides accurate monthly cost projections before deployment
- **Security Scanning**: Automated Checkov integration scans generated infrastructure for security vulnerabilities and compliance issues
- **Interactive Visualization**: Dynamic architecture diagrams with real-time updates during generation
- **Configuration Management**: Automatic Ansible playbook generation for post-deployment configuration
- **Downloadable Artifacts**: Complete infrastructure packages including Terraform files, Ansible playbooks, and documentation

## Architecture

### Backend

Built with FastAPI and Python 3.11, the backend orchestrates a LangGraph workflow with the following specialized agents:

- **Architect Agent**: Converts natural language to Terraform HCL using Groq's llama-3.3-70b-versatile model
- **Validator Agent**: Performs Terraform validation and linting to ensure syntactic correctness
- **Security Agent**: Runs Checkov security scans to identify policy violations and compliance issues
- **FinOps Agent**: Executes Infracost analysis for accurate cloud cost estimation
- **Configuration Agent**: Generates Ansible playbooks for automated post-deployment configuration

### Frontend

Modern Next.js 16 application featuring:

- React 19 with TypeScript for type-safe development
- Clerk authentication for secure user management
- ReactFlow for interactive architecture visualization with dagre layout
- TanStack Query for efficient server state management
- Zustand for client-side state management
- Markdown rendering with GitHub Flavored Markdown support
- Responsive design with Tailwind CSS 4

## Technology Stack

### Backend
- FastAPI 0.109.0
- LangChain 0.1.4
- LangGraph 0.0.20
- Groq API (llama-3.3-70b-versatile)
- Terraform (validation)
- Checkov 3.2.495 (security scanning)
- Infracost (cost analysis)
- Ansible 9.1.0 (configuration management)

### Frontend
- Next.js 16.0.3
- React 19.2.0
- TypeScript 5
- Clerk 6.35.4
- ReactFlow 12.9.3
- TanStack Query 5.90.10
- react-markdown 10.1.0
- Tailwind CSS 4

## Prerequisites

### Backend Requirements
- Python 3.11 or higher
- pip package manager
- Groq API key (obtain from https://console.groq.com)
- Infracost CLI installed
- Checkov installed globally

### Frontend Requirements
- Node.js 18 or higher
- npm or yarn package manager

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install DevOps tools:
```bash
# Install Infracost
curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh

# Install Checkov
pip install checkov
```

5. Create a `.env` file from the example:
```bash
cp .env.example .env
```

6. Configure environment variables in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
INFRACOST_API_KEY=your_infracost_api_key_here  # Optional
LANGSMITH_API_KEY=your_langsmith_key_here       # Optional for tracing
```

7. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file from the example:
```bash
cp .env.local.example .env.local
```

4. Configure Clerk authentication keys in `.env.local`:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

5. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Usage

1. Open the InfraGenie web interface at `http://localhost:3000`
2. Sign in using Clerk authentication
3. Describe your infrastructure requirements in the chat interface. Examples:
   - "Create an AWS EC2 instance with nginx server"
   - "Set up a load-balanced web application with RDS database"
   - "Deploy a containerized application on ECS with auto-scaling"
4. Watch the multi-agent workflow progress through the terminal loader
5. Review the generated infrastructure:
   - Interactive architecture diagram
   - Cost estimation badge
   - Security scan results
   - Markdown-formatted response
6. Download the complete infrastructure package as a ZIP file

## Project Structure

```
InfraGenie/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── graph.py         # LangGraph workflow definition
│   │   │   ├── state.py         # Workflow state management
│   │   │   └── agents/          # Specialized agent implementations
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   └── services/
│   │       ├── finops.py        # Cost analysis service
│   │       ├── sandbox.py       # Terraform validation
│   │       └── bundler.py       # Artifact packaging
│   ├── requirements.txt         # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main dashboard
│   │   └── layout.tsx          # Root layout with providers
│   ├── components/
│   │   ├── chat/               # Chat interface components
│   │   ├── diagram/            # Architecture visualization
│   │   └── dashboard/          # Dashboard widgets
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── store.ts            # Zustand state management
│   │   └── graph-utils.ts      # Graph layout utilities
│   └── package.json            # Node.js dependencies
└── docs/                       # Project documentation
```

## API Endpoints

### POST /api/v1/generate
Generates infrastructure from natural language description.

**Request Body**:
```json
{
  "prompt": "Create an AWS EC2 instance with nginx"
}
```

**Response**:
```json
{
  "terraform_code": "resource \"aws_instance\" \"web\" {...}",
  "ansible_code": "- name: Configure nginx...",
  "cost_estimate": "$24.50/mo",
  "security_risks": ["CKV_AWS_8: Ensure EBS volumes are encrypted"],
  "validation_status": "valid",
  "architecture_summary": "Infrastructure includes EC2 instance..."
}
```

### GET /health
Health check endpoint that verifies all DevOps tools are installed.

**Response**:
```json
{
  "status": "healthy",
  "terraform": "v1.6.0",
  "checkov": "3.2.495",
  "ansible": "2.16.2",
  "infracost": "v0.10.30"
}
```

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest tests/
```

Frontend type checking:
```bash
cd frontend
npm run build
```

### Code Style

Backend follows PEP 8 guidelines. Frontend uses ESLint configuration based on Next.js standards.

## Troubleshooting

### Backend fails to start
- Verify Python version: `python3.11 --version`
- Check virtual environment is activated
- Ensure all environment variables are set in `.env`
- Verify GROQ_API_KEY is valid

### Cost estimation shows "Unable to estimate"
- Verify Infracost is installed: `which infracost`
- Check Infracost API key is set (optional but recommended)
- Ensure Terraform code is syntactically valid

### Security scanning is skipped
- Verify Checkov is installed: `checkov --version`
- Check PATH includes Checkov installation directory
- Restart backend server after installing Checkov

### Frontend connection errors
- Verify backend is running at `http://localhost:8000`
- Check CORS configuration in `backend/app/main.py`
- Ensure no firewall blocking port 8000

### Workflow reports success: false despite generating code
- This has been fixed in the latest version
- The system now marks workflows as successful when all artifacts are generated
- Security warnings are included but do not prevent artifact delivery
- Restart backend server to apply the fix

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch with a descriptive name
3. Make your changes with clear commit messages
4. Test your changes thoroughly
5. Submit a pull request with detailed description of changes

## License

MIT License - See LICENSE file for details.

## Acknowledgments

Built with modern AI and DevOps technologies to streamline infrastructure automation and reduce manual configuration effort.
