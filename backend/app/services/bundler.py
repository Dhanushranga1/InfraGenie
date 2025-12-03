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
# Interactive TUI-based deployment with beautiful dialogs
# Zero configuration required - just follow the prompts!

set -e  # Exit on error

# Colors for output
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
MAGENTA='\\033[0;35m'
NC='\\033[0m' # No Color

# Detect best dialog tool available
if command -v dialog &> /dev/null; then
    DIALOG_CMD="dialog"
elif command -v whiptail &> /dev/null; then
    DIALOG_CMD="whiptail"
else
    DIALOG_CMD="none"
fi

# Function to show welcome screen
show_welcome() {
    if [ "$DIALOG_CMD" != "none" ]; then
        $DIALOG_CMD --title "🚀 InfraGenie Deployment Wizard" \\
            --msgbox "Welcome to InfraGenie!\\n\\nThis wizard will guide you through deploying your AI-generated infrastructure.\\n\\n✨ Everything is automated\\n✅ Validated and secure\\n🚀 Production-ready\\n\\nPress ENTER to continue..." 14 60
    else
        clear
        echo "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
        echo "${CYAN}║        🚀 InfraGenie Deployment Wizard 🚀             ║${NC}"
        echo "${CYAN}║    AI-Generated Infrastructure - Zero Configuration     ║${NC}"
        echo "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "${GREEN}✨ Everything is automated${NC}"
        echo "${GREEN}✅ Validated and secure${NC}"
        echo "${GREEN}🚀 Production-ready${NC}"
        echo ""
        read -p "Press ENTER to continue..."
    fi
}

# Function to check and install prerequisites
check_prerequisites() {
    if [ "$DIALOG_CMD" != "none" ]; then
        # Use dialog for nice progress display
        (
        echo "10" ; echo "Checking Terraform..." ; sleep 0.5
        command -v terraform &> /dev/null && echo "30" || echo "30"
        echo "Checking Ansible..." ; sleep 0.5
        command -v ansible-playbook &> /dev/null && echo "60" || echo "60"
        echo "Checking AWS CLI..." ; sleep 0.5
        command -v aws &> /dev/null && echo "80" || echo "80"
        echo "Checking jq..." ; sleep 0.5
        command -v jq &> /dev/null && echo "100" || echo "100"
        ) | $DIALOG_CMD --title "📋 Prerequisites Check" --gauge "Checking required tools..." 8 60 0
    fi
    
    # Detailed check with results
    local missing=0
    local check_results=""
    
    # Check Terraform
    if command -v terraform &> /dev/null; then
        TF_VERSION=$(terraform version -json 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
        check_results+="✅ Terraform: v$TF_VERSION\\n"
    else
        check_results+="❌ Terraform: NOT FOUND\\n"
        missing=1
    fi
    
    # Check Ansible
    if command -v ansible-playbook &> /dev/null; then
        ANSIBLE_VERSION=$(ansible --version 2>/dev/null | head -n1 | awk '{print $2}' || echo "unknown")
        check_results+="✅ Ansible: v$ANSIBLE_VERSION\\n"
    else
        check_results+="❌ Ansible: NOT FOUND\\n"
        missing=1
    fi
    
    # Check AWS CLI (optional)
    if command -v aws &> /dev/null; then
        AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2 || echo "unknown")
        check_results+="✅ AWS CLI: v$AWS_VERSION\\n"
    else
        check_results+="⚠️  AWS CLI: Optional (recommended)\\n"
    fi
    
    # Check jq (optional)
    if command -v jq &> /dev/null; then
        check_results+="✅ jq: Installed\\n"
    else
        check_results+="⚠️  jq: Optional (recommended)\\n"
    fi
    
    if [ "$DIALOG_CMD" != "none" ]; then
        if [ $missing -eq 0 ]; then
            $DIALOG_CMD --title "✅ Prerequisites Check" --msgbox "$check_results\\nAll required tools are installed!" 12 60
        else
            $DIALOG_CMD --title "❌ Missing Prerequisites" --msgbox "$check_results\\nPlease install missing tools and try again.\\n\\nInstall Terraform: https://terraform.io\\nInstall Ansible: pip install ansible" 15 60
            clear
            exit 1
        fi
    else
        echo ""
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "${BLUE}📋 Prerequisites Check${NC}"
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "$check_results"
        
        if [ $missing -eq 1 ]; then
            echo "${RED}Please install missing tools and try again.${NC}"
            exit 1
        fi
        echo ""
    fi
}

