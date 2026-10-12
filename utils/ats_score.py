import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.gemini_service import get_ats_analysis, configure_gemini
from utils.skill_extractor import extract_skills_offline


def clean_job_description_boilerplate(text):
    """
    Strips common HR/recruiting disclaimers, EEO statements, and benefits blurbs
    that distort ATS cosine similarity calculations.
    """
    if not text:
        return ""
    
    cleaned = text
    boilerplate_patterns = [
        r"equal opportunity employer.*?(?:\n\n|$)",
        r"we offer competitive (?:salary|compensation|benefits).*?(?:\n\n|$)",
        r"benefits include.*?(?:\n\n|$)",
        r"401\(?k\)?.*?(?:\n\n|$)",
        r"medical, dental, vision.*?(?:\n\n|$)",
        r"affirmative action.*?(?:\n\n|$)"
    ]
    for pattern in boilerplate_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def calculate_ats_score_tfidf(resume_text, job_description):
    """
    Calculates baseline ATS keyword similarity using n-gram TF-IDF and Cosine Similarity.
    """
    if not resume_text or not job_description:
        return 0.0
    try:
        clean_jd = clean_job_description_boilerplate(job_description)
        documents = [resume_text, clean_jd if clean_jd else job_description]
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_df=0.9,
            min_df=1
        )
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Scale reasonably: raw cosine similarity between resume & JD rarely exceeds 0.50
        scaled_score = min(98.0, float(similarity * 100 * 1.35))
        return round(scaled_score, 1)
    except Exception:
        return 0.0


def calculate_offline_ats_audit(resume_text, job_description):
    """
    Rich offline heuristic audit that extracts real keyword overlap from JD,
    estimates radar metrics, section health, and keyword gaps when Gemini API
    is offline or unconfigured.
    """
    tfidf_score = calculate_ats_score_tfidf(resume_text, job_description)
    
    # 1. Impact / Quantified Metrics (XYZ formula check)
    numbers_count = len(re.findall(r"\b\d+(?:%|\+|\s?k|\s?M|\s?X|x|\$)?\b", resume_text))
    impact_score = min(95, max(30, int(numbers_count * 4.5)))

    # 2. Section Audit
    sections = {
        "Contact & Links": bool(re.search(r"@|\.com|phone|\+?\d{10}", resume_text, re.IGNORECASE)),
        "Professional Summary": bool(re.search(r"summary|profile|about me|objective", resume_text, re.IGNORECASE)),
        "Work Experience & Metrics": bool(re.search(r"experience|work history|employment|projects", resume_text, re.IGNORECASE)),
        "Skills & ATS Keywords": bool(re.search(r"skills|technologies|tools|competencies|stack", resume_text, re.IGNORECASE)),
        "Education & Credentials": bool(re.search(r"education|degree|bachelor|master|university|college|b\.tech", resume_text, re.IGNORECASE))
    }
    formatting_score = min(95, int(sum(sections.values()) * 18 + 10))

    # 3. Dual Skill Extraction (Resume vs JD)
    detected_resume_skills = set(extract_skills_offline(resume_text))
    detected_jd_skills = set(extract_skills_offline(job_description))

    matched_skills = sorted(list(detected_resume_skills.intersection(detected_jd_skills)))
    missing_skills = sorted(list(detected_jd_skills - detected_resume_skills))

    # Skill Score based on real JD requirements
    if detected_jd_skills:
        match_ratio = len(matched_skills) / len(detected_jd_skills)
        skill_score = min(98, max(25, int(match_ratio * 100)))
    elif detected_resume_skills:
        skill_score = min(90, max(40, len(detected_resume_skills) * 5))
    else:
        skill_score = int(tfidf_score)

    experience_score = min(95, max(30, int(tfidf_score * 0.9 + skill_score * 0.3)))
    education_score = 85 if sections["Education & Credentials"] else 40

    overall_score = round(
        (tfidf_score * 0.30 + skill_score * 0.30 + experience_score * 0.20 + impact_score * 0.10 + formatting_score * 0.10),
        1
    )

    # Missing keywords separation
    missing_must_have = missing_skills[:6] if missing_skills else []
    missing_nice_to_have = missing_skills[6:14] if len(missing_skills) > 6 else []

    # Actionable optimization recommendations
    optimization_tips = []
    if missing_must_have:
        optimization_tips.append(
            f"Infuse missing job-critical technical keywords directly into your experience bullets: {', '.join(missing_must_have[:4])}."
        )
    if impact_score < 65:
        optimization_tips.append(
            "Increase quantified results using Google's XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]'."
        )
    for sec_name, passed in sections.items():
        if not passed:
            optimization_tips.append(f"Add a distinct, clearly labeled section header for '{sec_name}'.")
    optimization_tips.append(
        "Connect your free Gemini API key in the sidebar for qualitative AI semantic reasoning, STAR bullet rewrites, and mock interview coaching."
    )

    # Section Audit list
    section_audit = []
    for sec_name, passed in sections.items():
        section_audit.append({
            "section": sec_name,
            "status": "Pass" if passed else "Warning",
            "finding": "Standard section detected and readable by ATS engines." if passed else "Section heading or expected keywords appear missing."
        })

    return {
        "score_overall": int(overall_score),
        "score_skills": skill_score,
        "score_experience": experience_score,
        "score_formatting": formatting_score,
        "score_impact": impact_score,
        "score_education": education_score,
        "executive_summary": f"Offline Heuristic Audit: Identified {len(matched_skills)} matching core keywords from target job description ({int((len(matched_skills) / max(len(detected_jd_skills), 1)) * 100)}% coverage). Connect Gemini for deep qualitative semantic reasoning.",
        "strengths": [
            f"Direct keyword alignment: {', '.join(matched_skills[:6]) if matched_skills else 'Foundational engineering vocabulary'}",
            f"Quantified metrics density: {numbers_count} numerical accomplishments detected",
            "Standard ATS-compliant section hierarchy detected"
        ],
        "keyword_analysis": {
            "matched_keywords": matched_skills,
            "missing_must_have": missing_must_have if missing_must_have else ["No critical detected keywords missing"],
            "missing_nice_to_have": missing_nice_to_have if missing_nice_to_have else ["General alignment across secondary skills"]
        },
        "section_audit": section_audit,
        "optimization_tips": optimization_tips,
        "is_fallback": True
    }


def calculate_ats_score(resume_text, job_description, api_key=None, model_name=None):
    """
    Calculates multi-dimensional ATS score using Gemini if available,
    falling back to rich heuristic audit offline.
    """
    if configure_gemini(api_key):
        analysis = get_ats_analysis(resume_text, job_description, api_key=api_key, model_name=model_name)
        if analysis and "error" not in analysis and "score_overall" in analysis:
            return analysis

    return calculate_offline_ats_audit(resume_text, job_description)