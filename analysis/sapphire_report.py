"""
蓝宝石概念股池长线胜率 + 题材周期位置 — 付费深度研报 (reportlab, 中文)
================================================================
读取 sapphire_winrate.py 的 summary.json + figures/, 排版为付费研报 PDF。

核心诚实叙事:
  现在不是抄底位 —— 蓝宝石概念股池处 9.2 年历史 100 分位创新高(近12月 +154%),
  历史上买在 ≥90 分位、一次性持有 3 年, 胜率仅 53% / 中位 +4%;
  真正的钱在低位(≤30分位)赚(3y 中位 +188%); 5 年数据全部正收益是幸存者偏差不展示。

Usage:
    conda activate research
    python analysis/sapphire_winrate.py
    python analysis/sapphire_report.py
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

ROOT = Path("./output/2026-06-18/sapphire")
FIGS = ROOT / "figures"
CARDS = ROOT / "cards"
PDF = ROOT / "蓝宝石概念评估_量化深度研报.pdf"
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

# 蓝宝石主信号是 3y, 不展示 5y (起点全在 2017-2021 早期, 100% 是幸存者偏差)
HS = [(12, "1年"), (24, "2年"), (36, "3年")]
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
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "蓝宝石概念评估 · 量化深度研报")
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
S.append(Paragraph("蓝宝石概念·题材龙头，现在能追吗？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"7 只龙头等权指数 · {N_YEARS:.1f} 年 · {N_MONTHS} 个月度起点 · 滚动回测 · "
    "分位条件胜率 · 当前题材位置评估", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))

# 三个核心数字 (诚实: 当前历史最高位赔率差)
ck_data = [["当前价格分位", "近12月动量", "历史 ≥90分位入场\n3年一次性胜率"],
           [pct0(CUR["price_pctile"]),
            pct(CUR["mom_12m"], 0),
            pct0(pg("vhigh", "lump", 36, "win"))]]
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
    "标的: 7 只蓝宝石概念龙头等权月度指数 (天通/露笑/奥瑞德/水晶光电/晶盛机电/国瓷材料/三超新材) · "
    f"数据 {N_MONTHS} 个月 (2017.04~2026.06) · "
    "覆盖 2017-19 长晶炉扩产 / 2020 LED 衰退 / 2021-22 Mini-Micro LED 牛 / 2023-25 沉寂 / 2026 AR 概念再起 · 全程可复现", SUB))
S.append(Spacer(1, 2.2 * cm))
S.append(Paragraph(
    "出品: 量化研究笔记　|　作者: 靳秋野　|　数据源 akshare (开源)　|　数据截止 " + AS_OF, CAP))
S.append(PageBreak())

# ── 摘要与核心结论 ──
S.append(Paragraph("摘要与核心结论", H2))
S.append(Paragraph(
    f"蓝宝石是 A 股最典型的“消费电子题材股”——单点应用催化、产能小、波动巨大、周期短促。"
    f"我们用 7 只 2017 年前已上市的蓝宝石概念龙头, 等权构造一支 {N_YEARS:.1f} 年的"
    f"长线题材指数 (覆盖 9.2 年题材潮起潮落)。它从 2024 年的低点震荡 9 年后, "
    f"在 2026 年 6 月一举创出 {N_YEARS:.1f} 年的<b>历史最高净值 {CUR['price']:.2f}</b> "
    f"(基期 1.00 起算, 涨幅 {pct(CUR['price']-1, 0)}), 价格分位 "
    f"<b>{pct0(CUR['price_pctile'])}</b>、近 12 个月暴涨 <b>{pct(CUR['mom_12m'], 0)}</b>"
    "——这是“山顶”而非“山脚”。本报告用滚动起点回测一次性(lump-sum) 与定投(DCA), "
    "并按入场时的<b>价格分位</b>做条件分组, 给出可复现的胜率与收益分布, "
    "回答最关心的一个问题: <b>现在这个位置, 还能追吗?</b>", BODY))

concl = [
    f"<b>现在是“极高位”, 历史赔率很差。</b> 当前价格处历史 {pct0(CUR['price_pctile'])} 分位 (创新高)。"
    f"历史上买在 ≥90 分位 (极高位)、一次性持有 <b>3 年</b>, 胜率仅 "
    f"{pct0(pg('vhigh','lump',36,'win'))} (n={pg('vhigh','lump',36,'n')}), "
    f"中位收益 {pct(pg('vhigh','lump',36,'med'),0)}; 持有 1 年更差, 胜率仅 "
    f"{pct0(pg('vhigh','lump',12,'win'))}、中位 {pct(pg('vhigh','lump',12,'med'),0)}; "
    f"持有 2 年胜率 {pct0(pg('vhigh','lump',24,'win'))}、中位 {pct(pg('vhigh','lump',24,'med'),0)}。"
    "题材股在高位买入, 大概率 1-2 年不赚钱。",

    f"<b>真正的钱在低位赚。</b> 历史上买在 ≤30 分位 (低位)、一次性持有 <b>3 年</b>, "
    f"胜率 {pct0(pg('low','lump',36,'win'))}、<b>中位 {pct(pg('low','lump',36,'med'),0)}</b>; "
    f"中位 (30-70 分位) 买入 3 年中位 {pct(pg('mid','lump',36,'med'),0)}。"
    f"低位 vs 极高位 3 年中位收益反差 {pct(pg('low','lump',36,'med')-pg('vhigh','lump',36,'med'),0)} "
    "——这正是题材股“贵就是贵、便宜就是便宜”的铁律。",

    f"<b>时间能提高胜率, 但救不了高位。</b> 任意时点入场, 蓝宝石 1 年定投胜率 "
    f"{pct0(g('蓝宝石','dca',12,'win'))}, 3 年升至 {pct0(g('蓝宝石','dca',36,'win'))}; "
    "但“拉长持有”的统计是对所有起点的平均——若起点恰在极高位, 时间也难以挽回 (见上)。",

    f"<b>高波动是题材股的“原罪”。</b> 自 {RISK['common_start'][:4]} 年以来, 蓝宝石年化波动 "
    f"{pct0(RISK['蓝宝石']['ann_vol'])}、最大回撤 {pct0(abs(RISK['蓝宝石']['max_dd']))}, "
    f"显著高于沪深300 ({pct0(RISK['沪深300']['ann_vol'])} / {pct0(abs(RISK['沪深300']['max_dd']))})。"
    "题材弹性的另一面是巨震, 想拿这份收益必须扛得住中途的腰斩。",

    "<b>一句话结论。</b> 当前位置对“想上车的人”历史上是<b>偏不利</b>的入场区间: "
    "(1) 已持有者——趋势虽在 (站上 200 日线) 但位置极端, 应控制仓位、设跌破均线的止盈线、分批兑现; "
    "(2) 想买入者——别在历史新高追高, 等价格回到中低分位再分批定投。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "* 结论基于 9.2 年历史回测 / 重叠样本统计反映条件期望, 不代表未来; 趋势可能再创新高 (动量), "
    "也可能高位回撤数年, 本报告只讲历史赔率, 不预测点位 (见局限)。", NOTE))
S.append(PageBreak())

# ── 一、背景 ──
S.append(Paragraph("一、为什么现在重新评估蓝宝石概念", H2))
S.append(Paragraph(
    "蓝宝石 (Al<sub>2</sub>O<sub>3</sub> 单晶) 是消费电子领域最典型的“题材股驱动型”小赛道, "
    "股价由<b>下游单点应用</b>驱动: 摄像头盖板、Apple Watch 表盖、Mini/MicroLED 衬底、"
    "AR/VR 显示组件。它和有色金属、半导体不同——既没有“商品超级周期”也没有“摩尔定律”, "
    "应用催化一来一波、催化褪去一沉数年, 是 A 股最典型的<b>题材股波动模式</b>。", BODY))
S.append(Paragraph(
    "过去一年, 在 Apple Vision Pro 二代发布预期、AR 眼镜放量预期与"
    "智能手机摄像头盖板需求复苏的共振下, 蓝宝石概念股池近 12 个月上涨 "
    f"{pct(CUR['mom_12m'], 0)}, 在 2026 年 6 月创出 9.2 年最高净值 {CUR['price']:.2f}。"
    "2026 年 6 月 18 日蓝宝石主力净流入超 11 亿、概念整体涨 4.17%、"
    "国瓷材料涨停。社交媒体上“蓝宝石还能不能上车”“是不是新一轮题材牛”成了高频问题。", BODY))
S.append(Paragraph(
    "本报告不预测苹果发布会的实际催化结果, 也不预测某只龙头的点位; 而是回答一个更底层、"
    "更可复现的问题: <b>历史上当蓝宝石概念处于不同位置 (分位) 时, 用定投或一次性入场, "
    "持有 1/2/3 年的胜率与收益分布到底如何? 当前 100 分位创新高的位置, "
    "对“现在追入”意味着什么?</b>", BODY))
S.append(PageBreak())

# ── 二、方法与数据 ──
S.append(Paragraph("二、研究方法与数据", H2))
S.append(Paragraph("2.1 数据来源与样本", H3))
S.append(Paragraph(
    "<b>主代理</b>: 7 只 2017 年 4 月前已上市的蓝宝石概念龙头, 等权构造月度题材指数 "
    "——天通股份(600330)、露笑科技(002617)、奥瑞德(600666)、水晶光电(002273)、"
    "晶盛机电(300316)、国瓷材料(300285)、三超新材(300554)。"
    "等权构造避免了单只龙头的特异性, 让指数更接近“题材股池总体表现”。"
    f"覆盖 2017 年 4 月至 2026 年 6 月, 共 {N_MONTHS} 个月观测 (约 {N_YEARS:.1f} 年), "
    "涵盖 2017-19 长晶炉扩产、2020 LED 衰退、2021-22 Mini/MicroLED 与苹果手表盖板、"
    "2023-25 沉寂、2026 AR 概念再起——题材完整潮起潮落。", BODY))
S.append(Paragraph(
    "<b>对比基准</b>: 沪深300 指数(sh000300), 同期月末收盘价, 用于把蓝宝石的"
    "“高波动代价”与“题材回报”同宽基做对照。", BODY))
S.append(Paragraph(
    "<b>可投工具</b>: 蓝宝石尚无单一标准 ETF, 实操可用 7 只龙头自构等权或筛选 1-2 只龙头建仓; "
    "本报告统计以等权指数为准, 不考虑单只标的的α/β 漂移。", BODY))

S.append(Paragraph("2.2 回测方法", H3))
for c in [
    "<b>口径统一</b>: 7 只龙头月末后复权价格, 等权日均化构造指数, 月末取值, 滚动起点。",
    "<b>一次性 (LUMP)</b>: 某起点月一次性买入, 持有 H 月后估值, 收益 = 期末/起点 − 1。",
    "<b>定投 (DCA)</b>: 从起点月起每月末等额买入 1 份共 H 份, 第 H 月末估值, 收益 = 总市值/总投入 − 1。",
    "<b>滚动起点</b>: 对每个可行起点月、每个持有期 H∈{1,2,3} 年都算一遍, 合并统计"
    "胜率、中位、P10/P90、最差/最好与不同深度亏损概率。",
    "<b>分位条件胜率 (本报告核心)</b>: 在每个起点月, 用<b>截至当时的全部历史</b>计算价格"
    "“扩张分位”(expanding percentile, 只用过去信息、无未来函数), 按 ≤30 / 30-70 / 70-90 / "
    "≥90 分位分四档, 分别统计后续前瞻收益——直接回答“买在山顶 vs 山脚”。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))

S.append(Paragraph("2.3 关于本研究的诚实说明", H3))
for c in [
    "<b>(1) 单标的池、重叠样本。</b> 仅跑一支 7 只龙头等权指数的滚动回测, 滚动起点之间有重叠, "
    "同段历史被多次计入, 因此置信区间比独立样本更宽; 胜率应理解为“历史条件期望”, 非未来保证。",

    f"<b>(2) 主信号选用 3 年, 不展示 5 年。</b> 极高位 (≥90分位) 5 年前瞻样本起点全部落在 "
    f"2017-2021 早期 (n=51), 这些起点全部回到了 2026 年的历史新高位置, 5 年胜率因此呈现 "
    f"100% 的“几何幻象”——这并不反映“极高位入场必赚”, 而是“2026 年指数恰好创新高”的样本偏置。"
    "因此本报告主胜率窗口选用 3 年 (n=30, 样本相对独立), 5 年数据仅在原始 CSV 中保留作为参考。",

    f"<b>(3) 分位分档样本不均。</b> 极高位 (≥90分位) 3 年前瞻样本 "
    f"n={pg('vhigh','lump',36,'n')}, 低位 (≤30分位) n={pg('low','lump',36,'n')}; "
    f"低位样本集中在 2017 年 (题材尚未启动) 与 2024 年 (深度沉寂期), "
    f"其“{pct(pg('low','lump',36,'med'),0)} 中位”有“从大坑反弹”幸存者色彩, "
    "不应线性外推为“随时买低位都能翻几倍”。",

    "<b>(4) 等权指数 ≠ 可投资产。</b> 等权构造指数无对应 ETF, 真实操作需自行调仓再平衡, "
    "存在调仓成本; 7 只龙头的成分相对稳定, 但若未来题材龙头切换 (如新增 AR 玻璃龙头), "
    "成分将不再代表题材整体。",

    "<b>(5) 不含交易成本</b>, 未计佣金/印花税/冲击成本; 月度调仓再平衡的真实摩擦在 0.3-0.5%/年量级。",
]:
    S.append(Paragraph(c, NOTE))
S.append(PageBreak())

# ── 三、主结论① 持有期与胜率 ──
S.append(Paragraph(
    f"三、主结论①: 时间能熨平题材吗? 持有 3 年定投胜率 {pct0(g('蓝宝石','dca',36,'win'))}", H2))
S.append(img("fig_winrate.png", 16))
S.append(Paragraph("图1　蓝宝石概念股池不同持有年限的赚钱概率(胜率): 一次性 vs 定投", CAP))

t1 = [["持有期", "定投胜率", "定投样本", "一次性胜率", "一次性样本", "一次性中位"]]
for H, lab in HS:
    t1.append([lab,
               pct0(g("蓝宝石", "dca", H, "win")), str(g("蓝宝石", "dca", H, "n")),
               pct0(g("蓝宝石", "lump", H, "win")), str(g("蓝宝石", "lump", H, "n")),
               pct(g("蓝宝石", "lump", H, "med"), 0)])
S.append(table(t1, [2.4 * cm, 2.7 * cm, 2.4 * cm, 2.9 * cm, 2.4 * cm, 2.6 * cm], hl=[3]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>解读</b>: 持有 1 年, 蓝宝石一次性胜率 {pct0(g('蓝宝石','lump',12,'win'))}、"
    f"定投 {pct0(g('蓝宝石','dca',12,'win'))}, 中位 {pct(g('蓝宝石','lump',12,'med'),0)} "
    "——题材股短线“摸彩票”特征明显, 节奏抓不准就割肉。"
    f"持有 2 年, 一次性胜率 {pct0(g('蓝宝石','lump',24,'win'))}、定投 "
    f"{pct0(g('蓝宝石','dca',24,'win'))}; 中位 {pct(g('蓝宝石','lump',24,'med'),0)} —— "
    "题材股最折磨人的“两年魔咒”: 第二年通常是上一波热度退潮、新催化未起的真空期。"
    f"持有 3 年, 一次性胜率升到 {pct0(g('蓝宝石','lump',36,'win'))}、定投 "
    f"{pct0(g('蓝宝石','dca',36,'win'))}, 中位 {pct(g('蓝宝石','lump',36,'med'),0)}。"
    "<b>时间确实提高胜率, 但这是对“所有起点”的平均; 下一节会看到, 起点的位置 (分位) "
    "才是决定性变量。</b>", BODY))
S.append(PageBreak())

# ── 四、主结论② 高波动的代价 ──
S.append(Paragraph("四、主结论②: 题材股的代价与回报", H2))
S.append(img("fig_riskreturn.png", 15))
S.append(Paragraph(
    f"图2　蓝宝石 vs 沪深300: 年化收益 / 年化波动 / 最大回撤 (自 {RISK['common_start'][:4]} 年)", CAP))

t2 = [["指标", "蓝宝石", "沪深300"],
      ["年化收益", pct(RISK["蓝宝石"]["ann_ret"], 1), pct(RISK["沪深300"]["ann_ret"], 1)],
      ["年化波动", pct0(RISK["蓝宝石"]["ann_vol"]), pct0(RISK["沪深300"]["ann_vol"])],
      ["最大回撤", pct0(RISK["蓝宝石"]["max_dd"]), pct0(RISK["沪深300"]["max_dd"])],
      ["3年一次性中位", pct(g("蓝宝石", "lump", 36, "med"), 0), pct(g("沪深300", "lump", 36, "med"), 0)],
      ["3年一次性P10(差)", pct(g("蓝宝石", "lump", 36, "p10"), 0), pct(g("沪深300", "lump", 36, "p10"), 0)]]
S.append(table(t2, [5.0 * cm, 4.2 * cm, 4.2 * cm], hl=[2, 3]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>解读</b>: 蓝宝石的年化波动 ({pct0(RISK['蓝宝石']['ann_vol'])}) 与最大回撤"
    f"({pct0(abs(RISK['蓝宝石']['max_dd']))}) 都显著高于沪深300, 这是“题材股”的标价。"
    f"年化收益方面, 蓝宝石 {pct0(RISK['蓝宝石']['ann_ret'])} 高于沪深300 "
    f"{pct0(RISK['沪深300']['ann_ret'])}; 3 年中位收益, 蓝宝石 "
    f"{pct(g('蓝宝石','lump',36,'med'),0)} 也高于沪深300 "
    f"{pct(g('沪深300','lump',36,'med'),0)}——题材股长期持有确实跑赢宽基。"
    f"但尾部更深 (P10 蓝宝石 {pct(g('蓝宝石','lump',36,'p10'),0)} vs 沪深300 "
    f"{pct(g('沪深300','lump',36,'p10'),0)}): 一旦运气不好买在题材高峰, "
    "亏损深度远超宽基。", BODY))
S.append(Paragraph(
    "<b>关键启示: 蓝宝石的超额收益不是“躺平拿到”的, 而是高度依赖择时——"
    "买在低位/中位, 题材股 3 年中位回报远超沪深300; 买在极高位, "
    "题材股的弹性反过来变成深坑。把它当“宽基替代”长期满仓, "
    "扛回撤的痛苦远大于多出来的那点α。</b>", QUOTE))
S.append(PageBreak())

# ── 五、主结论③ 买在山顶 vs 山脚 (核心) ──
S.append(Paragraph("五、主结论③: 买在山顶 vs 山脚——位置决定赔率", H2))
S.append(img("fig_percentile.png", 16))
S.append(Paragraph("图3　按入场时的“历史价格分位”分档, 一次性持有 1/2/3 年的胜率与中位收益(扩张分位口径)", CAP))

t3 = [["入场分位", "样本n", "1年胜率", "1年中位", "2年胜率", "2年中位", "3年胜率", "3年中位"]]
for k, lab in PB:
    t3.append([lab, str(pg(k, "lump", 36, "n")),
               pct0(pg(k, "lump", 12, "win")), pct(pg(k, "lump", 12, "med"), 0),
               pct0(pg(k, "lump", 24, "win")), pct(pg(k, "lump", 24, "med"), 0),
               pct0(pg(k, "lump", 36, "win")), pct(pg(k, "lump", 36, "med"), 0)])
S.append(table(t3, [3.0 * cm, 1.4 * cm, 1.7 * cm, 1.9 * cm, 1.7 * cm, 1.9 * cm, 1.7 * cm, 1.9 * cm],
               fs=8.8, hl=[4]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"<b>这是全篇最重要的一张表。</b> 入场时的历史分位, 几乎单调地决定了未来 1-3 年的赔率: "
    f"买在低位 (≤30分位), 3 年胜率 {pct0(pg('low','lump',36,'win'))}、"
    f"<b>中位 {pct(pg('low','lump',36,'med'),0)}</b>; 而买在极高位 (≥90分位), 3 年胜率骤降到 "
    f"{pct0(pg('vhigh','lump',36,'win'))}、<b>中位仅 {pct(pg('vhigh','lump',36,'med'),0)}</b>。"
    f"两者中位收益反差 <b>{pct(pg('low','lump',36,'med')-pg('vhigh','lump',36,'med'),0)}</b> "
    "——题材股的核心铁律: <b>位置 > 标的 > 时间</b>。", BODY))
S.append(Paragraph(
    f"<b>当前价格分位 {pct0(CUR['price_pctile'])} (创历史新高), "
    "正落在“极高位 ≥90 分位”这一档。</b> 也就是说, 现在追入蓝宝石概念, "
    "在历史上对应的是<b>最差的那一档赔率</b>——多数情形下 1-2 年不赚钱、3 年中位仅微利。"
    "这并不否认趋势仍可能延续 (动量是真实的), 但它清楚地告诉我们: <b>现在的位置, 安全垫极薄。</b>", BODY))
S.append(Paragraph(
    f"需要诚实补充: 低位档 (≤30分位)“{pct(pg('low','lump',36,'med'),0)} 中位”带有“从历史大坑反弹”的幸存者色彩, "
    "样本集中在 2017-2018 题材未启动期与 2023-2024 沉寂期, 不应线性理解为“买低位必翻几倍”; "
    "但<b>“高位赔率显著差于低位”这一方向性结论, 在四档之间单调、稳健。</b>", NOTE))
S.append(PageBreak())

# ── 六、当前位置 ──
S.append(Paragraph("六、当前位置: 100 分位的“山顶”长什么样", H2))
S.append(img("fig_drawdown.png", 16))
S.append(Paragraph("图4　蓝宝石等权指数长期净值(对数)与回撤曲线, 橙色虚线为当前回撤", CAP))

t4 = [["指标", "数值", "含义"],
      ["价格历史分位", pct0(CUR["price_pctile"]), "100 分位创新高, 价格已透支"],
      ["距 9.2 年高点", pct(CUR["drawdown"], 0), "正处于历史新高 (回撤 0%)"],
      ["距 200 日均线", pct(CUR["vs_ma200"], 0), "远在均线上方, 趋势强但有过热"],
      ["近 6 月动量", pct(CUR["mom_6m"], 0), "中期暴涨, 警惕回调"],
      ["近 12 月动量", pct(CUR["mom_12m"], 0), "12 个月翻 1.5 倍, 严重过热"]]
S.append(table(t4, [4.0 * cm, 3.2 * cm, 6.6 * cm]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "<b>四个信号合起来看: </b>"
    "估值/位置——<font color='#dc2626'>警惕</font> (100 分位创新高); "
    "趋势/均线——<font color='#16a34a'>尚好</font> (站上 200 日线); "
    f"动量——<font color='#dc2626'>过热</font> (近 12 月 {pct(CUR['mom_12m'],0)}, 易剧烈回撤); "
    f"历史赔率——<font color='#dc2626'>警惕</font> (同位置 3 年胜率仅 {pct0(pg('vhigh','lump',36,'win'))}、"
    f"中位 {pct(pg('vhigh','lump',36,'med'),0)})。", BODY))
S.append(Paragraph(
    "<b>结论: 趋势还在, 但位置极端 → 这是“追涨”而非“抄底”。</b> "
    "对趋势/题材交易者, 可顺势但必须带紧止损 (跌破均线/前低即离场); "
    "对偏长线的投资者, 这是分批兑现、而非加仓建仓的区域。"
    "题材股的特点是: 顶部回撤往往又快又深, 一波退潮可以让 12 个月涨幅在 3 个月内归零。", QUOTE))
S.append(PageBreak())

# ── 七、操作建议 ──
S.append(Paragraph("七、把胜率翻译成动作", H2))
S.append(Paragraph("7.1 如果你已经持有", H3))
for c in [
    "趋势虽在但位置极端: 设“跌破 200 日线 / 月线”的纪律止盈线, 触发即分批兑现。",
    f"分批兑现利润, 不在 100 分位满仓“等催化再创新高”——题材股顶部的回撤往往又快又深 "
    f"(历史最大回撤 {pct0(abs(RISK['蓝宝石']['max_dd']))})。",
    "若坚持持有, 至少把仓位降到“能扛 -50% 回撤而不影响生活”的水平; "
    "题材股的回撤幅度比宽基大 1.5-2 倍, 心态不稳的投资者应直接减仓。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Paragraph("7.2 如果你想上车", H3))
for c in [
    f"别在历史新高追高: 历史同位置 3 年一次性胜率仅 {pct0(pg('vhigh','lump',36,'win'))}、"
    f"中位 {pct(pg('vhigh','lump',36,'med'),0)}; 1 年胜率仅 {pct0(pg('vhigh','lump',12,'win'))}、"
    f"中位 {pct(pg('vhigh','lump',12,'med'),0)}。",
    f"等价格回到中低分位 (≤30-50 分位) 再分批定投——历史上买在 ≤30 分位、3 年定投胜率 "
    f"{pct0(pg('low','dca',36,'win'))}、中位 {pct(pg('low','dca',36,'med'),0)}。",
    "用“定投 + 分位触发”而非“一次性梭哈”: 把择时风险摊到时间轴上, 题材股短线情绪驱动剧烈, "
    "定投比一次性入场更扛波动。",
    "标的选择: 等权 7 只龙头自构组合, 或选估值/换手相对温和的 1-2 只 (避开短期妖股); "
    "蓝宝石尚无单一标准 ETF, 操作前需自行评估调仓成本。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Paragraph("7.3 仓位框架(示意, 非建议)", H3))
t5 = [["价格分位", "历史3年赔率", "建议姿态"],
      ["≤30 分位 (低位)",
       f"胜率 {pct0(pg('low','lump',36,'win'))} / 中位 {pct(pg('low','lump',36,'med'),0)}",
       "分批定投, 可逐步加大"],
      ["30-70 分位 (中位)",
       f"胜率 {pct0(pg('mid','lump',36,'win'))} / 中位 {pct(pg('mid','lump',36,'med'),0)}",
       "常规定投, 标配仓位"],
      ["70-90 分位 (高位)",
       f"胜率 {pct0(pg('high','lump',36,'win'))} / 中位 {pct(pg('high','lump',36,'med'),0)}",
       "停止加仓, 持有观察"],
      ["≥90 分位 (极高位·现在)",
       f"胜率 {pct0(pg('vhigh','lump',36,'win'))} / 中位 {pct(pg('vhigh','lump',36,'med'),0)}",
       "减仓/止盈, 不新建仓"]]
S.append(table(t5, [4.6 * cm, 5.8 * cm, 4.0 * cm], hl=[4]))
S.append(PageBreak())

# ── 八、局限与风险 ──
S.append(Paragraph("八、局限、风险与免责声明", H2))
for c in [
    "<b>历史不代表未来。</b> 所有胜率均来自 9.2 年历史重叠样本的条件统计, 反映条件期望而非未来保证; "
    "本轮 AR/Vision Pro 催化的宏观背景与 2017-2022 历次催化并不完全可比。",

    "<b>分位是相对、不是绝对。</b> “极高位”指相对自身 9.2 年历史的价格分位, 不等于基本面一定见顶; "
    "若蓝宝石进入新的“产能扩张超级周期” (如 AR 眼镜大规模量产), "
    "价格中枢可能系统性上移, 历史分位会被改写。",

    "<b>趋势可能再创新高。</b> 动量是真实存在的, 高位之后仍可能继续上涨一段; "
    "本报告只讲“历史赔率/期望”, 不预测点位与拐点, 也不构成卖出/买入的择时信号。",

    "<b>等权指数 ≠ 可投资产。</b> 等权构造指数无对应 ETF, 真实操作需自行调仓再平衡; "
    "若未来题材龙头切换 (如新增 AR 玻璃龙头), 7 只样本可能不再代表题材整体。",

    "<b>样本与成本。</b> 单标的池、重叠样本, 极端分档 3 年样本 n 仅 11-40, 置信区间较宽; "
    "回测未计交易成本与税费, 真实摩擦在 0.3-0.5%/年。",

    "<b>历史窗口偏短。</b> 9.2 年仅覆盖 2-3 个完整题材周期, 比有色金属 (26 年) 等成熟周期股的"
    "样本量小很多——这意味着单一极端事件 (如 2026 年的创新高) 对统计的影响更显著, 应保留更多怀疑。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    "<b>免责声明</b>: 本报告为量化研究与科普, 所有数据来自公开来源, 仅供个人学习参考, "
    "不构成任何投资建议或买卖要约。市场有风险, 投资需谨慎。据此操作, 盈亏自负。", NOTE))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    f"数据截止 {AS_OF} · 7 只蓝宝石概念龙头等权指数 · {N_MONTHS} 个月度起点 · "
    "方法与代码可复现 · 出品: 量化研究笔记 · 作者: 靳秋野", CAP))


# ════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(str(PDF), pagesize=A4,
                        topMargin=2.0 * cm, bottomMargin=1.7 * cm,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        title="蓝宝石概念评估·量化深度研报", author="靳秋野")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print(f"✓ PDF 已生成: {PDF}")
print(f"  页数约 {len(S)} flowables")
