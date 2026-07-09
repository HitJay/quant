"""半导体全线爆发 7 页深度回测 · HTML+Playwright 路线

今日半导体 +6.53%, 主力净入 318.7亿, 13只涨停
"""
from __future__ import annotations
from pathlib import Path
import json

# ─── 路径 ─────
ROOT = Path("/das/user/QYJI/quant")
DATE = "20260709"
DAY_HUM = "2026-07-09"
TOPIC = "semi_rally"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 数据常量 ─────
MAIN_PCT = 6.53
MAIN_NAME = "半导体板块"
MAIN_LEADER = "华天科技"
MAIN_LEADER_PCT = 10.01

# 三大数字
NUM1 = ("318.7亿", "主力净入", "--red")
NUM2 = ("+6.53%", "行业涨幅NO.1", "--cyan")
NUM3 = ("13只", "涨停封板", "--gold")

# 胜率分桶 (来自SW 801081回测)
BUCKETS = [
    ("[5%, 6%)", 73, 51, 65, +5.5, +4.1, +1.5, -1.8, False),
    ("[6%, 7%)", 41, 54, 55, +4.5, +2.6, +1.6, -4.2, True),   # ← 当前
    ("[7%+)",   33, 67, 67, +1.9, +4.4, +3.8, +0.2, False),
]

# 反共识形态: 5日内两次+5%
CROSS_PCT = 55      # 当前档 [6%,7%) 的20d胜率
CROSS_TRAP = 42     # 双涨陷阱的20d胜率
CROSS_60D = -3.0    # 双涨陷阱60d均值
FAIL_N = 55
FAIL_LOSS = 30
FAIL_DRAWDOWN = 26

# 历史样本 (最近5次)
SAMPLES = [
    ("2024-09-27", "2024-09-30", "+7.3% · +15.5%", "+15.9%"),
    ("2024-09-30", "2024-10-08", "+15.5% · +16.6%", "+4.4%"),
    ("2025-08-22", "2025-08-28", "+7.7% · +6.7%", "+8.9%"),
    ("2026-05-06", "2026-05-11", "+5.3% · +6.1%", "-1.8%"),
]

# 位置指标 (3年)
POS_3Y = 98.8
HIGH_3Y = 14332
LOW_3Y = 2702
DIST_HIGH = -11.0
DIST_LOW = 372.0

# 今日 10 只代表股 (东财人气 + 涨停标的)
STOCKS = [
    ("300046", "华天科技", 23.73, 10.01, 182.5, "涨停"),
    ("600584", "长电科技", 103.52, 10.00, 168.2, "涨停"),
    ("000021", "深科技", 56.24, 9.99, 145.8, "涨停"),
    ("600667", "太极实业", 26.27, 10.01, 95.6, "涨停"),
    ("603986", "兆易创新", 663.49, 10.00, 128.3, "涨停"),
    ("600206", "有研新材", 59.38, 10.00, 112.4, "涨停"),
    ("002156", "通富微电", 72.17, 10.00, 98.7, "涨停"),
    ("000734", "领先股份", 18.52, 7.30, 62.1, "领涨"),
    ("300661", "圣邦股份", 312.80, 6.85, 45.3, "强势"),
    ("688256", "寒武纪", 1535.01, 5.80, 54.8, "强势"),
]

# ETF 影子链
ETF_LIST = [
    ("512480", "半导体ETF", 1.235, 6.45, 185.6),
    ("159813", "半导体ETF", 1.178, 6.38, 142.3),
    ("512760", "芯片ETF", 1.412, 6.72, 168.7),
    ("159995", "芯片ETF", 1.385, 6.51, 135.2),
    ("516640", "半导体材料设备ETF", 1.087, 6.22, 89.5),
]


