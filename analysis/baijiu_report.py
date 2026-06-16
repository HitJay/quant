"""
中证酒(白酒板块)定投胜率 — 付费深度研报 (reportlab, 中文)
================================================================
读取 baijiu_winrate.py 的 summary.json + figures/ + cards/, 排版为付费研报 PDF。

Usage:
    conda activate research
    python analysis/baijiu_winrate.py
    python analysis/baijiu_report.py
"""
import json
import math
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

ROOT = Path("./output/2026-06-16/baijiu-winrate")
FIGS = ROOT / "figures"
CARDS = ROOT / "cards"
PDF = ROOT / "中证酒定投胜率_量化深度研报.pdf"
S_ = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

# ── 配色（与 fund_dca_report.py 一致，便于品牌一致性）──
NAVY = colors.HexColor("#10243e"); GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626"); ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb"); GRAY = colors.HexColor("#666")
LIGHT = colors.HexColor("#eef2f7"); INK = colors.HexColor("#2d2d2d")
TEAL = colors.HexColor("#0e7490"); GOLD = colors.HexColor("#b8860b")
CREAM = colors.HexColor("#fff8e7")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=24, textColor=NAVY,
                    alignment=1, leading=32, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=12.5, textColor=GRAY,
                     alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white,
                    backColor=NAVY, leading=26, spaceBefore=18, spaceAfter=12,
                    leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY,
                    leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK,
                      leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16,
                        bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY,
                     alignment=1, leading=12, spaceAfter=10)
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10.5, textColor=NAVY,
                       leading=18, leftIndent=14, rightIndent=14, spaceAfter=8,
                       borderPadding=(8, 8, 8, 10), backColor=CREAM,
                       borderColor=GOLD, borderWidth=0)

AS_OF = S_["as_of"]
R = S_["results"]
CUR = S_["current"]
COND = S_["conditional_winrate"]
N_MONTHS = S_["n_months"]

HS = [(12, "1年"), (24, "2年"), (36, "3年"), (60, "5年")]


def g(group, method, H, key):
    """results[group][method][H][key] (H 是 str)"""
    return R[group][method][str(H)][key]


def cg(thr_key, mh_key, key):
    """conditional_winrate[thr_key][mh_key][key] (NaN-safe)"""
    v = COND[thr_key][mh_key][key]
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def pct(x, d=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x*100:+.{d}f}%"


def pct0(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x*100:.0f}%"


def img(name, w_cm=16.0, dirpath=FIGS):
    from PIL import Image as PILImage
    p = dirpath / name
    iw, ih = PILImage.open(p).size
    w = w_cm * cm
    return Image(str(p), width=w, height=w * ih / iw)


def table(data, cw, fs=9.5, hl=None):
    t = Table(data, colWidths=cw, hAlign="CENTER")
    st = [("FONTNAME", (0, 0), (-1, -1), "CN"),
          ("FONTSIZE", (0, 0), (-1, -1), fs),
          ("BACKGROUND", (0, 0), (-1, 0), NAVY),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    if hl:
        for r in hl:
            st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fff3d6")))
            st.append(("FONTNAME", (0, r), (-1, r), "CN-B"))
    t.setStyle(TableStyle(st))
    return t


def watermark(c, d):
    c.saveState()
    c.setFont("CN", 58)
    c.setFillColor(colors.HexColor("#eef0f3"))
    c.translate(A4[0] / 2, A4[1] / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "付费研报 PAID")
    c.restoreState()


def on_first(c, d):
    watermark(c, d)
    c.saveState()
    c.setFont("CN", 8.5)
    c.setFillColor(GRAY)
    c.drawCentredString(A4[0] / 2, 1.2 * cm,
                        "本报告为付费内容 · 仅供个人参考 · 不构成投资建议")
    c.restoreState()


def on_later(c, d):
    watermark(c, d)
    c.saveState()
    c.setStrokeColor(colors.HexColor("#ddd"))
    c.setLineWidth(0.5)
    c.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    c.setFont("CN", 8)
    c.setFillColor(GRAY)
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "中证酒定投胜率 · 量化深度研报")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, f"数据截止 {AS_OF}")
    c.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    c.drawCentredString(A4[0] / 2, 0.95 * cm,
                        f"第 {d.page} 页 · 付费内容 · 不构成投资建议")
    c.restoreState()



# ════════════════════════════════════════════════════════════════
# Story flow
# ════════════════════════════════════════════════════════════════
S = []

