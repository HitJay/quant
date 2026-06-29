"""2026-06-29 医药主线量化付费研报 PDF."""

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
OUT = ROOT / "output/2026-06-29/today-hotspots"
PDF = OUT / "医药主线量化付费研报_20260629.pdf"
CARDS = OUT / "cards"

SUMMARY = json.loads((ROOT / "output/hotspot/20260629/summary.json").read_text(encoding="utf-8"))
PERSIST = json.loads((OUT / "pharma_persistence_summary.json").read_text(encoding="utf-8"))
EVENTS = pd.read_csv(OUT / "pharma_persistence_event_study.csv")

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
CREAM = colors.HexColor("#fff8e7")
INK = colors.HexColor("#2d2d2d")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=25, textColor=NAVY, alignment=1, leading=34, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=12.5, textColor=GRAY, alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white, backColor=NAVY,
                    leading=26, spaceBefore=18, spaceAfter=12, leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY, leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK, leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY, alignment=1, leading=12, spaceAfter=10)
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10.5, textColor=NAVY, leading=18,
                       leftIndent=14, rightIndent=14, spaceAfter=8, borderPadding=(8, 8, 8, 10),
                       backColor=CREAM, borderColor=GOLD, borderWidth=0)


def pct(value: float, digits: int = 1, signed: bool = True) -> str:
    sign = "+" if signed else ""
    return f"{value * 100:{sign}.{digits}f}%"


def pct_from_points(value: float, digits: int = 2) -> str:
    return f"{value:+.{digits}f}%"


def money(value: float) -> str:
    if abs(value) >= 1e8:
        return f"{value / 1e8:.1f}亿"
    if abs(value) >= 1e4:
        return f"{value / 1e4:.0f}万"
    return f"{value:.0f}"


def persistence(code: str, horizon: int, threshold: float = 0.04) -> dict:
    for row in PERSIST["rows"]:
        if row["code"] == code and row["threshold"] == threshold and row["horizon"] == horizon:
            return row
    raise KeyError((code, horizon, threshold))


def tbl(data, col_widths, font_size: float = 9.5, highlight_rows: set[int] | None = None) -> Table:
    table = Table(data, colWidths=col_widths, hAlign="CENTER")
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
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    for row in highlight_rows or set():
        style.extend([
            ("BACKGROUND", (0, row), (-1, row), colors.HexColor("#fff3d6")),
            ("FONTNAME", (0, row), (-1, row), "CN-B"),
        ])
    table.setStyle(TableStyle(style))
    return table


def card_image(name: str, width_cm: float = 7.2) -> Image:
    from PIL import Image as PILImage

    path = CARDS / name
    image = PILImage.open(path)
    width = width_cm * cm
    return Image(str(path), width=width, height=width * image.height / image.width)


def watermark(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("CN", 58)
    canvas.setFillColor(colors.HexColor("#eef0f3"))
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "付费研报 PAID")
    canvas.restoreState()


def on_first(canvas, doc) -> None:
    watermark(canvas, doc)
    canvas.saveState()
    canvas.setFont("CN", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, "本报告为付费内容 · 仅供个人复盘 · 不构成投资建议")
    canvas.restoreState()


def on_later(canvas, doc) -> None:
    watermark(canvas, doc)
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, A4[1] - 1.25 * cm, "医药主线量化付费研报")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, f"数据截至 {SNAPSHOT_LABEL}")
    canvas.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.95 * cm, f"第 {doc.page} 页 · 复旦杰伦 · 付费内容")
    canvas.restoreState()


