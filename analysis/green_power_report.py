"""
绿色电力深度量化研报 — PDF生成(reportlab, 中文)
================================================
读取 green_power_analysis.py 产出的 summary.json + data/,
排版为专业付费研报 PDF。

Usage:
    conda activate research
    python analysis/green_power_analysis.py   # 先跑分析
    python analysis/green_power_report.py
"""

import json
from pathlib import Path
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ── 路径 ──
ROOT = Path("./output/2026-06-15/green-power-winrate")
DATA = ROOT / "data"
PDF = ROOT / "绿色电力量化研报.pdf"
summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

# 读取CSV数据
wr_df = pd.read_csv(DATA / "rolling_winrate.csv")
cond_df = pd.read_csv(DATA / "conditional_winrate_1y.csv")

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
                      leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", fontName="CN", fontSize=10.5, textColor=INK,
                        leading=18, spaceAfter=5, leftIndent=16, bulletIndent=2)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY,
                     alignment=1, leading=12, spaceAfter=10)


def pct(x, d=1):
    if x != x:
        return "-"
    return f"{x*100:+.{d}f}%"


def pct0(x):
    if x != x:
        return "-"
    return f"{x*100:.0f}%"


# ── 表格 ──
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
                             "本报告为付费内容 - 仅供个人参考 - 不构成投资建议")
    canvas.restoreState()


def on_later(canvas, doc):
    _watermark(canvas, doc)
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#dddddd"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    canvas.setFont("CN", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, A4[1] - 1.25 * cm, "绿色电力量化研报")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm,
                           f"数据: {summary['data_range']}")
    canvas.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    canvas.drawCentredString(A4[0] / 2, 0.95 * cm,
                             f"第 {doc.page} 页 - 付费内容 - 不构成投资建议")
    canvas.restoreState()


# ════════════════════════════════════════════════════════════════
# 正文
# ════════════════════════════════════════════════════════════════
S = []

# ---- 封面 ----
S.append(Spacer(1, 3.2 * cm))
S.append(Paragraph("绿色电力，长线能赢吗？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph("17年历史数据深度量化: 胜率、择时、定投与风险", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))

# 封面KPI
cover_kpi = [
    ["持有1年胜率", "回撤>30%后胜率", "3年定投正收益"],
    [pct0(summary["winrate_1y"]), "88%", pct0(summary["dca_3y_winrate"])],
]
ct = Table(cover_kpi, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"), ("FONTSIZE", (0, 0), (-1, 0), 11),
    ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"), ("FONTSIZE", (0, 1), (-1, 1), 22),
    ("TEXTCOLOR", (0, 1), (0, 1), BLUE),
    ("TEXTCOLOR", (1, 1), (1, 1), GREEN),
    ("TEXTCOLOR", (2, 1), (2, 1), BLUE),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 1), (-1, 1), 6),
]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph(f"基于中证电力公用事业指数(000932) {summary['data_range']}", SUB))
S.append(Spacer(1, 2.6 * cm))
S.append(Paragraph(f"出品: 量化研究笔记 | 数据区间 {summary['data_range']} | 生成 {summary['date']}", CAP))
S.append(PageBreak())

# ---- 摘要 ----
S.append(Paragraph("摘要与核心结论", H2))
abstract = (
    "绿色电力(光伏/风电/绿电)是新能源转型的核心赛道，但近3年ETF表现惨淡，"
    "部分产品回撤超50%。本报告利用中证电力公用事业指数17年完整历史数据，"
    "系统量化绿电板块的长线持有胜率、最佳入场时机、定投效果与风险水平，"
    "为长期投资者提供数据驱动的决策框架。"
)
S.append(Paragraph(abstract, BODY))
S.append(Spacer(1, 0.2 * cm))

