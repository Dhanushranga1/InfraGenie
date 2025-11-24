This is the official **Project Design Document (PDD)** for **InfraGenie**.

---

# **InfraGenie: The Autonomous DevOps Architect**

Project Status: Planning Phase

Developer: Solo Engineer

Target Completion: 3 Weeks

---

## **1\. Executive Summary**

**InfraGenie** is an AI-powered Internal Developer Platform (IDP) designed to bridge the gap between "Generative AI" and "Production Engineering."

Unlike standard coding assistants that output raw text, InfraGenie functions as an autonomous agent. It architects, validates, secures, and configures cloud infrastructure, delivering a comprehensive **"Deployment Kit"** (Terraform \+ Ansible) that allows developers to launch production-ready environments in one click.

**The Hook:** "It doesn't just write the infrastructure; it budgets for it, secures it, and creates the automation to turn it off when you aren't looking."

---

## **2\. The Problem Statement**

Modern cloud development faces three critical issues, especially for startups and junior engineers:

1. **Security Debt:** Cloud resources are often provisioned with open ports and default passwords (e.g., leaving port 22 open).  
2. **Cost Leakage:** Development environments are spun up and forgotten, leading to massive cloud bills (Zombie Infrastructure).  
3. **Configuration Gap:** Terraform creates the server, but it doesn't configure the software inside it. Developers struggle to connect Terraform outputs to Ansible configuration.

## **3\. The Solution: "The Deployment Kit"**

InfraGenie solves this by generating a **Self-Contained Deployment Artifact**. Instead of managing the user's cloud directly (security risk), it generates a verified zip file containing:

* **Infrastructure:** Validated Terraform code (main.tf).  
* **Configuration:** Ansible Playbooks (playbook.yml) for hardening and software installation.  
* **Automation:** A deploy.sh script that automatically bridges Terraform outputs to Ansible inputs.

---

## **4\. Technical Architecture**

### **4.1 High-Level Stack**

| Layer | Technology | Purpose |
| :---- | :---- | :---- |
| **Frontend** | **Next.js 14** | App Router, Tailwind CSS, ShadcnUI. |
| **Visuals** | **ReactFlow** | Interactive node-based diagram of the infrastructure. |
| **Backend** | **FastAPI** | High-performance Async Python API. |
| **AI Logic** | **LangChain \+ LangGraph** | Orchestrating stateful multi-agent workflows. |
| **DevOps** | **Terraform** | Infrastructure as Code (IaC). |
| **Config** | **Ansible** | Configuration Management & Security Hardening. |
| **Security** | **Checkov** | Static Analysis (IaC Security Scanning). |
| **FinOps** | **Infracost** | Pre-deployment Cloud Cost Estimation. |

### **4.2 The "Agentic" Workflow (Backend)**

The backend runs a **LangGraph State Machine** with the following nodes:

1. **Architect Agent:** Parses user prompt (e.g., "Scalable Python App") $\\rightarrow$ Generates Terraform logic.  
2. **Validator Agent:** Runs terraform validate. If syntax errors exist, it self-corrects.  
3. **Security Guardian:** Runs checkov \-f main.tf. If high-severity risks are found (e.g., Open S3 bucket), it instructs the Architect Agent to patch them.  
4. **FinOps Advisor:** Runs infracost \--path . to tag the project with an estimated monthly cost.  
5. **Config Manager:** Generates the Ansible Playbook (e.g., installs Docker, sets up Nginx) and the "Cost Assassin" cron jobs.  
6. **Bundler:** Zips all verified files into the downloadable kit.

---

## **5\. Key Features (The "Wow" Factors)**

### **🛡️ Feature A: The "Fortress" (Auto-Hardening)**

InfraGenie assumes every environment is hostile. The generated Ansible playbook automatically:

* Disables Root Login.  
* Installs fail2ban.  
* Configures UFW (Firewall) to allow only necessary ports.

