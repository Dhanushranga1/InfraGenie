# Self-Healing Security Loop - Implementation Complete ✅

## Overview
Implemented intelligent security remediation system where the Architect Agent applies specific fixes for Checkov security violations instead of random retries.

## Key Changes

### 1. Enhanced Security Violation Tracking
**Files Modified**: 
- `backend/app/services/sandbox.py`
- `backend/app/core/state.py`
- `backend/app/core/graph.py`

**Changes**:
- Modified `run_checkov()` to return detailed violation dictionaries with:
  - `check_id`: Checkov check ID (e.g., CKV_AWS_8)
  - `check_name`: Human-readable violation name
  - `resource`: Affected Terraform resource
  - `file_path`: Location in code
  - `severity`: Risk level (HIGH, MEDIUM, LOW)
  - `guideline`: Remediation guidance URL

- Added `security_violations: List[Dict[str, str]]` to AgentState
- Updated `security_node()` to populate both legacy `security_errors` (IDs) and detailed `security_violations`
- Added `security_violations: []` to initial state

### 2. Intelligent Architect Agent (MODE 1 vs MODE 2)
**Files Modified**: 
- `backend/app/core/agents/architect.py`

**Changes**:

#### A. Updated ARCHITECT_SYSTEM_PROMPT
- **MODE 1: CREATION** - First-time code generation with proactive security
- **MODE 2: REMEDIATION** - Intelligent fixing of specific violations

New prompt includes:
- Clear operational mode distinction
- Detailed security fix instructions for common Checkov violations:
  - EC2: CKV_AWS_8, CKV_AWS_79, CKV_AWS_126, CKV_AWS_135, CKV2_AWS_41
  - S3: CKV_AWS_18, CKV_AWS_21, CKV_AWS_19
  - RDS: CKV_AWS_16, CKV_AWS_17, CKV_AWS_129
  - VPC: CKV2_AWS_11
- Specific code snippets for each fix
- Instructions to preserve architecture while adding security configs

#### B. Rewrote build_architect_input()
```python
def build_architect_input(state: AgentState) -> str:
    """
    Construct the input message for the Architect based on current state.
    Includes detailed security violation context for intelligent remediation.
    """
```

Key improvements:
- Detects CREATION vs REMEDIATION mode based on `retry_count` and violations
- Formats security violations with full context:
  ```
  1. [CKV_AWS_8] on `aws_instance.web_server`
     Issue: Ensure all data stored in the EBS is securely encrypted
     Severity: MEDIUM
  ```
- Includes previous code with fixes section
- Clear instructions to apply EXACT fixes from system prompt

### 3. Increased Recursion Limit
**File Modified**: `backend/app/core/graph.py`

**Change**: Increased recursion_limit from 50 to 100 in workflow invocation to allow more self-healing iterations before failing.

```python
final_state = workflow_app.invoke(
    initial_state,
    config={"recursion_limit": 100}
)
```

### 4. Backup Created
**File**: `backend/app/core/agents/architect.py.backup`

Preserved original working version before modifications for safety.

## How It Works

### Before (Random Retries)
1. Checkov finds violations → returns check IDs like "CKV_AWS_8"
2. Architect receives: "Fix these violations: CKV_AWS_8, CKV_AWS_79"
3. Architect guesses what these mean → random fixes
4. Often fails to apply correct remediation

### After (Intelligent Remediation)
1. Checkov finds violations → returns detailed dictionaries:
   ```python
   {
     "check_id": "CKV_AWS_8",
     "check_name": "Ensure all data stored in the EBS is securely encrypted",
     "resource": "aws_instance.web_server",
     "severity": "MEDIUM"
   }
   ```

2. Security node populates state with detailed `security_violations`

3. build_architect_input() formats violations for LLM:
   ```
   **SECURITY VIOLATIONS TO FIX:**
   1. [CKV_AWS_8] on `aws_instance.web_server`
      Issue: Ensure all data stored in the EBS is securely encrypted
      Severity: MEDIUM
   
   **INSTRUCTIONS:**
   Apply the EXACT fixes specified in your system prompt for each violation.
   ```

4. Architect Agent (MODE 2: REMEDIATION):
   - Reads specific violation details
   - Looks up exact fix in system prompt under section 6
   - Applies targeted remediation:
     ```hcl
     root_block_device {
       encrypted = true
     }
     ```
   - Preserves all other resources and configurations
   - Returns COMPLETE corrected code

5. Workflow re-validates → if still has violations, repeats with remaining issues

## Example Flow

**User Request**: "Create a web server on AWS"

**Iteration 1** (MODE 1: CREATION):
- Architect generates basic EC2 instance
- Security scan finds: CKV_AWS_8, CKV_AWS_79, CKV_AWS_126

**Iteration 2** (MODE 2: REMEDIATION):
- Input to Architect:
  ```
  **REMEDIATION MODE - Retry 1**
  Original Request: Create a web server on AWS
  
  **SECURITY VIOLATIONS TO FIX:**
  1. [CKV_AWS_8] on `aws_instance.web_server`
     Issue: Ensure all data stored in the EBS is securely encrypted
     Severity: MEDIUM
  2. [CKV_AWS_79] on `aws_instance.web_server`
     Issue: Ensure Instance Metadata Service Version 1 is not enabled
     Severity: HIGH
  3. [CKV_AWS_126] on `aws_instance.web_server`
     Issue: Ensure that detailed monitoring is enabled for EC2 instances
     Severity: LOW
  
  **CURRENT CODE (needs fixes):**
  resource "aws_instance" "web_server" {
    ami           = "ami-0c55b159cbfafe1f0"
    instance_type = "t3.micro"
  }
  ```

- Architect applies EXACT fixes from system prompt
- Outputs corrected code with encrypted EBS, IMDSv2, monitoring enabled
- Security scan passes → workflow completes

## Benefits

1. **Targeted Remediation**: Fixes specific vulnerabilities, not random changes
2. **Architectural Preservation**: Maintains user's intent while adding security
3. **Faster Convergence**: Fewer retry iterations needed
4. **Better Success Rate**: Applies known-good fixes from system prompt
5. **Auditability**: Clear trace of which violations were fixed and how

## Testing Recommendations

1. Test simple EC2 creation → verify security fixes applied
2. Test S3 bucket with multiple violations → verify all fixed
3. Test RDS instance → verify encryption, backup, deletion protection
4. Test validation error + security violations → verify both fixed
5. Monitor retry counts → should decrease compared to before

## Monitoring

Check logs for:
- "MODE 1: CREATION" vs "MODE 2: REMEDIATION" in architect input
- Security violation details being formatted correctly
- Retry counts (should be lower than before)
- Final state `is_clean: True` (security passed)

## Rollback

If issues occur, restore from backup:
```bash
cp backend/app/core/agents/architect.py.backup backend/app/core/agents/architect.py
```

## Next Steps

Consider adding:
1. More Checkov check IDs to system prompt (currently covers ~13 common ones)
2. Support for Azure/GCP security violations (currently AWS-only)
3. Metrics tracking: fix success rate, avg retries, time to convergence
4. User-facing security report: violations found → fixes applied → final status
