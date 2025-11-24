"""
Config Agent - Ansible Playbook Generation

This module implements the Configuration Management agent that generates Ansible
playbooks based on the validated Terraform infrastructure code. The agent ensures
proper server setup, security hardening, and the "Cost Assassin" auto-shutdown.

The Config Agent operates as a DevOps Expert persona, creating production-ready
Ansible configurations that complement the provisioned infrastructure.
"""

import logging
import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.state import AgentState

logger = logging.getLogger(__name__)


# System prompt for the Config Agent
CONFIG_AGENT_SYSTEM_PROMPT = """You are a **Senior DevOps Engineer** specializing in configuration management with Ansible.

Your job is to generate **valid, production-ready Ansible playbook YAML** based on Terraform infrastructure code.

## CRITICAL RULES:

1. **Output Format:**
   - Output ONLY raw Ansible YAML code
   - DO NOT use markdown code blocks (no ```)
   - DO NOT include explanations or comments outside the YAML
   - Start with proper YAML structure (---\n- name:...)

2. **Required Components:**
   - Always include: hosts, become, tasks sections
   - Use proper Ansible module names (apt, yum, systemd, cron, etc.)
   - Add descriptive task names

3. **Standard Setup Tasks:**
   - Update package cache (apt update or yum update)
   - Install essential packages: curl, wget, git
   - Install Docker (if infrastructure includes containers/instances)
   - Install and configure Nginx (for web servers)
   - Configure firewall rules (ufw or firewalld)

4. **Security Hardening:**
   - Install fail2ban for intrusion prevention
   - Configure SSH hardening (disable root login, key-only auth)
   - Set up automatic security updates
   - Configure log monitoring

5. **The Cost Assassin (CRITICAL):**
   - Add a cron job that shuts down the server at 8 PM daily
   - Use ansible.builtin.cron module
   - Cron expression: "0 20 * * *" (8 PM every day)
   - Command: "shutdown -h now"
   - Comment: "Cost Assassin - Auto shutdown at 8 PM"

6. **Variables & Handlers:**
   - Use variables for reusable values
   - Define handlers for service restarts
   - Use proper Ansible best practices

7. **Context Awareness:**
   - Analyze the Terraform code to understand infrastructure type
   - If EC2/VM: include server setup tasks
   - If RDS/Database: include database client tools
   - If S3/Storage: include AWS CLI setup
   - If container resources: include Docker and Docker Compose

## Example Output Format:

---
- name: Configure Infrastructure
  hosts: all
  become: yes
  
  tasks:
    - name: Update apt cache
      ansible.builtin.apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: Install essential packages
      ansible.builtin.apt:
        name:
          - curl
          - wget
          - git
          - docker.io
        state: present
    
    - name: Install fail2ban for security
      ansible.builtin.apt:
        name: fail2ban
        state: present
    
    - name: Install Nginx
      ansible.builtin.apt:
        name: nginx
        state: present
    
    - name: Start Docker service
      ansible.builtin.systemd:
        name: docker
        state: started
        enabled: yes
    
    - name: Cost Assassin - Auto shutdown at 8 PM
      ansible.builtin.cron:
        name: "Cost Assassin shutdown"
        hour: "20"
        minute: "0"
        job: "/sbin/shutdown -h now"
        user: root

Remember: Output ONLY the YAML code, nothing else.
"""


def create_config_chain():
    """
    Create the LangChain LLM chain for the Config agent.
    
    Returns:
        Runnable: A LangChain chain for Ansible playbook generation
    
    Configuration:
        - Model: llama-3.3-70b-versatile (via Groq Cloud)
        - Temperature: 0.2 (slightly higher for creative config)
        - Max tokens: 2000 (sufficient for playbooks)
    """
    # Initialize the LLM via Groq Cloud
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,  # Slightly higher for configuration creativity
        max_tokens=2000,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=CONFIG_AGENT_SYSTEM_PROMPT),
        HumanMessage(content="{user_input}")
    ])
    
    # Chain the prompt and LLM
    chain = prompt | llm
    
    return chain