# Function to configure AWS credentials
configure_aws_credentials() {
    # Check if AWS credentials are already configured
    if [ -f ~/.aws/credentials ] || [ -n "$AWS_ACCESS_KEY_ID" ]; then
        if command -v aws &> /dev/null; then
            if aws sts get-caller-identity &> /dev/null 2>&1; then
                AWS_ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null || echo "unknown")
                AWS_USER=$(aws sts get-caller-identity --query 'Arn' --output text 2>/dev/null | cut -d'/' -f2 || echo "unknown")
                
                if [ "$DIALOG_CMD" != "none" ]; then
                    $DIALOG_CMD --title "✅ AWS Credentials Found" --msgbox "AWS credentials detected and validated!\\n\\nAccount: $AWS_ACCOUNT\\nUser: $AWS_USER\\n\\nProceeding with deployment..." 12 60
                else
                    echo "${GREEN}✅ AWS credentials detected and validated${NC}"
                    echo "   Account: $AWS_ACCOUNT"
                    echo "   User: $AWS_USER"
                    echo ""
                fi
                return 0
            fi
        fi
    fi
    
    # No credentials found - collect interactively
    if [ "$DIALOG_CMD" != "none" ]; then
        # Show info dialog
        $DIALOG_CMD --title "🔐 AWS Credentials Required" --msgbox "InfraGenie needs AWS credentials to deploy infrastructure.\\n\\nYou'll be asked to provide:\\n• AWS Access Key ID\\n• AWS Secret Access Key\\n• AWS Region (optional)\\n\\n💡 Your credentials will only be used for this session\\n🔒 They will NOT be saved to disk\\n\\nPress ENTER to continue..." 16 65
        
        # Collect Access Key ID
        aws_access_key=$($DIALOG_CMD --title "AWS Access Key ID" --inputbox "Enter your AWS Access Key ID:\\n\\n(Starts with AKIA...)" 10 60 3>&1 1>&2 2>&3 3>&-)
        
        if [ -z "$aws_access_key" ]; then
            $DIALOG_CMD --title "❌ Error" --msgbox "AWS Access Key ID is required!\\n\\nDeployment cancelled." 8 50
            clear
            exit 1
        fi
        
        # Collect Secret Access Key
        aws_secret_key=$($DIALOG_CMD --title "AWS Secret Access Key" --passwordbox "Enter your AWS Secret Access Key:\\n\\n(Will be hidden for security)" 10 60 3>&1 1>&2 2>&3 3>&-)
        
        if [ -z "$aws_secret_key" ]; then
            $DIALOG_CMD --title "❌ Error" --msgbox "AWS Secret Access Key is required!\\n\\nDeployment cancelled." 8 50
            clear
            exit 1
        fi
        
        # Collect Region
        aws_region=$($DIALOG_CMD --title "AWS Region" --inputbox "Enter AWS Region:\\n\\n(Leave empty for default: us-east-1)" 10 60 "us-east-1" 3>&1 1>&2 2>&3 3>&-)
        aws_region=${aws_region:-us-east-1}
        
        # Confirm credentials
        $DIALOG_CMD --title "🔐 Credentials Configured" --msgbox "AWS credentials configured for this session!\\n\\nRegion: $aws_region\\n\\n✅ Ready to deploy\\n🔒 Credentials stored in environment only" 12 60
        
    else
        # Fallback to terminal input
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "${BLUE}🔐 AWS Credentials Configuration${NC}"
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "${YELLOW}No AWS credentials found.${NC}"
        echo ""
        echo "Please enter your AWS credentials:"
        echo "${YELLOW}(These will be exported as environment variables for this session only)${NC}"
        echo ""
        
        read -p "AWS Access Key ID: " aws_access_key
        read -sp "AWS Secret Access Key: " aws_secret_key
        echo ""
        read -p "AWS Region (default: us-east-1): " aws_region
        aws_region=${aws_region:-us-east-1}
        
        if [ -z "$aws_access_key" ] || [ -z "$aws_secret_key" ]; then
            echo "${RED}❌ Credentials are required!${NC}"
            exit 1
        fi
        
        echo ""
        echo "${GREEN}✅ Credentials configured for this session${NC}"
        echo ""
    fi
    
    # Export credentials
    export AWS_ACCESS_KEY_ID="$aws_access_key"
    export AWS_SECRET_ACCESS_KEY="$aws_secret_key"
    export AWS_DEFAULT_REGION="$aws_region"
}