# ═══════════════════════════════════════════
# 全局 CSS
# ═══════════════════════════════════════════
BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0d1117;
  --card: #161b22;
  --card2: #1c2129;
  --border: #30363d;
  --text: #e6edf3;
  --text2: #c9d1d9;
  --muted: #8b949e;
  --dim: #6e7681;
  --blue: #58a6ff;
  --green: #3fb950;
  --red: #f85149;
  --rose: #ff7b72;
  --orange: #d2991d;
  --gold: #f0c040;
  --gold2: #ffd77a;
  --cyan: #56d4dd;
  --purple: #bc8cff;
}
body {
  width: 1080px;
  height: 1440px;
  background: var(--bg);
  font-family: 'Noto Sans SC', 'Noto Sans CJK SC', 'Droid Sans Fallback', sans-serif;
  color: var(--text);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 34px 48px 20px;
  font-size: 27px;
}
body::before {
  content: '';
  position: absolute;
  top: -300px; right: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(248, 81, 73, 0.06) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body::after {
  content: '';
  position: absolute;
  bottom: -400px; left: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(88, 166, 255, 0.04) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body > * { position: relative; z-index: 1; }
.pill {
  display: inline-block; padding: 8px 26px;
  border-radius: 24px; font-size: 23px; font-weight: 700;
  color: var(--bg); text-align: center; letter-spacing: 0.5px;
}
.top-pill { display: flex; justify-content: center; }
.subtitle {
  text-align: center; font-size: 32px; font-weight: 700;
  color: var(--text); margin-top: 20px;
}
.subtitle-sm {
  text-align: center; font-size: 22px; color: var(--muted);
  margin-top: 8px; font-style: italic;
}
.footer {
  margin-top: 16px; padding-top: 14px;
  display: flex; justify-content: space-between;
  font-size: 22px; color: var(--dim);
  border-top: 1px solid var(--border);
}
.big-num { font-weight: 900; line-height: 1; letter-spacing: -1px; }
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 20px 24px;
}
"""

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'

def base_html(body: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
{FONT_LINK}
<style>{BASE_CSS}{extra_css}</style>
</head>
<body>
{body}
</body>
</html>"""


# ═══════════════════════════════════════════
# Page 1 — 封面
# ═══════════════════════════════════════════
def page_1_html() -> str:
    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} · 板块暴动</div></div>
<div class="subtitle" style="font-size:34px">半导体全线爆发 · 今日主角</div>

<div style="text-align:center;margin-top:36px">
  <div class="big-num" style="font-size:220px;background:linear-gradient(180deg,#ff7b72 0%,#f85149 60%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:16px 0;filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">
    +{MAIN_PCT:.2f}%
  </div>
  <div style="font-size:25px;color:var(--muted);margin-top:12px;letter-spacing:1px">
    半导体 · 申万二级指数 · 近 3 年第 1.2% 分位
  </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:52px">
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:56px;color:var({NUM1[2]})">{NUM1[0]}</div>
    <div style="font-size:22px;color:var(--muted);margin-top:12px">{NUM1[1]}</div>
  </div>
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:56px;color:var({NUM2[2]})">{NUM2[0]}</div>
    <div style="font-size:22px;color:var(--muted);margin-top:12px">{NUM2[1]}</div>
  </div>
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:56px;color:var({NUM3[2]})">{NUM3[0]}</div>
    <div style="font-size:22px;color:var(--muted);margin-top:12px">{NUM3[1]}</div>
  </div>
</div>

<div style="padding:28px 32px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--orange);border-radius:16px;box-shadow:0 0 32px rgba(210,153,29,0.15);text-align:center">
  <div style="font-size:25px;color:var(--text2);margin-bottom:14px">但 —— 历史数据告诉你</div>
  <div class="big-num" style="font-size:72px;background:linear-gradient(90deg,var(--orange) 0%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent">[6%, 7%) 档 20 日胜率 {CROSS_PCT}%</div>
  <div style="font-size:25px;color:var(--muted);margin-top:14px">
    [5%, 6%) 档反而是 <b style="color:var(--red)">65%</b>  ! 今天多涨了 0.5% 反而胜率更低 ?
  </div>
</div>

<div style="text-align:center">
  <div style="display:inline-block;padding:16px 32px;background:var(--card);border:1.5px solid var(--cyan);border-radius:14px;font-size:26px;font-weight:700;color:var(--cyan);box-shadow:0 4px 16px rgba(86,212,221,0.15)">
    半导体的反直觉规律
  </div>
  <div style="font-size:23px;color:var(--muted);font-style:italic;margin-top:18px">翻到下一页 → 看今日全景</div>
</div>

<div class="footer">
  <span>* 数据: 申万二级指数 801081 · 6407 天样本</span>
  <span>1/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# Page 2 — 板块链全景 (10 只代表股)
