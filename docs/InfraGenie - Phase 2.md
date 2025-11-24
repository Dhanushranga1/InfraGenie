This is the **Detailed Engineering Execution Plan for Phase 2**.

This document is written for the **Frontend Engineer** (You). It focuses on transforming the API capabilities built in Phase 1 into a polished, interactive web application.

**Goal:** Build a Next.js application where users can chat with the AI, see their infrastructure visualized in real-time, and download their deployment kit.

---

## **🎨 Step 2.1: The Frontend Skeleton**

**Context:** We need a modern, type-safe environment. We will use **Next.js 14 (App Router)** for performance and **ShadcnUI** for rapid, accessible component design.

**Action Items:**

1. **Initialize Project:**  
2. Bash

npx create-next-app@latest frontend \--typescript \--tailwind \--eslint  
\# Select "Yes" for App Router and "No" for src/ directory (optional, but standard)

3.   
4.   
5. **Install Core Dependencies:**  
6. Bash

npm install axios @tanstack/react-query clsx tailwind-merge lucide-react  
npm install reactflow

7.   
8.   
9. **Install UI Components (Shadcn):**  
10. Bash

npx shadcn-ui@latest init  
npx shadcn-ui@latest add button card input scroll-area badge separator toast

11.   
12.   
13. **Layout Architecture:**  
    * Create app/layout.tsx: Add a globally persistent Navbar (Logo \+ User Profile).  
    * Create app/page.tsx: The main dashboard view (we are building a Single Page App feel).  
    * Define a **2-Column Layout**:  
      * **Left Panel (30%):** Chat Interface.  
      * **Right Panel (70%):** Visualization Canvas (ReactFlow).

**✅ Definition of Done:** You can run npm run dev, see a split-screen layout with a "Chat" area and a "Canvas" area, and the UI is responsive.

---

## **💬 Step 2.2: The Chat Interface & API Integration**

**Context:** The frontend needs to talk to the Dockerized backend. Since the backend generation takes time (30-60s), we need to handle "Loading" states gracefully.

**Action Items:**

1. **API Client (lib/api.ts):**  
   * Create an Axios instance with baseURL: http://localhost:8000/api/v1.  
   * Add an interceptor to inject the Auth Token (from Clerk) later.  
2. **Chat State Management:**  
   * Use useState for the messages array: \[{ role: 'user', text: '...' }, { role: 'ai', text: '...' }\].  
   * Use useMutation (React Query) for the /generate POST request.  
3. **The Interaction Loop:**  
   * **User Input:** User types \-\> Click Send \-\> Add User Message to state.  
   * **Loading:** Show a "Thinking..." bubble or skeleton loader.  
   * **API Call:** Send prompt to Backend.  
   * **Response:** Receive the JSON payload (Terraform code, Cost, Security).  
   * **Update:** Add "Generation Complete" message to chat and update the **Global Context** with the infrastructure data.

**✅ Definition of Done:** You can type "EC2 server" in the UI, wait 30 seconds, and see a console.log containing the JSON response from your FastAPI container.

---

## **🕸️ Step 2.3: The Visualizer (ReactFlow Implementation)**

**Context:** This is the "Wow" factor. We need to translate raw Terraform JSON into a visual graph.

**Action Items:**

1. **The Parser Utility (lib/parsers/terraformToGraph.ts):**  
   * *Input:* The terraform\_json from the backend.  
   * *Logic:* Iterate through resource\_changes or planned\_values.  
   * **Node Logic:**  
     * If type is aws\_instance, create a Node with a custom "Server Icon".  
     * If type is aws\_s3\_bucket, create a Node with a "Bucket Icon".  
   * **Edge Logic:**  
     * If a resource references another (e.g., vpc\_id \= aws\_vpc.main.id), create an Edge between them.  
   * *Output:* { nodes: \[...\], edges: \[...\] } compatible with ReactFlow.  
