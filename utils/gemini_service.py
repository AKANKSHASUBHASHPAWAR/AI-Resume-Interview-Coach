import os
import json
import re
import warnings

# Suppress google.generativeai deprecation warning for clean logs
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai

# Supported models list with fallback priority
SUPPORTED_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
DEFAULT_MODEL = "gemini-2.0-flash"


def load_env_file():
    """
    Safely load key-value pairs from .env if present in workspace root.
    """
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception:
            pass


# Try loading .env at module import
load_env_file()


def save_api_key_to_env(api_key, env_filename=".env"):
    """
    Saves or updates the GEMINI_API_KEY in the specified .env file in the workspace root,
    sets os.environ["GEMINI_API_KEY"], and configures google.generativeai.
    Returns True if successful, False otherwise.
    """
    key = api_key.strip() if api_key else ""
    if not key:
        return False

    env_path = os.path.join(os.getcwd(), env_filename)
    lines = []
    found = False

    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY=") or line.strip().startswith("GOOGLE_API_KEY="):
                        lines.append(f"GEMINI_API_KEY={key}\n")
                        found = True
                    else:
                        lines.append(line)
        except Exception:
            lines = []

    if not found:
        lines.append(f"GEMINI_API_KEY={key}\n")

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        os.environ["GEMINI_API_KEY"] = key
        configure_gemini(key)
        return True
    except Exception:
        return False


def remove_saved_api_key(env_filename=".env"):
    """
    Removes the saved GEMINI_API_KEY from .env file and os.environ.
    Returns True if successful.
    """
    env_path = os.path.join(os.getcwd(), env_filename)
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = [
                line for line in lines
                if not (line.strip().startswith("GEMINI_API_KEY=") or line.strip().startswith("GOOGLE_API_KEY="))
            ]
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass

    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]

    return True



def get_active_api_key(api_key=None):
    """
    Resolves the API key from parameter, Streamlit secrets, or environment.
    """
    if api_key and api_key.strip():
        return api_key.strip()

    # Streamlit secrets
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
        elif "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"].strip()
    except Exception:
        pass

    # Environment variables
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


def configure_gemini(api_key=None):
    """
    Configures genai with the resolved API key.
    Returns True if configured, False otherwise.
    """
    key = get_active_api_key(api_key)
    if not key:
        return False
    try:
        genai.configure(api_key=key)
        return True
    except Exception:
        return False


def test_gemini_connection(api_key=None, model_name=None):
    """
    Tests whether the Gemini API key is valid by running a lightweight prompt.
    Returns a tuple: (success: bool, message: str).
    """
    if not configure_gemini(api_key):
        return False, "No Gemini API key provided or found."

    chosen_model = model_name or DEFAULT_MODEL
    models_to_try = [chosen_model]
    for m in SUPPORTED_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = ""
    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            resp = model.generate_content("Ping. Reply with 'OK'.")
            if resp and resp.text:
                return True, f"Connected successfully using {m}!"
        except Exception as e:
            last_error = str(e)
            continue

    return False, f"Connection test failed: {last_error}"


def clean_json_response(text):
    """
    Cleans and extracts valid JSON from model responses that might contain
    markdown code blocks, trailing commas, or surrounding conversational text.
    """
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()

    # Attempt 1: Direct JSON parsing
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Attempt 2: Find outermost { ... }
    obj_match = re.search(r"(\{[\s\S]*\})", cleaned)
    if obj_match:
        cand = obj_match.group(1)
        try:
            return json.loads(cand)
        except Exception:
            try:
                fixed_cand = re.sub(r",\s*([\]}])", r"\1", cand)
                return json.loads(fixed_cand)
            except Exception:
                pass

    # Attempt 3: Find outermost [ ... ]
    arr_match = re.search(r"(\[[\s\S]*\])", cleaned)
    if arr_match:
        cand = arr_match.group(1)
        try:
            return json.loads(cand)
        except Exception:
            try:
                fixed_cand = re.sub(r",\s*([\]}])", r"\1", cand)
                return json.loads(fixed_cand)
            except Exception:
                pass

    # Attempt 4: Fix trailing commas on cleaned text
    fixed = re.sub(r",\s*([\]}])", r"\1", cleaned)
    try:
        return json.loads(fixed)
    except Exception:
        return None


