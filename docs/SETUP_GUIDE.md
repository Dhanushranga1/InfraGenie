# 🚀 InfraGenie - Complete Setup & Usage Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Usage Examples](#usage-examples)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### **Prerequisites Check**
```bash
# Check Python version (need 3.11+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm version
npm --version
```

### **One-Command Setup**
```bash
# Clone and setup
git clone https://github.com/Dhanushranga1/InfraGenie.git
cd InfraGenie
./setup.sh
```

### **Configure API Key**
```bash
# Edit backend/.env
nano backend/.env

# Add your Groq API key (get it from https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### **Start Application**
```bash
# Start both backend and frontend
./start.sh

# Or start individually:
./start-backend.sh   # Backend only (port 8000)
./start-frontend.sh  # Frontend only (port 3000)
```

### **Access the Application**
- 🌐 **Frontend**: http://localhost:3000
- 🔌 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

---

## Detailed Setup

### **1. Backend Setup**

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import fastapi, langchain_groq, hcl2; print('✓ All imports working')"
```

### **2. Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list next react @xyflow/react

# Optional: Run type check
npm run build
```

### **3. Environment Configuration**

#### Backend `.env`
```bash
# ══════════════════════════════════════════════════
# InfraGenie Backend Configuration
# ══════════════════════════════════════════════════

# ── REQUIRED ──────────────────────────────────────
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

# ── AI Model Configuration ────────────────────────
GROQ_MODEL=llama-3.3-70b-versatile
MODEL_TEMPERATURE=0.1
MAX_TOKENS=2000

# ── Workflow Configuration ────────────────────────
MAX_RETRIES=5              # Max validation retries
RECURSION_LIMIT=100        # LangGraph recursion limit

# ── Server Configuration ──────────────────────────
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# ── Logging ───────────────────────────────────────
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR

# ── Feature Flags ─────────────────────────────────
ENABLE_SECURITY_SCAN=true
ENABLE_COST_ESTIMATION=true
ENABLE_ANSIBLE_GENERATION=true
```

#### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Usage Examples

### **Example 1: Simple Web Server**

**Input:**
```
Create a web server on AWS
```

**Expected Output:**
- ✅ Terraform code with EC2 instance
- ✅ Security hardening (encrypted EBS, IMDSv2, monitoring)
- ✅ Architecture diagram with 4-5 nodes
- ✅ Cost estimate (~$8-10/month)
- ✅ Ansible playbook

**Diagram Structure:**
```
[VPC] → [Subnet] → [Security Group] → [EC2 Instance]
```

---

### **Example 2: Three-Tier Web Application**

**Input:**
```
Build a production-ready three-tier web application with:
- VPC with public and private subnets
- Application Load Balancer in public subnet
- Auto-scaling EC2 instances in private subnet
- RDS PostgreSQL database
- S3 bucket for static assets
- CloudWatch monitoring
```

**Expected Output:**
- ✅ 15+ Terraform resources
- ✅ Complete network architecture
- ✅ Security groups with least-privilege access
- ✅ Professional architecture diagram with swim lanes
- ✅ Cost estimate (~$150-200/month)

**Diagram Structure:**
```
Network Layer:    [VPC] → [IGW] → [Public Subnet] → [Private Subnet]
Security Layer:   [ALB SG] → [Web SG] → [DB SG]
Compute Layer:    [ALB] → [Auto Scaling Group] → [EC2 Instances]
Database Layer:   [RDS Primary] → [RDS Standby]
Storage Layer:    [S3 Bucket]
```

---

### **Example 3: Microservices Architecture**

**Input:**
```
Create a microservices platform with:
- ECS Fargate cluster
- Application Load Balancer with path-based routing
- 3 microservices (auth, api, frontend)
- ElastiCache Redis for session storage
- RDS PostgreSQL for persistent data
- CloudFront for CDN
- S3 for static assets
```

**Expected Output:**
- ✅ 20+ Terraform resources
- ✅ Container-based architecture
- ✅ Multiple swim lanes (Network, Container, Database, Storage, CDN)
- ✅ Cost estimate (~$300-400/month)

---

## Troubleshooting

### **Common Issues**

#### 1. **"Import Error: No module named 'fastapi'"**
```bash
# Solution: Activate virtual environment
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. **"GROQ_API_KEY not set"**
```bash
# Solution: Add API key to .env
echo "GROQ_API_KEY=gsk_your_key_here" >> backend/.env
```

