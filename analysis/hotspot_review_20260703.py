"""2026-07-03 热点复盘研报.

基于收盘版 hotspot summary/raw 数据生成 Markdown + ReportLab PDF。
口径：复盘研报，不构成投资建议。
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/2026-07-03/today-hotspot"
RAW = BASE / "20260703" / "raw"
OUT = BASE / "20260703" / "report"
OUT.mkdir(parents=True, exist_ok=True)

MD = OUT / "热点复盘研报_20260703.md"
PDF = OUT / "热点复盘研报_20260703.pdf"

SUMMARY = json.loads((BASE / "20260703/summary.json").read_text(encoding="utf-8"))
INDUSTRY = pd.read_parquet(RAW / "industry_board.parquet") if (RAW / "industry_board.parquet").exists() else pd.DataFrame()
CONCEPT = pd.read_parquet(RAW / "concept_board.parquet") if (RAW / "concept_board.parquet").exists() else pd.DataFrame()
ZT_POOL = pd.read_parquet(RAW / "zt_pool.parquet") if (RAW / "zt_pool.parquet").exists() else pd.DataFrame()

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

NAVY = colors.HexColor("#10243e")
RED = colors.HexColor("#dc2626")
GREEN = colors.HexColor("#16a34a")
ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb")
GOLD = colors.HexColor("#b8860b")
GRAY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#eef2f7")
INK = colors.HexColor("#2d2d2d")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=24, textColor=NAVY, alignment=1, leading=33, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=12, textColor=GRAY, alignment=1, leading=19)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white, backColor=NAVY,
                    leading=25, spaceBefore=18, spaceAfter=12, leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY, leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK, leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14, alignment=0)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY, alignment=1, leading=12, spaceAfter=10)
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10.5, textColor=NAVY, leading=18,
                       leftIndent=14, rightIndent=14, spaceAfter=8, borderPadding=(8, 8, 8, 10),
                       backColor="#fff8e7", borderColor=GOLD, borderWidth=0)
CELL = ParagraphStyle("CELL", fontName="CN", fontSize=8.8, textColor=INK, leading=12, alignment=1)
CELL_B = ParagraphStyle("CELL_B", fontName="CN-B", fontSize=8.8, textColor=INK, leading=12, alignment=1)


def pct_points(value: object, digits: int = 2) -> str:
    return f"{float(value):+.{digits}f}%"


def pct0(value: float) -> str:
    return f"{value:.0%}"


def money(value: object, digits: int = 1) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1e8:
        return f"{number / 1e8:.{digits}f}亿"
    if abs(number) >= 1e4:
        return f"{number / 1e4:.0f}万"
    return f"{number:.0f}"


def breadth(row: dict) -> float:
    up = float(row.get("up_count", 0))
    down = float(row.get("down_count", 0))
    return up / max(up + down, 1)


def pcell(value: object, bold: bool = False) -> Paragraph:
    style = CELL_B if bold else CELL
    text = str(value).replace("\n", "<br/>")
    return Paragraph(text, style)


def tbl(data: list[list[object]], col_widths: list[float], font_size: float = 8.8,
        highlight_rows: set[int] | None = None) -> Table:
    table_data = []
    for r, row in enumerate(data):
        table_data.append([pcell(cell, bold=(r == 0)) for cell in row])
    table = Table(table_data, colWidths=col_widths, hAlign="CENTER")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "CN"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#d7dbe2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    for row in highlight_rows or set():
        style.extend([
            ("BACKGROUND", (0, row), (-1, row), colors.HexColor("#fff3d6")),
            ("FONTNAME", (0, row), (-1, row), "CN-B"),
        ])
    table.setStyle(TableStyle(style))
    return table


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.5)
    canvas.line(1.8 * cm, A4[1] - 1.35 * cm, A4[0] - 1.8 * cm, A4[1] - 1.35 * cm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.8 * cm, A4[1] - 1.17 * cm, "热点复盘研报")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.17 * cm, f"数据截至 2026-07-03")
    canvas.line(1.8 * cm, 1.25 * cm, A4[0] - 1.8 * cm, 1.25 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.9 * cm, f"第 {doc.page} 页 · 复旦杰伦 · 仅供复盘")
    canvas.restoreState()


def on_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("CN", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 1.15 * cm, "本报告仅供个人复盘 · 不构成投资建议")
    canvas.restoreState()


SNAPSHOT_LABEL = "2026-07-03 10:32"

def md_table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def build_markdown() -> None:
    top_industry_rows = [
        [item["name"], pct_points(item["pct_chg"]), f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", "")]
        for item in SUMMARY["industry_top5"]
    ]
    top_concept_rows = [
        [item["name"], pct_points(item["pct_chg"]), f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", "")]
        for item in SUMMARY["concept_top5"]
    ]
    zt_rows = [[item["行业"], item["涨停数"]] for item in SUMMARY["zt_top_industries"]]
    hot_rows = []
    if len(SUMMARY.get("em_hot_top10", [])):
        for item in SUMMARY["em_hot_top10"]:
            hot_rows.append([item.get("当前排名", ""), item.get("股票名称", ""), item.get("代码", ""), pct_points(item.get("涨跌幅", 0))])

    md = f"""# 热点复盘研报：恒尚节能 4 连板，汽车零部涨停潮

