This is a crucial document. In modern software engineering, **Design Systems** are just as important as the backend code. A "Senior" project doesn't just work; it feels premium, trustworthy, and intuitive.

Since you are targeting developers (DevOps engineers), the aesthetic should be **"Dark Mode, Technical, and Precision-Oriented."** Think *VS Code* meets *ChatGPT* meets *Cyberpunk*.

Save this file as DESIGN\_SYSTEM.md in your root directory.

---

# **🎨 InfraGenie: UI/UX Design System & Style Guide**

## **1\. Design Philosophy**

"The Cockpit Interface"

InfraGenie is a professional tool, not a toy. The interface should feel like a pilot's cockpit or an IDE (Integrated Development Environment).

* **Precision:** High information density but low clutter.  
* **Trust:** Use reassuring colors (Greens/Blues) for security, clear warnings (Yellow/Red) for costs.  
* **Feedback:** Every action has an immediate reaction. The user never guesses if the AI is working.

## **2\. Color Palette (Tailwind CSS)**

We will stick to standard Tailwind colors to speed up development, but specific shades are chosen for the "Dark Mode" aesthetic.

### **🌑 Backgrounds (The Canvas)**

* **App Background:** bg-zinc-950 (Almost black, softer than pure black).  
* **Panels/Cards:** bg-zinc-900 with a subtle border border-zinc-800.  
* **Input Fields:** bg-zinc-950 (Deepest depth).

### **⚡ Brand & Action (The Energy)**

* **Primary Brand:** Violet-600 (Represents AI/Intelligence).  
* **Accent/Action:** Cyan-400 (Represents Connectivity/Cloud).  
* **Gradient:** Use a subtle gradient from-violet-600 to-indigo-600 for primary buttons.

### **🚥 Semantic Colors (The Status)**

* **Success (Secure):** Emerald-500 (e.g., "0 Risks Found").  
* **Warning (Cost/Review):** Amber-400 (e.g., "Cost \> $50/mo").  
* **Error (Critical):** Rose-500 (e.g., "Port 22 Open").  
* **Loading:** Blue-400 (Pulse animations).

## **3\. Typography**

Developers prefer readability and familiarity.

* **Headings:** Inter or Geist Sans (Clean, modern, highly legible).  
  * *H1:* Bold, Tight Tracking.  
* **Body:** Inter or Geist Sans (Regular weight).  
* **Code/Terminal:** JetBrains Mono or Fira Code (Critical for the Terraform snippets).  
  * *Usage:* In the chat window for file names, IP addresses, and the code preview tab.

## **4\. UI Layout & Structure**

### **The "IDE" Layout (Dashboard)**

We strictly follow a 2-Column Split View (30/70 ratio).

**Left Panel: The Intelligence (Chat)**

* **Width:** 30% (min-width 350px).  
* **Behavior:** Scrollable chat history. Fixed input bar at the bottom.  
* **Visuals:** Glassmorphism effect (backdrop-blur-md) over the dark background.

**Right Panel: The Reality (Canvas)**

* **Width:** 70%.  
* **Tool:** ReactFlow Infinite Canvas.  
* **Overlay:** "Floating Badges" in the top-right corner for Cost & Security status.  
* **Background:** Dot pattern (bg-dot-pattern) to give it an engineering blueprint look.

## **5\. Component Patterns (ShadcnUI Customization)**

### **A. Buttons**

* **Primary:** Solid Violet, slight glow effect on hover.  
  * className="bg-violet-600 hover:bg-violet-700 shadow-\[0\_0\_15px\_rgba(124,58,237,0.5)\]"  
* **Secondary:** Outline Zinc.  
  * className="border border-zinc-700 hover:bg-zinc-800"

### **B. Cards (Nodes in Diagram)**

Instead of default boxes, our ReactFlow nodes will look like "Tech Cards".

* **Header:** Icon (e.g., AWS Logo) \+ Resource Name (aws\_instance).  
* **Body:** Key Details (Type: t3.micro, IP: 10.0.0.1).  
* **Status Indicator:** Small glowing dot (Green \= Validated).

### **C. The Loading State (The "Terminal" Effect)**

Do not use a simple spinning circle. It's boring.

Use: A "Terminal Log" simulation for the AI thinking process.

UX Flow:

User: "Build a server."

AI:

\> Architecting solution... \[OK\]

\> Validating Terraform syntax... \[OK\]

\> Scanning security (Checkov)... \[PATCHING\]

\> Estimating costs... \[DONE\]

*Why?* This hides the 30-second latency while showing the user exactly *why* it's taking time (Value demonstration).

## **6\. Micro-Interactions (Framer Motion)**

1. **Streaming Text:** The AI response should appear character-by-character (Typewriter effect).  
2. **Node Pop-in:** When the diagram generates, nodes should scale up from 0 to 1 with a spring animation.  
3. **Badge Updates:** If the cost changes, the number should "count up" quickly rather than just swapping.

## **7\. Accessibility (A11y)**

* **Contrast:** Ensure the Grey text on Black background passes WCAG AA standards (Use text-zinc-400 minimum for muted text).  
* **Keyboard:** The Chat Input must capture focus on load (autoFocus). The user should be able to submit with Enter.

---

## **8\. Implementation Guide (For Phase 2\)**

Step 1: Install Fonts

In app/layout.tsx:

TypeScript

import { Inter, JetBrains\_Mono } from 'next/font/google'

const inter \= Inter({ subsets: \['latin'\], variable: '--font-sans' })  
const mono \= JetBrains\_Mono({ subsets: \['latin'\], variable: '--font-mono' })

export default function RootLayout({ children }) {  
  return (  
    \<html lang="en" className="dark"\>  
      \<body className={\`${inter.variable} ${mono.variable} bg-zinc-950 text-zinc-50 font-sans antialiased\`}\>  
        {children}  
      \</body\>  
    \</html\>  
  )  
}

Step 2: Tailwind Config (tailwind.config.ts)

Extend your theme to lock in these colors:

TypeScript

theme: {  
  extend: {  
    colors: {  
      border: "hsl(var(--border))",  
      background: "\#09090b", // zinc-950  
      foreground: "\#fafafa", // zinc-50  
      primary: {  
        DEFAULT: "\#7c3aed", // violet-600  
        foreground: "\#ffffff",  
      },  
      destructive: {  
        DEFAULT: "\#f43f5e", // rose-500  
        foreground: "\#ffffff",  
      },  
    },  
    fontFamily: {  
      sans: \["var(--font-sans)"\],  
      mono: \["var(--font-mono)"\],  
    },  
  },  
}

Step 3: ReactFlow Node Styling

When building your custom node component:

TypeScript

// components/nodes/ServerNode.tsx  
\<div className="rounded-md border border-zinc-700 bg-zinc-900 p-4 shadow-xl min-w-\[200px\]"\>  
  \<div className="flex items-center gap-2 border-b border-zinc-800 pb-2 mb-2"\>  
    \<ServerIcon className="h-4 w-4 text-violet-500" /\>  
    \<span className="font-bold text-sm"\>EC2 Instance\</span\>  
  \</div\>  
  \<div className="text-xs font-mono text-zinc-400"\>  
    type: t3.micro\<br/\>  
    ami: ubuntu-22.04  
  \</div\>  
\</div\>

---

### **💡 Why this Design System works for YOU**

1. **It hides complexity:** The "Terminal Log" loader turns a slow backend into a cool feature.  
2. **It feels "Senior":** Junior devs use default Bootstrap/Material UI. Senior devs build bespoke, branded experiences using Tailwind.  
3. **It's Dark Mode:** Developers live in dark mode. You are building for your own tribe.

