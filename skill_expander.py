# skill_expander.py — Updated for openai>=1.0.0
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def expand_skills(skills: str, target_role: str = "") -> str:
    """
    Expands user-provided skills into related or advanced skills for that target role.
    Returns a comma-separated list.
    """
    if not skills:
        return ""

    prompt = f"""
User skills: {skills}
Target role: {target_role}

Suggest 6–10 advanced or related professional skills, frameworks, or tools.
Return as a comma-separated list only (no sentences).
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150,
        )
        text = resp.choices[0].message.content.strip()
        return text.replace("\n", " ").strip()
    except Exception as e:
        print("⚠️ Skill expansion failed:", e)
        # fallback suggestion logic
        base = [s.strip().lower() for s in skills.split(",") if s.strip()]
        extra = []
        if "python" in ",".join(base):
            extra += ["Django", "Flask", "FastAPI", "NumPy", "Pandas"]
        if "java" in ",".join(base):
            extra += ["Spring Boot", "Hibernate", "Maven", "Jenkins"]
        if "aws" in ",".join(base):
            extra += ["Docker", "Kubernetes", "Terraform", "CI/CD"]
        return ", ".join(list(dict.fromkeys(extra)))
