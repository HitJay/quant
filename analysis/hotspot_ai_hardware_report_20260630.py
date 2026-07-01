"""2026-06-30 AI 硬件链主题研报.

基于收盘版 hotspot summary/raw 数据生成 Markdown + ReportLab PDF。
口径: 复盘研报, 不构成投资建议。
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
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/2026-06-30/today-hotspot"
RAW = BASE / "raw"
CARDS = BASE / "cards_ai_hardware"
OUT = BASE / "report_ai_hardware"
OUT.mkdir(parents=True, exist_ok=True)

MD = OUT / "AI硬件链主题研报_20260630.md"
PDF = OUT / "AI硬件链主题研报_20260630.pdf"

SUMMARY = json.loads((BASE / "summary.json").read_text(encoding="utf-8"))
INDUSTRY = pd.read_parquet(RAW / "industry_board.parquet")
CONCEPT = pd.read_parquet(RAW / "concept_board.parquet")
ZT_POOL = pd.read_parquet(RAW / "zt_pool.parquet")
EM_HOT = pd.read_parquet(RAW / "em_hot_rank.parquet") if (RAW / "em_hot_rank.parquet").exists() else pd.DataFrame()
XQ_TWEET = pd.read_parquet(RAW / "xueqiu_tweet.parquet") if (RAW / "xueqiu_tweet.parquet").exists() else pd.DataFrame()

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
PURPLE = colors.HexColor("#7c3aed")
GRAY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#eef2f7")
CREAM = colors.HexColor("#fff8e7")
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
                       backColor=CREAM, borderColor=GOLD, borderWidth=0)
CELL = ParagraphStyle("CELL", fontName="CN", fontSize=8.8, textColor=INK, leading=12, alignment=1)
CELL_B = ParagraphStyle("CELL_B", fontName="CN-B", fontSize=8.8, textColor=INK, leading=12, alignment=1)


def row_by_name(df: pd.DataFrame, name: str) -> dict:
    hit = df.loc[df["name"].eq(name)]
    if hit.empty:
        raise KeyError(name)
    return hit.iloc[0].to_dict()


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


def card_image(path: Path, width_cm: float) -> Image:
    from PIL import Image as PILImage

    image = PILImage.open(path)
    width = width_cm * cm
    return Image(str(path), width=width, height=width * image.height / image.width)


def on_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.5)
    canvas.line(1.8 * cm, A4[1] - 1.35 * cm, A4[0] - 1.8 * cm, A4[1] - 1.35 * cm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.8 * cm, A4[1] - 1.17 * cm, "AI硬件链主题复盘研报")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.17 * cm, f"数据截至 {SNAPSHOT_LABEL}")
    canvas.line(1.8 * cm, 1.25 * cm, A4[0] - 1.8 * cm, 1.25 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.9 * cm, f"第 {doc.page} 页 · 复旦杰伦 · 仅供复盘")
    canvas.restoreState()


def on_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("CN", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 1.15 * cm, "本报告仅供个人复盘 · 不构成投资建议")
    canvas.restoreState()


APPLE = row_by_name(CONCEPT, "苹果概念")
LED = row_by_name(CONCEPT, "LED概念")
WEARABLE = row_by_name(CONCEPT, "智能穿戴")
OPTICAL = row_by_name(INDUSTRY, "光学光电子")
SEMI = row_by_name(INDUSTRY, "半导体")
ELECTRONICS = row_by_name(INDUSTRY, "电子")
COMM = row_by_name(INDUSTRY, "通信设备")
COMPONENT = row_by_name(INDUSTRY, "元件")
CONSUMER = row_by_name(INDUSTRY, "消费电子")

HARDWARE_ROWS = [OPTICAL, SEMI, ELECTRONICS, COMM, COMPONENT]
HARDWARE_NET = sum(float(item["main_net_in"]) for item in HARDWARE_ROWS)
HARDWARE_UP = sum(float(item["up_count"]) for item in HARDWARE_ROWS)
HARDWARE_DOWN = sum(float(item["down_count"]) for item in HARDWARE_ROWS)
HARDWARE_BREADTH = HARDWARE_UP / max(HARDWARE_UP + HARDWARE_DOWN, 1)
APPLE_BREADTH = breadth(APPLE)
ELECTRONICS_BREADTH = breadth(ELECTRONICS)
ZHABAN_RATE = SUMMARY["zb_count"] / max(SUMMARY["zt_count"] + SUMMARY["zb_count"], 1)
SEMI_NET_SHARE = float(SEMI["main_net_in"]) / max(HARDWARE_NET, 1)
SNAPSHOT_LABEL = SUMMARY.get("generated_at", "").replace("T", " ")[:16]


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
    if len(EM_HOT):
        for item in EM_HOT.head(10).to_dict("records"):
            hot_rows.append([item.get("当前排名", ""), item.get("股票名称", ""), item.get("代码", ""), pct_points(item.get("涨跌幅", 0))])

    md = f"""# AI硬件链主题研报：苹果概念只是入口

