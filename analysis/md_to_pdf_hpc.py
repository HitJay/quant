"""MD 转 PDF — 付费深度研报 (NotoSansSC + Droid Sans Fallback)"""
import sys
from pathlib import Path
from markdown_it import MarkdownIt
from weasyprint import HTML

if len(sys.argv) < 3:
    print("用法: python md_to_pdf_hpc.py <input.md> <output.pdf>")
    sys.exit(1)

md_path = Path(sys.argv[1])
pdf_path = Path(sys.argv[2])

md_content = md_path.read_text(encoding="utf-8")

md = MarkdownIt("commonmark", {"html": True}).enable("table")
html_body = md.render(md_content)

# 字体：用户家目录 NotoSansSC + 系统 Droid Sans Fallback
fd_user = "/home/QYJI/.fonts"
fd_droid = "/usr/share/fonts/google-droid"

html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {{
    font-family: 'SansSC';
    src: url('file://{fd_user}/NotoSansSC-Regular.otf');
    font-weight: normal;
}}
@font-face {{
    font-family: 'SansSC';
    src: url('file://{fd_user}/NotoSansSC-Bold.otf');
    font-weight: bold;
}}
@font-face {{
    font-family: 'DroidFallback';
    src: url('file://{fd_droid}/DroidSansFallback.ttf');
}}

@page {{
    size: A4;
    margin: 2.2cm 2cm 2cm 2cm;
    @bottom-right {{
        content: counter(page) " / " counter(pages);
        font-size: 9pt;
        color: #888;
        font-family: 'SansSC', sans-serif;
    }}
    @bottom-left {{
        content: "复旦杰伦 · 反共识研究";
        font-size: 9pt;
        color: #888;
        font-family: 'SansSC', sans-serif;
    }}
}}

body {{
    font-family: 'SansSC', 'DroidFallback', sans-serif;
    font-size: 10.5pt;
    line-height: 1.75;
    color: #1f2937;
}}

h1 {{
    font-family: 'SansSC', sans-serif;
    font-size: 22pt;
    color: #0f172a;
    border-bottom: 3px solid #dc2626;
    padding-bottom: 12px;
    margin-top: 0;
    font-weight: bold;
    page-break-after: avoid;
}}

h2 {{
    font-family: 'SansSC', sans-serif;
    font-size: 15pt;
    color: #1e293b;
    border-left: 5px solid #dc2626;
    padding-left: 14px;
    margin-top: 30px;
    font-weight: bold;
    page-break-after: avoid;
}}

h3 {{
    font-family: 'SansSC', sans-serif;
    font-size: 12.5pt;
    color: #334155;
    margin-top: 18px;
    font-weight: bold;
    page-break-after: avoid;
}}

p {{ margin: 10px 0; }}

blockquote {{
    background: #fef2f2;
    border-left: 4px solid #dc2626;
    padding: 12px 16px;
    margin: 16px 0;
    color: #444;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9.5pt;
    font-family: 'SansSC', 'DroidFallback', sans-serif;
    page-break-inside: avoid;
}}

th {{
    background: #0f172a;
    color: white;
    padding: 8px 10px;
    text-align: left;
    font-weight: bold;
}}

td {{
    padding: 6px 10px;
    border-bottom: 1px solid #e2e8f0;
}}

tr:nth-child(even) td {{ background: #f8fafc; }}

strong {{ color: #b91c1c; font-weight: bold; }}

hr {{
    border: none;
    border-top: 1px solid #cbd5e1;
    margin: 30px 0;
}}

ul, ol {{ padding-left: 22px; }}
li {{ margin: 5px 0; line-height: 1.7; }}

code {{
    background: #f1f5f9;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 9.5pt;
    font-family: 'DroidFallback', monospace;
}}

pre {{
    background: #0f172a;
    color: #e2e8f0;
    padding: 12px 14px;
    border-radius: 4px;
    font-size: 8.5pt;
    line-height: 1.5;
    overflow-x: auto;
    page-break-inside: avoid;
}}

pre code {{
    background: transparent;
    color: inherit;
    padding: 0;
}}

em {{ color: #64748b; }}

/* 首页摘要框 */
h1 + p, h2:first-of-type ~ p:first-of-type {{
    background: #fef9c3;
    border-radius: 4px;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

HTML(string=html_full).write_pdf(str(pdf_path))
print(f"PDF: {pdf_path}")
print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB")
