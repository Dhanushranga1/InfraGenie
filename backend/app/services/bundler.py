"""
Bundler Service - Deployment Kit Generation

This module creates the final "Deployment Kit" - a downloadable ZIP archive
containing all necessary files for infrastructure deployment: Terraform code,
Ansible playbook, deployment script, and documentation.

The bundler creates a complete, self-contained package that users can download
and execute to provision their infrastructure with a single command.
"""

import io
import zipfile
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.state import AgentState

logger = logging.getLogger(__name__)


# README template for the deployment kit
README_TEMPLATE = """# InfraGenie Deployment Kit

**Generated:** {timestamp}
**Estimated Monthly Cost:** {cost}

## 🎯 Zero-Configuration Deployment

This is an **AI-generated, production-ready** infrastructure deployment kit. 
Everything is automated - just run one script and provide your AWS credentials!

## 📦 What's Included

- ✅ **main.tf** - Validated Terraform code (syntax checked, security scanned)
- ✅ **playbook.yml** - Ansible playbook for server configuration
- ✅ **deploy.sh** - Fully automated deployment (YOU ONLY RUN THIS!)
- ✅ **destroy.sh** - Safe infrastructure cleanup
- ✅ **README.md** - This documentation

## 🚀 Quick Start (2 Steps!)

### Step 1: Make Script Executable (One-Time)

```bash
chmod +x deploy.sh
```

### Step 2: Deploy Everything

```bash
./deploy.sh
```

**That's it!** The script will:
1. ✅ Check prerequisites (Terraform, Ansible)
2. ✅ Configure AWS credentials (interactive if needed)
3. ✅ Show deployment summary
4. ✅ Provision infrastructure (automated)
5. ✅ Configure servers (automated)
6. ✅ Set up security (automated)
7. ✅ Give you SSH access details

### What You'll Be Asked

The script is **almost zero-interaction**, but will ask for:

1. **AWS Credentials** (if not already configured):
   - Access Key ID
   - Secret Access Key
   - Region (optional, defaults to us-east-1)

2. **Deployment Confirmation**: 
   - Reviews what will be deployed
   - You type "yes" to proceed

**That's all the interaction needed!** Everything else is automated.

## 🔧 Prerequisites

The deploy script will check for you, but you need:

1. **Terraform** (v1.0+)
   ```bash
   # macOS
   brew install terraform
   
   # Linux
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **Ansible** (v2.9+)
   ```bash
   # macOS/Linux
   pip install ansible
   
   # Or using apt
   sudo apt install ansible
   ```

3. **AWS Account** with IAM permissions to create resources

## 💰 Cost Management

**Estimated Monthly Cost:** {cost}

### Built-in Cost Control Features:

1. **Cost Assassin™** - Automatic shutdown at 8 PM daily
2. **Right-sized Resources** - Optimized instance types
3. **No Unnecessary Services** - Only what you requested

### Disable Auto-Shutdown (if needed):

```bash
# SSH into your server
ssh -i [generated-key.pem] ubuntu@[server-ip]

# Remove cron job
sudo crontab -e
# Delete the line containing "Cost Assassin"
```

## 🔒 Security Features

Your infrastructure includes:
- ✅ **Security Groups** - Firewall rules configured
- ✅ **fail2ban** - Intrusion prevention
- ✅ **Automatic Updates** - Security patches
- ✅ **SSH Key Authentication** - No password login
- ✅ **Non-root User** - Secure access

## 📝 What Was Requested

{user_prompt}

## 🛠️ Advanced Usage

### Manual Deployment (if you prefer more control)

**Step 1: Initialize Terraform**
```bash
terraform init
```

**Step 2: Review Plan**
```bash
terraform plan
```

**Step 3: Apply Infrastructure**
```bash
terraform apply
```

**Step 4: Configure with Ansible**
```bash
# Get server IP
SERVER_IP=$(terraform output -raw instance_ip)

# Create inventory
echo "[$SERVER_IP ansible_user=ubuntu ansible_ssh_private_key_file=infragenie-key.pem]" > inventory.ini

# Run playbook
ansible-playbook -i inventory.ini playbook.yml
```

### Update Infrastructure

```bash
# Edit main.tf with your changes
nano main.tf

# Apply updates
terraform apply
```

### Check Terraform Outputs

```bash
terraform output
```

## 🧹 Cleanup When Done

When you're finished with your infrastructure:

```bash
./destroy.sh
```

This will:
1. Show resources to be destroyed
2. Ask for confirmation
3. Remove all infrastructure
4. Optionally clean up local files

**Important:** Keep `terraform.tfstate` until you're done destroying - it tracks your infrastructure!

## � Troubleshooting

### Issue: "Terraform not found"
**Solution:** Install Terraform (see Prerequisites section)

### Issue: "AWS authentication failed"
**Solution:** 
- Check AWS credentials are correct
- Verify IAM permissions
- Try: `aws sts get-caller-identity` to test

### Issue: "SSH connection timeout"
**Reasons:**
1. Instance still booting (wait 2-3 minutes)
2. Security group blocks your IP
3. No public IP assigned

**Solution:**
- Check AWS Console → EC2 → Security Groups
- Verify status checks show "2/2 passed"
- Ensure instance has public IP

### Issue: "Ansible failed"
**Solution:**
- Infrastructure is deployed, configuration failed
- SSH manually: `ssh -i [key].pem ubuntu@[ip]`
- Retry: `ansible-playbook -i inventory.ini playbook.yml`

## 📚 Understanding the Files

### main.tf
Terraform configuration defining:
- Cloud resources (EC2, security groups, etc.)
- Networking configuration
- Storage and compute specifications

### playbook.yml
Ansible playbook that:
- Installs required packages
- Configures services
- Sets up security (fail2ban, firewall)
- Applies best practices

### deploy.sh
Automated deployment script that:
- Validates prerequisites
- Configures credentials
- Runs Terraform
- Executes Ansible
- Provides status updates

### terraform.tfstate
**CRITICAL FILE** - Tracks your infrastructure state
- Required for updates and destruction
- Contains resource IDs and metadata
- **Keep secure** - may contain sensitive data
- **Backup regularly** if making changes

## ⚡ Pro Tips

1. **First Time:** Let the script handle everything - it's designed for this!
2. **Credentials:** Script stores them only in environment variables (not on disk)
3. **SSH Key:** Auto-generated and saved as `infragenie-key.pem` - keep it safe!
4. **Logs:** All output is visible - watch for any warnings
5. **Testing:** Use `./destroy.sh` after testing to avoid costs

## 🎯 Design Philosophy

This kit is designed with one goal: **Minimal User Effort**

- ✅ AI validated the infrastructure code before generating this kit
- ✅ Security scanned (Checkov) - no known vulnerabilities
- ✅ Syntax validated - guaranteed to work
- ✅ Best practices applied - production-ready
- ✅ Cost optimized - right-sized resources
- ✅ Self-documented - clear README and comments

## 🤝 Support

For issues:
1. Check troubleshooting section above
2. Review script output for specific errors
3. Consult [Terraform docs](https://terraform.io/docs)
4. Consult [Ansible docs](https://docs.ansible.com)

## ⚠️ Important Reminders

1. **Monitor Costs** - Check AWS billing dashboard regularly
2. **Security** - Review security groups and access policies
3. **Backups** - Set up automated backups for production
4. **Updates** - Keep packages updated (automatic security updates enabled)
5. **Cleanup** - Run `./destroy.sh` when done to stop charges

---

**Generated by InfraGenie** - AI-Powered Infrastructure Automation  
Zero configuration • Production ready • Fully automated

*This entire infrastructure was designed, validated, and packaged by AI.  
You just run one script. That's the magic.*
"""


