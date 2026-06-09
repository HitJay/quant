"""
科技抄底量化研报 — PDF生成(reportlab, 中文)
=============================================
读取 tech_dip_analysis.py 产出的 summary.json + figures/ + data/,
排版为专业付费研报 PDF。

Usage:
    conda activate research
    python analysis/tech_dip_analysis.py   # 先跑分析
    python analysis/tech_dip_report.py
"""

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ── 路径 ──
ROOT = Path("./output/2026-06-08/tech-dip-buy")
FIGS = ROOT / "figures"
PDF = ROOT / "科技抄底量化研报.pdf"
summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

# ── 字体 ──
FONT_PATH = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT_PATH))
pdfmetrics.registerFont(TTFont("CN-B", FONT_PATH))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

# ── 配色 ──
NAVY = colors.HexColor("#1a1a2e")
GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626")
ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb")
GRAY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#eef1f6")
INK = colors.HexColor("#2d2d2d")

# ── 样式 ──
H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=27, textColor=NAVY,
                    alignment=1, leading=36, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=13, textColor=GRAY,
                     alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white,
                    backColor=NAVY, leading=26, spaceBefore=20, spaceAfter=12,
                    leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY,
                    leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK,
                      leading=18, spaceAfter=7, alignment=4)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=2,
                        spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY,
                     alignment=1, leading=12, spaceAfter=10)

AS_OF = summary["as_of"]
st = summary["state"]
cur = summary["cur_dip"]
knife = summary["knife"]


def pct(x, d=1):
    return f"{x*100:+.{d}f}%" if x == x else "—"


def pct0(x):
    return f"{x*100:.0f}%" if x == x else "—"


def img(path, width_cm=16.0):
    from PIL import Image as PILImage
    p = FIGS / path
    iw, ih = PILImage.open(p).size
    w = width_cm * cm
    return Image(str(p), width=w, height=w * ih / iw)


# ── 表格构建 ──
def styled_table(data, col_widths, header_bg=NAVY, font_size=9.5, highlight_rows=None):
    t = Table(data, colWidths=col_widths, hAlign="CENTER")
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "CN"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ]
    if highlight_rows:
        for r in highlight_rows:
            style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fff3d6")))
            style.append(("FONTNAME", (0, r), (-1, r), "CN-B"))
    t.setStyle(TableStyle(style))
    return t


# ── 页眉页脚 + 水印 ──
def _watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont("CN", 60)
    canvas.setFillColor(colors.HexColor("#f0f0f2"))
    canvas.translate(A4[0] / 2, A4[1] / 2)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "付费研报 PAID")
    canvas.restoreState()


def on_first(canvas, doc):
    _watermark(canvas, doc)
    canvas.saveState()
    canvas.setFont("CN", 8.5)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm,
                             "本报告为付费内容 · 仅供个人参考 · 不构成投资建议")
    canvas.restoreState()


def on_later(canvas, doc):
    _watermark(canvas, doc)
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, A4[1] - 1.25 * cm, "科技抄底量化研报")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, f"数据截止 {AS_OF}")
    canvas.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.95 * cm,
                             f"第 {doc.page} 页 · 付费内容 · 不构成投资建议")
    canvas.restoreState()


# ════════════════════════════════════════════════════════════════
# 正文
# ════════════════════════════════════════════════════════════════
S = []  # story

# ---------- 封面 ----------
S.append(Spacer(1, 3.2 * cm))
S.append(Paragraph("科技股大跌，能抄底吗？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph("美股纳指 × A股科技 回调抄底的量化胜率研究", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))

cover_kpi = [
    ["纳指ETF 近5日", "科创50 距一年高", "芯片ETF 近10日"],
    [pct(st["513100"]["ret5"]), pct(st["588000"]["dd"]), pct(st["159995"]["ret10"])],
]
ct = Table(cover_kpi, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"), ("FONTSIZE", (0, 0), (-1, 0), 11),
    ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"), ("FONTSIZE", (0, 1), (-1, 1), 22),
    ("TEXTCOLOR", (0, 1), (-1, 1), RED),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 1), (-1, 1), 6),
]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph("基于 AKShare 十年历史日线 · 条件胜率 · 接飞刀风险 · 策略回测", SUB))
S.append(Spacer(1, 2.6 * cm))
S.append(Paragraph("出品：量化研究笔记　|　数据截止 " + AS_OF + "　|　生成 " + summary["generated"], CAP))
S.append(PageBreak())

