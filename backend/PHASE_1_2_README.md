# Phase 1.2 Implementation Guide

## 🧠 The AI Brain - LangGraph Workflow

This document explains the Phase 1.2 implementation: the intelligent core of InfraGenie that orchestrates multiple AI agents to generate, validate, and secure infrastructure code.

## 📐 Architecture Overview

### State Management
The workflow uses a **TypedDict** (`AgentState`) that serves as shared memory across all nodes:

```python
class AgentState(TypedDict):
    user_prompt: str              # Original user request
    terraform_code: str           # Generated HCL code
    validation_error: Optional[str]  # Terraform validation error
    security_errors: List[str]    # Checkov violation IDs
    retry_count: int              # Loop prevention counter
    is_clean: bool                # Ready for next phase flag
```

### Workflow Graph

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   ARCHITECT     │  ← LLM Node (GPT-4)
│  (Generate HCL) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDATOR     │  ← Tool Node (terraform validate)
│  (Check syntax) │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Valid? │
    └─┬────┬──┘
      │    │
   No │    │ Yes
      │    │
      │    ▼
      │ ┌──────────────┐
      │ │   SECURITY   │  ← Tool Node (checkov)
      │ │ (Scan risks) │
      │ └──────┬───────┘
      │        │
      │   ┌────┴────┐
      │   │ Clean?  │
      │   └─┬────┬──┘
      │     │    │
      │  No │    │ Yes
      │     │    │
      │     │    ▼
      │     │  ┌─────┐
      │     │  │ END │ Success!
      │     │  └─────┘
      │     │
      └─────┴──► Back to ARCHITECT (if retry < 3)
                     │
                     ▼
                   ┌─────┐
                   │ END │ Failed after max retries
                   └─────┘
```

## 🔧 Components

### 1. State Schema (`app/core/state.py`)

Defines the data structure that flows through the graph. Each node reads from and writes to this shared state.

**Key Design Decision**: Using `TypedDict` provides:
- Type safety at development time
- Runtime flexibility for LangGraph
- Clear contract between nodes

### 2. Sandbox Service (`app/services/sandbox.py`)

Provides **isolated execution** of CLI tools in temporary directories.

#### Functions:

**`run_tool(directory, command, timeout)`**
- Base function for all subprocess execution
- Time-limited to prevent hangs
- Captures stdout/stderr
- Thread-safe (isolated directories)

**`validate_terraform(hcl_code) -> Optional[str]`**
- Creates temp workspace
- Writes code to `main.tf`
- Runs `terraform init` (downloads providers)
- Runs `terraform validate -json`
- Parses diagnostics
- Returns `None` if valid, error string if invalid

**`run_checkov(hcl_code) -> List[str]`**
- Creates temp workspace
- Writes code to `main.tf`
- Runs `checkov -f main.tf --output json`
- Extracts failed check IDs
- Returns list of violations (e.g., `['CKV_AWS_8', 'CKV_AWS_23']`)

**Why Temporary Directories?**
- Prevents state pollution between requests
- Enables concurrent execution
- Automatic cleanup
- Security isolation

### 3. Architect Agent (`app/core/agents/architect.py`)

The **LLM-powered code generator** using GPT-4.

#### Prompt Strategy:

The system prompt enforces:
- Raw HCL output (no markdown)
- AWS provider standards
- Cost optimization (t3.micro defaults)
- Security best practices
- Error-aware regeneration

#### Context Building:

The agent receives different inputs based on state:

**First Attempt:**
```
User Request: Create an EC2 instance
```

**After Validation Error:**
```
Original Request: Create an EC2 instance

VALIDATION ERROR TO FIX:
Error: Missing required argument 'ami' in aws_instance.web

Analyze this error carefully and fix the exact issue.
```

**After Security Scan:**
```
Original Request: Create an EC2 instance

SECURITY VIOLATIONS TO FIX:
Failed Checkov checks: CKV_AWS_8, CKV_AWS_23

For each check ID, apply the specific fix required by that policy.
```

**Output Processing:**
- Strips markdown fencing if present
- Increments retry counter
- Resets error fields for next cycle

### 4. Graph Orchestration (`app/core/graph.py`)

The **workflow controller** that connects all nodes.

#### Nodes:

1. **`architect_node`** - Calls the LLM to generate/fix code
2. **`validator_node`** - Runs Terraform validation
3. **`security_node`** - Runs Checkov security scan

#### Conditional Edges:

**After Validator:**
```python
if validation_error is None:
    → Go to "security"
elif retry_count < 3:
    → Go to "architect" (retry)
else:
    → Go to "end" (failed)
```

**After Security:**
```python
if is_clean:
    → Go to "end" (success)
elif retry_count < 3:
    → Go to "architect" (fix security)
