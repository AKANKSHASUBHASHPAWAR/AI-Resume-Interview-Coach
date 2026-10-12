import os
import re
import pandas as pd
from utils.gemini_service import parse_full_resume_with_gemini, configure_gemini

# Aliases and canonical mapping
SKILL_ALIASES = {
    "golang": "Go",
    "k8s": "Kubernetes",
    "react.js": "React",
    "reactjs": "React",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "nuxt.js": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "express.js": "Express",
    "expressjs": "Express",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "tf": "TensorFlow",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "amazon web services": "AWS",
    "microsoft azure": "Azure",
    "ci/cd pipelines": "CI/CD",
    "continuous integration": "CI/CD",
    "natural language processing": "NLP",
    "large language models": "LLMs",
    "retrieval-augmented generation": "RAG",
    "apache airflow": "Airflow",
    "pyspark": "Apache Spark",
    "oauth2": "OAuth",
    "tdd": "Test-Driven Development",
    "html5": "HTML",
    "css3": "CSS",
    "restful apis": "REST API",
    "restful api": "REST API",
    "rest apis": "REST API"
}

# Master category mapping
SKILL_CATEGORY_MAP = {
    # Programming Languages
    "Python": "Programming Languages",
    "JavaScript": "Programming Languages",
    "TypeScript": "Programming Languages",
    "Java": "Programming Languages",
    "C": "Programming Languages",
    "C++": "Programming Languages",
    "C#": "Programming Languages",
    "Go": "Programming Languages",
    "Golang": "Programming Languages",
    "Rust": "Programming Languages",
    "Ruby": "Programming Languages",
    "PHP": "Programming Languages",
    "Swift": "Programming Languages",
    "Kotlin": "Programming Languages",
    "Dart": "Programming Languages",
    "Scala": "Programming Languages",
    "R": "Programming Languages",
    "SQL": "Programming Languages",
    "HTML": "Programming Languages",
    "HTML5": "Programming Languages",
    "CSS": "Programming Languages",
    "CSS3": "Programming Languages",
    "Bash": "Programming Languages",
    "Shell Scripting": "Programming Languages",
    "Solidity": "Programming Languages",

    # Frameworks & Libraries
    "React": "Frameworks & Libraries",
    "React.js": "Frameworks & Libraries",
    "Next.js": "Frameworks & Libraries",
    "Vue": "Frameworks & Libraries",
    "Vue.js": "Frameworks & Libraries",
    "Nuxt.js": "Frameworks & Libraries",
    "Angular": "Frameworks & Libraries",
    "Svelte": "Frameworks & Libraries",
    "Redux": "Frameworks & Libraries",
    "Redux Toolkit": "Frameworks & Libraries",
    "Zustand": "Frameworks & Libraries",
    "Node.js": "Frameworks & Libraries",
    "Express": "Frameworks & Libraries",
    "Express.js": "Frameworks & Libraries",
    "NestJS": "Frameworks & Libraries",
    "Django": "Frameworks & Libraries",
    "FastAPI": "Frameworks & Libraries",
    "Flask": "Frameworks & Libraries",
    "Spring Boot": "Frameworks & Libraries",
    "ASP.NET": "Frameworks & Libraries",
    "Ruby on Rails": "Frameworks & Libraries",
    "Tailwind CSS": "Frameworks & Libraries",
    "Bootstrap": "Frameworks & Libraries",
    "Material-UI": "Frameworks & Libraries",
    "Chakra UI": "Frameworks & Libraries",
    "Sass": "Frameworks & Libraries",
    "Streamlit": "Frameworks & Libraries",
    "Pandas": "Frameworks & Libraries",
    "NumPy": "Frameworks & Libraries",
    "SciPy": "Frameworks & Libraries",
    "Scikit-learn": "Frameworks & Libraries",
    "TensorFlow": "Frameworks & Libraries",
    "PyTorch": "Frameworks & Libraries",
    "Keras": "Frameworks & Libraries",
    "OpenCV": "Frameworks & Libraries",
    "Hugging Face": "Frameworks & Libraries",
    "Transformers": "Frameworks & Libraries",
    "LangChain": "Frameworks & Libraries",
    "LangGraph": "Frameworks & Libraries",
    "LlamaIndex": "Frameworks & Libraries",
    "Pydantic": "Frameworks & Libraries",
    "Boto3": "Frameworks & Libraries",
    "Prisma": "Frameworks & Libraries",
    "TypeORM": "Frameworks & Libraries",
    "SQLAlchemy": "Frameworks & Libraries",

    # Cloud, DevOps & Tools
    "AWS": "Cloud, DevOps & Tools",
    "Amazon Web Services": "Cloud, DevOps & Tools",
    "AWS Lambda": "Cloud, DevOps & Tools",
    "AWS S3": "Cloud, DevOps & Tools",
    "AWS EC2": "Cloud, DevOps & Tools",
    "AWS ECS": "Cloud, DevOps & Tools",
    "AWS EKS": "Cloud, DevOps & Tools",
    "AWS SageMaker": "Cloud, DevOps & Tools",
    "AWS RDS": "Cloud, DevOps & Tools",
    "Azure": "Cloud, DevOps & Tools",
    "Microsoft Azure": "Cloud, DevOps & Tools",
    "Azure DevOps": "Cloud, DevOps & Tools",
    "GCP": "Cloud, DevOps & Tools",
    "Google Cloud": "Cloud, DevOps & Tools",
    "Google Cloud Platform": "Cloud, DevOps & Tools",
    "Docker": "Cloud, DevOps & Tools",
    "Kubernetes": "Cloud, DevOps & Tools",
    "K8s": "Cloud, DevOps & Tools",
    "Terraform": "Cloud, DevOps & Tools",
    "Ansible": "Cloud, DevOps & Tools",
    "Helm": "Cloud, DevOps & Tools",
    "Puppet": "Cloud, DevOps & Tools",
    "Chef": "Cloud, DevOps & Tools",
    "Jenkins": "Cloud, DevOps & Tools",
    "GitHub Actions": "Cloud, DevOps & Tools",
    "GitLab CI": "Cloud, DevOps & Tools",
    "CI/CD": "Cloud, DevOps & Tools",
    "CI/CD Pipelines": "Cloud, DevOps & Tools",
    "Linux": "Cloud, DevOps & Tools",
    "Git": "Cloud, DevOps & Tools",
    "GitHub": "Cloud, DevOps & Tools",
    "GitLab": "Cloud, DevOps & Tools",
    "Bitbucket": "Cloud, DevOps & Tools",
    "Vercel": "Cloud, DevOps & Tools",
    "Netlify": "Cloud, DevOps & Tools",
    "Nginx": "Cloud, DevOps & Tools",
    "Apache": "Cloud, DevOps & Tools",

    # Databases & Storage
    "PostgreSQL": "Databases & Storage",
    "Postgres": "Databases & Storage",
    "MySQL": "Databases & Storage",
    "MariaDB": "Databases & Storage",
    "SQLite": "Databases & Storage",
    "MongoDB": "Databases & Storage",
    "Redis": "Databases & Storage",
    "Elasticsearch": "Databases & Storage",
    "DynamoDB": "Databases & Storage",
    "Cassandra": "Databases & Storage",
    "Couchbase": "Databases & Storage",
    "Neo4j": "Databases & Storage",
    "Snowflake": "Databases & Storage",
    "BigQuery": "Databases & Storage",
    "Databricks": "Databases & Storage",
    "Amazon Redshift": "Databases & Storage",
    "Pinecone": "Databases & Storage",
    "ChromaDB": "Databases & Storage",
    "Weaviate": "Databases & Storage",
    "Qdrant": "Databases & Storage",
    "Milvus": "Databases & Storage",
    "Supabase": "Databases & Storage",
    "Firebase": "Databases & Storage",

    # AI, ML & Data Science
    "Machine Learning": "AI, ML & Data Science",
    "Deep Learning": "AI, ML & Data Science",
    "NLP": "AI, ML & Data Science",
    "Natural Language Processing": "AI, ML & Data Science",
    "Computer Vision": "AI, ML & Data Science",
    "LLMs": "AI, ML & Data Science",
    "Large Language Models": "AI, ML & Data Science",
    "RAG": "AI, ML & Data Science",
    "Retrieval-Augmented Generation": "AI, ML & Data Science",
    "Prompt Engineering": "AI, ML & Data Science",
    "Fine-tuning": "AI, ML & Data Science",
    "LoRA": "AI, ML & Data Science",
    "QLoRA": "AI, ML & Data Science",
    "Ollama": "AI, ML & Data Science",
    "vLLM": "AI, ML & Data Science",
    "Gemini API": "AI, ML & Data Science",
    "OpenAI API": "AI, ML & Data Science",
    "Anthropic API": "AI, ML & Data Science",
    "Data Analysis": "AI, ML & Data Science",
    "Data Engineering": "AI, ML & Data Science",
    "Data Science": "AI, ML & Data Science",
    "Statistics": "AI, ML & Data Science",
    "Power BI": "AI, ML & Data Science",
    "Tableau": "AI, ML & Data Science",
    "Looker": "AI, ML & Data Science",
    "Apache Spark": "AI, ML & Data Science",
    "PySpark": "AI, ML & Data Science",
    "Apache Kafka": "AI, ML & Data Science",
    "RabbitMQ": "AI, ML & Data Science",
    "Celery": "AI, ML & Data Science",
    "Airflow": "AI, ML & Data Science",
    "Apache Airflow": "AI, ML & Data Science",
    "dbt": "AI, ML & Data Science",
    "ETL": "AI, ML & Data Science",
    "ELT": "AI, ML & Data Science",
    "Data Warehousing": "AI, ML & Data Science",
    "Data Modeling": "AI, ML & Data Science",

    # Architecture, Methodologies & Leadership
    "System Design": "Architecture & Methodologies",
    "Distributed Systems": "Architecture & Methodologies",
    "Microservices": "Architecture & Methodologies",
    "REST API": "Architecture & Methodologies",
    "RESTful APIs": "Architecture & Methodologies",
    "gRPC": "Architecture & Methodologies",
    "GraphQL": "Architecture & Methodologies",
    "WebSockets": "Architecture & Methodologies",
    "Object-Oriented Programming": "Architecture & Methodologies",
    "OOP": "Architecture & Methodologies",
    "Design Patterns": "Architecture & Methodologies",
    "Unit Testing": "Architecture & Methodologies",
    "Pytest": "Architecture & Methodologies",
    "Jest": "Architecture & Methodologies",
    "Cypress": "Architecture & Methodologies",
    "Playwright": "Architecture & Methodologies",
    "Selenium": "Architecture & Methodologies",
    "Integration Testing": "Architecture & Methodologies",
    "Test-Driven Development": "Architecture & Methodologies",
    "TDD": "Architecture & Methodologies",
    "Cybersecurity": "Architecture & Methodologies",
    "OAuth": "Architecture & Methodologies",
    "OAuth2": "Architecture & Methodologies",
    "JWT": "Architecture & Methodologies",
    "High Availability": "Architecture & Methodologies",
    "Disaster Recovery": "Architecture & Methodologies",
    "Performance Optimization": "Architecture & Methodologies",
    "Agile": "Architecture & Methodologies",
    "Scrum": "Architecture & Methodologies",
    "Kanban": "Architecture & Methodologies",
    "Jira": "Architecture & Methodologies",
    "Confluence": "Architecture & Methodologies",
    "Cross-Functional Leadership": "Architecture & Methodologies",
    "Project Management": "Architecture & Methodologies",
    "Product Management": "Architecture & Methodologies",
    "Sprint Planning": "Architecture & Methodologies",
    "Code Review": "Architecture & Methodologies",
    "Technical Mentorship": "Architecture & Methodologies"
}


