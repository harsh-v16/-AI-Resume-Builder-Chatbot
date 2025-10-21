# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from resume_generator import generate_resume
from pdf_util import generate_resume_pdf
import json

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Resume Builder", page_icon="🧠", layout="centered")
st.title("🤖 AI Resume Builder Chatbot")

# Check API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OpenAI API key not found. Add it in your .env file as OPENAI_API_KEY.")
    st.stop()

# Maintain session
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = None

# -------------------- INPUT FORM --------------------
with st.form("resume_form"):
    st.subheader("📋 Enter Your Details")
    name = st.text_input("Full Name")
    contact = st.text_input("Contact Number (optional)")
    email = st.text_input("Email Address")
    linkedin = st.text_input("LinkedIn URL (optional)")
    github = st.text_input("GitHub URL (optional)")
    portfolio = st.text_input("Portfolio URL (optional)")
    target_role = st.text_input("🎯 Target Job Role (e.g., Software Developer)")

    education = st.text_area("🎓 Education (degree, institute, dates)")
    experience = st.text_area("💼 Experience (company, role, dates, bullets)")
    projects = st.text_area("🚀 Projects (title, short description, tools — use [Title](https://...) for links)")
    skills = st.text_area("🧠 Technical Skills (comma separated)")
    achievements = st.text_area("🏆 Achievements / Certifications (optional)")

    submitted = st.form_submit_button("Generate Resume")

# -------------------- HELPER FUNCTION --------------------
def build_header(name, role, contact, email, linkedin, github, portfolio):
    parts = []
    if name and role:
        parts.append(f"{name} | {role}")
    elif name:
        parts.append(name)
    if contact:
        parts.append(contact)
    if email:
        parts.append(email)
    if linkedin:
        parts.append(f"[LinkedIn]({linkedin})")
    if github:
        parts.append(f"[GitHub]({github})")
    if portfolio:
        parts.append(f"[Portfolio]({portfolio})")
    return " | ".join(parts)

# -------------------- GENERATION --------------------
if submitted:
    if not name or not email or not target_role:
        st.warning("Please fill in at least your name, email, and target role.")
    else:
        with st.spinner("🧠 Generating your professional resume..."):
            user_data = {
                "name": name,
                "contact": contact,
                "email": email,
                "linkedin": linkedin,
                "github": github,
                "portfolio": portfolio,
                "target_role": target_role,
                "education": education,
                "experience": experience,
                "projects": projects,
                "skills": skills,
                "achievements": achievements,
            }

            try:
                resume_text = generate_resume(user_data)
                # Clean markdown fences if model returns them
                resume_text = resume_text.replace("```markdown", "").replace("```", "").strip()

                header_line = build_header(name, target_role, contact, email, linkedin, github, portfolio)
                if header_line not in resume_text:
                    resume_text = header_line + "\n\n" + resume_text

                st.session_state.generated_resume = resume_text
                st.success("✅ Resume generated successfully!")
            except Exception as e:
                st.error("Error generating resume.")
                st.exception(e)

# -------------------- PREVIEW + PDF --------------------
# -------------------- PREVIEW + PDF --------------------
if st.session_state.generated_resume:
    st.markdown("### 📝 Resume Preview")
    st.markdown(st.session_state.generated_resume, unsafe_allow_html=True)

    # ✅ FIX: Ensure resume_text is not None or empty
    if isinstance(st.session_state.generated_resume, str) and st.session_state.generated_resume.strip():
        try:
            # --- MANUAL EDIT & PREVIEW BLOCK START ---
            st.subheader("📝 Preview & Edit Resume Before Download")

# Let user review and tweak the resume before final generation
            edited_resume = st.text_area(
    "Make final edits to your resume below (optional):",
                value=st.session_state.generated_resume,
                height=600,
            )

            pdf_data = None

            if st.button("Generate Final PDF"):
                pdf_data = generate_resume_pdf(edited_resume)
                st.download_button(
                    label="📄 Download Final Resume (PDF)",
                    data=pdf_data,
                    file_name=f"{st.session_state.get('name','resume').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
            if pdf_data is not None and isinstance(pdf_data, bytes):
                pass
# --- MANUAL EDIT & PREVIEW BLOCK END ---

            if isinstance(pdf_data, bytes):  # because your pdf_util returns bytes when buffer used
                st.download_button(
                    label="📄 Download Resume (PDF)",
                    data=pdf_data,
                    file_name=f"{name.replace(' ', '_')}_resume.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("PDF could not be generated. Please try again.")
        except Exception as e:
            st.error("PDF generation failed. Please check logs for details.")
            st.exception(e)
    else:
        st.warning("Resume text is empty — cannot generate PDF.")

st.markdown("---")
st.caption("Built with Streamlit + OpenAI + ReportLab")
