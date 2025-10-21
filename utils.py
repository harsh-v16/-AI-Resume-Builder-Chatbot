import re
import openai
import logging

# You can adjust this to your own API setup if you’re using OpenAI or another LLM
def _call_chat(messages, temperature=0.4, max_tokens=800):
    """
    Generic wrapper for LLM calls.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Error in _call_chat: {e}")
        return ""


def _clean_md(text):
    """
    Cleans Markdown or extra formatting before rendering to PDF.
    """
    if not text:
        return ""
    # Remove markdown bold/italics, headers, links
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"#+\s*", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = text.replace("•", "•")  # keep bullet
    return text.strip()


def _enrich_experience(experience_text, target_role, seniority, all_skills):
    """
    Optionally enriches experience section using LLM.
    Expands short experiences into 2–3 strong bullet points.
    """
    try:
        if not experience_text.strip():
            return ""

        messages = [
            {
                "role": "system",
                "content": "You are a professional resume writer. Expand and format experiences into strong, quantified bullet points.",
            },
            {
                "role": "user",
                "content": f"Role: {target_role}\nSeniority: {seniority}\nSkills: {all_skills}\n\nExperience:\n{experience_text}\n\nExpand this into 2–4 concise, action-oriented bullet points with metrics.",
            },
        ]
        enriched = _call_chat(messages, temperature=0.5, max_tokens=500)
        return enriched.strip() if enriched else experience_text
    except Exception as e:
        logging.error(f"Error in _enrich_experience: {e}")
        return experience_text
