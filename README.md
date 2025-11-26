# 🚀 InfraGenie - AI-Powered Infrastructure as Code Generator# InfraGenie



<div align="center">A production-ready AI-powered infrastructure automation platform that transforms natural language descriptions into complete cloud infrastructure using LangGraph orchestration and multi-agent workflows.



![InfraGenie](https://img.shields.io/badge/InfraGenie-v1.0-purple?style=for-the-badge&logo=terraform)## Overview

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)

![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=for-the-badge&logo=typescript)InfraGenie combines the power of large language models with DevOps best practices to automatically generate, validate, and configure cloud infrastructure. The platform uses a sophisticated multi-agent architecture where specialized AI agents collaborate to produce secure, cost-optimized infrastructure code.

![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=for-the-badge&logo=fastapi)

![Next.js](https://img.shields.io/badge/Next.js-14+-black?style=for-the-badge&logo=next.js)## Key Features



**Generate production-ready Terraform infrastructure with AI, complete with security scanning, cost estimation, and self-healing capabilities.**- **Natural Language to Infrastructure**: Describe your infrastructure requirements in plain English and receive production-ready Terraform code

- **Multi-Agent Workflow**: Specialized agents for architecture design, validation, security scanning, cost analysis, and configuration management

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation)- **Real-Time Cost Estimation**: Integration with Infracost provides accurate monthly cost projections before deployment

- **Security Scanning**: Automated Checkov integration scans generated infrastructure for security vulnerabilities and compliance issues

</div>- **Interactive Visualization**: Dynamic architecture diagrams with real-time updates during generation

- **Configuration Management**: Automatic Ansible playbook generation for post-deployment configuration

---- **Downloadable Artifacts**: Complete infrastructure packages including Terraform files, Ansible playbooks, and documentation



## ✨ Features## Architecture



### 🤖 **AI-Powered Code Generation**### Backend

- Natural language to Terraform conversion using Groq LLM (llama-3.3-70b-versatile)

- Context-aware infrastructure design following AWS best practicesBuilt with FastAPI and Python 3.11, the backend orchestrates a LangGraph workflow with the following specialized agents:

- Multi-agent LangGraph workflow for iterative improvement

- **Architect Agent**: Converts natural language to Terraform HCL using Groq's llama-3.3-70b-versatile model

### 🔒 **Self-Healing Security Loop**- **Validator Agent**: Performs Terraform validation and linting to ensure syntactic correctness

- Automatic Checkov security scanning- **Security Agent**: Runs Checkov security scans to identify policy violations and compliance issues

- **MODE 1 (CREATION)**: Proactive security hardening- **FinOps Agent**: Executes Infracost analysis for accurate cloud cost estimation

- **MODE 2 (REMEDIATION)**: Intelligent, targeted vulnerability fixes- **Configuration Agent**: Generates Ansible playbooks for automated post-deployment configuration

- Detailed violation tracking with specific remediation guidance

- Supports 13+ common security checks (EC2, S3, RDS, VPC, IAM)### Frontend



### 📊 **Professional Architecture Visualization**Modern Next.js 16 application featuring:

- Real-time infrastructure graph rendering

- AWS Architecture Icons style with color-coded resource categories- React 19 with TypeScript for type-safe development

- Hierarchical layout with swim lanes (Network, Security, Compute, Storage, Database)- Clerk authentication for secure user management

- Interactive diagram with zoom, pan, and node inspection- ReactFlow for interactive architecture visualization with dagre layout

- **Eraser.io-inspired professional design**- TanStack Query for efficient server state management

- Zustand for client-side state management

### 💰 **Cost Optimization**- Markdown rendering with GitHub Flavored Markdown support

- Real-time cost estimation using AWS pricing- Responsive design with Tailwind CSS 4

- Budget-aware resource recommendations

- Cost breakdown by resource type## Technology Stack



### 🎯 **Production-Ready Output**### Backend