# ---------- 摘要 ----------
S.append(Paragraph("摘要与核心结论", H2))
win_us = cur["513100"]["win60"]
win_a = cur["588000"]["win60"]
abstract = (
    f"2026年6月初，美股纳斯达克与A股硬科技板块同步快速回调：纳指ETF(513100)近5个交易日下跌"
    f"{pct(st['513100']['ret5'])}，A股芯片ETF(159995)、科创50ETF(588000)近10个交易日跌幅均接近16%。"
    f"市场再度出现\"要不要抄底\"的讨论。本报告用各标的全部历史日线，量化\"回调后买入\"的胜率、"
    f"买入后的浮亏风险，以及不同抄底方式的长期表现，给出基于数据的判断。"
)
S.append(Paragraph(abstract, BODY))
concl = [
    f"<b>回调已进入历史区间</b>：纳指当前距一年高点{pct(st['513100']['dd'])}，"
    f"科创50{pct(st['588000']['dd'])}、芯片{pct(st['159995']['dd'])}，均跌入过往的可抄底档位。",
    f"<b>胜率严重分化</b>：纳指各回撤档位持有3个月上涨概率高达67%~86%（长期向上属性），"
    f"而科创50同口径仅17%~58%，标的质量决定抄底成败。",
    f"<b>当前位置胜率</b>：纳指处于{cur['513100']['label']}档，3个月胜率约{pct0(win_us)}；"
    f"科创50处于{cur['588000']['label']}档，3个月胜率仅约{pct0(win_a)}。",
    f"<b>接飞刀风险真实存在</b>：当前档位买入后3个月内，纳指最坏浮亏{pct(knife['513100']['mae_worst'])}、"
    f"科创50最坏{pct(knife['588000']['mae_worst'])}，再跌超10%的概率分别为"
    f"{pct0(knife['513100']['prob_drop10'])}和{pct0(knife['588000']['prob_drop10'])}。",
    f"<b>策略选择</b>：高波动品种(科创50)上\"越跌越买\"未必优于无脑定投/分批；"
    f"优质资产(纳指)上一把梭与定投均大幅跑赢，分批可显著降低回撤。",
    f"<b>一句话结论</b>：可以抄底，但要<b>分品种、分批入场、严格止损</b>——"
    f"对美股科技可相对积极，对A股科技务必克制仓位、留足子弹。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph("* 本报告所有结论基于历史回测，重叠样本统计仅反映条件期望，不代表未来表现。", NOTE))
S.append(PageBreak())

# ---------- 一、市场背景 ----------
S.append(Paragraph("一、市场背景：2026年6月的科技回调", H2))
S.append(Paragraph(
    "本轮回调由海外科技股领跌：纳指在创出阶段新高后快速回撤，5个交易日跌幅超过10%；"
    "A股硬科技(科创50、芯片)受外围情绪与自身高估值压力影响，近两周补跌，回撤幅度更深；"
    "创业板50相对抗跌。下表为四个代表性ETF截至报告日的跌幅与技术状态。", BODY))
mkt = [["标的", "代码", "近5日", "近10日", "近20日", "距一年高", "RSI(14)"]]
for code in ["513100", "588000", "159995", "159949"]:
    s = st[code]
    mkt.append([s["name"], code, pct(s["ret5"]), pct(s["ret10"]),
                pct(s["ret20"]), pct(s["dd"]), f"{s['rsi']:.0f}"])
S.append(styled_table(mkt, [2.6 * cm, 1.8 * cm, 1.9 * cm, 1.9 * cm, 1.9 * cm, 2.2 * cm, 1.8 * cm]))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph(
    "解读：纳指属\"急跌\"(5日-10.6%但20日仍接近持平)，科创50/芯片属\"阴跌补跌\""
    "(10日跌约16%，RSI已进入或接近超卖)。两类回调的后续路径与抄底逻辑不同，下文分别量化。", BODY))
S.append(PageBreak())

# ---------- 二、方法 ----------
S.append(Paragraph("二、研究方法与数据", H2))
S.append(Paragraph("2.1 数据", H3))
S.append(Paragraph(
    "数据来源为 AKShare 开源接口的ETF后复权日线收盘价。纳指ETF(513100)为A股上市QDII，"
    "可直接买卖，按A股交易日历，天然贴合\"A股投资者抄美股科技\"的真实场景。"
    "纳指、创业板50样本自2016年起，科创50、芯片自2020/2021年上市起，数据截止" + AS_OF + "。", BODY))
