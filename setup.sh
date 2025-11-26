#!/bin/bash

###############################################################################
# InfraGenie - One-Click Setup Script
# Makes the entire system plug-and-play with minimal configuration
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print with color
print_header() {
    echo -e "\n${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

###############################################################################
# 1. Pre-flight Checks
###############################################################################

print_header "🚀 InfraGenie Setup - Pre-flight Checks"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 detected: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js detected: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm detected: v$NPM_VERSION"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# Check Terraform
if command_exists terraform; then
    TF_VERSION=$(terraform --version | head -n1 | cut -d'v' -f2)
    print_success "Terraform detected: v$TF_VERSION"
else
    print_warning "Terraform not found. Installing validators will still work."
fi

# Check Checkov
if command_exists checkov; then
    CHECKOV_VERSION=$(checkov --version | head -n1)
    print_success "Checkov detected: $CHECKOV_VERSION"
else
    print_warning "Checkov not found. It will be installed with Python dependencies."
fi

###############################################################################
# 2. Environment Setup
###############################################################################

print_header "🔧 Setting Up Environment"

# Create .env files if they don't exist
if [ ! -f "backend/.env" ]; then
    print_info "Creating backend/.env file..."
    cat > backend/.env << 'EOF'
# InfraGenie Backend Configuration
# Generated automatically by setup.sh

# Groq API Configuration (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
GROQ_MODEL=llama-3.3-70b-versatile
MODEL_TEMPERATURE=0.1
MAX_TOKENS=2000

# Workflow Configuration
MAX_RETRIES=5
RECURSION_LIMIT=100

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_SECURITY_SCAN=true
ENABLE_COST_ESTIMATION=true
ENABLE_ANSIBLE_GENERATION=true
EOF
    print_success "Created backend/.env (⚠️ REMEMBER TO ADD YOUR GROQ_API_KEY)"
else
    print_info "backend/.env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
    print_info "Creating frontend/.env.local file..."
    cat > frontend/.env.local << 'EOF'
# InfraGenie Frontend Configuration
# Generated automatically by setup.sh

NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    print_success "Created frontend/.env.local"
else
    print_info "frontend/.env.local already exists"
fi

###############################################################################
# 3. Backend Setup
###############################################################################

print_header "🐍 Setting Up Backend (Python + FastAPI)"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Verify critical packages
print_info "Verifying critical packages..."
python3 -c "import fastapi; import langchain_groq; import hcl2; print('✓ All critical imports working')"
print_success "Package verification complete"

cd ..

###############################################################################
# 4. Frontend Setup
###############################################################################

print_header "⚛️  Setting Up Frontend (Next.js + React)"

cd frontend

# Install dependencies
print_info "Installing npm dependencies..."
npm install
print_success "npm dependencies installed"

# Verify Next.js setup
if [ -f "package.json" ]; then
    print_success "Next.js project configured"
fi

cd ..

###############################################################################
# 5. Create Helper Scripts
###############################################################################

print_header "📝 Creating Helper Scripts"

# Start script
cat > start.sh << 'EOF'
#!/bin/bash
# Start both backend and frontend

echo "🚀 Starting InfraGenie..."

# Start backend
echo "📦 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting Frontend (Next.js)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ InfraGenie is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start.sh
print_success "Created start.sh"

# Backend only script
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "📦 Starting Backend Only..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

chmod +x start-backend.sh
print_success "Created start-backend.sh"

# Frontend only script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "⚛️  Starting Frontend Only..."
cd frontend
npm run dev
EOF

chmod +x start-frontend.sh
print_success "Created start-frontend.sh"

# Test script
cat > test.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing InfraGenie Setup..."

echo "Testing Backend..."
cd backend
source venv/bin/activate
python3 -c "
import sys
try:
    from app.core.agents.architect import create_architect_chain
    from app.services.parser import parse_hcl_to_graph
    from app.services.sandbox import run_checkov
    print('✓ All backend imports working')
except Exception as e:
    print(f'✗ Backend test failed: {e}')
    sys.exit(1)
"
cd ..

echo "Testing Frontend..."
cd frontend
if [ -d "node_modules" ]; then
    echo "✓ node_modules exists"
else
    echo "✗ node_modules missing - run npm install"
    exit 1
fi
cd ..

echo ""
echo "✅ All tests passed!"
EOF

chmod +x test.sh
print_success "Created test.sh"

###############################################################################
# 6. Final Verification
###############################################################################

print_header "✅ Final Verification"

# Run tests
print_info "Running test suite..."
./test.sh

###############################################################################
# 7. Summary
###############################################################################

print_header "🎉 Setup Complete!"

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}InfraGenie is ready to use!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Add your GROQ API key to backend/.env${NC}"
echo ""
echo -e "${CYAN}Quick Start:${NC}"
echo -e "  ${GREEN}1.${NC} Edit ${BLUE}backend/.env${NC} and add your ${YELLOW}GROQ_API_KEY${NC}"
echo -e "  ${GREEN}2.${NC} Run: ${BLUE}./start.sh${NC}"
echo -e "  ${GREEN}3.${NC} Open: ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "${CYAN}Available Scripts:${NC}"
echo -e "  ${BLUE}./start.sh${NC}          - Start both backend and frontend"
echo -e "  ${BLUE}./start-backend.sh${NC}  - Start backend only"
echo -e "  ${BLUE}./start-frontend.sh${NC} - Start frontend only"
echo -e "  ${BLUE}./test.sh${NC}           - Test installation"
echo ""
echo -e "${CYAN}Documentation:${NC}"
echo -e "  ${BLUE}docs/InfraGenie - Project Design Document.md${NC}"
echo -e "  ${BLUE}docs/self-healing-security-implementation.md${NC}"
echo ""
echo -e "${GREEN}Happy Infrastructure Coding! 🚀${NC}"
echo ""