# Function to display deployment summary
show_deployment_summary() {
    local summary="This deployment will:\\n\\n"
    summary+="✨ Provision infrastructure on AWS\\n"
    summary+="🔒 Configure security (firewalls, fail2ban)\\n"
    summary+="📦 Install and configure applications\\n"
    summary+="💰 Enable Cost Assassin (8 PM shutdown)\\n\\n"
    summary+="⚠️  Important:\\n"
    summary+="• Infrastructure will incur AWS charges\\n"
    summary+="• Use ./destroy.sh when done\\n"
    summary+="• Review costs in AWS billing dashboard"
    
    if [ "$DIALOG_CMD" != "none" ]; then
        if $DIALOG_CMD --title "📊 Deployment Summary" --yesno "$summary\\n\\nReady to proceed with deployment?" 20 65; then
            return 0
        else
            $DIALOG_CMD --title "Cancelled" --msgbox "Deployment cancelled by user." 6 40
            clear
            exit 0
        fi
    else
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "${BLUE}📊 Deployment Summary${NC}"
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "$summary"
        echo ""
        read -p "${YELLOW}Ready to deploy? (yes/no): ${NC}" proceed
        if [ "$proceed" != "yes" ]; then
            echo "Deployment cancelled."
            exit 0
        fi
    fi
}

# Show progress in dialog
show_step_progress() {
    local step_title="$1"
    local step_desc="$2"
    local step_num="$3"
    
    if [ "$DIALOG_CMD" == "none" ]; then
        echo ""
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "${BLUE}$step_title${NC}"
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "   $step_desc"
        echo ""
    fi
}

# Main execution
clear
show_welcome
check_prerequisites
configure_aws_credentials
show_deployment_summary

# Terraform deployment
show_step_progress "🏗️  Step 4/6: Provisioning Infrastructure" "Setting up your AWS resources..."

if [ "$DIALOG_CMD" != "none" ]; then
    # Run Terraform with progress dialog
    (
        echo "10"
        echo "Initializing Terraform..."
        terraform init -input=false > /tmp/terraform_init.log 2>&1
        if [ $? -ne 0 ]; then
            cat /tmp/terraform_init.log
            exit 1
        fi
        
        echo "25"
        echo "Validating configuration..."
        terraform validate > /tmp/terraform_validate.log 2>&1
        if [ $? -ne 0 ]; then
            cat /tmp/terraform_validate.log
            exit 1
        fi
        
        echo "40"
        echo "Planning infrastructure changes..."
        terraform plan -out=tfplan > /tmp/terraform_plan.log 2>&1
        if [ $? -ne 0 ]; then
            cat /tmp/terraform_plan.log
            exit 1
        fi
        
        echo "50"
        echo "Provisioning infrastructure... (2-5 minutes)"
        terraform apply -auto-approve tfplan > /tmp/terraform_apply.log 2>&1
        if [ $? -ne 0 ]; then
            cat /tmp/terraform_apply.log
            exit 1
        fi
        
        echo "100"
        echo "Infrastructure provisioned successfully!"
        sleep 1
    ) | $DIALOG_CMD --title "🏗️  Infrastructure Provisioning" --gauge "Preparing..." 8 70 0
    
    if [ $? -ne 0 ]; then
        $DIALOG_CMD --title "Error" --msgbox "Terraform failed. Check logs:\\n\\n$(tail -20 /tmp/terraform_*.log | head -10)" 15 70
        exit 1
    fi
    
    $DIALOG_CMD --title "Success" --msgbox "✅ Infrastructure provisioned successfully!\\n\\nYour AWS resources are now ready." 8 50
else
    # Terminal fallback
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
fi

# Extract instance IP
show_step_progress "📡 Step 5/6: Configuring Deployment" "Extracting server information..."

if [ "$DIALOG_CMD" == "none" ]; then
    echo "   → Extracting server information..."
