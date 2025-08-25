# app.py

import os
import io
import random
import json
import datetime
from pathlib import Path
from zipfile import ZipFile

import gradio as gr
from pydub import AudioSegment
from gtts import gTTS
from google.cloud import texttospeech
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ✅ NEW LangChain imports (post-2024 split)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA

from langgraph.graph import StateGraph
from typing import TypedDict, List

# ----------------------------------------
# 🔐 OpenAI API key
# ----------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ----------------------------------------
# 🔐 Google TTS credentials (Space secret: GOOGLE_CLOUD_TTS_JSON)
# ----------------------------------------
def init_google_tts_client():
    try:
        sa_json = os.getenv("GOOGLE_CLOUD_TTS_JSON")
        if sa_json:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=".json")
            with os.fdopen(fd, "w") as f:
                f.write(sa_json)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
        return texttospeech.TextToSpeechClient()
    except Exception:
        return None

tts_client = init_google_tts_client()

# ----------------------------------------
# 👥 Patients
# ----------------------------------------
def get_patient_by_name(name):
    patients = {
        "anne": {"name": "Anne",   "location": "Nice, France",    "symptoms": "severe leg pain after a fall", "urgency": "emergency"},
        "liam": {"name": "Liam",   "location": "Da Nang, Vietnam", "symptoms": "high fever and dizziness",     "urgency": "outpatient"},
        "priya": {"name": "Priya", "location": "Doha Airport, Qatar", "symptoms": "abdominal pain",           "urgency": "emergency"},
    }
    return patients.get(name.lower())

# ----------------------------------------
# 🎭 Emotion presets
# ----------------------------------------
agent_emotions = {
    "ClientAgent": "stress", "ClientAgent_2": "stress", "ClientAgent_3": "concerned", "ClientAgent_4": "curious",
    "ClientAgent_5": "in_pain", "ClientAgent_6": "grateful", "ClientInteractionAgent": "calm",
    "TriageMedicalAssessmentAgent": "urgent", "ProviderNetworkAgent": "neutral",
    "PolicyValidationAgent": "neutral", "MedicalDocumentationAgent": "calm",
    "RepatriationPlannerAgent": "calm", "MedicalDecisionAgent": "calm",
    "ComplianceConsentAgent": "neutral", "CountryCareLevelAgent": "neutral",
    "OrchestratorAgent": "calm",
}

audio_dir = Path("tts_audio"); audio_dir.mkdir(exist_ok=True)
log_file = Path("case_log.txt")
zip_output = Path("case_export.zip")

# Optional ringtone
ringtone_path = Path("sounds/ringtone.mp3")
ringtone = AudioSegment.from_file(ringtone_path)[:5000] if ringtone_path.exists() else AudioSegment.silent(duration=5000)

client_voices = {"liam": "en-GB-Standard-A", "anne": "en-GB-Wavenet-F", "priya": "en-GB-Wavenet-F"}
agent_voice = "en-GB-Wavenet-D"

# ----------------------------------------
# 🔈 TTS
# ----------------------------------------
def synthesize_speech(text, agent, emotion="neutral", context="none"):
    pitch = "+2st" if emotion == "calm" else ("+0st" if emotion == "urgent" else "-2st")
    rate = "slow" if emotion == "stress" else ("fast" if emotion == "urgent" else "medium")
    has_ringtone = "📞" in text
    clean_text = text.replace("📞", "").strip()
    is_client = agent.startswith("ClientAgent")

    # pick voice
    voice_name = agent_voice if not is_client else client_voices.get(
        next((n for n in client_voices if n in clean_text.lower()), "liam"),
        "en-GB-Standard-A",
    )
    mp3_path = audio_dir / f"{agent}_{random.randint(1000,9999)}.mp3"