- Validated Terraform HCL code- FastAPI 0.109.0

- Ansible playbooks for deployment- LangChain 0.1.4

- Complete resource relationship mapping- LangGraph 0.0.20

- Infrastructure state tracking- Groq API (llama-3.3-70b-versatile)

- Terraform (validation)

---- Checkov 3.2.495 (security scanning)

- Infracost (cost analysis)

## 🚀 Quick Start- Ansible 9.1.0 (configuration management)



### **One-Click Setup** ✨### Frontend

- Next.js 16.0.3

```bash- React 19.2.0

# Clone the repository- TypeScript 5

git clone https://github.com/Dhanushranga1/InfraGenie.git- Clerk 6.35.4

cd InfraGenie- ReactFlow 12.9.3

- TanStack Query 5.90.10

# Run the automated setup script- react-markdown 10.1.0

./setup.sh- Tailwind CSS 4

```

## Prerequisites

The setup script will:

- ✅ Check all prerequisites (Python, Node.js, Terraform)### Backend Requirements

- ✅ Create virtual environments- Python 3.11 or higher

- ✅ Install all dependencies (backend + frontend)- pip package manager

- ✅ Generate `.env` configuration files- Groq API key (obtain from https://console.groq.com)

- ✅ Create helper scripts (`start.sh`, `test.sh`)- Infracost CLI installed

- ✅ Verify the installation- Checkov installed globally



```bash### Frontend Requirements

# Add your Groq API key to backend/.env- Node.js 18 or higher

# Get your free API key from: https://console.groq.com/keys- npm or yarn package manager



# Start both backend and frontend## Installation

./start.sh

```### Backend Setup



**That's it!** 🎉 Open [http://localhost:3000](http://localhost:3000)1. Navigate to the backend directory:

```bash

---cd backend

```

## 🏗️ Architecture

2. Create and activate a virtual environment:

### **System Overview**```bash

python3.11 -m venv venv

```source venv/bin/activate  # On Windows: venv\Scripts\activate

┌────────────────────────────────────────────────────────────────┐```

│                   User Interface (Next.js 14)                   │

│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │3. Install Python dependencies:

│  │  Chat Input  │  │ Code Editor  │  │ Architecture Viewer │  │```bash

│  │  (Natural    │  │  (Monaco)    │  │  (ReactFlow Pro)    │  │pip install -r requirements.txt

│  │  Language)   │  │              │  │                     │  │```

│  └──────────────┘  └──────────────┘  └─────────────────────┘  │

└────────────────────────┬───────────────────────────────────────┘4. Install DevOps tools:

                         │ REST API (JSON)```bash

┌────────────────────────▼───────────────────────────────────────┐# Install Infracost

│                    FastAPI Backend (Python)                     │curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh

│  ┌────────────────────────────────────────────────────────────┐│

│  │          LangGraph Multi-Agent Workflow Engine            ││# Install Checkov

│  │                                                            ││pip install checkov

│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐           ││```

│  │  │Architect │ ──→│Validator │──→ │  Parser  │           ││

│  │  │  Agent   │    │  Agent   │    │  Agent   │           ││5. Create a `.env` file from the example:

│  │  └────┬─────┘    └──────────┘    └──────────┘           ││```bash

│  │       │  ↑                            │                  ││cp .env.example .env

│  │       │  │                            ↓                  ││```

│  │       │  │         ┌──────────┐    ┌──────────┐         ││

│  │       │  └─────────│ Security │←───│  FinOps  │         ││6. Configure environment variables in `.env`:

│  │       │            │  Agent   │    │  Agent   │         ││```

│  │       │            └──────────┘    └──────────┘         ││GROQ_API_KEY=your_groq_api_key_here

│  │       │                 │                               ││INFRACOST_API_KEY=your_infracost_api_key_here  # Optional

│  │       └─────────────────┘                               ││LANGSMITH_API_KEY=your_langsmith_key_here       # Optional for tracing

│  │         Self-Healing Loop (MODE 2)                      ││```

│  └────────────────────────────────────────────────────────────┘│

│                                                                 │7. Start the backend server:

│  ┌───────────────┐  ┌───────────────┐  ┌──────────────────┐  │```bash

│  │ HCL Parser    │  │   Checkov     │  │  Groq LLM API    │  │uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

│  │ (python-hcl2) │  │  (Security)   │  │  (Llama 3.3)     │  │```

│  └───────────────┘  └───────────────┘  └──────────────────┘  │

└─────────────────────────────────────────────────────────────────┘The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

```

### Frontend Setup

### **Self-Healing Security Workflow**

1. Navigate to the frontend directory:

``````bash

User Prompt: "Create a web server"cd frontend

         │```

         ▼

┌─────────────────────────────────────────┐2. Install dependencies:

│ Architect Agent (MODE 1: CREATION)     │```bash

│ • Generate secure infrastructure        │npm install

│ • Apply proactive security hardening    │```

│ • Use cost-optimized instance types     │

└─────────────┬───────────────────────────┘3. Create a `.env.local` file from the example:

              │ terraform_code```bash

              ▼cp .env.local.example .env.local

┌─────────────────────────────────────────┐```

│ Validator Agent                         │

│ • Terraform syntax validation           │4. Configure Clerk authentication keys in `.env.local`:

│ • Check resource references             │```

└─────────────┬───────────────────────────┘NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key

              │ ✓ ValidCLERK_SECRET_KEY=your_clerk_secret_key

              ▼```

┌─────────────────────────────────────────┐

│ Parser Agent                            │5. Start the development server:

│ • Extract resources from HCL            │```bash

│ • Build dependency graph                │npm run dev

│ • Detect relationships                  │```

└─────────────┬───────────────────────────┘

              │ graph_dataThe application will be available at `http://localhost:3000`.

              ▼

┌─────────────────────────────────────────┐## Usage

│ Security Agent (Checkov)                │

│ • Scan for vulnerabilities              │1. Open the InfraGenie web interface at `http://localhost:3000`

│ • Extract detailed violation info       │2. Sign in using Clerk authentication

└─────────────┬───────────────────────────┘3. Describe your infrastructure requirements in the chat interface. Examples:

              │   - "Create an AWS EC2 instance with nginx server"

              ▼   - "Set up a load-balanced web application with RDS database"

         Has violations?   - "Deploy a containerized application on ECS with auto-scaling"

         ┌───┴────┐4. Watch the multi-agent workflow progress through the terminal loader

         │   YES  │   NO5. Review the generated infrastructure:

         │        │    │   - Interactive architecture diagram

         │        │    ▼   - Cost estimation badge

         │        │  FinOps → Done ✓   - Security scan results

         │        │   - Markdown-formatted response

         ▼        │6. Download the complete infrastructure package as a ZIP file

┌─────────────────────────────────────────┐

│ Architect Agent (MODE 2: REMEDIATION)  │## Project Structure

│                                         │

│ Input Received:                         │```

│ ┌─────────────────────────────────────┐ │InfraGenie/

│ │ SECURITY VIOLATIONS TO FIX:         │ │├── backend/

│ │ 1. [CKV_AWS_8] on aws_instance.web  │ ││   ├── app/

│ │    Issue: EBS encryption required   │ ││   │   ├── main.py              # FastAPI application entry point

│ │    Severity: MEDIUM                 │ ││   │   ├── core/

│ │                                     │ ││   │   │   ├── graph.py         # LangGraph workflow definition

│ │ 2. [CKV_AWS_79] on aws_instance.web │ ││   │   │   ├── state.py         # Workflow state management

│ │    Issue: IMDSv2 not enabled        │ ││   │   │   └── agents/          # Specialized agent implementations

│ │    Severity: HIGH                   │ ││   │   ├── api/

│ └─────────────────────────────────────┘ ││   │   │   └── routes.py        # API endpoints

│                                         ││   │   └── services/

│ Actions:                                ││   │       ├── finops.py        # Cost analysis service

│ • Lookup EXACT fix in system prompt    ││   │       ├── sandbox.py       # Terraform validation

│ • Apply targeted remediation           ││   │       └── bundler.py       # Artifact packaging

│ • Preserve existing architecture       ││   ├── requirements.txt         # Python dependencies

│ • Return corrected code                ││   └── .env.example            # Environment variables template

└─────────────┬───────────────────────────┘├── frontend/

              │ corrected_code│   ├── app/

              ││   │   ├── page.tsx            # Main dashboard

              └──→ Loop back to Validator│   │   └── layout.tsx          # Root layout with providers

                   (Max 100 iterations)│   ├── components/

```│   │   ├── chat/               # Chat interface components

│   │   ├── diagram/            # Architecture visualization

### **Resource Categories & Colors**│   │   └── dashboard/          # Dashboard widgets

│   ├── lib/

| Category | Color | Resources | Icon |│   │   ├── api.ts              # API client

|----------|-------|-----------|------|│   │   ├── store.ts            # Zustand state management

| **Network** | Purple | VPC, Subnet, IGW, NAT, ALB | 🌐 |│   │   └── graph-utils.ts      # Graph layout utilities

| **Security** | Orange | Security Groups, IAM Roles, Policies | 🛡️ |│   └── package.json            # Node.js dependencies

| **Compute** | AWS Orange | EC2, Lambda, ECS | 💻 |└── docs/                       # Project documentation

| **Storage** | Green | S3, EBS | 🪣 |```

| **Database** | Pink | RDS, DynamoDB | 🗄️ |

| **Serverless** | Red | Lambda Functions | ⚡ |## API Endpoints

| **Container** | Orange | ECS, EKS | 🐳 |

### POST /api/v1/generate

---Generates infrastructure from natural language description.



## 📚 Key Improvements**Request Body**:

```json

### ✨ **Plug-and-Play Setup**{

- **One-command installation**: `./setup.sh` handles everything  "prompt": "Create an AWS EC2 instance with nginx"

- **Auto-generated configs**: `.env` files created with sensible defaults}