# ═══════════════════════════════════════════
def page_2_html() -> str:
    max_pct = max(s[3] for s in STOCKS)
    rows = []
    for code, name, price, pct_chg, vol, tag in STOCKS:
        bar_w = (pct_chg / max_pct) * 0.35
        pct_str = f"+{pct_chg:.2f}%" if pct_chg > 0 else f"{pct_chg:.2f}%"
        bar_color = "var(--red)" if pct_chg > 7 else "var(--orange)" if pct_chg > 5 else "var(--gold)"
        vol_str = f"{vol:.0f}亿"
        rows.append(f"""
    <div style="display:grid;grid-template-columns:100px 90px 1fr 90px 80px 90px;align-items:center;gap:10px;padding:8px 12px;border-bottom:1px solid var(--border)">
        <div style="font-size:23px;color:var(--text2);font-weight:500">{name}</div>
        <div style="font-size:22px;color:var(--muted);text-align:right">{price:.2f}</div>
        <div style="position:relative;height:28px;display:flex;align-items:center">
            <div style="width:{bar_w};height:22px;background:linear-gradient(90deg,{bar_color} 0%,rgba(248,81,73,0.3) 100%);border-radius:4px;min-width:6px"></div>
        </div>
        <div style="font-size:26px;font-weight:900;color:{bar_color};text-align:right">{pct_str}</div>
        <div style="font-size:22px;color:var(--muted);text-align:right">{vol_str}</div>
        <div style="padding:3px 12px;border-radius:10px;font-size:19px;font-weight:600;text-align:center;background:{'var(--red)' if tag=='涨停' else 'var(--orange)' if tag=='领涨' else 'var(--cyan)'};color:var(--bg)">{tag}</div>
    </div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--blue)">板块链全景</div></div>
<div class="subtitle">10 只代表股今天涨了多少</div>
<div class="subtitle-sm">涨幅排序  ·  涨停 8 只  ·  主力净入 318.7亿</div>

<div style="margin-top:22px;flex:1;display:flex;flex-direction:column">
    <div style="display:grid;grid-template-columns:100px 90px 1fr 90px 80px 105px;align-items:center;gap:10px;padding:10px 14px;font-size:23px;font-weight:700;color:var(--muted);border-bottom:2px solid var(--border);background:var(--card2);border-radius:10px 10px 0 0">
        <div>名称</div>
        <div style="text-align:right">价格</div>
        <div style="text-align:center">今日涨幅</div>
        <div style="text-align:right">涨幅%</div>
        <div style="text-align:right">成交</div>
        <div style="text-align:center">标签</div>
    </div>
    <div style="overflow:hidden;flex:1">{"".join(rows)}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:14px;padding:14px 16px;background:var(--card2);border:1px solid var(--border);border-radius:12px">
        <div style="text-align:center">
            <div style="font-size:22px;color:var(--muted)">涨停密度</div>
            <div style="font-size:34px;font-weight:900;color:var(--red)">13</div>
            <div style="font-size:20px;color:var(--muted)">行业涨停</div>
        </div>
        <div style="text-align:center">
            <div style="font-size:22px;color:var(--muted)">概念涨幅</div>
            <div style="font-size:34px;font-weight:900;color:var(--red)">+3.42%</div>
            <div style="font-size:20px;color:var(--muted)">蓝宝石</div>
        </div>
        <div style="text-align:center">
            <div style="font-size:22px;color:var(--muted)">东财人气</div>
            <div style="font-size:34px;font-weight:900;color:var(--gold)">top 10 占 7</div>
            <div style="font-size:20px;color:var(--muted)">半导体霸榜</div>
        </div>
    </div>
</div>

<div class="footer">
  <span>* 数据: 东财人气榜 + 涨停池</span>
  <span>2/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# Page 3 — 主题 ETF 影子链
# ═══════════════════════════════════════════
def page_3_html() -> str:
    cards = []
    for code, name, price, pct, vol in ETF_LIST:
        pct_str = f"+{pct:.2f}%"
        vol_str = f"{vol:.0f}亿"
        cards.append(f"""
    <div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 20px;text-align:center">
        <div style="font-size:22px;color:var(--muted);margin-bottom:4px">{code}</div>
        <div style="font-size:28px;font-weight:700;color:var(--text);margin-bottom:10px">{name}</div>
        <div class="big-num" style="font-size:38px;color:var(--red)">{pct_str}</div>
        <div style="font-size:22px;color:var(--muted);margin-top:6px">{price:.3f}元 · {vol_str}</div>
    </div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--purple)">ETF 影子链</div></div>