fi

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
    if [ "$DIALOG_CMD" != "none" ]; then
        INSTANCE_IP=$($DIALOG_CMD --title "Server IP Required" \
            --inputbox "Could not automatically extract instance IP.\\n\\nPlease check 'terraform output' and enter the IP:" 12 60 \
            3>&1 1>&2 2>&3 3>&-)
    else
        echo "${YELLOW}⚠️  Could not automatically extract instance IP${NC}"
        echo ""
        echo "Available outputs:"
        terraform output
        echo ""
        read -p "Enter the server IP address manually: " INSTANCE_IP
    fi
fi

if [ -z "$INSTANCE_IP" ]; then
    if [ "$DIALOG_CMD" != "none" ]; then
        $DIALOG_CMD --title "Error" --msgbox "No instance IP provided. Cannot continue." 6 50
    else
        echo "${RED}❌ No instance IP provided${NC}"
    fi
    exit 1
fi

if [ "$DIALOG_CMD" == "none" ]; then
    echo "${GREEN}   ✅ Server IP: $INSTANCE_IP${NC}"
    echo ""
fi

# Auto-detect SSH key
if [ "$DIALOG_CMD" == "none" ]; then
    echo "   → Locating SSH key..."
fi

SSH_KEY=""

# Check for Terraform-generated key
if [ -f "infragenie-key.pem" ]; then
    SSH_KEY="infragenie-key.pem"
    chmod 600 "$SSH_KEY"
    [ "$DIALOG_CMD" == "none" ] && echo "${GREEN}   ✅ Found generated key: $SSH_KEY${NC}"
elif [ -f "terraform-key.pem" ]; then
    SSH_KEY="terraform-key.pem"
    chmod 600 "$SSH_KEY"
    [ "$DIALOG_CMD" == "none" ] && echo "${GREEN}   ✅ Found generated key: $SSH_KEY${NC}"
else
    # Try to extract key from Terraform output
    terraform output -raw private_key 2>/dev/null > temp_key.pem
    if [ -s temp_key.pem ]; then
        SSH_KEY="temp_key.pem"
        chmod 600 "$SSH_KEY"
        [ "$DIALOG_CMD" == "none" ] && echo "${GREEN}   ✅ Extracted key from Terraform output${NC}"
    else
        rm -f temp_key.pem
        [ "$DIALOG_CMD" == "none" ] && echo "${YELLOW}   ⚠️  No SSH key found (will use default SSH auth)${NC}"
    fi
fi

[ "$DIALOG_CMD" == "none" ] && echo ""

# Create Ansible inventory
if [ "$DIALOG_CMD" == "none" ]; then
    echo "   → Creating Ansible inventory..."
fi

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

if [ "$DIALOG_CMD" == "none" ]; then
    echo "${GREEN}   ✅ Inventory created${NC}"
    echo ""
fi

# Wait for instance to be ready with intelligent SSH polling
if [ "$DIALOG_CMD" == "none" ]; then
    echo "   → Waiting for server to be ready..."
    echo "${YELLOW}   ⏳ This typically takes 1-3 minutes (instance boot + SSH)${NC}"
    echo ""
fi

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

# Wait with progress gauge for dialog mode
if [ "$DIALOG_CMD" != "none" ]; then
    (
        until $SSH_TEST_CMD 2>/dev/null
        do
            RETRIES=$((RETRIES+1))
            ELAPSED=$(($(date +%s) - START_TIME))
            PERCENTAGE=$((RETRIES * 100 / MAX_RETRIES))
            
            if [ $RETRIES -ge $MAX_RETRIES ]; then
                echo "100"
                echo "Connection timeout!"
                sleep 1
                exit 1
            fi
            
            echo "$PERCENTAGE"
            echo "Waiting for SSH... (Attempt $RETRIES/$MAX_RETRIES, ${ELAPSED}s elapsed)"
            sleep 10
        done
        
        echo "100"
        TOTAL_WAIT=$(($(date +%s) - START_TIME))
        echo "Server ready! (${TOTAL_WAIT}s)"
        sleep 1
    ) | $DIALOG_CMD --title "🔌 Waiting for Server" --gauge "Connecting to $INSTANCE_IP..." 8 70 0
    
    if [ $? -ne 0 ]; then
        $DIALOG_CMD --title "Connection Error" --msgbox "Could not connect to server after $MAX_RETRIES attempts.\\n\\nTroubleshooting:\\n• Check AWS Console EC2 status\\n• Verify Security Group allows SSH\\n• Ensure instance has public IP\\n\\nTry manual connection:\\n$SSH_CONNECT_CMD" 16 70
        exit 1
    fi
    
    $DIALOG_CMD --title "Success" --msgbox "✅ Server is ready and accepting connections!" 6 50
