import re
from datetime import datetime
from utils.information_extractor import extract_all_contact_info
from utils.skill_extractor import extract_skills_offline


def generate_offline_bullet_rewrite(bullet_text, job_context=""):
    """
    Transforms a resume bullet point into 3 Google XYZ formula variations offline
    using grammatical analysis, action verbs, and injected job keywords.
    """
    clean_bullet = bullet_text.strip().rstrip(".")
    if not clean_bullet:
        clean_bullet = "Managed technical systems and developed applications"

    # Identify weak starter verbs
    weak_starters = [
        r"^(?:responsible for|tasked with|handled|worked on|helped with|assisted in|involved in|participated in)\s+",
        r"^(?:duties included|was in charge of)\s+"
    ]
    core_content = clean_bullet
    for pattern in weak_starters:
        core_content = re.sub(pattern, "", core_content, flags=re.IGNORECASE).strip()

    # Determine keywords to emphasize
    keywords = [k.strip() for k in re.split(r"[,;|]", job_context) if k.strip()] if job_context else []
    kw_str = f" using {', '.join(keywords[:3])}" if keywords else ""

    # Generate 3 XYZ variations
    var_metric = {
        "style": "Metric-Driven (Results Focus)",
        "rewritten": f"Accelerated operational efficiency by 38% and reduced latency by 45% by architecting and optimizing {core_content}{kw_str}.",
        "highlight": "Quantified 38% efficiency gain & 45% latency improvement"
    }
    var_leadership = {
        "style": "Leadership & Ownership",
        "rewritten": f"Spearheaded end-to-end design and cross-functional delivery of {core_content}{kw_str}, mentoring 4 engineers and maintaining 99.9% service uptime.",
        "highlight": "Cross-functional ownership, mentorship & 99.9% uptime SLA"
    }
    var_tech = {
        "style": "Technical Precision (Stack Focus)",
        "rewritten": f"Engineered resilient, high-throughput microservices for {core_content}{kw_str}, implementing automated CI/CD pipelines and comprehensive test coverage.",
        "highlight": "Production engineering rigor & CI/CD automation"
    }

    critique = (
        "Original bullet lacked quantified outcomes and clear personal ownership. "
        "Rewritten versions leverage strong action verbs and Google's XYZ formula: "
        "'Accomplished [X], as measured by [Y], by doing [Z]'."
    )

    return {
        "critique": critique,
        "variations": [var_metric, var_leadership, var_tech],
        "is_offline": True
    }


def generate_offline_tailored_summary(resume_text, job_description):
    """
    Synthesizes a tailored 3-4 sentence professional executive summary offline
    connecting candidate credentials with target job requirements.
    """
    contact = extract_all_contact_info(resume_text)
    cand_name = contact.get("full_name", "Professional")
    exp_years = contact.get("estimated_exp_years", 4)
    skills = extract_skills_offline(resume_text)
    jd_skills = extract_skills_offline(job_description)

    top_skills = [s for s in skills if s in jd_skills][:4]
    if not top_skills:
        top_skills = skills[:4] if skills else ["Software Development", "System Design"]

    skills_str = ", ".join(top_skills)
    role_hint = "Engineer"
    if any(w in job_description.lower() for w in ["machine learning", "ai", "data scientist"]):
        role_hint = "AI & Machine Learning Engineer"
    elif any(w in job_description.lower() for w in ["full-stack", "full stack", "frontend", "backend"]):
        role_hint = "Full-Stack Software Engineer"
    elif any(w in job_description.lower() for w in ["devops", "cloud", "platform"]):
        role_hint = "Cloud & Platform Engineer"

    summary = (
        f"Results-oriented {role_hint} with {exp_years}+ years of experience building scalable, "
        f"high-performance solutions with {skills_str}. Proven track record of architecting reliable "
        f"distributed systems, optimizing production workflows, and collaborating cross-functionally "
        f"to achieve measurable business impact. Passionate about applying modern engineering practices "
        f"and rapid problem-solving to deliver mission-critical value."
    )
    return summary


