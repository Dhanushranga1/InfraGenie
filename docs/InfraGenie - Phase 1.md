This is the **Detailed Engineering Execution Plan for Phase 1**.

This document is written for the **Backend Engineer** (You). It contains the exact technical steps, command-line arguments, and logic flows required to build the "Engine" of InfraGenie.

**Goal:** Transform an empty folder into a Dockerized FastAPI service that accepts a prompt and returns a verifiable "Deployment Kit" zip file.

---

## **🏗️ Step 1.1: The "Toolbox" Container (Dockerfile)**

**Context:** We cannot rely on the host machine having Terraform or Checkov. The Docker container must be a self-contained DevOps environment.

**Action Items:**

1. **Create backend/Dockerfile:**  
   * **Base Image:** python:3.11-slim-bookworm (Debian-based is easier for installing tools than Alpine).  
   * **System Dependencies:** Install curl, unzip, git, software-properties-common, gnupg.  
   * **Terraform Install:** Add HashiCorp GPG key, add repo, apt-get install terraform.  
   * **Ansible Install:** pip install ansible.  
   * **Checkov Install:** pip install checkov.  
   * **Infracost Install:** Download the binary from GitHub releases, chmod \+x, and move to /usr/local/bin.  
   * **Python Deps:** Copy requirements.txt and install.  
2. **Create backend/requirements.txt:**  
3. Plaintext

fastapi  
uvicorn  
pydantic  
langchain  
langchain-openai  
langgraph  
python-multipart  
python-dotenv

4.   
5.   
6. **Environment Config (.env):**  
   * OPENAI\_API\_KEY=sk-...  
   * INFRACOST\_API\_KEY=ico-... (Get this free from infracost.io).  
7. **Verification:**  
   * Build: docker build \-t infragenie-backend ./backend  
   * Run: docker run \--rm infragenie-backend terraform \--version (Must output v1.x.x).

**✅ Definition of Done:** Docker build succeeds, and you can run terraform, ansible, checkov, and infracost commands inside the container.

---

## **🧠 Step 1.2: The State & Architecture (LangGraph)**

**Context:** We are building a State Machine, not a linear script. We need to define the "Memory" that gets passed between agents.

**Action Items:**

1. Define State (app/core/state.py):  
   Create a TypedDict class named AgentState:  
   * user\_prompt (str): The original request.  
   * terraform\_code (str): The HCL code (starts empty).  
   * validation\_error (str | None): Output from terraform validate.  
   * security\_errors (list\[str\]): List of Checkov failure IDs.  
   * cost\_estimate (str): "$/month" string.  
   * ansible\_playbook (str): The YAML code.  
   * retry\_count (int): To stop infinite loops (default 0).  
2. **Initialize Graph (app/core/graph.py):**  
   * Import StateGraph from langgraph.  
   * Add Nodes (placeholders for now): architect, validator, security, finops, config.  
   * **Define Edges (The Logic):**  
     * architect \-\> validator  
     * validator \-\> (Condition: if error exists) \-\> architect  
     * validator \-\> (Condition: if clean) \-\> security  
     * security \-\> (Condition: if high risk) \-\> architect  
     * security \-\> (Condition: if clean) \-\> finops  
     * finops \-\> config  
     * config \-\> END

**✅ Definition of Done:** The Graph compiles without errors (even if functions are empty stubs).

---

## **👷 Step 1.3: The Architect Agent (LLM)**

**Context:** This is the prompt that generates the actual Terraform.

**Action Items:**

