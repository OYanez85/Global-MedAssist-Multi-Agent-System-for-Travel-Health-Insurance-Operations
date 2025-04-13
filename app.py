# app.py

from pathlib import Path
from pydub import AudioSegment
from google.cloud import texttospeech
from google.oauth2 import service_account
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import gradio as gr
import os, random, datetime, json

# ----------------------------
# Patients
# ----------------------------
def get_patient_by_name(name):
    patients = {
        "anne": {"name": "Anne", "location": "Nice, France", "symptoms": "severe leg pain", "urgency": "emergency", "lang": "fr"},
        "liam": {"name": "Liam", "location": "Da Nang, Vietnam", "symptoms": "fever and dizziness", "urgency": "outpatient", "lang": "en"},
        "priya": {"name": "Priya", "location": "Doha Airport, Qatar", "symptoms": "abdominal pain", "urgency": "emergency", "lang": "en"}
    }
    return patients.get(name.lower())

# ----------------------------
# Emotion presets
# ----------------------------
agent_emotions = {
    "ClientAgent": "stress",
    "ClientInteractionAgent": "calm",
    "TriageMedicalAssessmentAgent": "urgent",
    "ProviderNetworkAgent": "neutral",
    "PolicyValidationAgent": "neutral",
    "MedicalDocumentationAgent": "calm",
    "RepatriationPlannerAgent": "calm",
    "MedicalDecisionAgent": "calm",
    "ComplianceConsentAgent": "neutral",
    "OrchestratorAgent": "calm"
}

# ----------------------------
# Environment setup
# ----------------------------
audio_dir = Path("tts_audio"); audio_dir.mkdir(exist_ok=True, parents=True)
log_file = Path("case_log.txt")
zip_output = Path("case_export.zip")
ambient_map = {"hospital": "ambient_hospital.mp3", "airport": "ambient_airport.mp3"}

# Load Google credentials from Hugging Face secret
gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not gcp_creds:
    raise RuntimeError("❌ GOOGLE_APPLICATION_CREDENTIALS_JSON secret not found. Add it in HF Space Settings.")

creds_dict = json.loads(gcp_creds)
credentials = service_account.Credentials.from_service_account_info(creds_dict)
tts_client = texttospeech.TextToSpeechClient(credentials=credentials)

# ----------------------------
# TTS Synthesis
# ----------------------------
def synthesize_speech(text, agent, emotion, context, lang="en"):
    pitch = {"calm": "+2st", "stress": "-2st", "urgent": "+0st"}.get(emotion, "+0st")
    rate = {"calm": "medium", "stress": "slow", "urgent": "fast"}.get(emotion, "medium")
    ssml = f"""<speak><prosody rate='{rate}' pitch='{pitch}'>{text}</prosody></speak>"""

    voice_code = "fr-FR-Wavenet-A" if lang == "fr" else "en-GB-Wavenet-A"
    input_text = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(language_code=voice_code, name=voice_code)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)

    mp3_path = audio_dir / f"{agent}_{random.randint(1000, 9999)}.mp3"
    with open(mp3_path, "wb") as out: out.write(response.audio_content)

    ambient_file = ambient_map.get(context)
    if ambient_file and Path(ambient_file).exists():
        voice = AudioSegment.from_file(mp3_path)
        ambient = AudioSegment.from_file(ambient_file).apply_gain(-12)
        mix = ambient.overlay(voice)
        mix.export(mp3_path, format="mp3")

    return str(mp3_path)

# ----------------------------
# RAG Setup
# ----------------------------
Path("rag_docs").mkdir(exist_ok=True, parents=True)
Path("rag_docs/hospital_data.txt").write_text("Hospital Pasteur is a Level 1 trauma center in Nice, France. ICU facilities included.")
Path("rag_docs/policy_terms.txt").write_text("Standard policy covers emergencies with repatriation and escort.")

def create_rag_chain(file):
    loader = TextLoader(file)
    docs = loader.load()
    chunks = CharacterTextSplitter(chunk_size=300, chunk_overlap=50).split_documents(docs)
    vector = FAISS.from_documents(chunks, OpenAIEmbeddings())
    return RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0), retriever=vector.as_retriever())

rag_hospital = create_rag_chain("rag_docs/hospital_data.txt")
rag_policy = create_rag_chain("rag_docs/policy_terms.txt")