def generate_offline_cover_letter(
    resume_text,
    job_description,
    tone="Professional",
    company_name="",
    hiring_manager="",
    focus_area="",
    length="Standard (350 words)"
):
    """
    Generates a structured, customized cover letter offline.
    """
    contact = extract_all_contact_info(resume_text)
    cand_name = contact.get("full_name", "Candidate")
    email = contact.get("email", "candidate@email.com")
    phone = contact.get("phone", "+1 (555) 0100")
    exp_years = contact.get("estimated_exp_years", 4)

    skills = extract_skills_offline(resume_text)
    jd_skills = extract_skills_offline(job_description)
    matching = [s for s in skills if s in jd_skills][:5]
    if not matching:
        matching = skills[:4] if skills else ["System Architecture", "Modern Engineering"]
    matching_str = ", ".join(matching)

    company = company_name.strip() if company_name else "your organization"
    manager = hiring_manager.strip() if hiring_manager else "Hiring Manager"
    focus = focus_area.strip() if focus_area else f"delivering scalable outcomes with {matching_str}"

    date_str = datetime.now().strftime("%B %d, %Y")

    letter = f"""{cand_name}
{contact.get('location', 'San Francisco, CA')} | {email} | {phone}

{date_str}

Dear {manager},

I am writing to express my enthusiastic interest in joining {company}. With over {exp_years} years of progressive experience and strong technical expertise in {matching_str}, I am excited about the opportunity to contribute directly to your team's mission and engineering initiatives.

Throughout my career, I have focused on solving complex challenges through scalable architecture and measured outcomes. Specifically, my recent work emphasizes {focus}. In past roles, I have consistently improved performance, streamlined deployments, and collaborated with cross-functional partners to translate technical capability into tangible business value.

What attracts me most to {company} is your commitment to technical innovation and high-impact delivery. Having worked extensively with {', '.join(matching[:3])}, I am confident that my background aligns well with the demands of this position and that I can quickly hit the ground running.

Thank you for your time and consideration. I welcome the opportunity to discuss how my experience and skill set can help drive {company}'s goals forward.

Sincerely,

{cand_name}
"""
    return letter.strip()


def generate_offline_cold_outreach(
    resume_text,
    job_description,
    outreach_type="LinkedIn Connection Note (<300 chars)",
    company_name="",
    recipient_name="",
    tone="Professional & Direct"
):
    """
    Generates high-conversion recruiter and networking messages offline.
    """
    contact = extract_all_contact_info(resume_text)
    cand_name = contact.get("full_name", "Candidate")
    skills = extract_skills_offline(resume_text)
    top_skill = skills[0] if skills else "software engineering"
    company = company_name.strip() if company_name else "your team"
    recipient = recipient_name.strip() if recipient_name else "there"

    if "LinkedIn Connection Note" in outreach_type:
        msg = (
            f"Hi {recipient}! Came across your work at {company} and wanted to connect. "
            f"I'm an engineer specializing in {top_skill} with a background scaling production systems. "
            f"Would love to follow your team's journey!"
        )
        # Guarantee strictly under 300 chars
        if len(msg) > 295:
            msg = f"Hi {recipient}! Connecting as an engineer experienced in {top_skill} interested in {company}'s team."
        return {
            "subject_or_headline": f"Connect regarding {company}",
            "message_body": msg,
            "character_count": len(msg),
            "pro_tip": "Keep LinkedIn notes strictly under 300 characters to ensure 100% sendability without truncation.",
            "is_offline": True
        }

    elif "Recruiter InMail" in outreach_type:
        subj = f"Experienced {top_skill} Engineer interested in opportunities at {company}"
        msg = f"""Hi {recipient},

I hope this message finds you well! I have been closely following {company}'s work and wanted to reach out regarding open engineering opportunities.

With a solid background in {', '.join(skills[:3])}, I have driven measurable impact:
• Optimized system throughput and reduced latency across core microservices.
• Delivered high-availability architecture while maintaining rigorous testing standards.

I would love to learn if there might be a mutual fit for your current openings. Would you be open to a brief 10-minute introductory conversation this week?

Best regards,
{cand_name}"""
        return {
            "subject_or_headline": subj,
            "message_body": msg,
            "character_count": len(msg),
            "pro_tip": "Include 2 concise, quantified bullet points so recruiters can assess fit in under 6 seconds.",
            "is_offline": True
        }

    elif "Employee Referral" in outreach_type:
        subj = f"Quick question about engineering at {company}"
        msg = f"""Hi {recipient},

Hope you're having a great week! I came across your profile and noticed your engineering work at {company}.

I'm currently preparing an application for the open role on your team, bringing deep experience in {top_skill} and scalable systems. I would love to get your authentic perspective on the team culture and engineering priorities if you have 5-10 minutes.

Either way, appreciate what you're building!

Thanks,
{cand_name}"""
        return {
            "subject_or_headline": subj,
            "message_body": msg,
            "character_count": len(msg),
            "pro_tip": "Ask for advice and culture insights rather than directly begging for a referral — it dramatically increases reply rates.",
            "is_offline": True
        }

    else:  # Cold Email Pitch
        subj = f"Quick Idea & Intro: {cand_name} for {company} Engineering"
        msg = f"""Hi {recipient},

I'm reaching out because I've been following {company}'s trajectory and wanted to share how my background in {', '.join(skills[:3])} could help tackle your current scaling priorities.

A few recent highlights from my background:
• Architected high-throughput pipelines with sub-50ms P99 latency.
• Reduced compute & cloud infrastructure overhead by 25%+ through optimized resource caching.
• Shipped resilient features with automated CI/CD and comprehensive unit test coverage.

Would you be open to a 10-minute chat this Thursday or Friday to discuss how I can add immediate value to your team?

Best,
{cand_name}
{contact.get('email', '')} | {contact.get('linkedin', '')}"""
        return {
            "subject_or_headline": subj,
            "message_body": msg,
            "character_count": len(msg),
            "pro_tip": "Propose specific days/times for the call to reduce scheduling friction.",
            "is_offline": True
        }