def call_gemini_resilient(prompt, is_json=False, api_key=None, model_name=None, generation_config=None):
    """
    Universal resilient caller that tries the preferred model and automatically
    falls back to secondary supported models on any error or tier mismatch.
    """
    if not configure_gemini(api_key):
        return None, "Gemini API key is not configured."

    config = generation_config or {}
    if is_json and "response_mime_type" not in config:
        config["response_mime_type"] = "application/json"

    chosen = model_name or DEFAULT_MODEL
    models_to_try = [chosen]
    for m in SUPPORTED_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_err = ""
    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt, generation_config=config)
            raw_text = ""
            if response:
                try:
                    raw_text = response.text.strip() if response.text else ""
                except (ValueError, AttributeError):
                    if hasattr(response, "candidates") and response.candidates:
                        parts = []
                        for c in response.candidates:
                            if hasattr(c, "content") and hasattr(c.content, "parts"):
                                for p in c.content.parts:
                                    if hasattr(p, "text") and p.text:
                                        parts.append(p.text)
                        raw_text = "\n".join(parts).strip()
            if raw_text:
                if is_json:
                    parsed = clean_json_response(raw_text)
                    if parsed is not None:
                        return parsed, ""
                else:
                    return raw_text, ""
        except Exception as e:
            last_err = str(e)
            continue

    return None, last_err or "Unknown Gemini execution error."


# ---------------------------------------------------------
# 1. Full Structured Resume Parsing
# ---------------------------------------------------------
def parse_full_resume_with_gemini(resume_text, api_key=None, model_name=None):
    """
    Extracts deep, structured candidate profile details from resume text into JSON.
    """
    prompt = f"""
    You are an expert HR technologist and executive recruiter.
    Analyze the following resume and extract all relevant candidate profile information into structured JSON.

    RESUME CONTENT:
    \"\"\"{resume_text}\"\"\"

    Your output MUST be a valid JSON object matching this schema precisely:
    {{
        "full_name": "<candidate full name, or 'Candidate' if unidentifiable>",
        "headline": "<current or target professional title, e.g. 'Senior Full-Stack Engineer'>",
        "contact": {{
            "email": "<email or 'Not Found'>",
            "phone": "<phone number with country code or 'Not Found'>",
            "location": "<city, state/country or 'Not Found'>",
            "linkedin": "<linkedin URL or 'Not Found'>",
            "github": "<github URL or 'Not Found'>",
            "portfolio": "<portfolio / website URL or 'Not Found'>"
        }},
        "summary": "<a 2-3 sentence executive professional summary synthesizing candidate's experience>",
        "skills_by_category": {{
            "Programming Languages": [<list of programming languages>],
            "Frameworks & Libraries": [<list of frameworks, web/app/ml libraries>],
            "Cloud, DevOps & Tools": [<list of cloud platforms, CI/CD, docker, git, etc.>],
            "Databases & Storage": [<list of SQL, NoSQL, data warehouses>],
            "AI, ML & Data Science": [<list of AI, ML, NLP, LLMs, data tools>],
            "Architecture & Methodologies": [<list of domain knowledge, agile, system design, testing>]
        }},
        "education": [
            {{
                "degree": "<degree title or certificate>",
                "institution": "<university or school>",
                "year": "<graduation year or date range>"
            }}
        ],
        "work_experience_highlights": [
            {{
                "role": "<job title>",
                "company": "<company name>",
                "duration": "<dates or duration>",
                "key_achievements": [<1-2 key quantifiable bullet points>]
            }}
        ]
    }}

    Return ONLY the raw JSON object.
    """
    if configure_gemini(api_key):
        data, _ = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "full_name" in data:
            return data

    # Offline Heuristic Candidate Profile Fallback
    from utils.information_extractor import extract_all_contact_info
    from utils.skill_extractor import extract_categorized_skills
    contact = extract_all_contact_info(resume_text)
    skills_cat = extract_categorized_skills(resume_text)
    headline = "Professional Candidate"
    if "AI, ML & Data Science" in skills_cat:
        headline = "AI & Machine Learning Engineer"
    elif "Frameworks & Libraries" in skills_cat and "Databases & Storage" in skills_cat:
        headline = "Full-Stack Software Engineer"

    return {
        "full_name": contact.get("full_name", "Candidate"),
        "headline": headline,
        "contact": {
            "email": contact.get("email", "Not Found"),
            "phone": contact.get("phone", "Not Found"),
            "location": contact.get("location", "Not Specified"),
            "linkedin": contact.get("linkedin", "Not Found"),
            "github": contact.get("github", "Not Found"),
            "portfolio": contact.get("portfolio", "Not Found")
        },
        "summary": f"Results-driven engineer with approximately {contact.get('estimated_exp_years', 4)} years of experience in system design, scalable software architecture, and modern technologies.",
        "skills_by_category": skills_cat,
        "education": [],
        "work_experience_highlights": [],
        "is_offline": True
    }


