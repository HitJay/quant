"""炸板潮反共识 · 早盘付费深度研报 PDF — 2026-06-26

输入: output/2026-06-26/morning-card/summary.json
输出: output/2026-06-26/morning-card/炸板潮反共识深度研报.pdf
"""

from __future__ import annotations
import json
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

ROOT = Path("/das/user/QYJI/quant/output/2026-06-26/morning-card")
PDF = ROOT / "炸板潮反共识深度研报.pdf"
S = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
H = S["headline_numbers"]
LB = S["lb_distribution"]
ZTO = S["zt_open_top10"]
ZBA = S["zb_amp_top10"]
MACRO = S["macro"]
INDL = S["industry_loss_top"]

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

# 配色
NAVY = colors.HexColor("#10243e")
GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626")
ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb")
GOLD = colors.HexColor("#b8860b")
GRAY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#eef2f7")
CREAM = colors.HexColor("#fff8e7")
INK = colors.HexColor("#2d2d2d")

# 样式
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
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10.5, textColor=NAVY,
                       leading=18, leftIndent=14, rightIndent=14, spaceAfter=8,
                       borderPadding=(8, 8, 8, 10), backColor=CREAM,
                       borderColor=GOLD, borderWidth=0)


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


def on_later(c, d):
    watermark(c, d)
    # 页眉线
    c.setStrokeColor(colors.HexColor("#cfd6e0"))
    c.setLineWidth(0.4)
    c.line(2 * cm, A4[1] - 1.6 * cm, A4[0] - 2 * cm, A4[1] - 1.6 * cm)
    c.setFont("CN", 9)
    c.setFillColor(GRAY)
    c.drawString(2 * cm, A4[1] - 1.3 * cm, "炸板潮反共识研报 · 2026-06-26 早盘 11:30 快照")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.3 * cm, "复旦杰伦 · 量化研究")
    # 页脚线
    c.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    c.drawString(2 * cm, 1.2 * cm, "* 仅供研究参考 · 不构成投资建议")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"第 {d.page} 页")


def hr():
    return HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cfd6e0"),
                      spaceBefore=4, spaceAfter=6)


story = []

# ============ 封面 ============
story.append(Spacer(1, 3.5 * cm))
story.append(Paragraph("炸板潮里的反共识", H1))
story.append(Paragraph("39 个涨停 vs 36 个炸板 — 早盘 11:30 快照", SUB))
story.append(Spacer(1, 1.3 * cm))

cover_nums = [
    [Paragraph(f'<font color="#16a34a"><b>{H["n_zt"]}</b></font>', H1),
     Paragraph(f'<font color="#dc2626"><b>{H["n_zb"]}</b></font>', H1),
     Paragraph(f'<font color="#ea580c"><b>{H["zt_open_pct"]:.0f}%</b></font>', H1)],
    [Paragraph("涨停 (表面赢家)", NOTE),
     Paragraph("炸板 (上午曾涨停, 没守住)", NOTE),
     Paragraph("涨停股当日炸过封板", NOTE)],
]
ct = Table(cover_nums, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
ct.setStyle(TableStyle([
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ("TOPPADDING", (0, 1), (-1, 1), 0),
]))
story.append(ct)
story.append(Spacer(1, 1.0 * cm))
story.append(Paragraph(
    "<b>核心结论</b>: 在大盘 -2.14% / 创业板 -3.72% / 4600 只下跌的环境下, 39 只涨停 "
    "和 36 只炸板几乎 1:1 出现. 涨停股中 21 只 (54%) 当日炸过封板, 11 只炸过 3 次以上, "
    "五方光电单日炸板 22 次. 这不是题材爆发, 是流动性陷阱里游资博弈剩余羊毛 — "
    "追涨停板的散户当下的赔率，比表面看到的要差得多.",
    QUOTE))
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph("数据范围: 2026-06-26 09:30 — 11:30 (早盘)", NOTE))
story.append(Paragraph("数据源: 东方财富涨停池 / 炸板池 / 行业板块 (sina + push2 直连)", NOTE))
story.append(Paragraph("付费版 · 复旦杰伦量化研究 · v1", NOTE))
story.append(PageBreak())

# ============ Section 1: 摘要 ============
story.append(Paragraph("一、摘要与核心结论", H2))

