---
title: Global MedAssist
emoji: 🧠
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.25.0
app_file: app.py
pinned: false
---

# 🧠 Capstone Project: Multi-Agent System for Travel Health Insurance Operations
<<<<<<< HEAD
...

# 🧠 Capstone Project: Multi-Agent System for Travel Health Insurance Operations
=======
>>>>>>> e407f9fa7269228f99f19aa85a3e2283b51b3e6f

Welcome to the repository for my AI-powered Capstone Project built using **Gemini models**, **LangChain/CrewAI**, and enhanced with insights from **Google Cloud’s Generative AI Whitepapers** and **Kaggle multi-agent competition frameworks**.

## 🚀 Project Overview

This capstone simulates a real-world **Travel Health Insurance Operations Agent**, capable of:

- Responding to medical incidents globally
- Coordinating emergency & outpatient care
- Validating policy coverage
- Planning complex repatriation flows (wheelchair assistance, air ambulances, escort nurses/doctors)
- Ensuring GDPR-compliant client consent

All via a **multi-agent conversational architecture** replacing human operations staff.

---

## 🧩 Agents in the System

| Agent                    | Responsibility |
|-------------------------|----------------|
| 🤝 `ClientInteractionAgent` | Collects symptoms, location, urgency level |
| 🏥 `TriageMedicalAssessmentAgent` | Assesses urgency, requests PMH & medical reports |
| 🌐 `ProviderNetworkAgent` | Finds in-network hospitals, assesses safety, plans evacuations |
| 📄 `MedicalDocumentationAgent` | Manages Fit-to-Fly, medical docs, hospital reports |
| 🛡️ `PolicyValidationAgent` | Checks exclusions, coverage dates, benefits |
| ✈️ `RepatriationPlannerAgent` | Creates travel assistance plans (wheelchair type, escort level, etc.) |
| 🧠 `MedicalDecisionAgent` | Simulates doctor decision, validates repatriation plan |
| 📋 `ComplianceConsentAgent` | Ensures GDPR compliance and client consent |
| 🧭 `OrchestratorAgent` | Controls end-to-end agent coordination |

---

## 🧠 Technical Stack

- **LLM**: Google Gemini (via Vertex AI or Kaggle endpoints)
- **Framework**: LangChain / CrewAI + LangGraph
- **Memory**: ConversationBufferMemory across agents
- **Tools Simulated**: Hospital lookup, policy checker, PDF report generator
- **UI**: Streamlit App
- **RAG**: VectorDB for policy & hospital retrieval
- **Evaluation**: Agent scoring (completeness, accuracy, empathy)

---

## 📁 Folder Structure
📦 travel-health-insurance-capstone/ ├── 📓 Capstone_Notebook.ipynb ← Full Kaggle-compatible notebook ├── 📄 Capstone_Report.pdf ← Generated PDF report (simulated) ├── 🖼️ screenshots/ ← UI & demo captures ├── 📝 README.md ← You're here └── app/ └── 🖥️ streamlit_app.py ← Optional Streamlit demo app


---

## 🧪 Sample Simulation Scenarios

- 🧓 Elderly woman with knee fracture in France → wheelchair + nurse escort
- 🌴 Teen with dengue in rural Vietnam → inpatient + evacuation
- 🛬 Elderly man with cardiac history collapses in Dubai airport → air ambulance + oxygen support
- 🕵️‍♀️ Traveler assaulted in South Africa → medical + legal + embassy support

---

## 📚 References

- [📘 Prompt Engineering Guide](https://developers.google.com/machine-learning/prompt-engineering)
- [🧾 Domain-Specific LLMs PDF](#)
- [🔗 Agents Companion PDF](#)
- [🤖 Vertex AI Operationalizing GenAI](#)
- [📍 LangChain & LangGraph Docs](https://docs.langchain.com/)
- [🌐 Kaggle Gemini Competition](https://www.kaggle.com/competitions/multimodal-multi-agent/overview)

---

## 📚 Reference Material

This project is built upon the concepts, agent patterns, and code examples from the **5-Day Generative AI Intensive by Google DeepMind & Kaggle**.

You can find all related notebooks (Units 1–6) and whitepapers (Prompt Engineering, AgentOps, RAG, LangChain, Vertex AI) in this public GitHub repository:

🔗 [5-Day_Gen_AI_Intensive_by_Kaggle_and_Google_Deep_Mind_2025](https://github.com/OYanez85/5-Day_Gen_AI_Intensive_by_Kaggle_and_Goggle_Deep_Mind_2025)

---

## 🧪 Sample Simulation Scenarios

- 🧓 Elderly woman with knee fracture in France → wheelchair + nurse escort
- 🌴 Teen with dengue in rural Vietnam → inpatient + evacuation
- 🛬 Elderly man with cardiac history collapses in Dubai airport → air ambulance + oxygen support
- 🕵️‍♀️ Traveler assaulted in South Africa → medical + legal + embassy support

---

## 💬 Try It Now

- 🔗 [**Launch on Kaggle**](#)
- 🌐 Or [Run the Streamlit App](#) locally via:

```bash
cd app
streamlit run streamlit_app.py
´´´ 
# 👋 Author

Oscar Yáñez-Feijóo
Data Scientist | Python Developer | Healthcare AI Enthusiast
📧 Email • 🐦 Twitter • 🌍 LinkedIn
📝 License

<<<<<<< HEAD
# MIT License. Feel free to reuse or extend this for educational or experimental purposes.
=======
# MIT License. Feel free to reuse or extend this for educational or experimental purposes.
>>>>>>> e407f9fa7269228f99f19aa85a3e2283b51b3e6f
