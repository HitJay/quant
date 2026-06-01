#!/usr/bin/env python3
"""巴菲特分析茅台 — HTML/CSS Flexbox 自动排版 7 张卡片"""

import os

PRICE = 1467.75
MKT_CAP = PRICE * 1.256 / 10000  # 万亿
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

OUT = "/mnt/d/vscode/quant/output/moutai-buffett"
os.makedirs(OUT, exist_ok=True)

CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0d1117; display:flex; flex-direction:column; align-items:center; gap:40px; padding:40px 0; }
.card {
  width:600px; height:800px; background:#161b22; border-radius:16px;
  display:flex; flex-direction:column; justify-content:space-between; padding:36px 32px 28px;
  font-family:'Noto Sans SC',sans-serif; color:#c9d1d9; position:relative;
  overflow:hidden;
}
.card .page { position:absolute; bottom:12px; right:16px; font-size:13px; color:#484f58; }
.card h2 { font-size:36px; color:#c9d1d9; text-align:center; margin-bottom:6px; font-weight:700; }
.card h3 { font-size:20px; color:#8b949e; text-align:center; margin-bottom:18px; font-weight:400; }
.card .hero-num { font-size:120px; color:#f0b866; text-align:center; font-weight:700; line-height:1; margin:8px 0; }
.card .hero-label { font-size:18px; color:#8b949e; text-align:center; margin-bottom:4px; }
.card .hero-sub { font-size:18px; color:#8b949e; text-align:center; margin-bottom:16px; }
.card .kpi-row { display:flex; justify-content:space-around; margin:12px 0; }
.card .kpi { text-align:center; }
.card .kpi .val { font-size:36px; font-weight:700; }
.card .kpi .lab { font-size:15px; color:#8b949e; margin-top:2px; }
.card .section { margin-top:18px; }
.card .section-title { font-size:22px; font-weight:700; margin-bottom:8px; display:flex; align-items:center; gap:8px; }
.card .section-title .bar { width:5px; height:24px; border-radius:2px; flex-shrink:0; }
.card .section-body { font-size:17px; line-height:1.7; color:#c9d1d9; padding-left:12px; }
.card .section-body .item { margin-bottom:2px; }
.card .section-body .sub { font-size:14px; color:#8b949e; margin-left:12px; }
.card .tag { display:inline-block; padding:4px 14px; border-radius:12px; font-size:15px; font-weight:600; }
.card .tag-green { background:#0d3320; color:#3fb950; }
.card .tag-gold { background:#2d1f00; color:#f0b866; }
.card .tag-blue { background:#0d1f33; color:#58a6ff; }
.card .tag-red { background:#330d0d; color:#f85149; }
.card .big-verdict { text-align:center; font-size:38px; font-weight:700; margin:8px 0; }
.card .cta { text-align:center; color:#f0b866; font-size:18px; font-weight:600; }
.card .disclaimer { text-align:center; font-size:13px; color:#484f58; margin-top:4px; }
.card .score-row { display:flex; justify-content:space-between; align-items:center; padding:4px 0; font-size:18px; }
.card .score-row .stars { font-size:18px; }
.card .score-row .detail { font-size:15px; color:#8b949e; }
.card .check-item { display:flex; align-items:flex-start; gap:6px; margin-bottom:2px; }
.card .check-item .mark { color:#3fb950; font-weight:700; font-size:20px; width:16px; flex-shrink:0; }
.card .check-item .q { font-size:17px; }
.card .check-item .d { font-size:14px; color:#8b949e; }
.card .risk-group { margin-bottom:10px; }
.card .risk-group .rg-title { font-size:18px; font-weight:700; margin-bottom:4px; }
.card .risk-item { display:flex; gap:8px; margin-bottom:2px; }
.card .risk-item .ri-label { font-size:15px; font-weight:600; white-space:nowrap; }
.card .risk-item .ri-desc { font-size:14px; color:#8b949e; }
.card .sell-row { display:flex; flex-wrap:wrap; gap:6px 24px; font-size:15px; }
.card .sell-row .ok { color:#3fb950; font-weight:600; }
.bar-amber { background:#f0b866; }
.bar-green { background:#3fb950; }
.bar-blue { background:#58a6ff; }
.bar-indigo { background:#7fa5c4; }
.bar-red { background:#f85149; }
.text-green { color:#3fb950; }
.text-gold { color:#f0b866; }
.text-blue { color:#58a6ff; }
.text-amber { color:#f0b866; }
.text-indigo { color:#7fa5c4; }
"""

def card(n, title, subtitle, body_html, css_extra=""):
    return f"""<div class="card">
  <div class="page">{n}/7</div>
  <h2>{title}</h2>
  <h3>{subtitle}</h3>
  {body_html}
</div>"""

cards_html = []

# ── Card 0: Cover ──
cards_html.append(card(0, "巴菲特怎么看茅台？", "用价值投资框架深度拆解 A 股之王", f"""
  <div class="hero-label">10 年平均 ROE</div>
  <div class="hero-num">{ROE_AVG:.0f}%</div>
  <div class="hero-sub">远超巴菲特 15% 门槛</div>
  <div class="kpi-row">
    <div class="kpi"><div class="val text-indigo">{MKT_CAP:.2f}万亿</div><div class="lab">市值</div></div>
    <div class="kpi"><div class="val text-blue">{PE:.1f}x</div><div class="lab">PE</div></div>
    <div class="kpi"><div class="val text-green">{GROSS:.0f}%</div><div class="lab">毛利率</div></div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="val text-gold">{ROE_AVG:.0f}%</div><div class="lab">10年ROE均值</div></div>
    <div class="kpi"><div class="val text-green">{NET:.0f}%</div><div class="lab">净利率</div></div>
    <div class="kpi"><div class="val text-green">{DEBT:.1f}%</div><div class="lab">负债率</div></div>
  </div>
  <div style="text-align:center;margin:12px 0">
    <span class="tag tag-green">8/8 巴菲特筛选通过</span>
    <span class="tag tag-gold" style="margin-left:8px">护城河 ★★★★★</span>
  </div>
  <div style="text-align:center;font-size:14px;color:#8b949e;margin:8px 0">
    净利润 10 年 CAGR <span style="color:#f0b866;font-weight:700">{NPM_CAGR:.1f}%</span> · 现金流/净利 <span style="color:#3fb950;font-weight:700">{CASH_NP:.0f}%</span>
  </div>
  <div class="cta">专业 AI 量化研究员 · 用巴菲特框架告诉你答案</div>
  <div class="disclaimer">贵州茅台 · 600519 · 2025.05.30</div>
"""))

# ── Card 1: Moat ──
moat_items = [
    ("品牌壁垒", "amber", [
        "800 年历史，国酒地位无可撼动",
        "商务宴请硬通货，社交货币属性",
        "消费者心智占领：白酒第一品牌",
    ]),
    ("定价权", "amber", [
        "20 年出厂价 268→1169 元，涨 4.4 倍",
        "提价 5-10% 对销量几乎无影响",
        f"毛利率 {GROSS:.1f}%，净利率 {NET:.1f}%",
    ]),
    ("稀缺性", "amber", [
        "茅台镇 7.5km² 核心产区不可复制",
        "年产量受限 ~5.7 万吨，长期供不应求",
        "库存越陈越值钱 — 反折旧特性",
    ]),
    ("趋势判断", "amber", [
        "护城河状态：宽且仍在拓宽",
        "消费升级 + 中产扩大 = 长期利好",
        "唯一软肋：政策（反腐），但历史恢复力强",
    ]),
]
moat_html = '<div style="text-align:center;margin-bottom:12px"><span class="tag tag-gold">品牌护城河 · 不可复制 ★★★★★</span></div>'
for title, color, lines in moat_items:
    moat_html += f'<div class="section"><div class="section-title"><span class="bar bar-{color}"></span>{title}</div><div class="section-body">'
    for l in lines:
        moat_html += f'<div class="item">• {l}</div>'
    moat_html += '</div></div>'
moat_html += f"""<div class="kpi-row" style="margin-top:auto">
  <div class="kpi"><div class="val text-green">{GROSS:.0f}%</div><div class="lab">毛利率</div></div>
  <div class="kpi"><div class="val text-green">{NET:.0f}%</div><div class="lab">净利率</div></div>
  <div class="kpi"><div class="val text-gold">极强</div><div class="lab">定价权</div></div>
</div>"""
cards_html.append(card(1, "护城河分析", "品牌护城河 — 巴菲特五大护城河之首", moat_html))

# ── Card 2: Financials ──
fin_items = [
    ("10 年平均 ROE", f"{ROE_AVG:.1f}%", "#f0b866"),
    ("净利润 10 年 CAGR", f"{NPM_CAGR:.1f}%", "#f0b866"),
    ("毛利率", f"{GROSS:.1f}%", "#3fb950"),
    ("净利率", f"{NET:.1f}%", "#c9d1d9"),
    ("现金流 / 净利润", f"{CASH_NP:.0f}%", "#3fb950"),
    ("资产负债率", f"{DEBT:.1f}%", "#3fb950"),
    ("流动比率", f"{CUR:.1f}", "#3fb950"),
    ("速动比率", f"{QUICK:.1f}", "#3fb950"),
]
fin_html = '<div style="display:flex;flex-wrap:wrap;gap:4px 0;margin-bottom:14px">'
for i, (lab, val, clr) in enumerate(fin_items):
    fin_html += f'<div style="width:50%;display:flex;justify-content:space-between;padding:2px 8px;font-size:15px"><span style="color:#8b949e">{lab}</span><span style="color:{clr};font-weight:700">{val}</span></div>'
fin_html += '</div>'
fin_html += f"""<div class="section"><div class="section-title"><span class="bar bar-amber"></span>Owner Earnings 估算</div>
  <div class="section-body">
    <div class="item">净利 823 亿 + 折旧≈30 亿 − 维护 capex≈20 亿</div>
    <div class="item" style="color:#f0b866;font-weight:600;font-size:16px">≈ 830 亿 / 年 · 真实可支配利润</div>
  </div></div>
  <div style="margin-top:auto;font-size:13px;color:#8b949e;text-align:center">「寻找 ROE>15%、低负债、高现金流的公司」— 巴菲特</div>"""
cards_html.append(card(2, "财务体检", "Owner Earnings · ROIC · 现金质量", fin_html))

# ── Card 3: Valuation ──
val_html = '<div class="section"><div class="section-title"><span class="bar bar-amber"></span>内在价值估算</div><div class="section-body">'
for method, val, note, clr in [
    ("保守 (28x)", f"{IV_28:.0f} 元", f"安全边际 {MOS:.1f}%", "#3fb950"),
    ("历史中枢 (30x)", f"{IV_30:.0f} 元", f"安全边际 {(IV_30-PRICE)/IV_30*100:.1f}%", "#58a6ff"),
    ("乐观 (35x)", f"{IV_35:.0f} 元", f"上涨空间 {(IV_35/PRICE-1)*100:.1f}%", "#f0b866"),
]:
    val_html += f'<div class="score-row"><span style="color:#8b949e;font-size:15px">{method}</span><span style="color:{clr};font-weight:700;font-size:18px">{val}</span><span style="font-size:15px">{note}</span></div>'
val_html += '</div></div>'

val_html += f"""<div class="section"><div class="section-title"><span class="bar bar-amber"></span>安全边际: {MOS:.1f}%</div>
  <div style="background:#21262d;border-radius:6px;height:8px;margin:4px 0">
    <div style="background:#3fb950;height:8px;border-radius:6px;width:{MOS/40*100:.0f}%"></div>
  </div>
  <div style="font-size:10px;color:#8b949e">巴菲特要求 20-30% — 当前刚好达标</div>
</div>"""

val_html += '<div class="section"><div class="section-title"><span class="bar bar-amber"></span>核心假设</div><div class="section-body">'
for a in ["未来 5 年净利润增速: 10-12%（保守估计）", "出厂价仍有提价空间（当前 1169 元）",
           "直销比例持续提升（2025 年 ~47%）", "估值中枢 PE 25-35x 区间波动"]:
    val_html += f'<div class="item">• {a}</div>'
val_html += '</div></div>'

val_html += f"""<div style="margin-top:auto">
  <div style="font-size:15px;color:#8b949e">近 5 年 PE: 20x (低估) ~ 55x (高估)</div>
  <div style="font-size:16px;color:#3fb950;font-weight:600;margin-top:2px">当前 {PE:.1f}x — 处于历史低位区间</div>
</div>"""
cards_html.append(card(3, "估值分析", f"当前 PE {PE:.1f}x · 历史中枢 ~30x · 处于历史低位区间", val_html))

# ── Card 4: Quick Filter ──
filter_html = '<div style="display:flex;flex-direction:column;gap:2px">'
for dim, q, detail in [
    ("能力圈", "一句话讲清怎么赚钱？", "卖高端白酒，低成本高售价"),
    ("持久性", "10 年后还在且更强？", "800 年品牌，不可替代"),
    ("护城河", "竞争者砸钱能复制吗？", "品牌+产区双壁垒，不能"),
    ("定价权", "提价 5-10% 丢客户？", "几乎不会，需求刚性"),
    ("盈利质量", "利润真实变现金？", f"现金流/净利 {CASH_NP:.0f}%"),
    ("债务安全", "营收 −30% 能存活？", f"负债率仅 {DEBT:.1f}%"),
    ("管理层", "正视问题不隐瞒？", "国企治理，整体稳健"),
    ("价格", "安全边际够吗？", f"当前 {MOS:.1f}%，刚达标"),
]:
    filter_html += f'<div class="check-item"><span class="mark">✓</span><div><div class="q">{q}</div><div class="d">{detail}</div></div></div>'
filter_html += '</div>'
filter_html += '<div style="text-align:center;padding:6px 8px;background:#0d3320;border-radius:8px;color:#3fb950;font-weight:600;font-size:18px">8/8 全部通过 — 巴菲特会认真考虑这家公司</div>'
cards_html.append(card(4, "8 题快速筛选", "巴菲特 2 分钟判断法：全部通过", filter_html))

# ── Card 5: Risks ──
risk_html = ''
for title, clr, items in [
    ("结构性风险", "#f85149", [
        ("政策风险（最大）", "反腐 / 消费税 → 历史最大回撤 60%+"),
        ("消费趋势变化", "年轻人白酒消费下降，但高端场景刚性"),
        ("替代品威胁", "洋酒 / 精酿分流，但商务宴请不可替代"),
    ]),
    ("财务风险", "#3fb950", [
        ("杠杆", f"负债率 {DEBT:.1f}%，几乎零风险"),
        ("现金流", f"经营现金流 / 净利 {CASH_NP:.0f}%，质量高"),
        ("存货", "越陈越值钱，反折旧特性"),
    ]),
    ("行为风险", "#f0b866", [
        ("过度扩张", "历史上试水红酒 / 啤酒未成功，规模不大"),
        ("估值泡沫", "PE 曾达 73x（2021），追高是最大个人风险"),
        ("确认偏误", "「茅台永远涨」是危险思维定式"),
    ]),
]:
    risk_html += f'<div class="risk-group"><div class="rg-title" style="color:{clr}">{title}</div>'
    for t, d in items:
        risk_html += f'<div class="risk-item"><span class="ri-label" style="color:{clr}">• {t}</span><span class="ri-desc">{d}</span></div>'
    risk_html += '</div>'

risk_html += '<div class="section"><div class="section-title"><span class="bar bar-blue"></span>卖出条件检查</div>'
risk_html += '<div class="sell-row">'
for cond, status in [("价格严重高估 (PE>50x)", "否"), ("护城河根本破坏", "否"),
                      ("管理层诚信问题", "无"), ("有更好的机会", "视情况")]:
    risk_html += f'<span>{cond}: <span class="ok">{status}</span></span>'
risk_html += '</div></div>'
cards_html.append(card(5, "风险清单", "巴菲特担心的三类风险 + 卖出条件检查", risk_html))

# ── Card 6: Verdict ──
verdict_html = f"""<div class="big-verdict text-green">结论：可买入（分批建仓）</div>
<div style="text-align:center;font-size:16px;margin-bottom:14px">PE {PE:.1f}x · 安全边际 {MOS:.1f}% · 合理偏低估</div>"""

verdict_html += '<div class="section"><div class="section-title"><span class="bar bar-amber"></span>评分卡</div>'
for lab, stars, detail, clr in [
    ("商业质量", "★★★★★", "品牌+定价权+稀缺性", "#f0b866"),
    ("管理水平", "★★★★☆", "国企稳健，资本配置中上", "#f0b866"),
    ("财务健康", "★★★★★", f"ROE {ROE_AVG:.0f}%+ 零负债", "#3fb950"),
    ("成长性",   "★★★★☆", f"10年CAGR {NPM_CAGR:.0f}%", "#c9d1d9"),
    ("估值",     "★★★★☆", f"PE {PE:.1f}x 低于历史中枢", "#58a6ff"),
]:
    verdict_html += f'<div class="score-row"><span style="color:#8b949e;font-size:16px">{lab}</span><span class="stars" style="color:{clr}">{stars}</span><span class="detail">{detail}</span></div>'
verdict_html += '</div>'

verdict_html += '<div class="section"><div class="section-title"><span class="bar bar-indigo"></span>每季度监控指标</div><div class="section-body">'
for m in ["直销比例 (当前 47%) 是否持续提升", "批价与出厂价价差 (警戒 <200 元)",
           "ROE 是否维持 25%+", "PE 突破 40x → 减仓; 跌破 18x → 加仓"]:
    verdict_html += f'<div class="item">• {m}</div>'
verdict_html += '</div></div>'

verdict_html += '<div class="cta" style="margin-top:auto">关注我，解锁更多深度分析 · 复旦杰伦</div>'
verdict_html += '<div class="disclaimer">以上为学术展示，不构成投资建议。投资有风险，入市需谨慎。</div>'
cards_html.append(card(6, "巴菲特式最终裁决", "「以合理价格买入伟大公司」", verdict_html))

# ── Build HTML ──
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
{"".join(cards_html)}
</body></html>"""

path = os.path.join(OUT, "buffett_moutai.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(html)

fsize = os.path.getsize(path) / 1024
print(f"✅ {path} ({fsize:.0f} KB)")
print("   浏览器打开 → 逐张截图 → 发布小红书")
