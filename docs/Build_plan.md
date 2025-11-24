Here is the comprehensive **BUILD\_PLAN.md**.

This document breaks the project into **3 Logical Phases**. Since you are working solo with flexible hours, treat each checkbox as a "Session Goal." Do not move to Phase 2 until Phase 1 is 100% complete—this is how you avoid the "half-finished project" trap.

---

# **🚧 InfraGenie: Phase-Wise Implementation Plan**

## **Phase 1: The Engine (Backend & AI Core)**

**Objective:** Build a working API that takes a text prompt and returns a validated .zip file. No UI yet—strictly Postman/cURL testing.

### **1.1 Foundation & Tools**

* \[ \] **Docker Environment:** Create backend/Dockerfile.  
  * Base image: python:3.11-slim.  
  * **Critical:** Install terraform, ansible, checkov, and infracost binaries within this Dockerfile.  
* \[ \] **Project Skeleton:** Initialize FastAPI (main.py) and standard folders (app/core, app/api).  
* \[ \] **Tool Verification:** Create a test endpoint GET /health that runs terraform \--version and checkov \-v via Python subprocess. Ensure they execute without errors.

### **1.2 The LangChain/LangGraph Brain**

* \[ \] **State Schema:** Define the AgentState TypedDict (User Prompt, HCL Code, Errors, Cost, etc.) in app/core/state.py.  
* \[ \] **Architect Agent:** Build the LLMChain using gpt-4o. Write the system prompt to output pure Terraform HCL.  
* \[ \] **Validator Node:** Implement the Python function that runs terraform validate.  
  * *Logic:* If exit code \!= 0, capture stderr and loop back to Architect Agent.  
* \[ \] **Security Node:** Implement the Python wrapper for checkov.  
  * *Logic:* Parse JSON output. If failed\_checks \> 0, feed the specific check IDs back to the LLM for patching.  
* \[ \] **Graph Orchestration:** Wire these nodes together in app/core/graph.py using StateGraph.

### **1.3 FinOps & Config Agents**

* \[ \] **FinOps Node:** Implement the wrapper for infracost breakdown \--path . \--format json. Extract the totalMonthlyCost string.  
* \[ \] **Config Agent:** Create the prompt that reads the finalized main.tf and generates a corresponding playbook.yml (Ansible).  
  * *Task:* Ensure it injects the "Cost Assassin" cron job logic.

### **1.4 Artifact Generation**

* \[ \] **The Bundler:** Write a service app/services/bundler.py that takes the strings (HCL, YAML) and writes them to a temporary directory.  
* \[ \] **The Script:** Auto-generate the deploy.sh file (hardcoded text) into that directory.  
* \[ \] **Zip Endpoint:** Create POST /api/v1/download that zips the directory and returns it as a binary stream.

---

## **Phase 2: The Experience (Frontend & Visualization)**

**Objective:** Connect the powerful backend to a user-friendly "Chat & Visualize" interface.

### **2.1 Interface Skeleton**

* \[ \] **Next.js Init:** Initialize project with TypeScript, Tailwind CSS, and ShadcnUI.  
* \[ \] **API Client:** Set up axios or fetch with a base URL pointing to your FastAPI container.  
* \[ \] **Chat Component:** Build a UI that accepts text input and displays a "Thinking..." state (Streaming text support is optional for MVP, loading spinners are fine).

### **2.2 Visualization (ReactFlow)**

* \[ \] **The Parser:** Write a TypeScript utility that takes terraform plan \-json output (from backend) and converts it into ReactFlow Nodes (Resources) and Edges (Dependencies).  
* \[ \] **Canvas:** Render the ReactFlow component on the main dashboard.  
* \[ \] **Test:** Ensure an aws\_instance shows up as a box and a security\_group connects to it.

### **2.3 Dashboard Intelligence**

* \[ \] **Status Badges:** Create UI components for:  
  * 🛡️ **Security:** Green/Red shield icon based on Checkov results.  
  * 💰 **Cost:** Dollar amount badge based on Infracost.  
* \[ \] **Auth Integration:** Set up Clerk.com for GitHub Authentication. Protect the main route so only logged-in users can generate infrastructure.

---

## **Phase 3: The Polish & Delivery (Resume Readiness)**

**Objective:** Make the project look professional, portable, and understandable for recruiters.

### **3.1 The "Magic Script" Refinement**

* \[ \] **Testing:** Manually run the downloaded deploy.sh on your own AWS account.  
  * Does it actually provision EC2?  
  * Does Ansible actually install Docker?  
  * **Fix:** Debug and refine the script until it works 100% of the time.

### **3.2 Documentation**

* \[ \] **README:** Write a professional README with:  
  * High-level architecture diagram.  
  * "How to Run" (Docker Compose commands).  
  * Demo GIF.  
* \[ \] **Architecture Decision Records (ADRs):** Ensure your docs/decisions/ folder is populated (as discussed).

### **3.3 Media**

* \[ \] **Demo Video:** Record a clean run-through (Loom/OBS).  
  * *Scenario:* "I need a dev server." \-\> Generate \-\> Check Cost \-\> Download \-\> Show the code.  
* \[ \] **Cleanup:** Remove any API keys from code (use .env files) and finalize the repo.