<div class="subtitle">A 股散户参与半导体</div>
<div class="subtitle-sm">5 只 ETF 今日表现</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:32px">
    {"".join(cards[:3])}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">
    {"".join(cards[3:])}
</div>

<div style="padding:20px 24px;background:var(--card2);border:1px solid var(--border);border-radius:14px;text-align:center;margin-top:24px">
    <div style="font-size:24px;color:var(--cyan);font-weight:700">今日半导体 ETF 全线飘红 · 最高 +6.72%</div>
    <div style="font-size:22px;color:var(--muted);margin-top:8px">散户最便捷的参与方式 · 无门槛无涨跌幅限制</div>
</div>

<div class="footer">
  <span>* 数据: 东方财富 · A 股 ETF</span>
  <span>3/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# Page 4 — 胜率表
# ═══════════════════════════════════════════
def page_4_html() -> str:
    bucket_cards = []
    for label, n, w5, w20, m20, med20, m60, med60, is_current in BUCKETS:
        cls = "bucket-card bucket-hl" if is_current else "bucket-card"
        w5_col = "--red" if w5 >= 65 else "--orange" if w5 >= 50 else "--green"
        w20_col = "--red" if w20 >= 65 else "--orange" if w20 >= 50 else "--green"
        m20_col = "--red" if m20 > 0 else "--green"
        hl_line = f'<div style="font-size:25px;font-weight:900;color:var(--orange);margin-top:10px">← 今日 +{MAIN_PCT}% 在此档</div>' if is_current else ""
        bucket_cards.append(f"""
<div class="{cls}">
  <div style="display:grid;grid-template-columns:200px 1fr 1fr 1fr;align-items:center;gap:22px">
    <div>
      <div style="font-size:36px;font-weight:900;color:var(--red)">{label}</div>
      <div style="font-size:25px;color:var(--muted);margin-top:8px">样本 n = {n}</div>
      {hl_line}
    </div>
    <div style="text-align:center">
      <div style="font-size:23px;color:var(--muted);margin-bottom:8px">5 日胜率</div>
      <div style="font-size:48px;font-weight:900;color:var({w5_col})">{w5}%</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:23px;color:var(--muted);margin-bottom:8px">20 日胜率</div>
      <div style="font-size:48px;font-weight:900;color:var({w20_col})">{w20}%</div>
      <div style="font-size:22px;color:var(--muted);margin-top:6px">均 {m20:+.1f}%</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:23px;color:var(--muted);margin-bottom:8px">60 日均值</div>
      <div style="font-size:48px;font-weight:900;color:var({m20_col})">{m60:+.1f}%</div>
      <div style="font-size:22px;color:var(--muted);margin-top:6px">中位 {med60:+.1f}%</div>
    </div>
  </div>
</div>""")

    extra = """
.bucket-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 22px 26px;
}
.bucket-hl {
  background: linear-gradient(135deg, var(--card) 0%, rgba(210, 153, 29, 0.05) 100%);
  border: 2px solid var(--orange);
  box-shadow: 0 0 28px rgba(210, 153, 29, 0.2);
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--gold)">历史胜率</div></div>
<div class="subtitle">单日大涨后, 半导体 N 天怎么走?</div>
<div class="subtitle-sm">SW 801081 · 6407 交易日 · 单日 ≥ +5% 分档</div>

<div style="display:flex;flex-direction:column;gap:16px">
  {"".join(bucket_cards)}
</div>

<div style="padding:18px 24px;background:var(--card2);border:1px solid var(--border);border-radius:12px;text-align:center">
  <div style="font-size:26px;font-weight:900;color:var(--cyan);margin-bottom:8px">关键发现</div>
  <div style="font-size:24px;color:var(--text2);line-height:1.6">
    [5%, 6%) 档 20 日胜率 <b style="color:var(--red)">65%</b> · 但今日 +6.53% 落在 [6%, 7%) 档仅 <b style="color:var(--orange)">55%</b><br>
    奇怪吗? 半导体 <b style="color:var(--gold)">7% 以上的暴涨反而胜率 67%</b> — [6%, 7%) 是最尴尬的中档
  </div>
</div>

<div style="padding:20px 28px;background:linear-gradient(135deg,var(--card) 0%,rgba(210,153,29,0.08) 100%);border:2px solid var(--orange);border-radius:14px;text-align:center;box-shadow:0 0 28px rgba(210,153,29,0.15)">
  <div style="font-size:28px;font-weight:900;color:var(--orange)">半导体的反直觉规律</div>
  <div style="font-size:24px;color:var(--muted);margin-top:10px">
    最强档是 [5%, 6%) 和 [7%+), 中间档反而最弱 — 决定胜率的不是涨了多少, 而是涨的结构 (翻到下一页 →)
  </div>
</div>

<div class="footer">
  <span>* 回测基准: 1999-12 至今</span>
  <span>4/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# Page 5 — 反共识重锤
# ═══════════════════════════════════════════
def page_5_html() -> str:
    sample_rows = []
    for d1, d2, combo, r20 in SAMPLES:
        val = float(r20.strip("%").strip("+"))
        is_neg = val < 0
        bg = "rgba(63, 185, 80, 0.14)" if is_neg else "transparent"
        col = "var(--green)" if is_neg else "var(--red)"
        fw = "900" if is_neg else "500"
        fs = "27px" if is_neg else "22px"
        sample_rows.append(f"""
    <div class="sample-row" style="background:{bg}">
      <div>{d1}</div>
      <div>{d2}</div>
      <div style="text-align:center">{combo}</div>
      <div style="text-align:right;font-size:{fs};font-weight:{fw};color:{col}">{r20}</div>
    </div>""")

    extra = """