S.append(Paragraph("2.2 回撤档位与条件胜率", H3))
S.append(Paragraph(
    "对每个交易日计算\"距过去252日最高点的回撤\"(dd)，并据此分为6档：-5~0%、-10~-5%、"
    "-15~-10%、-20~-15%、-30~-20%、≤-30%。在每个交易日按其所处档位\"买入\"，"
    "持有20/60/120个交易日(约1/3/6个月)，统计未来收益为正的比例(胜率)、平均收益、中位数与盈亏比。"
    "由于逐日取样，相邻样本高度重叠，统计量反映的是\"该回撤状态下的条件期望\"，仅供参考。", BODY))
S.append(Paragraph("2.3 接飞刀风险 (MAE)", H3))
S.append(Paragraph(
    "用最大不利偏移(Maximum Adverse Excursion)度量\"抄底后还会跌多少\"：对每个买入时点，"
    "计算其后60个交易日内的最低收盘价相对买入价的跌幅，统计中位数、最坏值与\"再跌超10%\"的概率。", BODY))
S.append(Paragraph("2.4 抄底策略回测 (仓位法)", H3))
S.append(Paragraph(
    "以单位资金、现金零利率、T+1执行、仓位∈[0,1]的口径对比三种抄底方式："
    "①一把梭(始终满仓持有)；②智能抄底(越跌越买，目标仓位=回撤深度/30%，封顶满仓)；"
    "③无脑定投(每20个交易日加一档，约5个月建满)。净值=∏(1+前一日仓位×当日收益)。", BODY))
S.append(Paragraph("2.5 指标定义", H3))
defn = [["指标", "定义"],
        ["年化收益", "按净值首尾与实际天数几何年化"],
        ["最大回撤", "净值从峰值到谷底的最大跌幅"],
        ["夏普比率", "(年化收益-2%无风险)/年化波动率"],
        ["卡玛比率", "年化收益 / 最大回撤"],
        ["盈亏比", "平均盈利 / 平均亏损(绝对值)"]]
S.append(styled_table(defn, [3.5 * cm, 12.3 * cm], font_size=9.5))
S.append(PageBreak())

# ---------- 三、当前定位 ----------
S.append(Paragraph("三、当前回调的量化定位", H2))
S.append(Paragraph(
    "下图为科创50ETF上市以来的回撤(距一年高点)曲线，阴影标出-20%~-10%的常见抄底区间，"
    "蓝色虚线为当前水平。可见当前回撤已进入历史上多次出现的中等回调区域，但尚未达到"
    "2022/2024年那种极端深跌(回撤超30%)的程度。", BODY))
S.append(img("fig_dd_history.png", 16))
S.append(Paragraph("图1　科创50ETF 历史回撤与当前位置", CAP))
S.append(Paragraph(
    f"量化定位：纳指当前dd={pct(st['513100']['dd'])}(属{cur['513100']['label']}档)，"
    f"科创50 dd={pct(st['588000']['dd'])}(属{cur['588000']['label']}档)。"
    f"科创50的RSI已降至{st['588000']['rsi']:.0f}，进入技术超卖；纳指RSI={st['513100']['rsi']:.0f}，"
    f"为急跌但未超卖。", BODY))
S.append(PageBreak())

# ---------- 四、抄底胜率 ----------
S.append(Paragraph("四、抄底胜率：跌多少才该买", H2))
S.append(Paragraph("4.1 美股科技(纳指ETF) 各档位持有3个月胜率", H3))


def winrate_table(records, cur_label):
    rows = [["回撤档位", "样本数", "胜率", "平均收益", "中位数", "盈亏比"]]
    hl = []
    for i, r in enumerate(records, start=1):
        if r["样本"] < 5 or r["胜率"] != r["胜率"]:
            continue
        rows.append([r["档位"], str(int(r["样本"])), pct0(r["胜率"]),
                     pct(r["均值"]), pct(r["中位数"]),
                     f"{r['盈亏比']:.2f}" if r["盈亏比"] == r["盈亏比"] else "—"])
        if r["档位"] == cur_label:
            hl.append(len(rows) - 1)
    return rows, hl


rows_us, hl_us = winrate_table(summary["winrate_us"], cur["513100"]["label"])
S.append(styled_table(rows_us, [2.8 * cm, 2.2 * cm, 2.4 * cm, 2.6 * cm, 2.6 * cm, 2.4 * cm],
                      highlight_rows=hl_us))