else:
    → Go to "end" (failed with violations)
```

#### Retry Logic:

- **Max retries**: 3 (constant `MAX_RETRIES`)
- **Counter**: Incremented by architect node
- **Prevents infinite loops**: Workflow terminates after 3 attempts

## 🧪 Testing the Implementation

### 1. Test via API Endpoint

The `/test/generate` endpoint allows manual workflow testing:

```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a secure S3 bucket with versioning"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "terraform_code": "provider \"aws\" {\n  region = \"us-east-1\"\n}\n\nresource \"aws_s3_bucket\" \"main\" {...}",
  "validation_error": null,
  "security_errors": [],
  "retry_count": 1,
  "is_clean": true
}
```

### 2. Test Scenarios

#### ✅ Simple Valid Request
```bash
curl -X POST http://localhost:8000/test/generate \
  -d '{"prompt": "Create a t3.micro EC2 instance"}' \
  -H "Content-Type: application/json"
```
Expected: 1 retry, success

#### ⚠️ Complex Request (May Need Fixes)
```bash
curl -X POST http://localhost:8000/test/generate \
  -d '{"prompt": "Create an RDS PostgreSQL database with encryption"}' \
  -H "Content-Type: application/json"
```
Expected: 2-3 retries, eventual success

#### ❌ Intentionally Broken Request
```bash
curl -X POST http://localhost:8000/test/generate \
  -d '{"prompt": "Create a foo bar baz"}' \
  -H "Content-Type: application/json"
```
Expected: 3 retries, validation errors

### 3. Verify Logs

Check Docker logs to see workflow execution:

```bash
docker logs -f infragenie-backend
```

Look for:
```
======================================================================
WORKFLOW START: Create an EC2 instance...
======================================================================
============================================================
ARCHITECT AGENT: Starting code generation
Retry count: 0
============================================================
VALIDATOR NODE: Running Terraform validation
✓ Validation passed successfully
============================================================
SECURITY NODE: Running Checkov security scan
✓ Security scan passed - no violations found
============================================================
✓ WORKFLOW SUCCESS
Total retries: 1
```

## 🐛 Common Issues & Fixes

### Issue 1: "Import langchain_openai could not be resolved"

**Cause**: Dependencies not installed in local environment
**Solution**: These errors only appear in VS Code. They disappear when running in Docker.

**To verify Docker has dependencies:**
```bash
docker exec infragenie-backend pip list | grep langchain
```

### Issue 2: Terraform validation hangs

**Cause**: Terraform trying to download large provider plugins
**Solution**: Already handled with 120s timeout in `sandbox.py`

**To check:**
```bash
docker exec infragenie-backend terraform version
```

### Issue 3: Checkov returns empty violations list

**Cause**: JSON parsing error or Checkov installed incorrectly
**Solution**: Check Checkov installation:
```bash
docker exec infragenie-backend checkov --version
docker exec infragenie-backend checkov -f /tmp/test.tf --output json
```

### Issue 4: GPT-4 returns markdown-fenced code

**Cause**: LLM ignoring system prompt
**Solution**: Already handled in `architect.py` - code strips markdown fencing
```python
if generated_code.startswith("```"):
    # Remove fencing
```

### Issue 5: Workflow fails with "Max retries exceeded"

**Cause**: LLM unable to fix the specific error
**Solution**: Check logs for the actual validation/security error. May need to:
- Adjust system prompt
- Increase `MAX_RETRIES`
- Add more context to error messages

## 📊 Performance Metrics

**Typical Execution Times:**
- Simple request (EC2): ~15-20 seconds
- Complex request (VPC): ~30-45 seconds  
- With retries (2x): ~40-60 seconds

**Breakdown:**
- Architect (GPT-4): 8-12s per generation
- Terraform init: 5-8s
- Terraform validate: 1-2s
- Checkov scan: 2-5s

## 🔐 Security Considerations

1. **API Key Protection**: OpenAI key stored in `.env`, never logged
2. **Subprocess Isolation**: All commands run in temp directories
3. **Timeout Protection**: All subprocess calls have max execution time
4. **No Shell Injection**: Commands passed as lists, not strings
5. **Automatic Cleanup**: Temp directories deleted after use

## 🚀 Next Steps (Phase 1.3)

After verifying Phase 1.2:

1. **Add FinOps Node** - Infracost integration
2. **Add Config Agent** - Ansible playbook generation
3. **Implement Bundler** - Create .zip artifact
4. **Create Download Endpoint** - Return the deployment kit

## 📚 References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Terraform Validation](https://www.terraform.io/cli/commands/validate)
- [Checkov Policies](https://www.checkov.io/5.Policy%20Index/all.html)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

---

**Phase 1.2 Complete** ✅
