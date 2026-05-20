# hr_engine.py — AI engine for HIRA

import json
import re
from groq import Groq
from hr_config import (
    JOB_SEEKER_SYSTEM, HR_MANAGER_SYSTEM,
    RESUME_ANALYZER_PROMPT, MOCK_INTERVIEW_SYSTEM,
    CAREER_REPORT_PROMPT
)

def clean_json(raw: str) -> dict:
    raw = raw.strip().replace("```json","").replace("```","").strip()
    s = raw.find("{"); e = raw.rfind("}") + 1
    if s == -1 or e == 0:
        return {}
    try:
        return json.loads(raw[s:e])
    except:
        return {}

def chat_response(client, model, mode, messages, user_context="", resume_summary=""):
    """Get chat response based on mode."""
    system = JOB_SEEKER_SYSTEM if mode == "job_seeker" else HR_MANAGER_SYSTEM
    system = system.format(
        user_context=user_context or "Not provided",
        resume_summary=resume_summary or "No resume uploaded yet"
    )
    resp = client.chat.completions.create(
        model=model,
        max_tokens=1000,
        messages=[{"role":"system","content":system}] + messages,
    )
    return resp.choices[0].message.content.strip()

def analyze_resume(client, model, resume_text: str) -> dict:
    """Analyze resume and return structured JSON."""
    prompt = RESUME_ANALYZER_PROMPT.format(resume_text=resume_text[:5000])
    resp = client.chat.completions.create(
        model=model,
        max_tokens=1500,
        messages=[{"role":"user","content":prompt}],
    )
    return clean_json(resp.choices[0].message.content)

def mock_interview_response(client, model, messages, job_role, interview_type, background, q_num):
    """Get mock interview response."""
    system = MOCK_INTERVIEW_SYSTEM.format(
        job_role=job_role,
        interview_type=interview_type,
        candidate_background=background or "Not specified",
        q_num=q_num,
    )
    resp = client.chat.completions.create(
        model=model,
        max_tokens=800,
        messages=[{"role":"system","content":system}] + messages,
    )
    return resp.choices[0].message.content.strip()

def generate_career_report(client, model, candidate_info, resume_summary, target_role, chat_history):
    """Generate comprehensive career report."""
    # Summarize chat history for context
    chat_insights = ""
    if chat_history:
        recent = chat_history[-6:]
        chat_insights = " | ".join([m["content"][:100] for m in recent if m["role"]=="user"])

    prompt = CAREER_REPORT_PROMPT.format(
        candidate_info=json.dumps(candidate_info),
        resume_summary=resume_summary or "Not provided",
        target_role=target_role or "Not specified",
        chat_insights=chat_insights or "No chat history",
    )
    resp = client.chat.completions.create(
        model=model,
        max_tokens=2000,
        messages=[{"role":"user","content":prompt}],
    )
    return clean_json(resp.choices[0].message.content)

def extract_resume_text(uploaded_file) -> str:
    """Extract text from uploaded PDF or TXT."""
    if uploaded_file is None:
        return ""
    filename = uploaded_file.name.lower()
    if filename.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    elif filename.endswith(".pdf"):
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except:
            try:
                import PyPDF2
                import io
                uploaded_file.seek(0)
                reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except:
                return ""
    return ""