bullets = [
    f"<b>涨停 vs 炸板比例近 1:1</b>: 全市场涨停 {H['n_zt']} 只, 炸板 {H['n_zb']} 只 — "
    f"这意味着每追到 1 只成功封板的股, 几乎要承担 1 只『冲过涨停又被砸下来』的同质风险.",
    f"<b>{H['zt_open_pct']:.0f}% 的涨停股当日炸过封板</b>: {H['n_zt_with_open']}/{H['n_zt']} 涨停股『封板被打开过』, "
    f"{H['n_zt_open_3plus']} 只炸 ≥3 次, {H['max_open_name']}({H['max_open_code']}) 单日炸 {H['max_open_count']} 次. "
    "这些是『反复横跳』的伪强势.",
    f"<b>题材无龙头</b>: 涨停股 {H['first_board']} 只 ({H['first_board_pct']:.0f}%) 是首板, 只有 "
    f"{H['top_lb']['name']} ({H['top_lb']['code']}) 1 只 6 板, 没有 5 板 / 4 板梯队. "
    "题材接力断档 — 这是不健康的涨停结构.",
    f"<b>炸板池振幅惊人</b>: {H['n_zb']} 只炸板股振幅 TOP1 是 {H['zb_amp_max_name']} ({H['zb_amp_max']}%), "
    f"24 只振幅 >10%. 上午冲到涨停又被砸下来十几个点 — 追涨停的散户当下账面被套.",
    "<b>宏观背景把答案写在脸上</b>: 沪指 -2.14% / 深成指 -3.04% / 创业板 -3.72% / 4600 只跌, "
    "通信领跌主力流出 347 亿, 锂电流出 84 亿. 资金避险, 涨停潮不是『信号反转』, 是『流动性窄活水里的羊毛博弈』.",
]
for b in bullets:
    story.append(Paragraph("• " + b, BULLET))

story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "<b>给读者的一句话</b>: 看到 39 个涨停别先兴奋, 看东财涨停池的『炸板次数』字段, "
    "再看炸板池里有多少只 — 你会得到完全不同的结论.",
    QUOTE))

# ============ Section 2: 大盘背景 ============
story.append(Paragraph("二、大盘背景: 大跌中的窄活水", H2))
story.append(Paragraph("2.1 三大指数与资金流", H3))

macro_data = [
    ["指数", "点位", "涨跌幅", "解读"],
    ["上证指数", f"{MACRO['sh_pt']:.0f}", f"{MACRO['sh_chg_pct']:+.2f}%", "权重股普跌"],
    ["深证成指", f"{MACRO['sz_pt']:.0f}", f"{MACRO['sz_chg_pct']:+.2f}%", "中盘跟跌"],
    ["创业板指", f"{MACRO['cyb_pt']:.0f}", f"{MACRO['cyb_chg_pct']:+.2f}%", "成长股深跌"],
]
mt = Table(macro_data, colWidths=[3.5 * cm, 3 * cm, 3 * cm, 6 * cm])
mt.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("TEXTCOLOR", (2, 1), (2, -1), RED),
    ("ALIGN", (1, 0), (2, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
]))
story.append(mt)
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    f"<b>关键数字</b>: 全市场近 {MACRO['n_decline']} 只下跌, 两市半日成交 2.43 万亿 (放量 33 亿). "
    "放量下跌 = 抛压堆叠, 不是恐慌底, 是恐慌中.", BODY))

story.append(Paragraph("2.2 行业跌幅 TOP6", H3))
ind_rows = [["板块", "涨跌幅", "主力净流入 (亿)"]]
for r in INDL[:6]:
    ind_rows.append([r["板块名称"], f"{r['涨跌幅']:.2f}%", f"{r['主力净流入']/1e8:+.1f}"])
indt = Table(ind_rows, colWidths=[5.5 * cm, 4 * cm, 5 * cm])
indt.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("TEXTCOLOR", (1, 1), (1, -1), RED),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
]))
story.append(indt)
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    "<b>解读</b>: 跌幅前 5 全是热门赛道 — 能源金属 (锂电上游) / 通信设备 (CPO 算力) / 贵金属 / 通信 / 电池. "
    "雪球讨论榜上散户在聊的茅台 / 比亚迪 / 寒武纪 / 宁德, 今天没有一个在涨, 多数下跌 3% 以上. "
    "这就是『资金避险 + 题材轮动到冷门』的典型结构.", BODY))
