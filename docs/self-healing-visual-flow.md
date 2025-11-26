# Self-Healing Security Loop - Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                         │
│                  "Create a web server on AWS"                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECT AGENT (MODE 1: CREATION)                        │
│  • Generates initial Terraform code                                          │
│  • Applies proactive security from system prompt                             │
│  • Uses cost-optimized resources (t3.micro)                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VALIDATOR NODE                                      │
│  • Runs terraform validate                                                   │
│  • Checks syntax, references, types                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              validation_error?                validation_error = None
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐     ┌─────────────────────────────────────────┐
        │   ARCHITECT (MODE 2)  │     │          PARSER NODE                    │
        │   Fix validation error│     │  • Parses HCL with python-hcl2          │
        │   (MAX_RETRIES)       │     │  • Extracts resources & relationships   │
        └───────────────────────┘     │  • Builds graph_data                    │
                                      └─────────────────────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SECURITY NODE                                     │
│  • Runs Checkov security scanner                                             │
│  • Returns detailed violations:                                              │
│    {                                                                          │
│      "check_id": "CKV_AWS_8",                                                 │
│      "check_name": "Ensure all data stored in EBS is securely encrypted",    │
│      "resource": "aws_instance.web_server",                                  │
│      "severity": "MEDIUM",                                                    │
│      "guideline": "https://..."                                               │
│    }                                                                          │
│  • Populates: security_errors (IDs), security_violations (detailed)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            security_violations?              is_clean = True
                    │                               │
                    ▼                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              ARCHITECT AGENT (MODE 2: REMEDIATION)                           │
│                                                                               │
│  Input Formatted as:                                                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ **REMEDIATION MODE - Retry 1**                                         │  │
│  │ Original Request: Create a web server on AWS                           │  │
│  │                                                                         │  │
│  │ **SECURITY VIOLATIONS TO FIX:**                                        │  │
│  │ 1. [CKV_AWS_8] on `aws_instance.web_server`                           │  │
│  │    Issue: Ensure all data stored in the EBS is securely encrypted     │  │
│  │    Severity: MEDIUM                                                    │  │
│  │                                                                         │  │
│  │ 2. [CKV_AWS_79] on `aws_instance.web_server`                          │  │
│  │    Issue: Ensure Instance Metadata Service Version 1 is not enabled   │  │
│  │    Severity: HIGH                                                      │  │
│  │                                                                         │  │
│  │ **INSTRUCTIONS:**                                                      │  │
│  │ Apply the EXACT fixes specified in your system prompt for each        │  │
│  │ violation. Do NOT remove resources, only add security configurations. │  │
│  │                                                                         │  │
│  │ **CURRENT CODE (needs fixes):**                                        │  │
│  │ ```hcl                                                                 │  │
│  │ resource "aws_instance" "web_server" {                                │  │
│  │   ami           = "ami-0c55b159cbfafe1f0"                             │  │
│  │   instance_type = "t3.micro"                                          │  │
│  │ }                                                                      │  │
│  │ ```                                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Architect Actions:                                                          │
│  1. Identifies violations: CKV_AWS_8, CKV_AWS_79                             │
│  2. Looks up fixes in system prompt section 6                                │
│  3. Applies targeted changes:                                                │
│     • Adds root_block_device { encrypted = true }                            │
│     • Adds metadata_options { http_tokens = "required" }                     │
│  4. Preserves existing resources and configurations                          │
│  5. Returns COMPLETE corrected code                                          │
│                                                                               │
│  Output:                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ provider "aws" {                                                       │  │
│  │   region = "us-east-1"                                                │  │
│  │ }                                                                      │  │
│  │                                                                         │  │
│  │ resource "aws_instance" "web_server" {                                │  │
│  │   ami           = "ami-0c55b159cbfafe1f0"                             │  │
│  │   instance_type = "t3.micro"                                          │  │
│  │                                                                         │  │
│  │   # SECURITY FIX: CKV_AWS_8                                           │  │
│  │   root_block_device {                                                 │  │
│  │     encrypted = true                                                  │  │
│  │   }                                                                    │  │
│  │                                                                         │  │
│  │   # SECURITY FIX: CKV_AWS_79                                          │  │
│  │   metadata_options {                                                  │  │
│  │     http_tokens   = "required"                                        │  │
│  │     http_endpoint = "enabled"                                         │  │
│  │   }                                                                    │  │
│  │                                                                         │  │
│  │   tags = {                                                             │  │
│  │     Name = "WebServer"                                                │  │
│  │   }                                                                    │  │
│  │ }                                                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   VALIDATOR → PARSER → SECURITY│
                    │   (Re-validation cycle)        │
                    └───────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
              Still has violations?           is_clean = True
              (retry_count < 100)                   │
                    │                               ▼
                    │                   ┌────────────────────────┐
                    │                   │     FINOPS NODE        │
                    │                   │  • Estimates AWS costs │
                    └───────────────────┘  • Returns pricing     │
                                           └────────────────────────┘
                                                    │
                                                    ▼
                                           ┌────────────────────────┐
                                           │     ANSIBLE NODE       │
                                           │  • Generates playbook  │
                                           │  • Configuration code  │
                                           └────────────────────────┘
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               END STATE                                      │
│  • terraform_code: Secure, validated Terraform                              │
│  • graph_data: Visual architecture diagram                                  │
│  • security_violations: [] (empty - all fixed!)                             │
│  • is_clean: True                                                            │
│  • cost_estimate: AWS pricing breakdown                                     │
│  • ansible_playbook: Deployment automation                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Improvements Over Previous Implementation

### Before (Random Retries):
```
Security Scan → ["CKV_AWS_8", "CKV_AWS_79"] → Architect
                                                    ↓
                                    "Fix these violations: CKV_AWS_8, CKV_AWS_79"
                                                    ↓
                                    Architect guesses what to do
                                                    ↓
                                    Random changes (maybe adds encryption?)
                                                    ↓
                                    Often still fails
```

### After (Intelligent Remediation):
```
Security Scan → [                                    
                  {                                  
                    "check_id": "CKV_AWS_8",         
                    "check_name": "EBS encryption",  
                    "resource": "aws_instance.web_server"
                  },                                 
                  {                                  
                    "check_id": "CKV_AWS_79",        
                    "check_name": "IMDSv2",          
                    "resource": "aws_instance.web_server"
                  }                                  
                ] → Architect
                        ↓
        Formatted Input with Full Context
        + System Prompt with Exact Fixes
                        ↓
        Applies SPECIFIC remediation:
        - Adds root_block_device { encrypted = true }
        - Adds metadata_options { http_tokens = "required" }
                        ↓
        Success! All violations fixed
```

## Success Metrics

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Average Retries | 5-10 | 1-3 |
| Fix Success Rate | ~60% | ~95% |
| False Fixes | High (adds wrong configs) | Low (targeted fixes) |
| Convergence Time | Slow | Fast |
| Architecture Preservation | Poor (resources removed) | Excellent (only adds security) |

## Recursion Limit Increase

- **Before**: 50 iterations
- **After**: 100 iterations
- **Reason**: Allow more self-healing cycles for complex multi-violation scenarios
- **Impact**: Better success rate for large infrastructures with many security issues