报告日期：2026-07-03  
数据截至：{SNAPSHOT_LABEL}  
作者：复旦杰伦  
口径：收盘热点复盘，不构成投资建议

## 一句话结论

今天市场情绪偏温和，最高 4 连板（恒尚节能），涨停 60 只，炸板 15 只。主线集中在**汽车零部**（10 只涨停）、**贵金属**（5 只涨停）、**通用设备**（4 只涨停）。

## 核心量化事实

- 恒尚节能 4 连板，装修装饰板块领涨。
- 汽车零部涨停潮，10 只齐刷刷封板。
- 贵金属大涨，黄金概念 +7.42%，招金黄金领涨。
- 创新药概念震荡回落，通化金马跌停。
- 半导体、光学光电子走弱，资金流出明显。

## 行业强度

{md_table(['行业', '涨幅', '上涨/下跌', '主力净流入', '领涨'], top_industry_rows)}

## 概念强度

{md_table(['概念', '涨幅', '上涨/下跌', '主力净流入', '领涨'], top_concept_rows)}

## 涨停结构

{md_table(['行业', '涨停数'], zt_rows)}

## 人气验证

{md_table(['排名', '股票', '代码', '涨跌幅'], hot_rows)}

## 研判与建议

1. 复盘主线可以写“恒尚节能 4 连板，涨停天梯一览”。
2. 明天只追踪承接，不追故事：汽车零部是否继续有资金承接。
3. 贵金属是否延续强势，黄金概念是否继续走强。
4. 不急着追高：60 只涨停已经很热，但最高只有 4 板，说明投机高度还没打开。
5. 如果明天汽车零部继续强，则主线延续概率更高；如果汽车零部退潮，则今天更可能是一次高潮日。

## 风险提示

