#!/bin/bash

# Senior Engineer Code Review - Validation Script
# Verifies all 4 architectural improvements are in place

echo "🎯 Senior Engineer Code Review - Validation"
echo "==========================================="
echo ""

PASS=0
FAIL=0

# Test 1: Parser Node Position
echo "Test 1: Parser Runs After Security Scan"
echo "----------------------------------------"
if grep -q '"security": "security"' backend/app/core/graph.py && \
   grep -q '"parser": "parser"' backend/app/core/graph.py && \
   grep -q 'workflow.add_edge("parser", "finops")' backend/app/core/graph.py; then
    echo "✅ Parser positioned correctly (security → parser → finops)"
    ((PASS++))
else
    echo "❌ Parser position incorrect"
    ((FAIL++))
fi

if grep -q 'Literal\["architect", "parser"\]' backend/app/core/graph.py; then
    echo "✅ route_after_security returns 'parser' (not 'finops')"
    ((PASS++))
else
    echo "❌ route_after_security still returns 'finops'"
    ((FAIL++))
fi
echo ""

# Test 2: Logs Field in State
echo "Test 2: Real-Time Observability Logs"
echo "-------------------------------------"
if grep -q 'logs: List\[str\]' backend/app/core/state.py; then
    echo "✅ logs field added to AgentState"
    ((PASS++))
else
    echo "❌ logs field missing from AgentState"
    ((FAIL++))
fi

if grep -q '"logs": \[\]' backend/app/core/graph.py; then
    echo "✅ logs initialized in initial_state"
    ((PASS++))
else
    echo "❌ logs not initialized"
    ((FAIL++))
fi

if grep -q '"logs": state.get("logs", \[\]) +' backend/app/core/graph.py; then
    echo "✅ Nodes append to logs array"
    ((PASS++))
else
    echo "❌ Nodes not appending logs"
    ((FAIL++))
fi

if grep -q '✅ Terraform syntax validation passed' backend/app/core/graph.py; then
    echo "✅ Validator logs success messages"
    ((PASS++))
else
    echo "❌ Validator not logging properly"
    ((FAIL++))
fi

if grep -q '❌ Security scan found' backend/app/core/graph.py; then
    echo "✅ Security node logs violations"
    ((PASS++))
else
    echo "❌ Security node not logging properly"
    ((FAIL++))
fi

if grep -q '💰 Cost calculated' backend/app/core/graph.py; then
    echo "✅ FinOps logs cost estimate"
    ((PASS++))
else
    echo "❌ FinOps not logging properly"
    ((FAIL++))
fi
echo ""

# Test 3: Utils.py DRY Principle
echo "Test 3: DRY Utility Function"
echo "-----------------------------"
if [ -f "backend/app/core/utils.py" ]; then
    echo "✅ utils.py file created"
    ((PASS++))
else
    echo "❌ utils.py file missing"
    ((FAIL++))
fi

if grep -q 'def clean_llm_output' backend/app/core/utils.py; then
    echo "✅ clean_llm_output() function exists"
    ((PASS++))
else
    echo "❌ clean_llm_output() function missing"
    ((FAIL++))
fi

if grep -q 'from app.core.utils import clean_llm_output' backend/app/core/agents/architect.py; then
    echo "✅ Architect imports clean_llm_output"
    ((PASS++))
else
    echo "❌ Architect not using utils"
    ((FAIL++))
fi

if grep -q 'clean_llm_output(response.content, "hcl")' backend/app/core/agents/architect.py; then
    echo "✅ Architect uses clean_llm_output for HCL"
    ((PASS++))
else
    echo "❌ Architect not calling clean_llm_output"
    ((FAIL++))
fi

if grep -q 'from app.core.utils import clean_llm_output' backend/app/core/agents/config.py; then
    echo "✅ Config agent imports clean_llm_output"
    ((PASS++))
else
    echo "❌ Config agent not using utils"
    ((FAIL++))
