#!/bin/bash

###############################################################################
# InfraGenie - Comprehensive Verification Script
# Checks all components and provides detailed status report
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

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

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

ERRORS=0
WARNINGS=0

###############################################################################
# 1. File Structure Verification
###############################################################################

print_header "📁 Checking File Structure"

# Helper scripts
if [ -f "setup.sh" ]; then
    print_success "setup.sh exists"
else
    print_error "setup.sh missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "start.sh" ]; then
    print_success "start.sh exists"
else
    print_error "start.sh missing"
    ERRORS=$((ERRORS + 1))
fi

# Backend files
if [ -f "backend/app/core/agents/architect.py" ]; then
    print_success "architect.py exists"
else
    print_error "architect.py missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "backend/app/core/agents/architect.py.backup" ]; then
    print_success "architect.py.backup exists (safety backup)"
else
    print_warning "architect.py.backup missing (no rollback available)"
    WARNINGS=$((WARNINGS + 1))
fi

# Frontend files
if [ -f "frontend/lib/graph-utils.ts" ]; then
    print_success "graph-utils.ts exists"
else
    print_error "graph-utils.ts missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "frontend/components/diagram/architecture-diagram.tsx" ]; then
    print_success "architecture-diagram.tsx exists"
else
    print_error "architecture-diagram.tsx missing"
    ERRORS=$((ERRORS + 1))
fi

# Documentation
if [ -f "README.md" ]; then
    print_success "README.md exists"
else
    print_error "README.md missing"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "docs/SETUP_GUIDE.md" ]; then
    print_success "SETUP_GUIDE.md exists"
else
    print_error "SETUP_GUIDE.md missing"
    ERRORS=$((ERRORS + 1))
fi

###############################################################################
# 2. Configuration Verification
###############################################################################

print_header "⚙️  Checking Configuration"

if [ -f "backend/.env" ]; then
    print_success "backend/.env exists"
    
    # Check for GROQ_API_KEY
    if grep -q "GROQ_API_KEY=your_groq_api_key_here" backend/.env; then
        print_warning "GROQ_API_KEY not configured (still default value)"
        print_info "   → Edit backend/.env and add your Groq API key"
        WARNINGS=$((WARNINGS + 1))
    elif grep -q "GROQ_API_KEY=gsk_" backend/.env; then
        print_success "GROQ_API_KEY configured"
    else
        print_warning "GROQ_API_KEY format unclear"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_warning "backend/.env missing (will be created by setup.sh)"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -f "frontend/.env.local" ]; then
    print_success "frontend/.env.local exists"
else
    print_warning "frontend/.env.local missing (will be created by setup.sh)"
    WARNINGS=$((WARNINGS + 1))
fi

###############################################################################
# 3. Backend Verification
###############################################################################

print_header "🐍 Checking Backend"

if [ -d "backend/venv" ]; then
    print_success "Virtual environment exists"
    
    # Activate and check packages
    source backend/venv/bin/activate 2>/dev/null || true
    
    # Check critical packages
    if python3 -c "import fastapi" 2>/dev/null; then
        print_success "fastapi installed"
    else
        print_error "fastapi not installed"
        ERRORS=$((ERRORS + 1))
    fi
    
    if python3 -c "import langchain_groq" 2>/dev/null; then
        print_success "langchain_groq installed"
    else
        print_error "langchain_groq not installed"
        ERRORS=$((ERRORS + 1))
    fi
    
    if python3 -c "import hcl2" 2>/dev/null; then
        print_success "hcl2 installed"
    else
        print_error "hcl2 not installed"
        ERRORS=$((ERRORS + 1))
    fi
    
    deactivate 2>/dev/null || true
else
    print_warning "Virtual environment not found (run setup.sh)"
    WARNINGS=$((WARNINGS + 1))
fi

###############################################################################
# 4. Frontend Verification
###############################################################################

print_header "⚛️  Checking Frontend"

