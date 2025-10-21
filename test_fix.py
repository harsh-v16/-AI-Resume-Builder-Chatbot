import re

text = """
Programming Languages & Frameworks: bJava/b, bC++/b, bPython/b, bJavaScript/b, bReact/b, bNode.js/b, bSpring Boot/b, bExpress.js/b, bAngular.js/b, bDjango/b
Databases: bPostgreSQL/b
Tools: bJProfiler/b
Testing & Debugging: bJUnit/b, bMockito/b
"""

clean_text = re.sub(
    r"(?i)(?:^|(?<=\s))b([A-Za-z0-9\.\+\#\-\_ ]+?)\/b(?=$|(?=\s|,|\.|;|:|</))",
    r"<b>\1</b>",
    text,
)

print(clean_text)