1. **Create app/core/agents/architect.py:**  
2. **The System Prompt:**  
   "You are a Senior Cloud Architect. Generate valid Terraform HCL code for AWS based on the user's request.  
   RULES:  
   * Output ONLY the code. No markdown fencing (\`\`\`).  
   * Use 'aws' provider.  
   * Use 't3.micro' for EC2 unless specified.  
   * If validation\_error is present in the state, fix the specific error mentioned: {state\['validation\_error'\]}."  
3. **The Code:**  
   * Use ChatOpenAI(model="gpt-4o", temperature=0).  
   * Input: state.  
   * Output: Update state\['terraform\_code'\] and increment state\['retry\_count'\].

**✅ Definition of Done:** You can run a script that sends "I need an EC2" and it prints valid HCL code to the console.

---

## **🛡️ Step 1.4: The Sandbox Tools (Subprocess)**

**Context:** The AI generates text. We need to save that text to a file and run real CLI tools against it.

**Action Items:**

1. **Create app/services/sandbox.py:**  
   * Create a helper run\_tool(directory, command) using subprocess.run.  
2. **Implement validate\_terraform(hcl\_code):**  
   * Create a temp directory (tempfile module).  
   * Write hcl\_code to main.tf.  
   * Run terraform init (Required to download providers\!).  
   * Run terraform validate \-json.  
   * **Return:** Exit code and stderr/stdout.  
3. **Implement run\_checkov(hcl\_code):**  
   * Run checkov \-f main.tf \--output json.  
   * Parse the JSON to find checks with check\_result\["result"\] \== "FAILED".  
   * **Return:** A list of failed Check IDs (e.g., \['CKV\_AWS\_21'\]).  
4. **Implement run\_infracost(directory):**  
   * Run infracost breakdown \--path . \--format json.  
   * Parse JSON to find projects\[0\].breakdown.totalMonthlyCost.

**✅ Definition of Done:**

* validate\_terraform returns "Success" for good code and "Error" for bad code.  
* run\_checkov returns a list of risks.

---

## **⚙️ Step 1.5: The Config Agent (Ansible)**

**Context:** The second LLM call to configure the server.

**Action Items:**

1. **Create app/core/agents/config.py:**  
2. **The System Prompt:**  
   "You are a DevOps Engineer. Read the following Terraform code:  
   {state\['terraform\_code'\]}  
   Generate an Ansible Playbook (playbook.yml) to configure these resources.  
   MANDATORY TASKS:  
   1. Install Docker and Nginx.  
   2. Setup a cron job to shut down the server at 20:00 (8 PM) daily to save costs.  
   3. Output ONLY valid YAML."  
3. **The Output:** Update state\['ansible\_playbook'\].

**✅ Definition of Done:** Sending Terraform code to this agent returns a YAML string containing a "cron" task.

---

## **📦 Step 1.6: The Bundler & API**

**Context:** Bringing it all together into a downloadable file.

**Action Items:**

1. **Create deploy.sh Template (app/templates/deploy.sh):**  
   * Paste the Bash script content defined in SPECS.md.  
2. **Implement app/services/bundler.py:**  
   * Function create\_deployment\_kit(hcl, playbook, cost):  
   * Create a BytesIO object (in-memory zip).  
   * Write main.tf, playbook.yml, README.md, and deploy.sh into the zip.  
   * Return the BytesIO object.  
3. **Implement API Endpoint (app/api/routes.py):**  
   * POST /generate:  
     * Input: PromptRequest.  
     * Action: graph.invoke(input).  
     * Output: Returns the state (JSON).  
   * POST /download:  
     * Input: PromptRequest (or ID).  
     * Action: Calls Bundler.  
     * Output: StreamingResponse(zip\_file, media\_type="application/zip").

**✅ Definition of Done:**

1. Start Docker container.  
2. Send POST request via Postman: {"prompt": "Simple EC2"}.  
3. Wait \~30 seconds.  
4. Receive JSON response.  
5. Send POST request to /download.  
6. You receive a valid .zip file on your machine.  
7. Unzipping it reveals main.tf, playbook.yml, and deploy.sh.

---

### **⚠️ Critical Implementation Notes for "My Engineer"**

1. **Terraform Init Latency:** terraform init takes time because it downloads AWS plugins. In app/services/sandbox.py, try to **cache** the .terraform folder if possible, or accept that validation might take 10-15 seconds.  
2. **LLM Temperature:** Set temperature=0 for the Architect Agent. We want deterministic code, not creative writing.  
3. **JSON Parsing:** LLMs are bad at outputting clean JSON sometimes. Use Pydantic's JsonOutputParser in LangChain to enforce structure, or simply ask for "Text Code" and save it directly to file.  
4. **Error Handling:** If retry\_count hits 3, stop the graph and return the error to the user. Don't let the AI spin in circles forever.