concl = [
    f"<b>无条件胜率平平</b>: 任意时点买入持有1年, 胜率仅{pct0(summary['winrate_1y'])}, "
    f"与沪深300({pct0(summary['csi300_1y_winrate'])})相当 -- 盲买不是好策略。",
    f"<b>择时是真正的alpha</b>: 回撤>30%买入持有1年, 胜率飙升至88%; "
    f"回撤>40%时甚至达到100%(样本11)。但半山腰(-20~-30%)胜率仅39%, 是典型陷阱区。",
    f"<b>定投可行但非必赢</b>: 3年月定投正收益率{pct0(summary['dca_3y_winrate'])}, "
    f"均值收益+15.8%, 跑赢一次性的概率仅38% -- 定投摊低成本, 但需配合止盈。",
    f"<b>长期绩效优于宽基</b>: 绿电年化{pct(summary['annual_return'])}, "
    f"沪深300同期仅+2.2%; 但最大回撤高达{pct0(summary['max_dd'])}, 需要强大持仓耐力。",
    f"<b>当前位置评估</b>: 距一年高点{pct(summary['current_dd'])}, "
    f"处于历史-20~-30%档位(胜率39%), 尚未进入高胜率区间。",
    "<b>一句话结论</b>: 绿电长线向上确定性高, 但<b>入场时机决定胜负</b> -- "
    "跌透再买(>30%回撤)是最优策略, 当前宜分批观察而非一次性重仓。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="\xe2\x80\xa2"))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph("* 本报告所有结论基于历史回测, 重叠样本统计仅反映条件期望, 不代表未来表现。", NOTE))
S.append(PageBreak())

# ---- 一、研究框架 ----
S.append(Paragraph("一、研究框架与数据", H2))
S.append(Paragraph("1.1 为什么选中证电力公用事业指数(000932)?", H3))
S.append(Paragraph(
    "绿电ETF(如159865/515790)上市最早不过2020年底, 历史数据不足5年, "
    "无法进行有统计意义的长线胜率分析。中证电力公用事业指数(000932)自2009年7月发布, "
    "涵盖电力(含新能源发电)与公用事业, 是目前可获取的最长绿电代理序列(17年), "
    "能覆盖完整的牛熊周期。", BODY))
S.append(Paragraph("1.2 数据与方法", H3))
S.append(Paragraph(
    "数据来源: AKShare开源接口(sina源)日线收盘价。分析方法: "
    "(1) 滚动起点胜率 -- 以每个交易日为买入时点, 统计持有N天后正收益概率; "
    "(2) 回撤分档条件胜率 -- 按距一年高点回撤深度分为6档, 分别统计后续1年收益分布; "
    "(3) 定投模拟 -- 滚动N个月月末定投 vs 月初一次性买入; "
    "(4) 绩效指标 -- 年化/回撤/夏普/卡玛多维比较。", BODY))
S.append(Paragraph("1.3 数据概览", H3))
overview = [
    ["指标", "值"],
    ["主分析序列", "中证电力公用事业(000932)"],
    ["数据起止", summary["data_range"]],
    ["总交易日", "4115"],
    ["累计涨幅", "+182%"],
    ["年化收益", pct(summary["annual_return"])],
    ["最大回撤", pct0(summary["max_dd"])],
    ["夏普比率", f"{summary['sharpe']:.2f}"],
]
S.append(styled_table(overview, [4 * cm, 12 * cm], font_size=10))
S.append(PageBreak())

# ---- 二、滚动胜率 ----
S.append(Paragraph("二、滚动起点胜率: 盲买能赢吗?", H2))
S.append(Paragraph(
    "以2009年以来的每一个交易日为起点, 分别计算持有1月/3月/半年/1年/2年后的收益, "
    "统计正收益比例(胜率)。这是最朴素的\"定性\"指标: 如果任意时点随机买入, 长期大概率赚钱, "
    "说明资产本身具备正期望。", BODY))
S.append(Paragraph("2.1 绿电 vs 沪深300 vs 化石能源", H3))

wr_rows = [["持有期", "绿电胜率", "绿电均值", "沪深300胜率", "沪深300均值", "化石能源胜率"]]
for _, row in wr_df.iterrows():
    wr_rows.append([
        row["持有期"],
        pct0(row["绿电胜率"]),
        pct(row["绿电均值"]),
        pct0(row["沪深300胜率"]),
        pct(row["沪深300均值"]),
        pct0(row["化石能源胜率"]),
    ])
S.append(styled_table(wr_rows, [2.4*cm, 2.4*cm, 2.4*cm, 2.6*cm, 2.6*cm, 2.8*cm], font_size=9.5))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph(
    "解读: 绿电的无条件胜率与沪深300相近(52% vs 51%), 并不具备显著优势。"
    "真正的差异在均值回报: 绿电持有1年均值+10.0% vs 沪深300+4.7%, 赔率(盈利幅度)更高。"
    "化石能源胜率与绿电相近, 但均值回报为负(-1.1%年化), 长期价值毁灭。", BODY))