def canonicalize_skill(skill_name):
    """
    Maps abbreviations and casing aliases to clean canonical display name.
    """
    clean = skill_name.strip()
    clean_lower = clean.lower()
    if clean_lower in SKILL_ALIASES:
        return SKILL_ALIASES[clean_lower]
    return clean


def extract_skills_offline(text):
    """
    Extracts skills using word-boundary safe regex against data/skills.csv.
    Handles tricky punctuation boundaries (+, #, ., /, -).
    """
    if not text:
        return []

    detected = set()
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "skills.csv")
    if not os.path.exists(csv_path):
        csv_path = "data/skills.csv"

    skills_list = []
    try:
        df = pd.read_csv(csv_path)
        skills_list = df["skill"].dropna().tolist()
    except Exception:
        skills_list = list(SKILL_CATEGORY_MAP.keys())

    # Pre-pad text with spaces to make boundary matching easy
    padded_text = f" {text} "

    for raw_skill in skills_list:
        skill = raw_skill.strip()
        if not skill:
            continue

        escaped = re.escape(skill)
        # Handle special characters like C++, C#, .NET, Node.js, CI/CD
        if any(c in skill for c in "+#./-"):
            pattern = r"(?:^|[\s,;:()[\]{}|/])" + escaped + r"(?:$|[\s,;:()[\]{}|/])"
        else:
            pattern = r"\b" + escaped + r"\b"

        if re.search(pattern, padded_text, re.IGNORECASE):
            canonical = canonicalize_skill(skill)
            detected.add(canonical)

    return sorted(list(detected))