- **Helper scripts**: `start.sh`, `test.sh` for easy operation```

- **Dependency verification**: Checks all prerequisites before setup

**Response**:

### 🎨 **Professional Architecture Diagrams**```json

- **Eraser.io-inspired design**: Clean, modern, enterprise-grade visualization{

- **AWS Architecture Icons**: Industry-standard visual language  "terraform_code": "resource \"aws_instance\" \"web\" {...}",

- **Swim lane layout**: Resources grouped by category for clarity  "ansible_code": "- name: Configure nginx...",

- **Color-coded connections**: Network (blue), Security (orange), Data (green)  "cost_estimate": "$24.50/mo",

- **Interactive features**: Zoom, pan, minimap, node inspector  "security_risks": ["CKV_AWS_8: Ensure EBS volumes are encrypted"],

- **Larger nodes**: 180x95px with category badges and hover effects  "validation_status": "valid",

  "architecture_summary": "Infrastructure includes EC2 instance..."

### 🔒 **Robust Self-Healing**}

- **Detailed violation tracking**: Full context (check_id, name, resource, severity)```

- **Intelligent remediation**: MODE 1 vs MODE 2 with specific fix instructions

- **13+ security checks**: Comprehensive coverage for AWS resources### GET /health

- **100 iteration limit**: More self-healing cycles before giving upHealth check endpoint that verifies all DevOps tools are installed.

- **Architectural preservation**: Fixes without breaking user intent

**Response**:

---```json

{

## 🛠️ Configuration  "status": "healthy",

  "terraform": "v1.6.0",

### **Backend Environment** (`backend/.env`)  "checkov": "3.2.495",

  "ansible": "2.16.2",

```bash  "infracost": "v0.10.30"

# ── Required ──────────────────────────────────────────}

GROQ_API_KEY=your_groq_api_key_here```

# Get free key: https://console.groq.com/keys

## Development

# ── Model Configuration ───────────────────────────────

GROQ_MODEL=llama-3.3-70b-versatile### Running Tests

MODEL_TEMPERATURE=0.1

MAX_TOKENS=2000Backend tests:

```bash

# ── Workflow Configuration ────────────────────────────cd backend

MAX_RETRIES=5pytest tests/

RECURSION_LIMIT=100```



# ── Server Configuration ──────────────────────────────Frontend type checking:

HOST=0.0.0.0```bash

PORT=8000cd frontend

CORS_ORIGINS=http://localhost:3000npm run build

```

# ── Feature Flags ─────────────────────────────────────

ENABLE_SECURITY_SCAN=true### Code Style

ENABLE_COST_ESTIMATION=true

ENABLE_ANSIBLE_GENERATION=trueBackend follows PEP 8 guidelines. Frontend uses ESLint configuration based on Next.js standards.

```

## Troubleshooting

### **Frontend Environment** (`frontend/.env.local`)

### Backend fails to start

```bash- Verify Python version: `python3.11 --version`

NEXT_PUBLIC_API_URL=http://localhost:8000- Check virtual environment is activated

```- Ensure all environment variables are set in `.env`

- Verify GROQ_API_KEY is valid

---

### Cost estimation shows "Unable to estimate"

## 🎯 Example Usage- Verify Infracost is installed: `which infracost`

- Check Infracost API key is set (optional but recommended)

### **Input:**- Ensure Terraform code is syntactically valid

```

Create a production-ready web application with:### Security scanning is skipped

- VPC with public and private subnets- Verify Checkov is installed: `checkov --version`

- Application Load Balancer- Check PATH includes Checkov installation directory

- Auto-scaling EC2 instances- Restart backend server after installing Checkov

- RDS PostgreSQL database

- S3 bucket for static assets### Frontend connection errors

```- Verify backend is running at `http://localhost:8000`

- Check CORS configuration in `backend/app/main.py`

### **Output:**- Ensure no firewall blocking port 8000

- ✅ **Terraform Code**: 15+ resources, security-hardened

- ✅ **Architecture Diagram**: Professional visual with swim lanes### Workflow reports success: false despite generating code

- ✅ **Security Report**: All Checkov checks passed- This has been fixed in the latest version

- ✅ **Cost Estimate**: Monthly AWS spending breakdown- The system now marks workflows as successful when all artifacts are generated

- ✅ **Ansible Playbook**: Deployment automation- Security warnings are included but do not prevent artifact delivery

- Restart backend server to apply the fix

---

## Contributing

## 📖 Documentation

Contributions are welcome. Please follow these guidelines:

- [📋 Project Design Document](docs/InfraGenie%20-%20Project%20Design%20Document.md)

- [🔒 Self-Healing Security](docs/self-healing-security-implementation.md)1. Fork the repository

- [🤖 Agent Documentation](docs/agents.md)2. Create a feature branch with a descriptive name

- [🎨 UI/UX Design](docs/InfraGenie%20-%20UI%20UX.md)3. Make your changes with clear commit messages

4. Test your changes thoroughly

---5. Submit a pull request with detailed description of changes



## 🤝 Contributing## License



Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)MIT License - See LICENSE file for details.



---## Acknowledgments



## 📄 LicenseBuilt with modern AI and DevOps technologies to streamline infrastructure automation and reduce manual configuration effort.


MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**Made with ❤️ by Dhanush Ranga**

[![GitHub](https://img.shields.io/badge/GitHub-Dhanushranga1-black?style=for-the-badge&logo=github)](https://github.com/Dhanushranga1)

⭐ **Star this repo if you find it helpful!**

</div>