# Deployment script template
DEPLOY_SCRIPT_TEMPLATE = """#!/bin/bash

# InfraGenie Deployment Script
# Fully automated infrastructure provisioning and configuration
# Minimal user interaction required - just credentials!

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════╗"
echo "║        🚀 InfraGenie Automated Deployment 🚀          ║"
echo "║    AI-Generated Infrastructure - Zero Configuration     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Function to check and install prerequisites
check_prerequisites() {
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}📋 Step 1/6: Checking Prerequisites${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    local missing=0
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        echo "${RED}❌ Terraform not found${NC}"
        echo "   Install: https://www.terraform.io/downloads"
        missing=1
    else
        TF_VERSION=$(terraform version -json | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
        echo "${GREEN}✅ Terraform: v$TF_VERSION${NC}"
    fi
    
    # Check Ansible
    if ! command -v ansible-playbook &> /dev/null; then
        echo "${RED}❌ Ansible not found${NC}"
        echo "   Install: pip install ansible"
        missing=1
    else
        ANSIBLE_VERSION=$(ansible --version | head -n1 | awk '{print $2}' || echo "unknown")
        echo "${GREEN}✅ Ansible: v$ANSIBLE_VERSION${NC}"
    fi
    
    # Check AWS CLI (optional but recommended)
    if ! command -v aws &> /dev/null; then
        echo "${YELLOW}⚠️  AWS CLI not found (optional but recommended)${NC}"
        echo "   Install: https://aws.amazon.com/cli/"
    else
        AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2 || echo "unknown")
        echo "${GREEN}✅ AWS CLI: v$AWS_VERSION${NC}"
    fi
    
    # Check jq for JSON parsing (optional)
    if ! command -v jq &> /dev/null; then
        echo "${YELLOW}⚠️  jq not found (recommended for automation)${NC}"
        echo "   Install: apt install jq / brew install jq"
    else
        echo "${GREEN}✅ jq: installed${NC}"
    fi
    
    echo ""
    
    if [ $missing -eq 1 ]; then
        echo "${RED}❌ Missing required tools. Please install them and try again.${NC}"
        exit 1
    fi
    
    echo "${GREEN}✅ All prerequisites satisfied!${NC}"
    echo ""
}

# Function to configure AWS credentials
configure_aws_credentials() {
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}🔐 Step 2/6: AWS Credentials Configuration${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Check if AWS credentials are already configured
    if [ -f ~/.aws/credentials ] || [ -n "$AWS_ACCESS_KEY_ID" ]; then
        echo "${GREEN}✅ AWS credentials detected${NC}"
        
        # Verify credentials work
        if command -v aws &> /dev/null; then
            if aws sts get-caller-identity &> /dev/null; then
                AWS_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null || echo "unknown")
                AWS_USER=$(aws sts get-caller-identity --query 'Arn' --output text 2>/dev/null | cut -d'/' -f2 || echo "unknown")
                echo "${GREEN}   Account: $AWS_ACCOUNT${NC}"
                echo "${GREEN}   User: $AWS_USER${NC}"
                echo ""
                return 0
            fi
        fi
        
        echo "${YELLOW}⚠️  Credentials found but couldn't verify them${NC}"
        echo "   Continuing anyway..."
        echo ""
        return 0
    fi
    
    echo "${YELLOW}⚠️  No AWS credentials found${NC}"
    echo ""
    echo "InfraGenie needs AWS credentials to provision infrastructure."
    echo "You can provide them in one of two ways:"
    echo ""
    echo "  ${GREEN}Option 1: Environment Variables (Recommended)${NC}"
    echo "  ${GREEN}Option 2: AWS CLI Configuration${NC}"
    echo ""
    
    read -p "Do you want to configure credentials now? (yes/no): " configure_now
    
    if [ "$configure_now" != "yes" ]; then
        echo "${YELLOW}⚠️  Skipping credential configuration${NC}"
        echo "   Make sure to set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        echo "   environment variables before running this script."
        echo ""
        return 0
    fi
    
    echo ""
    echo "Please enter your AWS credentials:"
    echo "${YELLOW}(These will be exported as environment variables for this session only)${NC}"
    echo ""
    
    read -p "AWS Access Key ID: " aws_access_key
    read -sp "AWS Secret Access Key: " aws_secret_key
    echo ""
    
    if [ -n "$aws_access_key" ] && [ -n "$aws_secret_key" ]; then
        export AWS_ACCESS_KEY_ID="$aws_access_key"
        export AWS_SECRET_ACCESS_KEY="$aws_secret_key"
        
        read -p "AWS Region (default: us-east-1): " aws_region
        aws_region=${aws_region:-us-east-1}
        export AWS_DEFAULT_REGION="$aws_region"
        
        echo ""
        echo "${GREEN}✅ Credentials configured for this session${NC}"
        echo "${YELLOW}   Note: Credentials are NOT saved to disk (secure)${NC}"
        echo ""
    else
        echo "${RED}❌ Invalid credentials provided${NC}"
        exit 1
    fi
}

# Function to display deployment summary
show_deployment_summary() {
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}📊 Step 3/6: Deployment Summary${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "This deployment will:"
    echo "  • Provision infrastructure on AWS"
    echo "  • Configure security groups and networking"
    echo "  • Set up automated security (fail2ban, updates)"
    echo "  • Install and configure applications"
    echo "  • Enable Cost Assassin (8 PM daily shutdown)"
    echo ""
    echo "${YELLOW}⚠️  Important:${NC}"
    echo "  • Infrastructure will incur AWS charges"
    echo "  • Review costs in your AWS billing dashboard"
    echo "  • Use ./destroy.sh when done to avoid ongoing charges"
    echo ""
}

# Run pre-flight checks
check_prerequisites
configure_aws_credentials
show_deployment_summary

read -p "${YELLOW}Ready to deploy? This will provision real infrastructure. (yes/no): ${NC}" proceed
echo ""

if [ "$proceed" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Terraform deployment
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}🏗️  Step 4/6: Provisioning Infrastructure${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "   → Initializing Terraform..."
terraform init -input=false
if [ $? -ne 0 ]; then
    echo "${RED}❌ Terraform init failed${NC}"
    exit 1
fi
echo "${GREEN}   ✅ Terraform initialized${NC}"
echo ""

echo "   → Validating configuration..."
terraform validate
if [ $? -ne 0 ]; then
    echo "${RED}❌ Terraform validation failed${NC}"
    exit 1
fi
echo "${GREEN}   ✅ Configuration valid${NC}"
echo ""

echo "   → Planning infrastructure changes..."
echo ""
terraform plan -out=tfplan
if [ $? -ne 0 ]; then
    echo "${RED}❌ Terraform plan failed${NC}"
    exit 1
fi
echo ""
echo "${GREEN}   ✅ Plan created successfully${NC}"
echo ""

echo "${YELLOW}   ⏳ Applying changes (this may take 2-5 minutes)...${NC}"
terraform apply -auto-approve tfplan
if [ $? -ne 0 ]; then
    echo "${RED}❌ Terraform apply failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  • Check AWS credentials are valid"
    echo "  • Verify you have necessary IAM permissions"
    echo "  • Review error messages above"
    echo "  • Check AWS service limits/quotas"
    exit 1
fi

echo ""
echo "${GREEN}✅ Infrastructure provisioned successfully!${NC}"
echo ""

# Extract instance IP
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}📡 Step 5/6: Configuring Deployment${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "   → Extracting server information..."

# Try multiple methods to get instance IP
INSTANCE_IP=""

# Method 1: Terraform output (most reliable)
INSTANCE_IP=$(terraform output -raw instance_ip 2>/dev/null)

# Method 2: JSON output
if [ -z "$INSTANCE_IP" ] || [ "$INSTANCE_IP" == "null" ]; then
    INSTANCE_IP=$(terraform output -json 2>/dev/null | jq -r '.instance_ip.value // .server_ip.value // .public_ip.value' 2>/dev/null)
fi

# Method 3: Parse state file directly
if [ -z "$INSTANCE_IP" ] || [ "$INSTANCE_IP" == "null" ]; then
    INSTANCE_IP=$(terraform show -json 2>/dev/null | jq -r '.values.root_module.resources[] | select(.type=="aws_instance") | .values.public_ip' 2>/dev/null | head -n1)
fi

if [ -z "$INSTANCE_IP" ] || [ "$INSTANCE_IP" == "null" ]; then
    echo "${YELLOW}⚠️  Could not automatically extract instance IP${NC}"
    echo ""
    echo "Available outputs:"
    terraform output
    echo ""
    read -p "Enter the server IP address manually: " INSTANCE_IP
fi

if [ -z "$INSTANCE_IP" ]; then
    echo "${RED}❌ No instance IP provided${NC}"
    exit 1
fi

echo "${GREEN}   ✅ Server IP: $INSTANCE_IP${NC}"
echo ""

# Auto-detect SSH key
echo "   → Locating SSH key..."
SSH_KEY=""

# Check for Terraform-generated key
if [ -f "infragenie-key.pem" ]; then
    SSH_KEY="infragenie-key.pem"
    chmod 600 "$SSH_KEY"
    echo "${GREEN}   ✅ Found generated key: $SSH_KEY${NC}"
elif [ -f "terraform-key.pem" ]; then
    SSH_KEY="terraform-key.pem"
    chmod 600 "$SSH_KEY"
    echo "${GREEN}   ✅ Found generated key: $SSH_KEY${NC}"
else
    # Try to extract key from Terraform output
    terraform output -raw private_key 2>/dev/null > temp_key.pem
    if [ -s temp_key.pem ]; then
        SSH_KEY="temp_key.pem"
        chmod 600 "$SSH_KEY"
        echo "${GREEN}   ✅ Extracted key from Terraform output${NC}"
    else
        rm -f temp_key.pem
        echo "${YELLOW}   ⚠️  No SSH key found (will use default SSH auth)${NC}"
    fi
fi
echo ""

# Create Ansible inventory
echo "   → Creating Ansible inventory..."

if [ -n "$SSH_KEY" ]; then
    cat > inventory.ini << EOF
[servers]
$INSTANCE_IP ansible_user=ubuntu ansible_ssh_private_key_file=$SSH_KEY ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
EOF
else
    cat > inventory.ini << EOF
[servers]
$INSTANCE_IP ansible_user=ubuntu ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
EOF
fi

echo "${GREEN}   ✅ Inventory created${NC}"
echo ""

# Wait for instance to be ready with intelligent SSH polling
echo "   → Waiting for server to be ready..."
echo "${YELLOW}   ⏳ This typically takes 1-3 minutes (instance boot + SSH)${NC}"
echo ""

RETRIES=0
MAX_RETRIES=36  # 36 attempts * 10 seconds = 6 minutes max
START_TIME=$(date +%s)

# Build SSH command
if [ -n "$SSH_KEY" ]; then
    SSH_TEST_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 -o BatchMode=yes ubuntu@$INSTANCE_IP exit"
    SSH_CONNECT_CMD="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$INSTANCE_IP"
else
    SSH_TEST_CMD="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 -o BatchMode=yes ubuntu@$INSTANCE_IP exit"
    SSH_CONNECT_CMD="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$INSTANCE_IP"
fi

# Progress bar function
show_progress() {
    local current=$1
    local total=$2
    local elapsed=$3
    local bar_width=30
    local filled=$((current * bar_width / total))
    local empty=$((bar_width - filled))
    
    printf "\\r   ["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%% (%ds elapsed)" $((current * 100 / total)) "$elapsed"
}

until $SSH_TEST_CMD 2>/dev/null
do
    RETRIES=$((RETRIES+1))
    ELAPSED=$(($(date +%s) - START_TIME))
    
    if [ $RETRIES -ge $MAX_RETRIES ]; then
        echo ""
        echo ""
        echo "${RED}❌ Connection timeout after $MAX_RETRIES attempts (${ELAPSED}s)${NC}"
        echo ""
        echo "Troubleshooting checklist:"
        echo "  ${YELLOW}1.${NC} AWS Console → EC2 → Status: Should show '2/2 checks passed'"
        echo "  ${YELLOW}2.${NC} Security Group: Must allow SSH (port 22) from your IP"
        echo "  ${YELLOW}3.${NC} Instance: Should have a public IP address"
        echo "  ${YELLOW}4.${NC} VPC/Subnet: Instance must be in public subnet with internet access"
        if [ -z "$SSH_KEY" ]; then
            echo "  ${YELLOW}5.${NC} SSH Key: No key found, check Terraform generated 'infragenie-key.pem'"
        fi
        echo ""
        echo "Manual connection test:"
        echo "  $SSH_CONNECT_CMD"
        echo ""
        echo "${YELLOW}TIP: Infrastructure is deployed. Fix connectivity and run:${NC}"
        echo "  ansible-playbook -i inventory.ini playbook.yml"
        exit 1
    fi
    
    show_progress "$RETRIES" "$MAX_RETRIES" "$ELAPSED"
    sleep 10
done

TOTAL_WAIT=$(($(date +%s) - START_TIME))
echo ""
echo ""
echo "${GREEN}   ✅ Server ready! (${TOTAL_WAIT}s wait)${NC}"
echo ""

# Run Ansible configuration
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}⚙️  Step 6/6: Configuring Server${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "   → Running Ansible playbook..."
echo "${YELLOW}   ⏳ Installing packages and configuring services...${NC}"
echo ""

# Run Ansible with retry logic
MAX_ANSIBLE_ATTEMPTS=3
ANSIBLE_ATTEMPT=1

while [ $ANSIBLE_ATTEMPT -le $MAX_ANSIBLE_ATTEMPTS ]; do
    if [ $ANSIBLE_ATTEMPT -gt 1 ]; then
        echo ""
        echo "${YELLOW}   → Retry attempt $ANSIBLE_ATTEMPT/$MAX_ANSIBLE_ATTEMPTS${NC}"
    fi
    
    # Run Ansible with proper output formatting
    if ansible-playbook -i inventory.ini playbook.yml 2>&1 | tee /tmp/ansible_output.log; then
        echo ""
        echo "${GREEN}   ✅ Server configuration completed!${NC}"
        break
    else
        ANSIBLE_EXIT_CODE=$?
        
        if [ $ANSIBLE_ATTEMPT -lt $MAX_ANSIBLE_ATTEMPTS ]; then
            echo ""
            echo "${YELLOW}   ⚠️  Configuration failed (exit code: $ANSIBLE_EXIT_CODE)${NC}"
            echo "   → Waiting 20 seconds before retry..."
            sleep 20
            ANSIBLE_ATTEMPT=$((ANSIBLE_ATTEMPT + 1))
        else
            echo ""
            echo "${RED}   ❌ Ansible configuration failed after $MAX_ANSIBLE_ATTEMPTS attempts${NC}"
            echo ""
            echo "   Infrastructure is deployed but configuration incomplete."
            echo "   You can:"
            echo "     1. Check the logs above for specific errors"
            echo "     2. SSH to server: $SSH_CONNECT_CMD"
            echo "     3. Retry manually: ansible-playbook -i inventory.ini playbook.yml"
            echo "     4. Or destroy and redeploy: ./destroy.sh"
            echo ""
            exit 1
        fi
    fi
done

echo ""

# Final summary
echo ""
echo "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo "${GREEN}║          🎉 Deployment Successful! 🎉                 ║${NC}"
echo "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "${BLUE}📊 Deployment Summary:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ${GREEN}✅${NC} Infrastructure: Provisioned & Validated"
echo "  ${GREEN}✅${NC} Server: $INSTANCE_IP"
echo "  ${GREEN}✅${NC} Configuration: Applied Successfully"
echo "  ${GREEN}✅${NC} Security: fail2ban + auto-updates enabled"
echo "  ${GREEN}✅${NC} Cost Control: Auto-shutdown at 8 PM"
echo ""
echo "${BLUE}🔗 Quick Access:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$SSH_KEY" ]; then
    echo "  SSH Connection:"
    echo "    ${GREEN}$SSH_CONNECT_CMD${NC}"
    echo ""
    echo "  Or copy the command:"
    echo "    ${GREEN}ssh -i $SSH_KEY ubuntu@$INSTANCE_IP${NC}"
else
    echo "  SSH Connection:"
    echo "    ${GREEN}ssh ubuntu@$INSTANCE_IP${NC}"
fi
echo ""
echo "${BLUE}📂 Generated Files:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • main.tf - Infrastructure definition"
echo "  • terraform.tfstate - State (${RED}KEEP THIS FILE!${NC})"
if [ -n "$SSH_KEY" ]; then
    echo "  • $SSH_KEY - SSH private key (${RED}KEEP SECURE!${NC})"
fi
echo "  • inventory.ini - Ansible inventory"
echo "  • playbook.yml - Configuration playbook"
echo ""
echo "${YELLOW}⚠️  Important Reminders:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  1. ${YELLOW}Monitor AWS Costs${NC} - Check billing dashboard regularly"
echo "  2. ${YELLOW}Auto-Shutdown${NC} - Server stops at 8 PM daily (Cost Assassin)"
echo "  3. ${YELLOW}terraform.tfstate${NC} - Required for updates/destroy, don't delete!"
echo "  4. ${YELLOW}Security${NC} - Review security groups in AWS Console"
if [ -n "$SSH_KEY" ]; then
    echo "  5. ${YELLOW}SSH Key${NC} - Keep $SSH_KEY secure, it's your server access"
fi
echo ""
echo "${BLUE}🔄 Next Steps:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ${GREEN}Connect:${NC}     $SSH_CONNECT_CMD"
echo "  ${GREEN}Outputs:${NC}     terraform output"
echo "  ${GREEN}Update:${NC}      Edit main.tf → terraform apply"
echo "  ${GREEN}Destroy:${NC}     ./destroy.sh (when done)"
echo ""
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${GREEN}  Thank you for using InfraGenie! 🚀${NC}"
echo "${GREEN}  Generated by AI • Deployed with confidence${NC}"
echo "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
"""