# ---------------------------------------------------------
# 2. Advanced Multi-Dimensional ATS Analysis & Radar Metrics
# ---------------------------------------------------------
def get_ats_analysis(resume_text, job_description, api_key=None, model_name=None):
    """
    Performs deep, multi-dimensional ATS benchmarking against the target job description.
    """
    prompt = f"""
    You are an enterprise-grade Applicant Tracking System (ATS) auditor and hiring committee advisor.
    Perform a comprehensive, rigorous ATS audit of the candidate's resume against the target job description.

    RESUME CONTENT:
    \"\"\"{resume_text}\"\"\"

    TARGET JOB DESCRIPTION:
    \"\"\"{job_description}\"\"\"

    Evaluate the match thoroughly and return a valid JSON object matching this schema:
    {{
        "score_overall": <integer 0-100, holistic candidate fit>,
        "score_skills": <integer 0-100, technical & domain skill overlap>,
        "score_experience": <integer 0-100, depth, relevance and seniority alignment>,
        "score_formatting": <integer 0-100, ATS parsing readiness, clear headings, no complex tables>,
        "score_impact": <integer 0-100, presence of quantified metrics, revenue, % improvements, action verbs>,
        "score_education": <integer 0-100, educational requirements and certifications alignment>,
        
        "executive_summary": "<a concise 2-sentence summary of candidate fit for this exact role>",
        
        "strengths": [
            "<top matching qualifications and experiences that directly fulfill high-priority JD requirements>"
        ],
        
        "keyword_analysis": {{
            "matched_keywords": [<list of crucial skills/keywords found in both resume and JD>],
            "missing_must_have": [<list of critical, non-negotiable skills or tools present in JD but missing in resume>],
            "missing_nice_to_have": [<list of secondary/preferred skills present in JD but absent in resume>]
        }},
        
        "section_audit": [
            {{
                "section": "Contact & Links",
                "status": "<'Pass' or 'Warning' or 'Critical'>",
                "finding": "<brief audit observation>"
            }},
            {{
                "section": "Professional Summary",
                "status": "<'Pass' or 'Warning' or 'Critical'>",
                "finding": "<brief audit observation>"
            }},
            {{
                "section": "Work Experience & Metrics",
                "status": "<'Pass' or 'Warning' or 'Critical'>",
                "finding": "<brief audit observation>"
            }},
            {{
                "section": "Skills & ATS Keywords",
                "status": "<'Pass' or 'Warning' or 'Critical'>",
                "finding": "<brief audit observation>"
            }},
            {{
                "section": "Education & Credentials",
                "status": "<'Pass' or 'Warning' or 'Critical'>",
                "finding": "<brief audit observation>"
            }}
        ],
        
        "optimization_tips": [
            "<actionable, specific improvement instruction to increase ATS rank>"
        ]
    }}

    Return ONLY the raw JSON object.
    """
    data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
    if isinstance(data, dict):
        return data
    return {"error": f"Failed to analyze resume with Gemini: {err}"}