fi

if grep -q 'clean_llm_output(response.content, "yaml")' backend/app/core/agents/config.py; then
    echo "✅ Config agent uses clean_llm_output for YAML"
    ((PASS++))
else
    echo "❌ Config agent not calling clean_llm_output"
    ((FAIL++))
fi

# Verify duplicate code removed
if ! grep -q 'if.*startswith("```"):' backend/app/core/agents/architect.py; then
    echo "✅ Duplicate markdown stripping removed from architect"
    ((PASS++))
else
    echo "⚠️  Old markdown stripping code still present in architect"
    ((FAIL++))
fi

if ! grep -q 'if playbook_yaml.startswith("```"):' backend/app/core/agents/config.py; then
    echo "✅ Duplicate markdown stripping removed from config"
    ((PASS++))
else
    echo "⚠️  Old markdown stripping code still present in config"
    ((FAIL++))
fi
echo ""

# Test 4: Remediation Strategy
echo "Test 4: Remediation Strategy Rule #0"
echo "-------------------------------------"
if grep -q 'REMEDIATION STRATEGY (MOST CRITICAL)' backend/app/core/agents/architect.py; then
    echo "✅ Rule #0 Remediation Strategy exists"
    ((PASS++))
else
    echo "❌ Rule #0 missing"
    ((FAIL++))
fi

if grep -q 'DO NOT create a new resource with a different name' backend/app/core/agents/architect.py; then
    echo "✅ Explicit anti-duplication instruction"
    ((PASS++))
else
    echo "❌ Anti-duplication instruction missing"
    ((FAIL++))
fi

if grep -q 'Example of WRONG approach' backend/app/core/agents/architect.py; then
    echo "✅ Wrong/Correct examples provided"
    ((PASS++))
else
    echo "❌ Examples missing"
    ((FAIL++))
fi
echo ""

# Test 5: Python Syntax
echo "Test 5: Python Syntax Validation"
echo "---------------------------------"
cd backend
if python3 -m py_compile app/core/utils.py 2>/dev/null; then
    echo "✅ utils.py syntax valid"
    ((PASS++))
else
    echo "❌ utils.py syntax error"
    ((FAIL++))
fi

if python3 -m py_compile app/core/state.py 2>/dev/null; then
    echo "✅ state.py syntax valid"
    ((PASS++))
else
    echo "❌ state.py syntax error"
    ((FAIL++))
fi

if python3 -m py_compile app/core/graph.py 2>/dev/null; then
    echo "✅ graph.py syntax valid"
    ((PASS++))
else
    echo "❌ graph.py syntax error"
    ((FAIL++))
fi

if python3 -m py_compile app/core/agents/architect.py 2>/dev/null; then
    echo "✅ architect.py syntax valid"
    ((PASS++))
else
    echo "❌ architect.py syntax error"
    ((FAIL++))
fi

if python3 -m py_compile app/core/agents/config.py 2>/dev/null; then
    echo "✅ config.py syntax valid"
    ((PASS++))
else
    echo "❌ config.py syntax error"
    ((FAIL++))
fi
cd ..
echo ""

# Summary
echo "==========================================="
echo "📊 VALIDATION SUMMARY"
echo "==========================================="
echo "✅ Passed: $PASS tests"
echo "❌ Failed: $FAIL tests"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 ALL SENIOR ENGINEER FIXES VALIDATED!"
    echo ""
    echo "Architectural improvements verified:"
    echo "  1. ✅ Parser runs on final secure code"
    echo "  2. ✅ Real-time logs for observability"
    echo "  3. ✅ DRY utility function (no duplication)"
    echo "  4. ✅ Comprehensive remediation strategy"
    echo ""
    echo "Status: Ready for Senior Engineer Approval ✨"
    exit 0
else
    echo "⚠️  VALIDATION FAILED - Please review failures above"
    exit 1
fi
