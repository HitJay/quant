#!/usr/bin/env python3
"""巴菲特框架分析茅台 — 7张小红书卡片 (momentum_viz风格)"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os

# ── Fonts ──────────────────────────────────────────
FP_BOLD = FontProperties(fname=os.path.expanduser("~/.local/share/fonts/NotoSansSC-Bold.otf"))
FP_REG = FontProperties(fname=os.path.expanduser("~/.local/share/fonts/NotoSansSC-Regular.otf"))

# ── Dark theme ─────────────────────────────────────
BG = "#1a1a2e"
GOLD = "#ffd700"
GREEN = "#e74c3c"   # A股红涨
RED = "#4ecca3"      # A股绿跌
AMBER = "#f0b866"
INDIGO = "#7fa5c4"
WHITE = "white"
GRAY = "#7f8c8d"
DIMGRAY = "#555555"
BORDER = "#333366"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "text.color": WHITE,
    "font.size": 11,
})

OUTDIR = "/mnt/d/vscode/quant/output/moutai-buffett"
os.makedirs(OUTDIR, exist_ok=True)

# ── Data ───────────────────────────────────────────
PRICE = 1467.75
MKT_CAP = PRICE * 1.256  # 亿
EPS = 65.66
PE = PRICE / EPS
IV_28 = 28 * EPS
MOS = (IV_28 - PRICE) / IV_28 * 100
IV_30 = 30 * EPS
IV_35 = 35 * EPS
ROE_AVG = 31.5
NPM_CAGR = 17.3
GROSS = 91.8
NET = 47.8
CASH_NP = 74.7
DEBT = 16.4
CUR = 5.09
QUICK = 3.85

years = ["2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"]
roe_vals = [24.4, 32.9, 34.5, 33.1, 31.4, 29.9, 30.3, 34.2, 36.0, 32.5]

# ── Helpers ────────────────────────────────────────
def page_tag(fig, n, total=7):
    fig.text(0.93, 0.015, f"{n}/{total}", ha="right", va="bottom",
             fontsize=10, color=DIMGRAY, fontproperties=FP_REG)

def title_text(ax, s, y=0.94):
    ax.text(0.5, y, s, ha="center", va="top", fontsize=20, fontweight="bold",
            color=WHITE, transform=ax.transAxes, fontproperties=FP_BOLD)

def subtitle_text(ax, s, y=0.88):
    ax.text(0.5, y, s, ha="center", va="top", fontsize=12,
            color=GRAY, transform=ax.transAxes, fontproperties=FP_REG)

def section_head(ax, x, y, s, color=AMBER):
    """Section heading with colored left accent bar"""
    ax.plot([x-0.02, x+0.015], [y, y], color=color, linewidth=3,
            transform=ax.transAxes, solid_capstyle='butt')
    body(ax, x+0.03, y, s, size=14, color=color, bold=True)

def body(ax, x, y, s, size=11, color=WHITE, bold=False):
    fp = FP_BOLD if bold else FP_REG
    ax.text(x, y, s, ha="left", va="top", fontsize=size, color=color,
            transform=ax.transAxes, fontproperties=fp)

def center(ax, x, y, s, size=14, color=WHITE, bold=False):
    fp = FP_BOLD if bold else FP_REG
    ax.text(x, y, s, ha="center", va="top", fontsize=size, color=color,
            transform=ax.transAxes, fontproperties=fp)

def bullet(ax, x, y, s, size=10, color=WHITE):
    body(ax, x, y, f"• {s}", size=size, color=color)

def save(fig, name):
    p = os.path.join(OUTDIR, name)
    fig.savefig(p, dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    return p

# ═══════════════════════════════════════════════════
# 0. COVER
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "巴菲特怎么看茅台？", y=0.90)
subtitle_text(ax, "用价值投资框架深度拆解 A 股之王", y=0.84)

# Hero number
center(ax, 0.5, 0.70, "10 年平均 ROE", size=14, color=GRAY)
center(ax, 0.5, 0.59, f"{ROE_AVG:.0f}%", size=68, color=GOLD, bold=True)
center(ax, 0.5, 0.44, "远超巴菲特 15% 门槛", size=13, color=GRAY)

# Sub metrics
for i, (lab, val, clr) in enumerate([
    ("市值", f"{(MKT_CAP/10000):.2f} 万亿", WHITE),
    ("PE", f"{PE:.1f}x", INDIGO),
    ("毛利率", f"{GROSS:.0f}%", GREEN),
]):
    x = 0.20 + i * 0.30
    center(ax, x, 0.34, lab, size=10, color=GRAY)
    center(ax, x, 0.29, val, size=22, color=clr, bold=True)

# CTA
center(ax, 0.5, 0.16, "专业 AI 量化研究员", size=16, color=AMBER, bold=True)
center(ax, 0.5, 0.12, "用巴菲特框架告诉你答案", size=12, color=GRAY)
center(ax, 0.5, 0.05, "贵州茅台 · 600519 · 2025.05.30", size=9, color=DIMGRAY)

page_tag(fig, 0)
save(fig, "00_cover.png")
print("0 cover")

# ═══════════════════════════════════════════════════
# 1. MOAT
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "护城河分析", y=0.95)
subtitle_text(ax, "品牌护城河 — 巴菲特五大护城河之首", y=0.89)

# Score
center(ax, 0.5, 0.83, "品牌壁垒：★★★★★", size=18, color=GOLD, bold=True)

sections = [
    (0.78, "品牌壁垒", [
        "800 年历史，国酒地位无可撼动",
        "商务宴请硬通货，社交货币属性",
        "消费者心智占领：白酒第一品牌",
    ]),
    (0.62, "定价权", [
        "20 年出厂价 268→1169 元，涨 4.4 倍",
        "提价 5-10% 对销量几乎无影响",
        f"毛利率 {GROSS:.1f}%，净利率 {NET:.1f}%",
    ]),
    (0.46, "稀缺性", [
        "茅台镇 7.5km² 核心产区不可复制",
        "年产量受限 ~5.7 万吨，长期供不应求",
        "库存越陈越值钱 — 反折旧特性",
    ]),
    (0.30, "趋势判断", [
        "护城河状态：宽且仍在拓宽",
        "消费升级 + 中产扩大 = 长期利好",
        "唯一软肋：政策（反腐），但历史恢复力强",
    ]),
]

for y_start, heading, lines in sections:
    body(ax, 0.08, y_start, heading, size=14, color=AMBER, bold=True)
    for j, line in enumerate(lines):
        bullet(ax, 0.10, y_start - 0.04 - j * 0.035, line, size=10)

# Key metric bar (safely below content)
for i, (lab, val, clr) in enumerate([
    ("毛利率", f"{GROSS:.0f}%", GREEN),
    ("净利率", f"{NET:.0f}%", GREEN),
    ("定价权", "极强", GOLD),
]):
    x = 0.18 + i * 0.32
    center(ax, x, 0.11, lab, size=9, color=GRAY)
    center(ax, x, 0.06, val, size=18, color=clr, bold=True)

page_tag(fig, 1)
save(fig, "01_moat.png")
print("1 moat")

# ═══════════════════════════════════════════════════
# 2. FINANCIALS
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "财务体检", y=0.95)
subtitle_text(ax, "Owner Earnings · ROIC · 现金质量", y=0.89)

# ROE chart
ax_bar = plt.axes([0.12, 0.60, 0.76, 0.18])
ax_bar.set_facecolor(BG)
colors = [GOLD if v >= 30 else INDIGO for v in roe_vals]
ax_bar.bar(range(len(years)), roe_vals, color=colors, width=0.55, edgecolor=BG)
ax_bar.axhline(y=15, color=RED, linestyle="--", linewidth=0.8)
ax_bar.text(9.3, 16, "15%", color=RED, fontsize=7, ha="right", fontproperties=FP_REG)
ax_bar.set_xticks(range(len(years)))
ax_bar.set_xticklabels(years, fontsize=7, color=GRAY, fontproperties=FP_REG)
ax_bar.set_ylim(0, 45)
ax_bar.tick_params(colors=GRAY, labelsize=7)
ax_bar.set_ylabel("ROE (%)", fontsize=9, color=GRAY, fontproperties=FP_REG)
for s in ax_bar.spines.values():
    s.set_color(BORDER)
    s.set_linewidth(0.5)

# Metrics
metrics = [
    ("10 年平均 ROE", f"{ROE_AVG:.1f}%", GOLD),
    ("净利润 10 年 CAGR", f"{NPM_CAGR:.1f}%", GOLD),
    ("毛利率", f"{GROSS:.1f}%", GREEN),
    ("净利率", f"{NET:.1f}%", WHITE),
    ("现金流 / 净利润", f"{CASH_NP:.0f}%", GREEN),
    ("资产负债率", f"{DEBT:.1f}%", GREEN),
    ("流动比率", f"{CUR:.1f}", GREEN),
    ("速动比率", f"{QUICK:.1f}", GREEN),
]
for i, (lab, val, clr) in enumerate(metrics):
    col, row = i % 2, i // 2
    x, y = 0.10 + col * 0.42, 0.54 - row * 0.055
    body(ax, x, y, lab, size=10, color=GRAY)
    body(ax, x + 0.30, y, val, size=11, color=clr, bold=True)

# Owner earnings
section_head(ax, 0.08, 0.22, "Owner Earnings 估算")
body(ax, 0.10, 0.16, "净利 823 亿 + 折旧≈30 亿 − 维护 capex≈20 亿", size=10)
body(ax, 0.10, 0.12, "≈ 830 亿 / 年 · 真实可支配利润", size=12, color=GOLD, bold=True)

center(ax, 0.5, 0.05, "「寻找 ROE>15%、低负债、高现金流的公司」— 巴菲特", size=9, color=GRAY)

page_tag(fig, 2)
save(fig, "02_financials.png")
print("2 financials")

# ═══════════════════════════════════════════════════
# 3. VALUATION
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "估值分析", y=0.95)
subtitle_text(ax, f"当前 PE {PE:.1f}x · 历史中枢 ~30x · 处于历史低位", y=0.89)

# Intrinsic value
body(ax, 0.08, 0.80, "内在价值估算 (EPS × PE)", size=14, color=AMBER, bold=True)

vals = [
    ("保守 (28x)", f"{IV_28:.0f} 元", f"安全边际 {MOS:.1f}%", GREEN),
    ("历史中枢 (30x)", f"{IV_30:.0f} 元",
     f"安全边际 {(IV_30-PRICE)/IV_30*100:.1f}%", INDIGO),
    ("乐观 (35x)", f"{IV_35:.0f} 元",
     f"上涨空间 {(IV_35/PRICE-1)*100:.1f}%", GOLD),
]
for i, (method, val, note, clr) in enumerate(vals):
    y = 0.73 - i * 0.07
    body(ax, 0.10, y, method, size=11, color=GRAY)
    body(ax, 0.32, y, val, size=14, color=clr, bold=True)
    body(ax, 0.52, y, note, size=11, color=WHITE)

# MOS bar
section_head(ax, 0.08, 0.50, f"安全边际: {MOS:.1f}%")

ax_mos = plt.axes([0.15, 0.42, 0.70, 0.03])
ax_mos.set_facecolor(BG)
ax_mos.barh([0], [MOS], color=GREEN, height=0.6)
ax_mos.barh([0], [20], color=GRAY, height=0.6, alpha=0.2)
ax_mos.set_xlim(0, 40)
ax_mos.axis("off")
body(ax, 0.08, 0.39, "巴菲特要求 20-30% — 当前刚好达标", size=10, color=GRAY)

# Assumptions
section_head(ax, 0.08, 0.33, "核心假设")
for i, a in enumerate([
    "未来 5 年净利润增速: 10-12%（保守估计）",
    "出厂价仍有提价空间（当前 1169 元）",
    "直销比例持续提升（2025 年 ~47%）",
    "估值中枢 PE 25-35x 区间波动",
]):
    bullet(ax, 0.10, 0.27 - i * 0.04, a, size=10)

# PE range
body(ax, 0.08, 0.12, "近 5 年 PE 区间: 20x (低估) ~ 55x (高估)", size=10)
body(ax, 0.08, 0.06, f"当前 {PE:.1f}x — 处于历史低位区间", size=11, color=GREEN, bold=True)

page_tag(fig, 3)
save(fig, "03_valuation.png")
print("3 valuation")

# ═══════════════════════════════════════════════════
# 4. QUICK FILTER
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "8 题快速筛选", y=0.95)
subtitle_text(ax, "巴菲特 2 分钟判断法：全部通过", y=0.89)

checks = [
    ("能力圈", "一句话讲清怎么赚钱？", "卖高端白酒，低成本高售价"),
    ("持久性", "10 年后还在且更强？", "800 年品牌，不可替代"),
    ("护城河", "竞争者砸钱能复制吗？", "品牌+产区双壁垒，不能"),
    ("定价权", "提价 5-10% 丢客户？", "几乎不会，需求刚性"),
    ("盈利质量", "利润真实变现金？", f"现金流/净利 {CASH_NP:.0f}%"),
    ("债务安全", "营收 −30% 能存活？", f"负债率仅 {DEBT:.1f}%"),
    ("管理层", "正视问题不隐瞒？", "国企治理，整体稳健"),
    ("价格", "安全边际够吗？", f"当前 {MOS:.1f}%，刚达标"),
]

for i, (dim, q, detail) in enumerate(checks):
    y = 0.82 - i * 0.09
    body(ax, 0.08, y, f"✓  {q}", size=10, color=GREEN, bold=True)
    body(ax, 0.12, y - 0.025, detail, size=8, color=GRAY)

center(ax, 0.5, 0.05, "8/8 全部通过 — 巴菲特会认真考虑这家公司", size=14, color=GREEN, bold=True)

page_tag(fig, 4)
save(fig, "04_filter.png")
print("4 filter")

# ═══════════════════════════════════════════════════
# 5. RISKS
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "风险清单", y=0.95)
subtitle_text(ax, "巴菲特担心的三类风险 + 卖出条件检查", y=0.89)

risk_groups = [
    (0.82, "结构性风险", RED, [
        ("政策风险（最大）", "反腐 / 消费税 → 历史最大回撤 60%+"),
        ("消费趋势变化", "年轻人白酒消费下降，但高端场景刚性"),
        ("替代品威胁", "洋酒 / 精酿分流，但商务宴请不可替代"),
    ]),
    (0.56, "财务风险", GREEN, [
        ("杠杆", f"负债率 {DEBT:.1f}%，几乎零风险"),
        ("现金流", f"经营现金流 / 净利 {CASH_NP:.0f}%，质量高"),
        ("存货", "越陈越值钱，反折旧特性"),
    ]),
    (0.30, "行为风险", GOLD, [
        ("过度扩张", "历史上试水红酒 / 啤酒未成功，规模不大"),
        ("估值泡沫", "PE 曾达 73x（2021），追高是最大个人风险"),
        ("确认偏误", "「茅台永远涨」是危险思维定式"),
    ]),
]

for y_start, heading, clr, items in risk_groups:
    body(ax, 0.08, y_start, heading, size=13, color=clr, bold=True)
    for j, (t, d) in enumerate(items):
        y = y_start - 0.035 - j * 0.038
        body(ax, 0.10, y, f"• {t}", size=9, color=clr, bold=True)
        body(ax, 0.38, y, d, size=8, color=GRAY)

# Sell criteria
body(ax, 0.08, 0.14, "卖出条件检查", size=13, color=INDIGO, bold=True)
for i, (cond, status) in enumerate([
    ("价格严重高估 (PE>50x)", "否"),
    ("护城河根本破坏", "否"),
    ("管理层诚信问题", "无"),
    ("有更好的机会", "视情况"),
]):
    x = 0.10 + (i % 2) * 0.42
    y = 0.09 - (i // 2) * 0.04
    body(ax, x, y, f"{cond}: ", size=9, color=GRAY)
    body(ax, x + 0.26, y, status, size=9, color=GREEN, bold=True)

page_tag(fig, 5)
save(fig, "05_risks.png")
print("5 risks")

# ═══════════════════════════════════════════════════
# 6. VERDICT
# ═══════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")

title_text(ax, "巴菲特式最终裁决", y=0.95)
subtitle_text(ax, "「以合理价格买入伟大公司」", y=0.89)

# Verdict
center(ax, 0.5, 0.80, "结论：可买入（分批建仓）", size=22, color=GREEN, bold=True)
center(ax, 0.5, 0.75, f"PE {PE:.1f}x · 安全边际 {MOS:.1f}% · 合理偏低估", size=12, color=WHITE)

# Scorecard
section_head(ax, 0.08, 0.67, "评分卡")

ratings = [
    ("商业质量", "★★★★★", "品牌+定价权+稀缺性", GOLD),
    ("管理水平", "★★★★☆", "国企稳健，资本配置中上", GOLD),
    ("财务健康", "★★★★★", f"ROE {ROE_AVG:.0f}%+ 零负债", GREEN),
    ("成长性",   "★★★★☆", f"10年CAGR {NPM_CAGR:.0f}%", WHITE),
    ("估值",     "★★★★☆", f"PE {PE:.1f}x 低于历史中枢", INDIGO),
]
for i, (lab, stars, detail, clr) in enumerate(ratings):
    y = 0.60 - i * 0.07
    body(ax, 0.10, y, lab, size=12, color=GRAY)
    body(ax, 0.30, y, stars, size=13, color=clr, bold=True)
    body(ax, 0.48, y, detail, size=10, color=WHITE)

# Monitoring
section_head(ax, 0.08, 0.28, "每季度监控指标", color=INDIGO)
for i, m in enumerate([
    "直销比例 (当前 47%) 是否持续提升",
    "批价与出厂价价差 (警戒 <200 元)",
    "ROE 是否维持 25%+",
    "PE 突破 40x → 减仓; 跌破 18x → 加仓",
]):
    bullet(ax, 0.10, 0.23 - i * 0.04, m, size=10)

# Disclaimer + CTA
center(ax, 0.5, 0.06, "关注我，解锁更多深度分析  ·  复旦杰伦", size=12, color=AMBER, bold=True)
center(ax, 0.5, 0.02, "以上为学术展示，不构成投资建议。投资有风险，入市需谨慎。", size=8, color=DIMGRAY)

page_tag(fig, 6)
save(fig, "06_verdict.png")
print("6 verdict")

# ── Summary ────────────────────────────────────────
print(f"\n7 cards → {OUTDIR}/")
for f in sorted(os.listdir(OUTDIR)):
    if f.endswith(".png"):
        print(f"  {f}  ({os.path.getsize(os.path.join(OUTDIR, f))//1024} KB)")
