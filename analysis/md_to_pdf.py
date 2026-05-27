"""MD转PDF - 付费报告 (思源宋体+黑体)"""
from pathlib import Path
from markdown_it import MarkdownIt
from weasyprint import HTML

md_path = Path('output/commodity-rotation/paid_report.md')
pdf_path = Path('output/commodity-rotation/paid_report.pdf')

# 读取MD
md_content = md_path.read_text(encoding='utf-8')

# MD转HTML
md = MarkdownIt('commonmark', {'html': True}).enable('table')
html_body = md.render(md_content)

# 字体路径
fd = '/home/jay/.local/share/fonts'

html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@font-face {{
    font-family: 'SerifSC';
    src: url('file://{fd}/NotoSerifSC-Regular.otf');
    font-weight: normal;
}}
@font-face {{
    font-family: 'SerifSC';
    src: url('file://{fd}/NotoSerifSC-Bold.otf');
    font-weight: bold;
}}
@font-face {{
    font-family: 'SansSC';
    src: url('file://{fd}/NotoSansSC-Regular.otf');
    font-weight: normal;
}}
@font-face {{
    font-family: 'SansSC';
    src: url('file://{fd}/NotoSansSC-Bold.otf');
    font-weight: bold;
}}

@page {{
    size: A4;
    margin: 2cm;
    @bottom-center {{
        content: "第 " counter(page) " 页";
        font-size: 9pt;
        color: #999;
        font-family: 'SansSC', sans-serif;
    }}
}}

body {{
    font-family: 'SerifSC', serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #2d2d2d;
}}

h1 {{
    font-family: 'SansSC', sans-serif;
    font-size: 24pt;
    color: #1a1a2e;
    border-bottom: 3px solid #00aa66;
    padding-bottom: 12px;
    margin-top: 30px;
    font-weight: bold;
}}

h2 {{
    font-family: 'SansSC', sans-serif;
    font-size: 16pt;
    color: #2d2d44;
    border-left: 5px solid #00aa66;
    padding-left: 14px;
    margin-top: 30px;
    font-weight: bold;
}}

h3 {{
    font-family: 'SansSC', sans-serif;
    font-size: 13pt;
    color: #3d3d6b;
    margin-top: 20px;
    font-weight: bold;
}}

blockquote {{
    background: #f5f9f5;
    border-left: 4px solid #00aa66;
    padding: 14px 18px;
    margin: 18px 0;
    color: #444;
    font-family: 'SerifSC', serif;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 10pt;
    font-family: 'SansSC', sans-serif;
}}

th {{
    background: #1a1a2e;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: bold;
}}

td {{
    padding: 8px 12px;
    border-bottom: 1px solid #ddd;
}}

tr:nth-child(even) {{
    background: #f9f9f9;
}}

strong {{
    color: #008855;
    font-weight: bold;
}}

hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 35px 0;
}}

ul, ol {{
    padding-left: 25px;
}}

li {{
    margin: 6px 0;
    line-height: 1.7;
}}

code {{
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10pt;
}}

em {{
    color: #888;
    font-size: 10pt;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

# 生成PDF
HTML(string=html_full).write_pdf(str(pdf_path))
print(f"PDF已生成: {pdf_path}")
print(f"文件大小: {pdf_path.stat().st_size / 1024:.1f} KB")
