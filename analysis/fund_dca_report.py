"""
定投场外热门基金 vs 场内买股票 — 付费深度研报 (reportlab, 中文)
================================================================
读取 fund_dca_winrate.py 的 summary.json + figures/, 排版为付费研报 PDF。

Usage:
    conda activate research
    python analysis/fund_dca_winrate.py
    python analysis/fund_dca_report.py
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

ROOT = Path("./output/2026-06-10/fund-dca-winrate")
FIGS = ROOT / "figures"
PDF = ROOT / "定投热门基金胜率_量化研报.pdf"
S_ = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

NAVY = colors.HexColor("#10243e"); GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626"); ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb"); GRAY = colors.HexColor("#666")
LIGHT = colors.HexColor("#eef2f7"); INK = colors.HexColor("#2d2d2d")
TEAL = colors.HexColor("#0e7490")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=26, textColor=NAVY, alignment=1, leading=34, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=13, textColor=GRAY, alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white, backColor=NAVY,
                    leading=26, spaceBefore=18, spaceAfter=12, leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY, leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK, leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY, alignment=1, leading=12, spaceAfter=10)

AS_OF = S_["as_of"]
R = S_["results"]
BASE_DCA = S_["baseline_dca"]
CHASE = S_["chase"]
HS = [("12", "1年"), ("24", "2年"), ("36", "3年"), ("60", "5年")]


def g(group, method, H, key):
    return R[group][method][str(H)][key]


def pct(x, d=1):
    return f"{x*100:+.{d}f}%" if x == x else "—"


def pct0(x):
    return f"{x*100:.0f}%" if x == x else "—"


def img(name, w_cm=16.0):
    from PIL import Image as PILImage
    p = FIGS / name
    iw, ih = PILImage.open(p).size
    w = w_cm * cm
    return Image(str(p), width=w, height=w * ih / iw)


def table(data, cw, fs=9.5, hl=None):
    t = Table(data, colWidths=cw, hAlign="CENTER")
    st = [("FONTNAME", (0, 0), (-1, -1), "CN"), ("FONTSIZE", (0, 0), (-1, -1), fs),
          ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "CN-B"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    if hl:
        for r in hl:
            st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fff3d6")))
            st.append(("FONTNAME", (0, r), (-1, r), "CN-B"))
    t.setStyle(TableStyle(st))
    return t


def watermark(c, d):
    c.saveState(); c.setFont("CN", 58); c.setFillColor(colors.HexColor("#eef0f3"))
    c.translate(A4[0] / 2, A4[1] / 2); c.rotate(45)
    c.drawCentredString(0, 0, "付费研报 PAID"); c.restoreState()


def on_first(c, d):
    watermark(c, d); c.saveState(); c.setFont("CN", 8.5); c.setFillColor(GRAY)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, "本报告为付费内容 · 仅供个人参考 · 不构成投资建议"); c.restoreState()


def on_later(c, d):
    watermark(c, d); c.saveState(); c.setStrokeColor(colors.HexColor("#ddd")); c.setLineWidth(0.5)
    c.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    c.setFont("CN", 8); c.setFillColor(GRAY)
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "定投热门基金胜率 · 量化研报")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, f"数据截止 {AS_OF}")
    c.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    c.drawCentredString(A4[0] / 2, 0.95 * cm, f"第 {d.page} 页 · 付费内容 · 不构成投资建议")
    c.restoreState()


S = []
# ── 封面 ──
S.append(Spacer(1, 3.0 * cm))
S.append(Paragraph("定投场外热门基金，胜率到底有多高？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph("定投 vs 一把梭 × 场外热门基金 vs 场内个股 — 胜率与翻车率量化研究", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))
ck = [["基金定投3年胜率", "个股一把梭3年胜率", "个股亏损过半概率"],
      [pct0(g("基金", "dca", 36, "win")), pct0(g("个股", "lump", 36, "win")), pct0(g("个股", "lump", 36, "loss50"))]]
ct = Table(ck, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"), ("FONTSIZE", (0, 0), (-1, 0), 11), ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"), ("FONTSIZE", (0, 1), (-1, 1), 22), ("TEXTCOLOR", (0, 1), (0, 1), GREEN),
    ("TEXTCOLOR", (1, 1), (1, 1), ORANGE), ("TEXTCOLOR", (2, 1), (2, 1), RED),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 1), (-1, 1), 6)]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph(
    f"样本：{S_['n_funds']}只散户最爱的明星主动基金 × 沪深300全部 {S_['n_stocks']} 只成分股（外加沪深300指数基金作基准）· 滚动起点回测 · 全程可复现", SUB))
S.append(Spacer(1, 2.2 * cm))
S.append(Paragraph("出品：量化研究笔记　|　数据源 AKShare（开源）　|　数据截止 " + AS_OF, CAP))
S.append(PageBreak())

# ── 摘要 ──
S.append(Paragraph("摘要与核心结论", H2))
S.append(Paragraph(
    "“基金赚钱、基民不赚钱”“追星基金被深套”是过去几年A股最痛的两个话题。散户最常见的两种入场姿势——"
    "(A) 定投场外的明星/热门主动基金；(B) 自己在场内挑股票买——到底哪个胜率更高、谁的“翻车”风险更大？"
    f"本报告用 {S_['n_funds']} 只顶流明星基金的累计净值（含分红再投）与当前沪深300全部成分股的后复权价，"
    "对“每个月都入场一次”的滚动起点做回测，统计不同持有年限的赚钱概率（胜率）与亏损分布，给出可复现的答案。", BODY))
concl = [
    f"<b>胜率：基金定投 ≈ 买个股，并没有碾压</b>。持有3年，基金定投胜率 {pct0(g('基金','dca',36,'win'))}、"
    f"个股一把梭 {pct0(g('个股','lump',36,'win'))}、沪深300定投 {pct0(BASE_DCA['36']['win'])}——光看“赚不赚”三者差不多，"
    f"胜率主要由持有期决定（5年普遍升到 73%-86%）。“买基金胜率就碾压散户烒股”更多是一种错觉。",
    f"<b>真正的鸿沟在“翻车率”</b>。持有3年，个股一把梭“亏损过半(-50%)”的概率高达 "
    f"{pct0(g('个股','lump',36,'loss50'))}、亏30%+概率 {pct0(g('个股','lump',36,'loss30'))}、最差一次亏 {pct(g('个股','lump',36,'worst'),0)}；"
    f"而基金定投亏损过半概率 {pct0(g('基金','dca',36,'loss50'))}、最差 {pct(g('基金','dca',36,'worst'),0)}，宽基定投更是几乎零翻车——分散就是不归零。",
    f"<b>定投并不提高胜率、也不让你多赚</b>。对长期上涨的标的，一把梭（早买）的胜率和收益往往都更高"
    f"（基金一次性3年胜率 {pct0(g('基金','lump',36,'win'))}、均值 {pct(g('基金','lump',36,'mean'),0)} vs 定投 {pct0(g('基金','dca',36,'win'))}、{pct(g('基金','dca',36,'mean'),0)}）；"
    f"定投真正降的是最差情形、回撤与波动，治的是择时焦虑。",
    f"<b>最该避免的动作是“追热门”</b>。在基金近一年大涨（前1/3）时入场，一把梭3年胜率从平时的 "
    f"{pct0(CHASE['all_lump']['win'])} 掉到 {pct0(CHASE['hot_lump']['win'])}，定投从 {pct0(CHASE['all_dca']['win'])} 掉到 {pct0(CHASE['hot_dca']['win'])}——连定投也救不回追高。",
    f"<b>一句话结论</b>：对普通人，<b>“宽基定投打底 + 分散 + 拉长持有 + 不追热门”</b> 的价值，"
    f"不是“胜率更高”，而是<b>几乎不会翻车、不依赖选股运气、拿得住</b>——这才是它优于“场内挑个股一把梭”的地方。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph("* 结论基于历史回测、重叠样本统计反映条件期望，不代表未来；个股池采用当前成分股，存在生存者偏差（见方法）。", NOTE))
S.append(PageBreak())

# ── 一、背景 ──
S.append(Paragraph("一、为什么研究这个问题", H2))
S.append(Paragraph(
    "2019-2021年是公募基金的“造星”大年，张坤、葛兰、刘彦春等明星经理被冠以“yyds”，白酒、医疗、新能源主题基金"
    "巨额申购，无数新基民在板块最热时一把梭买入；随后2022-2024年的回撤，让“追星被套”成为集体记忆。"
    "与此同时，另一批投资者选择自己在场内买股票，幻想抓住下一个茅台、宁德。", BODY))
S.append(Paragraph(
    "这两种行为的底层差异是两件事的叠加：<b>① 方法</b>——是“定投（分批）”还是“一把梭（择时）”；"
    "<b>② 标的</b>——是“分散的基金”还是“集中的个股”。本报告把这两个维度拆开，做 2×2 对照，"
    "用数据回答：定投热门基金的胜率，到底是不是比自己买股票高。", BODY))
S.append(PageBreak())

# ── 二、方法 ──
S.append(Paragraph("二、研究方法与数据", H2))
S.append(Paragraph("2.1 数据与样本", H3))
S.append(Paragraph(
    f"<b>场外热门基金（{S_['n_funds']}只）</b>：取散户高知名度的明星主动权益基金（含 LOF），"
    "如易方达蓝筹精选(张坤)、中欧医疗健康(葛兰)、景顺长城新兴成长(刘彦春)、兴全合润(谢治宇)、"
    "富国天惠(朱少醒)、招商中证白酒、诺安成长等，使用<b>累计净值</b>（含分红再投，总收益口径）。", BODY))
S.append(Paragraph(
    f"<b>场内个股</b>：当前沪深300全部 {S_['n_stocks']} 只成分股，使用<b>后复权</b>收盘价（含分红，总收益口径）。"
    "用客观的指数成分股、而非手挑个股，避免“故意挑烂股”的质疑。", BODY))
S.append(Paragraph(
    "<b>重要说明（让结论更保守）</b>：当前沪深300成分股都是“今天还活着、且做大到能进指数”的大白马，"
    "天然带正向生存者偏差——相当于给“买个股”开了上帝视角。即便如此，下文结论依然成立，因此是偏保守的。", NOTE))
S.append(Paragraph("2.2 方法", H3))
for c in [
    "<b>口径统一</b>：所有净值/价格转为月末序列，均为含分红的总收益口径，基金与个股可比。",
    "<b>一把梭（一次性）</b>：在起点月投入全部本金，持有 H 个月，收益 = 期末/期初 - 1。",
    "<b>定投</b>：在起点起每月末等额投 1 份，共 H 份，在第 H 月末估值，收益 = 总市值/总投入 - 1。",
    "<b>滚动起点</b>：对每个标的、每个可行的起点月、每个持有期 H∈{1,2,3,5}年 都计算一遍，"
    "把同组（基金/个股）的全部结果合并，统计胜率与亏损分布。重叠样本反映“随机挑时点入场”的条件期望。",
    "<b>追热门子实验</b>：把入场时点限定在“该基金近一年涨幅处于自身历史前1/3”，比较一把梭与定投的3年胜率。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(PageBreak())

# ── 三、胜率 ──
S.append(Paragraph("三、主结论①：比胜率，基金并没赢个股", H2))
S.append(img("fig_winrate.png", 16))
S.append(Paragraph("图1　不同持有年限的赚钱概率（胜率）：基金定投 / 个股定投 / 个股一把梭 / 沪深300定投", CAP))
t1 = [["持有期", "基金定投", "个股定投", "个股一把梭", "沪深300定投"]]
for H, lab in HS:
    t1.append([lab, pct0(g("基金", "dca", H, "win")), pct0(g("个股", "dca", H, "win")),
               pct0(g("个股", "lump", H, "win")), pct0(BASE_DCA[H]["win"])])
S.append(table(t1, [3.0 * cm, 3.2 * cm, 3.0 * cm, 3.2 * cm, 3.2 * cm], hl=[3]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"解读：光看胜率，基金定投（{pct0(g('基金','dca',36,'win'))}）并不比个股一把梭（{pct0(g('个股','lump',36,'win'))}）高，"
    f"沪深300定投（{pct0(BASE_DCA['36']['win'])}）也在同一水平——三者差不多。胜率主要由“持有多久”决定，而非“买基金还是买个股”："
    f"持有期从1年拉到5年，胜率普遍从约 60% 抬升到 73%-86%。所以“买基金胜率就更高”是个误解，真正的差别在下一节。", BODY))
S.append(PageBreak())

# ── 四、尾部风险 ──
S.append(Paragraph("四、主结论②：真正的差距，在“翻车率”", H2))
S.append(img("fig_tailrisk.png", 16))
S.append(Paragraph("图2　持有3年的“亏损过半”概率与“最差情形”：基金 vs 个股", CAP))
t2 = [["组合（持有3年）", "亏30%+概率", "亏50%+概率", "最差情形", "中位收益", "P10(差)", "P90(好)"]]
for lab, grp, mth in [("基金定投", "基金", "dca"), ("基金一次性", "基金", "lump"),
                      ("个股定投", "个股", "dca"), ("个股一把梭", "个股", "lump")]:
    t2.append([lab, pct0(g(grp, mth, 36, "loss30")), pct0(g(grp, mth, 36, "loss50")),
               pct(g(grp, mth, 36, "worst"), 0), pct(g(grp, mth, 36, "med"), 0),
               pct(g(grp, mth, 36, "p10"), 0), pct(g(grp, mth, 36, "p90"), 0)])
S.append(table(t2, [3.2 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.0 * cm, 2.0 * cm], fs=9, hl=[4]))
S.append(Spacer(1, 0.15 * cm))
S.append(img("fig_distribution.png", 12))
S.append(Paragraph("图3　持有3年的收益分布（P10 / 中位 / P90）", CAP))
S.append(Paragraph(
    f"解读：胜率只是“赚不赚”，更致命的是“一旦错，会亏多惨”。押注单一个股，持有3年“亏损过半”的概率高达 "
    f"{pct0(g('个股','lump',36,'loss50'))}，历史最差亏到 {pct(g('个股','lump',36,'worst'),0)}（个股可能腰斩、退市、归零）；"
    f"而基金定投把亏损过半概率压到 {pct0(g('基金','dca',36,'loss50'))}、最差 {pct(g('基金','dca',36,'worst'),0)}。"
    f"<b>分散持仓的本质，是用“放弃单吊暴富”换“几乎不会归零”。</b>", BODY))
S.append(PageBreak())

# ── 五、定投 vs 一次性 ──
S.append(Paragraph("五、主结论③：定投 vs 一把梭，各买什么", H2))
S.append(img("fig_dca_vs_lump.png", 16))
S.append(Paragraph("图4　基金：定投 vs 一次性 的胜率与平均收益对比", CAP))
t3 = [["基金（持有3年）", "胜率", "平均收益", "中位收益", "最差情形"]]
for lab, mth in [("定投", "dca"), ("一次性梭哈", "lump")]:
    t3.append([lab, pct0(g("基金", mth, 36, "win")), pct(g("基金", mth, 36, "mean"), 0),
               pct(g("基金", mth, 36, "med"), 0), pct(g("基金", mth, 36, "worst"), 0)])
S.append(table(t3, [4.0 * cm, 2.8 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm], hl=[1]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "解读：这是最容易被误解的一点。<b>定投并不一定让你赚得更多，胜率也并不更高</b>——在长期向上的市场里，"
    "越早把钱投进去（一把梭）胜率和收益往往都更高，因为定投有相当一部分钱“买在了后面更高的位置”。"
    "定投真正的价值是：<b>压低最差情形、熨平波动、让你拿得住</b>。"
    "对“择时能力≈0、且容易追涨杀跌”的普通人，用一点平均收益换更浅的回撤和更好的持有体验，通常是划算的。", BODY))
S.append(PageBreak())

# ── 六、追热门 ──
S.append(Paragraph("六、主结论④：追在最火的高点怎么办", H2))
S.append(img("fig_chasing.png", 15))
S.append(Paragraph("图5　“追热门高点”情形下，一把梭 vs 定投 的3年胜率", CAP))
t4 = [["情形（持有3年）", "胜率", "中位收益", "最差情形"]]
for lab, key in [("任意时点 · 一把梭", "all_lump"), ("追热门高点 · 一把梭", "hot_lump"),
                 ("任意时点 · 定投", "all_dca"), ("追热门高点 · 定投", "hot_dca")]:
    c = CHASE[key]
    t4.append([lab, pct0(c["win"]), pct(c["med"], 0), pct(c["worst"], 0)])
S.append(table(t4, [4.6 * cm, 2.8 * cm, 3.0 * cm, 3.0 * cm], hl=[2, 4]))
S.append(Spacer(1, 0.15 * cm))
drop = (CHASE["all_lump"]["win"] - CHASE["hot_lump"]["win"]) * 100
drop_dca = (CHASE["all_dca"]["win"] - CHASE["hot_dca"]["win"]) * 100
S.append(Paragraph(
    f"解读：基金最“火”（近一年大涨、上热搜、巨额申购）的时候，往往也是入场最危险的时候——"
    f"追高一把梭的3年胜率从平时的 {pct0(CHASE['all_lump']['win'])} 掉到 {pct0(CHASE['hot_lump']['win'])}（低约 {drop:.0f} 个百分点），"
    f"定投也从 {pct0(CHASE['all_dca']['win'])} 掉到 {pct0(CHASE['hot_dca']['win'])}（低约 {drop_dca:.0f} 个百分点），这正是“追星被套”的量化写照。"
    f"<b>注意：这里定投并不能救回追高</b>（{pct0(CHASE['hot_dca']['win'])} 仍低于一把梭的 {pct0(CHASE['hot_lump']['win'])}）——因为这类强势基金在高位后往往要消化很久。"
    f"<b>所以最有效的纪律不是“追高后改定投”，而是一开始就别追热门。</b>", BODY))
S.append(PageBreak())

# ── 七、实操 ──
S.append(Paragraph("七、给普通人的实操手册", H2))
for c in [
    "<b>宽基打底、主动增强</b>：无脑定投沪深300/中证A500等宽基的胜率已经很高，先用它做底仓；"
    "明星主动基金作为“卫星仓”，别把全部身家 All in 单一爆款主题。",
    "<b>能定投就别梭哈</b>：尤其在高位、或自己看不懂行情时，用定投摇低成本。注意定投换的是更浅回撤与拿得住，而非更高胜率或收益。",
    "<b>越火越要克制</b>：近一年涨翻天、到处被安利的爆款，正是一把梭最危险的时刻；要买就分批定投进场。",
    "<b>拉长持有期</b>：1年胜率像掷硬币，3-5年胜率才显著抬升；定投最忌“跌了3个月就割肉”。",
    "<b>止盈比止损更重要</b>：主动基金会风格漂移、经理会变，涨多了要按纪律分批止盈，别让浮盈坐成过山车。",
    "<b>认清定投的边界</b>：定投降低的是“回撤/波动/择时焦虑”，而不是提高胜率或收益；它治的是人性，不是包赚。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph("八、局限与免责", H3))
S.append(Paragraph(
    "① 个股池为当前沪深300成分股，存在正向生存者偏差（真实“随便买个股”的胜率只会更低、尾部更差）；"
    "② 基金池为高知名度明星基金，亦含一定生存者偏差；③ 滚动起点为重叠样本，统计量反映条件期望而非独立同分布；"
    "④ 未计入申赎费率/管理费差异与税费；⑤ 历史规律不代表未来。本报告为研究性内容，不构成任何投资建议。", NOTE))

doc = SimpleDocTemplate(str(PDF), pagesize=A4, topMargin=2.0 * cm, bottomMargin=1.8 * cm,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        title="定投热门基金胜率量化研报", author="量化研究笔记")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print("PDF ->", PDF)