SNAPSHOT_LABEL = SUMMARY.get("generated_at", "").replace("T", " ")[:16]
PHARMA = next((item for item in SUMMARY["industry_top5"] if item["name"] == "医药生物"), SUMMARY["industry_top5"][0])
COMPONENT = next((item for item in SUMMARY["industry_bottom5"] if item["name"] == "元件"), SUMMARY["industry_bottom5"][0])
PHARMA_UP = sum(item["up_count"] for item in SUMMARY["industry_top5"] if item["name"] in {"生物制品", "医疗服务", "化学制药", "医药生物", "中药Ⅱ"})
PHARMA_DOWN = sum(item["down_count"] for item in SUMMARY["industry_top5"] if item["name"] in {"生物制品", "医疗服务", "化学制药", "医药生物", "中药Ⅱ"})
PHARMA_BREADTH = PHARMA_UP / max(PHARMA_UP + PHARMA_DOWN, 1)
PHARMA_ZT = next((item["涨停数"] for item in SUMMARY["zt_top_industries"] if item["行业"] == "化学制药"), 0)
ZHABAN_RATE = SUMMARY["zb_count"] / max(SUMMARY["zt_count"] + SUMMARY["zb_count"], 1)
REL_STRENGTH = PHARMA["pct_chg"] - COMPONENT["pct_chg"]

med5 = persistence("159929", 5)
med10 = persistence("159929", 10)
med20 = persistence("159929", 20)
inno10 = persistence("159992", 10)
latest_med = PERSIST["latest"]["159929"]
latest_inno = PERSIST["latest"]["159992"]


story = []

story.append(Spacer(1, 2.2 * cm))
story.append(Paragraph("医药主线还能持续吗？", H1))
story.append(Paragraph("2026-06-29 医药行情 · 热点拆解 × 当日强度 × 历史持久度回测", SUB))
story.append(Spacer(1, 0.8 * cm))
story.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
story.append(Spacer(1, 0.8 * cm))

hero = [
    ["医药生物", "涨停/炸板", "历史持久度"],
    [pct_from_points(PHARMA["pct_chg"]), f'{SUMMARY["zt_count"]}/{SUMMARY["zb_count"]}', f'{med10["win_rate"]:.0%}'],
    ["15:09快照涨幅", "涨停 / 炸板", "大涨后10日胜率"],
]
hero_table = Table(hero, colWidths=[5.2 * cm] * 3, rowHeights=[0.8 * cm, 1.2 * cm, 0.85 * cm], hAlign="CENTER")
hero_table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"),
    ("FONTSIZE", (0, 1), (-1, 1), 24),
    ("FONTSIZE", (0, 2), (-1, 2), 9),
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
story.append(Spacer(1, 0.8 * cm))
story.append(Paragraph(
    f"本报告基于 {SNAPSHOT_LABEL} A股热点数据、医药相关ETF历史日线和事件研究。"
    f"今天医药主线不是单只龙头脉冲: 生物制品、医疗服务、化学制药、医药生物、中药II 同时进入行业涨幅前列；"
    f"但历史上医药ETF单日大涨后的5日延续并不强, 10-20日才略有胜率优势。",
    BODY,
))
story.append(Spacer(1, 0.8 * cm))
story.append(Paragraph(f"作者: 复旦杰伦 · 数据截至: {SNAPSHOT_LABEL} · 输出: 付费专用", CAP))
story.append(PageBreak())

story.append(Paragraph("一、摘要结论", H2))
summary_bullets = [
    f"<b>当日强度:</b> 医药生物涨幅 {pct_from_points(PHARMA['pct_chg'])}, 生物制品 +7.29%、医疗服务 +6.10%、化学制药 +5.87%, 行业扩散明显。",
    f"<b>广度:</b> 五个医药细分合计上涨 {PHARMA_UP} 家、下跌 {PHARMA_DOWN} 家, 上涨广度 {PHARMA_BREADTH:.0%}; 化学制药 {PHARMA_ZT} 只涨停, 是涨停最集中的医药子线。",
    f"<b>对照:</b> 封面使用元件板块作为硬件链对照, 元件 {pct_from_points(COMPONENT['pct_chg'])}, 主力净流出 {money(COMPONENT['main_net_in'])}; 医药生物与元件强弱差 {REL_STRENGTH:.1f} 个百分点。",
    f"<b>短线风险:</b> 全市场涨停 {SUMMARY['zt_count']} 只, 炸板 {SUMMARY['zb_count']} 只, 炸板率 {ZHABAN_RATE:.0%}; 最高连板仅 {SUMMARY['zt_max_board']} 板, 高度仍未打开。",
    f"<b>持久度:</b> 159929 医药长序列ETF当日涨 {pct(latest_med['latest_ret'])}; 历史 >=4% 大涨日后, 5日胜率 {med5['win_rate']:.0%}, 10日胜率 {med10['win_rate']:.0%}, 20日胜率 {med20['win_rate']:.0%}。",
]
for item in summary_bullets:
    story.append(Paragraph(f"• {item}", BULLET))