def generate_offline_linkedin_profile(resume_text, target_role="Software Engineer"):
    """
    Generates high-converting LinkedIn profile branding offline.
    """
    skills = extract_skills_offline(resume_text)
    contact = extract_all_contact_info(resume_text)
    cand_name = contact.get("full_name", "Engineer")
    top_skills = skills[:5] if skills else ["Python", "System Design", "Cloud", "APIs", "SQL"]

    headline_1 = f"{target_role} | {' • '.join(top_skills[:3])} | Scaling Resilient Distributed Systems"
    headline_2 = f"Building High-Throughput Solutions & Cloud Infrastructure | {target_role} | {top_skills[0]} & {top_skills[1] if len(top_skills) > 1 else 'Cloud'}"
    headline_3 = f"{target_role} Helping Teams Ship Production Systems | {', '.join(top_skills[:3])}"

    about = (
        f"I am a {target_role} dedicated to designing resilient, maintainable, and high-performance software systems. "
        f"Throughout my career, I have focused on translating ambitious product goals into robust technical architectures, "
        f"leveraging modern tools like {', '.join(top_skills)}.\n\n"
        f"What excites me most is solving complex scaling challenges—whether that means optimizing latency, "
        f"automating CI/CD pipelines, or architecting reliable data models. I believe great engineering is not just "
        f"about writing code, but about fostering cross-functional collaboration and delivering measurable user impact.\n\n"
        f"Feel free to reach out to discuss distributed systems, innovative tech architectures, or upcoming engineering opportunities!"
    )

    return {
        "headlines": [headline_1, headline_2, headline_3],
        "about_summary": about,
        "top_skills_to_pin": top_skills[:5],
        "is_offline": True
    }


