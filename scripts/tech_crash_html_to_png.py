#!/usr/bin/env python3
"""HTML → PNG: weasyprint (PDF) → PyMuPDF (PNG)"""

import os, io, re
from weasyprint import HTML
import fitz

HTML_PATH = "/workspace/output/tech-crash-risk/tech_crash_risk.html"
OUT_DIR = "/workspace/output/tech-crash-risk"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    full_html = f.read()

parts = full_html.split('<div class="card">')
header = parts[0]

for i, part in enumerate(parts[1:]):
    card_body = part[:part.rfind('</div>')]
    single = f"""{header}
<style>body {{ padding:0; gap:0; }} @page {{ margin:0; size:600px 800px; }}</style>
<div class="card">
{card_body}
</div>
</body></html>"""

    pdf_bytes = HTML(string=single).write_pdf()
    doc = fitz.open("pdf", pdf_bytes)
    page = doc[0]
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)

    path = os.path.join(OUT_DIR, f"{i:02d}_card.png")
    pix.save(path)
    doc.close()

    sz = os.path.getsize(path) // 1024
    print(f"  {i:02d}_card.png ({sz} KB)")

print(f"\nDone: {OUT_DIR}/")