S.append(Paragraph(
    "关键洞察: 绿电是\"高赔率、低确定性\"资产 -- 赢的时候赚很多, 但输的概率也不小。"
    "这种特征暗示: 择时(而非盲买)才是获取超额收益的关键。", BODY))
S.append(PageBreak())

# ---- 三、条件胜率 ----
S.append(Paragraph("三、回撤择时: 跌多少才该买?", H2))
S.append(Paragraph(
    "将每个交易日按\"距过去252日最高点的回撤深度\"分为6档, 统计在各档位买入后持有1年的胜率。"
    "这是本报告最核心的分析 -- 回答\"现在该不该入场\"。", BODY))
S.append(Paragraph("3.1 回撤分档条件胜率(持有1年)", H3))

cond_rows = [["回撤档位", "样本数", "胜率", "平均收益", "中位数收益"]]
hl_rows = []
for i, (_, row) in enumerate(cond_df.iterrows(), start=1):
    win = row["胜率"]
    if win != win:
        continue
    cond_rows.append([
        row["档位"], str(int(row["样本"])),
        pct0(win), pct(row["均值"]), pct(row["中位数"])
    ])
    # 当前位置高亮
    if row["档位"] == "-30~-20%":
        hl_rows.append(len(cond_rows) - 1)
S.append(styled_table(cond_rows, [3*cm, 2.2*cm, 2.4*cm, 3*cm, 3*cm],
                      highlight_rows=hl_rows, font_size=10))
S.append(Paragraph("(高亮行为当前所处档位)", NOTE))
S.append(Spacer(1, 0.3 * cm))

S.append(Paragraph("3.2 深度解读: 微笑曲线", H3))
S.append(Paragraph(
    "条件胜率呈现明显的\"微笑曲线\"(U型):", BODY))
smile_points = [
    "<b>左端(深跌>30%)</b>: 胜率88-100%, 均值+22~31% -- 跌透就是黄金坑, 但需要极强心理素质;",
    "<b>中间(半山腰-20~-30%)</b>: 胜率仅39%, 均值+3.5% -- 典型陷阱区, 看似已跌很多实则还会跌;",
    "<b>右端(近高点-5~0%)</b>: 胜率71%, 均值+20% -- 趋势延续的动量效应, 强者恒强;",
    "<b>浅跌(-10~-5%)</b>: 胜率60%, 均值+11% -- 正常波动, 可以持有但不必追加。",
]
for p in smile_points:
    S.append(Paragraph(p, BULLET, bulletText="\xe2\x80\xa2"))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph(
    f"当前评估: 中证电力公用事业距一年高点{pct(summary['current_dd'])}, "
    f"处于-30~-20%的\"半山腰\"区间, 对应1年胜率39%。这意味着: "
    f"当前位置入场有约60%的概率1年后亏损。建议: 等待进一步下跌至-30%以下再大力布局, "
    f"或小仓位试探(不超过目标仓位的30%)。", BODY))
S.append(PageBreak())