def extract_categorized_skills(text, api_key=None, model_name=None):
    """
    Extracts and categorizes skills into semantic groups.
    If Gemini is active, uses structured AI categorization.
    Falls back to dictionary taxonomy mapping offline.
    """
    # Try Gemini First if key provided
    if configure_gemini(api_key):
        try:
            profile = parse_full_resume_with_gemini(text, api_key=api_key, model_name=model_name)
            if profile and "skills_by_category" in profile and profile["skills_by_category"]:
                cleaned_profile_skills = {}
                for cat, sk_list in profile["skills_by_category"].items():
                    if isinstance(sk_list, list) and sk_list:
                        cleaned_profile_skills[cat] = sorted(list(set(sk_list)))
                if cleaned_profile_skills:
                    return cleaned_profile_skills
        except Exception:
            pass

    # Fallback: Offline Categorization
    offline_skills = extract_skills_offline(text)
    categorized = {
        "Programming Languages": [],
        "Frameworks & Libraries": [],
        "Cloud, DevOps & Tools": [],
        "Databases & Storage": [],
        "AI, ML & Data Science": [],
        "Architecture & Methodologies": []
    }

    for skill in offline_skills:
        cat = SKILL_CATEGORY_MAP.get(skill, "Architecture & Methodologies")
        if cat in categorized:
            if skill not in categorized[cat]:
                categorized[cat].append(skill)
        else:
            categorized["Architecture & Methodologies"].append(skill)

    # Remove empty categories
    return {k: sorted(v) for k, v in categorized.items() if v}


def extract_skills(text, api_key=None, model_name=None):
    """
    Backward-compatible flat skill list extractor.
    Returns deduplicated, sorted list of skills.
    """
    categorized = extract_categorized_skills(text, api_key=api_key, model_name=model_name)
    flat = []
    for cat_list in categorized.values():
        flat.extend(cat_list)
    return sorted(list(set(flat)))