story.append(Paragraph(
    "<b>付费版一句话:</b> 今天医药强度和广度都是真强, 但历史事件研究不支持“第二天闭眼追”。"
    "更合理的读法是: 若政策/成交继续确认, 10-20日存在延续概率; 若次日冲高无承接, 5日维度反而常见震荡消化。",
    QUOTE,
))
story.append(PageBreak())

story.append(Paragraph("二、盘面结构: 医药为什么是今天主线", H2))
industry_rows = [["排名", "行业", "涨幅", "上涨/下跌", "主力净流入", "领涨"]]
for i, item in enumerate(SUMMARY["industry_top5"], 1):
    industry_rows.append([
        str(i), item["name"], pct_from_points(item["pct_chg"]),
        f'{item["up_count"]}/{item["down_count"]}', money(item["main_net_in"]), item.get("leader_name", ""),
    ])
story.append(tbl(industry_rows, [1.3 * cm, 3.2 * cm, 2.1 * cm, 2.4 * cm, 3.0 * cm, 3.0 * cm], font_size=9.2))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    "行业涨幅榜的关键不是“医药生物 +4.94%”这个单点数字, 而是生物制品、医疗服务、化学制药、中药II 同时在前五。"
    "这说明资金并非只做一个药明康德式的讨论热点, 而是在医药内部做扩散。",
    BODY,
))

zt_rows = [["行业", "涨停数", "读法"]]
for item in SUMMARY["zt_top_industries"]:
    note = "主线" if item["行业"] == "化学制药" else "扩散/对照"
    zt_rows.append([item["行业"], str(item["涨停数"]), note])
story.append(tbl(zt_rows, [4.2 * cm, 3.0 * cm, 5.0 * cm], font_size=9.8, highlight_rows={1}))
story.append(PageBreak())

story.append(Paragraph("三、量化强度: 不是单日情绪, 也不是无脑追涨", H2))
metrics_rows = [
    ["指标", "数值", "解释"],
    ["医药广度", f"{PHARMA_BREADTH:.0%}", f"5个医药细分上涨 {PHARMA_UP} 家 / 下跌 {PHARMA_DOWN} 家"],
    ["涨停集中度", f"{PHARMA_ZT}只", "化学制药位列行业涨停分布第1"],
    ["强弱差", f"{REL_STRENGTH:.1f}pp", f"医药生物 {pct_from_points(PHARMA['pct_chg'])} vs 元件 {pct_from_points(COMPONENT['pct_chg'])}"],
    ["炸板率", f"{ZHABAN_RATE:.0%}", f"{SUMMARY['zb_count']} / ({SUMMARY['zt_count']} + {SUMMARY['zb_count']})"],
    ["资金对照", f"{money(PHARMA['main_net_in'])}", f"医药生物净流入 vs 元件净流出 {money(abs(COMPONENT['main_net_in']))}"],
]
story.append(tbl(metrics_rows, [3.2 * cm, 3.0 * cm, 8.2 * cm], font_size=9.5, highlight_rows={1, 3}))
story.append(Spacer(1, 0.2 * cm))
story.append(Paragraph(
    "短线层面, 强度指标和风险指标是同时成立的: 医药广度高、涨停集中, 但炸板率并不低, 且全市场最高连板仅3板。"
    "这意味着行情可以做复盘和跟踪, 但不适合把“主线强”直接翻译成“次日无脑追”。",
    BODY,
))
story.append(PageBreak())