.sample-row {
  display: grid;
  grid-template-columns: 140px 140px 1fr 120px;
  gap: 10px; padding: 4px 14px;
  align-items: center;
  font-size: 22px; color: var(--text2);
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
}
.sample-header {
  display: grid;
  grid-template-columns: 140px 140px 1fr 120px;
  gap: 10px; padding: 4px 14px;
  font-size: 23px; font-weight: 900; color: var(--muted);
  border-bottom: 1px solid var(--border); margin-bottom: 4px;
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--orange)">反共识陷阱</div></div>
<div class="subtitle" style="font-size:42px">换挡不如换结构</div>

<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:20px;margin-top:18px;padding:0 20px">
  <div style="text-align:center">
    <div style="font-size:23px;color:var(--muted);margin-bottom:6px">今日档 [6%, 7%)</div>
    <div class="big-num" style="font-size:160px;color:var(--red);filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">{CROSS_PCT}%</div>
    <div style="font-size:24px;color:var(--muted);margin-top:4px">20 日胜率</div>
  </div>
  <div style="text-align:center;padding:0 8px">
    <div style="font-size:64px;font-weight:900;color:var(--orange);line-height:1">→</div>
    <div style="font-size:22px;color:var(--orange);margin-top:6px;font-weight:700">若 5 日内<br>两次 +5%</div>
  </div>
  <div style="text-align:center">
    <div style="font-size:23px;color:var(--muted);margin-bottom:6px">双次大涨后</div>
    <div class="big-num" style="font-size:160px;color:var(--green);filter:drop-shadow(0 4px 12px rgba(63,185,80,0.3))">{CROSS_TRAP}%</div>
    <div style="font-size:24px;color:var(--muted);margin-top:4px">20 日胜率</div>
  </div>
</div>

<div style="text-align:center;padding:12px 20px;background:var(--card2);border:1px solid var(--border);border-radius:12px;margin-top:10px;font-size:23px;font-weight:700">
  60 日均值:  单次大涨 +1.6%   VS   双次大涨后 <span style="color:var(--green)">{CROSS_60D:+.1f}%</span>
</div>

<div style="margin-top:12px">
  <div style="text-align:center;font-size:24px;font-weight:700;color:var(--cyan);margin-bottom:2px">追过第二次 +5% 的姐妹, 后来怎样了?</div>
  <div style="text-align:center;font-size:22px;color:var(--muted);font-style:italic;margin-bottom:4px">最近 4 次历史样本</div>
  <div class="sample-header">
    <div>首日</div>
    <div>次日</div>
    <div style="text-align:center">两次涨幅</div>
    <div style="text-align:right">20d 后</div>
  </div>
  {"".join(sample_rows)}
</div>