try:
    if tts_client:  # Google Cloud TTS
        safe_text = escape(clean_text)  # escape &, <, >, " for SSML/XML
        ssml = f'<speak><prosody rate="{rate}" pitch="{pitch}">{safe_text}</prosody></speak>'
        input_text = texttospeech.SynthesisInput(ssml=ssml)
        voice = texttospeech.VoiceSelectionParams(language_code="en-GB", name=voice_name)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = tts_client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        voice_audio = AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")
    else:  # gTTS fallback (requires internet)
        tts = gTTS(text=clean_text, lang="en", slow=False)
        temp = audio_dir / f"temp_{agent}.mp3"
        tts.save(temp)
        voice_audio = AudioSegment.from_file(temp)
        try:
            temp.unlink(missing_ok=True)  # ok on Python 3.8+
        except TypeError:
            # for older runtimes without missing_ok
            if temp.exists():
                temp.unlink()

    pause = AudioSegment.silent(duration=700)
    final_audio = (ringtone + pause + voice_audio) if has_ringtone else voice_audio
    final_audio.export(mp3_path, format="mp3")
    return str(mp3_path)

except Exception as e:
    # Last-resort 1s silence (still produce a file to avoid Gradio error)
    AudioSegment.silent(duration=1000).export(mp3_path, format="mp3")
    return str(mp3_path)

# ----------------------------------------
# 🧠 Mock RAG
# ----------------------------------------
def create_rag_chain(file):
    loader = TextLoader(file)
    docs = loader.load()
    chunks = CharacterTextSplitter(chunk_size=300, chunk_overlap=50).split_documents(docs)
    vector = FAISS.from_documents(chunks, OpenAIEmbeddings())
    return RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0), retriever=vector.as_retriever())

Path("rag_docs").mkdir(exist_ok=True)
Path("rag_docs/hospital_data.txt").write_text(
    "Hospital Pasteur is a Level 1 trauma center in Nice, France. It includes ICU facilities and is in-network."
)
Path("rag_docs/policy_terms.txt").write_text(
    "Standard policy covers outpatient and emergency treatment, includes repatriation with escort in emergencies."
)

# ----------------------------------------
# 🔗 LangGraph
# ----------------------------------------
class AgentState(TypedDict):
    patient: dict
    script: dict
    log: List[str]
    audio: List[str]

def agent_node(agent_name):
    def run(state: AgentState) -> AgentState:
        emotion = agent_emotions.get(agent_name, "neutral")
        context = "hospital" if "Hospital" in agent_name else "airport" if "Repatriation" in agent_name else "none"
        msg = state["script"].get(agent_name, f"{agent_name} is processing...")

        if agent_name == "ProviderNetworkAgent" and rag_hospital:
            try:
                msg = rag_hospital.run("What care level does Hospital Pasteur provide?")
            except Exception:
                pass
        if agent_name == "PolicyValidationAgent" and rag_policy:
            try:
                msg = rag_policy.run("Is repatriation with escort covered?")
            except Exception:
                pass

        state["log"].append(f"{agent_name}: {msg}")
        state["audio"].append(synthesize_speech(msg, agent_name, emotion, context))
        return state
    return run

def build_workflow():
    graph = StateGraph(AgentState)
    for node in agent_emotions:
        graph.add_node(node, agent_node(node))
    edges = [
        ("ClientAgent", "ClientInteractionAgent"),("ClientInteractionAgent","TriageMedicalAssessmentAgent"),
        ("TriageMedicalAssessmentAgent","ClientAgent_2"),("ClientAgent_2","ProviderNetworkAgent"),
        ("ProviderNetworkAgent","ClientAgent_3"),("ClientAgent_3","MedicalDocumentationAgent"),
        ("MedicalDocumentationAgent","ClientAgent_4"),("ClientAgent_4","PolicyValidationAgent"),
        ("PolicyValidationAgent","MedicalDecisionAgent"),("MedicalDecisionAgent","ClientAgent_5"),
        ("ClientAgent_5","RepatriationPlannerAgent"),("RepatriationPlannerAgent","ComplianceConsentAgent"),
        ("ComplianceConsentAgent","ClientAgent_6"),("ClientAgent_6","CountryCareLevelAgent"),
        ("CountryCareLevelAgent","OrchestratorAgent")
    ]
    for a, b in edges:
        graph.add_edge(a, b)
    graph.set_entry_point("ClientAgent")
    graph.set_finish_point("OrchestratorAgent")
    return graph.compile()

# ----------------------------------------
# 🧩 Helpers: audio concat & PDF
# ----------------------------------------
def concatenate_audio(audio_paths, output_path):
    combined = AudioSegment.empty()
    for p in audio_paths:
        combined += AudioSegment.from_file(p)
    combined.export(output_path, format="mp3")
    return output_path

