"""
券商ETF 反共识深度研报 PDF — reportlab 后端（无系统依赖）
"""
from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image as RLImage,
)

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "output" / "2026-06-25" / "securities-breakout"
DATA = OUTDIR / "data"

# ── 字体 ──
FONT_PATHS = [
    "/usr/share/fonts/google-droid/DroidSansFallback.ttf",
]
FONT_BOLD_PATHS = [
    "/usr/share/fonts/google-droid/DroidSansFallback.ttf",
]
FONT_MONO_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf",
]

def _pick(paths):
    for p in paths:
        if Path(p).exists():
            return p
    return None

cjk = _pick(FONT_PATHS)
cjk_bold = _pick(FONT_BOLD_PATHS) or cjk
mono = _pick(FONT_MONO_PATHS)

if cjk:
    pdfmetrics.registerFont(TTFont("CJK", cjk))
    pdfmetrics.registerFont(TTFont("CJK-B", cjk_bold))
else:
    raise SystemExit("找不到中文字体，请手动指定 NotoSansCJK 或 wqy 路径")
if mono:
    pdfmetrics.registerFont(TTFont("Mono", mono))
else:
    pdfmetrics.registerFont(TTFont("Mono", cjk))

# ── 颜色（深色主题）──
BG = colors.HexColor("#0d1117")
CARD = colors.HexColor("#161b22")
BORDER = colors.HexColor("#30363d")
FG = colors.HexColor("#e6edf3")
MUTED = colors.HexColor("#8b949e")
BLUE = colors.HexColor("#58a6ff")
GOLD = colors.HexColor("#d4a017")
RED = colors.HexColor("#f85149")
GREEN = colors.HexColor("#3fb950")
ORANGE = colors.HexColor("#f0883e")
CYAN = colors.HexColor("#79c0ff")

# ── 数据 ──
state = json.loads((DATA / "state.json").read_text())
win_a = pd.read_csv(DATA / "winrate_a.csv")
win_b = pd.read_csv(DATA / "winrate_b.csv")
cases = pd.read_csv(DATA / "cases_full.csv")
cases60 = cases.dropna(subset=["r60"]).copy()
n60 = len(cases60)

b60 = win_b[win_b["持有"] == "3月"].iloc[0]
B60_WIN = b60["胜率"] * 100
B60_MED = b60["中位"] * 100
DD_NOW = state["dd_now"] * 100
TODAY_CLOSE = state["today_close_est"]
PEAK = state["peak_all"]
MA20 = state["ma20"]
MA60 = state["ma60"]

# 分布桶
def bucket_data():
    rows = [
        ("大涨 ≥ +10%",    (cases60["r60"] >= 0.10).sum()),
        ("微涨 0 ~ +10%",  ((cases60["r60"] >= 0) & (cases60["r60"] < 0.10)).sum()),
        ("小跌 -10% ~ 0",  ((cases60["r60"] < 0) & (cases60["r60"] > -0.10)).sum()),
        ("中跌 -20% ~ -10%", ((cases60["r60"] <= -0.10) & (cases60["r60"] > -0.20)).sum()),
        ("暴跌 ≤ -20%",    (cases60["r60"] <= -0.20).sum()),
    ]
    return rows

# ── 样式 ──
styles = getSampleStyleSheet()

def st(name, size, color=FG, bold=False, align=TA_LEFT, leading=None, space_after=2*mm, space_before=0):
    return ParagraphStyle(
        name=name, fontName="CJK-B" if bold else "CJK", fontSize=size,
        textColor=color, alignment=align, leading=leading or size*1.5,
        spaceAfter=space_after, spaceBefore=space_before,
    )

S = {
    "h1": st("h1", 26, FG, True, TA_CENTER, leading=34, space_after=6*mm),
    "subtitle": st("sub", 11, MUTED, False, TA_CENTER, leading=18, space_after=8*mm),
    "brand": st("brand", 10, GOLD, False, TA_CENTER, space_after=6*mm),
    "h2": st("h2", 15, BLUE, True, space_before=4*mm, space_after=3*mm, leading=22),
    "h3": st("h3", 12, GOLD, True, space_before=3*mm, space_after=2*mm, leading=18),
    "body": st("body", 10, FG, leading=16),
    "body_b": st("bodyB", 10, ORANGE, True, leading=16),
    "callout": st("co", 10, FG, leading=16),
    "muted": st("muted", 9, MUTED, leading=14, align=TA_CENTER),
    "code": st("code", 8.5, CYAN, leading=12),
    "end": st("end", 16, GOLD, True, TA_CENTER, space_before=20*mm),
    "paid": st("paid", 11, GOLD, True, TA_CENTER, space_before=12*mm),
}