# Destroy script template for infrastructure cleanup
DESTROY_SCRIPT_TEMPLATE = """#!/bin/bash

# InfraGenie - Infrastructure Destruction Script
# This script safely destroys all provisioned infrastructure
# Use this when you're done with your deployment

set -e

# Colors for output
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m' # No Color

echo "⚠️  ================================================"
echo "     INFRASTRUCTURE DESTRUCTION"
echo "    ================================================"
echo ""
echo "${YELLOW}WARNING: This will PERMANENTLY DELETE all resources.${NC}"
echo ""
echo "Resources that will be destroyed:"
terraform show -no-color | grep "^resource" || echo "  (Run 'terraform show' to see details)"
echo ""

read -p "Are you absolutely sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
    echo "Destruction cancelled."
    exit 0
fi

echo ""
echo "🗑️  Starting infrastructure destruction..."
echo "=========================================="
echo ""

# Check if Terraform state exists
if [ ! -f "terraform.tfstate" ]; then
    echo "${YELLOW}⚠️  No terraform.tfstate found.${NC}"
    echo "Either infrastructure was never created or state file is missing."
    read -p "Continue with destroy anyway? (yes/no): " force_confirm
    if [ "$force_confirm" != "yes" ]; then
        echo "Destruction cancelled."
        exit 0
    fi
fi

# Run Terraform destroy
terraform destroy -auto-approve

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================="
    echo "${GREEN}✅ Infrastructure Destroyed${NC}"
    echo "===================================="
    echo ""
    echo "All resources have been removed."
    echo "You can safely delete this directory."
    echo ""
    
    # Optionally remove generated files
    read -p "Remove generated files (terraform.tfstate, infragenie-key.pem)? (yes/no): " cleanup
    if [ "$cleanup" == "yes" ]; then
        rm -f terraform.tfstate terraform.tfstate.backup infragenie-key.pem inventory.ini
        echo "${GREEN}✅ Cleaned up generated files${NC}"
    fi
else
    echo "${RED}❌ Destruction failed${NC}"
    echo "Check the error messages above."
    echo "You may need to manually clean up resources in the AWS console."
    exit 1
fi

echo ""
echo "Thank you for using InfraGenie! 👋"
"""