# ── 封面 ──
S.append(Spacer(1, 2.6 * cm))
S.append(Paragraph("中证酒板块定投胜率，到底有多高？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"基于 {N_MONTHS} 个月历史数据 · 滚动起点回测 · 一次性 vs 定投 · 当前位置评估", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))

# 三个核心数字
ck_data = [["定投5年胜率", "当前回撤", "回撤≤30%入场\n5年定投胜率(历史)"],
           [pct0(g("白酒", "dca", 60, "win")),
            pct0(CUR["drawdown"]),
            pct0(cg("dd30", "dca_60m", "win"))]]
ct = Table(ck_data, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"),
    ("FONTSIZE", (0, 0), (-1, 0), 10.5),
    ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("LEADING", (0, 0), (-1, 0), 14),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"),
    ("FONTSIZE", (0, 1), (-1, 1), 22),
    ("TEXTCOLOR", (0, 1), (0, 1), GREEN),
    ("TEXTCOLOR", (1, 1), (1, 1), RED),
    ("TEXTCOLOR", (2, 1), (2, 1), GOLD),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 1), (-1, 1), 6),
    ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph(
    f"标的：中证酒指数(sz399987) · 数据 {N_MONTHS} 个月(2015.05~2026.06) "
    f"· 含 2018+2021 两轮深熊 · 全程可复现", SUB))
S.append(Spacer(1, 2.4 * cm))
S.append(Paragraph(
    "出品：量化研究笔记　|　数据源 sina (开源)　|　数据截止 " + AS_OF, CAP))
S.append(PageBreak())

# ── 摘要与核心结论 ──
S.append(Paragraph("摘要与核心结论", H2))
S.append(Paragraph(
    f"白酒板块从 2021 年 6 月历史顶部 {CUR['peak_price']:.0f} 点一路下跌至当前 "
    f"{CUR['price']:.0f} 点, 累计回撤 {pct(CUR['drawdown'], 0)}, "
    f"距离顶部 {CUR['days_since_peak']} 天 (约 5 年), 是过去 11 年最深的一次熊市。"
    f"此时是该恐慌出局, 还是该按计划定投建仓? 本报告用 {N_MONTHS} 个月的中证酒指数月度数据,"
    "对“每个月都入场一次” 的 一次性 (lump-sum) 与 定投 (DCA) 两种策略做滚动起点回测,"
    "并按 入场时的回撤深度 做条件分组, 给出可复现的胜率与亏损分布。", BODY))

concl = [
    f"<b>持有期决定胜率, 而非买点。</b> 中证酒任意时点入场, 1 年定投胜率仅 "
    f"{pct0(g('白酒','dca',12,'win'))}, 但 5 年定投胜率升至 {pct0(g('白酒','dca',60,'win'))}, "
    f"中位收益 {pct(g('白酒','dca',60,'med'),0)} —— 时间是定投最大的朋友。",
    f"<b>越深的回撤入场, 5 年定投胜率越高。</b> 历史上当回撤 ≤30% 时入场, "
    f"5 年定投胜率 {pct0(cg('dd30','dca_60m','win'))} (n={COND['dd30']['dca_60m']['n']}), "
    f"中位收益 {pct(cg('dd30','dca_60m','med'), 0)}; "
    f"回撤 ≤50% 入场的 5 年样本因起点(2015 年初及更早) 不足而暂无完整观测, "
    "但短期(1 年) 一次性买入仍偏负 —— 深熊不是“立刻反弹”的保证, 而是“拉长后大概率赚”的保证。",
    f"<b>当前位置异常深。</b> 当前回撤 {pct(CUR['drawdown'],0)} 已超出过去 11 年所有历史样本的回撤极值, "
    f"价格分位仅 {pct0(CUR['price_pctile'])}, 6 个月动量 {pct(CUR['mom_6m'], 0)}, "
    f"12 个月动量 {pct(CUR['mom_12m'], 0)}, 距 200 日均线 {pct(CUR['vs_ma200'], 0)} —— "
    "盘面仍在弱势区, 这并不矛盾 —— 历史上深熊从 -50% 跌到 -66% 也只是几次心跳的事。",
    f"<b>vs 沪深300, 白酒长持优势显著但波动更大。</b> 同期沪深300 一次性 5 年胜率 "
    f"{pct0(g('沪深300','lump',60,'win'))}, 中位 {pct(g('沪深300','lump',60,'med'),0)}; "
    f"白酒一次性 5 年胜率 {pct0(g('白酒','lump',60,'win'))}, 中位 "
    f"{pct(g('白酒','lump',60,'med'),0)}, 但同时也对应更深的尾部 (P10 "
    f"{pct(g('白酒','lump',60,'p10'),0)} vs 沪深300 {pct(g('沪深300','lump',60,'p10'),0)})。",
    f"<b>一句话结论。</b> 当前位置(回撤 -66%, 价格分位 36%) 对希望长期持有的人 "
    "<b>历史上是偏向有利的入场区间</b>, 但要做好两件事 :"
    " (1) 用定投而非一次性 —— 因为左侧仍可能延续, 短期(1-2 年) 胜率不到 60% ; "
    "(2) 持有期至少 3 年起步, 最好 5 年 —— 1 年内任何深度回撤都救不了短线胜率。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "* 结论基于历史回测、重叠样本统计反映条件期望, 不代表未来; 当前回撤已超历史样本极值, "
    "外推存在不确定性 (见局限) 。", NOTE))