# ---- 四、定投分析 ----
S.append(Paragraph("四、定投策略: 能躺赢吗?", H2))
S.append(Paragraph(
    "高波动资产(如绿电)的定投有天然优势: 下跌时买到更多份额, "
    "摊低成本的效果比低波动资产更明显。但定投也有局限: 在长期上涨的市场中, "
    "会因为晚入场而跑输一次性投入。我们用滚动3年/2年月定投来量化。", BODY))
S.append(Paragraph("4.1 定投效果汇总", H3))

dca_rows = [
    ["指标", "3年月定投", "2年月定投"],
    ["正收益概率", pct0(summary["dca_3y_winrate"]), "55%"],
    ["平均收益", "+15.8%", "+9.4%"],
    ["跑赢一次性概率", "38%", "-"],
]
S.append(styled_table(dca_rows, [4*cm, 4*cm, 4*cm], font_size=10.5))
S.append(Spacer(1, 0.3 * cm))

S.append(Paragraph("4.2 解读与建议", H3))
dca_insights = [
    "3年定投正收益率60%, 远高于\"赌一把\"的随机52% -- 定投确实能改善胜率;",
    "但跑赢一次性的概率仅38% -- 如果判断对了入场时机, 一次性买入更优;",
    "定投的真正价值: 降低择时难度, 适合\"看好方向但不确定时点\"的投资者;",
    "优化建议: 定投+下跌加码(跌10%加倍金额) + 止盈(+30%减半, +50%清仓)。",
]
for p in dca_insights:
    S.append(Paragraph(p, BULLET, bulletText="\xe2\x80\xa2"))
S.append(PageBreak())

# ---- 五、风险分析 ----
S.append(Paragraph("五、风险全景: 代价有多大?", H2))
S.append(Paragraph(
    "绿电的高收益伴随着高波动和极端回撤。投资者必须事先了解\"最坏情况\", "
    "才能做出匹配自身风险承受力的仓位决策。", BODY))
S.append(Paragraph("5.1 风险指标对比", H3))

risk_rows = [
    ["指标", "中证电力公用", "沪深300", "CSI能源(化石)"],
    ["年化收益", pct(summary["annual_return"]), "+2.2%", "-1.1%"],
    ["最大回撤", pct0(summary["max_dd"]), "47%", "74%"],
    ["夏普比率", f"{summary['sharpe']:.2f}", "0.12", "0.02"],
    ["最长回本期", "~5年(2015-2020)", "~6年(2007-2014)", ">10年"],
]
S.append(styled_table(risk_rows, [3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm], font_size=10))
S.append(Spacer(1, 0.3 * cm))

S.append(Paragraph("5.2 关键风险点", H3))
risks = [
    f"最大回撤{pct0(summary['max_dd'])} -- 满仓买入最坏情况亏损过半, 心理冲击极大;",
    "回本时间长 -- 如果在2015年牛市顶部买入, 需等到2020年碳中和牛市才解套;",
    "政策依赖性强 -- 碳中和政策、光伏补贴变化直接影响板块走势;",
    "单一赛道风险 -- 技术路线变化(如钙钛矿替代硅基)可能导致行业洗牌;",
    "建议仓位: 绿电不宜超过总投资组合的15-20%, 搭配债券/红利类做风险对冲。",
]
for r in risks:
    S.append(Paragraph(r, BULLET, bulletText="\xe2\x80\xa2"))
S.append(PageBreak())

# ---- 六、实操建议 ----
S.append(Paragraph("六、实操策略建议", H2))
S.append(Paragraph("6.1 标的选择", H3))
etf_recs = [
    ["ETF", "代码", "特点", "适合人群"],
    ["绿色电力ETF", "159865", "纯绿电, 覆盖风光水核", "看好电力改革"],
    ["光伏ETF", "515790", "聚焦光伏产业链", "看好光伏降本"],
    ["绿电ETF华夏", "561560", "近3年表现最好(+7.7%/年)", "追求稳健"],
    ["风电ETF", "561330", "高弹性, 近期强势", "高风险偏好"],
]
S.append(styled_table(etf_recs, [3*cm, 2*cm, 4.5*cm, 3.5*cm], font_size=9.5))
S.append(Spacer(1, 0.3 * cm))

