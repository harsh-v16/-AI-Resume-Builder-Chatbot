# resume_generator.py — Fully updated for openai>=1.0.0
import os
import time
import logging
import re
from dotenv import load_dotenv
from openai import OpenAI

from prompts import resume_system_prompt, enrichment_prompt_prefix
from skill_expander import expand_skills

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PRIMARY_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FALLBACK_MODEL = "gpt-3.5-turbo"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _call_chat(messages, model=PRIMARY_MODEL, max_retries=2, temperature=0.6, max_tokens=900):
    """
    Wrapper for OpenAI chat calls with retry + fallback handling.
    """
    last_exc = None
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"⚠️ Attempt {attempt+1} failed: {e}")
            last_exc = e
            time.sleep(1 + attempt * 2)

    try:
        resp = client.chat.completions.create(
            model=FALLBACK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logging.error("Fallback also failed", exc_info=e)
        raise last_exc or e


def _infer_seniority(user_inputs: dict) -> str:
    """
    Estimate seniority level based on explicit selection or experience content.
    """
    sel = user_inputs.get("seniority", "Auto")
    if sel != "Auto":
        if "Senior" in sel:
            return "Senior"
        if "Mid" in sel:
            return "Mid"
        if "Junior" in sel:
            return "Junior"

    exp = user_inputs.get("experience", "")
    years = 0
    years_found = re.findall(r"(\d{4})\s*[–-]\s*(\d{4}|Present|present)", exp)
    for start, end in years_found:
        try:
            s = int(start)
            e = int(end) if end.isdigit() else 2025
            years += max(0, e - s)
        except:
            continue

    yrs_keywords = re.search(r"(\d+)\s*\+?\s*yr", exp)
    if yrs_keywords:
        years = max(years, int(yrs_keywords.group(1)))

    if years >= 5:
        return "Senior"
    elif 3 <= years < 5:
        return "Mid"
    elif years > 0:
        return "Junior"
    else:
        return "Mid"


def _clean_md(md: str) -> str:
    """
    Clean markdown (remove extra blank lines).
    """
    lines = [l.rstrip() for l in md.splitlines()]
    out = []
    blank = 0
    for l in lines:
        if l.strip() == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(l)
    return "\n".join(out).strip()


def _enrich_experience(raw_experience: str, target_role: str, seniority: str, skills: str) -> str:
    """
    Converts user’s raw text experience into strong, measurable bullet points.
    """
    if not raw_experience.strip():
        return ""

    lines = [l.strip() for l in re.split(r"\n+", raw_experience) if l.strip()]
    grouped = []
    current = []
    for l in lines:
        if re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})\b", l) and "–" in l:
            if current:
                grouped.append(current)
            current = [l]
        else:
            current.append(l)
    if current:
        grouped.append(current)

    enriched_sections = []
    for group in grouped:
        header = group[0] if group else ""
        raw_lines = "\n".join(group[1:]) if len(group) > 1 else "\n".join(group)

        prompt = enrichment_prompt_prefix.format(seniority=seniority, role=target_role, skills=skills)
        prompt += "\nRAW:\n"
        for rl in raw_lines.split("\n"):
            if rl.strip():
                prompt += f"- {rl.strip()}\n"

        messages = [
            {"role": "system", "content": "You rewrite experience lines into professional, metrics-based bullets."},
            {"role": "user", "content": prompt}
        ]

        try:
            out = _call_chat(messages, temperature=0.35, max_tokens=400)
        except Exception:
            bullets = []
            for rl in raw_lines.split("\n"):
                t = rl.strip().lstrip("-•")
                if t:
                    bullets.append(f"• {t}")
            out = "\n".join(bullets)

        section_text = header + "\n" + out
        enriched_sections.append(section_text.strip())

    return "\n\n".join(enriched_sections)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def generate_resume(user_inputs: dict) -> str:
    """
    Generate a professional, ATS-friendly Markdown resume.
    """
    name = user_inputs.get("name", "")
    target_role = user_inputs.get("target_role", "")
    skills = user_inputs.get("skills", "")
    experience = user_inputs.get("experience", "")
    projects = user_inputs.get("projects", "")
    education = user_inputs.get("education", "")
    achievements = user_inputs.get("achievements", "")
    contact = user_inputs.get("contact", "")
    email = user_inputs.get("email", "")
    linkedin = user_inputs.get("linkedin", "")
    github = user_inputs.get("github", "")
    portfolio = user_inputs.get("portfolio", "")

    seniority = _infer_seniority(user_inputs)

    # Expand skills
    try:
        expanded = expand_skills(skills, target_role) if skills else ""
    except Exception:
        expanded = ""

    all_skills = skills
    if expanded:
        all_list = [s.strip() for s in (skills + "," + expanded).split(",") if s.strip()]
        seen = set()
        dedup = []
        for s in all_list:
            key = s.lower()
            if key not in seen:
                dedup.append(s)
                seen.add(key)
        all_skills = ", ".join(dedup)

    # Enrich experience
    enriched_exp = _enrich_experience(experience, target_role, seniority, all_skills)

    # Detect low experience (NEW)
    is_low_exp = not enriched_exp.strip() or len(enriched_exp.split()) < 80

    # Header line
    links = []
    if linkedin:
        links.append(f"[LinkedIn]({linkedin})")
    if github:
        links.append(f"[GitHub]({github})")
    if portfolio:
        links.append(f"[Portfolio]({portfolio})")

    header_parts = [name, target_role, contact or "", email]
    header = " | ".join([p for p in header_parts if p])
    if links:
        header += " | " + " | ".join(links)

    # Full prompt
    instruction = resume_system_prompt + "\n\n"
    instruction += f"USER DATA:\nName: {name}\nRole: {target_role}\nSeniority: {seniority}\n"
    instruction += f"Contact: {contact}\nEmail: {email}\nSkills: {all_skills}\n"
    instruction += f"Education: {education}\nAchievements: {achievements}\nProjects: {projects}\n\n"
    instruction += "Use the provided enriched experience below for the 'Professional Experience' section.\n\n"
    instruction += "ENRICHED EXPERIENCE:\n" + (enriched_exp or experience or "No experience provided.\n")

    # NEW: if low experience, tell GPT to fill page naturally
    if is_low_exp:
        instruction += (
            "\n\nNOTE: The candidate has limited professional experience. "
            "Make sure the resume still looks like a full, rich one-page professional document. "
            "Expand the Professional Summary with technical exposure, teamwork, learning attitude, and relevant projects. "
            "Add more detail to Technical Skills and Projects/Achievements to ensure the layout fills one page naturally "
            "but does not exceed one page. Keep the same section structure and formatting."
        )

    messages = [
        {"role": "system", "content": "You are a world-class resume writer specialized in software roles."},
        {"role": "user", "content": instruction},
    ]

    result = _call_chat(messages, temperature=0.35, max_tokens=1200)
    result = result.replace("\r\n", "\n")
    result = _clean_md(result)

    if "## Education" in result:
        edu_match = re.search(r"## Education(.*?)(##|$)", result, re.S)
        if edu_match:
            edu_text = edu_match.group(1).strip()
            edu_lines = [ln.strip() for ln in edu_text.splitlines() if ln.strip()]
            formatted_edu = ""

            # Try to split each entry into 3 lines (University / Date+Location / Degree)
            for line in edu_lines:
                parts = re.split(r"\s*\|\s*", line)
                if len(parts) == 3:
                    university, date_loc, degree = parts
                    formatted_edu += f"{university.strip()}\n{date_loc.strip()}\n{degree.strip()}\n\n"
                elif len(parts) == 2:
                    left, right = parts
                    formatted_edu += f"{left.strip()}\n{right.strip()}\n\n"
                else:
                    formatted_edu += f"{line.strip()}\n"

            # Replace the section text in result
            result = result.replace(edu_text, formatted_edu.strip())

    if header.split("|")[0].strip().lower() not in result.splitlines()[0].lower():
        result = header + "\n\n" + result

    return result

