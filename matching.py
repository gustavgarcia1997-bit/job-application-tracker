"""Pure matching logic: easy to understand and unit-test without a database."""
import json
import re


def normalize_skill(skill):
    return re.sub(r"\s+", " ", str(skill).strip()).casefold()


def split_skills(text):
    """Accept a comma-separated list while removing duplicates and empty values."""
    seen = set()
    result = []
    for raw in str(text or "").split(","):
        skill = raw.strip()
        normalized = normalize_skill(skill)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(skill)
    return result


def read_json(value):
    """MySQL JSON fields may be returned as strings or already-decoded objects."""
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, ValueError):
        return {}


def required_skills(requirements):
    skills = read_json(requirements).get("skills", [])
    if isinstance(skills, str):
        return split_skills(skills)
    if isinstance(skills, list):
        return split_skills(",".join(str(s) for s in skills))
    return []


def job_match(user_skills, job_requirements):
    """Return a 0-100 match percent plus matched/missing skills.

    The denominator is the number of distinct skills required by the job.
    A job with no specified skills gets score None ("Not specified").
    """
    needed = required_skills(job_requirements)
    mine = {normalize_skill(skill) for skill in user_skills}
    matched = [s for s in needed if normalize_skill(s) in mine]
    missing = [s for s in needed if normalize_skill(s) not in mine]
    percent = round(100 * len(matched) / len(needed)) if needed else None
    return {"score": percent, "matched": matched, "missing": missing, "required": needed}
