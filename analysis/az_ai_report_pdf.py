"""
深度调研报告 Markdown → PDF (reportlab, 中文)
==============================================
把 阿斯利康中国AI研究院深度调研.md 渲染为专业 PDF。
行级解析: 标题(#/##/###)、表格(|)、引用(>)、有序/无序列表、分隔线(---)、加粗(**)。

Usage:
    conda activate research
    python analysis/az_ai_report_pdf.py
"""
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

ROOT = Path("./output/2026-06-09/astrazeneca-ai-research")
MD = ROOT / "阿斯利康中国AI研究院深度调研.md"
PDF = ROOT / "阿斯利康中国AI研究院深度调研.pdf"

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

NAVY = colors.HexColor("#10243e"); ACCENT = colors.HexColor("#7b2d8e")  # 阿斯利康紫
GRAY = colors.HexColor("#666"); LIGHT = colors.HexColor("#f0ecf4"); INK = colors.HexColor("#2d2d2d")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=22, textColor=NAVY, leading=30, spaceAfter=10, spaceBefore=6)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=14.5, textColor=colors.white, backColor=NAVY,
                    leading=24, spaceBefore=18, spaceAfter=10, leftIndent=8, borderPadding=(5, 5, 5, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12, textColor=ACCENT, leading=18, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.3, textColor=INK, leading=17.5, spaceAfter=6, alignment=0)
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10, textColor=colors.HexColor("#444"),
                       leading=17, leftIndent=14, rightIndent=8, spaceBefore=4, spaceAfter=8,
                       backColor=LIGHT, borderPadding=(8, 8, 8, 10))
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=18, bulletIndent=4, spaceAfter=4)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=8.5, textColor=GRAY, leading=13)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=11, textColor=GRAY, leading=17, spaceAfter=5)


def inline(text):
    """处理 **加粗** 和 `代码` 转 reportlab 标记。"""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r'<font name="CN-B">\1</font>', text)
    text = re.sub(r"`(.+?)`", r'<font name="CN-B">\1</font>', text)
    return text


def styled_table(rows):
    t = Table(rows, hAlign="LEFT")
    st = [("FONTNAME", (0, 0), (-1, -1), "CN"), ("FONTSIZE", (0, 0), (-1, -1), 9),
          ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "CN-B"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    t.setStyle(TableStyle(st))
    return t


def watermark(c, d):
    c.saveState(); c.setFont("CN", 52); c.setFillColor(colors.HexColor("#f2eef5"))
    c.translate(A4[0] / 2, A4[1] / 2); c.rotate(45)
    c.drawCentredString(0, 0, "深度调研 · 仅供参考"); c.restoreState()


def footer(c, d):
    watermark(c, d); c.saveState()
    c.setStrokeColor(colors.HexColor("#ddd")); c.setLineWidth(0.5)
    c.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    c.setFont("CN", 8); c.setFillColor(GRAY)
    c.drawString(2 * cm, 0.95 * cm, "阿斯利康中国 AI 研究院深度调研")
    c.drawRightString(A4[0] - 2 * cm, 0.95 * cm, f"第 {d.page} 页 · 不构成投资建议")
    c.restoreState()


def build_story(md_text):
    story = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1; continue
        # 表格
        if ln.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                block.append(lines[i]); i += 1
            rows = []
            for r, raw in enumerate(block):
                if re.match(r"^\s*\|[\s:|-]+\|\s*$", raw):
                    continue
                cells = [c.strip() for c in raw.strip().strip("|").split("|")]
                rows.append([Paragraph(inline(c), ParagraphStyle("c", parent=NOTE, fontSize=9, leading=12)) for c in cells])
            if rows:
                story.append(styled_table(rows)); story.append(Spacer(1, 0.2 * cm))
            continue
        # 标题
        if ln.startswith("### "):
            story.append(Paragraph(inline(ln[4:]), H3))
        elif ln.startswith("## "):
            story.append(Paragraph(inline(ln[3:]), H2))
        elif ln.startswith("# "):
            story.append(Paragraph(inline(ln[2:]), H1))
        elif ln.startswith("> "):
            story.append(Paragraph(inline(ln[2:]), QUOTE))
        elif re.match(r"^\s*[-*] ", ln):
            story.append(Paragraph(inline(re.sub(r"^\s*[-*] ", "", ln)), BULLET, bulletText="•"))
        elif re.match(r"^\s*\d+\. ", ln):
            story.append(Paragraph(inline(ln.strip()), BULLET))
        elif ln.strip() == "---":
            story.append(Spacer(1, 0.1 * cm))
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#ccc")))
            story.append(Spacer(1, 0.1 * cm))
        else:
            sty = SUB if ln.startswith("**") and ln.endswith("**") else BODY
            story.append(Paragraph(inline(ln), sty))
        i += 1
    return story


md_text = MD.read_text(encoding="utf-8")
doc = SimpleDocTemplate(str(PDF), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
                        title="阿斯利康中国AI研究院深度调研", author="量化研究笔记")
doc.build(build_story(md_text), onFirstPage=footer, onLaterPages=footer)
print(f"PDF 已生成 → {PDF}  ({PDF.stat().st_size // 1024} KB)")
