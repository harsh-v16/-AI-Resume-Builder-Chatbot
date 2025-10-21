from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import re, random

def generate_resume_pdf(resume_text: str, output_path: str = None):
    buffer = BytesIO()

    # Document config (unchanged)
    doc = SimpleDocTemplate(
        output_path or buffer,
        pagesize=letter,
        topMargin=25,
        bottomMargin=25,
        leftMargin=38,
        rightMargin=38,
        title="Resume"
    )

    styles = getSampleStyleSheet()

    # Base styles (Helvetica core fonts assumed available)
    normal = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=12,
        textColor=colors.black,
    )
    bold_enabled = ParagraphStyle(
        "BoldEnabled",
        parent=normal,
        fontName="Helvetica",
        fontSize=10.5,
        leading=12,
        textColor=colors.black,
    )

    # --- TECHNICAL SKILLS styles (category label slightly larger + bold; skills smaller) ---
    skill_label_style = ParagraphStyle(
        "SkillLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.2,   # slightly larger label
        leading=12,
        textColor=colors.black,
    )
    skill_text_style = ParagraphStyle(
        "SkillText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,    # smaller skill list to help fit on one line
        leading=10,
        textColor=colors.black,
    )

    # Professional Summary bullet style (tighter)
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=bold_enabled,
        leftIndent=10,
        bulletIndent=6,
        spaceBefore=0,   # tightened
        spaceAfter=0,    # tightened
        leading=10,
    )
    # ✅ Fine-tune bullet section appearance (Professional Summary)
    bullet_style.fontSize = 10.5
    bullet_style.leading = 10.4

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#001F5B"),
        leading=13,
        spaceBefore=6,
        spaceAfter=2,
    )
    name_style = ParagraphStyle(
        "Name",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=colors.black,
        spaceAfter=1,
    )
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=11,
        textColor=colors.black,
        italic=True,
        spaceAfter=1,
    )
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=9.8,
        textColor=colors.black,
        spaceAfter=0.5,
    )

    elements = []

    # Header (unchanged)
    name = "Shubham Shrotriya"
    title = "Software Developer"
    contact_html = (
        '<a href="tel:+19514659910" color="black">+1 (951) 465-9910</a> | '
        '<a href="mailto:shubhamshrotriya31@gmail.com" color="black">shubhamshrotriya31@gmail.com</a> | '
        '<a href="https://www.linkedin.com/in/shubhamshrotriya" color="black">LinkedIn</a> | '
        '<a href="https://github.com/shubhamshrotriya16427" color="black">GitHub</a> | '
        '<a href="https://shubhamshro.my.canva.site" color="black">Portfolio</a>'
    )
    elements.append(Paragraph(f"<b>{name}</b>", name_style))
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(contact_html, contact_style))
    elements.append(Spacer(1, 1.5))

    raw = resume_text or ""
    clean_text = re.sub(r"```(?:markdown)?|```", "", raw).strip()

    # Normalize bullets and markdown bold
    clean_text = re.sub(r"(?m)^[\-\*]\s+", "• ", clean_text)
    clean_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", clean_text)

    # Fix malformed literal tags like: bJava/b, bNode.js/b, etc.
    clean_text = re.sub(
        r"(?i)(?<!<)b([A-Za-z0-9\+\#\-\._ ]+?)\/b(?!>)",
        r"<b>\1</b>",
        clean_text,
    )

    # Smart bold engine
    def smart_bold(txt):
        txt = re.sub(r"(?<!<b>)(\d{1,3}(?:[,\d]{0,}|(?:\+))?(?:\s*(?:\+|%|years?|yrs?|projects?))?)(?!</b>)", r"<b>\1</b>", txt)
        patterns = [
            r"Spring\sBoot", r"Microservices", r"Node\.js", r"RESTful\sAPI", r"GraphQL",
            r"CI/CD", r"AWS", r"Azure", r"Docker", r"Kubernetes", r"PostgreSQL", r"MySQL",
            r"Redis", r"Kafka"
        ]
        for p in patterns:
            txt = re.sub(fr"(?<!<b>)\b({p})\b(?!</b>)", r"<b>\1</b>", txt, flags=re.IGNORECASE)
        verbs = ["Developed", "Built", "Created", "Designed", "Implemented", "Optimized",
                 "Improved", "Integrated", "Deployed", "Managed", "Automated", "Refactored"]
        for v in verbs:
            txt = re.sub(fr"(?<!<b>)\b({v})\b(?!</b>)", r"<b>\1</b>", txt, flags=re.IGNORECASE)
        techs = ["Java", "Python", "React", "Angular", "Spring", "SQL", "Linux", "Terraform", "Jenkins", "Git"]
        for t in techs:
            txt = re.sub(fr"(?<!<b>)\b({t})\b(?!</b>)", r"<b>\1</b>", txt, flags=re.IGNORECASE)
        return txt

    clean_text = smart_bold(clean_text)

    # 🔧 Fix unbalanced bold tags
    clean_text = re.sub(r"<b>([^<]*)<b>", r"<b>\1", clean_text)
    clean_text = re.sub(r"</b>([^>]*)</b>", r"</b>\1", clean_text)
    open_count = clean_text.count("<b>")
    close_count = clean_text.count("</b>")
    if open_count > close_count:
        clean_text += "</b>" * (open_count - close_count)
    elif close_count > open_count:
        clean_text = "<b>" * (close_count - open_count) + clean_text

    # Remove duplicates of header lines
    lines = clean_text.splitlines()
    filtered = []
    for ln in lines:
        lower = ln.strip().lower()
        if any(x in lower for x in ["linkedin", "github", "portfolio", "@gmail", "+1 (951)", "shubham shrotriya"]):
            continue
        filtered.append(ln)
    clean_text = "\n".join(filtered).strip()

    sections = re.split(r"\n(?=## )", clean_text)

    def expand_advanced_skills(base_text):
        pool = [
            "Kafka", "Prometheus", "Grafana", "Kibana", "ELK Stack", "Jenkins",
            "Terraform", "K8s", "Ansible", "Docker Swarm", "AWS CloudFormation",
            "SonarQube", "Datadog", "OpenShift", "Spring Cloud", "RabbitMQ", "Nginx"
        ]
        seed = abs(hash(base_text)) % 10000
        rnd = random.Random(seed)
        chosen = rnd.sample(pool, 8)
        return f"<b>Advanced Tools & Frameworks:</b> {', '.join(chosen)}"

    for section in sections:
        if not section.strip():
            continue
        if not section.strip().startswith("## "):
            continue

        header, *content_lines = section.strip().split("\n", 1)
        header_text = header.replace("##", "").strip().upper()

        elements.append(Paragraph(header_text, heading_style))
        elements.append(HRFlowable(width="100%", color=colors.black, thickness=0.8))
        elements.append(Spacer(1, 1))

        content = content_lines[0].strip() if content_lines else ""

        if header_text.lower() == "professional summary":
            bullets = re.split(r"•\s+|\n[-\*]\s+|\n", content)
            bullets = [b.strip() for b in bullets if b.strip()]
            items = [ListItem(Paragraph(b, bullet_style), bulletText="•") for b in bullets]
            elements.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    leftIndent=10,
                    spaceBefore=0,
                    spaceAfter=0,
                    bulletFontSize=10,
                    bulletOffsetY=-1.5,
                )
            )

        elif header_text.lower() == "technical skills":
            skill_lines = [ln.strip() for ln in content.splitlines() if ln.strip()]

            if len(skill_lines) == 1:
                raw_line = skill_lines[0]
                parts = re.split(r"\s{2,}|\s\|\s|\s-\s", raw_line)
                if len(parts) > 1:
                    skill_lines = [p.strip() for p in parts if p.strip()]

            bullet_items = []
            for ln in skill_lines:
                if ":" in ln:
                    left, right = ln.split(":", 1)
                    html = f"<b>{left.strip()}:</b> <font size=9>{right.strip()}</font>"
                else:
                    html = ln.replace('<', '').replace('>', '')
                bullet_items.append(ListItem(Paragraph(html, skill_text_style), bulletText="•"))

            elements.append(
                ListFlowable(
                    bullet_items,
                    bulletType="bullet",
                    leftIndent=10,
                    spaceBefore=0,
                    spaceAfter=0,
                    bulletFontSize=10,
                    bulletOffsetY=-1.5,
                )
            )
            elements.append(Spacer(1, 0.8))

        elif header_text.lower() in [
            "projects", "certifications", "achievements", "projects / certifications / achievements"
        ]:
            md_links = re.findall(r"\[(.*?)\]\((https?://[^\s)]+)\)", content)
            if md_links:
                for name, url in md_links:
                    disp = re.sub(r"</?b>", "", name)
                    html = f'<a href="{url}" color="black">{disp}</a>'
                    elements.append(Paragraph(html, bold_enabled))
                    elements.append(Spacer(1, 0.4))
            else:
                for ln in content.splitlines():
                    ln = ln.strip()
                    if not ln:
                        continue
                    m = re.search(r"(https?://[^\s]+)", ln)
                    if m:
                        url = m.group(1)
                        name_part = ln.replace(url, "").strip(" -–()")
                        if not name_part:
                            name_part = url
                        name_part = re.sub(r"</?b>", "", name_part)
                        html = f'<a href="{url}" color="black">{name_part}</a>'
                        elements.append(Paragraph(html, bold_enabled))
                    else:
                        elements.append(Paragraph(re.sub(r"</?b>", "", ln), bold_enabled))
                    elements.append(Spacer(1, 0.4))

        elif header_text.lower() == "professional experience":
            job_blocks = re.split(r"\n(?=[A-Z].*–.*\d{4})", content)
            for job in job_blocks:
                lines = [l.strip() for l in job.splitlines() if l.strip()]
                if not lines:
                    continue
                header_line = lines[0]
                m = re.match(r"^(.*?)(?:\s*\|\s*)(.*)$", header_line)
                if m:
                    left_text = m.group(1).strip()
                    right_text = m.group(2).strip()
                else:
                    left_text = header_line
                    right_text = ""
                formatted_line = f"<b>{left_text}</b>"
                elements.append(Paragraph(formatted_line, bold_enabled))
                if right_text:
                    right_para = Paragraph(
                        f'<font color="#6E6E6E" size=9>{right_text}</font>', normal
                    )
                    right_para.alignment = 2
                    elements.append(right_para)
                elements.append(Spacer(1, 0.4))
                bullets = [ln for ln in lines[1:] if ln.startswith("•") or ln.startswith("-")]
                for b in bullets:
                    clean_bullet = b.lstrip("•- ").strip()
                    elements.append(Paragraph(f"• {clean_bullet}", bullet_style))
                    elements.append(Spacer(1, 0.2))
                elements.append(Spacer(1, 6))

        elif header_text.lower() == "education":
            edu_lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
            i = 0
            while i < len(edu_lines):
                degree_line = edu_lines[i]
                date_line = edu_lines[i + 1] if i + 1 < len(edu_lines) else ""
                location_line = edu_lines[i + 2] if i + 2 < len(edu_lines) else ""
                elements.append(Paragraph(f"<b>{degree_line}</b>", bold_enabled))
                if date_line:
                    elements.append(
                        Paragraph(
                            f'<font color="#6E6E6E" size=9>{date_line}</font>', normal
                        )
                    )
                if location_line:
                    elements.append(Paragraph(location_line, normal))
                elements.append(Spacer(1, 6))
                i += 3

        else:
            paragraphs = [p.strip() for p in content.splitlines() if p.strip()]
            for p in paragraphs:
                elements.append(Paragraph(p, bold_enabled))
                elements.append(Spacer(1, 0.6))

        elements.append(Spacer(1, 1.2))

    doc.build(elements)

    if not output_path:
        buffer.seek(0)
        return buffer.getvalue()
