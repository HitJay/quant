#!/usr/bin/env python3
"""科技股崩盘风险分析 — 小红书 7 张卡片"""

import os

OUT = "/workspace/output/tech-crash-risk"
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
.text-red { color:#f85149; }
"""


def card(n, title, subtitle, body_html):
    return f"""<div class="card">
  <div class="page">{n}/7</div>
  <h2>{title}</h2>
  <h3>{subtitle}</h3>
  {body_html}
</div>"""


cards_html = []

# ── Card 0: Cover ──
cards_html.append(card(0, "科技股要崩盘？", "美股暴跌下的深度风险分析", """
  <div class="hero-label">席勒 PE（百年极值）</div>
  <div class="hero-num text-red">42.3x</div>
  <div class="hero-sub">距离 2000 年互联网泡沫仅一步之遥</div>
  <div class="kpi-row">
    <div class="kpi"><div class="val text-indigo">4万亿</div><div class="lab">英伟达市值</div></div>
    <div class="kpi"><div class="val text-blue">42x</div><div class="lab">纳指 100 PE</div></div>
    <div class="kpi"><div class="val text-green">25%+</div><div class="lab">科技股利润率</div></div>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="val text-red">-10%</div><div class="lab">6.5 费城半导体</div></div>
    <div class="kpi"><div class="val text-red">-6.2%</div><div class="lab">英伟达单日</div></div>
    <div class="kpi"><div class="val text-gold">1.1万亿</div><div class="lab">单日蒸发</div></div>
  </div>
  <div style="text-align:center;margin:12px 0">
    <span class="tag tag-red">高危预警信号</span>
    <span class="tag tag-blue" style="margin-left:8px">但非全面崩盘</span>
  </div>
  <div style="text-align:center;font-size:14px;color:#8b949e;margin:8px 0">
    数据来源：标普 500、纳指 100、彭博、财联社 · 2025.06.06
  </div>
  <div class="cta">7张图讲清楚科技股是否要崩盘</div>
  <div class="disclaimer">本文为市场分析，不构成投资建议</div>
"""))

# ── Card 1: 暴跌复盘 ──
crash_items = [
    ("导火索", "red", [
        "6.5 非农就业大超预期：17.2万 vs 预期 8万",
        "美联储降息预期彻底破灭，加息概率飙升至 70%",
        "美债收益率大幅走高，风险资产全线下挫",
    ]),
    ("芯片股重灾", "red", [
        "费城半导体单日暴跌 -10.6%（2020.3 以来最惨）",
        "博通先杀跌：Q3 芯片指引 160 亿低于预期 172 亿",
        "英伟达 -6.2%，美光 -13%，AMD -11%",
    ]),
    ("流动性背景", "amber", [
        "5.31-6.5 纳指连涨 9 周，积累大量获利盘",
        "SpaceX 上市虹吸效应，流动性提前出逃",
        "中东局势持续紧张，能源价格反弹推升通胀",
    ]),
]
crash_html = '<div style="text-align:center;margin-bottom:12px"><span class="tag tag-red">6.5 单日暴跌全复盘</span></div>'
for title, color, lines in crash_items:
    crash_html += f'<div class="section"><div class="section-title"><span class="bar bar-{color}"></span>{title}</div><div class="section-body">'
    for l in lines:
        crash_html += f'<div class="item">• {l}</div>'
    crash_html += '</div></div>'
crash_html += f"""<div class="kpi-row" style="margin-top:auto">
  <div class="kpi"><div class="val text-red">-4.2%</div><div class="lab">纳指跌幅</div></div>
  <div class="kpi"><div class="val text-red">-2.6%</div><div class="lab">标普跌幅</div></div>
  <div class="kpi"><div class="val text-red">-10.6%</div><div class="lab">半导体跌幅</div></div>
</div>"""
cards_html.append(card(1, "单日暴跌复盘", "非农超预期 + 获利盘出逃", crash_html))

# ── Card 2: 泡沫指标 ──
bubble_items = [
    ("估值极度高估", "red", [
        "席勒 CAPE：42.3x，仅次于 1929 大萧条、2000 科网泡沫",
        "科技股相对大盘溢价 1.34x，资金高度拥挤",
        "科创 50 市盈率 173x，超过 2000 年纳斯达克 85-120x",
    ]),
    ("资本开支泡沫", "amber", [
        "AI 资本开支增速远超 1999-2000 科网泡沫时期",
        "科技投资占 GDP 3.3%，超过互联网泡沫时期 2.6%",
        "美国银行预测：2030 年 AI 资本开支达 1.2 万亿美元",
    ]),
    ("市场高度集中", "amber", [
        "前 5 大公司占标普 500 权重 30%，50 年极值",
        "AI 相关企业占前十大市值 8/10，主题过于集中",
        "英伟达单家市值突破 4 万亿美元，接近整个德国股市",
    ]),
]
bubble_html = '<div style="text-align:center;margin-bottom:12px"><span class="tag tag-red">泡沫指标全扫描</span></div>'
for title, color, lines in bubble_items:
    bubble_html += f'<div class="section"><div class="section-title"><span class="bar bar-{color}"></span>{title}</div><div class="section-body">'
    for l in lines:
        bubble_html += f'<div class="item">• {l}</div>'
    bubble_html += '</div></div>'
cards_html.append(card(2, "泡沫指标全览", "估值 · 资本开支 · 市场集中度", bubble_html))

# ── Card 3: vs 2000 ──
vs2000_html = '<div style="text-align:center;margin-bottom:12px"><span class="tag tag-gold">当前 vs 2000 年对比</span></div>'
vs2000_html += '<div style="display:flex;flex-wrap:wrap;gap:4px 0;margin-bottom:14px">'
vs_items = [
    ("纳指 PE", "200x", "42x", "#f85149"),
    ("科技公司盈利比例", "14%", "90%+", "#3fb950"),
    ("科技股净利润率", "<10%", "25%+", "#3fb950"),
    ("英伟达市值", "无", "4万亿", "#f0b866"),
    ("市场集中度", "前10大占27%", "前5大占30%", "#f85149"),
    ("AI 资本开支/GDP", "<2.6%", "3.3%", "#f85149"),
    ("实际经济增长", "过热", "软着陆", "#58a6ff"),
    ("债务水平", "较低", "偏高", "#f0b866"),
]
for i, (lab, val2000, valNow, clr) in enumerate(vs_items):
    vs2000_html += f'<div style="width:50%;display:flex;justify-content:space-between;padding:2px 8px;font-size:15px"><span style="color:#8b949e">{lab}</span><span>2000年 <span style="color:#8b949e">{val2000}</span> / 现在 <span style="color:{clr};font-weight:700">{valNow}</span></span></div>'
vs2000_html += '</div>'
vs2000_html += f"""<div class="section"><div class="section-title"><span class="bar bar-green"></span>核心差异点</div>
  <div class="section-body">
    <div class="item">• 当前科技公司盈利质量远好于 2000 年</div>
    <div class="item">• 2000 年是纯概念，现在是真金白银的 AI 算力需求</div>
    <div class="item" style="color:#f0b866;font-weight:600;font-size:16px">结论：不是 2000 年级别崩盘，但仍是高危期</div>
  </div></div>"""
vs2000_html += '<div style="margin-top:auto;font-size:13px;color:#8b949e;text-align:center">「估值需要回归，但不是全盘否定」</div>'
cards_html.append(card(3, "vs 2000 年对比", "有泡沫但比科网时期健康", vs2000_html))

# ── Card 4: 大佬观点 ──
bigshot_items = [
    ("看空派", "#f85149", [
        ("迈克尔·巴里", "做空英伟达、Palantir，仓位翻倍至近11亿美元"),
        ("桥水达利欧", "AI 已出现泡沫苗头，逼近 1929、2000 水平"),
        ("国内学者张光平", "货币-科技联动模型显示拐点已至，2026 年泡沫破裂"),
    ]),
    ("相对乐观", "#3fb950", [
        ("高盛", "科技股估值已低于大盘，形成罕见价值机会"),
        ("富国银行", "只是仓位调整，半导体牛市未结束"),
        ("贝莱德", "AI 仍在早期，长期趋势不变"),
    ]),
    ("关键共识", "#f0b866", [
        ("估值过高", "短期内确实需要消化高估值"),
        ("分化加剧", "有业绩的活下去，纯概念的会被出清"),
        ("长期看好", "AI 技术革命方向不变，但要等待时机"),
    ]),
]
bigshot_html = ''
for title, clr, items in bigshot_items:
    bigshot_html += f'<div class="risk-group"><div class="rg-title" style="color:{clr}">{title}</div>'
    for t, d in items:
        bigshot_html += f'<div class="risk-item"><span class="ri-label" style="color:{clr}">• {t}</span><span class="ri-desc">{d}</span></div>'
    bigshot_html += '</div>'
cards_html.append(card(4, "大佬观点一览", "看空 vs 看多，谁更有道理？", bigshot_html))

# ── Card 5: 风险清单 ──
risk_items = [
    ("短期风险（1-3个月）", "#f85149", [
        ("美联储政策转向", "CPI、就业数据超预期，加息概率上升"),
        ("获利盘集中出逃", "连续 9 周上涨后积累大量获利盘"),
        ("SpaceX 上市", "可能虹吸市场流动性"),
        ("中东局势恶化", "能源价格反弹推升通胀"),
    ]),
    ("中期风险（3-12个月）", "#f0b866", [
        ("AI 业绩不及预期", "资本开支高投入但短期 ROI 不明确"),
        ("估值回归均值", "估值修复过程中波动率放大"),
        ("经济增长放缓", "美国经济软着陆但增速下降"),
    ]),
    ("长期确定性（1年+）", "#3fb950", [
        ("AI 技术革命", "算力、应用商业化仍在进行中"),
        ("硬科技分化", "有真实业绩的科技股会走出来"),
    ]),
]
risk_html = ''
for title, clr, items in risk_items:
    risk_html += f'<div class="risk-group"><div class="rg-title" style="color:{clr}">{title}</div>'
    for t, d in items:
        risk_html += f'<div class="risk-item"><span class="ri-label" style="color:{clr}">• {t}</span><span class="ri-desc">{d}</span></div>'
    risk_html += '</div>'

risk_html += '<div class="section"><div class="section-title"><span class="bar bar-blue"></span>可能的调整幅度</div><div class="section-body">'
risk_html += """<div style="display:flex;flex-wrap:wrap;gap:4px 0;margin-bottom:14px">
  <div style="width:50%;display:flex;justify-content:space-between;padding:2px 8px;font-size:15px"><span style="color:#8b949e">温和调整</span><span style="color:#58a6ff;font-weight:700">-10~-15%</span></div>
  <div style="width:50%;display:flex;justify-content:space-between;padding:2px 8px;font-size:15px"><span style="color:#8b949e">中度调整</span><span style="color:#f0b866;font-weight:700">-15~-25%</span></div>
  <div style="width:50%;display:flex;justify-content:space-between;padding:2px 8px;font-size:15px"><span style="color:#8b949e">崩盘级</span><span style="color:#f85149;font-weight:700">-40%+</span></div>
</div>
<div class="item">• 高盛测算：科技股估值回归历史均值约跌 35%</div>
<div class="item">• 我们判断：大概率是-15~-25%的中度调整</div>
</div></div>"""
cards_html.append(card(5, "风险清单", "短期 · 中期 · 长期风险全景图", risk_html))

# ── Card 6: 结论与行动 ──
verdict_html = f"""<div class="big-verdict text-amber">结论：高危但非崩盘</div>
<div style="text-align:center;font-size:16px;margin-bottom:14px">不是 2000 年级别，但确实需要谨慎</div>"""

verdict_html += '<div class="section"><div class="section-title"><span class="bar bar-blue"></span>应对策略</div>'
for lab, stars, detail, clr in [
    ("短期", "☆☆☆☆★", "降低仓位，等待估值消化", "#f0b866"),
    ("中期", "☆☆☆★★", "逢低布局有业绩的硬科技", "#3fb950"),
    ("长期", "★★★★★", "AI 技术革命方向不变", "#58a6ff"),
]:
    verdict_html += f'<div class="score-row"><span style="color:#8b949e;font-size:16px">{lab}</span><span class="stars" style="color:{clr}">{stars}</span><span class="detail">{detail}</span></div>'
verdict_html += '</div>'

verdict_html += '<div class="section"><div class="section-title"><span class="bar bar-green"></span>现在该做什么？</div><div class="section-body">'
for m in ["减持纯概念、高估值、无业绩的科技股", "等待 CPI、美联储会议等关键数据明朗", "关注真正有现金流、盈利能力的硬科技龙头", "配置部分防御性资产（黄金、美债、消费必需品）", "如果出现恐慌性杀跌（单日-5%+），可分批建仓优质标的"]:
    verdict_html += f'<div class="item">• {m}</div>'
verdict_html += '</div></div>'

verdict_html += '<div class="cta" style="margin-top:auto">关注我，第一时间解读市场动向</div>'
verdict_html += '<div class="disclaimer">以上为市场分析，不构成投资建议。投资有风险，入市需谨慎。</div>'
cards_html.append(card(6, "最终结论与策略", "高危但非崩盘，调整是布局良机", verdict_html))

# ── Build HTML ──
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body>
{"".join(cards_html)}
</body></html>"""

path = os.path.join(OUT, "tech_crash_risk.html")
with open(path, "w", encoding="utf-8") as f:
    f.write(html)

fsize = os.path.getsize(path) / 1024
print(f"✅ {path} ({fsize:.0f} KB)")
print("   浏览器打开 → 逐张截图 → 发布小红书")