S.append(Paragraph("（高亮行为当前所处档位）", NOTE))
S.append(Paragraph("4.2 A股科技(科创50ETF) 各档位持有3个月胜率", H3))
rows_a, hl_a = winrate_table(summary["winrate_a"], cur["588000"]["label"])
S.append(styled_table(rows_a, [2.8 * cm, 2.2 * cm, 2.4 * cm, 2.6 * cm, 2.6 * cm, 2.4 * cm],
                      highlight_rows=hl_a))
S.append(Paragraph("（高亮行为当前所处档位）", NOTE))
S.append(Spacer(1, 0.2 * cm))
S.append(img("fig_winrate_compare.png", 16))
S.append(Paragraph("图2　两类科技资产 各回撤档位抄底胜率对比", CAP))
S.append(Paragraph(
    "深度解读：纳指几乎在任何回撤档位抄底，持有3个月的胜率都在67%以上，这是其十年长牛"
    "(年化约20%)的结构性结果——回调即上车机会。科创50则呈现典型的高波动震荡特征：浅回调"
    "(-5~0%)买入胜率反而最低(仅17%，因多为高位回落)，中等回调(-15~-5%)胜率回升至56%~58%，"
    "而深度回调(-30~-20%)胜率骤降至28%(下跌趋势中的接刀)。这说明对A股科技，"
    "\"机械地越跌越买\"并不可靠，需结合趋势与止损。", BODY))
S.append(PageBreak())

# ---------- 五、接飞刀 ----------
S.append(Paragraph("五、接飞刀风险：抄底后还会跌多少", H2))
kf = [["标的", "当前档位", "样本数", "浮亏中位", "最坏浮亏", "再跌超10%概率"]]
for code in ["513100", "588000"]:
    k = knife[code]
    kf.append([st[code]["name"], cur[code]["label"], str(int(k["n"])),
               pct(k["mae_median"]), pct(k["mae_worst"]), pct0(k["prob_drop10"])])
S.append(styled_table(kf, [2.6 * cm, 2.6 * cm, 2.0 * cm, 2.4 * cm, 2.4 * cm, 3.0 * cm]))
S.append(Spacer(1, 0.2 * cm))
S.append(img("fig_mae_dist.png", 16))
S.append(Paragraph("图3　当前档位买入后3个月内最大浮亏分布", CAP))
S.append(Paragraph(
    f"解读：即便胜率不低，抄底买入后短期内承受浮亏几乎是常态。纳指当前档位买入后3个月浮亏中位"
    f"{pct(knife['513100']['mae_median'])}，但最坏曾达{pct(knife['513100']['mae_worst'])}；"
    f"科创50浮亏中位虽小({pct(knife['588000']['mae_median'])})，但尾部风险更大，最坏达"
    f"{pct(knife['588000']['mae_worst'])}，再跌超10%的概率高达{pct0(knife['588000']['prob_drop10'])}。"
    f"这意味着：抄底必须为浮亏预留空间，一次性满仓极易被深套。", BODY))
S.append(PageBreak())

# ---------- 六、策略回测 ----------
S.append(Paragraph("六、抄底策略回测：哪种抄法更靠谱", H2))
S.append(img("fig_strategy_nav.png", 16))
S.append(Paragraph("图4　三种抄底方式净值对比(左:科创50  右:纳指)", CAP))


def strat_table(metrics, title):
    rows = [["策略", "总收益", "年化", "最大回撤", "夏普", "卡玛"]]
    for name, m in metrics.items():
        rows.append([name, pct(m["total"], 0), pct(m["ann"]), pct0(m["mdd"]),
                     f"{m['sharpe']:.2f}", f"{m['calmar']:.2f}"])
    return rows


S.append(Paragraph("6.1 A股科技 · 科创50ETF", H3))
S.append(styled_table(strat_table(summary["strategy_metrics"], "科创50"),
                      [3.6 * cm, 2.4 * cm, 2.2 * cm, 2.4 * cm, 1.9 * cm, 1.9 * cm]))
