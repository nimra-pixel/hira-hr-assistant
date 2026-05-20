import streamlit as st
import json
import datetime
import time
from groq import Groq
from hr_config import (
    APP_NAME, JOB_SEEKER_QUICK_PROMPTS, HR_QUICK_PROMPTS,
    INTERVIEW_TYPES, JOB_ROLES
)
from hr_engine import (
    chat_response, analyze_resume, mock_interview_response,
    generate_career_report, extract_resume_text
)

st.set_page_config(page_title="HIRA — HR Assistant", page_icon="💼", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
  html,body,[class*="css"]{background:#0a0d14!important;color:#e2e8f0!important;font-family:'Inter',sans-serif!important;}
  .stApp{background:#0a0d14!important;}
  .block-container{padding-top:1rem!important;}
  h1,h2,h3{color:#7dd3fc!important;}
  [data-testid="stSidebar"]{background:#060810!important;border-right:1px solid #1e293b!important;}

  /* Buttons */
  .stButton>button{background:#0f1f38!important;color:#7dd3fc!important;border:1px solid #7dd3fc33!important;border-radius:8px!important;font-size:12px!important;transition:all 0.2s;}
  .stButton>button:hover{background:#7dd3fc22!important;border-color:#7dd3fc!important;}
  .stButton>button[kind="primary"]{background:linear-gradient(135deg,#7dd3fc22,#a78bfa22)!important;border:1px solid #7dd3fc!important;font-weight:700!important;color:#7dd3fc!important;}

  /* Chat messages */
  .chat-user{background:#1e3a5f;border-radius:12px 12px 2px 12px;padding:12px 16px;margin:8px 0 8px 60px;font-size:14px;color:#e2e8f0;line-height:1.6;}
  .chat-bot{background:#0f1f38;border:1px solid #1e3a5f;border-radius:12px 12px 12px 2px;padding:12px 16px;margin:8px 60px 8px 0;font-size:14px;color:#e2e8f0;line-height:1.6;}
  .chat-name-user{font-size:11px;color:#7dd3fc;text-align:right;margin-bottom:3px;}
  .chat-name-bot{font-size:11px;color:#a78bfa;margin-bottom:3px;}

  /* Mode cards */
  .mode-card{background:#0f1f38;border:2px solid #1e3a5f;border-radius:12px;padding:20px;text-align:center;cursor:pointer;transition:all 0.2s;}
  .mode-card:hover,.mode-card.active{border-color:#7dd3fc;background:#0d1f3c;}
  .mode-card h3{color:#7dd3fc!important;margin:8px 0 4px 0;}
  .mode-card p{color:#64748b;font-size:12px;margin:0;}

  /* Quick prompts */
  .quick-btn{background:#0f1f38!important;border:1px solid #1e3a5f!important;border-radius:20px!important;padding:6px 14px!important;font-size:11px!important;color:#94a3b8!important;margin:3px!important;}
  .quick-btn:hover{border-color:#7dd3fc!important;color:#7dd3fc!important;}

  /* Resume card */
  .resume-card{background:#0f1f38;border:1px solid #1e3a5f;border-radius:10px;padding:14px;margin:8px 0;}
  .score-ring{font-size:36px;font-weight:700;text-align:center;}
  .tag{display:inline-block;background:#1e3a5f;border-radius:12px;padding:3px 10px;font-size:11px;margin:2px;color:#94a3b8;}
  .tag.tech{background:#1a1f38;color:#7dd3fc;}
  .tag.soft{background:#1a2a1a;color:#4ade80;}
  .tag.role{background:#2a1a38;color:#a78bfa;}

  /* Metrics */
  [data-testid="stMetric"]{background:#0f1f38!important;border:1px solid #1e293b!important;border-radius:8px!important;padding:10px!important;}
  [data-testid="stMetricValue"]{color:#7dd3fc!important;}
  [data-testid="stMetricLabel"]{color:#4a6a8a!important;font-size:0.65rem!important;}

  /* Interview */
  .interview-q{background:#0f1f38;border-left:4px solid #7dd3fc;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;font-size:14px;}
  .interview-feedback{background:#0a1f14;border-left:4px solid #4ade80;border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;font-size:13px;color:#86efac;}

  /* Report */
  .report-section{background:#0f1f38;border:1px solid #1e293b;border-radius:10px;padding:16px;margin:10px 0;}
  .report-section h4{color:#7dd3fc!important;margin:0 0 10px 0;font-size:13px;letter-spacing:1px;}

  /* Tabs */
  .stTabs [data-baseweb="tab"]{color:#4a6a8a!important;font-size:13px!important;}
  .stTabs [aria-selected="true"]{color:#7dd3fc!important;border-bottom:2px solid #7dd3fc!important;}

  /* Other */
  hr{border-color:#1e293b!important;}
  .stTextInput input,.stTextArea textarea{background:#0f1f38!important;border:1px solid #1e293b!important;color:#e2e8f0!important;}
  .stSelectbox>div>div{background:#0f1f38!important;border:1px solid #1e293b!important;color:#e2e8f0!important;}
  .stSelectbox label,.stSlider label,.stFileUploader label{color:#4a6a8a!important;font-size:12px!important;}
  [data-testid="stExpander"]{border:1px solid #1e293b!important;background:#0f1f38!important;}
  .streamlit-expanderHeader{color:#7dd3fc!important;}
  .stProgress>div>div{background:#7dd3fc!important;}
  .stSuccess{background:#0a1f14!important;border:1px solid #4ade80!important;color:#4ade80!important;}
  .stWarning{background:#1a1500!important;border:1px solid #fbbf24!important;}
  .stInfo{background:#0f1f38!important;border:1px solid #7dd3fc33!important;}
</style>
""", unsafe_allow_html=True)

# ── Secrets ───────────────────────────────────────────────────────────────────
default_key = st.secrets.get("GROQ_API_KEY", "")

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "mode": None,
    "chat_history": [],
    "interview_history": [],
    "resume_text": "",
    "resume_analysis": {},
    "interview_active": False,
    "interview_q_num": 1,
    "interview_role": "",
    "interview_type": "",
    "user_info": {},
    "career_report": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ CONFIG")
    api_key = st.text_input("Groq API Key", value=default_key, type="password", placeholder="gsk_...")
    model   = st.selectbox("Model", ["llama-3.1-8b-instant","llama-3.3-70b-versatile"], help="8b is faster and less likely to hit rate limits")
    st.divider()

    if st.session_state.mode:
        mode_label = "🧑‍💼 Job Seeker Mode" if st.session_state.mode=="job_seeker" else "🏢 HR Manager Mode"
        st.markdown(f"**Active Mode:** {mode_label}")
        if st.button("🔄 Switch Mode", use_container_width=True):
            st.session_state.mode = None
            st.session_state.chat_history = []
            st.rerun()
        st.divider()

    st.markdown("### 👤 YOUR PROFILE")
    user_name = st.text_input("Your Name", placeholder="e.g. Nimra", key="u_name")
    if st.session_state.mode == "job_seeker":
        user_role   = st.text_input("Target Job Role", placeholder="e.g. AI Engineer", key="u_role")
        user_exp    = st.selectbox("Experience", ["Student","0-1 years","1-3 years","3-5 years","5+ years"], key="u_exp")
        user_skills = st.text_input("Key Skills", placeholder="Python, ML, NLP…", key="u_skills")
    elif st.session_state.mode == "hr_manager":
        company     = st.text_input("Company", placeholder="e.g. Tech Corp", key="u_company")
        industry    = st.text_input("Industry", placeholder="e.g. FinTech", key="u_industry")

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 💼 HIRA — HR INTELLIGENCE & RECRUITMENT ASSISTANT")
st.caption("Dual-mode AI HR Platform · Job Seekers & HR Managers · Resume Analysis · Mock Interviews · Career Reports")
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# MODE SELECTION
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.mode:
    st.markdown("### 🎯 SELECT YOUR MODE")
    st.markdown('<span style="color:#64748b;font-size:13px">Choose how you want to use HIRA today</span>', unsafe_allow_html=True)
    st.markdown("")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
        <div class="mode-card">
          <div style="font-size:48px">🧑‍💼</div>
          <h3>JOB SEEKER</h3>
          <p>Resume review · Interview prep · Career advice · Mock interviews · Salary guidance</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter as Job Seeker →", use_container_width=True, type="primary"):
            st.session_state.mode = "job_seeker"
            st.session_state.chat_history = []
            st.rerun()

    with m2:
        st.markdown("""
        <div class="mode-card">
          <div style="font-size:48px">🏢</div>
          <h3>HR MANAGER</h3>
          <p>Job descriptions · Candidate screening · HR policies · Onboarding · Labor law · Templates</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter as HR Manager →", use_container_width=True, type="primary"):
            st.session_state.mode = "hr_manager"
            st.session_state.chat_history = []
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP (after mode selected)
# ══════════════════════════════════════════════════════════════════════════════
mode = st.session_state.mode

# Build user context
if mode == "job_seeker":
    user_context = f"Name:{st.session_state.get('u_name','')} Role:{st.session_state.get('u_role','')} Exp:{st.session_state.get('u_exp','')} Skills:{st.session_state.get('u_skills','')}"
else:
    user_context = f"Name:{st.session_state.get('u_name','')} Company:{st.session_state.get('u_company','')} Industry:{st.session_state.get('u_industry','')}"

resume_summary = ""
if st.session_state.resume_analysis:
    ra = st.session_state.resume_analysis
    resume_summary = f"ATS:{ra.get('ats_score',0)} Level:{ra.get('experience_level','')} Skills:{ra.get('skills',{})}"

# ── Tabs ──────────────────────────────────────────────────────────────────────
if mode == "job_seeker":
    tab1, tab2, tab3, tab4 = st.tabs(["💬 CHAT", "📄 RESUME ANALYZER", "🎤 MOCK INTERVIEW", "📊 CAREER REPORT"])
else:
    tab1, tab2 = st.tabs(["💬 CHAT", "📋 HR TOOLKIT"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    mode_label = "🧑‍💼 Job Seeker Assistant" if mode=="job_seeker" else "🏢 HR Manager Assistant"
    st.markdown(f"### {mode_label}")

    # Quick prompts
    quick_prompts = JOB_SEEKER_QUICK_PROMPTS if mode=="job_seeker" else HR_QUICK_PROMPTS
    st.markdown('<span style="color:#4a6a8a;font-size:11px">QUICK PROMPTS:</span>', unsafe_allow_html=True)
    qcols = st.columns(4)
    for i, qp in enumerate(quick_prompts[:4]):
        with qcols[i]:
            if st.button(qp[:35]+"…" if len(qp)>35 else qp, key=f"qp_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":qp})
                if api_key:
                    with st.spinner("HIRA is thinking…"):
                        reply = chat_response(
                            Groq(api_key=api_key), model, mode,
                            st.session_state.chat_history, user_context, resume_summary
                        )
                    st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()

    qcols2 = st.columns(4)
    for i, qp in enumerate(quick_prompts[4:8]):
        with qcols2[i]:
            if st.button(qp[:35]+"…" if len(qp)>35 else qp, key=f"qp2_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","content":qp})
                if api_key:
                    with st.spinner("HIRA is thinking…"):
                        reply = chat_response(
                            Groq(api_key=api_key), model, mode,
                            st.session_state.chat_history, user_context, resume_summary
                        )
                    st.session_state.chat_history.append({"role":"assistant","content":reply})
                st.rerun()

    st.divider()

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            hira_intro = (
                "👋 Hi! I'm **HIRA**, your AI HR assistant. I can help you with resume review, interview prep, career advice, salary guidance, and more. What would you like to work on today?"
                if mode == "job_seeker" else
                "👋 Hi! I'm **HIRA**, your AI HR operations assistant. I can help you write job descriptions, create interview questions, draft HR policies, answer labor law questions, and more. How can I help?"
            )
            st.markdown(f'<div class="chat-name-bot">🤖 HIRA</div><div class="chat-bot">{hira_intro}</div>', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                name = st.session_state.get("u_name","You") or "You"
                st.markdown(f'<div class="chat-name-user">👤 {name}</div><div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-name-bot">🤖 HIRA</div><div class="chat-bot">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    st.markdown("")
    inp_col, send_col = st.columns([5, 1])
    with inp_col:
        user_input = st.text_input("Message HIRA…", placeholder="Ask anything about HR, careers, interviews…", label_visibility="collapsed", key="chat_input")
    with send_col:
        send_btn = st.button("Send ➤", use_container_width=True, type="primary")

    if (send_btn or user_input) and user_input and api_key:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        with st.spinner("HIRA is thinking…"):
            reply = chat_response(
                Groq(api_key=api_key), model, mode,
                st.session_state.chat_history, user_context, resume_summary
            )
        st.session_state.chat_history.append({"role":"assistant","content":reply})
        st.rerun()

    if not api_key:
        st.warning("⚠️ Add your Groq API key in the sidebar")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 (Job Seeker) — RESUME ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
if mode == "job_seeker":
    with tab2:
        st.markdown("### 📄 RESUME ANALYZER")
        st.markdown('<span style="color:#4a6a8a;font-size:12px">Upload your resume for ATS score, skill analysis, and improvement suggestions</span>', unsafe_allow_html=True)

        r_tab1, r_tab2 = st.tabs(["📎 Upload PDF/TXT", "📝 Paste Resume Text"])

        with r_tab1:
            uploaded = st.file_uploader("Upload your resume", type=["pdf","txt"], key="resume_upload")
            if uploaded:
                text = extract_resume_text(uploaded)
                if text:
                    st.session_state.resume_text = text
                    st.success(f"✅ Resume loaded — {len(text.split())} words")
                else:
                    st.error("Could not extract text. Try pasting instead.")

        with r_tab2:
            pasted_resume = st.text_area("Paste your resume text here", height=250, key="resume_paste",
                placeholder="Paste your full resume text here…")
            if pasted_resume.strip():
                st.session_state.resume_text = pasted_resume

        if st.session_state.resume_text:
            if st.button("🔍 ANALYZE RESUME", type="primary", use_container_width=True):
                if not api_key:
                    st.error("API key required")
                else:
                    with st.spinner("Analyzing your resume with AI…"):
                        analysis = analyze_resume(Groq(api_key=api_key), model, st.session_state.resume_text)
                    if analysis:
                        st.session_state.resume_analysis = analysis
                    else:
                        st.error("Could not parse analysis. Try again.")

        if st.session_state.resume_analysis:
            ra = st.session_state.resume_analysis
            st.divider()
            st.markdown("### 📊 ANALYSIS RESULTS")

            # ATS Score
            score = ra.get("ats_score", 0)
            score_color = "#4ade80" if score>=75 else "#fbbf24" if score>=50 else "#ef4444"
            sc1, sc2, sc3 = st.columns([1,2,1])
            with sc2:
                st.markdown(f'<div style="text-align:center;padding:20px;background:#0f1f38;border-radius:12px;border:2px solid {score_color}">'
                           f'<div style="font-size:12px;color:#4a6a8a">ATS COMPATIBILITY SCORE</div>'
                           f'<div style="font-size:56px;font-weight:700;color:{score_color}">{score}</div>'
                           f'<div style="font-size:12px;color:#4a6a8a">/ 100</div>'
                           f'<div style="font-size:13px;color:{score_color};margin-top:6px">{"Excellent ✅" if score>=75 else "Needs Work ⚠️" if score>=50 else "Poor ❌"}</div>'
                           f'</div>', unsafe_allow_html=True)

            st.markdown("")
            m1,m2,m3 = st.columns(3)
            m1.metric("Experience Level", ra.get("experience_level","N/A"))
            m2.metric("Technical Skills", len(ra.get("skills",{}).get("technical",[])))
            m3.metric("Soft Skills",      len(ra.get("skills",{}).get("soft",[])))

            # Skills
            tech_skills = ra.get("skills",{}).get("technical",[])
            soft_skills = ra.get("skills",{}).get("soft",[])
            if tech_skills or soft_skills:
                st.markdown("#### 🔧 Skills Detected")
                skill_html = ""
                for s in tech_skills: skill_html += f'<span class="tag tech">{s}</span>'
                for s in soft_skills:  skill_html += f'<span class="tag soft">{s}</span>'
                st.markdown(skill_html, unsafe_allow_html=True)

            # Matching roles
            roles = ra.get("matching_roles",[])
            if roles:
                st.markdown("#### 🎯 Matching Job Roles")
                role_html = "".join([f'<span class="tag role">{r}</span>' for r in roles])
                st.markdown(role_html, unsafe_allow_html=True)

            # Strengths & weaknesses
            str_col, weak_col = st.columns(2)
            with str_col:
                st.markdown("#### ✅ Strengths")
                for s in ra.get("strengths",[]):
                    st.markdown(f'<div style="color:#4ade80;font-size:13px;padding:3px 0">✓ {s}</div>', unsafe_allow_html=True)
            with weak_col:
                st.markdown("#### ⚠️ Weaknesses")
                for w in ra.get("weaknesses",[]):
                    st.markdown(f'<div style="color:#fbbf24;font-size:13px;padding:3px 0">• {w}</div>', unsafe_allow_html=True)

            # Improvements
            st.markdown("#### 🚀 Top Improvements")
            for i, imp in enumerate(ra.get("improvements",[])):
                st.markdown(f'<div style="background:#0f1f38;border-left:3px solid #7dd3fc;padding:8px 12px;margin:4px 0;border-radius:0 6px 6px 0;font-size:13px">{i+1}. {imp}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 (Job Seeker) — MOCK INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if mode == "job_seeker":
    with tab3:
        st.markdown("### 🎤 MOCK INTERVIEW SIMULATOR")

        if not st.session_state.interview_active:
            st.markdown('<span style="color:#4a6a8a;font-size:12px">Configure your mock interview and practice with AI feedback</span>', unsafe_allow_html=True)
            ic1, ic2 = st.columns(2)
            with ic1:
                int_role = st.selectbox("Job Role", JOB_ROLES, key="int_role")
                int_type = st.selectbox("Interview Type", INTERVIEW_TYPES, key="int_type")
            with ic2:
                int_bg   = st.text_area("Your Background (brief)", height=100,
                    placeholder="e.g. 2 years Python experience, worked on ML projects…", key="int_bg")

            if st.button("🎤 START MOCK INTERVIEW", type="primary", use_container_width=True):
                if not api_key:
                    st.error("API key required")
                else:
                    st.session_state.interview_active = True
                    st.session_state.interview_role   = int_role
                    st.session_state.interview_type   = int_type
                    st.session_state.interview_history= []
                    st.session_state.interview_q_num  = 1
                    # Get first question
                    with st.spinner("Preparing your interview…"):
                        first_q = mock_interview_response(
                            Groq(api_key=api_key), model,
                            [{"role":"user","content":"Start the interview. Ask me the first question."}],
                            int_role, int_type, int_bg, 1
                        )
                    st.session_state.interview_history.append({"role":"assistant","content":first_q})
                    st.rerun()
        else:
            st.markdown(f'<div style="color:#4a6a8a;font-size:12px">Role: <b style="color:#7dd3fc">{st.session_state.interview_role}</b> | Type: <b style="color:#7dd3fc">{st.session_state.interview_type}</b> | Question {st.session_state.interview_q_num}/5</div>', unsafe_allow_html=True)
            prog = min(st.session_state.interview_q_num / 5, 1.0)
            st.progress(prog, text=f"Question {st.session_state.interview_q_num} of 5")

            # Display interview history
            for msg in st.session_state.interview_history:
                if msg["role"] == "assistant":
                    st.markdown(f'<div class="interview-q">🤖 <b>HIRA:</b> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)

            # Answer input
            ans_col, submit_col = st.columns([4,1])
            with ans_col:
                answer = st.text_area("Your answer…", height=100, label_visibility="collapsed", key="int_answer", placeholder="Type your answer here…")
            with submit_col:
                if st.button("Submit ➤", use_container_width=True, type="primary"):
                    if answer and api_key:
                        st.session_state.interview_history.append({"role":"user","content":answer})
                        with st.spinner("Getting feedback…"):
                            feedback = mock_interview_response(
                                Groq(api_key=api_key), model,
                                st.session_state.interview_history,
                                st.session_state.interview_role,
                                st.session_state.interview_type,
                                st.session_state.get("int_bg",""),
                                st.session_state.interview_q_num + 1
                            )
                        st.session_state.interview_history.append({"role":"assistant","content":feedback})
                        st.session_state.interview_q_num += 1
                        st.rerun()

            if st.button("🛑 End Interview", use_container_width=True):
                st.session_state.interview_active = False
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 (Job Seeker) — CAREER REPORT
# ══════════════════════════════════════════════════════════════════════════════
if mode == "job_seeker":
    with tab4:
        st.markdown("### 📊 CAREER INTELLIGENCE REPORT")
        st.markdown('<span style="color:#4a6a8a;font-size:12px">AI generates a personalized career roadmap based on your profile and resume</span>', unsafe_allow_html=True)

        target_role = st.text_input("Target Role", placeholder="e.g. Senior AI Engineer at a tech company", key="target_role")

        if st.button("🧠 GENERATE CAREER REPORT", type="primary", use_container_width=True):
            if not api_key:
                st.error("API key required")
            else:
                candidate_info = {
                    "name":   st.session_state.get("u_name",""),
                    "role":   st.session_state.get("u_role",""),
                    "exp":    st.session_state.get("u_exp",""),
                    "skills": st.session_state.get("u_skills",""),
                }
                with st.spinner("Generating your career report…"):
                    report = generate_career_report(
                        Groq(api_key=api_key), model,
                        candidate_info,
                        resume_summary,
                        target_role,
                        st.session_state.chat_history
                    )
                if report:
                    st.session_state.career_report = report
                else:
                    st.error("Could not generate report. Try again.")

        if st.session_state.career_report:
            r = st.session_state.career_report
            st.divider()

            # Score
            score = r.get("overall_readiness_score", 0)
            score_color = "#4ade80" if score>=75 else "#fbbf24" if score>=50 else "#ef4444"
            st.markdown(f'<div style="text-align:center;padding:16px;background:#0f1f38;border-radius:12px;border:2px solid {score_color};margin-bottom:16px">'
                       f'<div style="font-size:11px;color:#4a6a8a;letter-spacing:1px">CAREER READINESS SCORE</div>'
                       f'<div style="font-size:48px;font-weight:700;color:{score_color}">{score}<span style="font-size:20px">/100</span></div>'
                       f'</div>', unsafe_allow_html=True)

            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown('<div class="report-section"><h4>✅ STRENGTHS</h4>', unsafe_allow_html=True)
                for s in r.get("strengths",[]):
                    st.markdown(f'<div style="color:#4ade80;font-size:13px;padding:3px 0">✓ {s}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="report-section"><h4>🎯 RECOMMENDED ROLES</h4>', unsafe_allow_html=True)
                for role in r.get("recommended_roles",[]):
                    st.markdown(f'<span class="tag role">{role}</span>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with rc2:
                st.markdown('<div class="report-section"><h4>⚠️ SKILL GAPS</h4>', unsafe_allow_html=True)
                for g in r.get("skill_gaps",[]):
                    st.markdown(f'<div style="color:#fbbf24;font-size:13px;padding:3px 0">• {g}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                sal = r.get("salary_range",{})
                if sal:
                    st.markdown(f'<div class="report-section"><h4>💰 SALARY RANGE</h4>'
                               f'<div style="font-size:22px;font-weight:700;color:#7dd3fc">{sal.get("currency","PKR")} {sal.get("min",0):,} – {sal.get("max",0):,}</div>'
                               f'<div style="color:#4a6a8a;font-size:12px">per month estimated</div></div>', unsafe_allow_html=True)

            # Learning path
            lp = r.get("learning_path",[])
            if lp:
                st.markdown('<div class="report-section"><h4>📚 LEARNING ROADMAP</h4>', unsafe_allow_html=True)
                for item in lp:
                    st.markdown(f'<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1e293b;font-size:13px">'
                               f'<span style="color:#e2e8f0">🎯 {item.get("skill","")}</span>'
                               f'<span style="color:#7dd3fc">{item.get("resource","")}</span>'
                               f'<span style="color:#4a6a8a">{item.get("timeline","")}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Action items
            actions = r.get("action_items",[])
            if actions:
                st.markdown('<div class="report-section"><h4>⚡ ACTION ITEMS</h4>', unsafe_allow_html=True)
                for i, a in enumerate(actions):
                    st.markdown(f'<div style="background:#0a1526;border-left:3px solid #7dd3fc;padding:8px 12px;margin:4px 0;border-radius:0 6px 6px 0;font-size:13px">{i+1}. {a}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Download report
            st.divider()
            report_text = f"""HIRA — CAREER INTELLIGENCE REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Candidate: {r.get('candidate_name','')}
Target Role: {target_role}
Readiness Score: {r.get('overall_readiness_score',0)}/100

STRENGTHS: {', '.join(r.get('strengths',[]))}
SKILL GAPS: {', '.join(r.get('skill_gaps',[]))}
RECOMMENDED ROLES: {', '.join(r.get('recommended_roles',[]))}
SALARY RANGE: {r.get('salary_range',{}).get('currency','PKR')} {r.get('salary_range',{}).get('min',0):,} - {r.get('salary_range',{}).get('max',0):,}

CAREER TRAJECTORY:
{r.get('career_trajectory','')}

ACTION ITEMS:
{chr(10).join([f'{i+1}. {a}' for i,a in enumerate(r.get('action_items',[]))])}

LEARNING ROADMAP:
{chr(10).join([f'- {item.get("skill","")} | {item.get("resource","")} | {item.get("timeline","")}' for item in r.get('learning_path',[])])}
"""
            st.download_button(
                "📥 DOWNLOAD CAREER REPORT",
                data=report_text,
                file_name=f"HIRA_Career_Report_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 (HR Manager) — HR TOOLKIT
# ══════════════════════════════════════════════════════════════════════════════
if mode == "hr_manager":
    with tab2:
        st.markdown("### 📋 HR TOOLKIT")
        tool = st.selectbox("Select Tool", [
            "📝 Job Description Writer",
            "❓ Interview Question Bank",
            "📊 Candidate Evaluation Rubric",
            "📄 Offer Letter Template",
            "📋 Onboarding Checklist",
            "⚖️ Pakistan Labor Law Quick Reference",
        ], key="hr_tool")

        tool_prompt_map = {
            "📝 Job Description Writer":       "Write a detailed job description for: {input}. Include responsibilities, requirements, nice-to-haves, and company culture section.",
            "❓ Interview Question Bank":       "Generate 10 interview questions (mix behavioral, technical, situational) for: {input}. Include expected answer hints.",
            "📊 Candidate Evaluation Rubric":  "Create a detailed evaluation rubric for hiring: {input}. Include criteria, scoring 1-5, and weightings.",
            "📄 Offer Letter Template":         "Write a professional offer letter template for: {input} role. Include salary, benefits, start date placeholders.",
            "📋 Onboarding Checklist":          "Create a comprehensive 30-day onboarding checklist for a new: {input}.",
            "⚖️ Pakistan Labor Law Quick Reference": "Explain Pakistan labor law regarding: {input}. Reference relevant acts.",
        }

        tool_input = st.text_input("Enter details", placeholder="e.g. Senior Python Developer / 30-day leave policy / Software Engineer offer", key="tool_input")

        if st.button("⚡ GENERATE", type="primary", use_container_width=True):
            if not api_key:
                st.error("API key required")
            elif not tool_input:
                st.warning("Enter details above")
            else:
                prompt = tool_prompt_map[tool].format(input=tool_input)
                with st.spinner("Generating…"):
                    result = chat_response(
                        Groq(api_key=api_key), model, "hr_manager",
                        [{"role":"user","content":prompt}], user_context
                    )
                st.markdown("### 📄 Result")
                st.markdown(f'<div class="chat-bot">{result}</div>', unsafe_allow_html=True)
                st.download_button(
                    "📥 Download",
                    data=result,
                    file_name=f"HIRA_{tool.split()[1]}_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