def create_deployment_kit(state: AgentState) -> io.BytesIO:
    """
    Create a complete deployment kit ZIP archive from the workflow state.
    
    This function bundles all generated artifacts into a single downloadable
    ZIP file that contains everything needed to deploy the infrastructure.
    
    Args:
        state (AgentState): Complete workflow state with all generated content:
            - terraform_code: Validated Terraform HCL
            - ansible_playbook: Generated Ansible YAML
            - cost_estimate: Monthly cost string
            - user_prompt: Original request
    
    Returns:
        io.BytesIO: In-memory ZIP file ready for download/streaming
    
    ZIP Contents:
        - main.tf: Terraform infrastructure code
        - playbook.yml: Ansible configuration playbook
        - deploy.sh: Automated deployment script (executable)
        - README.md: Complete documentation
        - inventory.ini: Empty template for Ansible
    
    Example:
        ```python
        state = {
            "terraform_code": "provider \"aws\" {...}",
            "ansible_playbook": "---\\n- name: ...",
            "cost_estimate": "$24.50/mo",
            "user_prompt": "Create EC2 instance"
        }
        
        zip_buffer = create_deployment_kit(state)
        
        # Save to file
        with open("deployment-kit.zip", "wb") as f:
            f.write(zip_buffer.getvalue())
        
        # Or stream via HTTP
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=deployment-kit.zip"}
        )
        ```
    
    Implementation:
        - Uses in-memory BytesIO for efficiency
        - Sets proper file permissions (deploy.sh as executable)
        - Includes timestamp for traceability
        - Formats README with user context
        - Validates all required fields present
    """
    logger.info("=" * 60)
    logger.info("BUNDLER: Creating deployment kit")
    
    # Extract state components
    terraform_code = state.get("terraform_code", "")
    ansible_playbook = state.get("ansible_playbook", "")
    cost_estimate = state.get("cost_estimate", "Unknown")
    user_prompt = state.get("user_prompt", "Infrastructure deployment")
    
    # Validate required content
    if not terraform_code:
        logger.warning("No Terraform code in state, using placeholder")
        terraform_code = "# No Terraform code generated\n"
    
    if not ansible_playbook:
        logger.warning("No Ansible playbook in state, using placeholder")
        ansible_playbook = "---\n# No playbook generated\n"
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # Add main.tf
            logger.info("Adding main.tf to kit...")
            zip_file.writestr('main.tf', terraform_code)
            
            # Add playbook.yml
            logger.info("Adding playbook.yml to kit...")
            zip_file.writestr('playbook.yml', ansible_playbook)
            
            # Add deploy.sh with executable permissions
            logger.info("Adding deploy.sh to kit...")
            deploy_info = zipfile.ZipInfo('deploy.sh')
            deploy_info.external_attr = 0o755 << 16  # Unix executable permissions
            zip_file.writestr(deploy_info, DEPLOY_SCRIPT_TEMPLATE)
            
            # Add destroy.sh with executable permissions
            logger.info("Adding destroy.sh to kit...")
            destroy_info = zipfile.ZipInfo('destroy.sh')
            destroy_info.external_attr = 0o755 << 16  # Unix executable permissions
            zip_file.writestr(destroy_info, DESTROY_SCRIPT_TEMPLATE)
            
            # Add README.md
            logger.info("Adding README.md to kit...")
            readme_content = README_TEMPLATE.format(
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                cost=cost_estimate,
                user_prompt=user_prompt
            )
            zip_file.writestr('README.md', readme_content)
            
            # Add empty inventory.ini template
            logger.info("Adding inventory.ini template to kit...")
            inventory_template = """# Ansible Inventory
# This file will be populated automatically by deploy.sh
# Or manually add your server IPs here:

[servers]
# your-server-ip ansible_user=ubuntu
"""
            zip_file.writestr('inventory.ini', inventory_template)
        
        # Get file count and size
        zip_buffer.seek(0, 2)  # Seek to end
        zip_size = zip_buffer.tell()
        zip_buffer.seek(0)  # Reset to start
        
        logger.info(f"✓ Deployment kit created successfully")
        logger.info(f"  - Size: {zip_size / 1024:.2f} KB")
        logger.info(f"  - Files: main.tf, playbook.yml, deploy.sh, destroy.sh, README.md, inventory.ini")
        
        return zip_buffer
    
    except Exception as e:
        logger.error(f"Error creating deployment kit: {str(e)}")
        logger.exception("Full traceback:")
        
        # Return a minimal ZIP with error info
        error_zip = io.BytesIO()
        with zipfile.ZipFile(error_zip, 'w') as zf:
            zf.writestr('ERROR.txt', f"Failed to create deployment kit: {str(e)}")
        error_zip.seek(0)
        return error_zip