def generate_offline_interview_questions(resume_text, job_description, seniority_level="Mid-Level"):
    """
    Generates 5 realistic, seniority-calibrated interview questions offline.
    """
    skills = extract_skills_offline(resume_text)
    jd_skills = extract_skills_offline(job_description)
    matching = [s for s in skills if s in jd_skills]
    s1 = matching[0] if matching else (skills[0] if skills else "Python")
    s2 = matching[1] if len(matching) > 1 else (skills[1] if len(skills) > 1 else "System Design")

    questions = [
        {
            "id": 1,
            "type": "Technical",
            "question": f"Can you walk me through how you architect and optimize production workflows using {s1}? What design trade-offs did you face?",
            "interviewer_intent": f"Evaluates practical hands-on mastery with {s1}, architectural judgment, and handling technical trade-offs.",
            "key_points_to_include": ["Concrete architectural choices", "Performance and bottleneck mitigation", "Testing and observability"]
        },
        {
            "id": 2,
            "type": "Technical",
            "question": f"Describe a challenging scalability or data consistency challenge you encountered while working with {s2}. How did you resolve it?",
            "interviewer_intent": f"Tests depth in {s2}, debugging methodology, and system resilience under load.",
            "key_points_to_include": ["Root-cause analysis", "Metrics used to measure resolution", "Preventive mechanisms implemented"]
        },
        {
            "id": 3,
            "type": "Behavioral",
            "question": "Tell me about a time when you disagreed with a technical design decision or product priority. How did you handle it using data and communication?",
            "interviewer_intent": "Measures conflict resolution, collaboration, stakeholder management, and professional maturity.",
            "key_points_to_include": ["Specific conflict context", "Objective data and trade-offs presented", "Constructive alignment outcome"]
        },
        {
            "id": 4,
            "type": "Behavioral",
            "question": "Give an example of a critical project where you faced tight deadlines or ambiguity. How did you prioritize deliverables to ensure successful execution?",
            "interviewer_intent": "Tests composure under pressure, agile prioritization, and ownership.",
            "key_points_to_include": ["Clear task breakdown", "Proactive communication with stakeholders", "Measurable project launch"]
        },
        {
            "id": 5,
            "type": "Situational",
            "question": f"If our primary production service experienced a sudden 5x traffic surge causing elevated latency, how would you systematically diagnose and mitigate the incident?",
            "interviewer_intent": "Assesses incident response capability, telemetry/monitoring familiarity, and emergency triage.",
            "key_points_to_include": ["Telemetry/log inspection", "Traffic shedding/caching layers", "Post-mortem root cause analysis"]
        }
    ]
    return questions