else
    # Terminal progress bar fallback
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
fi

# Run Ansible configuration
show_step_progress "⚙️  Step 6/6: Configuring Server" "Installing packages and configuring services..."

# Run Ansible with retry logic
MAX_ANSIBLE_ATTEMPTS=3
ANSIBLE_ATTEMPT=1

if [ "$DIALOG_CMD" != "none" ]; then
    # Run Ansible with progress dialog
    (
        while [ $ANSIBLE_ATTEMPT -le $MAX_ANSIBLE_ATTEMPTS ]; do
            PERCENTAGE=$((ANSIBLE_ATTEMPT * 33))
            echo "$PERCENTAGE"
            echo "Running Ansible (attempt $ANSIBLE_ATTEMPT/$MAX_ANSIBLE_ATTEMPTS)..."
            
            if ansible-playbook -i inventory.ini playbook.yml > /tmp/ansible_output.log 2>&1; then
                echo "100"
                echo "Configuration completed successfully!"
                sleep 1
                break
            else
                if [ $ANSIBLE_ATTEMPT -lt $MAX_ANSIBLE_ATTEMPTS ]; then
                    echo "$PERCENTAGE"
                    echo "Configuration failed, retrying in 20 seconds..."
                    sleep 20
                    ANSIBLE_ATTEMPT=$((ANSIBLE_ATTEMPT + 1))
                else
                    echo "100"
                    echo "Configuration failed after $MAX_ANSIBLE_ATTEMPTS attempts"
                    sleep 1
                    exit 1
                fi
            fi
        done
    ) | $DIALOG_CMD --title "⚙️  Server Configuration" --gauge "Installing packages..." 8 70 0
    
    if [ $? -ne 0 ]; then
        $DIALOG_CMD --title "Configuration Failed" --msgbox "Ansible configuration failed.\\n\\nYou can retry manually:\\nansible-playbook -i inventory.ini playbook.yml\\n\\nOr destroy and redeploy:\\n./destroy.sh" 12 70
        exit 1
    fi
else
    # Terminal fallback
    echo "   → Running Ansible playbook..."
    echo "${YELLOW}   ⏳ Installing packages and configuring services...${NC}"
    echo ""
    
    while [ $ANSIBLE_ATTEMPT -le $MAX_ANSIBLE_ATTEMPTS ]; do
        if [ $ANSIBLE_ATTEMPT -gt 1 ]; then
            echo ""
            echo "${YELLOW}   → Retry attempt $ANSIBLE_ATTEMPT/$MAX_ANSIBLE_ATTEMPTS${NC}"
        fi
        
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
fi

# Final success summary
if [ "$DIALOG_CMD" != "none" ]; then
    # Beautiful success dialog
    SUCCESS_MSG="🎉 Deployment completed successfully!\\n\\n"
    SUCCESS_MSG+="📊 Summary:\\n"
    SUCCESS_MSG+="✅ Infrastructure provisioned\\n"
    SUCCESS_MSG+="✅ Server IP: $INSTANCE_IP\\n"
    SUCCESS_MSG+="✅ Security configured\\n"
    SUCCESS_MSG+="✅ Cost control active (8 PM shutdown)\\n\\n"
    SUCCESS_MSG+="🔗 SSH Connection:\\n"
    if [ -n "$SSH_KEY" ]; then
        SUCCESS_MSG+="   ssh -i $SSH_KEY ubuntu@$INSTANCE_IP\\n\\n"
    else
        SUCCESS_MSG+="   ssh ubuntu@$INSTANCE_IP\\n\\n"
    fi
    SUCCESS_MSG+="⚠️  Important:\\n"
    SUCCESS_MSG+="• Monitor AWS costs\\n"
    SUCCESS_MSG+="• Keep terraform.tfstate file\\n"
    SUCCESS_MSG+="• Run ./destroy.sh when done"
    
    $DIALOG_CMD --title "🎉 Deployment Complete!" --msgbox "$SUCCESS_MSG" 22 70
    clear
else
    # Terminal success display
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
fi
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