报告日期：2026-06-30  
数据截至：{SNAPSHOT_LABEL}  
作者：复旦杰伦  
口径：收盘热点复盘，不构成投资建议

## 一句话结论

今天表面最强标签是“苹果概念”，但收盘数据更像一轮 **AI硬件链扩散行情**：苹果概念净流入 {money(APPLE['main_net_in'])}、上涨占比 {pct0(APPLE_BREADTH)}；光学光电子、半导体、电子、通信设备、元件同步走强，代表性电子链板块合计净流入 {money(HARDWARE_NET)}。不过最高连板只有 {SUMMARY['zt_max_board']} 板、炸板率 {pct0(ZHABAN_RATE)}，说明行情强在宽度，不是无脑连板高度。

## 核心量化事实

- 苹果概念：{pct_points(APPLE['pct_chg'])}，上涨 {APPLE['up_count']} / 下跌 {APPLE['down_count']}，主力净流入 {money(APPLE['main_net_in'])}。
- 代表性电子链：合计净流入 {money(HARDWARE_NET)}，板块上涨占比 {pct0(HARDWARE_BREADTH)}。
- 半导体：{pct_points(SEMI['pct_chg'])}，净流入 {money(SEMI['main_net_in'])}，资金占电子链代表板块 {pct0(SEMI_NET_SHARE)}。
- 情绪：涨停 {SUMMARY['zt_count']} 只，炸板 {SUMMARY['zb_count']} 只，最高 {SUMMARY['zt_max_board']} 板，炸板率 {pct0(ZHABAN_RATE)}。
- 弱势对照：医药商业、煤炭、中药、银行、保险仍在跌幅榜，资金风格明显偏科技硬件。

## 行业强度

{md_table(['行业', '涨幅', '上涨/下跌', '主力净流入', '领涨'], top_industry_rows)}

## 概念强度

{md_table(['概念', '涨幅', '上涨/下跌', '主力净流入', '领涨'], top_concept_rows)}

## 涨停结构

{md_table(['行业', '涨停数'], zt_rows)}

## 人气验证

{md_table(['排名', '股票', '代码', '涨跌幅'], hot_rows)}

## 研判与建议

1. 复盘主线可以写“苹果只是入口，AI硬件链才是核心”。
2. 明天只追踪承接，不追故事：光学、通信、元件、半导体是否继续净流入。
3. 半导体午后补强，但资金占比仍不是绝对主导，不能把行情简化成单一半导体线。
4. 不急着追高：{SUMMARY['zt_count']} 只涨停已经很热，但最高只有 {SUMMARY['zt_max_board']} 板，说明投机高度还没打开。
5. 如果明天电子链净流入收缩、弱势方向反抽，则今天更可能是一次科技硬件高潮日；如果光学/通信/元件继续强，则主线延续概率更高。

## 风险提示

