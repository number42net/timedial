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
from jinja2 import Template

CONTENT_DIR = Path("content")
TEMPLATE_PATH = Path("base.html")
OUTPUT_DIR = Path("../html")

# Load HTML template
with open(TEMPLATE_PATH, encoding="utf-8") as f:
    base_template = Template(f.read())

OUTPUT_DIR.mkdir(exist_ok=True)


def clean_up(html: str) -> str:
    """Clean-up the HTML with indendations and fix links."""
    final = []
    for line in html.split("\n"):
        line = line.replace('.md">', '.html">')
        line = line.replace("<br />", "<br>")
        if line.strip()[:-2].endswith("</h"):
            line = "\n" + line
        final.append(line)

    return "\n".join(final)


for md_file in CONTENT_DIR.glob("*.md"):
    print(f"Processing: {md_file}")
    try:
        with open(md_file, encoding="utf-8") as f:
            md_content = f.read()

        for number, line in enumerate(md_content.split("\n")):
            if not line.isascii():
                result = [(i, c) for i, c in enumerate(line) if ord(c) >= 128]
                print(f"Found non-ascii character on line: {number + 1} col: {result[0][0] + 1}: {result[0][1]}")
                exit(1)

        html_content = markdown.markdown(md_content, extensions=["fenced_code"])

        title = f"TimeDial {md_file.stem.capitalize()}"
        rendered_html = base_template.render(title=title, content=clean_up(html_content))

        output_path = OUTPUT_DIR / f"{md_file.stem}.html"
        with open(output_path, "w", encoding="ascii") as f:
            f.writelines(rendered_html)

        print(f"Generated: {output_path}")

    except Exception as e:
        print(f"Error processing {md_file.name}: {e}")