2. **The Canvas Component (components/ArchitectureDiagram.tsx):**  
   * Import ReactFlow, Background, Controls.  
   * Use the useNodesState and useEdgesState hooks.  
   * Use dagre (graph layout library) to automatically arrange nodes so they don't overlap.  
3. **Custom Nodes:**  
   * Create a custom React component for nodes that shows the **Resource Name** and a specific **Icon** (use lucide-react icons for servers, databases, etc.).

**✅ Definition of Done:** When the API response comes back, the right panel automatically populates with boxes connected by lines representing the requested infrastructure.

---

## **🛡️ Step 2.4: Dashboard Intelligence (Badges & Download)**

**Context:** We need to display the "Meta-Data" (Cost and Security) returned by the agents.

**Action Items:**

1. **Cost Badge Component:**  
   * Read agent\_state.cost\_estimate (e.g., "$24.50").  
   * Render a Card: "Estimated Monthly Cost".  
   * *Logic:* If cost \> $100, make the text **Red** (Warning). If \< $50, make it **Green**.  
2. **Security Badge Component:**  
   * Read agent\_state.security\_risks.  
   * *Logic:*  
     * 0 Risks: Display "Shield Secure" (Green).  
     * 0 Risks: Display "Vulnerabilities patched" (Yellow).  
3. **The Download Button:**  
   * Create a prominent button: **"Download Deployment Kit"**.  
   * **On Click:** Trigger window.open('http://localhost:8000/api/v1/download/{session\_id}').  
   * Ensure the browser handles the .zip download correctly.

**✅ Definition of Done:** After generation, the user sees the price tag, the security status, and successfully downloads the zip file by clicking the button.

---

## **🔐 Step 2.5: Authentication (Clerk)**

**Context:** Protect the app so only verified users can generate expensive API calls.

**Action Items:**

1. **Clerk Setup:**  
   * Create a Clerk account and a new application.  
   * Copy NEXT\_PUBLIC\_CLERK\_PUBLISHABLE\_KEY and CLERK\_SECRET\_KEY to .env.local.  
2. **Middleware:**  
   * Create middleware.ts in the root.  
   * Use authMiddleware to protect the dashboard route (/). Redirect unauthenticated users to the Clerk Sign-In page.  
3. **Frontend Auth:**  
   * Wrap your app in \<ClerkProvider\>.  
   * Add the \<UserButton /\> to your Navbar.  
4. **Backend Connection (Crucial):**  
   * Update your Axios client to await getToken() from Clerk.  
   * Send this token in the Authorization: Bearer header to FastAPI.  
   * *Note:* For MVP, if passing the token to FastAPI is too complex to debug locally, you can skip the *backend validation* of the token, but keep the *frontend gate* to simulate a real SaaS.

**✅ Definition of Done:** You cannot access the dashboard without signing in via GitHub. The User Profile picture appears in the top right.

---

### **⚠️ Critical Implementation Notes for "My Engineer"**

1. **CORS Errors:** You will likely hit Cross-Origin Resource Sharing errors because Frontend is port 3000 and Backend is port 8000\.  
   * **Fix:** In FastAPI main.py, add CORSMiddleware allowing http://localhost:3000.  
2. **ReactFlow Layout:** By default, ReactFlow nodes spawn at x:0, y:0 (on top of each other).  
   * **Fix:** You **must** install dagre. Use it to calculate x/y coordinates for the nodes *before* passing them to ReactFlow. This is the standard way to auto-layout graphs.  
3. **Streaming Text:** If setting up a WebSocket or Server-Sent Events (SSE) for streaming text is too hard for Phase 2, **don't do it**.  
   * **Fallback:** Use a "Spinner" that says "Agents are working... (Architecting \-\> Validating \-\> Securing)". This is often *better* UX than watching raw text scroll by.

### **🚀 Final Outcome of Phase 2**

You will have a fully functional web application. A user can log in, ask for a "Secure Redis Cluster," watch the diagram appear, check the price, and download the code. This is the "MVP Complete" milestone.