if [ -d "frontend/node_modules" ]; then
    print_success "node_modules exists"
    
    # Check critical packages
    if [ -d "frontend/node_modules/next" ]; then
        print_success "next installed"
    else
        print_error "next not installed"
        ERRORS=$((ERRORS + 1))
    fi
    
    if [ -d "frontend/node_modules/@xyflow/react" ]; then
        print_success "@xyflow/react installed"
    else
        print_error "@xyflow/react not installed"
        ERRORS=$((ERRORS + 1))
    fi
else
    print_warning "node_modules not found (run setup.sh or npm install)"
    WARNINGS=$((WARNINGS + 1))
fi

###############################################################################
# 5. Code Quality Checks
###############################################################################

print_header "🔍 Code Quality Checks"

# Check for MODE 1/MODE 2 in architect.py
if grep -q "MODE 1: CREATION" backend/app/core/agents/architect.py 2>/dev/null; then
    print_success "architect.py has MODE 1/MODE 2 logic"
else
    print_error "architect.py missing MODE logic (upgrade needed)"
    ERRORS=$((ERRORS + 1))
fi

# Check for security_violations in state.py
if grep -q "security_violations" backend/app/core/state.py 2>/dev/null; then
    print_success "state.py has security_violations field"
else
    print_error "state.py missing security_violations (upgrade needed)"
    ERRORS=$((ERRORS + 1))
fi

# Check for recursion_limit: 100 in graph.py
if grep -q "recursion_limit.*100" backend/app/core/graph.py 2>/dev/null; then
    print_success "graph.py has recursion_limit: 100"
else
    print_warning "graph.py recursion_limit not set to 100"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for professional styling in graph-utils.ts
if grep -q "RESOURCE_CONFIGS" frontend/lib/graph-utils.ts 2>/dev/null; then
    print_success "graph-utils.ts has resource configurations"
else
    print_error "graph-utils.ts missing resource configs"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "bgColor" frontend/lib/graph-utils.ts 2>/dev/null; then
    print_success "graph-utils.ts has professional color system"
else
    print_warning "graph-utils.ts may need color updates"
    WARNINGS=$((WARNINGS + 1))
fi

###############################################################################
# 6. Documentation Check
###############################################################################

print_header "📚 Documentation Verification"

DOC_FILES=(
    "README.md"
    "docs/SETUP_GUIDE.md"
    "docs/architecture-diagram-guide.md"
    "docs/self-healing-security-implementation.md"
    "docs/ENHANCEMENT_SUMMARY.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        print_success "$doc exists"
    else
        print_warning "$doc missing"
        WARNINGS=$((WARNINGS + 1))
    fi
done

###############################################################################
# 7. Final Summary
###############################################################################

print_header "📊 Verification Summary"

echo -e "${CYAN}Results:${NC}"
echo -e "  ${GREEN}Passed checks${NC}"
echo -e "  ${YELLOW}$WARNINGS warnings${NC}"
echo -e "  ${RED}$ERRORS errors${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ All checks passed! InfraGenie is ready to use!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "  1. Ensure GROQ_API_KEY is set in ${BLUE}backend/.env${NC}"
    echo -e "  2. Run: ${BLUE}./start.sh${NC}"
    echo -e "  3. Open: ${BLUE}http://localhost:3000${NC}"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠ Some warnings detected (see above)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}Recommended actions:${NC}"
    [ $WARNINGS -gt 0 ] && echo -e "  - Review warnings above"
    echo -e "  - Run: ${BLUE}./setup.sh${NC} to fix configuration issues"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ Errors detected! Please fix before using InfraGenie${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}Recommended actions:${NC}"
    echo -e "  - Run: ${BLUE}./setup.sh${NC} to install dependencies"
    echo -e "  - Check error messages above"
    echo -e "  - See: ${BLUE}docs/SETUP_GUIDE.md${NC} for help"
    echo ""
    exit 1
fi