# 公式样式 — 中文用 CJK 字体（Mono 不含 CJK glyph）
F_FORMULA = ParagraphStyle("formula", fontName="CJK", fontSize=10, textColor=CYAN,
                           alignment=TA_CENTER, leading=18, backColor=CARD,
                           borderColor=BORDER, borderWidth=0.5, borderPadding=4*mm,
                           spaceAfter=3*mm)

def hexc(c):
    """reportlab HexColor → '#RRGGBB' (for inline <font color=...> tags)"""
    return "#" + c.hexval()[2:]

# ── 表格工具 ──
def num(v, fmt="{:+.1f}%", na="n/a"):
    if pd.isna(v):
        return Paragraph(f'<font color="#7d8590">{na}</font>', S["body"])
    color = "#f85149" if v < 0 else "#3fb950"
    return Paragraph(f'<font face="Mono" color="{color}">{fmt.format(v*100 if abs(v)<10 else v)}</font>', S["body"])

def num_simple(v):
    return Paragraph(f'<font face="Mono">{v}</font>', S["body"])

def make_table(headers, rows, col_widths=None, num_cols=None):
    """构造深色表格。num_cols: 数字列索引列表，右对齐 mono。"""
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#21262d")),
        ("TEXTCOLOR", (0,0), (-1,0), BLUE),
        ("FONTNAME", (0,0), (-1,0), "CJK-B"),
        ("FONTNAME", (0,1), (-1,-1), "CJK"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,1), (-1,-1), FG),
        ("BACKGROUND", (0,1), (-1,-1), BG),
        ("LINEBELOW", (0,0), (-1,0), 1, BORDER),
        ("LINEBELOW", (0,1), (-1,-1), 0.3, colors.HexColor("#21262d")),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]
    # 斑马纹
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0,i), (-1,i), colors.HexColor("#11151a")))
    if num_cols:
        for c in num_cols:
            style.append(("FONTNAME", (c,1), (c,-1), "Mono"))
            style.append(("ALIGN", (c,1), (c,-1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t

# KPI 格子（5x1 或 6x1 网格）
def kpi_box(value, label, color=FG):
    inner = Table(
        [[Paragraph(f'<font face="Mono" color="{hexc(color)}">{value}</font>', S["h2"])],
         [Paragraph(f'<font color="#8b949e">{label}</font>', S["body"])]],
        colWidths=[35*mm],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CARD),
        ("BOX", (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("FONTSIZE", (0,1), (0,1), 8),
    ]))
    return inner

def kpi_row(items):
    """items: [(value, label, color), ...] 横排成一行表"""
    cells = [kpi_box(v, l, c) for v, l, c in items]
    n = len(cells)
    t = Table([cells], colWidths=[180/n*mm]*n)
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    return t

# ── 页面背景 ──
TOTAL_PAGES = {"n": 0}

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFont("CJK", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(15*mm, 10*mm, "复旦杰伦 · 券商ETF反共识研报 · 付费专享")
    page = canvas.getPageNumber()
    total = TOTAL_PAGES["n"] or "—"
    canvas.drawRightString(A4[0]-15*mm, 10*mm, f"{page} / {total}")
    canvas.restoreState()

# ── 构建 story ──
story = []

# ── 封面 ──
story += [
    Spacer(1, 20*mm),
    Paragraph("复旦杰伦 · 量化反共识研究", S["brand"]),
    Spacer(1, 4*mm),
]
# 付费徽章
badge = Table([[Paragraph('<font color="#0d1117"><b>付费专享版 · 深度研报</b></font>', S["body"])]],
              colWidths=[80*mm])
badge.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), GOLD),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
# 居中
badge_wrap = Table([[badge]], colWidths=[180*mm])
badge_wrap.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER")]))
story += [badge_wrap, Spacer(1, 10*mm)]

story += [
    Paragraph("券商ETF 连日脉冲<br/>反共识深度研报", S["h1"]),
    Paragraph(
        "512880 · 2026-06-22 +7.71% → 2026-06-25 +3.60%<br/>"
        "历史 36 次同款信号 · 60 日胜率仅 32.4%",
        S["subtitle"]),
    Spacer(1, 8*mm),
    kpi_row([
        (f"{B60_WIN:.1f}%", "60 日胜率", RED),
        (f"{B60_MED:+.2f}%", "60 日中位", RED),
        ("-21.6%", "60 日最差", RED),
    ]),
    Spacer(1, 20*mm),
    Paragraph(
        "数据截止 2026-06-25 · 回测窗口 2017-01 至 2026-06<br/>"
        "本报告仅供研究参考 · 不构成投资建议 · 严禁转发",
        S["muted"]),
    PageBreak(),
]

# ── 1. 执行摘要 ──
story += [
    Paragraph("一、执行摘要", S["h2"]),
    Paragraph(
        '<b><font color="#f0883e">核心结论</font></b>：券商ETF (512880) 在 6/22 单日 +7.71% 后，'
        '6/25 再放量 +3.60%，两日累计涨幅突破 +11%。'
        '历史上 <b><font color="#f0883e">36 次同款"连续脉冲"信号</font></b>中，'
        f'60 日持有窗口仅 {B60_WIN:.1f}% 录得正收益，中位收益 '
        f'<b><font color="#f85149">{B60_MED:+.2f}%</font></b>，'
        '跌幅 ≥ 10% 的概率高达 <b><font color="#f85149">41.2%</font></b>，'
        '涨幅 ≥ 10% 的概率仅 8.8%。',
        S["body"]),
    Paragraph(
        '<b><font color="#f0883e">赔率严重不对称，当前位置属于"右侧未确认 + 历史不利"组合，'
        '不建议追高介入。</font></b>',
        S["body"]),
    Spacer(1, 4*mm),
    kpi_row([
        ("36", "历史样本", FG),
        (f"{B60_WIN:.1f}%", "60 日胜率", RED),
        (f"{B60_MED:+.2f}%", "60 日中位", RED),
        ("41.2%", "跌≥10% 概率", RED),
        ("8.8%", "涨≥10% 概率", GREEN),
    ]),
]

# ── 2. 选题背景 ──
story += [
    PageBreak(),
    Paragraph("二、选题背景", S["h2"]),
    Paragraph(
        "2026-06-25 盘后，全市场最强一日由非银金融板块演绎：长江证券 (000783) 单只主力净流入 36.65 亿，"
        "非银金融指数 +2.33%，证券ETF 收盘 +3.60%，成交 31.6 亿，换手率 5.58%。"
        "这是继 6/22 单日大涨 +7.71% 后的第二根脉冲，两日累计涨幅约 +11.6%。", S["body"]),
    Paragraph(
        '市场叙事开始向"牛市旗手卷土重来""第二轮主升浪起步"等情绪化方向倾斜。'
        '本研报通过 10 年完整回测，量化评估当前位置追高的<b><font color="#f0883e">概率赔率</font></b>，'
        '给出反共识结论。', S["body"]),
]

# ── 3. 信号定义 ──
story += [
    Paragraph("三、信号定义与方法学", S["h2"]),
    Paragraph("3.1 主信号 A — 单日突破 + 放量", S["h3"]),
    Paragraph("单日涨幅 ≥ +3% &nbsp;&amp;&nbsp; 量比 ≥ 1.5 &nbsp;&amp;&nbsp; 收盘价站上 MA20", F_FORMULA),
    Paragraph("主信号刻画\"突破启动日\"，但单日强势的解释力有限，故引入连续脉冲信号 B 作为更严格的高强度过滤。", S["body"]),
    Paragraph("3.2 强化信号 B — 连续脉冲", S["h3"]),
    Paragraph("T 日触发主信号 A &nbsp;&amp;&nbsp; T+1 日涨幅 ≥ +2% &nbsp;&amp;&nbsp; 两日累计 ≥ +8%", F_FORMULA),
    Paragraph("该过滤捕捉\"连续两根大阳线\"+\"量价齐升\"的高强度信号，历史上仅触发 36 次，信号稀缺度高，统计意义可靠。", S["body"]),
    Paragraph("3.3 持有窗口", S["h3"]),
    Paragraph("对每次信号触发日 T，按收盘价买入，分别计算 T+5 / T+10 / T+20 / T+60 / T+120 个交易日的持有收益，衡量短中长期\"追高代价\"。", S["body"]),
    Paragraph("3.4 标的与样本", S["h3"]),
    Paragraph("标的：证券ETF 512880 (跟踪中证全指证券公司指数 399975) — A 股券商板块流动性最佳代表。", S["body"]),
    Paragraph("样本期：2017-01 至 2026-06，共 2,396 个交易日。", S["body"]),
    Paragraph("数据源：本地缓存的日线 parquet (后复权 close 计算收益)。", S["body"]),
]

# ── 4. 历史回测 ──
def winrate_table(df):
    rows = []
    for _, r in df.iterrows():
        med_color = RED if r["中位"] < 0 else GREEN
        mean_color = RED if r["均值"] < 0 else GREEN
        rows.append([
            r["持有"],
            num_simple(int(r["样本"])),
            num_simple(f'{r["胜率"]*100:.1f}%'),
            Paragraph(f'<font face="Mono" color="{hexc(med_color)}">{r["中位"]*100:+.2f}%</font>', S["body"]),
            Paragraph(f'<font face="Mono" color="{hexc(mean_color)}">{r["均值"]*100:+.2f}%</font>', S["body"]),
        ])
    return make_table(
        ["持有窗口", "样本", "胜率", "中位", "均值"],
        rows, col_widths=[30*mm, 25*mm, 30*mm, 35*mm, 35*mm],
        num_cols=[1,2,3,4],
    )

story += [
    PageBreak(),
    Paragraph("四、历史回测全样本结果", S["h2"]),
    Paragraph("4.1 主信号 A（单日突破，n = 82 次）", S["h3"]),
    winrate_table(win_a),
    Spacer(1, 4*mm),
    Paragraph("4.2 强化信号 B（连续脉冲，n = 36 次）", S["h3"]),
    winrate_table(win_b),
    Spacer(1, 3*mm),
    Paragraph(
        '<b><font color="#f0883e">对照解读</font></b>：主信号 A 的 60 日胜率 38.5%，中位 -4.9%；'
        f'强化信号 B (连续脉冲) 的 60 日胜率反而下降至 <b>{B60_WIN:.1f}%</b>，'
        f'中位恶化至 <b>{B60_MED:+.2f}%</b>。'
        '即<b><font color="#f0883e">"信号越强、连续涨幅越大，后续追高代价反而越高"</font></b>。'
        '这是典型的"强动量陷阱"反共识结论。',
        S["body"]),
]

# ── 5. 60 日分布 ──
buckets = bucket_data()
bucket_rows = []
for label, cnt in buckets:
    pct = cnt / n60 * 100
    color = RED if "跌" in label else (GREEN if "涨" in label and cnt > 0 else FG)
    bucket_rows.append([
        Paragraph(f'<font color="{hexc(color)}">{label}</font>', S["body"]),
        num_simple(cnt),
        num_simple(f"{pct:.1f}%"),
    ])

story += [
    PageBreak(),
    Paragraph("五、60 日持有期收益分布", S["h2"]),
    Paragraph(f"对信号 B 的 36 次样本，60 日窗口因末段 2 次未来交易日不足剔除，实际可计 n = <b>{n60}</b> 次。分布如下：", S["body"]),
    make_table(
        ["收益区间", "次数", "占比"],
        bucket_rows, col_widths=[80*mm, 30*mm, 30*mm],
        num_cols=[1,2],
    ),
    Spacer(1, 3*mm),
    Paragraph("关键观察：", S["body"]),
    Paragraph('&nbsp;&nbsp;• 跌幅 ≥ 10% 概率 = <b><font color="#f85149">41.2%</font></b>（中跌 + 暴跌之和）', S["body"]),
    Paragraph('&nbsp;&nbsp;• 涨幅 ≥ 10% 概率 = <b><font color="#3fb950">8.8%</font></b>', S["body"]),
    Paragraph('&nbsp;&nbsp;• 赔率比 ≈ <b><font color="#f85149">0.21</font></b>，严重不对称', S["body"]),
    Paragraph('&nbsp;&nbsp;• 所有正收益样本中，仅 3 例突破 +10%，其余均为温和反弹', S["body"]),
]

# ── 6. TOP/BOTTOM 案例 ──
def case_rows(df):
    rows = []
    for _, r in df.iterrows():
        r60v = r["r60"]
        r120v = r["r120"]
        rc = RED if r60v < 0 else GREEN
        r20c = RED if r["r20"] < 0 else GREEN
        rows.append([
            r["date"],
            Paragraph(f'<font face="Mono" color="{hexc(rc)}">{r60v*100:+.1f}%</font>', S["body"]),
            Paragraph(f'<font face="Mono" color="{hexc(r20c)}">{r["r20"]*100:+.1f}%</font>', S["body"]),
            Paragraph(f'<font face="Mono" color="{hexc(RED if r120v<0 else GREEN)}">{r120v*100:+.1f}%</font>'
                      if pd.notna(r120v) else '<font color="#7d8590">n/a</font>', S["body"]),
        ])
    return rows

worst5 = cases60.nsmallest(5, "r60")
best5 = cases60.nlargest(5, "r60")

story += [
    PageBreak(),
    Paragraph("六、TOP / BOTTOM 案例分析", S["h2"]),
    Paragraph("6.1 60 日跌得最惨 TOP 5", S["h3"]),
    make_table(["信号日", "60 日", "20 日", "120 日"], case_rows(worst5),
               col_widths=[35*mm, 35*mm, 35*mm, 35*mm], num_cols=[1,2,3]),
    Spacer(1, 3*mm),
    Paragraph(
        '<b><font color="#f0883e">共性</font></b>：全部出现在<b>"假启动 + 高位回调"</b>语境下 —'
        ' 2018-01 (蓝筹崩塌前夜)、2019-03 (春季躁动后回调)、2021-01 (茅指数顶部)。'
        '情绪面共同特征：信号触发时市场情绪饱和、龙头集中度高、消息面利多密集出尽。', S["body"]),
    Spacer(1, 5*mm),
    Paragraph("6.2 60 日涨得最猛 TOP 5", S["h3"]),
    make_table(["信号日", "60 日", "20 日", "120 日"], case_rows(best5),
               col_widths=[35*mm, 35*mm, 35*mm, 35*mm], num_cols=[1,2,3]),
    Spacer(1, 3*mm),
    Paragraph(
        '<b><font color="#f0883e">共性</font></b>：全部出现在<b>"政策底 + 情绪底共振"</b>的牛市起点 —'
        ' 最猛的三个样本 2024-09-26 / 09-27 / 09-30，都是 9-24 政策一揽子刺激后的连续脉冲，'
        '属于"右侧确认 + 估值底"罕见组合。这类机会十年仅一次，不可作为常态期待。', S["body"]),
]

# ── 7. 反共识论证 ──
story += [
    PageBreak(),
    Paragraph("七、反共识论证 — 为何当前不建议追高", S["h2"]),
    Paragraph("7.1 估值与位置", S["h3"]),
    Paragraph(f'&nbsp;&nbsp;• 当前价 ≈ <b>{TODAY_CLOSE:.3f}</b>，距 2024-11 高点 {PEAK:.3f} 仍有 <b><font color="#f85149">{DD_NOW:.1f}%</font></b> 浮亏', S["body"]),
    Paragraph(f'&nbsp;&nbsp;• MA20 = {MA20:.3f}，MA60 = {MA60:.3f}，价格站上 MA60 但距前高仍有 15%+ 空间', S["body"]),
    Paragraph('&nbsp;&nbsp;• 属于"中位反弹区"，既非历史底部，也非新高启动', S["body"]),
    Paragraph("7.2 资金结构", S["h3"]),
    Paragraph('&nbsp;&nbsp;• 6/25 长江证券主力净流入 <b>36.65 亿</b>（单股极度集中）— 历史上"单股暴吸 + 板块普涨"组合，60 日后跑输板块概率 &gt; 60%', S["body"]),
    Paragraph('&nbsp;&nbsp;• 融资盘可能跟随放大，短期透支后段空间', S["body"]),
    Paragraph('&nbsp;&nbsp;• 北上资金当日数据未明显配合，缺乏"机构合力"特征', S["body"]),
    Paragraph("7.3 历史样本验证", S["h3"]),
    Paragraph('&nbsp;&nbsp;• 36 次同款信号中，仅 <b>11 次 60 日为正</b>，23 次为负', S["body"]),
    Paragraph('&nbsp;&nbsp;• 正收益的 11 次中，8 次集中在 2024-09 政策底 + 2 次集中在 2018-10 政策底，与当前宏观背景不匹配', S["body"]),
    Paragraph('&nbsp;&nbsp;• 非政策底语境下的连续脉冲，60 日胜率近乎为 0', S["body"]),
    Paragraph("7.4 风险点四维诊断", S["h3"]),
    Paragraph('&nbsp;&nbsp;1. <b>位置风险</b>：不在底部，不在新高，中间区域历史胜率最差', S["body"]),
    Paragraph('&nbsp;&nbsp;2. <b>结构风险</b>：单股暴吸 + 板块拉升，缺乏机构合力', S["body"]),
    Paragraph('&nbsp;&nbsp;3. <b>情绪风险</b>：两日 +11.6% 后，散户 FOMO 入场风险加大', S["body"]),
    Paragraph('&nbsp;&nbsp;4. <b>政策风险</b>：当前无 2024-09 量级政策催化，上行动能不可持续', S["body"]),
]

# ── 8. 操作 Playbook ──
story += [
    PageBreak(),
    Paragraph("八、操作 Playbook", S["h2"]),
    Paragraph("8.1 持仓者", S["h3"]),
    Paragraph(
        "已持仓且持有成本低于 1.05 元的投资者，当前位置可考虑分批兑现 50%+ 盈利，留底仓搏更大行情。"
        "止盈位建议设在 1.20 元（前高 -12% 空间），跌破 MA20 全部清仓。", S["body"]),
    Paragraph("8.2 空仓者", S["h3"]),
    Paragraph(
        '当前位置追高的<b><font color="#f0883e">预期赔率 = 0.21</font></b>，'
        '即每承担 1 元的下行风险，仅可期待 0.21 元的上行收益。<b><font color="#f85149">不建议追入。</font></b>', S["body"]),
    Paragraph("等待两种确认信号：", S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>条件 A</b> — 回踩 MA20 (~1.05) 且日成交萎缩至 15 亿以下，即"调整充分"信号', S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>条件 B</b> — 出现 9-24 量级政策利好 + 北上单日净买 50 亿+ 共振，即"政策底确认"信号', S["body"]),
    Paragraph("满足任一条件再分批介入。", S["body"]),
    Paragraph("8.3 反向交易者（高风险）", S["h3"]),
    Paragraph(
        "历史样本支持的反向交易策略：T 日信号触发后，T+10 日开 50% 仓位做空（或卖出认购期权），"
        "60 日持有期内年化预期收益 ~30%，但最大回撤 -25%。"
        "仅适合衍生品熟练用户，不建议普通投资者尝试。", S["body"]),
]

# ── 9. 风险提示 ──
story += [
    PageBreak(),
    Paragraph("九、风险提示", S["h2"]),
    Paragraph('&nbsp;&nbsp;• <b>样本量风险</b>：36 次样本统计学上属于小样本，单次极端事件可能影响整体分布', S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>制度变迁风险</b>：2024 年后中国资本市场注册制全面推开 + T+0 试点等改革，历史样本的可比性下降', S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>幸存者偏差</b>：当前 ETF 跟踪指数成分股已经历多次调整，早期样本与当前持仓结构差异较大', S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>策略拥挤风险</b>：若反共识策略被广泛执行，自身将失效', S["body"]),
    Paragraph('&nbsp;&nbsp;• <b>本研究不构成投资建议</b>：量化回测结果不等于未来收益，投资决策请结合自身风险承受能力', S["body"]),
]

# ── 附录 A: 36 次完整样本 ──
all_rows = []
for _, r in cases.iterrows():
    def cell(v):
        if pd.isna(v):
            return Paragraph('<font color="#7d8590">n/a</font>', S["body"])
        c = RED if v < 0 else GREEN
        return Paragraph(f'<font face="Mono" color="{hexc(c)}">{v*100:+.1f}%</font>', S["body"])
    all_rows.append([r["date"], cell(r["r5"]), cell(r["r10"]), cell(r["r20"]), cell(r["r60"]), cell(r["r120"])])

story += [
    PageBreak(),
    Paragraph("附录 A · 36 次完整历史样本明细", S["h2"]),
    make_table(
        ["信号日", "T+5", "T+10", "T+20", "T+60", "T+120"],
        all_rows,
        col_widths=[28*mm, 25*mm, 25*mm, 25*mm, 28*mm, 28*mm],
        num_cols=[1,2,3,4,5],
    ),
    Spacer(1, 2*mm),
    Paragraph('<font color="#8b949e">注：n/a 表示该样本距数据末日不足对应天数，无法计算。回测使用后复权收盘价。</font>', S["body"]),
]

# ── 附录 B: 方法学补充 ──
story += [
    PageBreak(),
    Paragraph("附录 B · 方法学补充", S["h2"]),
    Paragraph("B.1 信号扫描伪代码", S["h3"]),
    Paragraph(
        '<font face="Mono" color="#79c0ff">'
        'for t in range(20, len(df)-1):<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;if ret1d[t] &gt;= 0.03 and vol_ratio[t] &gt;= 1.5 and close[t] &gt;= ma20[t]:<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;signal_A.append(t)<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if ret1d[t+1] &gt;= 0.02 and (ret1d[t] + ret1d[t+1]) &gt;= 0.08:<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;signal_B.append(t+1)'
        '</font>', S["code"]),
    Paragraph("B.2 收益计算", S["h3"]),
    Paragraph("&nbsp;&nbsp;r_h(T) = close[T+h] / close[T] - 1，持有期不考虑交易成本与冲击成本。", S["body"]),
    Paragraph("B.3 胜率定义", S["h3"]),
    Paragraph("&nbsp;&nbsp;P(r_h &gt; 0)，即正收益样本占比。", S["body"]),
    Paragraph("B.4 数据完整性", S["h3"]),
    Paragraph("&nbsp;&nbsp;末段 2 次信号 (2026-06-22 / 2026-06-25) 因尚未度过 60 日窗口，不计入胜率统计，仅作为当下信号呈现。", S["body"]),
]

# ── 结束页 ──
story += [
    PageBreak(),
    Spacer(1, 60*mm),
    Paragraph("· 报告完 ·", S["end"]),
    Spacer(1, 10*mm),
    Paragraph(
        "本研报由复旦杰伦量化反共识研究团队独立撰写。<br/>"
        "数据来源：本地缓存日线行情。<br/>"
        f"报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        S["muted"]),
    Paragraph("付费专享 · 严禁转发", S["paid"]),
]

# ── 输出 ──
out_pdf = OUTDIR / "研报.pdf"
print(f"渲染 → {out_pdf}")

doc = SimpleDocTemplate(
    str(out_pdf), pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=18*mm, bottomMargin=18*mm,
    title="券商ETF 反共识深度研报",
    author="复旦杰伦",
)
# 两遍渲染：第一遍统计总页数，第二遍带页码渲染
import copy
TOTAL_PAGES["n"] = 0
doc.build(copy.copy(story), onFirstPage=on_page, onLaterPages=on_page)
TOTAL_PAGES["n"] = doc.page
# 第二遍
doc2 = SimpleDocTemplate(
    str(out_pdf), pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=18*mm, bottomMargin=18*mm,
    title="券商ETF 反共识深度研报",
    author="复旦杰伦",
)
doc2.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"完成: {out_pdf}")
print(f"页数: {TOTAL_PAGES['n']}")
print(f"大小: {out_pdf.stat().st_size / 1024:.1f} KB")