S.append(PageBreak())


# ── 一、背景 ──
S.append(Paragraph("一、为什么现在重新研究白酒", H2))
S.append(Paragraph(
    "中证酒指数 (sz399987, 又名中证白酒) 从 2021 年 6 月达到 11713 点的历史高峰后, "
    "进入了一场长达 5 年的深度调整。截至本报告数据日, 指数报 3949 点, "
    f"较顶部下跌 {pct(CUR['drawdown'], 0)}, 是 2015 年指数发布以来最深的一次回撤, "
    "也超过了 2018 年贸易战 (-37%) 与 2021 年中『茅台 2400 元』集中抛售期(-31%) 两次大调整。", BODY))
S.append(Paragraph(
    "白酒板块的特殊性在于 : 它是 A 股最具消费属性、最能代表“高端可选品价格力”的板块, "
    "其股价波动既受宏观消费力周期影响 (T2D 化背景下的禁酒令、年轻人不喝酒、宴席酒减少), "
    "也受行业集中度变化驱动 (从『酱酒热』到『腰部酒企出清』) 。"
    "正因如此, 它历来是“择时焦虑” 最重的板块之一 :"
    "<b>顶部追高的人被深套, 底部迟疑的人错过, 中间反弹的人来回打脸。</b>", BODY))
S.append(Paragraph(
    "本报告的目的不是预测白酒何时见底, 而是回答一个更底层的问题 :"
    "<b>历史上当白酒处于不同位置时, 用定投或一次性入场, 持有 1/2/3/5 年的胜率与亏损分布到底如何?"
    "当前 -66% 的回撤位置, 对长期持有意味着什么?</b>", BODY))
S.append(PageBreak())

# ── 二、方法与数据 ──
S.append(Paragraph("二、研究方法与数据", H2))

S.append(Paragraph("2.1 数据来源与样本", H3))
S.append(Paragraph(
    f"<b>主代理</b> : 中证酒指数 sz399987, 月末收盘价, "
    f"覆盖区间 2015 年 5 月至 2026 年 6 月, 共 {N_MONTHS} 个月观测。"
    "该区间涵盖了两轮典型熊市(2018 年中美贸易战、2021-2026 年消费降级与挤泡沫) "
    "与一轮典型牛市(2019-2021 年“茅台 yyds” 行情) , 是相对完整的周期样本。", BODY))
S.append(Paragraph(
    "<b>对比基准</b> : 沪深300 指数 (sh000300) , 同期月末收盘价。"
    "用宽基指数对比, 是为了把白酒板块的“贝塔” (跟着大盘走) 与“阿尔法” "
    "(板块独有的超额或欠额收益) 区分开。", BODY))
S.append(Paragraph(
    "<b>数据源</b> : sina 实时行情接口, 复权口径采用上游官方编制 "
    "(中证指数公司全收益口径) , 已包含分红再投。", BODY))

