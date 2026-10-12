import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

from utils.resume_parser import extract_pdf, extract_docx, extract_txt
from utils.information_extractor import extract_all_contact_info
from utils.skill_extractor import extract_categorized_skills, extract_skills
from utils.ats_score import calculate_ats_score
from utils.custom_css import apply_custom_css
from utils.gemini_service import (
    SUPPORTED_MODELS,
    DEFAULT_MODEL,
    configure_gemini,
    test_gemini_connection,
    parse_full_resume_with_gemini,
    rewrite_resume_bullet,
    generate_tailored_summary,
    generate_cover_letter,
    generate_cold_outreach,
    generate_linkedin_profile_content,
    generate_interview_questions,
    evaluate_interview_answer,
    generate_followup_question,
    generate_interview_cheat_sheet,
    generate_skill_gap_roadmap,
    get_active_api_key,
    save_api_key_to_env,
    remove_saved_api_key
)
from utils.export_helper import (
    create_cover_letter_docx,
    create_ats_report_markdown,
    create_ats_report_docx,
    create_interview_prep_docx,
    create_outreach_docx,
    create_roadmap_docx,
    create_roadmap_markdown,
    create_linkedin_docx,
    SAMPLE_PROFILES
)

# ----------------------------
# Streamlit Page Configuration
# ----------------------------
st.set_page_config(
    page_title="CareerAI Pro | Resume & Career Intelligence Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# ----------------------------
# Session State Initialization
# ----------------------------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""
if "candidate_profile" not in st.session_state:
    st.session_state.candidate_profile = None
if "categorized_skills" not in st.session_state:
    st.session_state.categorized_skills = {}
if "job_desc" not in st.session_state:
    st.session_state.job_desc = ""
if "ats_analysis" not in st.session_state:
    st.session_state.ats_analysis = None
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""
if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = []
if "selected_question_idx" not in st.session_state:
    st.session_state.selected_question_idx = 0
if "interview_feedback" not in st.session_state:
    st.session_state.interview_feedback = {}
if "followup_questions" not in st.session_state:
    st.session_state.followup_questions = {}
if "interview_cheat_sheet" not in st.session_state:
    st.session_state.interview_cheat_sheet = None
if "skill_roadmap" not in st.session_state:
    st.session_state.skill_roadmap = None
if "bullet_rewrite_result" not in st.session_state:
    st.session_state.bullet_rewrite_result = None
if "tailored_summary" not in st.session_state:
    st.session_state.tailored_summary = ""
if "outreach_results" not in st.session_state:
    st.session_state.outreach_results = {}
if "linkedin_profile_data" not in st.session_state:
    st.session_state.linkedin_profile_data = None

# Navigation Page Definitions
PAGES = [
    "📄 1. Resume Intelligence",
    "📊 2. ATS Match & Radar Audit",
    "🚀 3. Bullet Rewriter & Optimizer",
    "✍️ 4. Cover Letter Studio",
    "📬 5. Recruiter Outreach & LinkedIn",
    "🗣️ 6. AI Interview Coach 2.0",
    "🎯 7. 30-Day Skill Gap Roadmap"
]

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGES[0]
if st.session_state.current_page not in PAGES:
    st.session_state.current_page = PAGES[0]
if "nav_page" not in st.session_state or st.session_state.nav_page not in PAGES:
    st.session_state.nav_page = st.session_state.current_page

# Apply navigation requested by code that runs AFTER the sidebar radio widget.
# This must happen before the widget with key="nav_page" is created.
if "pending_nav_page" in st.session_state:
    pending_page = st.session_state.pop("pending_nav_page")
    if pending_page in PAGES:
        st.session_state.current_page = pending_page
        st.session_state.nav_page = pending_page

def set_page(target_page):
    """Use as a Streamlit widget callback to change pages safely."""
    if target_page in PAGES:
        st.session_state.current_page = target_page
        st.session_state.nav_page = target_page

def sync_nav():
    st.session_state.current_page = st.session_state.nav_page

def render_step_header(current_idx):
    """
    Renders an interactive step progression bar at the top of each page.
    """
    total_pages = len(PAGES)
    steps_html = []
    for i, p in enumerate(PAGES):
        step_num = i + 1
        raw_title = p.split(". ", 1)[-1]
        words = raw_title.split(" ")
        short_title = f"{words[0]} {words[1]}" if len(words) > 1 and len(words[0]) <= 5 else words[0]
        
        if i == current_idx:
            steps_html.append(f"<span class='step-pill step-pill-active'>Step {step_num}: {short_title}</span>")
        elif i < current_idx:
            steps_html.append(f"<span class='step-pill step-pill-completed'>✔ Step {step_num}</span>")
        else:
            steps_html.append(f"<span class='step-pill'>Step {step_num}</span>")

    steps_markup = " <span style='color: #94a3b8; font-weight: bold;'>→</span> ".join(steps_html)
    st.markdown(f"<div class='step-tracker-bar'>{steps_markup}</div>", unsafe_allow_html=True)

def render_step_navigation(current_idx):
    """
    Renders joined step-by-step navigation buttons inside each page at the bottom.
    """
    total_pages = len(PAGES)
    st.markdown("<div class='step-nav-box'>", unsafe_allow_html=True)
    
    col_prev, col_status, col_next = st.columns([1.6, 2.2, 1.6])
    
    with col_prev:
        if current_idx > 0:
            prev_p = PAGES[current_idx - 1]
            prev_t = prev_p.split(". ", 1)[-1]
            st.button(
                f"⬅️ Previous: Step {current_idx}",
                key=f"bottom_prev_{current_idx}",
                on_click=set_page,
                args=(prev_p,),
                use_container_width=True,
                help=f"Back to Step {current_idx}: {prev_t}"
            )
        else:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            
    with col_status:
        pct = int(((current_idx + 1) / total_pages) * 100)
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <span style='font-weight: 700; font-size: 0.95rem;'>Step {current_idx + 1} of {total_pages}</span>
                <span style='color: #64748b; font-size: 0.85rem;'> ({pct}% Completed)</span>
                <div style='background: #e2e8f0; border-radius: 9999px; height: 6px; width: 100%; margin-top: 6px;'>
                    <div style='background: linear-gradient(90deg, #4f46e5, #06b6d4); height: 6px; border-radius: 9999px; width: {pct}%;'></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_next:
        if current_idx < total_pages - 1:
            next_p = PAGES[current_idx + 1]
            next_t = next_p.split(". ", 1)[-1]
            st.button(
                f"Next: Step {current_idx + 2} ➡️",
                key=f"bottom_next_{current_idx}",
                on_click=set_page,
                args=(next_p,),
                type="primary",
                use_container_width=True,
                help=f"Proceed to Step {current_idx + 2}: {next_t}"
            )
        else:
            st.button(
                "Start Over: Step 1 🔄",
                key=f"bottom_restart_{current_idx}",
                on_click=set_page,
                args=(PAGES[0],),
                type="primary",
                use_container_width=True,
                help="Return to Step 1: Resume Intelligence"
            )
            
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Sidebar: Control Center
# ----------------------------
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 6px 0 16px 0;'>
        <h2 style='margin:0; color:#4f46e5; font-size: 1.45rem; font-weight:800;'>⚡ CareerAI Pro</h2>
        <span style='font-size: 0.8rem; color: #64748b;'>Resume, ATS & Interview Intelligence</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Model Selector
selected_model = st.sidebar.selectbox(
    "🤖 Gemini AI Model",
    SUPPORTED_MODELS,
    index=0,
    help="Select the Gemini model powering resume parsing, ATS benchmarking, and interview coaching."
)

# API Key Config & Management
st.sidebar.markdown("### 🔑 Gemini API Key Manager")
env_key = get_active_api_key()

api_key_input = st.sidebar.text_input(
    "Enter Gemini API Key",
    value="" if not env_key else "••••••••••••••••",
    type="password",
    help="Enter your Gemini API key from Google AI Studio. Click 'Save Key' to persist it to .env across sessions."
)

# Determine effective API key
active_key = env_key if (api_key_input == "••••••••••••••••" or not api_key_input.strip()) else api_key_input.strip()

col_save, col_test = st.sidebar.columns([1, 1])
with col_save:
    if st.sidebar.button("💾 Save Key", use_container_width=True, key="btn_save_key", help="Save API Key to .env file"):
        if api_key_input.strip() and api_key_input != "••••••••••••••••":
            if save_api_key_to_env(api_key_input.strip()):
                st.sidebar.success("✅ API Key saved to .env!")
                st.rerun()
            else:
                st.sidebar.error("❌ Failed to save API Key.")
        elif env_key:
            st.sidebar.info("Key is already saved in .env.")
        else:
            st.sidebar.warning("Please enter a key first.")

with col_test:
    test_btn = st.sidebar.button("🔌 Test API", use_container_width=True, key="btn_test_key", help="Test connection to Gemini")

if test_btn:
    with st.sidebar:
        with st.spinner("Connecting to Google Gemini..."):
            ok, msg = test_gemini_connection(active_key, selected_model)
            if ok:
                st.sidebar.success(f"✅ {msg}")
            else:
                st.sidebar.error(f"❌ {msg}")

col_status, col_clear = st.sidebar.columns([1.2, 0.8])
with col_status:
    if active_key:
        st.markdown("<div style='color: #059669; font-size: 0.82rem; font-weight:600; margin-top:6px;'>🟢 Key Connected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #d97706; font-size: 0.82rem; font-weight:600; margin-top:6px;'>🟡 Offline Mode</div>", unsafe_allow_html=True)

with col_clear:
    if active_key:
        if st.sidebar.button("🗑️ Clear", use_container_width=True, key="btn_clear_key", help="Remove saved API key from .env"):
            remove_saved_api_key()
            st.sidebar.info("Saved key cleared.")
            st.rerun()

with st.sidebar.expander("❓ How to Get & Create a Free API Key", expanded=False):
    st.markdown(
        """
        1. Open [Google AI Studio](https://aistudio.google.com/app/apikey).
        2. Sign in with your Google Account.
        3. Click **"Create API Key"**.
        4. Copy the API Key.
        5. Paste it above and click **"💾 Save Key"**!
        """
    )


st.sidebar.markdown("---")

# Quick 1-Click Sample Loader
st.sidebar.subheader("🚀 Quick Test Drive")
sample_choice = st.sidebar.selectbox(
    "Load Demo Profile & Job",
    ["Select a sample...", "AI / Machine Learning Engineer", "Full-Stack Software Engineer"],
    help="Instantly test all features with pre-configured resumes and matching job descriptions."
)

if st.sidebar.button("📥 Load Selected Sample", use_container_width=True):
    if sample_choice in SAMPLE_PROFILES:
        sample = SAMPLE_PROFILES[sample_choice]
        st.session_state.resume_text = sample["resume_text"]
        st.session_state.resume_name = f"{sample['name']} (Sample Resume)"
        st.session_state.job_desc = sample["job_desc"]
        
        # Reset downstream analyses
        st.session_state.ats_analysis = None
        st.session_state.cover_letter = ""
        st.session_state.interview_questions = []
        st.session_state.interview_feedback = {}
        st.session_state.followup_questions = {}
        st.session_state.interview_cheat_sheet = None
        st.session_state.skill_roadmap = None
        st.session_state.bullet_rewrite_result = None
        st.session_state.tailored_summary = ""
        st.session_state.outreach_results = {}
        st.session_state.linkedin_profile_data = None
        
        # Trigger parsing
        if active_key:
            profile = parse_full_resume_with_gemini(sample["resume_text"], api_key=active_key, model_name=selected_model)
            st.session_state.candidate_profile = profile
        else:
            st.session_state.candidate_profile = None

        st.session_state.categorized_skills = extract_categorized_skills(sample["resume_text"], api_key=active_key, model_name=selected_model)
        set_page(PAGES[0])
        st.sidebar.success(f"Loaded {sample['name']}!")
        st.rerun()

st.sidebar.markdown("---")

# Navigation Menu
st.sidebar.subheader("🧭 Navigation")
if st.session_state.nav_page != st.session_state.current_page:
    st.session_state.nav_page = st.session_state.current_page

page = st.sidebar.radio(
    "Go to",
    PAGES,
    key="nav_page",
    on_change=sync_nav
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='font-size: 0.78rem; color: #64748b; text-align: center; line-height: 1.4;'>
        <strong>CareerAI Pro v3.5</strong><br>
        Multi-Modal AI Career Acceleration
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Main App Header
# ----------------------------
st.markdown("<div class='main-header'>CareerAI Pro</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Next-Generation Resume Intelligence, ATS Benchmarking, STAR Bullet Polisher, Recruiter Outreach & Interactive Interview Coaching</div>", unsafe_allow_html=True)

# ----------------------------
# Global Resume Ingestion Section (Upload or Direct Paste)
# ----------------------------
with st.container():
    col_up1, col_up2 = st.columns([2.3, 1.1])
    with col_up1:
        tab_file, tab_paste = st.tabs(["📁 Upload File (PDF, DOCX, TXT)", "📋 Paste Resume Text Directly"])
        
        with tab_file:
            uploaded_file = st.file_uploader(
                "Upload Resume Document",
                type=["pdf", "docx", "txt", "md"],
                help="Upload PDF, Word document, TXT, or Markdown resume."
            )
            
        with tab_paste:
            direct_text = st.text_area(
                "Paste Resume Text",
                value="" if not st.session_state.resume_text or "Sample Resume" in st.session_state.resume_name else st.session_state.resume_text,
                placeholder="Paste full plain text resume here...",
                height=130
            )
            if st.button("📥 Parse Pasted Resume", key="btn_parse_pasted"):
                if direct_text.strip():
                    st.session_state.resume_text = direct_text.strip()
                    st.session_state.resume_name = "Pasted Resume Text"
                    
                    if active_key:
                        profile = parse_full_resume_with_gemini(st.session_state.resume_text, api_key=active_key, model_name=selected_model)
                        st.session_state.candidate_profile = profile
                    else:
                        st.session_state.candidate_profile = None

                    st.session_state.categorized_skills = extract_categorized_skills(st.session_state.resume_text, api_key=active_key, model_name=selected_model)
                    
                    st.session_state.ats_analysis = None
                    st.session_state.cover_letter = ""
                    st.session_state.interview_questions = []
                    st.session_state.interview_feedback = {}
                    st.session_state.followup_questions = {}
                    st.session_state.interview_cheat_sheet = None
                    st.session_state.skill_roadmap = None
                    st.session_state.bullet_rewrite_result = None
                    st.session_state.tailored_summary = ""
                    st.session_state.outreach_results = {}
                    st.session_state.linkedin_profile_data = None
                    st.success("✅ Pasted resume parsed successfully!")
                    st.rerun()

    with col_up2:
        if st.session_state.resume_text:
            char_count = len(st.session_state.resume_text)
            word_count = len(st.session_state.resume_text.split())
            prof = st.session_state.candidate_profile
            detected_name = prof.get("full_name") if (prof and prof.get("full_name")) else None
            if not detected_name:
                try:
                    detected_name = extract_all_contact_info(st.session_state.resume_text).get("full_name")
                except Exception:
                    detected_name = None
            
            name_badge = f"<div class='candidate-name' style='font-size: 1.15rem; font-weight:800; display:inline-block;'>👤 {detected_name}</div>" if detected_name else ""
            st.markdown(
                f"""
                <div class='info-card' style='padding: 0.85rem 1.1rem; margin-top: 1rem;'>
                    <strong>Active Candidate:</strong><br>
                    {name_badge}
                    <div style='color: #4f46e5; font-weight:700; font-size: 0.92rem; margin-top:2px;'>📄 {st.session_state.resume_name}</div>
                    <span style='color: #64748b; font-size: 0.8rem;'>{word_count} words | {char_count} chars</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class='info-card' style='padding: 0.85rem 1.1rem; margin-top: 1rem; text-align: center; border-style: dashed;'>
                    <span style='color: #64748b; font-size: 0.9rem;'>No active resume. Upload a file, paste text, or load a demo sample from the sidebar.</span>
                </div>
                """,
                unsafe_allow_html=True
            )

# Handle file upload processing
if uploaded_file and uploaded_file.name != st.session_state.resume_name:
    with st.spinner("Parsing resume content..."):
        file_ext = uploaded_file.name.split(".")[-1].lower()
        if file_ext == "pdf":
            parsed_text = extract_pdf(uploaded_file)
        elif file_ext in ["docx", "doc"]:
            parsed_text = extract_docx(uploaded_file)
        elif file_ext in ["txt", "md"]:
            parsed_text = extract_txt(uploaded_file)
        else:
            st.error("Unsupported file format.")
            parsed_text = ""

        if parsed_text and not parsed_text.startswith("Error"):
            st.session_state.resume_text = parsed_text
            st.session_state.resume_name = uploaded_file.name
            
            # Gemini Full Profile Parsing
            if active_key:
                profile = parse_full_resume_with_gemini(parsed_text, api_key=active_key, model_name=selected_model)
                st.session_state.candidate_profile = profile
            else:
                st.session_state.candidate_profile = None

            # Categorized Skills
            st.session_state.categorized_skills = extract_categorized_skills(parsed_text, api_key=active_key, model_name=selected_model)
            
            # Reset Downstream State
            st.session_state.ats_analysis = None
            st.session_state.cover_letter = ""
            st.session_state.interview_questions = []
            st.session_state.interview_feedback = {}
            st.session_state.followup_questions = {}
            st.session_state.interview_cheat_sheet = None
            st.session_state.skill_roadmap = None
            st.session_state.bullet_rewrite_result = None
            st.session_state.tailored_summary = ""
            st.session_state.outreach_results = {}
            st.session_state.linkedin_profile_data = None

            # Defer changing the radio widget's state until the next run,
            # before the widget is instantiated.
            st.session_state.current_page = PAGES[0]
            st.session_state.pending_nav_page = PAGES[0]
            st.success("✅ Resume parsed and intelligence profile generated!")
            st.rerun()

st.markdown("---")

# ==============================================================================
# PAGE 1: RESUME INTELLIGENCE & STRUCTURED PROFILE
# ==============================================================================
if page == "📄 1. Resume Intelligence":
    st.markdown("<div class='section-title'>📄 Structured Resume Intelligence Profile</div>", unsafe_allow_html=True)
    render_step_header(0)
    
    if not st.session_state.resume_text:
        st.info("💡 Upload your resume or load a sample from the sidebar to inspect candidate intelligence.")
    else:
        profile = st.session_state.candidate_profile
        offline_contact = extract_all_contact_info(st.session_state.resume_text)

        cand_name = profile.get("full_name") if (profile and profile.get("full_name")) else offline_contact["full_name"]
        headline = profile.get("headline", "Professional Candidate") if profile else "Professional Candidate"
        
        contact = profile.get("contact", {}) if profile else offline_contact
        email = contact.get("email", offline_contact["email"])
        phone = contact.get("phone", offline_contact["phone"])
        loc = contact.get("location", offline_contact.get("location", "Not Specified"))
        linkedin = contact.get("linkedin", offline_contact["linkedin"])
        github = contact.get("github", offline_contact["github"])
        portfolio = contact.get("portfolio", offline_contact["portfolio"])
        summary = profile.get("summary") if profile else f"Offline Heuristic Summary: Detected {offline_contact.get('estimated_exp_years', 'several')} estimated years of background. Connect Gemini API in the sidebar for AI executive synthesis."

        # Hero Profile Card
        st.markdown(
            f"""
            <div class='candidate-hero'>
                <div style='display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;'>
                    <div>
                        <h2 class='candidate-name' style='margin: 0; font-size: 2.1rem; font-weight:800;'>{cand_name}</h2>
                        <div style='color: #4f46e5; font-weight:600; font-size: 1.05rem; margin-top: 2px;'>{headline}</div>
                    </div>
                </div>
                <div style='display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 1rem; font-size: 0.9rem; color: #475569;'>
                    <span>📧 <strong>Email:</strong> {email}</span>
                    <span>📱 <strong>Phone:</strong> {phone}</span>
                    <span>📍 <strong>Location:</strong> {loc}</span>
                    <span>💼 <strong>LinkedIn:</strong> {f"<a href='{linkedin}' target='_blank'>{linkedin}</a>" if linkedin != "Not Found" else "Not Found"}</span>
                    <span>💻 <strong>GitHub:</strong> {f"<a href='{github}' target='_blank'>{github}</a>" if github != "Not Found" else "Not Found"}</span>
                    <span>🌐 <strong>Portfolio:</strong> {f"<a href='{portfolio}' target='_blank'>{portfolio}</a>" if portfolio != "Not Found" else "Not Found"}</span>
                </div>
                <div style='margin-top: 1.1rem; padding-top: 1rem; border-top: 1px solid #cbd5e1; font-size: 0.95rem; line-height: 1.5;'>
                    <strong>Executive Synthesis:</strong> {summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_sk, col_exp = st.columns([1.2, 1])

        # Categorized Skills Display
        with col_sk:
            st.markdown("### 🛠️ Categorized Skills Taxonomy")
            cats = st.session_state.categorized_skills
            if cats:
                cat_badges_class = {
                    "Programming Languages": "badge-lang",
                    "Frameworks & Libraries": "badge-framework",
                    "Cloud, DevOps & Tools": "badge-cloud",
                    "Databases & Storage": "badge-data",
                    "AI, ML & Data Science": "badge-ai",
                    "Architecture & Methodologies": "badge-arch"
                }
                
                total_skills_count = sum(len(v) for v in cats.values())
                st.caption(f"Detected {total_skills_count} skills across {len(cats)} categories:")

                for cat_name, skill_list in cats.items():
                    if skill_list:
                        badge_cls = cat_badges_class.get(cat_name, "badge-arch")
                        badges_html = "".join([f"<span class='skill-badge {badge_cls}'>{s}</span>" for s in skill_list])
                        st.markdown(
                            f"""
                            <div style='margin-bottom: 0.85rem;'>
                                <div style='font-size: 0.85rem; font-weight:700; color:#475569; margin-bottom: 4px;'>{cat_name} ({len(skill_list)})</div>
                                {badges_html}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.warning("No skills detected from the resume text.")

        # Career Highlights / Education Display
        with col_exp:
            st.markdown("### 🎓 Education & Career Highlights")
            if profile and profile.get("education"):
                st.markdown("#### Degrees & Credentials")
                for edu in profile["education"]:
                    st.markdown(
                        f"""
                        <div class='info-card' style='padding: 0.75rem 1rem; margin-bottom: 0.6rem;'>
                            <strong>{edu.get('degree', 'Degree')}</strong><br>
                            <span style='color: #64748b; font-size: 0.85rem;'>{edu.get('institution', 'Institution')} | {edu.get('year', 'Year')}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            if profile and profile.get("work_experience_highlights"):
                st.markdown("#### Experience Highlights")
                for exp in profile["work_experience_highlights"]:
                    achieve_html = "".join([f"<li>{a}</li>" for a in exp.get("key_achievements", [])])
                    st.markdown(
                        f"""
                        <div class='info-card' style='padding: 0.75rem 1rem; margin-bottom: 0.6rem;'>
                            <div style='display:flex; justify-content:space-between;'>
                                <strong>{exp.get('role', 'Role')}</strong>
                                <span style='font-size: 0.8rem; color:#64748b;'>{exp.get('duration', '')}</span>
                            </div>
                            <span style='color: #4f46e5; font-size: 0.85rem; font-weight:600;'>{exp.get('company', 'Company')}</span>
                            <ul style='margin: 0.4rem 0 0 0; padding-left: 1.2rem; font-size: 0.85rem;'>
                                {achieve_html}
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            if not profile:
                st.info("💡 Connect a Gemini API key in the sidebar to extract comprehensive career history and achievements.")

        # Raw Text View
        st.markdown("---")
        with st.expander("📄 View Parsed Raw Resume Text", expanded=False):
            st.text_area("Plain Text Content", st.session_state.resume_text, height=300)

    render_step_navigation(0)


# ==============================================================================
# PAGE 2: ATS MATCH & RADAR AUDIT
# ==============================================================================
elif page == "📊 2. ATS Match & Radar Audit":
    st.markdown("<div class='section-title'>📊 ATS Multi-Dimensional Radar & Alignment Audit</div>", unsafe_allow_html=True)
    render_step_header(1)
    
    if not st.session_state.resume_text:
        st.info("💡 Upload your resume or load a sample from the sidebar to benchmark ATS compatibility.")
    else:
        col_jd, col_score = st.columns([1.1, 1.3])
        
        with col_jd:
            st.markdown("### 📋 Target Job Description")
            job_desc = st.text_area(
                "Paste the Target Job Description below",
                value=st.session_state.job_desc,
                placeholder="Paste requirements, tech stack, and responsibilities...",
                height=280
            )
            st.session_state.job_desc = job_desc
            
            btn_analyze = st.button("🚀 Run Deep ATS Benchmark", use_container_width=True)

        with col_score:
            st.markdown("### 🎯 ATS Benchmark Results")
            
            if btn_analyze:
                if not job_desc.strip():
                    st.warning("⚠️ Please provide a target job description to match against.")
                else:
                    with st.spinner("Evaluating candidate alignment with AI..."):
                        analysis = calculate_ats_score(
                            st.session_state.resume_text,
                            job_desc,
                            api_key=active_key,
                            model_name=selected_model
                        )
                        st.session_state.ats_analysis = analysis

            if st.session_state.ats_analysis:
                analysis = st.session_state.ats_analysis
                
                if "error" in analysis:
                    st.error(analysis["error"])
                else:
                    overall = analysis.get("score_overall", 0)
                    skills_s = analysis.get("score_skills", 0)
                    exp_s = analysis.get("score_experience", 0)
                    format_s = analysis.get("score_formatting", 0)
                    impact_s = analysis.get("score_impact", 0)
                    edu_s = analysis.get("score_education", 0)
                    
                    # Spider / Radar Chart
                    categories = ['Skills Alignment', 'Experience Depth', 'Quantified Impact', 'ATS Formatting', 'Education & Certs']
                    values = [skills_s, exp_s, impact_s, format_s, edu_s]

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        fillcolor='rgba(79, 70, 229, 0.25)',
                        line=dict(color='#4f46e5', width=2),
                        name='Candidate Profile'
                    ))

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9)),
                            angularaxis=dict(tickfont=dict(size=10, color='#334155'))
                        ),
                        showlegend=False,
                        height=280,
                        margin=dict(l=30, r=30, t=20, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Score Badge Card
                    if overall >= 80:
                        st.success(f"🚀 **Outstanding Fit!** Overall ATS Score: **{overall}%** — High likelihood of clearing screening filters.")
                    elif overall >= 65:
                        st.info(f"👍 **Solid Candidate Match!** Overall ATS Score: **{overall}%** — Review the gap analysis to boost your ranking.")
                    else:
                        st.warning(f"⚠️ **Gaps Identified.** Overall ATS Score: **{overall}%** — Significant optimization recommended before applying.")
            else:
                st.info("Paste a Job Description on the left and click 'Run Deep ATS Benchmark'.")

        # Detailed Insights, Gaps & Checklist Tabs
        if st.session_state.ats_analysis and "error" not in st.session_state.ats_analysis:
            analysis = st.session_state.ats_analysis
            st.markdown("---")
            
            tab_summary, tab_keywords, tab_audit, tab_tips = st.tabs([
                "💡 Executive Summary & Strengths",
                "🔍 Keyword & Competency Gap",
                "📋 Section-by-Section Health Audit",
                "🚀 Optimization Checklist & Report"
            ])

            with tab_summary:
                st.markdown("#### Executive Match Assessment")
                st.info(analysis.get("executive_summary", "Comprehensive candidate alignment evaluation."))

                st.markdown("#### Key Profile Strengths")
                strengths = analysis.get("strengths", [])
                if strengths:
                    for s in strengths:
                        st.markdown(f"<div class='strength-box'>✔ {s}</div>", unsafe_allow_html=True)
                else:
                    st.write("No specific matching strengths returned.")

            with tab_keywords:
                kw_data = analysis.get("keyword_analysis", {})
                matched_kw = kw_data.get("matched_keywords", [])
                missing_must = kw_data.get("missing_must_have", [])
                missing_nice = kw_data.get("missing_nice_to_have", [])

                col_k1, col_k2, col_k3 = st.columns(3)
                
                with col_k1:
                    st.markdown(f"##### ✅ Matched ({len(matched_kw)})")
                    if matched_kw:
                        for m in matched_kw:
                            st.markdown(f"<div class='strength-box' style='padding: 0.5rem 0.75rem; font-size:0.85rem;'>✔ {m}</div>", unsafe_allow_html=True)
                    else:
                        st.write("None detected.")

                with col_k2:
                    st.markdown(f"##### ❌ Critical Missing ({len(missing_must)})")
                    if missing_must:
                        for mm in missing_must:
                            st.markdown(f"<div class='missing-box' style='border-left-color: #ef4444; background-color: #fef2f2; color: #991b1b; padding: 0.5rem 0.75rem; font-size:0.85rem;'>❌ {mm}</div>", unsafe_allow_html=True)
                    else:
                        st.write("No critical gaps detected!")

                with col_k3:
                    st.markdown(f"##### ⚠️ Preferred Missing ({len(missing_nice)})")
                    if missing_nice:
                        for mn in missing_nice:
                            st.markdown(f"<div class='missing-box' style='padding: 0.5rem 0.75rem; font-size:0.85rem;'>⚠️ {mn}</div>", unsafe_allow_html=True)
                    else:
                        st.write("No secondary gaps detected!")

            with tab_audit:
                st.markdown("#### Section-by-Section ATS Readiness Checklist")
                audit_items = analysis.get("section_audit", [])
                if audit_items:
                    for item in audit_items:
                        status = item.get("status", "Pass")
                        status_class = "status-pill-pass" if status == "Pass" else "status-pill-warn" if status == "Warning" else "status-pill-critical"
                        st.markdown(
                            f"""
                            <div class='info-card' style='display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.1rem; margin-bottom: 0.6rem;'>
                                <div>
                                    <strong>{item.get('section')}</strong><br>
                                    <span style='font-size: 0.85rem; color: #64748b;'>{item.get('finding')}</span>
                                </div>
                                <div>
                                    <span class='{status_class}'>{status}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.write("Standard formatting audit not available.")

            with tab_tips:
                st.markdown("#### Actionable Optimization Roadmap")
                tips = analysis.get("optimization_tips", [])
                if tips:
                    for t in tips:
                        st.markdown(f"<div class='tip-box'>💡 {t}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
                cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
                
                col_d_md, col_d_doc = st.columns(2)
                with col_d_md:
                    report_md = create_ats_report_markdown(analysis, candidate_name=cand_name)
                    st.download_button(
                        label="📥 Download ATS Report (.md)",
                        data=report_md,
                        file_name="ATS_Audit_Report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col_d_doc:
                    report_docx = create_ats_report_docx(analysis, candidate_name=cand_name)
                    st.download_button(
                        label="📄 Download ATS Report (.docx)",
                        data=report_docx,
                        file_name="ATS_Audit_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )

    render_step_navigation(1)


# ==============================================================================
# PAGE 3: AI RESUME OPTIMIZER (STAR BULLET REWRITER)
# ==============================================================================
elif page == "🚀 3. Bullet Rewriter & Optimizer":
    st.markdown("<div class='section-title'>🚀 AI Resume Optimizer & Bullet Polisher</div>", unsafe_allow_html=True)
    render_step_header(2)
    
    st.markdown(
        """
        Transform weak, passive resume bullet points into **Google/XYZ formula** accomplishments: 
        *Accomplished [X], as measured by [Y], by doing [Z]*.
        """
    )

    col_rew1, col_rew2 = st.columns([1, 1.2])

    with col_rew1:
        st.markdown("### ✏️ Input Bullet Point")
        default_bullet = "Responsible for managing the team's database and writing queries."
        bullet_input = st.text_area(
            "Enter any bullet point from your resume:",
            value=default_bullet,
            height=120,
            help="Paste a bullet point you want to upgrade with measurable metrics and action verbs."
        )

        job_ctx = st.text_input(
            "Target Skills / Keywords to infuse (optional):",
            value="PostgreSQL, Query Optimization, Latency reduction, AWS RDS",
            help="Keywords or technologies you want the rewritten bullet to emphasize."
        )

        btn_rewrite = st.button("✨ Polish & Rewrite Bullet", use_container_width=True)

        if btn_rewrite:
            if not bullet_input.strip():
                st.warning("Please provide a bullet point to rewrite.")
            else:
                with st.spinner("Polishing bullet point with Google XYZ formula..."):
                    res = rewrite_resume_bullet(
                        bullet_input,
                        job_context=job_ctx,
                        api_key=active_key,
                        model_name=selected_model
                    )
                    st.session_state.bullet_rewrite_result = res

    with col_rew2:
        st.markdown("### 💎 AI-Optimized Variations")
        res = st.session_state.bullet_rewrite_result
        if res:
            if res.get("is_offline"):
                st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Heuristics (Add API Key for GenAI)</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Optimized</span>", unsafe_allow_html=True)
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown(f"**Critique:** *{res.get('critique', '')}*")
                for var in res.get("variations", []):
                    style = var.get("style", "Optimized")
                    rewritten = var.get("rewritten", "")
                    highlight = var.get("highlight", "")
                    st.markdown(
                        f"""
                        <div class='rewrite-card'>
                            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;'>
                                <span style='font-size: 0.8rem; font-weight:700; color: #4f46e5; text-transform:uppercase;'>{style}</span>
                                <span style='font-size: 0.75rem; color: #059669; font-weight:600;'>{highlight}</span>
                            </div>
                            <div style='font-size: 0.95rem; font-weight:500; margin-bottom: 8px;'>• {rewritten}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.code(f"• {rewritten}", language="text")
        else:
            st.info("Enter a bullet point on the left and click 'Polish & Rewrite Bullet' to generate high-converting variations.")

    # Executive Summary Generator
    st.markdown("---")
    st.markdown("### 🎯 Tailored Professional Summary Generator")
    st.caption("Generate a tailored 3-4 sentence professional summary aligned directly with your target role.")
    
    if st.button("📝 Generate Tailored Summary for Active Job", use_container_width=False):
        if not st.session_state.resume_text:
            st.warning("Please upload a resume first.")
        elif not st.session_state.job_desc:
            st.warning("Please provide a Job Description in tab 2.")
        else:
            with st.spinner("Synthesizing tailored executive summary..."):
                summary = generate_tailored_summary(
                    st.session_state.resume_text,
                    st.session_state.job_desc,
                    api_key=active_key,
                    model_name=selected_model
                )
                st.session_state.tailored_summary = summary

    if st.session_state.tailored_summary:
        st.text_area("Tailored Executive Summary", st.session_state.tailored_summary, height=120)

    render_step_navigation(2)


# ==============================================================================
# PAGE 4: COVER LETTER STUDIO
# ==============================================================================
elif page == "✍️ 4. Cover Letter Studio":
    st.markdown("<div class='section-title'>✍️ AI Cover Letter Studio</div>", unsafe_allow_html=True)
    render_step_header(3)
    
    if not st.session_state.resume_text:
        st.info("💡 Upload your resume to begin crafting a tailored cover letter.")
    else:
        col_cl_in, col_cl_out = st.columns([1, 1.4])

        with col_cl_in:
            st.markdown("### 📋 Cover Letter Customization")
            
            job_desc_cl = st.text_area(
                "Job Description",
                value=st.session_state.job_desc,
                placeholder="Paste the target job description...",
                height=180,
                key="cl_jd_box"
            )
            st.session_state.job_desc = job_desc_cl

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                company_name = st.text_input("Company Name", placeholder="e.g. Stripe, Google, Airbnb")
                tone = st.selectbox("Tone of Voice", ["Professional", "Executive", "Enthusiastic", "Technical"])
            with col_c2:
                hiring_manager = st.text_input("Hiring Manager", placeholder="e.g. Engineering Lead")
                length_choice = st.selectbox("Target Length", ["Standard (350 words)", "Short (250 words)", "Comprehensive (450 words)"])

            focus_area = st.text_input("Special Focus Area / Story to Highlight", placeholder="e.g. Scaling microservices, cloud cost reduction")

            btn_gen_cl = st.button("✨ Draft Personalized Cover Letter", use_container_width=True)

        with col_cl_out:
            st.markdown("### ✉️ Live Cover Letter Draft")
            
            if btn_gen_cl:
                if not job_desc_cl.strip():
                    st.warning("⚠️ A job description is required to tailor the cover letter.")
                else:
                    spinner_text = "Generating tailored cover letter with Gemini..." if active_key else "Crafting personalized cover letter with smart offline engine..."
                    with st.spinner(spinner_text):
                        letter = generate_cover_letter(
                            st.session_state.resume_text,
                            job_desc_cl,
                            tone=tone,
                            company_name=company_name,
                            hiring_manager=hiring_manager,
                            focus_area=focus_area,
                            length=length_choice,
                            api_key=active_key,
                            model_name=selected_model
                        )
                        st.session_state.cover_letter = letter

            if st.session_state.cover_letter:
                if active_key:
                    st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Draft</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Tailored Draft</span>", unsafe_allow_html=True)
                edited_letter = st.text_area("Edit Draft", st.session_state.cover_letter, height=360)
                st.session_state.cover_letter = edited_letter

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
                    docx_buffer = create_cover_letter_docx(edited_letter, candidate_name=cand_name)
                    st.download_button(
                        label="📄 Download Word Document (.docx)",
                        data=docx_buffer,
                        file_name="Cover_Letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                with col_d2:
                    st.download_button(
                        label="📝 Download Plain Text (.txt)",
                        data=edited_letter,
                        file_name="Cover_Letter.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.info("Configure settings on the left and click 'Draft Personalized Cover Letter' to generate.")

    render_step_navigation(3)


# ==============================================================================
# PAGE 5: RECRUITER OUTREACH & LINKEDIN STUDIO
# ==============================================================================
elif page == "📬 5. Recruiter Outreach & LinkedIn":
    st.markdown("<div class='section-title'>📬 Recruiter Outreach & LinkedIn Personal Branding</div>", unsafe_allow_html=True)
    render_step_header(4)

    if not st.session_state.resume_text:
        st.info("💡 Upload your resume to create copy-ready networking messages and optimized LinkedIn content.")
    else:
        tab_outreach, tab_linkedin = st.tabs(["✉️ Recruiter & Networking Messages", "💼 LinkedIn Profile Optimizer"])

        with tab_outreach:
            col_o1, col_o2 = st.columns([1, 1.3])

            with col_o1:
                st.markdown("### 🎯 Message Configuration")
                outreach_type = st.selectbox(
                    "Outreach Channel / Format",
                    [
                        "LinkedIn Connection Note (<300 chars)",
                        "Recruiter InMail / Message",
                        "Employee Referral Request",
                        "Direct Hiring Manager Cold Email Pitch"
                    ]
                )
                company_o = st.text_input("Target Company", placeholder="e.g. Anthropic, Datadog", key="outreach_company")
                recipient_o = st.text_input("Recipient Name or Role", placeholder="e.g. Sarah Jenkins (Tech Recruiter)", key="outreach_recipient")
                tone_o = st.selectbox("Tone", ["Professional & Direct", "Warm & Conversational", "High Energy", "Executive"])

                btn_gen_outreach = st.button("🚀 Draft Outreach Message", use_container_width=True)

                if btn_gen_outreach:
                    spinner_text = "Crafting high-conversion networking message..." if active_key else "Generating copy-ready networking message with smart offline engine..."
                    with st.spinner(spinner_text):
                        res = generate_cold_outreach(
                            st.session_state.resume_text,
                            st.session_state.job_desc,
                            outreach_type=outreach_type,
                            company_name=company_o,
                            recipient_name=recipient_o,
                            tone=tone_o,
                            api_key=active_key,
                            model_name=selected_model
                        )
                        st.session_state.outreach_results[outreach_type] = res

            with col_o2:
                st.markdown("### 📋 Copy-Ready Message")
                active_res = st.session_state.outreach_results.get(outreach_type)
                if active_res:
                    if active_res.get("is_offline"):
                        st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Tailored Message</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Tailored</span>", unsafe_allow_html=True)
                    if "error" in active_res:
                        st.error(active_res["error"])
                    else:
                        subject = active_res.get("subject_or_headline", "")
                        body = active_res.get("message_body", "")
                        tip = active_res.get("pro_tip", "")
                        char_c = active_res.get("character_count", len(body))

                        if subject:
                            st.markdown(f"**Subject:** `{subject}`")

                        st.text_area("Message Body (Copy-Ready)", body, height=180, key=f"body_{outreach_type}")
                        
                        st.caption(f"Character Count: ~{char_c} characters")
                        if tip:
                            st.markdown(f"<div class='tip-box'>💡 <strong>Pro-Tip:</strong> {tip}</div>", unsafe_allow_html=True)

                        # Download Docx
                        cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
                        outreach_list = [{
                            "type": outreach_type,
                            "subject": subject,
                            "message": body,
                            "tip": tip
                        }]
                        doc_buf = create_outreach_docx(outreach_list, candidate_name=cand_name)
                        st.download_button(
                            "📥 Download Outreach Note (.docx)",
                            data=doc_buf,
                            file_name=f"Outreach_{outreach_type[:15].replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                else:
                    st.info("Select message format on the left and click 'Draft Outreach Message' to generate.")

        with tab_linkedin:
            col_l1, col_l2 = st.columns([1, 1.3])

            with col_l1:
                st.markdown("### 💼 Profile Branding Settings")
                target_role_li = st.text_input(
                    "Target Job Title",
                    value=st.session_state.candidate_profile.get("headline", "Senior Software Engineer") if st.session_state.candidate_profile else "Senior Software Engineer"
                )
                btn_gen_li = st.button("✨ Generate Optimized LinkedIn Profile", use_container_width=True)

                if btn_gen_li:
                    spinner_text = "Optimizing LinkedIn Headlines and About summary..." if active_key else "Generating LinkedIn branding kit with smart offline engine..."
                    with st.spinner(spinner_text):
                        li_data = generate_linkedin_profile_content(
                            st.session_state.resume_text,
                            target_role=target_role_li,
                            api_key=active_key,
                            model_name=selected_model
                        )
                        st.session_state.linkedin_profile_data = li_data

            with col_l2:
                st.markdown("### 🌟 Optimized Profile Content")
                li_res = st.session_state.linkedin_profile_data
                if li_res:
                    if li_res.get("is_offline"):
                        st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Branding Kit</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Branding Kit</span>", unsafe_allow_html=True)
                    if "error" in li_res:
                        st.error(li_res["error"])
                    else:
                        st.markdown("#### High-Converting Headlines (Pick One):")
                        for idx, h in enumerate(li_res.get("headlines", []), 1):
                            st.code(h, language="text")

                        st.markdown("#### 1st-Person LinkedIn 'About' Summary:")
                        st.text_area("About Section", li_res.get("about_summary", ""), height=220)

                        st.markdown("#### 📌 Top 5 Skills to Feature on Profile:")
                        pinned_badges = "".join([f"<span class='skill-badge badge-lang'>{s}</span>" for s in li_res.get("top_skills_to_pin", [])])
                        st.markdown(f"<div>{pinned_badges}</div>", unsafe_allow_html=True)

                        st.markdown("---")
                        col_li_d1, col_li_d2 = st.columns(2)
                        cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
                        with col_li_d1:
                            li_docx = create_linkedin_docx(li_res, candidate_name=cand_name, target_role=target_role_li)
                            st.download_button(
                                "📥 Download Branding Kit (.docx)",
                                data=li_docx,
                                file_name="LinkedIn_Profile_Kit.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        with col_li_d2:
                            li_txt = f"LinkedIn Headlines for {cand_name}:\n" + "\n".join(li_res.get("headlines", [])) + f"\n\nAbout Section:\n{li_res.get('about_summary', '')}\n\nTop Skills to Pin:\n" + ", ".join(li_res.get("top_skills_to_pin", []))
                            st.download_button(
                                "📝 Download Branding Kit (.txt)",
                                data=li_txt,
                                file_name="LinkedIn_Profile_Kit.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                else:
                    st.info("Click 'Generate Optimized LinkedIn Profile' to receive tailored headlines, an About section, and recommended skills to pin.")

    render_step_navigation(4)


# ==============================================================================
# PAGE 6: AI INTERVIEW COACH 2.0 (STAR EVALUATOR & FOLLOW-UPS)
# ==============================================================================
elif page == "🗣️ 6. AI Interview Coach 2.0":
    st.markdown("<div class='section-title'>🗣️ AI Mock Interview Coach 2.0</div>", unsafe_allow_html=True)
    render_step_header(5)
    
    if not st.session_state.resume_text:
        st.info("💡 Upload your resume to start practicing tailored interview questions.")
    else:
        col_iq1, col_iq2 = st.columns([1, 1.2])

        with col_iq1:
            st.markdown("### ❓ Practice Sandbox")
            
            job_desc_ic = st.text_area(
                "Target Job Description",
                value=st.session_state.job_desc,
                placeholder="Paste the job description...",
                height=130,
                key="ic_jd_box"
            )
            st.session_state.job_desc = job_desc_ic

            seniority = st.selectbox(
                "Select Seniority Level:",
                ["Mid-Level", "Junior / Entry-Level", "Senior Engineer", "Staff / Lead Engineer"],
                help="Calibrates the depth, complexity, and behavioral scrutiny of generated questions."
            )

            btn_gen_q = st.button("🎯 Generate Tailored Questions", use_container_width=True)

            if btn_gen_q:
                if not job_desc_ic.strip():
                    st.warning("⚠️ Please provide a job description.")
                else:
                    spinner_text = "Analyzing candidate background and generating questions with Gemini..." if active_key else "Generating interview scenarios with smart offline engine..."
                    with st.spinner(spinner_text):
                        qs = generate_interview_questions(
                            st.session_state.resume_text,
                            job_desc_ic,
                            seniority_level=seniority,
                            api_key=active_key,
                            model_name=selected_model
                        )
                        st.session_state.interview_questions = qs
                        st.session_state.interview_feedback = {}
                        st.session_state.followup_questions = {}
                        st.session_state.selected_question_idx = 0

            if st.session_state.interview_questions:
                q_list = st.session_state.interview_questions
                q_labels = [f"Q{q.get('id', i+1)} [{q.get('type', 'General')}]: {q.get('question', '')[:65]}..." for i, q in enumerate(q_list)]

                selected_q_idx = st.selectbox(
                    "Select Question:",
                    options=range(len(q_labels)),
                    format_func=lambda i: q_labels[i],
                    index=st.session_state.selected_question_idx
                )
                st.session_state.selected_question_idx = selected_q_idx
                current_q = q_list[selected_q_idx]

                st.markdown(
                    f"""
                    <div style='background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 1rem; margin: 0.8rem 0;'>
                        <div style='font-size: 0.78rem; font-weight:700; color: #4f46e5; text-transform:uppercase;'>Type: {current_q.get('type', 'General')}</div>
                        <div style='font-size: 1.05rem; font-weight:700; margin: 4px 0;'>"{current_q.get('question')}"</div>
                        <div style='font-size: 0.82rem; color: #64748b; margin-top: 6px;'>🎯 <strong>Interviewer Intent:</strong> {current_q.get('interviewer_intent', 'Tests domain mastery and problem-solving.')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                user_ans = st.text_area(
                    "Your Response (STAR Method recommended):",
                    placeholder="Structure your answer with: Situation, Task, Action, and Result...",
                    height=180,
                    key=f"ans_{current_q.get('id', selected_q_idx)}"
                )

                btn_eval = st.button("📊 Evaluate Response (STAR Rubric)", use_container_width=True)

                if btn_eval:
                    if not user_ans.strip():
                        st.warning("Please type your response before evaluating.")
                    else:
                        spinner_text = "Critiquing response against STAR criteria with Gemini..." if active_key else "Evaluating response against STAR rubric heuristics..."
                        with st.spinner(spinner_text):
                            feedback = evaluate_interview_answer(
                                current_q.get('question'),
                                user_ans,
                                job_desc_ic,
                                st.session_state.resume_text,
                                api_key=active_key,
                                model_name=selected_model
                            )
                            st.session_state.interview_feedback[current_q.get('id', selected_q_idx)] = feedback

                # Follow-up Question Trigger
                if current_q.get('id', selected_q_idx) in st.session_state.interview_feedback:
                    st.markdown("---")
                    if st.button("🔄 Generate Live Interviewer Follow-up Question", use_container_width=True):
                        with st.spinner("Generating follow-up question..."):
                            followup = generate_followup_question(
                                current_q.get('question'),
                                user_ans,
                                job_desc_ic,
                                api_key=active_key,
                                model_name=selected_model
                            )
                            st.session_state.followup_questions[current_q.get('id', selected_q_idx)] = followup

                    if current_q.get('id', selected_q_idx) in st.session_state.followup_questions:
                        st.markdown(
                            f"""
                            <div class='tip-box' style='margin-top: 0.8rem;'>
                                <strong>🗣️ Interviewer Drill-down Follow-up:</strong><br>
                                "{st.session_state.followup_questions[current_q.get('id', selected_q_idx)]}"
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.info("Click 'Generate Tailored Questions' to load interview scenarios calibrated to the job.")

        with col_iq2:
            st.markdown("### 📊 STAR Rubric Feedback & Model Answer")
            if st.session_state.interview_questions:
                current_id = st.session_state.interview_questions[st.session_state.selected_question_idx].get('id', st.session_state.selected_question_idx)
                
                if current_id in st.session_state.interview_feedback:
                    eval_res = st.session_state.interview_feedback[current_id]
                    if eval_res.get("is_offline"):
                        st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Rubric Critique</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Evaluation</span>", unsafe_allow_html=True)
                    if "error" in eval_res:
                        st.error(eval_res["error"])
                    else:
                        rating = eval_res.get("rating", "Solid Match")
                        score_total = eval_res.get("score_total", 75)
                        star = eval_res.get("star_breakdown", {})
                        
                        s_score = star.get("situation_score", 7)
                        t_score = star.get("task_score", 7)
                        a_score = star.get("action_score", 7)
                        r_score = star.get("result_score", 7)

                        # STAR Sub-Scores Grid
                        st.markdown(
                            f"""
                            <div class='candidate-hero' style='padding: 1rem 1.25rem; margin-bottom: 1rem;'>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <div>
                                        <span style='font-size:0.8rem; color:#64748b; font-weight:700;'>OVERALL RATING</span><br>
                                        <span style='font-size:1.4rem; font-weight:800; color:#4f46e5;'>{rating}</span>
                                    </div>
                                    <div style='text-align:right;'>
                                        <span style='font-size:0.8rem; color:#64748b; font-weight:700;'>TOTAL SCORE</span><br>
                                        <span style='font-size:1.8rem; font-weight:800;'>{score_total}/100</span>
                                    </div>
                                </div>
                                <div class='star-metric-grid'>
                                    <div class='star-metric-box'>
                                        <div style='font-size:0.75rem; color:#64748b;'>Situation</div>
                                        <div style='font-size:1.1rem; font-weight:800;'>{s_score}/10</div>
                                    </div>
                                    <div class='star-metric-box'>
                                        <div style='font-size:0.75rem; color:#64748b;'>Task</div>
                                        <div style='font-size:1.1rem; font-weight:800;'>{t_score}/10</div>
                                    </div>
                                    <div class='star-metric-box'>
                                        <div style='font-size:0.75rem; color:#64748b;'>Action</div>
                                        <div style='font-size:1.1rem; font-weight:800;'>{a_score}/10</div>
                                    </div>
                                    <div class='star-metric-box'>
                                        <div style='font-size:0.75rem; color:#64748b;'>Result</div>
                                        <div style='font-size:1.1rem; font-weight:800;'>{r_score}/10</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Strengths & Growth Areas
                        st.markdown("#### ✨ What Worked Well")
                        for str_item in eval_res.get("strengths", []):
                            st.markdown(f"<div class='strength-box'>✔ {str_item}</div>", unsafe_allow_html=True)

                        st.markdown("#### 🔍 Areas for Improvement")
                        for grow_item in eval_res.get("growth_areas", []):
                            st.markdown(f"<div class='missing-box'>⚠ {grow_item}</div>", unsafe_allow_html=True)

                        st.markdown("---")
                        st.markdown("#### 💡 Exemplary Model Response")
                        st.info(eval_res.get("sample_answer", "No sample answer available."))
                else:
                    st.info("Write your response on the left and click 'Evaluate Response (STAR Rubric)' to view in-depth coaching critique.")
            else:
                st.info("Generate questions on the left to begin your interactive mock interview session.")

        # Download Interview Guide Button
        if st.session_state.interview_questions:
            st.markdown("---")
            cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
            doc_prep = create_interview_prep_docx(
                st.session_state.interview_questions,
                st.session_state.interview_feedback,
                candidate_name=cand_name
            )
            st.download_button(
                "📥 Download Complete Mock Interview Scorecard (.docx)",
                data=doc_prep,
                file_name="Mock_Interview_Scorecard.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        # Interview Cheat Sheet Studio
        st.markdown("---")
        st.markdown("### 🏆 Role-Specific Interview Preparation Cheat Sheet")
        st.caption("Generate your top 3 anchor stories, 3 trap questions to watch out for, and 4 questions to ask the interviewer.")
        
        if st.button("✨ Generate Interview Preparation Cheat Sheet", use_container_width=False):
            spinner_text = "Compiling strategic interview cheat sheet with Gemini..." if active_key else "Generating strategic interview cheat sheet with smart offline engine..."
            with st.spinner(spinner_text):
                cheat = generate_interview_cheat_sheet(
                    st.session_state.resume_text,
                    st.session_state.job_desc,
                    api_key=active_key,
                    model_name=selected_model
                )
                st.session_state.interview_cheat_sheet = cheat

        if st.session_state.interview_cheat_sheet:
            cs = st.session_state.interview_cheat_sheet
            if "error" in cs:
                st.error(cs["error"])
            else:
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("#### ⚓ Anchor Stories to Tell")
                    for story in cs.get("anchor_stories", []):
                        st.markdown(
                            f"""
                            <div class='rewrite-card'>
                                <strong>{story.get('headline')}</strong><br>
                                <span style='font-size:0.85rem; color:#4f46e5;'>Best for: {story.get('applicable_to')}</span><br>
                                <span style='font-size:0.85rem; color:#64748b;'>Takeaway: {story.get('key_takeaway')}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                with col_c2:
                    st.markdown("#### ⚠️ Curveball Questions to Watch For")
                    for cb in cs.get("curveball_questions_to_watch", []):
                        st.markdown(
                            f"""
                            <div class='missing-box'>
                                <strong>"{cb.get('question')}"</strong><br>
                                <span style='font-size:0.85rem;'>Pitfall: {cb.get('pitfall_to_avoid')}</span><br>
                                <span style='font-size:0.85rem; font-weight:600;'>Angle: {cb.get('recommended_angle')}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("#### ❓ Smart Questions to Ask the Interviewer:")
                for q_ask in cs.get("questions_to_ask_interviewer", []):
                    st.markdown(f"<div class='tip-box'>💬 \"{q_ask}\"</div>", unsafe_allow_html=True)

    render_step_navigation(5)


# ==============================================================================
# PAGE 7: 30-DAY SKILL GAP & ROADMAP
# ==============================================================================
elif page == "🎯 7. 30-Day Skill Gap Roadmap":
    st.markdown("<div class='section-title'>🎯 30-Day Fast-Track Upskilling & Portfolio Roadmap</div>", unsafe_allow_html=True)
    render_step_header(6)
    
    st.markdown(
        """
        Don't just detect missing skills—bridge them! Gemini analyzes your skill gaps against the target job
        and builds a custom **4-week learning curriculum** and **portfolio project blueprints**.
        """
    )

    if not st.session_state.ats_analysis:
        st.info("💡 Run the ATS Benchmark in Step 2 first so we can identify your specific skill gaps.")
    else:
        kw = st.session_state.ats_analysis.get("keyword_analysis", {})
        missing_skills = kw.get("missing_must_have", []) + kw.get("missing_nice_to_have", [])
        clean_missing = [s for s in missing_skills if not s.startswith("Connect Gemini") and not s.startswith("Secondary skills") and not s.startswith("No critical")]

        if not clean_missing:
            st.success("🎉 No significant skill gaps detected! Your profile is exceptionally aligned with this job description.")
        else:
            st.markdown(f"**Identified Gaps ({len(clean_missing)}):** {', '.join(clean_missing[:8])}")

            if st.button("🚀 Generate 30-Day Upskilling Plan & Portfolio Projects", use_container_width=True):
                target_r = st.session_state.candidate_profile.get("headline", "Target Role") if st.session_state.candidate_profile else "Target Role"
                spinner_text = "Architecting 30-day learning curriculum with Gemini..." if active_key else "Generating personalized 30-day roadmap with smart offline engine..."
                with st.spinner(spinner_text):
                    roadmap = generate_skill_gap_roadmap(
                        clean_missing[:8],
                        target_role=target_r,
                        api_key=active_key,
                        model_name=selected_model
                    )
                    st.session_state.skill_roadmap = roadmap

            if st.session_state.skill_roadmap:
                rm = st.session_state.skill_roadmap
                if rm.get("is_offline"):
                    st.markdown("<span class='mode-pill-offline'>⚡ Smart Offline Curriculum</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='mode-pill-ai'>✨ Google Gemini AI Curriculum</span>", unsafe_allow_html=True)
                if "error" in rm:
                    st.error(rm["error"])
                else:
                    col_rm1, col_rm2 = st.columns([1.2, 1])

                    with col_rm1:
                        st.markdown("### 📅 4-Week Fast-Track Curriculum")
                        for week in rm.get("weekly_plan", []):
                            topics_html = "".join([f"<li>{t}</li>" for t in week.get("topics", [])])
                            st.markdown(
                                f"""
                                <div class='info-card' style='margin-bottom: 0.8rem;'>
                                    <div style='color: #4f46e5; font-weight:800; font-size: 1rem;'>{week.get('week')}</div>
                                    <div style='font-size: 0.9rem; font-weight:600; margin: 4px 0;'>Focus: {week.get('focus')}</div>
                                    <ul style='margin: 0.4rem 0; padding-left: 1.2rem; font-size: 0.85rem;'>
                                        {topics_html}
                                    </ul>
                                    <div style='font-size: 0.82rem; color: #059669; font-weight:600;'>🏆 Milestone: {week.get('deliverable')}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    with col_rm2:
                        st.markdown("### 🛠️ Portfolio Projects to Showcase")
                        for proj in rm.get("recommended_projects", []):
                            stack_badges = "".join([f"<span class='skill-badge badge-framework'>{s}</span>" for s in proj.get("tech_stack", [])])
                            st.markdown(
                                f"""
                                <div class='rewrite-card'>
                                    <div style='font-weight:800; font-size:1.05rem;'>{proj.get('project_title')}</div>
                                    <div style='font-size:0.85rem; color:#64748b; margin: 6px 0;'>{proj.get('description')}</div>
                                    <div style='margin-bottom: 8px;'>{stack_badges}</div>
                                    <div style='font-size:0.8rem; background:rgba(0,0,0,0.03); padding:0.5rem; border-radius:6px; border:1px solid #e2e8f0;'>
                                        <strong>Resume Bullet Preview:</strong><br>
                                        • {proj.get('resume_bullet_preview')}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown("#### 📚 Recommended Certifications & Resources")
                        for cert in rm.get("top_certifications_or_resources", []):
                            st.markdown(f"<div class='tip-box'>📖 {cert}</div>", unsafe_allow_html=True)

                    st.markdown("---")
                    cand_name = st.session_state.candidate_profile.get("full_name", "Candidate") if st.session_state.candidate_profile else "Candidate"
                    target_r = st.session_state.candidate_profile.get("headline", "Target Role") if st.session_state.candidate_profile else "Target Role"
                    col_rm_d1, col_rm_d2 = st.columns(2)
                    with col_rm_d1:
                        rm_docx = create_roadmap_docx(rm, candidate_name=cand_name, target_role=target_r)
                        st.download_button(
                            "📥 Download 30-Day Roadmap (.docx)",
                            data=rm_docx,
                            file_name="30_Day_Upskilling_Roadmap.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    with col_rm_d2:
                        rm_md = create_roadmap_markdown(rm, candidate_name=cand_name, target_role=target_r)
                        st.download_button(
                            "📄 Download 30-Day Roadmap (.md)",
                            data=rm_md,
                            file_name="30_Day_Upskilling_Roadmap.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

    render_step_navigation(6)