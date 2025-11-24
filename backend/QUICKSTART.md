# 🚀 Quick Start - Phase 1.2 Testing

## ⚡ Fast Track (5 Minutes)

### 1. Setup Environment
```bash
cd /home/dhanush/Development/Nexora/InfraGenie/backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Build Docker
```bash
cd ..
docker build -t infragenie-backend ./backend
```

### 3. Run Container
```bash
docker run --rm -p 8000:8000 --env-file backend/.env infragenie-backend
```

### 4. Test Health
```bash
curl http://localhost:8000/health | jq
```

### 5. Test Workflow
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a t3.micro EC2 instance"}' | jq
```

---

## 📋 Test Cases

### ✅ Case 1: Simple EC2
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a t3.micro EC2 instance with SSH key"}' | jq .success
```
**Expected**: `true` (1 retry)

### ✅ Case 2: Secure S3
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create an S3 bucket with encryption and versioning"}' | jq .is_clean
```
**Expected**: `true` (1-2 retries)

### ⚠️ Case 3: Complex VPC
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a VPC with public and private subnets"}' | jq .retry_count
```
**Expected**: `2-3` retries

### ❌ Case 4: Intentionally Vague
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create infrastructure"}' | jq .validation_error
```
**Expected**: Validation error or max retries

---

## 🔍 Verify Success

### Check Response Fields
```bash
# Full response
curl -s -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create EC2"}' | jq

# Just the code
curl -s -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create EC2"}' | jq -r .terraform_code
```

### Watch Logs
```bash
docker logs -f infragenie-backend | grep -E "ARCHITECT|VALIDATOR|SECURITY|SUCCESS|FAILED"
```

### Expected Log Pattern
```
ARCHITECT AGENT: Starting code generation
VALIDATOR NODE: Running Terraform validation
✓ Validation passed successfully
SECURITY NODE: Running Checkov security scan
✓ Security scan passed
✓ WORKFLOW SUCCESS
```

---

## 🐛 Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Connection refused | Container not running | Check `docker ps` |
| 500 error | Missing API key | Add to `.env` |
| Timeout | OpenAI API slow | Normal, wait 60s |
| Validation failed | LLM error | Check retry_count < 3 |

---

## ✅ Success Checklist

- [ ] Docker builds without errors
- [ ] Health endpoint returns 200 OK
- [ ] All 4 tools show "installed": true
- [ ] Test endpoint accepts JSON
- [ ] Simple EC2 test succeeds
- [ ] Response has terraform_code
- [ ] Logs show workflow steps
- [ ] is_clean = true on success

---

## 📊 Performance Benchmarks

| Request Type | Time | Retries |
|--------------|------|---------|
| Simple EC2 | 15-20s | 1 |
| S3 bucket | 20-30s | 1-2 |
| VPC setup | 30-45s | 2-3 |
| Complex infra | 45-60s | 3 |

---

## 🎯 What Success Looks Like

```json
{
  "success": true,
  "terraform_code": "provider \"aws\" {\n  region = \"us-east-1\"\n}\n\nresource \"aws_instance\" \"main\" {\n  ami           = \"ami-0c55b159cbfafe1f0\"\n  instance_type = \"t3.micro\"\n  \n  tags = {\n    Name = \"InfraGenie-Instance\"\n  }\n}",
  "validation_error": null,
  "security_errors": [],
  "retry_count": 1,
  "is_clean": true
}
```

**Key Indicators:**
- ✅ `success: true`
- ✅ `is_clean: true`
- ✅ `validation_error: null`
- ✅ `security_errors: []`
- ✅ `terraform_code` contains valid HCL

---

## 🚀 Ready for Phase 1.3?

If all tests pass, you're ready to add:
1. FinOps cost estimation
2. Ansible playbook generation
3. ZIP bundler
4. Download endpoint

---

**Quick Test Command:**
```bash
curl -X POST http://localhost:8000/test/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create EC2"}' | jq .success
```

If output is `true`, you're good! 🎉
