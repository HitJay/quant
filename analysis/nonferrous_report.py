"""
有色金属(周期之王)长线胜率 + 周期位置 — 付费深度研报 (reportlab, 中文)
================================================================
读取 nonferrous_winrate.py 的 summary.json + figures/, 排版为付费研报 PDF。

核心诚实叙事:
  现在不是抄底位 —— 有色处历史 99 分位高位(近12月 +90%), 历史上买在 ≥90 分位,
  5 年一次性胜率仅 18% / 中位 -36%; 真正的钱在低位(≤30分位)赚(5y 中位 +350%)。

Usage:
    conda activate research
    python analysis/nonferrous_winrate.py
    python analysis/nonferrous_report.py
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

ROOT = Path("./output/2026-06-17/nonferrous-metals")
FIGS = ROOT / "figures"
CARDS = ROOT / "cards"
PDF = ROOT / "有色金属周期评估_量化深度研报.pdf"
S_ = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

# ── 配色 ──
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
RISK = S_["risk"]
CUR = S_["current"]
COND = S_["conditional_winrate"]
PCOND = S_["percentile_winrate"]
CUR_BUCKET = S_["current_pctile_bucket"]
N_MONTHS = S_["n_months"]
N_YEARS = S_["n_years"]

HS = [(12, "1年"), (24, "2年"), (36, "3年"), (60, "5年")]
PB = [("low", "低位 ≤30分位"), ("mid", "中位 30-70分位"),
      ("high", "高位 70-90分位"), ("vhigh", "极高位 ≥90分位")]


def g(group, method, H, key):
    return R[group][method][str(H)][key]


def cg(thr_key, mh_key, key):
    v = COND[thr_key][mh_key][key]
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def pg(pkey, method, H, key):
    v = PCOND[pkey][f"{method}_{H}m"][key]
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
            st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fdeaea")))
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
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "有色金属周期评估 · 量化深度研报")
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
S.append(Paragraph("有色金属·周期之王，现在能追吗？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"申万有色金属指数 {N_YEARS:.0f} 年 · {N_MONTHS} 个月度起点 · 滚动回测 · "
    "分位/回撤条件胜率 · 当前周期位置评估", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))

# 三个核心数字 (诚实: 当前高位赔率差)
ck_data = [["当前价格分位", "近12月动量", "历史 ≥90分位入场\n5年一次性胜率"],
           [pct0(CUR["price_pctile"]),
            pct(CUR["mom_12m"], 0),
            pct0(pg("vhigh", "lump", 60, "win"))]]
ct = Table(ck_data, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"),
    ("FONTSIZE", (0, 0), (-1, 0), 10.5),
    ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("LEADING", (0, 0), (-1, 0), 14),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"),
    ("FONTSIZE", (0, 1), (-1, 1), 22),
    ("TEXTCOLOR", (0, 1), (0, 1), RED),
    ("TEXTCOLOR", (1, 1), (1, 1), ORANGE),
    ("TEXTCOLOR", (2, 1), (2, 1), RED),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 1), (-1, 1), 6),
    ("BOTTOMPADDING", (0, 1), (-1, 1), 6),
]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph(
    f"标的：申万有色金属指数(801050) · 数据 {N_MONTHS} 个月(1999.12~2026.06) "
    "· 含 2006-07 超级周期 / 2008 金融危机 / 2015 杠杆牛熊 / 2021 铜锂大牛 · 全程可复现", SUB))
S.append(Spacer(1, 2.2 * cm))
S.append(Paragraph(
    "出品：量化研究笔记　|　作者：靳秋野　|　数据源 akshare·申万/sina (开源)　|　数据截止 " + AS_OF, CAP))
S.append(PageBreak())

# ── 摘要与核心结论 ──
S.append(Paragraph("摘要与核心结论", H2))
S.append(Paragraph(
    f"有色金属是 A 股最典型的强周期板块——“周期之王”。它从 2026 年 1 月的高点 "
    f"{CUR['peak_price']:.0f} 点回落至当前 {CUR['price']:.0f} 点, 回撤仅 {pct(CUR['drawdown'],0)}, "
    f"但价格仍处于 {N_YEARS:.0f} 年历史的第 {pct0(CUR['price_pctile'])} 分位、近 12 个月暴涨 "
    f"{pct(CUR['mom_12m'],0)}——这是“山顶”而非“山脚”。本报告用 {N_MONTHS} 个月的申万有色月度数据, "
    "对“每月入场一次” 的一次性(lump-sum) 与定投(DCA) 做滚动起点回测, 并按入场时的"
    "<b>价格分位</b>与<b>回撤深度</b>做条件分组, 给出可复现的胜率与收益分布, "
    "回答最关心的一个问题：<b>现在这个位置, 还能追吗？</b>", BODY))

concl = [
    f"<b>现在是“极高位”, 历史赔率很差。</b> 当前价格处历史 {pct0(CUR['price_pctile'])} 分位。"
    f"历史上买在 ≥90 分位(极高位)、一次性持有 5 年, 胜率仅 {pct0(pg('vhigh','lump',60,'win'))}"
    f"(n={pg('vhigh','lump',60,'n')}), 中位收益 {pct(pg('vhigh','lump',60,'med'),0)}; "
    f"持有 3 年更差, 胜率 {pct0(pg('vhigh','lump',36,'win'))}、中位 {pct(pg('vhigh','lump',36,'med'),0)}。"
    "周期品在高位买入, 大概率要被套数年。",
    f"<b>真正的钱在低位赚。</b> 历史上买在 ≤30 分位(低位)、一次性持有 5 年, 胜率 "
    f"{pct0(pg('low','lump',60,'win'))}、中位 {pct(pg('low','lump',60,'med'),0)}; "
    f"中位(30-70分位)买入 5 年中位 {pct(pg('mid','lump',60,'med'),0)}。"
    "分位越低、未来赔率越高——这正是周期股“贵就是贵、便宜就是便宜”的铁律。",
    f"<b>时间能提高胜率, 但救不了高位。</b> 任意时点入场, 有色 1 年定投胜率仅 "
    f"{pct0(g('有色','dca',12,'win'))}, 5 年升至 {pct0(g('有色','dca',60,'win'))}; "
    "但“拉长持有”的统计是对所有起点的平均——若起点恰在极高位, 时间也难以挽回(见上)。",
    f"<b>高波动是有色的“原罪”。</b> 自 {RISK['common_start'][:4]} 年以来, 有色年化波动 "
    f"{pct0(RISK['有色']['ann_vol'])}、最大回撤 {pct0(abs(RISK['有色']['max_dd']))}, "
    f"显著高于沪深300({pct0(RISK['沪深300']['ann_vol'])} / {pct0(abs(RISK['沪深300']['max_dd']))}); "
    f"而 5 年中位收益(一次性 {pct(g('有色','lump',60,'med'),0)})并不比沪深300"
    f"({pct(g('沪深300','lump',60,'med'),0)})更高——高弹性未必带来更高的长期中位回报。",
    "<b>一句话结论。</b> 当前位置对“想上车的人”历史上是<b>偏不利</b>的入场区间："
    "(1) 已持有者——趋势虽在(站上 200 日线)但位置极端, 应控制仓位、设跌破均线的止盈线、分批兑现; "
    "(2) 想买入者——别在 99 分位追高, 等价格回到中低分位或出现深度回撤(≤-30%)再分批定投。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "* 结论基于历史回测、重叠样本统计反映条件期望, 不代表未来; 趋势可能再创新高(动量), "
    "也可能高位崩跌, 本报告只讲历史赔率, 不预测点位 (见局限)。", NOTE))
S.append(PageBreak())

# ── 一、背景 ──
S.append(Paragraph("一、为什么现在重新评估有色金属", H2))
S.append(Paragraph(
    "有色金属(铜、铝、锌、锂、稀土、贵金属等)是典型的强周期板块, 股价同时受三条线驱动："
    "全球商品价格周期(供需+库存)、美元与实际利率(定价货币与机会成本)、以及国内地产基建与"
    "新能源需求(终端消费)。正因为它把宏观、商品、汇率三重周期叠加在一起, "
    "波动天然巨大, 历来是“周期之王”。", BODY))
S.append(Paragraph(
    f"过去一年, 在全球再通胀预期、铜/铝供给约束与新能源(铜锂)需求的共振下, "
    f"申万有色指数近 12 个月上涨 {pct(CUR['mom_12m'],0)}, 一度创出 {CUR['peak_price']:.0f} 点的高点, "
    f"目前回落至 {CUR['price']:.0f} 点(回撤 {pct(CUR['drawdown'],0)})。"
    "在社交媒体上, “有色还能不能上车”“是不是牛市起点”成了高频问题。", BODY))
S.append(Paragraph(
    "本报告不预测铜价或某只票的点位, 而是回答一个更底层、更可复现的问题："
    "<b>历史上当有色处于不同位置(分位/回撤)时, 用定投或一次性入场, 持有 1/2/3/5 年的胜率与"
    "收益分布到底如何？当前 99 分位的位置, 对“现在追入”意味着什么？</b>", BODY))
S.append(PageBreak())

# ── 二、方法与数据 ──
S.append(Paragraph("二、研究方法与数据", H2))
S.append(Paragraph("2.1 数据来源与样本", H3))
S.append(Paragraph(
    f"<b>主代理</b>：申万一级行业指数·有色金属(801050), 月末收盘价, "
    f"覆盖 1999 年 12 月至 2026 年 6 月, 共 {N_MONTHS} 个月观测、约 {N_YEARS:.0f} 年。"
    "选它是因为它是 A 股<b>跨度最长</b>的有色序列, 完整涵盖 2006-2007 商品超级周期、"
    "2008 金融危机崩盘、2015 杠杆牛熊与 2020-2021 新能源/铜锂大牛, 周期样本相对完整。", BODY))
S.append(Paragraph(
    "<b>对比基准</b>：沪深300 指数(sh000300), 同期月末收盘价, 用于把有色的“高波动代价”"
    "与“周期回报”同宽基做对照。", BODY))
S.append(Paragraph(
    "<b>可投工具</b>：有色金属ETF(159866, 2021 年上市)为当前主流场内标的; "
    "因其历史不足 5 年, 本报告的长周期统计以申万指数为准, ETF 仅作当下交易参考。", BODY))

S.append(Paragraph("2.2 回测方法", H3))
for c in [
    "<b>口径统一</b>：月末价格序列, 滚动起点。",
    "<b>一次性(LUMP)</b>：某起点月一次性买入, 持有 H 月后估值, 收益 = 期末/起点 − 1。",
    "<b>定投(DCA)</b>：从起点月起每月末等额买入 1 份共 H 份, 第 H 月末估值, 收益 = 总市值/总投入 − 1。",
    "<b>滚动起点</b>：对每个可行起点月、每个持有期 H∈{1,2,3,5} 年都算一遍, 合并统计"
    "胜率、中位、P10/P90、最差/最好与不同深度亏损概率。",
    "<b>分位条件胜率(本报告核心)</b>：在每个起点月, 用<b>截至当时的全部历史</b>计算价格"
    "“扩张分位”(expanding percentile, 只用过去信息、无未来函数), 按 ≤30 / 30-70 / 70-90 / "
    "≥90 分位分四档, 分别统计后续前瞻收益——直接回答“买在山顶 vs 山脚”。",
    "<b>回撤条件胜率</b>：把入场限定为该月末回撤 ≤-30% / -40% / -50% / -60%, 统计前瞻收益。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("2.3 关于本研究的诚实说明", H3))
for c in [
    "<b>(1) 单标的、重叠样本。</b> 仅跑一个指数的滚动回测, 滚动起点之间有重叠, "
    "同段历史被多次计入, 因此置信区间比独立样本更宽; 胜率应理解为“历史条件期望”, 非未来保证。",
    "<b>(2) 分位分档样本不均。</b> 极高位(≥90分位)5 年前瞻样本 "
    f"n={pg('vhigh','lump',60,'n')}, 低位(≤30分位)n={pg('low','lump',60,'n')}; "
    "低位样本多集中在 2002-2005 与 2008、2014 等少数深熊, 其“+350% 中位”有显著的"
    "“从大坑反弹”幸存者色彩, 不应线性外推为“随时买低位都能翻几倍”。",
    "<b>(3) 指数 ≠ 可投。</b> 申万指数不可直接交易, 真实 ETF 有跟踪误差、费率与流动性; "
    "且行业成分随时间漂移(早年以铜铝为主, 近年锂/稀土权重上升)。",
    "<b>(4) 不含交易成本</b>, 未计佣金/印花税/冲击成本。",
]:
    S.append(Paragraph(c, NOTE))
S.append(PageBreak())

# ── 三、主结论① 持有期与胜率 ──
S.append(Paragraph(
    f"三、主结论①：时间提高胜率, 5 年定投胜率 {pct0(g('有色','dca',60,'win'))}", H2))
S.append(img("fig_winrate.png", 16))
S.append(Paragraph("图1　申万有色不同持有年限的赚钱概率(胜率)：一次性 vs 定投", CAP))

t1 = [["持有期", "定投胜率", "定投样本", "一次性胜率", "一次性样本", "一次性中位"]]
for H, lab in HS:
    t1.append([lab,
               pct0(g("有色", "dca", H, "win")), str(g("有色", "dca", H, "n")),
               pct0(g("有色", "lump", H, "win")), str(g("有色", "lump", H, "n")),
               pct(g("有色", "lump", H, "med"), 0)])
S.append(table(t1, [2.4 * cm, 2.7 * cm, 2.4 * cm, 2.9 * cm, 2.4 * cm, 2.6 * cm], hl=[4]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>解读</b>：持有 1 年, 有色一次性、定投胜率都只有约 {pct0(g('有色','lump',12,'win'))}—"
    "几乎是抛硬币, 这正是“追涨杀跌、来回打脸”最常发生的区间。"
    f"有意思的是持有 2 年, 一次性胜率反而降到 {pct0(g('有色','lump',24,'win'))}、中位 "
    f"{pct(g('有色','lump',24,'med'),0)}——周期股的“两年魔咒”：很多时候第二年正好撞上回调。"
    f"持有期拉到 5 年, 一次性胜率升到 {pct0(g('有色','lump',60,'win'))}、定投 "
    f"{pct0(g('有色','dca',60,'win'))}。<b>时间确实提高胜率, 但这是对“所有起点”的平均;"
    "下一节会看到, 起点的位置(分位)才是决定性变量。</b>", BODY))
S.append(PageBreak())

# ── 四、主结论② 高波动的代价 ──
S.append(Paragraph("四、主结论②：高波动的代价与回报", H2))
S.append(img("fig_riskreturn.png", 15))
S.append(Paragraph(
    f"图2　有色 vs 沪深300：年化收益 / 年化波动 / 最大回撤(自 {RISK['common_start'][:4]} 年)", CAP))

t2 = [["指标", "有色金属", "沪深300"],
      ["年化收益", pct(RISK["有色"]["ann_ret"], 1), pct(RISK["沪深300"]["ann_ret"], 1)],
      ["年化波动", pct0(RISK["有色"]["ann_vol"]), pct0(RISK["沪深300"]["ann_vol"])],
      ["最大回撤", pct0(RISK["有色"]["max_dd"]), pct0(RISK["沪深300"]["max_dd"])],
      ["5年一次性中位", pct(g("有色", "lump", 60, "med"), 0), pct(g("沪深300", "lump", 60, "med"), 0)],
      ["5年一次性P10(差)", pct(g("有色", "lump", 60, "p10"), 0), pct(g("沪深300", "lump", 60, "p10"), 0)]]
S.append(table(t2, [5.0 * cm, 4.2 * cm, 4.2 * cm], hl=[2, 3]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>解读</b>：有色的年化波动({pct0(RISK['有色']['ann_vol'])})与最大回撤"
    f"({pct0(abs(RISK['有色']['max_dd']))})都远高于沪深300, 这是“周期之王”的标价。"
    f"但代价并没有换来更高的长期中位回报——5 年一次性中位收益, 有色 "
    f"{pct(g('有色','lump',60,'med'),0)} 甚至略低于沪深300 {pct(g('沪深300','lump',60,'med'),0)}; "
    f"而尾部更深(P10 {pct(g('有色','lump',60,'p10'),0)} vs {pct(g('沪深300','lump',60,'p10'),0)})。", BODY))
S.append(Paragraph(
    "这说明有色的超额收益<b>不是“长期持有”就能拿到的, 而是高度依赖择时(买在周期低位)</b>——"
    "把它当“躺赢宽基”长期满仓, 历史上性价比并不优于沪深300。", QUOTE))
S.append(PageBreak())

# ── 五、主结论③ 买在山顶 vs 山脚 (核心) ──
S.append(Paragraph("五、主结论③：买在山顶 vs 山脚——位置决定赔率", H2))
S.append(img("fig_percentile.png", 16))
S.append(Paragraph("图3　按入场时的“历史价格分位”分档, 一次性持有 3/5 年的中位收益(扩张分位口径)", CAP))

t3 = [["入场分位", "样本n", "3年胜率", "3年中位", "5年胜率", "5年中位"]]
for k, lab in PB:
    t3.append([lab, str(pg(k, "lump", 60, "n")),
               pct0(pg(k, "lump", 36, "win")), pct(pg(k, "lump", 36, "med"), 0),
               pct0(pg(k, "lump", 60, "win")), pct(pg(k, "lump", 60, "med"), 0)])
S.append(table(t3, [4.0 * cm, 1.8 * cm, 2.2 * cm, 2.4 * cm, 2.2 * cm, 2.4 * cm], hl=[4]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>这是全篇最重要的一张表。</b> 入场时的历史分位, 几乎单调地决定了未来 3-5 年的赔率："
    f"买在低位(≤30分位), 5 年胜率 {pct0(pg('low','lump',60,'win'))}、中位 "
    f"{pct(pg('low','lump',60,'med'),0)}; 而买在极高位(≥90分位), 5 年胜率骤降到 "
    f"{pct0(pg('vhigh','lump',60,'win'))}、中位 {pct(pg('vhigh','lump',60,'med'),0)}, "
    f"3 年更是只有 {pct0(pg('vhigh','lump',36,'win'))} 胜率、中位 {pct(pg('vhigh','lump',36,'med'),0)}。", BODY))
S.append(Paragraph(
    f"<b>当前价格分位 {pct0(CUR['price_pctile'])}, 正落在“极高位 ≥90 分位”这一档。</b> "
    "也就是说, 现在追入有色, 在历史上对应的是<b>最差的那一档赔率</b>——多数情形下 3-5 年不赚钱。"
    "这并不否认趋势仍可能延续(动量是真实的), 但它清楚地告诉我们：<b>现在的位置, 安全垫极薄。</b>", BODY))
S.append(Paragraph(
    "需要诚实补充：低位档(≤30分位)“+350% 中位”带有“从历史大坑反弹”的幸存者色彩, "
    "样本集中在少数深熊年份, 不应线性理解为“买低位必翻几倍”; 但<b>“高位赔率显著差于低位”这一"
    "方向性结论, 在四档之间单调、稳健。</b>", NOTE))
S.append(PageBreak())

# ── 六、当前位置 ──
S.append(Paragraph("六、当前位置：99 分位的“山顶”长什么样", H2))
S.append(img("fig_drawdown.png", 16))
S.append(Paragraph("图4　申万有色指数长期净值(对数)与回撤曲线, 橙色虚线为当前回撤", CAP))

t4 = [["指标", "数值", "含义"],
      ["价格历史分位", pct0(CUR["price_pctile"]), "极高位, 估值/价格已透支"],
      ["当前回撤", pct(CUR["drawdown"], 0), "距 1 月高点仅小幅回落"],
      ["距 200 日均线", pct(CUR["vs_ma200"], 0), "仍在均线上方, 右侧趋势未破"],
      ["近 6 月动量", pct(CUR["mom_6m"], 0), "中期仍强"],
      ["近 12 月动量", pct(CUR["mom_12m"], 0), "涨幅巨大, 过热"]]
S.append(table(t4, [4.0 * cm, 3.2 * cm, 6.6 * cm]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "<b>四个信号合起来看：</b>估值/位置——<font color='#dc2626'>警惕</font>(99 分位极高); "
    "趋势/均线——<font color='#16a34a'>尚好</font>(站上 200 日线); "
    "动量——<font color='#dc2626'>过热</font>(近 12 月 +90%, 易剧烈回撤); "
    "历史赔率——<font color='#dc2626'>警惕</font>(同位置 5 年胜率仅 18%)。", BODY))
S.append(Paragraph(
    "<b>结论：趋势还在, 但位置极端 → 这是“追涨”而非“抄底”。</b> "
    "对趋势交易者, 可顺势但必须带紧止损(跌破均线即离场); "
    "对价值/周期投资者, 这是减仓兑现、而非加仓建仓的区域。", QUOTE))
S.append(PageBreak())

# ── 七、操作建议 ──
S.append(Paragraph("七、把胜率翻译成动作", H2))
S.append(Paragraph("7.1 如果你已经持有", H3))
for c in [
    "趋势虽在但位置极端：设“跌破 200 日线 / 月线”的纪律止盈线, 触发即分批兑现。",
    "分批兑现利润, 不在 99 分位满仓“等反转再创新高”——周期顶部的回撤往往又快又深。",
    "若坚持持有, 至少把仓位降到“能扛 -50% 回撤而不影响生活”的水平。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Paragraph("7.2 如果你想上车", H3))
for c in [
    f"别在极高位追高：历史同位置 5 年一次性胜率仅 {pct0(pg('vhigh','lump',60,'win'))}、中位 "
    f"{pct(pg('vhigh','lump',60,'med'),0)}。",
    f"等价格回到中低分位(≤30-50 分位)或出现深度回撤(≤-30%)再分批定投——"
    f"历史上回撤 ≤-30% 入场、5 年定投胜率 {pct0(cg('dd30','dca_60m','win'))}、中位 "
    f"{pct(cg('dd30','dca_60m','med'),0)}。",
    "用“定投 + 分位/回撤触发”而非“一次性梭哈”：把择时风险摊到时间轴上, 压制随机买点的伤害。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Paragraph("7.3 仓位框架(示意, 非建议)", H3))
t5 = [["价格分位", "历史5年赔率", "建议姿态"],
      ["≤30 分位(低位)", f"胜率{pct0(pg('low','lump',60,'win'))} / 中位{pct(pg('low','lump',60,'med'),0)}", "分批定投, 可逐步加大"],
      ["30-70 分位(中位)", f"胜率{pct0(pg('mid','lump',60,'win'))} / 中位{pct(pg('mid','lump',60,'med'),0)}", "常规定投, 标配仓位"],
      ["70-90 分位(高位)", f"胜率{pct0(pg('high','lump',60,'win'))} / 中位{pct(pg('high','lump',60,'med'),0)}", "停止加仓, 持有观察"],
      ["≥90 分位(极高位·现在)", f"胜率{pct0(pg('vhigh','lump',60,'win'))} / 中位{pct(pg('vhigh','lump',60,'med'),0)}", "减仓/止盈, 不新建仓"]]
S.append(table(t5, [4.6 * cm, 5.2 * cm, 4.0 * cm], hl=[4]))
S.append(PageBreak())

# ── 八、局限与风险 ──
S.append(Paragraph("八、局限、风险与免责声明", H2))
for c in [
    "<b>历史不代表未来。</b> 所有胜率均来自历史重叠样本的条件统计, 反映条件期望而非未来保证; "
    "本轮再通胀/新能源需求的宏观背景与历史并不完全可比。",
    "<b>分位是相对、不是绝对。</b> “极高位”指相对自身历史的价格分位, 不等于基本面一定见顶; "
    "若有色进入新的“超级周期”, 价格中枢可能系统性上移, 历史分位会被改写。",
    "<b>趋势可能再创新高。</b> 动量是真实存在的, 高位之后仍可能继续上涨一段; 本报告只讲"
    "“历史赔率/期望”, 不预测点位与拐点, 也不构成卖出/买入的择时信号。",
    "<b>指数 ≠ 可投资产。</b> 申万有色指数不可直接交易, 成分随时间漂移; 实际 ETF 有费率、"
    "跟踪误差与流动性差异。",
    "<b>样本与成本。</b> 单标的、重叠样本, 极端分档样本量有限; 回测未计交易成本与税费。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    "<b>免责声明</b>：本报告为量化研究与科普, 所有数据来自公开来源, 仅供个人学习参考, "
    "不构成任何投资建议或买卖要约。市场有风险, 投资需谨慎。据此操作, 盈亏自负。", NOTE))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"数据截止 {AS_OF} · 申万有色金属指数(801050) · {N_MONTHS} 个月度起点 · "
    "方法与代码可复现 · 出品：量化研究笔记 · 作者：靳秋野", CAP))


# ════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(str(PDF), pagesize=A4,
                        topMargin=2.0 * cm, bottomMargin=1.7 * cm,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        title="有色金属周期评估·量化深度研报", author="靳秋野")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print(f"✓ PDF 已生成: {PDF}")
print(f"  页数约 {len(S)} flowables")