# ---------------------------------------------------------
# 3. Resume Bullet Rewriter (STAR / XYZ Method)
# ---------------------------------------------------------
def rewrite_resume_bullet(bullet_text, job_context="", api_key=None, model_name=None):
    """
    Transforms a weak resume bullet point into 3 high-impact variations using Google's XYZ formula:
    'Accomplished [X], as measured by [Y], by doing [Z]'.
    Falls back to smart offline heuristics when Gemini API is unconfigured or unavailable.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an elite career coach specializing in high-converting resumes for top tech companies.
        Transform the following weak resume bullet point into 3 distinct, high-impact variations using strong action verbs
        and Google's XYZ formula ("Accomplished [X], as measured by [Y], by doing [Z]").

        ORIGINAL BULLET POINT:
        \"{bullet_text}\"

        JOB CONTEXT / TARGET SKILLS:
        \"{job_context}\"

        Return a valid JSON object matching this schema:
        {{
            "critique": "<brief 1-sentence breakdown of what was weak in the original bullet>",
            "variations": [
                {{
                    "style": "Metric-Driven (Results Focus)",
                    "rewritten": "<bullet with realistic quantified impact, percentage, scale, or latency improvement>",
                    "highlight": "<key improvement made>"
                }},
                {{
                    "style": "Leadership & Ownership",
                    "rewritten": "<bullet highlighting architectural ownership, cross-functional collaboration or mentorship>",
                    "highlight": "<key improvement made>"
                }},
                {{
                    "style": "Technical Precision (Stack Focus)",
                    "rewritten": "<bullet focusing on technical rigor, specific tools, patterns, and implementation depth>",
                    "highlight": "<key improvement made>"
                }}
            ]
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "variations" in data:
            return data

    from utils.offline_heuristics import generate_offline_bullet_rewrite
    return generate_offline_bullet_rewrite(bullet_text, job_context=job_context)


# ---------------------------------------------------------
# 4. Tailored Executive Summary Generator
# ---------------------------------------------------------
def generate_tailored_summary(resume_text, job_description, api_key=None, model_name=None):
    """
    Generates a tailored 3-4 sentence professional summary aligned directly with the target job.
    Falls back to smart offline heuristics when Gemini is offline.
    """
    if configure_gemini(api_key):
        prompt = f"""
        Based on the candidate's resume and target job description, write a compelling, tailored 3-4 sentence
        Executive Summary that can be placed at the top of their resume.
        Highlight the candidate's strongest matching credentials, years of relevant experience, and key value proposition.

        RESUME:
        \"\"\"{resume_text[:3000]}\"\"\"

        TARGET JOB DESCRIPTION:
        \"\"\"{job_description[:3000]}\"\"\"

        Return ONLY the polished summary paragraph. Do not include labels, headings, or quotes.
        """
        data, err = call_gemini_resilient(prompt, is_json=False, api_key=api_key, model_name=model_name)
        if data and not data.startswith("Error"):
            return data

    from utils.offline_heuristics import generate_offline_tailored_summary
    return generate_offline_tailored_summary(resume_text, job_description)


# ---------------------------------------------------------
# 5. Advanced Cover Letter Studio
# ---------------------------------------------------------
def generate_cover_letter(
    resume_text,
    job_description,
    tone="Professional",
    company_name="",
    hiring_manager="",
    focus_area="",
    length="Standard (350 words)",
    api_key=None,
    model_name=None
):
    """
    Generates a personalized, tailored cover letter based on candidate resume and job description.
    Falls back to smart offline templates when Gemini is offline.
    """
    if configure_gemini(api_key):
        word_guide = "around 250 words" if "Short" in length else "around 450 words" if "Comprehensive" in length else "around 350 words"
        prompt = f"""
        You are an expert executive career advisor. Write an outstanding, tailored cover letter for a candidate applying to this job.

        TONE: {tone}
        TARGET LENGTH: {word_guide}
        COMPANY NAME: {company_name if company_name else "[Company Name]"}
        ADDRESSED TO: {hiring_manager if hiring_manager else "Hiring Manager"}
        SPECIAL FOCUS / KEY PROJECT TO EMPHASIZE: {focus_area if focus_area else "Best matching technical experience"}

        CANDIDATE RESUME:
        \"\"\"{resume_text}\"\"\"

        JOB DESCRIPTION:
        \"\"\"{job_description}\"\"\"

        Formatting Requirements:
        1. Standard business letter format: Date, Salutation, 3-4 cohesive paragraphs, professional closing, and candidate's name.
        2. Directly connect specific accomplishments from the resume with the core problems the employer wants solved in the job description.
        3. Avoid generic buzzwords; use tangible outcomes and domain knowledge.
        4. Keep tone engaging, authentic, and confident.

        Return the final cover letter as clean formatted text.
        """
        data, err = call_gemini_resilient(prompt, is_json=False, api_key=api_key, model_name=model_name)
        if data and not data.startswith("Failed") and not data.startswith("Error"):
            return data

    from utils.offline_heuristics import generate_offline_cover_letter
    return generate_offline_cover_letter(
        resume_text, job_description, tone=tone, company_name=company_name,
        hiring_manager=hiring_manager, focus_area=focus_area, length=length
    )


# ---------------------------------------------------------
# 6. Recruiter Cold Outreach & LinkedIn Message Studio
# ---------------------------------------------------------
def generate_cold_outreach(
    resume_text,
    job_description,
    outreach_type="LinkedIn Connection Note",
    company_name="",
    recipient_name="",
    tone="Professional & Direct",
    api_key=None,
    model_name=None
):
    """
    Generates tailored recruiter outreach messages.
    Falls back to smart offline networking notes when Gemini is offline.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an elite career coach and executive recruiter.
        Draft a high-conversion networking/outreach message for a candidate reaching out regarding this role.

        OUTREACH TYPE: {outreach_type}
        COMPANY NAME: {company_name if company_name else "the company"}
        RECIPIENT NAME / TITLE: {recipient_name if recipient_name else "Hiring Manager / Recruiter"}
        TONE: {tone}

        CANDIDATE RESUME HIGHLIGHTS:
        \"\"\"{resume_text[:2500]}\"\"\"

        TARGET JOB DESCRIPTION:
        \"\"\"{job_description[:2500]}\"\"\"

        STRICT CONSTRAINTS:
        - If outreach_type is "LinkedIn Connection Note", the final text MUST be strictly under 300 characters total.
        - If outreach_type is "Direct Hiring Manager Cold Email Pitch", include a catchy Email Subject Line and 3 punchy bullet points of quantifiable value.
        - If outreach_type is "Employee Referral Request", craft a respectful, low-friction note to a peer engineer or alumnus asking for advice and potential referral.
        - Avoid sycophancy or generic clichés. Focus on mutual value, specific relevant achievements, and clear low-friction call to action.

        Return a valid JSON object matching this schema:
        {{
            "subject_or_headline": "<subject line if email, or brief connection hook>",
            "message_body": "<exact copy-paste message text>",
            "character_count": <approx integer length of message_body>,
            "pro_tip": "<1 actionable networking tip for sending this message>"
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "message_body" in data:
            return data

    from utils.offline_heuristics import generate_offline_cold_outreach
    return generate_offline_cold_outreach(
        resume_text, job_description, outreach_type=outreach_type,
        company_name=company_name, recipient_name=recipient_name, tone=tone
    )


# ---------------------------------------------------------
# 7. LinkedIn Headline & Profile Optimizer
# ---------------------------------------------------------
def generate_linkedin_profile_content(resume_text, target_role="Software Engineer", api_key=None, model_name=None):
    """
    Generates high-converting LinkedIn Headlines and a compelling 1st-person "About" summary.
    Falls back to offline heuristics when Gemini is offline.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an executive LinkedIn personal branding strategist.
        Based on the candidate's resume, generate high-converting LinkedIn profile branding optimized for the role of '{target_role}'.

        RESUME:
        \"\"\"{resume_text[:3000]}\"\"\"

        Return a valid JSON object matching this schema:
        {{
            "headlines": [
                "<Headline 1: Keyword & Stack Heavy (e.g. Senior Full-Stack Engineer | React, Node.js, AWS | Scaling SaaS to 4M+ Users)>",
                "<Headline 2: Value & Impact Centric (e.g. AI Engineer Helping Enterprises Ship Production RAG & Microservices | Ex-DataCore)>",
                "<Headline 3: Modern & Conversational (e.g. Building Resilient Cloud Systems & Mentoring Devs | Senior Software Engineer)>"
            ],
            "about_summary": "<A compelling, authentic 3-paragraph 1st-person LinkedIn About section highlighting candidate's engineering philosophy, proudest impact, core technical toolkit, and invitation to connect>",
            "top_skills_to_pin": [<list of 5 highest-priority skills candidate should pin on their LinkedIn profile>]
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "headlines" in data:
            return data

    from utils.offline_heuristics import generate_offline_linkedin_profile
    return generate_offline_linkedin_profile(resume_text, target_role=target_role)


# ---------------------------------------------------------
# 8. Advanced Interview Coach (Seniority-Aware & STAR Evaluator)
# ---------------------------------------------------------
def generate_interview_questions(resume_text, job_description, seniority_level="Mid-Level", api_key=None, model_name=None):
    """
    Generates tailored interview questions across technical, behavioral, and situational domains.
    Falls back to offline heuristics when Gemini is offline.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an expert hiring manager and technical interviewer conducting a mock interview for a {seniority_level} role.
        Based on the candidate's resume and job description, formulate 5 targeted interview questions:
        - 2 Technical / Architecture questions matching specific technologies and projects
        - 2 Behavioral (STAR method) questions regarding teamwork, challenges, or ownership
        - 1 Situational / Role-specific scenario question

        SENIORITY LEVEL: {seniority_level}

        RESUME:
        \"\"\"{resume_text}\"\"\"

        JOB DESCRIPTION:
        \"\"\"{job_description}\"\"\"

        Your output MUST be a valid JSON array of objects:
        [
            {{
                "id": 1,
                "type": "<'Technical' | 'Behavioral' | 'Situational'>",
                "question": "<question text>",
                "interviewer_intent": "<1 sentence explaining what the interviewer is testing here>",
                "key_points_to_include": [<list of 2-3 aspects candidate should mention>]
            }}
        ]

        Return ONLY the raw JSON array.
        """
        data, _ = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, list) and len(data) > 0:
            return data

    from utils.offline_heuristics import generate_offline_interview_questions
    return generate_offline_interview_questions(resume_text, job_description, seniority_level=seniority_level)


def evaluate_interview_answer(question, user_answer, job_description, resume_text, api_key=None, model_name=None):
    """
    Evaluates candidate's answer using the STAR method rubric.
    Falls back to heuristic rubric evaluation when Gemini is offline.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are a principal tech interviewer and executive interview coach.
        Critique the candidate's answer to the following interview question using the STAR (Situation, Task, Action, Result) methodology.

        QUESTION:
        \"{question}\"

        CANDIDATE'S ANSWER:
        \"{user_answer}\"

        TARGET JOB DESCRIPTION:
        \"\"\"{job_description}\"\"\"

        CANDIDATE RESUME CONTEXT:
        \"\"\"{resume_text}\"\"\"

        Evaluate the response thoroughly and return a valid JSON object matching this schema:
        {{
            "rating": "<'Outstanding' | 'Solid Match' | 'Needs Improvement' | 'Weak'>",
            "score_total": <integer 0-100 overall score>,
            "star_breakdown": {{
                "situation_score": <integer 0-10, context setting>,
                "task_score": <integer 0-10, clear definition of the goal/challenge>,
                "action_score": <integer 0-10, depth of personal contribution, tools used, decisions>,
                "result_score": <integer 0-10, tangible outcomes, metrics, lessons learned>
            }},
            "strengths": [
                "<what the candidate articulated effectively>"
            ],
            "growth_areas": [
                "<specific missing details, vague phrasing, or weak points>"
            ],
            "sample_answer": "<a model, exemplary answer the candidate could have delivered, drawing from their background>"
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "score_total" in data:
            return data

    from utils.offline_heuristics import evaluate_offline_interview_answer
    return evaluate_offline_interview_answer(question, user_answer, job_description, resume_text)


def generate_followup_question(question, user_answer, job_description, api_key=None, model_name=None):
    """
    Generates a dynamic follow-up drill-down question based on candidate's answer.
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an interviewer in the middle of a live interview.
        The candidate just gave this response to your question.
        Ask 1 sharp, realistic follow-up question that digs deeper into their technical decision-making, trade-offs, or leadership actions.

        QUESTION:
        \"{question}\"

        CANDIDATE'S ANSWER:
        \"{user_answer}\"

        Return ONLY the single follow-up question.
        """
        data, err = call_gemini_resilient(prompt, is_json=False, api_key=api_key, model_name=model_name)
        if data and not data.startswith("Error"):
            return data

    from utils.offline_heuristics import generate_offline_followup_question
    return generate_offline_followup_question(question, user_answer, job_description)


def generate_interview_cheat_sheet(resume_text, job_description, api_key=None, model_name=None):
    """
    Generates an interview preparation cheat sheet:
    - 3 Anchor stories to highlight
    - 3 Trap/Curveball questions to anticipate
    - 4 High-impact questions to ask the interviewer
    """
    if configure_gemini(api_key):
        prompt = f"""
        You are an executive career advisor. Prepare a high-yield Interview Cheat Sheet for the candidate
        applying for this role.

        RESUME:
        \"\"\"{resume_text[:2800]}\"\"\"

        JOB DESCRIPTION:
        \"\"\"{job_description[:2800]}\"\"\"

        Return a valid JSON object matching this schema:
        {{
            "anchor_stories": [
                {{
                    "headline": "<1-line story hook, e.g. Scaling RAG pipeline latency reduction by 42%>",
                    "applicable_to": "<e.g. Performance optimization, system design, or handling ambiguous problems>",
                    "key_takeaway": "<what core competency this proves>"
                }}
            ],
            "curveball_questions_to_watch": [
                {{
                    "question": "<challenging technical or situational question>",
                    "pitfall_to_avoid": "<common mistake candidates make>",
                    "recommended_angle": "<how to frame the response successfully>"
                }}
            ],
            "questions_to_ask_interviewer": [
                "<sharp question that demonstrates deep curiosity about architecture, team culture, or roadmaps>"
            ]
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "anchor_stories" in data:
            return data

    from utils.offline_heuristics import generate_offline_interview_cheat_sheet
    return generate_offline_interview_cheat_sheet(resume_text, job_description)


# ---------------------------------------------------------
# 9. 30-Day Skill Gap & Project Learning Roadmap
# ---------------------------------------------------------
def generate_skill_gap_roadmap(missing_skills, target_role="Target Position", api_key=None, model_name=None):
    """
    Builds a personalized 4-week learning curriculum and portfolio project ideas.
    Falls back to smart curriculum generation when Gemini is offline.
    """
    skills_str = ", ".join(missing_skills) if isinstance(missing_skills, list) else str(missing_skills)

    if configure_gemini(api_key):
        prompt = f"""
        You are a principal mentor and technical career advisor.
        A candidate wants to apply for the role of '{target_role}', but their resume has identified gaps in the following skills/tools:
        {skills_str}

        Design a high-yield 30-Day Fast-Track Upskilling Roadmap and 2 portfolio project ideas to bridge these gaps.

        Return a valid JSON object matching this schema:
        {{
            "weekly_plan": [
                {{
                    "week": "Week 1: Core Fundamentals & Setup",
                    "focus": "<primary focus area>",
                    "topics": [<2-3 specific topics to learn>],
                    "deliverable": "<concrete mini-task or milestone to complete>"
                }},
                {{
                    "week": "Week 2: Deep Dive & Hands-on Practice",
                    "focus": "<primary focus area>",
                    "topics": [<2-3 specific topics to learn>],
                    "deliverable": "<concrete mini-task or milestone to complete>"
                }},
                {{
                    "week": "Week 3: Integration & Advanced Architecture",
                    "focus": "<primary focus area>",
                    "topics": [<2-3 specific topics to learn>],
                    "deliverable": "<concrete mini-task or milestone to complete>"
                }},
                {{
                    "week": "Week 4: Portfolio Project & Resume Polish",
                    "focus": "<primary focus area>",
                    "topics": [<2-3 specific topics to learn>],
                    "deliverable": "<concrete mini-task or milestone to complete>"
                }}
            ],
            "recommended_projects": [
                {{
                    "project_title": "<creative, industry-grade project title>",
                    "description": "<2-sentence project overview demonstrating the missing skills>",
                    "tech_stack": [<3-4 tools/libraries to use>],
                    "resume_bullet_preview": "<how this project can be written as an XYZ bullet point on their resume>"
                }},
                {{
                    "project_title": "<second project title>",
                    "description": "<2-sentence project overview>",
                    "tech_stack": [<3-4 tools/libraries to use>],
                    "resume_bullet_preview": "<bullet point preview>"
                }}
            ],
            "top_certifications_or_resources": [
                "<recommended official documentation, free course, or industry certification>"
            ]
        }}

        Return ONLY the raw JSON object.
        """
        data, err = call_gemini_resilient(prompt, is_json=True, api_key=api_key, model_name=model_name)
        if isinstance(data, dict) and "weekly_plan" in data:
            return data

    from utils.offline_heuristics import generate_offline_skill_gap_roadmap
    return generate_offline_skill_gap_roadmap(missing_skills, target_role=target_role)


# Backward compatibility helper for existing calls
def extract_skills_with_gemini(resume_text, api_key=None):
    """
    Extracts all skills from resume text. Returns flat list of strings.
    """
    profile = parse_full_resume_with_gemini(resume_text, api_key=api_key)
    if profile and "skills_by_category" in profile:
        flat = []
        for cat_skills in profile["skills_by_category"].values():
            if isinstance(cat_skills, list):
                flat.extend(cat_skills)
        if flat:
            return sorted(list(set(flat)))
    return []
