# 🧠 Capstone Project: Multi-Agent System for Travel Health Insurance Operations

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

# MIT License. Feel free to reuse or extend this for educational or experimental purposes.
