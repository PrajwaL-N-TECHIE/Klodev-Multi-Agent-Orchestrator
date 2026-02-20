# 🚀 Klodev Enterprise Multi-Agent Sales Orchestrator

> **"From Intent to Action: The Secure, Multi-Agent Orchestration Platform."**

An autonomous, secure Multi-Agent System (MAS) designed to revolutionize enterprise sales outreach. This platform leverages specialized AI agents, Retrieval-Augmented Generation (RAG), and strict Human-in-the-Loop (HITL) cryptographic governance to classify user intent, identify high-value leads, and autonomously execute platform-specific communication workflows.

---

## 🧠 System Architecture

Instead of relying on a brittle, single-prompt LLM, this system utilizes a decentralized network of specialized AI agents that seamlessly pass context to one another:

* **Agent 1: The Classifier (Natural Language Processing)**
  Ingests raw, unstructured human prompts and extracts structured business context—including geographic location, urgency, and targeted roles (e.g., "urgent call to US-based VP of Engineering").
* **Agent 2: The ICP RAG Engine (Retrieval-Augmented Generation)**
  Acts as the data detective. It takes the parameters from Agent 1 and queries a localized SQLite vector-style database to mathematically match the Ideal Customer Profile (ICP). It evaluates lead scores, titles, and regional data to ensure zero AI hallucination and 100% accurate targeting.
* **Agent 3: The Routing Intelligence**
  Evaluates task priority and ICP communication preferences to autonomously decide the most effective outreach channel (LinkedIn, Email, or Voice Call).
* **Agent 4: The Content Generator**
  Dynamically crafts highly personalized, platform-optimized outreach. It seamlessly injects the specific lead's name, company, and pain points directly into the generated content, adjusting its tone based on the routed channel.

---

## 🛡️ Key Enterprise Features

* **Human-in-the-Loop (HITL) Governance Gate:** Enterprise AI requires safety. If Agent 3 routes a high-priority task to the **Call Channel**, the system triggers a secure, cryptographically logged UI barrier. Zero autonomous voice workflows are dispatched without explicit human authorization.
* **Role-Based Access Control (RBAC):** Gated by an admin-level Enterprise Encryption Key, ensuring only authorized personnel can access the agentic dashboard and authorize communications.
* **Asynchronous Telemetry:** Features a live "Agent Pulse" terminal that streams the AI's internal reasoning and decision-making logic directly to the DOM without requiring a page refresh.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask (Lightweight, RESTful architecture)
* **AI / LLM Core:** Google Gemini 2.5 API (High-speed JSON structuring and logic reasoning)
* **Database:** SQLite (Relational ground-truth data for the RAG pipeline)
* **Frontend:** Vanilla Asynchronous JavaScript, HTML5, CSS3 (Dynamic DOM manipulation and local storage management)

---

## 🎯 Use Case Example

**User Prompt:** > *"Make an urgent phone call to the VP of Engineering in the US region to pitch our AI scaling infrastructure."*

**Execution Flow:**
1. **Agent 1** extracts `Intent: Pitch`, `Role: VP Engineering`, `Location: US`, `Priority: High`.
2. **Agent 2** scans the database and retrieves *Sarah Chen from Google Cloud (USA) - Lead Score: 98*.
3. **Agent 3** identifies the "High" urgency and routes the task to the **Call** module.
4. **Agent 4** drafts the personalized call script addressing Sarah by name. 
5. The system halts, triggering the **HITL Sonar Ping**, awaiting admin approval before execution.

---

## 💻 Local Installation & Setup

Want to run this orchestration engine locally? Follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/PrajwaL-N-TECHIE/Klodev-Multi-Agent-Orchestrator.git](https://github.com/PrajwaL-N-TECHIE/Klodev-Multi-Agent-Orchestrator.git)
cd Klodev-Multi-Agent-Orchestrator