# ----------------------------
# LangGraph Flow
# ----------------------------
def agent_node(agent_name):
    def run(state):
        emotion = agent_emotions.get(agent_name, "neutral")
        context = "hospital" if "Hospital" in agent_name else "airport" if "Repatriation" in agent_name else "none"
        msg = state["script"].get(agent_name, f"{agent_name} is processing...")
        if agent_name == "ProviderNetworkAgent":
            msg = rag_hospital.run("What care level does Hospital Pasteur provide?")
        elif agent_name == "PolicyValidationAgent":
            msg = rag_policy.run("Is repatriation with escort covered?")
        audio = synthesize_speech(msg, agent=agent_name, emotion=emotion, context=context, lang=state["patient"]["lang"])
        state["log"].append(f"{agent_name}: {msg}")
        state["audio"].append(audio)
        return state
    return run

def build_workflow():
    graph = StateGraph()
    nodes = [
        "ClientAgent", "ClientInteractionAgent", "TriageMedicalAssessmentAgent",
        "ProviderNetworkAgent", "PolicyValidationAgent", "MedicalDocumentationAgent",
        "RepatriationPlannerAgent", "MedicalDecisionAgent", "ComplianceConsentAgent", "OrchestratorAgent"
    ]
    for node in nodes: graph.add_node(node, agent_node(node))
    for i in range(len(nodes) - 1): graph.set_edge(nodes[i], nodes[i + 1])
    graph.set_entry_point("ClientAgent")
    graph.set_finish_point("OrchestratorAgent")
    return graph.compile()

# ----------------------------
# Generate PDF
# ----------------------------
def generate_pdf_from_log(log_lines, pdf_path):
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter; y = height - 60
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 40, f"Conversation Log – {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for line in log_lines:
        if y < 40: c.showPage(); c.setFont("Helvetica", 10); y = height - 40
        c.drawString(30, y, line); y -= 14
    c.save()

# ----------------------------
# Simulation
# ----------------------------
def run_simulation_ui(patient_name):
    patient = get_patient_by_name(patient_name)
    if not patient: return "❌ Patient not found.", None, None
    if log_file.exists(): log_file.unlink()
    for f in audio_dir.glob("*.mp3"): f.unlink()

    script = {
        "ClientAgent": f"📞 Hello? I had a fall in {patient['location']}. It hurts badly!",
        "ClientInteractionAgent": f"Hello {patient['name']}, you're in {patient['location']} with '{patient['symptoms']}'. This is {patient['urgency']}.",
        "TriageMedicalAssessmentAgent": "Ambulance arranged. Requesting medical report.",
        "MedicalDocumentationAgent": f"Requesting Fit-to-Fly certificate for {patient['name']}.",
        "RepatriationPlannerAgent": "Planning business class flight with nurse escort.",
        "MedicalDecisionAgent": "✅ Case cleared.",
        "ComplianceConsentAgent": f"🔐 {patient['name']} consented to share medical data.",
        "OrchestratorAgent": "Case complete. Logs saved and KPIs triggered."
    }

    state = build_workflow().invoke({"patient": patient, "script": script, "log": [], "audio": []})
    pdf_path = audio_dir / f"{patient_name}_conversation.pdf"
    generate_pdf_from_log(state["log"], pdf_path)

    full_audio = audio_dir / f"{patient_name}_full_convo.mp3"
    combined = AudioSegment.empty()
    for a in state["audio"]: combined += AudioSegment.from_file(a)
    combined.export(full_audio, format="mp3")

    with zip_output.open("wb") as f:
        from zipfile import ZipFile
        with ZipFile(f, "w") as zipf:
            for a in state["audio"]: zipf.write(a, arcname=os.path.basename(a))
            zipf.write(log_file, arcname=log_file.name)
            zipf.write(pdf_path, arcname=pdf_path.name)
            zipf.write(full_audio, arcname=full_audio.name)

    return "\n".join(state["log"]), str(zip_output), str(full_audio)

# ----------------------------
# Gradio UI
# ----------------------------
def launch_ui():
    gr.Interface(
        fn=run_simulation_ui,
        inputs=gr.Dropdown(choices=["Anne", "Liam", "Priya"], label="Select Patient"),
        outputs=[
            gr.Textbox(label="Conversation Log"),
            gr.File(label="Download ZIP (Log + MP3 + PDF)"),
            gr.Audio(label="Stream Full Conversation", type="filepath", show_download_button=True)
        ],
        title="🧠 Global MedAssist – AI Agent Simulation",
        description="Multi-agent healthcare scenario with PDF + MP3 export, emotional TTS, and RAG."
    ).launch(share=True)

# Launch
launch_ui()