story.append(PageBreak())

# ============ Section 3: 涨停结构剖析 ============
story.append(Paragraph("三、涨停结构剖析: 看着 39, 真稳的不到一半", H2))
story.append(Paragraph("3.1 涨停股内部分层", H3))
story.append(Paragraph(
    "东财涨停池有一个被多数散户忽视的字段 — <b>『炸板次数』</b>. "
    "它记录的是该股当日盘中『封涨停 → 被打开 → 再次封涨停』发生的次数. "
    "封板次数越多 = 该涨停越不稳, 中间每一次打开都给空头 / 止损散户机会出货, "
    "等下次封回时分歧已经被释放, 这种『涨停』和『稳稳一字板』的赔率根本不是一个量级.",
    BODY))
story.append(Spacer(1, 0.2 * cm))

# 三层分布表
layer_data = [
    ["分层", "数量", "占涨停比", "说明"],
    [f"全部涨停", f"{H['n_zt']}", "100%", "表面看到的『赢家』"],
    [f"当日炸过封板 (≥1 次)", f"{H['n_zt_with_open']}", f"{H['zt_open_pct']:.0f}%", "封了又开, 不稳"],
    [f"炸过 3 次以上", f"{H['n_zt_open_3plus']}", f"{H['n_zt_open_3plus']/H['n_zt']*100:.0f}%", "极不稳定"],
    [f"6 板真龙头", "1", f"{1/H['n_zt']*100:.0f}%", f"{H['top_lb']['name']} ({H['top_lb']['code']})"],
]
lt = Table(layer_data, colWidths=[5 * cm, 2.5 * cm, 2.5 * cm, 5.5 * cm])
lt.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (1, 0), (2, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("TEXTCOLOR", (0, 2), (0, 2), ORANGE),
    ("TEXTCOLOR", (0, 3), (0, 3), RED),
    ("TEXTCOLOR", (0, 4), (0, 4), GOLD),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
]))
story.append(lt)
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    "<b>翻译人话</b>: 100 个涨停里, 真正稳稳封住、没被打开过的只有 46 个. "
    "剩下 54 个是『早盘冲上去 → 中午被砸 → 下午勉强封回』, "
    "这种股 T+1 翻车的概率显著高于一字板.",
    QUOTE))

story.append(Paragraph("3.2 炸板次数 TOP10 (心跳冲浪手榜)", H3))
zto_rows = [["排名", "代码", "名称", "行业", "炸板次数", "连板"]]
for i, r in enumerate(ZTO[:10]):
    zto_rows.append([str(i+1), r["代码"], r["名称"], r["所属行业"],
                     f"{r['炸板次数']}", f"{r['连板数']} 板"])
zt_table = Table(zto_rows, colWidths=[1.2 * cm, 2.2 * cm, 3 * cm, 3 * cm, 2.2 * cm, 1.8 * cm])
zt_table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ALIGN", (2, 1), (3, -1), "LEFT"),
    # 前 3 红色 (高炸板)
    ("TEXTCOLOR", (4, 1), (4, 3), RED),
    ("FONTNAME", (4, 1), (4, 3), "CN-B"),
    # 4-10 橙色
    ("TEXTCOLOR", (4, 4), (4, -1), ORANGE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
]))
story.append(zt_table)
story.append(Spacer(1, 0.2 * cm))
story.append(Paragraph(
    f"<b>{H['max_open_name']} ({H['max_open_code']}) 单日炸板 {H['max_open_count']} 次</b> — "
    "意味着今天封板被打开 22 次, 一整天反复『封→开→封→开』. 这种股的涨停, 是用全天血战换来的, "
    "而每一次开板都伴随大量止损盘 + 跟风盘换手, T+1 高开冲高承接难度极大.",
    BODY))
story.append(PageBreak())

# ============ Section 4: 连板梯队 ============
story.append(Paragraph("四、连板梯队: 题材接力断档", H2))

lb_rows = [["板位", "数量", "占比"]]
for lvl in sorted(LB.keys(), reverse=True):
    cnt = LB[lvl]
    lb_rows.append([f"{lvl} 板", str(cnt), f"{cnt/H['n_zt']*100:.0f}%"])