本报告是热点复盘与内容选题研究，不构成投资建议。板块资金流为东方财富板块口径，代表性电子链净流入为板块标签简单合计，未做成分股去重，只用于衡量资金叙事强度。
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
        title="AI硬件链主题研报",
        author="复旦杰伦",
    )
    story: list = []

    story.append(Spacer(1, 2.1 * cm))
    story.append(Paragraph("AI硬件链主题研报", H1))
    story.append(Paragraph("苹果概念只是入口 · 光学/半导体/通信/元件共同扩散", SUB))
    story.append(Paragraph(f"2026-06-30 收盘复盘 · 数据截至 {SNAPSHOT_LABEL}", SUB))
    story.append(Spacer(1, 0.75 * cm))
    story.append(HRFlowable(width="58%", thickness=1.2, color=NAVY, hAlign="CENTER"))
    story.append(Spacer(1, 0.75 * cm))

    hero = [
        ["苹果概念", "电子链资金", "情绪温度"],
        [money(APPLE["main_net_in"], 0), money(HARDWARE_NET), f'{SUMMARY["zt_count"]}/{SUMMARY["zb_count"]}'],
        [f"净流入 · 涨幅 {pct_points(APPLE['pct_chg'])}", "代表板块合计 · 非去重", "涨停 / 炸板"],
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
        f"收盘数据确认: 苹果概念 {pct_points(APPLE['pct_chg'])}, 主力净流入 {money(APPLE['main_net_in'])}; "
        f"光学光电子 {pct_points(OPTICAL['pct_chg'])}、半导体 {pct_points(SEMI['pct_chg'])}、电子 {pct_points(ELECTRONICS['pct_chg'])}、"
        f"通信设备 {pct_points(COMM['pct_chg'])} 同步走强。主线强在宽度和资金集中, 但最高连板仍只有 {SUMMARY['zt_max_board']} 板。",
        BODY,
    ))
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph("作者: 复旦杰伦 · 输出: 主题复盘研报 · 本报告不构成投资建议", CAP))
    story.append(PageBreak())

    story.append(Paragraph("一、摘要结论", H2))
    bullets = [
        f"<b>主线定义:</b> 表面标签是苹果概念, 但底层是 AI 硬件链扩散。苹果概念上涨占比 {pct0(APPLE_BREADTH)}, 主力净流入 {money(APPLE['main_net_in'])}。",
        f"<b>资金强度:</b> 光学光电子、半导体、电子、通信设备、元件五个代表板块合计净流入 {money(HARDWARE_NET)}; 该口径未做成分股去重, 用于衡量资金叙事强度。",
        f"<b>半导体变化:</b> 半导体收盘涨幅 {pct_points(SEMI['pct_chg'])}, 净流入 {money(SEMI['main_net_in'])}, 已明显补强; 但资金体量仍低于电子总项、通信设备和光学光电子。",
        f"<b>情绪结构:</b> 全市场涨停 {SUMMARY['zt_count']} 只、炸板 {SUMMARY['zb_count']} 只、炸板率 {pct0(ZHABAN_RATE)}; 最高连板 {SUMMARY['zt_max_board']} 板, 说明强在宽度而非高度。",
        "<b>策略含义:</b> 适合写成产业链扩散复盘, 不适合写成单票或单一半导体喊单。明天重点看光学/通信/元件/半导体能否继续承接。",
    ]
    for item in bullets:
        story.append(Paragraph(f"• {item}", BULLET))
    story.append(Paragraph(
        "<b>付费版一句话:</b> 今天不是简单的“苹果概念日”, 而是资金借苹果标签为入口, 重新定价端侧 AI、光学显示、通信硬件、电子元件和半导体的硬件链弹性。",
        QUOTE,
    ))

    story.append(Paragraph("二、板块强度: 哪些行业一起涨", H2))
    industry_rows = [["排名", "行业", "涨幅", "上涨/下跌", "主力净流入", "领涨"]]
    for i, item in enumerate(SUMMARY["industry_top5"], 1):
        industry_rows.append([
            str(i), item["name"], pct_points(item["pct_chg"]),
            f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", ""),
        ])
    story.append(tbl(industry_rows, [1.1 * cm, 3.0 * cm, 2.0 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm], highlight_rows={1, 2, 3, 4}))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        f"行业榜说明: 光学光电子和半导体收盘涨幅均超过 6%, 电子大类净流入 {money(ELECTRONICS['main_net_in'])}, "
        f"通信设备净流入 {money(COMM['main_net_in'])}。这组数据比单看苹果概念更能解释今日行情。",
        BODY,
    ))

    story.append(Paragraph("三、概念扩散: 苹果只是入口", H2))
    concept_rows = [["排名", "概念", "涨幅", "上涨/下跌", "主力净流入", "领涨"]]
    for i, item in enumerate(SUMMARY["concept_top5"], 1):
        concept_rows.append([
            str(i), item["name"], pct_points(item["pct_chg"]),
            f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", ""),
        ])
    story.append(tbl(concept_rows, [1.1 * cm, 3.0 * cm, 2.0 * cm, 2.2 * cm, 2.8 * cm, 2.8 * cm], highlight_rows={1, 2, 3}))
    story.append(Paragraph(
        f"苹果概念、LED概念、智能穿戴同时进入概念涨幅榜前三。水晶光电在苹果概念和智能穿戴中反复出现, "
        "说明资金并不只买一个“苹果”标签, 而是在找光学显示、终端硬件和端侧 AI 的交叉点。",
        BODY,
    ))

    story.append(PageBreak())
    story.append(Paragraph("四、资金质量: 半导体补强, 但不是唯一主线", H2))
    matrix = [["板块", "涨幅", "上涨占比", "主力净流入", "净流入占比", "解读"]]
    explain = {
        "光学光电子": "主线前排",
        "半导体": "午后补强",
        "电子": "大类载体",
        "通信设备": "资金最顺",
        "元件": "零部件承接",
    }
    for item in HARDWARE_ROWS:
        matrix.append([
            item["name"], pct_points(item["pct_chg"]), pct0(breadth(item)),
            money(item["main_net_in"]), f'{float(item["main_net_in_pct"]):.2f}%', explain.get(item["name"], ""),
        ])
    story.append(tbl(matrix, [2.5 * cm, 1.8 * cm, 2.0 * cm, 2.6 * cm, 2.0 * cm, 2.5 * cm], highlight_rows={1, 2, 3, 4}))
    story.append(Paragraph(
        f"半导体资金占代表性电子链净流入 {pct0(SEMI_NET_SHARE)}。这比午间更健康, 但仍不能把今日行情简化为“半导体单线”。"
        "更稳的表述是: 半导体、光学、通信和元件共同构成 AI 硬件链。",
        BODY,
    ))

    story.append(Paragraph("五、涨停和情绪: 宽度强, 高度一般", H2))
    zt_rows = [["行业", "涨停数", "读法"]]
    hardware_zts = 0
    for item in SUMMARY["zt_top_industries"]:
        note = "硬件链前排" if item["行业"] in {"半导体", "光学光电", "通信设备", "元件", "消费电子"} else "扩散/对照"
        if note == "硬件链前排":
            hardware_zts += int(item["涨停数"])
        zt_rows.append([item["行业"], str(item["涨停数"]), note])
    story.append(tbl(zt_rows, [4.0 * cm, 3.0 * cm, 5.2 * cm], highlight_rows={1, 2}))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        f"今日涨停 {SUMMARY['zt_count']} 只, 但最高只有 {SUMMARY['zt_max_board']} 板。半导体和光学光电分别贡献 {SUMMARY['zt_top_industries'][0]['涨停数']}、{SUMMARY['zt_top_industries'][1]['涨停数']} 只涨停, "
        f"说明硬件链在涨停池中有真实宽度; 但 {pct0(ZHABAN_RATE)} 的炸板率也提醒, 追涨容错并不高。",
        BODY,
    ))

    story.append(PageBreak())
    story.append(Paragraph("六、人气验证: 散户雷达也在硬件链", H2))
    hot_rows = [["排名", "股票", "代码", "涨跌幅", "解读"]]
    hardware_hot = {"京东方Ａ", "深科技", "多氟多", "长电科技", "TCL科技", "彩虹股份", "风华高科", "胜宏科技", "寒武纪", "新易盛", "中际旭创"}
    if len(EM_HOT):
        for item in EM_HOT.head(10).to_dict("records"):
            name = item.get("股票名称", "")
            hot_rows.append([
                item.get("当前排名", ""), name, item.get("代码", ""), pct_points(item.get("涨跌幅", 0)),
                "硬件链" if name in hardware_hot else "情绪锚",
            ])
    story.append(tbl(hot_rows, [1.2 * cm, 2.5 * cm, 2.6 * cm, 2.0 * cm, 2.5 * cm], font_size=8.5,
                     highlight_rows={1, 2, 3, 4, 6, 8, 10}))
    story.append(Paragraph(
        "东财人气榜中, 京东方A、深科技、多氟多、长电科技、TCL科技、彩虹股份、风华高科等均与显示面板、半导体封测、电子材料、元件相关。"
        "这和板块资金流方向一致。",
        BODY,
    ))

    story.append(Paragraph("七、明日跟踪框架", H2))
    checks = [["信号", "观察对象", "如果继续强", "如果转弱"]]
    checks.extend([
        ["主线承接", "光学/通信/元件", "确认硬件链延续", "今日可能是高潮日"],
        ["半导体质量", "半导体净流入", "从补涨变主线", "只剩标签普涨"],
        ["情绪高度", "最高连板", "4-5板打开高度", "宽度强但投机弱"],
        ["弱势反抽", "医药/银行/消费", "风格回摆", "科技吸金继续"],
        ["人气锚", "京东方/TCL/水晶光电", "大众关注确认", "散户热度退潮"],
    ])
    story.append(tbl(checks, [2.2 * cm, 3.0 * cm, 4.0 * cm, 4.0 * cm], font_size=8.4))
    story.append(Paragraph(
        "内容建议: 明天的二更或追踪帖不需要重新找大叙事, 只要用同一张框架更新“承接/退潮”即可。若光学、通信、元件继续净流入, 可以写“AI硬件链第二天仍有承接”; 若只剩半导体冲高, 则写“主线变窄”。",
        QUOTE,
    ))

    story.append(PageBreak())
    story.append(Paragraph("八、卡片预览与口径说明", H2))
    contact = CARDS / "contact_sheet.jpg"
    if contact.exists():
        story.append(card_image(contact, 16.0))
        story.append(Paragraph("图: 本主题配套小红书 7 页卡片预览", CAP))
    story.append(Paragraph("数据口径", H3))
    notes = [
        "行情、板块、资金流主要来自东方财富接口; 雪球/东财人气榜用于关注度验证。",
        "代表性电子链净流入为光学光电子、半导体、电子、通信设备、元件五个板块标签简单合计, 未做成分股去重。",
        "龙虎榜接口本轮未返回有效数据, 因此本报告不使用龙虎榜席位作为证据。",
        "本报告只做热点复盘和内容选题, 不构成投资建议。",
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