S.append(Paragraph("6.2 美股科技 · 纳指ETF", H3))
S.append(styled_table(strat_table(summary["strategy_metrics_us"], "纳指"),
                      [3.6 * cm, 2.4 * cm, 2.2 * cm, 2.4 * cm, 1.9 * cm, 1.9 * cm]))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph(
    "解读：两张表揭示同一条规律——<b>标的质量决定抄底成败</b>。在长期向上的纳指上，"
    "一把梭与定投都录得数倍收益，定投/分批还能把最大回撤从约29%进一步平滑；"
    "而在长期震荡、年化仅个位数的科创50上，\"智能抄底(越跌越买)\"虽然把回撤从60%压到43%，"
    "总收益却为负，反而是\"无脑定投\"以更低成本取得相对最优。结论：抄底方法的优劣高度依赖标的，"
    "对弱趋势品种，纪律性分批与止损比\"抄得狠\"更重要。", BODY))
S.append(PageBreak())

# ---------- 七、实操 ----------
S.append(Paragraph("七、实操建议", H2))
S.append(Paragraph("7.1 美股科技(纳指)：回调即机会，但控好成本", H3))
for c in ["长期结构向上，胜率高，回调可相对积极；",
          "建议在距高点-10%~-15%区间分2-3批建仓；",
          "留意QDII溢价与汇率波动，避免在高溢价时追买；",
          "可作为核心仓位长期持有，定投平滑入场成本。"]:
    S.append(Paragraph(c, BULLET, bulletText="▪"))
S.append(Paragraph("7.2 A股科技(科创50/芯片)：克制仓位，严格止损", H3))
for c in ["波动大、胜率平庸，切忌一把梭满仓；",
          "等待RSI跌入超卖(<35)且跌破年线企稳后再分批；",
          "单一品种仓位建议不超过总仓20%，作为卫星仓位；",
          "设置-15%硬止损，破位认错，避免深套。"]:
    S.append(Paragraph(c, BULLET, bulletText="▪"))
S.append(Paragraph("7.3 通用资金管理框架", H3))
fw = [["回撤档位", "建议累计仓位(占该标的预算)", "动作"],
      ["-5%~-10%", "20%~30%", "试探性建仓"],
      ["-10%~-15%", "40%~60%", "主力分批"],
      ["-15%~-20%", "60%~80%", "加仓但留子弹"],
      ["≤-20% 且破位", "止损/暂停", "趋势走坏，先保本金"]]
S.append(styled_table(fw, [3.4 * cm, 6.6 * cm, 5.8 * cm], font_size=9.5))
S.append(Paragraph("通用铁律：分批进场 · 永远留子弹 · 不借钱抄底 · 必设止损。", BODY))
S.append(PageBreak())

# ---------- 八、风险 + 附录 ----------
S.append(Paragraph("八、风险提示与免责声明", H2))
for c in ["本报告基于历史数据回测，历史规律不代表未来，市场环境可能发生结构性变化；",
          "条件胜率采用逐日重叠样本，存在自相关，统计显著性弱于独立样本；",
          "回测未完全计入冲击成本、QDII溢价波动、申赎限制等真实摩擦；",
          "纳指ETF受汇率与海外市场风险影响，A股科技受流动性与政策影响；",
          "本报告为付费研究内容，仅供个人学习参考，不构成任何投资建议，据此操作风险自负。"]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("附录：数据来源与复现", H2))
S.append(Paragraph(
    "数据来源：AKShare 开源接口(ETF后复权日线)。分析与可视化基于本仓库 quant 工具链"
    "(quant.data / quant.backtest.metrics / quant.factors.timing)。", BODY))
appx = [["交付文件", "说明"],
        ["cards/01~07_*.png", "小红书7张分享卡片"],
        ["科技抄底量化研报.pdf", "本研报(付费内容)"],
        ["figures/*.png", "研报图表(回撤/胜率/接飞刀/净值)"],
        ["data/*.csv", "当前状态/条件胜率/接飞刀/策略净值与指标"],
        ["summary.json", "全部关键数字汇总"],
        ["code/tech_dip_analysis.py", "分析+卡片+CSV 复现脚本"],
        ["code/tech_dip_report.py", "本PDF生成脚本"]]
S.append(styled_table(appx, [5.6 * cm, 10.2 * cm], font_size=9.5))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    "复现命令：<br/>conda activate research<br/>"
    "python analysis/tech_dip_analysis.py<br/>"
    "python analysis/tech_dip_report.py", NOTE))


# ── 生成 ──
doc = SimpleDocTemplate(
    str(PDF), pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=1.8 * cm, bottomMargin=1.6 * cm,
    title="科技抄底量化研报", author="量化研究笔记")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print(f"PDF 已生成 → {PDF}  ({PDF.stat().st_size//1024} KB)")