### **💰 Feature B: The "Cost Assassin" (FinOps)**

To solve "Zombie Infrastructure," the AI injects a specific Ansible task for development environments:

* **Action:** Sets up a system cron job to auto-shutdown the server at 8:00 PM and restart at 8:00 AM.  
* **Result:** Reduces development cloud bills by \~60% automatically.

### **📦 Feature C: The One-Click Deploy Script**

The system generates a deploy.sh script that handles the complex handoff between Terraform and Ansible:

Bash

\#\!/bin/bash  
\# 1\. Provision Infrastructure  
terraform apply \-auto-approve  
\# 2\. Dynamic Inventory Creation (The Hard Part)  
echo "\[web\]" \> inventory.ini  
terraform output \-raw public\_ip \>\> inventory.ini  
\# 3\. Configure Server  
ansible-playbook \-i inventory.ini playbook.yml

---

## **6\. Directory Structure (Monorepo)**

Plaintext

infragenie/  
├── 📂 frontend/                  \# Next.js Application  
│   ├── components/  
│   │   ├── ChatInterface.tsx  
│   │   └── ArchitectureDiagram.tsx (ReactFlow)  
│   └── app/page.tsx  
│  
├── 📂 backend/                   \# FastAPI Application  
│   ├── app/  
│   │   ├── api/  
│   │   │   └── routes.py         \# /generate, /download endpoints  
│   │   ├── core/  
│   │   │   ├── agents/           \# The AI Brains  
│   │   │   │   ├── architect.py  \# GPT-4o Wrapper  
│   │   │   │   ├── security.py   \# Checkov Integration  
│   │   │   │   └── config.py     \# Ansible Generator  
│   │   │   └── graph.py          \# LangGraph Workflow Definition  
│   │   └── services/  
│   │       ├── sandbox.py        \# Subprocess runner (Terraform/Checkov)  
│   │       └── bundler.py        \# Zip file creator  
│   ├── templates/                \# Jinja2 templates for Ansible/Terraform  
│   └── Dockerfile                \# Critical: Installs Py, TF, Ansible, Checkov  
│  
└── 📄 README.md

---

## **7\. Implementation Plan (3 Weeks)**

### **Phase 1: The Engine (Days 1-7)**

* **Objective:** Input Prompt $\\rightarrow$ Valid Deployment Kit (Zip).  
* \[ \] Set up FastAPI with Docker (Install Terraform/Ansible inside container).  
* \[ \] Implement LangGraph "Architect Agent" to generate main.tf.  
* \[ \] Implement "Security Agent" to run checkov and loop until clean.  
* \[ \] Implement "Config Agent" to write playbook.yml and deploy.sh.  
* \[ \] Create /download endpoint.

### **Phase 2: The Experience (Days 8-14)**

* **Objective:** A beautiful UI that visualizes the infrastructure.  
* \[ \] Initialize Next.js 14 project.  
* \[ \] Build Chat UI (Streaming responses).  
* \[ \] Implement ReactFlow to render nodes (EC2, RDS) based on backend JSON.  
* \[ \] Add "Cost" and "Security" badges to the UI.

### **Phase 3: The Polish & Documentation (Days 15-21)**

* \[ \] Write README.md with a Demo GIF.  
* \[ \] Create a simple Landing Page.  
* \[ \] Record a 2-minute Loom video walking through a deployment.  
* \[ \] (Optional) Deploy the tool itself (Frontend via Vercel, Backend via Render/Railway).

---

## **8\. Development Prerequisites**

To build this project, the developer needs:

1. **Docker Desktop:** To run the backend and the tools (Checkov/Terraform) in an isolated environment.  
2. **OpenAI API Key:** To power the Agents.  
3. **Infracost API Key:** (Free tier) for cost estimation.  
4. **AWS Account:** To test the *generated* code (InfraGenie itself does not need AWS keys, but the developer needs them to verify the output works).