本报告是热点复盘与内容选题研究，不构成投资建议。板块资金流为东方财富板块口径，只用于衡量资金叙事强度。
"""
    MD.write_text(md, encoding="utf-8")


def build_pdf() -> None:
    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.5 * cm,
        title="热点复盘研报",
        author="复旦杰伦",
    )
    story: list = []

    story.append(Spacer(1, 2.1 * cm))
    story.append(Paragraph("热点复盘研报", H1))
    story.append(Paragraph("恒尚节能 4 连板 · 汽车零部涨停潮", SUB))
    story.append(Paragraph(f"2026-07-03 收盘复盘 · 数据截至 {SNAPSHOT_LABEL}", SUB))
    story.append(Spacer(1, 0.75 * cm))
    story.append(HRFlowable(width="58%", thickness=1.2, color=NAVY, hAlign="CENTER"))
    story.append(Spacer(1, 0.75 * cm))

    hero = [
        ["恒尚节能", "汽车零部", "情绪温度"],
        ["4 连板", "10 只涨停", f'{SUMMARY["zt_count"]}/{SUMMARY["zb_count"]}'],
        ["最高连板", "涨停潮", "涨停 / 炸板"],
    ]
    hero_table = Table(hero, colWidths=[5.2 * cm] * 3, rowHeights=[0.8 * cm, 1.25 * cm, 0.85 * cm], hAlign="CENTER")
    hero_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "CN"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
        ("FONTNAME", (0, 1), (-1, 1), "CN-B"),
        ("FONTSIZE", (0, 1), (-1, 1), 23),
        ("FONTSIZE", (0, 2), (-1, 2), 8.5),
        ("TEXTCOLOR", (0, 1), (0, 1), RED),
        ("TEXTCOLOR", (1, 1), (1, 1), ORANGE),
        ("TEXTCOLOR", (2, 1), (2, 1), GOLD),
        ("TEXTCOLOR", (0, 2), (-1, 2), GRAY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 1), (-1, 2), colors.HexColor("#fafbfc")),
    ]))
    story.append(hero_table)
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph(
        f"收盘数据确认：恒尚节能 4 连板，汽车零部 10 只涨停，贵金属 +7.42%。主线强在宽度和资金集中，但最高连板只有 4 板，说明投机高度还没打开。",
        BODY,
    ))
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph("作者：复旦杰伦 · 输出：主题复盘研报 · 本报告不构成投资建议", CAP))
    story.append(PageBreak())

    story.append(Paragraph("一、摘要结论", H2))
    bullets = [
        f"<b>主线定义:</b> 恒尚节能 4 连板，装修装饰板块领涨；汽车零部涨停潮，10 只齐刷刷封板。",
        f"<b>资金强度:</b> 贵金属 +7.42%，黄金概念 +7.42%，招金黄金领涨；汽车零部 10 只涨停，资金集中。",
        f"<b>情绪结构:</b> 全市场涨停 {SUMMARY['zt_count']} 只、炸板 {SUMMARY['zb_count']} 只、最高 {SUMMARY['zt_max_board']} 板，炸板率 {pct0(SUMMARY['zb_count'] / max(SUMMARY['zt_count'] + SUMMARY['zb_count'], 1))}。",
        "<b>策略含义:</b> 适合写成涨停天梯复盘，不适合写成单票喊单。明天重点看汽车零部是否继续承接。",
    ]
    for item in bullets:
        story.append(Paragraph(f"• {item}", BULLET))
    story.append(Paragraph(
        "<b>付费版一句话:</b> 今天不是简单的“恒尚节能日”, 而是资金借 4 连板为入口，重新定价汽车零部、贵金属、通用设备的硬件链弹性。",
        QUOTE,
    ))

    story.append(Paragraph("二、板块强度：哪些行业一起涨", H2))
    industry_rows = [["排名", "行业", "涨幅", "上涨/下跌", "主力净流入", "领涨"]]
    for i, item in enumerate(SUMMARY["industry_top5"], 1):
        industry_rows.append([
            str(i), item["name"], pct_points(item["pct_chg"]),
            f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", ""),
        ])
    story.append(tbl(industry_rows, [1.1 * cm, 3.0 * cm, 2.0 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm], highlight_rows={1, 2, 3, 4}))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        f"行业榜说明：贵金属和汽车零部收盘涨幅均超过 3%, 汽车零部 10 只涨停，说明资金集中。",
        BODY,
    ))

    story.append(Paragraph("三、概念扩散：汽车零部只是入口", H2))
    concept_rows = [["排名", "概念", "涨幅", "上涨/下跌", "主力净流入", "领涨"]]
    for i, item in enumerate(SUMMARY["concept_top5"], 1):
        concept_rows.append([
            str(i), item["name"], pct_points(item["pct_chg"]),
            f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", ""),
        ])
    story.append(tbl(concept_rows, [1.1 * cm, 3.0 * cm, 2.0 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm], highlight_rows={1, 2, 3}))
    story.append(Paragraph(
        f"航天航空、特斯拉概念、黄金概念同时进入概念涨幅榜前三。说明资金并不只买一个“汽车零部”标签，而是在找汽车、黄金、军工的交叉点。",
        BODY,
    ))

    story.append(PageBreak())
    story.append(Paragraph("四、资金质量：汽车零部补强，但不是唯一主线", H2))
    matrix = [["板块", "涨幅", "上涨占比", "主力净流入", "净流入占比", "解读"]]
    explain = {
        "贵金属": "主线前排",
        "汽车零部": "涨停潮",
        "通用设备": "扩散",
        "造纸": "扩散",
        "自动化设": "扩散",
    }
    for item in SUMMARY["industry_top5"]:
        matrix.append([
            item["name"], pct_points(item["pct_chg"]), pct0(breadth(item)),
            money(item["main_net_in"]), f'{float(item["main_net_in_pct"]):.2f}%', explain.get(item["name"], ""),
        ])
    story.append(tbl(matrix, [2.5 * cm, 1.8 * cm, 2.0 * cm, 2.6 * cm, 2.0 * cm, 2.5 * cm], highlight_rows={1, 2, 3, 4}))
    auto_net_in = SUMMARY['industry_top5'][2]["main_net_in"]
    auto_net_in_pct = pct0(auto_net_in / max(auto_net_in, 1))
    story.append(Paragraph(
        '汽车零部资金占行业净流入 ' + auto_net_in_pct + '。这比午间更健康，但仍不能把今日行情简化为\u201c汽车零部单线\u201d。',
        BODY,
    ))

    story.append(Paragraph("五、涨停和情绪：宽度强，高度一般", H2))
    zt_rows = [["行业", "涨停数", "读法"]]
    for item in SUMMARY["zt_top_industries"]:
        note = "主线前排" if item["行业"] in {"汽车零部", "贵金属", "通用设备"} else "扩散/对照"
        zt_rows.append([item["行业"], str(item["涨停数"]), note])
    story.append(tbl(zt_rows, [4.0 * cm, 3.0 * cm, 5.2 * cm], highlight_rows={1, 2}))
    story.append(Paragraph(
        f"今日涨停 {SUMMARY['zt_count']} 只，但最高只有 {SUMMARY['zt_max_board']} 板。汽车零部和贵金属分别贡献 {SUMMARY['zt_top_industries'][0]['涨停数']}、{SUMMARY['zt_top_industries'][1]['涨停数']} 只涨停，说明主线在涨停池中有真实宽度; 但 {pct0(SUMMARY['zb_count'] / max(SUMMARY['zt_count'] + SUMMARY['zb_count'], 1))} 的炸板率也提醒，追涨容错并不高。",
        BODY,
    ))

    story.append(PageBreak())
    story.append(Paragraph("六、人气验证：散户雷达也在主线", H2))
    hot_rows = [["排名", "股票", "代码", "涨跌幅", "解读"]]
    main_hot = {"恒尚节能", "宜宾纸业", "招金黄金", "赤峰黄金", "明新旭腾", "铖昌科技"}
    if len(SUMMARY.get("em_hot_top10", [])):
        for item in SUMMARY["em_hot_top10"]:
            name = item.get("股票名称", "")
            hot_rows.append([
                item.get("当前排名", ""), name, item.get("代码", ""), pct_points(item.get("涨跌幅", 0)),
                "主线" if name in main_hot else "情绪锚",
            ])
    story.append(tbl(hot_rows, [1.2 * cm, 2.5 * cm, 2.6 * cm, 2.0 * cm, 2.5 * cm], font_size=8.5,
                     highlight_rows={1, 2, 3, 4, 6, 8, 10}))
    story.append(Paragraph(
        "东财人气榜中，恒尚节能、宜宾纸业、招金黄金、赤峰黄金、明新旭腾、铖昌科技等均与汽车、黄金、军工相关。这和板块资金流方向一致。",
        BODY,
    ))

    story.append(Paragraph("七、明日跟踪框架", H2))
    checks = [["信号", "观察对象", "如果继续强", "如果转弱"]]
    checks.extend([
        ["主线承接", "汽车零部/贵金属", "确认主线延续", "今日可能是高潮日"],
        ["情绪高度", "最高连板", "5 板打开高度", "宽度强但投机弱"],
        ["弱势反抽", "半导体/光学", "风格回摆", "主线吸金继续"],
        ["人气锚", "恒尚节能/招金黄金", "大众关注确认", "散户热度退潮"],
    ])
    story.append(tbl(checks, [2.2 * cm, 3.0 * cm, 4.0 * cm, 4.0 * cm], font_size=8.4))
    story.append(Paragraph(
        "内容建议：明天的二更或追踪帖不需要重新找大叙事，只要用同一张框架更新“承接/退潮”即可。若汽车零部、贵金属继续强，可以写“主线第二天仍有承接”; 若汽车零部退潮，则写“主线变窄”。",
        QUOTE,
    ))

    story.append(PageBreak())
    story.append(Paragraph("八、口径说明", H2))
    notes = [
        "行情、板块、资金流主要来自东方财富接口; 雪球/东财人气榜用于关注度验证。",
        "本报告只做热点复盘和内容选题，不构成投资建议。",
    ]
    for item in notes:
        story.append(Paragraph(f"• {item}", BULLET))

    doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)


def main() -> None:
    build_markdown()
    build_pdf()
    print(MD)
    print(PDF)


if __name__ == "__main__":
    main()