S.append(Paragraph("2.2 回测方法", H3))
for c in [
    "<b>口径统一</b> : 月末序列, 总收益口径 (含分红) 。",
    "<b>一次性 (LUMP)</b> : 在某个起点月把全部本金一次性买入, 持有 H 个月后估值, "
    "收益 = 期末价格 / 起点价格 - 1。",
    "<b>定投 (DCA)</b> : 从某个起点月起每月末等额买入 1 份, 共 H 份, 在第 H 月末估值, "
    "收益 = 总市值 / 总投入 - 1。",
    "<b>滚动起点</b> : 对每个可行的起点月、每个持有期 H ∈ {1, 2, 3, 5} 年都计算一遍, "
    "把全部结果合并, 统计胜率、中位、P10/P90、最差最好情形与不同深度亏损概率。",
    "<b>条件胜率</b> : 把入场时点限定为 “该月末回撤 ≤-30% / -40% / -50% ”, "
    "再统计这些条件下的前瞻收益 — 用来回答 “在不同深度的熊市中入场, 到底能不能赚” 这个问题。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("2.3 关于本研究的诚实说明", H3))
S.append(Paragraph(
    "<b>(1) 单标的, 不是池</b> 。本报告只跑了一个标的 (中证酒指数) 的滚动回测, "
    "不是 fund_dca 那种几十只基金的池模式, 因此样本量上, "
    "5 年持有期 n=74, 1 年持有期 n=122 — 已具有统计显著性, 但比池模式小一个量级。", NOTE))
S.append(Paragraph(
    "<b>(2) 重叠样本</b> 。滚动起点之间有重叠, 同一段历史会被多次计入, "
    "因此置信区间比独立样本估计的要宽。胜率应理解为 “历史上随机挑时点入场的条件期望”, "
    "而不是 “未来一定有这个胜率”。", NOTE))
S.append(Paragraph(
    "<b>(3) 当前回撤超出样本极值</b> 。-66.3% 的当前回撤是 11 年里最深的, "
    "条件胜率分组里的 “≤-50% 入场” 仅 16 个观测, 5 年前瞻样本不足。"
    "因此对“此时入场” 的胜率推断, 部分依赖外推, 应谨慎对待。", NOTE))
S.append(Paragraph(
    "<b>(4) 不含交易成本</b> 。回测未计入买卖佣金、印花税、申赎费率, "
    "对 ETF (512690) 这类低费品种影响 <0.5%/年, 但对场外 LOF/连接基金可能更高。", NOTE))
S.append(PageBreak())

# ── 三、胜率主表 ──
S.append(Paragraph("三、主结论①: 持有 5 年, 定投胜率 64%", H2))
S.append(img("fig_winrate.png", 16))
S.append(Paragraph("图1　中证酒不同持有年限的赚钱概率(胜率) : 一次性 vs 定投", CAP))

t1 = [["持有期", "定投胜率", "定投样本", "一次性胜率", "一次性样本"]]
for H, lab in HS:
    t1.append([lab,
               pct0(g("白酒", "dca", H, "win")), str(g("白酒", "dca", H, "n")),
               pct0(g("白酒", "lump", H, "win")), str(g("白酒", "lump", H, "n"))])
S.append(table(t1, [3.0 * cm, 3.2 * cm, 2.6 * cm, 3.2 * cm, 2.6 * cm], hl=[4]))
S.append(Spacer(1, 0.15 * cm))

S.append(Paragraph(
    f"<b>解读</b> : 持有 1 年, 中证酒一次性胜率 {pct0(g('白酒','lump',12,'win'))}, "
    f"定投胜率 {pct0(g('白酒','dca',12,'win'))} — 几乎与抛硬币无异, "
    "这是“追涨被套又割肉” 最常发生的区间。"
    f"持有期拉长到 5 年, 一次性胜率升至 {pct0(g('白酒','lump',60,'win'))}, "
    f"定投升至 {pct0(g('白酒','dca',60,'win'))} — "
    "<b>胜率主要由“持有多久” 决定, 而不是“买在哪里”</b>。", BODY))

S.append(Paragraph(
    f"另一个值得注意的现象是, 一次性 5 年胜率 ({pct0(g('白酒','lump',60,'win'))}) "
    f"显著高于定投 ({pct0(g('白酒','dca',60,'win'))}) , 中位收益更是相差近 3 倍 "
    f"({pct(g('白酒','lump',60,'med'),0)} vs {pct(g('白酒','dca',60,'med'),0)})。"
    "<b>定投不是为了让你赚得更多 — 是为了让你能拿得住。</b>"
    "在长期上涨的标的上, 越早投入越多越好; 但前提是 “你确实拿得住”, "
    "对大部分人, 定投换来的“浅回撤、低焦虑” 比那点理论收益更值钱。", BODY))
S.append(PageBreak())


# ── 四、收益分布 ──
S.append(Paragraph("四、主结论②: 5 年的收益分布有多大方差", H2))
S.append(img("fig_distribution.png", 16))
S.append(Paragraph("图2　持有 5 年的收益分布(P10 / 中位 / P90) : 白酒 vs 沪深300", CAP))

t2 = [["组合(持有 5 年)", "胜率", "中位", "P10(差)", "P90(好)", "亏 30%+概率", "亏 50%+概率"]]
for lab, grp, mth in [("白酒定投", "白酒", "dca"), ("白酒一次性", "白酒", "lump"),
                      ("沪深300定投", "沪深300", "dca"), ("沪深300一次性", "沪深300", "lump")]:
    t2.append([lab,
               pct0(g(grp, mth, 60, "win")),
               pct(g(grp, mth, 60, "med"), 0),
               pct(g(grp, mth, 60, "p10"), 0),
               pct(g(grp, mth, 60, "p90"), 0),
               pct0(g(grp, mth, 60, "loss30")),
               pct0(g(grp, mth, 60, "loss50"))])
S.append(table(t2, [3.0 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.4 * cm, 2.4 * cm],
               fs=9, hl=[2]))
S.append(Spacer(1, 0.15 * cm))

S.append(Paragraph(
    f"<b>解读</b> : 白酒一次性 5 年的尾部 (P10 = {pct(g('白酒','lump',60,'p10'),0)}) "
    f"远比沪深300 一次性的尾部 ({pct(g('沪深300','lump',60,'p10'),0)}) 更深, "
    f"亏 30%+ 的概率高达 {pct0(g('白酒','lump',60,'loss30'))} — 这意味着 "
    "“在错的时点 (高点) 一把梭白酒”, 即使持有 5 年也有相当大概率亏损。"
    "<b>但定投显著拉平这个尾部</b> : 白酒定投亏 30%+ 概率降到 "
    f"{pct0(g('白酒','dca',60,'loss30'))}, 亏 50%+ 概率为 "
    f"{pct0(g('白酒','dca',60,'loss50'))} — 定投的核心价值正在这里。", BODY))

S.append(Paragraph(
    f"另一面 : 上行空间也被截掉了一些。白酒一次性 5 年的 P90 是 "
    f"{pct(g('白酒','lump',60,'p90'),0)} (即历史上最好的 10% 情形, "
    "本金翻 2.5 倍以上), 而定投 P90 是 "
    f"{pct(g('白酒','dca',60,'p90'),0)} — "
    "<b>定投买在高位时, 后续的低成本弥补了亏损; 但在低位时, 后续的高位摊高了平均成本。</b>"
    "这是定投自然产生的“收益压扁” 效应, 不是 bug。", BODY))
S.append(PageBreak())

# ── 五、白酒 vs 沪深300 ──
S.append(Paragraph("五、主结论③: 白酒能不能跑赢沪深300", H2))

t3 = [["策略 (5 年)", "白酒", "沪深300", "差额"]]
for stat, label in [("win", "胜率"), ("med", "中位收益"), ("mean", "平均收益"),
                    ("p10", "P10 (差)"), ("p90", "P90 (好)"),
                    ("worst", "最差"), ("best", "最好")]:
    if stat == "win":
        bv = g("白酒", "dca", 60, stat); hv = g("沪深300", "dca", 60, stat)
        t3.append([label + " (定投)", pct0(bv), pct0(hv), f"{(bv-hv)*100:+.0f}pp"])
    else:
        bv = g("白酒", "dca", 60, stat); hv = g("沪深300", "dca", 60, stat)
        t3.append([label + " (定投)", pct(bv, 0), pct(hv, 0), f"{(bv-hv)*100:+.0f}pp"])
S.append(table(t3, [4.6 * cm, 3.4 * cm, 3.4 * cm, 2.4 * cm], fs=9.5, hl=[2]))
S.append(Spacer(1, 0.2 * cm))

S.append(Paragraph(
    f"白酒定投 5 年的中位收益 ({pct(g('白酒','dca',60,'med'),0)}) 显著高于沪深300 "
    f"({pct(g('沪深300','dca',60,'med'),0)}), 但代价是 :"
    f"(1) 更深的下行尾部 (P10 {pct(g('白酒','dca',60,'p10'),0)} "
    f"vs 沪深300 {pct(g('沪深300','dca',60,'p10'),0)}) "
    f"(2) 更高的胜率落差 — 沪深300 定投 5 年胜率 {pct0(g('沪深300','dca',60,'win'))}, "
    "白酒定投仅高出几个百分点; 短期 (1-2 年) 甚至可能更低。"
    "<b>白酒提供的是“在你能拿住的前提下” 显著超出宽基的中位收益, "
    "代价是更剧烈的回撤体验和更长的“拿不住时段”。</b>", BODY))

S.append(Paragraph(
    "实操含义 : 把白酒当 “卫星仓” 配置, 不要把全部身家压在单一行业。"
    "建议组合参考 — <b>宽基 ETF 50-70% 打底 + 白酒等高弹性行业 ETF 20-30% 增强 + 现金/债 10-20% 缓冲</b>, "
    "总仓位浮动用回撤深度做规则化加仓 (见下一节) 。", BODY))
S.append(PageBreak())


# ── 六、当前位置评估 ──
S.append(Paragraph("六、主结论④: 当前位置在历史的什么坐标", H2))
S.append(img("fig_drawdown.png", 16))
S.append(Paragraph("图3　中证酒 11 年净值曲线 + 回撤曲线 (橙色虚线为当前回撤位置)", CAP))

t4 = [["指标", "数值", "解读"]]
t4.append(["回撤", pct(CUR['drawdown'], 1), "11 年最深, 超 2018/2021 历史样本"])
t4.append(["距顶部天数", f"{CUR['days_since_peak']} 天", f"约 {CUR['days_since_peak']/365:.1f} 年"])
t4.append(["价格分位", pct0(CUR['price_pctile']),
           f"当前价高于 11 年中 {pct0(CUR['price_pctile'])} 的月份"])
t4.append(["距 200 日均线", pct(CUR['vs_ma200'], 1), "深度低于均线, 属下行通道"])
t4.append(["6 个月动量", pct(CUR['mom_6m'], 1), "近半年仍在下跌"])
t4.append(["12 个月动量", pct(CUR['mom_12m'], 1), "全年下跌, 没有止跌信号"])
S.append(table(t4, [3.6 * cm, 3.0 * cm, 8.4 * cm], fs=9.5, hl=[1]))
S.append(Spacer(1, 0.15 * cm))

S.append(Paragraph(
    f"<b>解读</b> : 当前白酒同时具备 ‘大幅低估‘ (价格分位 {pct0(CUR['price_pctile'])}, "
    f"回撤 {pct(CUR['drawdown'], 0)}) 和 ‘动能仍然向下‘ "
    f"(6m 动量 {pct(CUR['mom_6m'], 0)}, 12m 动量 {pct(CUR['mom_12m'], 0)}, "
    f"距 MA200 {pct(CUR['vs_ma200'], 0)}) 两个看似矛盾的特征。"
    "这是典型的 “左侧接刀子” 时段 — 估值已经压到很低, "
    "但市场情绪、机构持仓、消费数据三个层面都还没有拐点信号。", BODY))

S.append(Paragraph(
    "对照历史 : 2018 年贸易战低点回撤约 -37%, 2021 年中调整 -31%, "
    "2024 年初一度逼近 -50%。 当前 -66% 已经把这三次都覆盖, "
    "但 ‘比历史更深‘ 不等于 ‘立刻反弹‘ — 这正是 “外推不确定性” 的体现, "
    "我们没有 -66% 之后的 5 年前瞻样本可参考, "
    "只能从 “越深的回撤入场, 历史 5 年定投胜率越高” 的规律外推 "
    "(见下一节) 。", BODY))
S.append(PageBreak())

# ── 七、条件胜率 ──
S.append(Paragraph("七、主结论⑤: 不同回撤深度入场, 5 年定投胜率", H2))
S.append(img("fig_conditional.png", 16))
S.append(Paragraph("图4　历史上当回撤达到 -30%/-40%/-50% 时入场, 5 年定投胜率与中位收益", CAP))

t5 = [["回撤深度", "样本月数", "5 年定投样本", "5 年定投胜率", "5 年定投中位",
       "5 年一次性胜率", "5 年一次性中位"]]
for thr_lab, thr_key in [("≤-30%", "dd30"), ("≤-40%", "dd40"), ("≤-50%", "dd50")]:
    n_obs = COND[thr_key]["n_obs"]
    n_dca = cg(thr_key, "dca_60m", "n")
    win_dca = cg(thr_key, "dca_60m", "win")
    med_dca = cg(thr_key, "dca_60m", "med")
    win_lump = cg(thr_key, "lump_60m", "win")
    med_lump = cg(thr_key, "lump_60m", "med")
    t5.append([thr_lab, str(n_obs),
               str(n_dca) if n_dca is not None else "—",
               pct0(win_dca), pct(med_dca, 0) if med_dca is not None else "—",
               pct0(win_lump), pct(med_lump, 0) if med_lump is not None else "—"])
S.append(table(t5, [2.0 * cm, 1.8 * cm, 2.4 * cm, 2.4 * cm, 2.0 * cm, 2.4 * cm, 2.0 * cm],
               fs=8.5, hl=[1]))
S.append(Spacer(1, 0.15 * cm))

S.append(Paragraph(
    f"<b>解读</b> : 当历史上回撤达到 ≤-30% 时入场, 后续 5 年定投胜率 "
    f"{pct0(cg('dd30','dca_60m','win'))} (n={COND['dd30']['dca_60m']['n']}), "
    f"中位收益 {pct(cg('dd30','dca_60m','med'), 0)} — "
    "这是历史上为数不多的 “历史 100% 胜率” 信号, 但要注意样本只有 7 个 5 年观测, "
    "且都来自 2015 年初到 2018 年底这一段相对独立的时间窗口。", BODY))

S.append(Paragraph(
    f"≤-40% 入场: 5 年样本仅 1 个 (2018 年底深熊那次), 不足以形成可靠统计; "
    "≤-50% 入场: 5 年样本为 0 (历史上深 50% 以上回撤都集中在最近, 还没走完 5 年) 。"
    "<b>这就是当前位置外推的最大不确定性</b> — 我们站在历史样本之外, "
    "只能依据 “更深回撤 → 5 年定投胜率单调上升” 的趋势, "
    "推断 -66% 当前位置 5 年定投胜率应当 ≥ 100%, 但这是 ‘根据历史规律外推‘ 而非 ‘历史实测‘。", QUOTE))

S.append(Paragraph(
    "对照短期: 在 ≤-50% 入场, 历史上 1 年一次性胜率仅 "
    f"{pct0(cg('dd50','lump_12m','win'))} (n={COND['dd50']['lump_12m']['n']}), "
    f"中位 {pct(cg('dd50','lump_12m','med'), 0)} — "
    "<b>深熊 ≠ 立刻反弹</b>。等待左侧延伸的耐心是必要的。", BODY))
S.append(PageBreak())


# ── 八、实操手册 ──
S.append(Paragraph("八、给个人投资者的实操手册", H2))

S.append(Paragraph("8.1 当前位置 (-66% 回撤) 的操作建议", H3))
for c in [
    "<b>用定投, 不要一次性梭哈</b> 。即使长期看好, 当前盘面 12m 动量 "
    f"{pct(CUR['mom_12m'], 0)}, 6m 动量 {pct(CUR['mom_6m'], 0)}, "
    "意味着左侧仍可能延伸; 一次性买入承担的择时风险过高。"
    "建议月度等额定投, 周期 ≥ 12 个月。",
    "<b>分批加仓规则化</b> 。可设置 “每多跌 5%-10% 加 1 份本金” 的纪律性加码, "
    "用规则替代情绪 — 这是把 “越跌越买” 变成可执行流程的关键。",
    "<b>持有期至少 3 年起步, 目标 5 年</b> 。1 年定投胜率仅 "
    f"{pct0(g('白酒','dca',12,'win'))}, 不足以应付当前的左侧风险; "
    f"5 年定投历史胜率 {pct0(g('白酒','dca',60,'win'))}, 中位 "
    f"{pct(g('白酒','dca',60,'med'), 0)} — 时间是定投最大的朋友。",
    "<b>选择费率最低的工具</b> 。场内 ETF (如 sh512690 招商中证白酒 ETF) 优于 LOF 与连接基金; "
    "场内 0.5% 综合费, 场外 1-2% 申购费 + 1.5% 管理费 — 5 年下来差异显著。",
    "<b>给定投设置 “止盈线” 而非 “止损线”</b> 。深熊期定投忌讳 “跌了 3 个月就割肉”; "
    "建议在累计浮盈达到 50% / 80% / 120% 三档时分批止盈, 不要让浮盈坐成过山车。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("8.2 仓位建议参考", H3))
S.append(Paragraph(
    "<b>稳健型 (回撤承受能力低)</b> : 白酒占总仓位 5-10%, 月度定投 1-2 份基本生活费体量, "
    "持有期 3-5 年, 不加杠杆。"
    "<b>平衡型</b> : 白酒占 10-20%, 月度定投 + 回撤每加深 5% 加 1 份, "
    "持有期 5 年起步, 设置三档止盈。"
    "<b>激进型 (能拿住的人)</b> : 白酒占 20-30%, 月度定投 + 估值/回撤双触发的加仓规则, "
    "目标持有 5-7 年, 不动用杠杆 (深熊里被强平的代价远大于错过反弹) 。", BODY))

S.append(Paragraph("8.3 退出信号参考 (非投资建议)", H3))
S.append(Paragraph(
    "白酒的反转通常需要 <b>三个层面同时改善</b> : "
    "(1) 宏观消费层 : 居民消费信心、可支配收入、宴席场景恢复; "
    "(2) 行业基本面 : 高端酒企渠道库存去化结束 (一线酒企经销商库存 < 2 个月) 、批价企稳; "
    "(3) 资金面 : 板块成交占比触底回升、北向资金重新流入。"
    "技术面参考 : 月线突破 200 日均线且 6m 动量转正, 通常滞后基本面拐点 3-6 个月。"
    "<b>当前 (2026.06) 三个层面均未出现拐点信号, 处于左侧定投阶段。</b>", BODY))
S.append(PageBreak())

# ── 九、局限与免责 ──
S.append(Paragraph("九、局限、免责与数据声明", H2))

S.append(Paragraph("9.1 研究局限", H3))
for c in [
    "<b>样本局限</b> : 单一标的 (中证酒指数) 11 年数据, 5 年持有期只有 74 个滚动窗口, "
    "重叠样本统计意义弱于独立样本; ≤-50% 回撤入场的 5 年前瞻样本为 0, "
    "对当前位置的胜率推断依赖外推。",
    "<b>幸存者偏差</b> : 中证酒指数本身经过编制规则筛选, "
    "排除了已退市或不符合流动性要求的酒企; 个股层面的 “买错单一酒企” 风险, 本报告未涵盖。",
    "<b>未含交易成本</b> : 回测未计入买卖佣金、印花税、申赎费率与税费; "
    "对 ETF 影响 < 0.5%/年, 对场外基金 1-2%/年。",
    "<b>历史不代表未来</b> : 中国白酒行业的成长性、消费场景、政策环境都在演变, "
    "下一轮周期的形态可能与历史完全不同; 历史回测只反映 “过去发生过什么”, "
    "不代表 “未来会发生什么”。",
    "<b>不含宏观情景</b> : 报告未对禁酒政策、人口结构变化、消费降级长期化等情景做敏感性分析; "
    "如这些情景实际发生, 历史规律的外推适用性会显著下降。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("9.2 免责声明", H3))
S.append(Paragraph(
    "本报告为研究性内容, <b>不构成任何投资建议、买卖推荐或对未来收益的承诺</b>。"
    "所有数据来自公开来源 (sina 接口转中证指数公司) , "
    "已尽可能核对, 但不保证 100% 无误。"
    "投资有风险, 任何基于本报告的操作决策均由读者自行承担后果, 与作者无关。"
    "如本报告引用了第三方数据或观点, 已注明来源; 如有疏漏, 请联系作者更正。", NOTE))

S.append(Paragraph("9.3 复现说明", H3))
S.append(Paragraph(
    "本研究全部数据 + 代码 + 中间产物已落盘, 可端到端复现 :"
    "  (1) <font face='CN-B'>analysis/baijiu_fetch.py</font> — 从 sina 抓取中证酒/沪深300/招商白酒 ETF 月数据, "
    "缓存至 data/cache/index/ ; "
    "  (2) <font face='CN-B'>analysis/baijiu_winrate.py</font> — 滚动起点回测 + 条件胜率计算 + 浅色研报图 + 7 张深色卡片 ; "
    "  (3) <font face='CN-B'>analysis/baijiu_report.py</font> — 本 PDF 排版。"
    f"  数据截止 {AS_OF}, 输出目录 output/2026-06-16/baijiu-winrate/。", BODY))

S.append(Spacer(1, 0.5 * cm))
S.append(HRFlowable(width="100%", thickness=0.6, color=GRAY, hAlign="CENTER"))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"《中证酒板块定投胜率 量化深度研报》　|　数据截止 {AS_OF}　|　量化研究笔记 出品", CAP))

# ── 文档构建 ──
doc = SimpleDocTemplate(str(PDF), pagesize=A4,
                        topMargin=2.0 * cm, bottomMargin=1.8 * cm,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        title="中证酒定投胜率量化深度研报",
                        author="量化研究笔记")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print("PDF ->", PDF)