def evaluate_offline_interview_answer(question, user_answer, job_description, resume_text):
    """
    Evaluates candidate's answer using heuristic STAR rubric offline.
    """
    text = user_answer.strip()
    words = text.split()
    word_count = len(words)

    # Situation indicators (context setting)
    has_situation = any(w in text.lower() for w in ["when", "at my previous", "while working", "in my role", "we were building", "the project", "context"])
    s_score = min(10, max(4, (3 if has_situation else 1) + min(6, word_count // 35)))

    # Task indicators (challenge definition)
    has_task = any(w in text.lower() for w in ["goal was", "needed to", "tasked with", "objective", "challenge was", "problem"])
    t_score = min(10, max(4, (3 if has_task else 1) + min(6, word_count // 35)))

    # Action indicators (personal contributions, tools)
    action_verbs = len(re.findall(r"\b(?:designed|built|implemented|refactored|optimized|configured|led|architected|resolved|deployed)\b", text, re.IGNORECASE))
    has_i = bool(re.search(r"\b(?:I|my|personally)\b", text, re.IGNORECASE))
    a_score = min(10, max(4, action_verbs * 2 + (2 if has_i else 0) + 2))

    # Result indicators (metrics, outcomes)
    metrics_count = len(re.findall(r"\b\d+(?:%|\+|\s?k|\s?ms|\s?users|\$)?\b", text))
    has_result = any(w in text.lower() for w in ["result", "reduced", "increased", "improved", "saved", "achieved", "delivered"])
    r_score = min(10, max(3, metrics_count * 3 + (3 if has_result else 1)))

    total_score = int((s_score + t_score + a_score + r_score) * 2.5)

    if total_score >= 85:
        rating = "Outstanding"
    elif total_score >= 70:
        rating = "Solid Match"
    elif total_score >= 55:
        rating = "Needs Improvement"
    else:
        rating = "Weak"

    strengths = []
    if a_score >= 7:
        strengths.append("Clear articulation of personal technical action and decision-making.")
    if metrics_count > 0:
        strengths.append(f"Effective use of quantified results ({metrics_count} numerical metrics detected).")
    if word_count >= 60:
        strengths.append("Comprehensive depth covering key aspects of the problem.")
    if not strengths:
        strengths.append("Addressed the central theme of the interviewer's question.")

    growth_areas = []
    if metrics_count == 0:
        growth_areas.append("Quantify the final result: specify % improvement, latency reduction, cost savings, or user scale.")
    if not has_i:
        growth_areas.append("Highlight your personal role ('I designed/implemented') rather than speaking solely about 'we'.")
    if word_count < 50:
        growth_areas.append("Expand on the technical methodology, tools used, and trade-offs considered.")

    sample_answer = (
        "Situation: In my previous role, our core data service faced intermittent latency spikes during peak load. "
        "Task: I was responsible for identifying the bottleneck and stabilizing response times below 100ms. "
        "Action: I profiled the system using distributed tracing, identified unindexed database queries, and implemented Redis caching alongside asynchronous batch processing. "
        "Result: This reduced P99 latency by 52%, eliminated downtime during traffic surges, and saved $20K in monthly server provisioning."
    )

    return {
        "rating": rating,
        "score_total": total_score,
        "star_breakdown": {
            "situation_score": s_score,
            "task_score": t_score,
            "action_score": a_score,
            "result_score": r_score
        },
        "strengths": strengths,
        "growth_areas": growth_areas,
        "sample_answer": sample_answer,
        "is_offline": True
    }


def generate_offline_followup_question(question, user_answer, job_description):
    """
    Generates a dynamic follow-up drill-down question offline.
    """
    if any(w in user_answer.lower() for w in ["cache", "redis", "database", "query"]):
        return "How did you handle cache invalidation and potential data inconsistency between cache and primary storage?"
    elif any(w in user_answer.lower() for w in ["scale", "traffic", "load"]):
        return "What were the limits of that approach, and at what scale would that architecture begin to fail?"
    elif any(w in user_answer.lower() for w in ["team", "disagree", "conflict"]):
        return "Looking back, what is one thing you would do differently in building consensus earlier?"
    else:
        return "What technical trade-offs did you evaluate, and how did you monitor the solution once deployed to production?"


def generate_offline_interview_cheat_sheet(resume_text, job_description):
    """
    Generates an interview preparation cheat sheet offline.
    """
    skills = extract_skills_offline(resume_text)
    s1 = skills[0] if skills else "Core Engineering"
    s2 = skills[1] if len(skills) > 1 else "System Architecture"

    anchor_stories = [
        {
            "headline": f"Optimizing high-throughput service performance with {s1}",
            "applicable_to": "System performance, debugging complex bottlenecks, and architectural ownership",
            "key_takeaway": "Proves ability to identify root causes and deliver measured latency/throughput gains."
        },
        {
            "headline": f"Leading cross-functional delivery of resilient {s2} workflows",
            "applicable_to": "Cross-functional collaboration, ambiguity handling, and engineering mentorship",
            "key_takeaway": "Demonstrates teamwork, proactive communication, and end-to-end execution reliability."
        },
        {
            "headline": "Mitigating high-severity production incident under tight SLA constraints",
            "applicable_to": "Incident response, high availability, and operational composure",
            "key_takeaway": "Shows calm decision-making, rapid triage, and blameless post-mortem follow-through."
        }
    ]

    curveball_questions = [
        {
            "question": "Can you describe a technical decision you made that turned out to be a mistake?",
            "pitfall_to_avoid": "Claiming you've never made a mistake, or choosing an issue where you blame others.",
            "recommended_angle": "Pick a genuine technical trade-off, explain the lessons learned, and highlight how it improved your future engineering practices."
        },
        {
            "question": "How do you handle ambiguous requirements when product specs are incomplete?",
            "pitfall_to_avoid": "Starting implementation blindly or waiting passively for complete specs.",
            "recommended_angle": "Emphasize creating lightweight prototypes, documenting assumptions, and syncing frequently with product stakeholders."
        },
        {
            "question": "Why do you want to work at this specific company over other opportunities?",
            "pitfall_to_avoid": "Giving generic answers about company reputation or perks.",
            "recommended_angle": "Connect your specific technical toolkit to their product challenges and engineering values."
        }
    ]

    questions_to_ask = [
        "What are the biggest technical scaling bottlenecks the engineering team is currently working to solve?",
        "How does the team balance shipping new features quickly versus addressing technical debt and infrastructure reliability?",
        "What does success look like in this role over the first 90 days?",
        "How is cross-functional feedback gathered between engineering, product, and leadership during sprint reviews?"
    ]

    return {
        "anchor_stories": anchor_stories,
        "curveball_questions_to_watch": curveball_questions,
        "questions_to_ask_interviewer": questions_to_ask,
        "is_offline": True
    }


def generate_offline_skill_gap_roadmap(missing_skills, target_role="Target Position"):
    """
    Builds a personalized 4-week learning curriculum and portfolio project blueprints offline.
    """
    gaps = missing_skills if isinstance(missing_skills, list) and missing_skills else ["System Design", "Cloud Architecture"]
    sk1 = gaps[0] if len(gaps) > 0 else "Cloud Architecture"
    sk2 = gaps[1] if len(gaps) > 1 else "Microservices"
    sk3 = gaps[2] if len(gaps) > 2 else "Performance Optimization"

    weekly_plan = [
        {
            "week": "Week 1: Core Fundamentals & Environment Setup",
            "focus": f"Master foundational concepts and core architecture of {sk1}",
            "topics": [f"Official documentation & lifecycle of {sk1}", "Local development setup & CLI tools", "Core primitives and hands-on hello-world tutorial"],
            "deliverable": f"Working sandbox repository implementing basic {sk1} integration with automated tests."
        },
        {
            "week": "Week 2: Deep Dive & Real-World Patterns",
            "focus": f"Practical implementation patterns and data flow with {sk2}",
            "topics": [f"Deep dive into {sk2} data modeling", "Error handling, resilience, and retry policies", "Integration with existing tech stacks"],
            "deliverable": f"Functional micro-module connecting {sk1} and {sk2}."
        },
        {
            "week": "Week 3: Advanced Architecture & Scaling",
            "focus": f"Production readiness, observability, and scaling {sk3}",
            "topics": [f"High-concurrency tuning and indexing", "Monitoring, logging, and metrics telemetry", "Security best practices and environment isolation"],
            "deliverable": "Benchmark report detailing latency, throughput, and edge-case handling under simulated load."
        },
        {
            "week": "Week 4: Portfolio Blueprint & Resume Integration",
            "focus": "End-to-end portfolio project polish and resume bullet formulation",
            "topics": ["Architecture diagram & comprehensive README documentation", "Live deployment to cloud provider", "Crafting Google XYZ bullet points for resume"],
            "deliverable": "Production-grade GitHub repository with live demo URL and ready-to-paste resume bullet."
        }
    ]

    recommended_projects = [
        {
            "project_title": f"Distributed Production Pipeline using {sk1} & {sk2}",
            "description": f"An end-to-end scalable backend system demonstrating real-time processing, automated caching, and high availability using {sk1}.",
            "tech_stack": [sk1, sk2, "Docker", "PostgreSQL"],
            "resume_bullet_preview": f"Architected high-throughput distributed pipeline utilizing {sk1} and {sk2}, achieving 40% latency reduction and handling 10K+ simulated requests/sec."
        },
        {
            "project_title": f"Automated Telemetry & Microservice Gateway with {sk3}",
            "description": f"Resilient API gateway and telemetry dashboard that tracks service health, rate-limiting, and error spikes using {sk3}.",
            "tech_stack": [sk3, "FastAPI", "Redis", "GitHub Actions"],
            "resume_bullet_preview": f"Engineered observability gateway incorporating {sk3} and Redis rate limiting, decreasing incident response time by 45%."
        }
    ]

    resources = [
        f"Official Documentation & Tutorials for {sk1}",
        f"Hands-on GitHub Reference Projects & Boilerplates for {sk2}",
        "High Performance Browser Networking / Distributed Systems Engineering Guides",
        f"Free interactive courses on Coursera, freeCodeCamp, or edX covering {sk3}"
    ]

    return {
        "weekly_plan": weekly_plan,
        "recommended_projects": recommended_projects,
        "top_certifications_or_resources": resources,
        "is_offline": True
    }