def generate_pdf_from_log(log_lines, pdf_path):
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 10)
    c.drawString(30, height-40, f"Conversation Log - Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = height-60
    for line in log_lines:
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height-40
        c.drawString(30, y, line[:110])  # wrap defensively
        y -= 14
    c.save()

# ----------------------------------------
# 🗣️ Minimal patient scripts (replace with yours)
# ----------------------------------------
patient_scripts = {
    "Anne": {
        "ClientAgent": "📞 Hello, this is Anne. I fell and I have severe leg pain.",
        "ClientInteractionAgent": "Thank you Anne, I’ll collect a few details.",
        "TriageMedicalAssessmentAgent": "Based on symptoms, an urgent assessment is recommended.",
        "ClientAgent_2": "I understand. What should I do?",
        "ProviderNetworkAgent": "Nearest in-network is Hospital Pasteur, Level 1 trauma center.",
        "ClientAgent_3": "Okay, can you book me in?",
        "MedicalDocumentationAgent": "We will log your medical history and consent.",
        "ClientAgent_4": "Consent provided.",
        "PolicyValidationAgent": "Your policy covers emergency treatment and escorted repatriation if needed.",
        "MedicalDecisionAgent": "Decision: proceed to emergency department at Pasteur.",
        "ClientAgent_5": "I’m heading there now.",
        "RepatriationPlannerAgent": "Repatriation not required at this time.",
        "ComplianceConsentAgent": "Consent stored and compliant.",
        "ClientAgent_6": "Thank you.",
        "CountryCareLevelAgent": "France care level is adequate.",
        "OrchestratorAgent": "Case closed. Get well soon."
    },
    "Liam": {"ClientAgent": "Hi, I have high fever and dizziness."},
    "Priya": {"ClientAgent": "I have abdominal pain at the airport."}
}

# ----------------------------------------
# 🚀 Gradio UI
# ----------------------------------------
def run_simulation_ui(patient_name):
    patient = get_patient_by_name(patient_name)
    if not patient:
        return "❌ Patient not found.", None, None
    script = patient_scripts.get(patient_name)
    if not script:
        return "❌ No script found for this patient.", None, None

    # Build RAG chains
    global rag_hospital, rag_policy
    rag_hospital = rag_policy = None
    try:
        rag_hospital = create_rag_chain("rag_docs/hospital_data.txt")
        rag_policy   = create_rag_chain("rag_docs/policy_terms.txt")
    except Exception as e:
        return f"⚠️ Error building RAG indexes: {e}", None, None

    # Cleanup
    for f in audio_dir.glob("*.mp3"):
        try: f.unlink()
        except: pass
    if log_file.exists():
        try: log_file.unlink()
        except: pass

    # Run graph
    graph = build_workflow()
    state = graph.invoke({
        "patient": patient,
        "script": script,
        "log": [],
        "audio": []
    })

    # Outputs
    full_audio = audio_dir / f"{patient_name}_full.mp3"
    pdf_file   = audio_dir / f"{patient_name}_log.pdf"
    concatenate_audio(state["audio"], full_audio)
    generate_pdf_from_log(state["log"], pdf_file)

    with zip_output.open("wb") as f:
        with ZipFile(f, "w") as z:
            for a in state["audio"]:
                z.write(a, arcname=Path(a).name)
            log_file.write_text("\n".join(state["log"]))
            z.write(log_file, arcname=log_file.name)
            z.write(pdf_file, arcname=pdf_file.name)
            z.write(full_audio, arcname=full_audio.name)

    return "\n".join(state["log"]), str(zip_output), str(full_audio)

def launch_ui():
    demo = gr.Interface(
        fn=run_simulation_ui,
        inputs=gr.Dropdown(choices=["Anne","Liam","Priya"], label="Select Patient", value="Anne"),
        outputs=[
            gr.Textbox(label="Conversation Log"),
            gr.File(label="Download ZIP"),
            gr.Audio(label="Full Conversation", type="filepath")
        ],
        title="🧠 Global MedAssist",
        description="Multi-agent simulation with TTS, RAG, PDF export"
    )
    # queue() helps under load
    demo.queue().launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", 7860)))

if __name__ == "__main__":
    launch_ui()

