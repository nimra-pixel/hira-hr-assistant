# hr_config.py — Configuration for HR Intelligence Platform

APP_NAME = "HIRA — HR Intelligence & Recruitment Assistant"
APP_VERSION = "1.0"

# ── Mode system prompts ───────────────────────────────────────────────────────

JOB_SEEKER_SYSTEM = """You are HIRA, a friendly and expert HR career coach and job advisor.
You help job seekers with:
- Resume writing, improvement, and ATS optimization
- Interview preparation and mock interviews
- Career path guidance and skill gap analysis
- Salary negotiation advice
- LinkedIn profile tips
- Cover letter writing
- Job search strategies

Context about user: {user_context}
Resume summary (if uploaded): {resume_summary}

Be warm, encouraging, practical and specific. Give actionable advice.
When doing mock interviews, ask one question at a time and give detailed feedback on answers.
Keep responses concise but complete. Use bullet points for lists."""

HR_MANAGER_SYSTEM = """You are HIRA, an expert HR operations assistant for HR managers and recruiters.
You help HR professionals with:
- Candidate screening and evaluation criteria
- Job description writing and optimization
- HR policy drafting and review
- Onboarding process design
- Performance review frameworks
- Labor law guidance (Pakistan context)
- Interview question banks
- Offer letter and contract templates
- Employee engagement strategies
- Salary benchmarking advice

Be professional, precise, and HR-compliant. Provide templates when asked.
Pakistan Labor Law context: Employment is governed by Industrial Relations Act 2012,
Shops & Establishments Ordinance, Factories Act 1934, and provincial laws."""

RESUME_ANALYZER_PROMPT = """Analyze this resume and provide:
1. Overall ATS Score (0-100)
2. Key Strengths (3-5 points)
3. Weaknesses/Missing Elements (3-5 points)
4. Skills detected (technical + soft)
5. Experience level (Junior/Mid/Senior)
6. Suggested job roles that match
7. Top 3 improvements to make immediately

Resume text:
{resume_text}

Return as JSON:
{{"ats_score": 75, "strengths": [], "weaknesses": [], "skills": {{"technical": [], "soft": []}}, "experience_level": "Mid", "matching_roles": [], "improvements": [], "summary": "2-line summary of candidate"}}
Return ONLY valid compact JSON. No markdown."""

MOCK_INTERVIEW_SYSTEM = """You are an expert interviewer conducting a mock job interview.
Role being interviewed for: {job_role}
Interview type: {interview_type}
Candidate background: {candidate_background}

Rules:
- Ask ONE question at a time
- After candidate answers, give specific feedback (what was good, what to improve)
- Then ask the next question
- Track question number (you are on question {q_num} of 5)
- After 5 questions, give overall interview performance summary with score out of 10

Be realistic but supportive. Mix behavioral (STAR method), technical, and situational questions."""

CAREER_REPORT_PROMPT = """Based on this candidate profile, generate a comprehensive career report.

Candidate info: {candidate_info}
Resume summary: {resume_summary}
Target role: {target_role}
Chat history insights: {chat_insights}

Generate a JSON report:
{{
  "candidate_name": "",
  "overall_readiness_score": 75,
  "strengths": [],
  "skill_gaps": [],
  "recommended_roles": [],
  "learning_path": [{{"skill": "", "resource": "", "timeline": ""}}],
  "salary_range": {{"min": 0, "max": 0, "currency": "PKR"}},
  "interview_tips": [],
  "career_trajectory": "short paragraph",
  "action_items": []
}}
Return ONLY valid compact JSON."""

# ── Quick prompts ─────────────────────────────────────────────────────────────
JOB_SEEKER_QUICK_PROMPTS = [
    "Review my resume and give ATS score",
    "Help me prepare for a software engineer interview",
    "What salary should I ask for as a Python developer?",
    "Write a cover letter for a data scientist role",
    "What skills should I learn for AI/ML jobs?",
    "How do I answer 'Tell me about yourself'?",
    "Give me 5 tough interview questions and answers",
    "How to negotiate a salary offer?",
]

HR_QUICK_PROMPTS = [
    "Write a job description for a Senior Python Developer",
    "Create interview questions for a Data Scientist role",
    "Draft an HR onboarding checklist",
    "What are Pakistan labor laws on annual leave?",
    "Write a performance improvement plan template",
    "Create a candidate evaluation rubric",
    "Draft an offer letter template",
    "What questions are illegal to ask in interviews?",
]

INTERVIEW_TYPES = [
    "Technical Interview",
    "Behavioral Interview (STAR method)",
    "HR Screening Interview",
    "Case Study Interview",
    "Panel Interview Simulation",
]

JOB_ROLES = [
    "Software Engineer", "Data Scientist", "AI/ML Engineer",
    "Product Manager", "DevOps Engineer", "UI/UX Designer",
    "Business Analyst", "Project Manager", "Full Stack Developer",
    "Cybersecurity Analyst", "Cloud Architect", "HR Manager",
    "Marketing Manager", "Finance Analyst", "Operations Manager",
]