<div style="padding:20px 28px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:14px;text-align:center;box-shadow:0 6px 24px rgba(210,153,29,0.3)">
  <div style="font-size:32px;font-weight:900;color:var(--bg)">{FAIL_N} 次双涨信号中 {FAIL_LOSS} 次亏钱 · {FAIL_DRAWDOWN} 次跌超 -3%</div>
  <div style="font-size:25px;color:var(--bg);margin-top:8px;opacity:0.85">20 日均 -3.0% · 中位 -2.9% · 高开低走才是真风险</div>
</div>

<div class="footer">
  <span>* 反共识形态: 5 日内两次单日 ≥ +5%</span>
  <span>5/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# Page 6 — 位置指标 + 三档操作
# ═══════════════════════════════════════════
def page_6_html() -> str:
    tiers = [
        ("激进",   "--red",    "已入 → 明天观察能否站稳 +5% 支撑, 跌破减仓"),
        ("稳健",   "--orange", "未入 → 别追高, 等回踩 MA20 确认再上"),
        ("长线",   "--cyan",   "定投半导体 ETF, 分位虽然高但行业长期向上"),
    ]
    tier_rows = "".join(f"""
    <div style="display:flex;align-items:center;gap:20px;padding:14px 18px;background:var(--card);border:1px solid var(--border);border-radius:12px">
      <div style="min-width:80px;padding:10px 16px;background:var({col});color:var(--bg);border-radius:22px;font-size:23px;font-weight:900;text-align:center">{tag}</div>
      <div style="font-size:24px;color:var(--text2);line-height:1.5;flex:1">{body}</div>
    </div>""" for tag, col, body in tiers)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--cyan)">当前位置</div></div>
<div class="subtitle">涨了一天, 但半导体在哪儿?</div>

<div style="text-align:center;margin-top:24px">
  <div style="font-size:22px;color:var(--muted);margin-bottom:10px">近 3 年分位</div>
  <div class="big-num" style="font-size:200px;background:linear-gradient(180deg,#f85149 0%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">{POS_3Y:.1f}%</div>
  <div style="font-size:23px;color:var(--orange);margin-top:14px;font-weight:600">高位区 · 距 3 年高点仅 -{abs(DIST_HIGH):.0f}%</div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:28px">
  <div class="card" style="text-align:center;padding:18px 12px">
    <div style="font-size:22px;color:var(--muted);margin-bottom:8px">距 3 年高点</div>
    <div style="font-size:38px;font-weight:900;color:var(--green)">{DIST_HIGH:+.1f}%</div>
    <div style="font-size:20px;color:var(--muted);margin-top:6px">{HIGH_3Y} → 现值</div>
  </div>
  <div class="card" style="text-align:center;padding:18px 12px">
    <div style="font-size:22px;color:var(--muted);margin-bottom:8px">距 3 年低点</div>
    <div style="font-size:38px;font-weight:900;color:var(--red)">+{DIST_LOW:.0f}%</div>
    <div style="font-size:20px;color:var(--muted);margin-top:6px">{LOW_3Y} → 现值</div>
  </div>
  <div class="card" style="text-align:center;padding:18px 12px">
    <div style="font-size:22px;color:var(--muted);margin-bottom:8px">主力净入</div>
    <div style="font-size:38px;font-weight:900;color:var(--red)">318.7亿</div>
    <div style="font-size:20px;color:var(--muted);margin-top:6px">单日行业 NO.1</div>
  </div>
</div>

<div>
  <div style="text-align:center;font-size:26px;font-weight:900;color:var(--text);margin-bottom:12px">三档操作建议</div>
  <div style="display:flex;flex-direction:column;gap:10px">
    {tier_rows}
  </div>
</div>

<div style="padding:16px 22px;background:linear-gradient(90deg,rgba(210,153,29,0.12),rgba(210,153,29,0.03));border-left:5px solid var(--orange);border-radius:8px">
  <div style="font-size:22px;font-weight:900;color:var(--orange)">散户友情提醒</div>
  <div style="font-size:23px;color:var(--text2);margin-top:6px">半导体 3 年分位 {POS_3Y}%, 已是高位区, 且今日 [6%,7%) 档 20d 胜率仅 55%. 追涨前先看位置.</div>
</div>

<div class="footer">
  <span>* 分位基于收盘价 · 3 年基准</span>
  <span>6/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# Page 7 — CTA
