"""TimeDial project.

Copyright (c) Martin Miedema
Repository: https://github.com/number42net/timedial

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path

import markdown
import requests
from jinja2 import Template

CONTENT_DIR = Path("content")
TEMPLATE_PATH = Path("base.html")
OUTPUT_DIR = Path("../html")


def validate(html: str) -> None:
    """Validate the generated HTML using w3.org api."""
    files = files = {"uploaded_file": ("test.html", html, "text/html; charset=us-ascii")}
    response = requests.post("https://validator.w3.org/check", files=files, data={"doctype": "Inline", "output": "json"})

    result = response.json()
    if result["messages"]:
        for message in result["messages"]:
            for key, value in message.items():
                print(f"## {key}")
                print(value)
            print()
        exit(1)


def clean_up(html: str) -> str:
    """Clean-up the HTML with indendations and fix links."""
    final = []
    pre = False
    for line in html.split("\n"):
        # Replace .md links to .html
        line = line.replace('.md">', '.html">')
        # Replace html5 <br /> with html2 <br>
        line = line.replace("<br />", "<br>")
        # Add a HR in front of every H1
        line = line.replace("<h1>", "<hr><h1>")
        # Fix &quot; in <PRE> blocks
        if "<pre>" in line.lower():
            pre = True
        if "</pre>" in line.lower():
            pre = False
        if pre:
            line = line.replace("&quot;", '"')
        final.append(line)

    return "\n".join(final)


# Load HTML template
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    base_template = Template(f.read())

OUTPUT_DIR.mkdir(exist_ok=True)

# Load list of files
files = list(CONTENT_DIR.glob("*.md"))
files.sort()

# Generate all pages, ensure Index is always first
all_pages = [i.stem.capitalize() for i in files]
all_pages.remove("Index")
all_pages.insert(0, "Index")

for md_file in files:
    print(f"Processing: {md_file}")
    try:
        # Read markdown file
        with open(md_file, encoding="utf-8") as f:
            md_content = f.read()

        # Check for non-ascii characters
        for number, line in enumerate(md_content.split("\n")):
            if not line.isascii():
                result = [(i, c) for i, c in enumerate(line) if ord(c) >= 128]
                print(f"Found non-ascii character on line: {number + 1} col: {result[0][0] + 1}: {result[0][1]}")
                exit(1)

        # Convert Markdown to THML
        html_content = markdown.markdown(md_content, extensions=["fenced_code"])

        # Create page title and generate HTML
        title = md_file.stem.capitalize()
        rendered_html = base_template.render(title=title, all_pages=all_pages, content=clean_up(html_content))

        # Validate output
        validate(rendered_html)

        # Write output
        output_path = OUTPUT_DIR / f"{md_file.stem}.html"
        with open(output_path, "w", encoding="ascii") as f:
            f.writelines(rendered_html)

        print(f"Generated: {output_path}")

    except Exception as e:
        print(f"Error processing {md_file.name}: {e}")
