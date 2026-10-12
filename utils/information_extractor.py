import re
from datetime import datetime


def extract_email(text):
    """
    Extracts email address using standard RFC-compliant regex.
    """
    if not text:
        return "Not Found"
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group().strip().rstrip(".,;:") if match else "Not Found"


def extract_phone(text):
    """
    Extracts phone numbers supporting international formats (+1, +44, +91, E.164),
    parentheses, spaces, and hyphens.
    """
    if not text:
        return "Not Found"
    patterns = [
        r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}",
        r"(\+91[-\s]?)?[6-9]\d{9}",
        r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cleaned = match.group().strip()
            digits = re.sub(r"\D", "", cleaned)
            if 7 <= len(digits) <= 15:
                return cleaned
    return "Not Found"


def extract_linkedin(text):
    """
    Extracts LinkedIn profile URL or handle.
    """
    if not text:
        return "Not Found"
    match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?", text, re.IGNORECASE)
    if match:
        return match.group().strip().rstrip("/")
    short_match = re.search(r"(?:linkedin\.com/in/)([A-Za-z0-9_-]+)", text, re.IGNORECASE)
    if short_match:
        return f"https://www.linkedin.com/in/{short_match.group(1).rstrip('/')}"
    return "Not Found"


def extract_github(text):
    """
    Extracts GitHub profile URL or username.
    """
    if not text:
        return "Not Found"
    match = re.search(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_-]+/?", text, re.IGNORECASE)
    if match:
        return match.group().strip().rstrip("/")
    short_match = re.search(r"(?:github\.com/)([A-Za-z0-9_-]+)", text, re.IGNORECASE)
    if short_match:
        return f"https://github.com/{short_match.group(1).rstrip('/')}"
    return "Not Found"


def extract_portfolio(text):
    """
    Extracts portfolio, website, or personal blog URL.
    """
    if not text:
        return "Not Found"
    match = re.search(r"https?://[A-Za-z0-9.-]+\.(?:dev|io|me|app|tech|org|com)(?:/[^\s,]+)?", text, re.IGNORECASE)
    if match:
        url = match.group().strip().rstrip("/")
        if "linkedin.com" not in url and "github.com" not in url:
            return url
    return "Not Found"


def extract_location(text):
    """
    Extracts city, state/country heuristic from the header block.
    """
    if not text:
        return "Not Found"

    lines = [line.strip() for line in text.split("\n")[:10] if line.strip()]
    city_state_pattern = r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2}\b|[A-Z][a-z]+)\b"

    for line in lines:
        if any(w in line.lower() for w in ["summary", "experience", "education", "skills", "technologies"]):
            continue
        # Split only on separators like |, •, ·, ;, not commas
        parts = re.split(r"[|•·;]", line)
        for part in parts:
            part = part.strip()
            if not re.search(r"@|\.com|\d{5,}", part):
                loc_m = re.search(city_state_pattern, part)
                if loc_m:
                    return loc_m.group(0).strip()
        
        loc_m = re.search(city_state_pattern, line)
        if loc_m and not re.search(r"@|\.com", loc_m.group(0)):
            return loc_m.group(0).strip()

    return "Not Specified"


def extract_name_heuristic(text):
    """
    Offline heuristic to identify candidate full name from top lines of resume.
    Avoids titles, contact lines, and common section headers.
    """
    if not text:
        return "Candidate"

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    ignore_words = {
        "resume", "curriculum vitae", "cv", "page", "email", "phone", "profile",
        "contact", "summary", "experience", "education", "skills", "projects",
        "developer", "engineer", "scientist", "manager", "architect", "analyst"
    }

    # Explicit name pattern
    for line in lines[:8]:
        name_match = re.search(r"(?:name|candidate)\s*[:\-]\s*([A-Za-z\s.'-]+)", line, re.IGNORECASE)
        if name_match:
            cand = name_match.group(1).strip()
            if 2 <= len(cand.split()) <= 4:
                return cand.title()

    # Top non-empty lines
    for line in lines[:6]:
        if "@" in line or "http" in line or "www." in line or "|" in line or "•" in line:
            continue
        words = line.split()
        if 2 <= len(words) <= 4:
            if any(w.lower() in ignore_words for w in words):
                continue
            if all(re.match(r"^[A-Za-z][a-zA-Z.'-]*$", w) for w in words):
                return " ".join(words).title()

    return "Candidate"


def estimate_experience_years(text):
    """
    Estimates total professional experience in years by prioritizing explicit statements,
    then falling back to date span analysis.
    """
    if not text:
        return 0

    # 1. Prioritize explicit statements e.g. "5+ years of experience"
    exp_match = re.search(r"(\d+)\+?\s*(?:years|yrs)(?:\s+of)?\s+(?:professional\s+)?experience", text, re.IGNORECASE)
    if exp_match:
        val = int(exp_match.group(1))
        if 1 <= val <= 40:
            return val

    current_year = datetime.now().year
    # Match years like 1990 - 2026
    years = [int(y) for y in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
    if not years:
        return 0

    valid_years = [y for y in years if 1980 <= y <= current_year + 1]
    if not valid_years:
        return 0

    has_present = bool(re.search(r"\b(present|current|now)\b", text, re.IGNORECASE))
    min_year = min(valid_years)
    max_year = current_year if has_present else max(valid_years)

    span = max_year - min_year
    return max(0, min(span, 35))


def extract_all_contact_info(text):
    """
    Master extractor combining regex and heuristics for offline profiling.
    """
    return {
        "full_name": extract_name_heuristic(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text),
        "portfolio": extract_portfolio(text),
        "estimated_exp_years": estimate_experience_years(text)
    }