# ═══════════════════════════════════════════
def page_7_html() -> str:
    cards = [
        ("01", "复盘",   "--red",    "涨停天梯 · 行业冠亚军 · 炸板预警"),
        ("02", "雷达",   "--purple", "雪球新热点 · 资金搬家 · 分档胜率"),
        ("03", "反共识", "--cyan",   "拒绝小作文 · 数据驱动 · 历史样本核对"),
    ]
    card_rows = "".join(f"""
<div style="display:flex;align-items:center;gap:24px;padding:26px 28px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,0.3) 100%);border:2px solid var({col});border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
  <div style="font-size:76px;font-weight:900;color:var({col});min-width:96px;text-align:center;line-height:1;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4))">{num}</div>
  <div style="flex:1">
    <div style="font-size:34px;font-weight:900;color:var(--text)">{title}</div>
    <div style="font-size:25px;color:var(--muted);margin-top:8px">{body}</div>
  </div>
</div>""" for num, title, col, body in cards)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--rose)">关注我</div></div>
<div style="text-align:center;font-size:25px;font-style:italic;color:var(--text2);margin-top:20px">
  明天半导体还能续命吗? 数据每天替你盯
</div>

<div style="text-align:center">
  <div style="font-size:42px;color:var(--text);margin-bottom:14px">每天 3 分钟</div>
  <div class="big-num" style="font-size:84px;background:linear-gradient(90deg,var(--gold) 0%,var(--gold2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(240,192,64,0.3))">看懂 A 股 + 港股</div>
</div>

<div style="display:flex;flex-direction:column;gap:16px">
  {card_rows}
</div>

<div style="padding:28px 32px;background:linear-gradient(135deg,var(--gold) 0%,#e8b73a 100%);border-radius:16px;text-align:center;box-shadow:0 8px 32px rgba(240,192,64,0.35)">
  <div style="font-size:36px;font-weight:900;color:var(--bg)">点关注 + 收藏 不迷路</div>
  <div style="font-size:26px;color:var(--bg);margin-top:10px;opacity:0.8">明早 9:15 继续给你递盘前情报</div>
</div>

<div style="text-align:center">
  <div style="font-size:25px;font-weight:900;color:var(--cyan);margin-bottom:10px">评论区告诉我</div>
  <div style="font-size:26px;color:var(--text2);margin-bottom:8px">半导体今天你追了吗? 明天该减仓还是持有?</div>
  <div style="font-size:23px;color:var(--muted)">明天想看哪只票的盘后追踪? 评论区点名 →</div>
</div>

<div class="footer">
  <span>* 复旦杰伦 · 拒绝小作文 · 拒绝喊单</span>
  <span>7/7</span>
</div>
"""
    return base_html(body)


PAGE_HTML_GENERATORS = [
    page_1_html, page_2_html, page_3_html, page_4_html,
    page_5_html, page_6_html, page_7_html,
]


def render_all():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1080, "height": 1440},
            device_scale_factor=2, locale="zh-CN",
        )
        page = ctx.new_page()
        for i, gen in enumerate(PAGE_HTML_GENERATORS, 1):
            out = OUT / f"page_{i}.png"
            page.set_content(gen(), wait_until="networkidle")
            page.wait_for_timeout(2000)
            page.screenshot(path=str(out), full_page=False)
            print(f"  saved {out.name} ({out.stat().st_size/1024:.0f}KB)")
        browser.close()


def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 8)]
    w, h = pages[0].size
    # 2x4 grid (last slot empty)
    tw, th = 470, 615
    canvas = Image.new("RGB", (tw * 4 + 30, th * 2 + 20), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, 4)
        canvas.paste(p.resize((tw, th)), (c * tw + 5 + c*5, r * th + 5 + r*5))
    canvas.save(OUT / "preview_2x4.png")
    print(f"  saved preview_2x4.png")
    
    total_h = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, total_h), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y)); y += p.height
    ratio = 720 / w
    stacked.resize((720, int(total_h * ratio))).save(OUT / "all_pages_stacked.png")
    print(f"  saved all_pages_stacked.png")


if __name__ == "__main__":
    print(f"HTML 7 页深度回测 → {OUT}")
    render_all()
    make_preview()
    print(f"\n完成. 7 张 2160×2880 PNG")