story.append(Paragraph("四、行情持久度: 历史大涨日后怎么走", H2))
story.append(Paragraph(
    "为了避免只用今天的盘面讲故事, 本节使用ETF价格做事件研究。事件定义为: ETF单日涨幅 >=4%, "
    "并对相邻5个交易日内的重复信号做去簇处理, 统计未来5/10/20个交易日收益。",
    BODY,
))

p_rows = [["标的", "事件", "持有期", "样本", "胜率", "中位收益", "回吐<-2%"]]
for code, label in [("159929", "医药长序列ETF"), ("159992", "创新药ETF")]:
    for horizon in [5, 10, 20]:
        row = persistence(code, horizon)
        p_rows.append([
            label, ">=4%", f"{horizon}日", str(int(row["n"])),
            f'{row["win_rate"]:.0%}', pct(row["median_ret"]), f'{row["giveback_rate"]:.0%}',
        ])
story.append(tbl(p_rows, [3.0 * cm, 1.8 * cm, 1.8 * cm, 1.6 * cm, 1.8 * cm, 2.4 * cm, 2.4 * cm], font_size=8.8,
                 highlight_rows={2, 5}))
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    f"读法: 医药长序列ETF在>=4%大涨日后, 5日胜率只有 {med5['win_rate']:.0%}, 中位收益 {pct(med5['median_ret'])}; "
    f"10日胜率回到 {med10['win_rate']:.0%}, 中位收益 {pct(med10['median_ret'])}; "
    f"20日胜率 {med20['win_rate']:.0%}, 中位收益 {pct(med20['median_ret'])}。"
    "也就是说, 行情持久度不是“第二天就线性延续”, 而更像“先震荡, 再看10-20日是否有政策/资金确认”。",
    QUOTE,
))
story.append(PageBreak())

story.append(Paragraph("五、交易框架: 付费版跟踪清单", H2))
checklist = [
    ["问题", "跟踪指标", "阈值/读法"],
    ["主线是否继续", "医药广度", "上涨家数占比继续维持>70%, 不是只剩1-2个龙头"],
    ["资金是否确认", "医药生物主力净流入", "连续2-3日为正, 且化学制药/医疗服务不掉队"],
    ["短线是否过热", "炸板率", "若继续>25%, 不追高, 等分歧后的二次确认"],
    ["行情是否扩散", "创新药ETF vs 宽基医药", "创新药相对强, 说明出海/医保叙事更纯"],
    ["风险是否缓和", "元件/通信设备", "硬件链企稳, 市场风险偏好更健康"],
]
story.append(tbl(checklist, [3.0 * cm, 4.0 * cm, 8.3 * cm], font_size=9.3, highlight_rows={1, 3}))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "本报告建议的不是“买入/卖出”指令, 而是一个跟踪框架: 如果医药广度继续维持、主力流入延续、炸板率下降, "
    "则行情从短线爆发进入可观察的10-20日持久度窗口; 如果次日只剩个别高位股和高炸板率, 则更接近冲高回落后的消化。",
    BODY,
))
story.append(PageBreak())

story.append(Paragraph("六、附录: 小红书卡片摘要", H2))
story.append(Paragraph("以下两页为对外传播版卡片的缩略图, 付费报告正文以上述量化框架为准。", BODY))
card_table = Table([[card_image("page_01.png", 6.5), card_image("page_07.png", 6.5)]], colWidths=[7.2 * cm, 7.2 * cm])
card_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
story.append(card_table)
story.append(Paragraph("图: 封面强弱对照与行情持久度回测页", CAP))

story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "免责声明: 本报告仅基于公开行情数据与历史回测, 不构成任何投资建议。历史统计不代表未来, ETF净值与成份股结构可能变化, "
    "医药政策、医保谈判、出海事件、流动性与市场风格均可能改变后续路径。",
    NOTE,
))


def main() -> None:
    doc = SimpleDocTemplate(
        str(PDF),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="医药主线量化付费研报_20260629",
        author="复旦杰伦",
    )
    doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
    print(PDF)


if __name__ == "__main__":
    main()