S.append(Paragraph("6.2 入场时机", H3))
timing = [
    "当前(-28%回撤): 可小仓位试探(目标仓位的20-30%), 不宜一次性重仓;",
    "跌至-30%: 加仓至目标的50%;",
    "跌至-40%: 满仓(历史100%胜率区间, 虽样本少但逻辑强);",
    "若反弹至-10%以内: 暂停加仓, 等下一次回调机会。",
]
for t in timing:
    S.append(Paragraph(t, BULLET, bulletText="\xe2\x80\xa2"))

S.append(Paragraph("6.3 止盈与退出", H3))
exits = [
    "浮盈+30%: 减仓一半, 锁定利润;",
    "浮盈+50%: 清仓, 等待下一轮回撤;",
    "持有>2年仍亏损: 审视是否行业基本面已变, 考虑止损;",
    "政策重大变化(如补贴取消/技术路线切换): 立即评估, 不盲目硬扛。",
]
for e in exits:
    S.append(Paragraph(e, BULLET, bulletText="\xe2\x80\xa2"))

S.append(Paragraph("6.4 定投方案(适合大多数人)", H3))
dca_plan = [
    "频率: 每周或每月定额投入;",
    "金额: 月定投额 = 可投资金额 / 24 (计划2年建仓);",
    "加码: 每跌10%, 当期定投金额翻倍;",
    "止盈: 累计盈利达30%时暂停定投并减仓;",
    "坚持: 设定最低12个月定投纪律, 避免中途放弃。",
]
for d in dca_plan:
    S.append(Paragraph(d, BULLET, bulletText="\xe2\x80\xa2"))
S.append(PageBreak())

# ---- 七、总结 ----
S.append(Paragraph("七、总结", H2))
S.append(Paragraph(
    "绿色电力是具备长期正期望的优质赛道: 17年年化+6.3%, 累计翻近3倍, "
    "在碳中和大背景下基本面向上趋势不变。但这不意味着\"随时买入都能赚\" -- "
    "52%的无条件胜率说明, 接近一半的时点买入1年后是亏钱的。", BODY))
S.append(Paragraph(
    "本报告的核心发现是: <b>同一个资产, 入场时机不同, 胜率天差地别</b> -- "
    "跌透再买(>30%回撤)胜率88%, 半山腰买入仅39%。这个\"微笑曲线\"规律, "
    "才是长线投资绿电的真正alpha来源。", BODY))
S.append(Paragraph(
    "对于当下: 绿电回撤-28%处于\"半山腰\", 尚未进入最佳入场区。"
    "建议: 小仓位观察, 等待回撤>30%后逐步加码, 或启动定投+加码方案。"
    "耐心, 是绿电投资者最重要的品质。", BODY))
S.append(Spacer(1, 1 * cm))
S.append(HRFlowable(width="80%", thickness=1, color=GRAY, hAlign="CENTER"))
S.append(Spacer(1, 0.5 * cm))
S.append(Paragraph("- 全文完 -", ParagraphStyle("END", fontName="CN", fontSize=12,
                                                textColor=GRAY, alignment=1)))
S.append(Spacer(1, 0.5 * cm))
S.append(Paragraph("更多量化研究内容, 请关注主页置顶链接。", CAP))

# ════════════════════════════════════════════════════════════════
# 生成PDF
# ════════════════════════════════════════════════════════════════
print("生成PDF研报...")
doc = SimpleDocTemplate(
    str(PDF), pagesize=A4,
    topMargin=2.0 * cm, bottomMargin=2.0 * cm,
    leftMargin=2.0 * cm, rightMargin=2.0 * cm,
    title="绿色电力量化研报",
    author="量化研究笔记",
)
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print(f"完成! -> {PDF}")
print(f"PDF大小: {PDF.stat().st_size / 1024:.0f} KB")
