You are absolutely right to ask this. Since your project relies on **LangGraph (a state machine)** and **LLMs (nondeterministic inputs)**, the standard specs aren't quite enough for the backend logic.

You need **two specific technical documents** for the backend. Without these, you will likely get lost in "Prompt Hell" or "Infinite Loop Hell" when coding the agents.

Here are the two files you must add to backend/docs/:

### **1\. The Brain Logic: AGENT\_WORKFLOW.md**

**Why you need it:** You are building a **State Machine**, not a linear script. If you don't define the "States" and "Transitions" clearly, your code will turn into spaghetti. This document maps exactly how data moves between your Python functions.

**Save as:** backend/docs/AGENT\_WORKFLOW.md

Markdown

\# 🧠 Agentic Workflow Logic (LangGraph)

\#\# 1\. The Shared State (The "Memory")  
This data structure is passed between EVERY node in the graph.  
\`\`\`python  
class AgentState(TypedDict):  
    \# Inputs  
    user\_prompt: str          \# "I need an EC2..."  
    session\_id: str  
      
    \# Artifacts (The Code)  
    terraform\_code: str       \# Current HCL  
    ansible\_playbook: str     \# Current YAML  
      
    \# Feedback (The Loops)  
    validation\_error: str     \# Output of 'terraform validate'  
    security\_risks: List\[str\] \# Checkov IDs \['CKV\_AWS\_1'\]  
    retry\_count: int          \# Safety break (Max 3\)  
      
    \# Outputs  
    cost\_estimate: str        \# "$24.50"  
    is\_clean: bool            \# True if ready for Config Agent

## **2\. The Nodes (The Processors)**

| Node Name | Input | Action | Output Updates |
| :---- | :---- | :---- | :---- |
| architect | user\_prompt | LLM generates HCL | terraform\_code |
| validator | terraform\_code | Run terraform validate | validation\_error |
| security | terraform\_code | Run checkov | security\_risks |
| finops | terraform\_code | Run infracost | cost\_estimate |
| config | terraform\_code | LLM generates YAML | ansible\_playbook |

## **3\. The Edges (The Logic Flow)**

This defines the conditional routing.

1. **Start** \-\> architect  
2. architect \-\> validator  
3. **Condition A (Validator):**  
   * IF validation\_error exists AND retry\_count \< 3 \-\> GOTO architect (Fix it)  
   * ELSE IF retry\_count \>= 3 \-\> ERROR (Stop)  
   * ELSE (Clean) \-\> GOTO security  
4. **Condition B (Security):**  
   * IF security\_risks \> 0 AND retry\_count \< 3 \-\> GOTO architect (Patch it)  
   * ELSE \-\> GOTO finops  
5. finops \-\> config  
6. config \-\> **End**

## **4\. Failure Modes**

* **Infinite Loop:** If architect keeps generating bad code, retry\_count breaks the loop.  
* **Hallucination:** If LLM generates a non-existent resource, validator catches it immediately.

\---

\#\#\# 2\. The "Prompt Library": \`PROMPTS.md\`  
\*\*Why you need it:\*\* Prompt Engineering is 50% of this project. If you hardcode prompts inside your Python files, tweaking them later is a nightmare. Centralize them here first so you can iterate on the "English Code" before writing the Python Code.

\*\*Save as:\*\* \`backend/docs/PROMPTS.md\`

\`\`\`markdown  
\# 🗣️ System Prompts Library

\#\# A. The Architect (Terraform Generator)  
\*\*Context:\*\* Generates infrastructure code.  
\*\*Temperature:\*\* 0.1 (Strict)

\> "You are a Senior Cloud Architect. Your goal is to generate valid Terraform HCL code for AWS.  
\>   
\> \*\*Instructions:\*\*  
\> 1\. Use the \`hashicorp/aws\` provider.  
\> 2\. Do NOT wrap output in markdown blocks (no \`\`\`hcl). Output raw text only.  
\> 3\. Use \`t3.micro\` for EC2 instances to save costs, unless the user asks for high performance.  
\> 4\. If \`validation\_error\` is provided in the input, you MUST fix that specific error in your new output.  
\> 5\. If \`security\_risks\` are provided, you MUST patch those vulnerabilities (e.g., if CKV\_AWS\_24 is present, ensure port 22 is not open to 0.0.0.0/0)."

\---

\#\# B. The Config Manager (Ansible Generator)  
\*\*Context:\*\* Generates post-provisioning configuration.  
\*\*Temperature:\*\* 0.2

\> "You are a DevOps Engineer. You have received the following Terraform code:  
\> {terraform\_code}  
\>   
\> \*\*Instructions:\*\*  
\> 1\. Generate a single Ansible \`playbook.yml\` to configure these resources.  
\> 2\. \*\*Security Hardening (REQUIRED):\*\* Include tasks to install \`fail2ban\` and \`ufw\`.  
\> 3\. \*\*Cost Optimization (REQUIRED):\*\* If an EC2 instance is present, add a cron job:  
\>    \- Name: 'Cost Assassin'  
\>    \- Schedule: 20:00 (8 PM) daily.  
\>    \- Command: \`/sbin/shutdown \-h now\`  
\> 4\. Output ONLY raw YAML."

\---

\#\# C. The Explanation (Frontend UI)  
\*\*Context:\*\* When the user hovers over a node in the diagram.

\> "Explain this AWS resource to a junior developer in 1 sentence. Focus on cost and purpose."

### **📝 Summary of Backend Docs**

You now have everything needed to build the backend without guessing:

1. **AGENT\_WORKFLOW.md:** The Map (How the graph moves).  
2. **PROMPTS.md:** The Instructions (What the AI is told to do).  
3. **SPECS.md** (Existing): The Requirements (What the endpoints look like).

**Do not add any more documents.** Any more paperwork is procrastination. You are ready to build Phase 1\. 🚀