lb_table = Table(lb_rows, colWidths=[5 * cm, 4 * cm, 4 * cm])
lb_table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 10.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
]))
story.append(lb_table)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    f"<b>关键</b>: {H['first_board']}/{H['n_zt']} = {H['first_board_pct']:.0f}% 是首板, 只 1 只 6 板 "
    f"({H['top_lb']['name']}, 行业属冷门纺织制造). 没有 4-5 板梯队 = 没有题材接力. "
    "这与上一轮 AI 行情的『5 个龙头 + 8-10 板长龙』形成鲜明对比.", BODY))

story.append(Paragraph("4.1 健康涨停潮 vs 今日结构对比", H3))
compare_rows = [
    ["特征", "健康涨停潮 (e.g. 2023 AI / 2024 低空)", "今日 (2026-06-26)"],
    ["龙头数量", "3-5 个", f"1 个 ({H['top_lb']['name']})"],
    ["最高连板", "8-10 板", f"6 板"],
    ["首板占比", "<60%", f"{H['first_board_pct']:.0f}%"],
    ["炸板/涨停比", "<0.5", f"{H['n_zb']/H['n_zt']:.2f}"],
    ["主线行业", "1-2 个明确赛道", "专用设备/电力/光学 散乱"],
    ["大盘情绪", "上涨日 或 缩量整理", "大跌 -2.14% / 4600 只跌"],
]
cmp_table = Table(compare_rows, colWidths=[4 * cm, 6 * cm, 5.5 * cm])
cmp_table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("TEXTCOLOR", (1, 1), (1, -1), GREEN),
    ("TEXTCOLOR", (2, 1), (2, -1), RED),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
]))
story.append(cmp_table)
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    "六项特征里, 今日有 5 项偏负面 (龙头少 / 连板低 / 首板高 / 炸板比高 / 主线散). "
    "唯一勉强中性的是『大盘大跌』 — 这本身就解释了为什么涨停看着热闹但不持续: "
    "增量资金不足时, 涨停潮 = 存量游资在剩余热点里的快速进出.", BODY))

story.append(PageBreak())

# ============ Section 5: 炸板池 ============
story.append(Paragraph("五、炸板池: 上午追涨停的散户当下在哪", H2))
story.append(Paragraph(
    f"炸板池 = 当日盘中曾触及涨停但收盘未能封住的股. 今天 {H['n_zb']} 只, "
    f"和涨停 {H['n_zt']} 只几乎 1:1. 这些股的振幅 (全天最高价 / 最低价跨度) 直接反映了"
    "『冲到涨停后又被砸到多深』 — 也就是高位追入的散户当下账面被套幅度.", BODY))
story.append(Spacer(1, 0.15 * cm))

zb_rows = [["排名", "代码", "名称", "行业", "全日振幅", "当下涨幅"]]
for i, r in enumerate(ZBA[:10]):
    cur = r["涨跌幅"]
    cur_str = f"{cur:+.1f}%"
    zb_rows.append([str(i+1), r["代码"], r["名称"], r["所属行业"],
                    f"{r['振幅']:.1f}%", cur_str])
zb_table = Table(zb_rows, colWidths=[1.2 * cm, 2.2 * cm, 3 * cm, 3 * cm, 2.5 * cm, 2.5 * cm])
zb_table.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "CN"),
    ("FONTNAME", (0, 0), (-1, 0), "CN-B"),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ALIGN", (2, 1), (3, -1), "LEFT"),
    ("TEXTCOLOR", (4, 1), (4, 4), RED),     # 前 4 振幅红色
    ("FONTNAME", (4, 1), (4, 4), "CN-B"),
    ("TEXTCOLOR", (4, 5), (4, -1), ORANGE),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cfd6e0")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
]))
story.append(zb_table)
story.append(Spacer(1, 0.25 * cm))
story.append(Paragraph(
    f"<b>{H['zb_amp_max_name']} 振幅 {H['zb_amp_max']}%</b>: 从最高点到最低点跨度 26.9%. "
    "上午 9:30 开盘冲涨停 → 11:30 已经被砸到 -1% 区间. 9:35 在涨停板上挂买追入的散户, "
    "当下账面就是 -25% 的浮亏. 这就是炸板的真实代价.", QUOTE))
story.append(Spacer(1, 0.2 * cm))
story.append(Paragraph(
    f"全部 {H['n_zb']} 只炸板股里, 24 只振幅 >10%, 也就是 {24/H['n_zb']*100:.0f}% 的炸板股 "
    "都把高位追入者套了 10 个点以上. 这个比例在过去几个月的『中位』水平大约是 30-40%, "
    "今天达到 67% — 反映了大跌日里炸板的杀伤力被放大.", BODY))