#### 3. **"Port 8000 already in use"**
```bash
# Solution 1: Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Solution 2: Change port in backend/.env
echo "PORT=8001" >> backend/.env
```

#### 4. **"Frontend can't connect to backend"**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/.env
CORS_ORIGINS=http://localhost:3000

# Check frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 5. **"Checkov not found"**
```bash
# Install Checkov
pip install checkov

# Verify installation
checkov --version
```

#### 6. **"Terraform validation fails"**
```bash
# Install Terraform
# Ubuntu/Debian:
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify installation
terraform --version
```

#### 7. **"Diagram not rendering"**
```bash
# Check browser console for errors
# Open DevTools (F12) → Console tab

# Clear browser cache
# Ctrl+Shift+R (hard reload)

# Check if graph_data is received
# Network tab → look for /api/generate response
```

---

## Advanced Configuration

### **Custom LLM Models**

To use a different Groq model:
```bash
# Edit backend/.env
GROQ_MODEL=llama-3.1-70b-versatile    # Faster, less accurate
# OR
GROQ_MODEL=llama-3.3-70b-versatile    # Slower, more accurate (default)
# OR
GROQ_MODEL=mixtral-8x7b-32768         # Alternative model
```

### **Adjust Retry Limits**

```bash
# Edit backend/.env
MAX_RETRIES=10              # More retries for complex architectures
RECURSION_LIMIT=150         # More self-healing cycles
```

### **Enable Debug Logging**

```bash
# Edit backend/.env
LOG_LEVEL=DEBUG

# Restart backend to see detailed logs
./start-backend.sh
```

### **Disable Features**

```bash
# Edit backend/.env
ENABLE_SECURITY_SCAN=false        # Skip Checkov scanning
ENABLE_COST_ESTIMATION=false      # Skip cost estimation
ENABLE_ANSIBLE_GENERATION=false   # Skip Ansible playbook generation
```

### **Change Frontend Theme**

```typescript
// Edit frontend/app/globals.css
:root {
  --primary: 262.1 83.3% 57.8%;      # Purple (default)
  --secondary: 220 14.3% 95.9%;      # Slate
}

// Custom theme example (blue):
:root {
  --primary: 221.2 83.2% 53.3%;      # Blue
  --secondary: 210 40% 96.1%;        # Light blue
}
```

---

## Performance Optimization

### **Backend**

```bash
# Use production-grade ASGI server
cd backend
source venv/bin/activate
pip install gunicorn uvicorn[standard]

# Start with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### **Frontend**

```bash
# Build for production
cd frontend
npm run build

# Start production server
npm start
```

---

## Deployment

### **Docker Deployment**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY frontend/ .
RUN npm install && npm run build
CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

---

## Testing

### **Backend Tests**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### **Frontend Tests**
```bash
cd frontend
npm test
```

### **Integration Tests**
```bash
# Start both services
./start.sh

# Run end-to-end tests (in another terminal)
cd frontend
npm run test:e2e
```

---

## Getting Help

### **Resources**
- 📚 **Documentation**: `docs/` folder
- 🐛 **Issues**: https://github.com/Dhanushranga1/InfraGenie/issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: dhanushranga1@gmail.com

### **Logs to Check**

```bash
# Backend logs
tail -f backend/app.log

# Frontend logs
cd frontend
npm run dev  # Check terminal output

# System logs
journalctl -u infragenie  # If running as systemd service
```

---

## Next Steps

1. ✅ Complete setup
2. ✅ Add GROQ_API_KEY
3. ✅ Test with simple examples
4. 📖 Read [Architecture Guide](docs/architecture-diagram-guide.md)
5. 🔒 Review [Security Implementation](docs/self-healing-security-implementation.md)
6. 🚀 Start building infrastructure!

---

<div align="center">

**Happy Infrastructure Coding! 🎉**

[⬆ Back to Top](#-infragenie---complete-setup--usage-guide)

</div>