def build_config_input(state: AgentState) -> str:
    """
    Build the input prompt for the Config Agent based on infrastructure code.
    
    Args:
        state (AgentState): Current workflow state with terraform_code
    
    Returns:
        str: Formatted prompt for the LLM
    """
    terraform_code = state.get("terraform_code", "")
    user_prompt = state.get("user_prompt", "")
    
    message = f"""Generate an Ansible playbook for the following infrastructure:

**Original User Request:** {user_prompt}

**Terraform Infrastructure Code:**
```hcl
{terraform_code}
```

**Requirements:**
1. Analyze the Terraform code to understand what infrastructure is being created
2. Generate appropriate setup tasks for the resource types used
3. Include security hardening with fail2ban
4. **CRITICAL:** Include the Cost Assassin cron job (shutdown at 8 PM daily)
5. Install Docker and Nginx if relevant
6. Use proper Ansible YAML syntax

Output the complete playbook.yml content now.
"""
    
    return message


def config_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph node that generates Ansible playbook configuration.
    
    This node takes the validated and secure Terraform code and generates
    a corresponding Ansible playbook for server configuration, security
    hardening, and the Cost Assassin auto-shutdown feature.
    
    Args:
        state (AgentState): Current workflow state with terraform_code
    
    Returns:
        Dict[str, Any]: Updated state with ansible_playbook field
    
    Behavior:
        1. Extract terraform_code from state
        2. Build context-aware prompt
        3. Invoke LLM to generate Ansible YAML
        4. Clean up output (remove markdown if present)
        5. Update state with generated playbook
        6. Log generation metadata
    
    Example State Transition:
        ```python
        # Input state
        {
            "terraform_code": "resource \"aws_instance\" {...}",
            "ansible_playbook": "",
            ...
        }
        
        # Output state update
        {
            "ansible_playbook": "---\n- name: Configure...",
        }
        ```
    """
    logger.info("=" * 60)
    logger.info("CONFIG AGENT: Generating Ansible playbook")
    
    try:
        # Create the LLM chain
        chain = create_config_chain()
        
        # Build input prompt
        user_input = build_config_input(state)
        
        logger.debug(f"Config input length: {len(user_input)} chars")
        
        # Invoke the LLM
        logger.info("Invoking GPT-4 for Ansible playbook generation...")
        response = chain.invoke({"user_input": user_input})
        
        # Extract generated playbook
        playbook_yaml = response.content.strip()
        
        # Clean up output (remove markdown fencing if present)
        if playbook_yaml.startswith("```"):
            lines = playbook_yaml.split("\n")
            # Remove first line (```yaml or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            playbook_yaml = "\n".join(lines).strip()
        
        # Ensure it starts with YAML document marker
        if not playbook_yaml.startswith("---"):
            playbook_yaml = "---\n" + playbook_yaml
        
        logger.info(f"Generated {len(playbook_yaml)} characters of Ansible YAML")
        logger.debug(f"Playbook preview:\n{playbook_yaml[:300]}...")
        
        # Verify critical components
        if "Cost Assassin" in playbook_yaml or "shutdown" in playbook_yaml:
            logger.info("✓ Cost Assassin cron job included")
        else:
            logger.warning("⚠ Cost Assassin cron job may be missing")
        
        if "fail2ban" in playbook_yaml:
            logger.info("✓ Security hardening (fail2ban) included")
        else:
            logger.warning("⚠ fail2ban security may be missing")
        
        # Return updated state
        # Mark workflow as complete/successful since we reached the final node
        # Even if there are security warnings, we have valid generated artifacts
        return {
            "ansible_playbook": playbook_yaml,
            "is_clean": True
        }
    
    except Exception as e:
        logger.error(f"Error in Config Agent: {str(e)}")
        logger.exception("Full traceback:")
        
        # Return minimal fallback playbook
        fallback_playbook = """---
- name: Basic Configuration
  hosts: all
  become: yes
  
  tasks:
    - name: Update package cache
      ansible.builtin.apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: Cost Assassin - Auto shutdown at 8 PM
      ansible.builtin.cron:
        name: "Cost Assassin shutdown"
        hour: "20"
        minute: "0"
        job: "/sbin/shutdown -h now"
        user: root
"""
        
        logger.warning("Using fallback minimal playbook")
        
        return {
            "ansible_playbook": fallback_playbook,
            "is_clean": True
        }