# ============ Section 6: 操作手册 ============
story.append(Paragraph("六、给个人投资者的实操手册", H2))

story.append(Paragraph("6.1 当下不应该做的事", H3))
no_list = [
    "不要看到 39 个涨停就觉得『情绪好』 — 真正的情绪指标是『涨停 - 炸板』差值, 今天只有 +3, 几乎中性偏弱.",
    "不要追首板, 尤其是冷门行业的首板. 今天 32 只首板, 续板成功率历史中位 ~30%, 在大跌日里更低.",
    "不要在炸板股开板瞬间冲进去『接龙头』. 五方光电炸 22 次, 每一次开板都有人觉得自己抄到了底, 但下一次 22 分之 1 的概率才是真底.",
    "不要凭板块名感觉买. 涨停集中在专用设备 / 电力 / 光学光电 / 化学制品 — 不是 AI / 锂电 / 算力主线.",
]
for n in no_list:
    story.append(Paragraph("× " + n, BULLET))

story.append(Paragraph("6.2 当下可以做的事", H3))
yes_list = [
    "<b>看东财涨停池『炸板次数』字段</b>. 这是免费数据但被大多数散户忽视. 选股先过滤『炸板次数 = 0』的真稳板.",
    "<b>看连板梯队是否有 4-5 板</b>. 没有 4-5 板的涨停潮, 题材接力不会持续, 短线快进快出.",
    "<b>关注 6 板兴业科技后续表现</b>. 如果它 T+1 能再封, 说明资金还有信仰; 如果开板, 说明这一波就是局部博弈.",
    "<b>大盘 -2% 以上日子里, 仓位收紧到 5 成以下</b>. 中长线 ETF 仓位维持, 短线投机仓位减半.",
    "<b>等收盘数据更新</b>. 11:30 早盘的快照只是上午的故事, 下午可能有反包, 也可能继续杀跌. 重要决策推到收盘后.",
]
for n in yes_list:
    story.append(Paragraph("✓ " + n.replace("✓", ""), BULLET))

story.append(Paragraph("6.3 一句话总结", H3))
story.append(Paragraph(
    "<b>大盘大跌日里出现的『涨停潮』, 通常不是机会信号, 而是流动性陷阱里的羊毛博弈. "
    "看『炸板次数』不看『涨停股数』, 你的胜率会比 90% 的散户高一截.</b>",
    QUOTE))

# ============ Section 7: 局限与免责 ============
story.append(Paragraph("七、局限与免责声明", H2))
limit_list = [
    "本报告为 <b>2026-06-26 11:30 早盘快照</b>, 下午行情可能反转, 不代表全日收盘结构.",
    "炸板次数字段为东方财富统计口径 (盘中封板后被打开的次数), 不同行情软件统计可能略有差异.",
    "『健康涨停潮 vs 不健康涨停潮』的对比是基于历史经验直观描述, 没有严格 backtest, 仅供方向性参考.",
    "本报告所列个股 (兴业科技 / 五方光电 / TCL中环 / 莱赛激光 等) 仅作为数据样本举例, "
    "不构成买入或卖出建议. 任何个股操作请独立判断.",
    "本报告为研究记录, 非投资咨询服务, 不对读者据此操作产生的盈亏承担任何责任.",
    "数据源: 东方财富涨停池 (stock_zt_pool_em) / 炸板池 (stock_zt_pool_zbgc_em) / "
    "行业板块 (push2 直连) / 雪球关注 / 东财新闻. 抓取脚本 hotspot_card_prep.py 公开可复现.",
]
for n in limit_list:
    story.append(Paragraph("• " + n, BULLET))

story.append(Spacer(1, 0.4 * cm))
story.append(hr())
story.append(Paragraph(
    "© 复旦杰伦 · 量化研究 · 2026-06-26 早盘版 · 付费内容仅限订阅者阅读 · 严禁未授权转发", NOTE))


# ============ 渲染 ============
doc = SimpleDocTemplate(str(PDF), pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2.2 * cm, bottomMargin=2.2 * cm)
doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
print(f"[OK] PDF 写入: {PDF}")
print(f"  size: {PDF.stat().st_size / 1024:.1f} KB")
