\# 🛠️ InfraGenie: Product Specifications

\#\# 1\. User Flow  
1\.  \*\*Login:\*\* User signs in via GitHub (Clerk).  
2\.  \*\*Input:\*\* User types prompt: \*"I need a scalable Python API with Postgres."\*  
3\.  \*\*Processing (The Black Box):\*\*  
    \* \*\*Agent A (Architect):\*\* Generates Terraform HCL.  
    \* \*\*Agent B (Security):\*\* Runs \`checkov\`. Patches if high severity.  
    \* \*\*Agent C (FinOps):\*\* Runs \`infracost\`. Estimates price.  
    \* \*\*Agent D (Config):\*\* Generates Ansible \`playbook.yml\`.  
4\.  \*\*Review:\*\* User sees Diagram (ReactFlow), Code Preview, and Cost Estimate.  
5\.  \*\*Action:\*\* User clicks \*\*"Download Kit"\*\*.

\#\# 2\. Functional Requirements

\#\#\# Backend (FastAPI)  
\* \*\*Endpoint:\*\* \`POST /api/v1/generate\`  
    \* Input: \`{"prompt": "string", "user\_id": "string"}\`  
    \* Output: \`{"status": "completed", "files": {...}, "cost": "$24.00"}\`  
\* \*\*Endpoint:\*\* \`POST /api/v1/download\`  
    \* Input: \`project\_id\`  
    \* Output: \`.zip\` file stream.  
\* \*\*Sandboxing:\*\* Must run Terraform/Checkov in isolated Docker processes.

\#\#\# Frontend (Next.js)  
\* \*\*Chat UI:\*\* Streaming text effect (Typewriter).  
\* \*\*Diagram:\*\* Dynamic Node Graph.  
    \* Nodes: EC2, RDS, S3.  
    \* Edges: Security Groups (Port 80 allowed).  
\* \*\*Badges:\*\*  
    \* 🛡️ Security Score (e.g., "A+")  
    \* 💰 Monthly Cost (e.g., "$15.20")

\#\# 3\. The "Deployment Kit" Artifact Structure  
The downloaded zip must match this exact tree:  
\`\`\`text  
project-name/  
├── main.tf           \# Infrastructure definition  
├── outputs.tf        \# Outputs (IPs, DNS)  
├── playbook.yml      \# Ansible Configuration  
├── inventory.ini     \# (Empty \- populated by script)  
├── README.md         \# Instructions  
└── deploy.sh         \# The "Magic Script"  
Here is the revised, highly detailed SPECS.md. I have expanded the **Backend Architecture** section to explicitly define the **LangChain** and **LangGraph** implementation details, including the state schema, prompt strategies, and agent orchestration logic.

---

# **InfraGenie: Product Specifications and Technical Requirements**

## **1\. Introduction**

This document defines the comprehensive functional and technical specifications for **InfraGenie**, an AI-powered Internal Developer Platform (IDP). It serves as the authoritative blueprint for development, specifically focusing on the integration of Large Language Models (LLMs) via LangChain to automate DevOps workflows.

## **2\. System Overview**

InfraGenie operates as a **Stateful Multi-Agent System**. It does not simply "prompt" an LLM; it orchestrates a directed cyclic graph (DCG) of specialized AI agents that reason, generate, validate, and fix infrastructure code iteratively before presenting it to the user.

## **3\. User Journey**

1. **Authentication:** User authenticates via GitHub (Clerk).  
2. **Intent Capture:** User submits a high-level request (e.g., "AWS ECS Cluster with Fargate").  
3. **Agentic Orchestration (The "Brain"):** The backend initializes a LangGraph workflow to architect, validate, and cost-optimize the solution.  
4. **Interactive Visualization:** The frontend renders the real-time infrastructure topology using ReactFlow.  
5. **Delivery:** User downloads a validated .zip artifact containing the execution-ready code.

## **4\. Technical Requirements: The AI Engine (LangChain \+ LangGraph)**

### **4.1 Orchestration Framework**

The backend logic must be implemented using **LangGraph** to manage the cyclic workflow. A simple linear chain is insufficient due to the requirement for self-correction loops (Validation and Security patching).

Graph State Schema (TypedDict):

The shared state passed between agents must adhere to the following structure:

Python

class AgentState(TypedDict):  
    user\_prompt: str             \# Original user intent  
    terraform\_code: str          \# Current version of HCL code  
    validation\_errors: List\[str\] \# Output from 'terraform validate'  
    security\_risks: List\[dict\]   \# Output from 'checkov'  
    cost\_estimate: str           \# Output from 'infracost'  
    ansible\_playbook: str        \# Generated YAML configuration  
    retry\_count: int             \# To prevent infinite loops

### **4.2 Agent Definitions & Prompts**

All LLM interactions must utilize **LangChain's ChatOpenAI** wrapper (Model: gpt-4o) with **System Messages** to enforce strict persona adoption.

#### **A. The Architect Agent (Node)**

* **Role:** Senior Cloud Architect.  
* **LangChain Component:** LLMChain with Structured Output Parser (Pydantic).  
* **System Prompt Strategy:**  
  "You are a Terraform Expert. You must output strictly valid HCL code for AWS. Do not include markdown fencing. Use t3.micro for EC2 unless specified otherwise."  
* **Input:** AgentState.user\_prompt  
* **Output:** Updates AgentState.terraform\_code.

#### **B. The Validator Tool (Node)**

* **Type:** Deterministic Tool (Not LLM).  
* **Implementation:** subprocess.run(\['terraform', 'validate', '-json'\]).  
* **Logic:**  
  * If exit\_code \== 0: Transition to Security Node.  
  * If exit\_code \!= 0: Update AgentState.validation\_errors and transition back to **Architect Agent** for repair.

#### **C. The Security Guardian (Node)**

* **Type:** Hybrid (Tool \+ LLM).  
* **Tool Step:** Execute checkov \-f main.tf \--output json.  
* **Reasoning Step (LLM):** If High/Critical risks are found, invoke the LLM to rewrite the Terraform code to fix specific violations (e.g., "Restrict ingress on port 22").  
* **LangGraph Edge:**  
  * Risk Count \> 0: Loop back to Validator.  
  * Risk Count \== 0: Proceed to FinOps.

#### **D. The FinOps Advisor (Node)**

* **Type:** Deterministic Tool.  
* **Implementation:** subprocess.run(\['infracost', 'breakdown', '--path', '.'\]).  
* **Output:** Updates AgentState.cost\_estimate.

#### **E. The Configuration Agent (Node)**

* **Role:** Ansible Automation Engineer.  
* **LangChain Component:** LLMChain.  
* **Prompt Strategy:**  
  "Given the following Terraform resources \[INSERT TERRYFORM\], generate an Ansible Playbook. If EC2 is present, inject a cron job to shut down the server at 8 PM daily."  
* **Input:** AgentState.terraform\_code.  
* **Output:** Updates AgentState.ansible\_playbook.

---

## **5\. Functional Requirements: Application Layer**

### **5.1 Backend (FastAPI)**

* **API Framework:** FastAPI with Pydantic v2.  
* **Asynchronous Execution:** Generation endpoints must be async to prevent blocking the main thread while LangChain agents invoke external CLI tools (Terraform/Checkov).  
* **Dependencies:**  
  * langchain-openai: For LLM integration.  
  * langgraph: For state machine definition.  
  * python-multipart: For file handling.  
* **Sandboxing:** All CLI tool executions must occur within the Docker container's shell environment.

### **5.2 Frontend (Next.js 14\)**

* **Component Library:** ShadcnUI \+ Tailwind CSS.  
* **State Management:** React Query (TanStack Query) for handling API loading states.  
* **Visualization Logic:**  
  * Must implement a parser to convert **Terraform JSON** (generated by terraform show \-json) into **ReactFlow Nodes and Edges**.  
  * *Example:* An aws\_instance becomes a Node; a security\_group\_rule becomes an Edge connecting the instance to the internet.

---

## **6\. Deployment Kit Artifacts**

The final output provided to the user must be a standardized .zip file containing:

| File | Source Component | Description |
| :---- | :---- | :---- |
| main.tf | Architect Agent | The validated, secured Infrastructure as Code. |
| playbook.yml | Config Agent | Ansible configuration including hardening rules. |
| outputs.tf | Static Template | Standard outputs (Public IP, Instance ID). |
| deploy.sh | Static Script | Bash script bridging Terraform outputs to Ansible inventory. |
| README.md | Static Template | Instructions for setting AWS credentials. |

## **7\. Non-Functional Requirements**

1. **AI Reliability:** The Architect Agent must implement a retry\_limit (Max 3\) in the LangGraph workflow to prevent infinite loops if validation fails repeatedly.  
2. **Security:** The Backend must **never** ask for or store the user's AWS Secret Keys. All execution happens on the user's machine via the downloaded kit.  
3. **Performance:** "Cold Start" generation time should remain under 60 seconds.  
4. **Cost Control:** The system must default to AWS Free Tier resources (t2.micro or t3.micro) unless the user explicitly requests high-performance computing.

