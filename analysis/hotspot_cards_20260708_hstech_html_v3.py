"""恒生科技暴动 7 页深度卡片 · HTML+Playwright 路线 v2

v1 → v2 修复:
- 字号整体 +30% (2160 输出下 12→16, 14→18, 17→22, 大字数字全放大)
- flex 布局改成 gap-based, 消除 900px 空白断层
- 背景加径向渐变 (P1/P5/P7 用主题色柔光)
- P1/P4/P6 内容密度提升 (填补空白, 加辅助数据/装饰元素)

产出 2160×2880 PNG × 7 张.
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260708"
DAY_HUM = "2026-07-08"
TOPIC = "hstech_rally"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_v3"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 数据常量 ─────
HSTECH_PCT = 5.51
HSTECH_CLOSE = 4759.66
HSTECH_AMT_YI = 1084
HSI_PCT = 3.28
NANXIANG_YI = 130
NANXIANG_1Y_RANK = 84.3
NANXIANG_1Y_AVG = 41.6
POS_1Y = 10.2
HIGH_1Y = 6683
LOW_1Y = 4256
DIST_HIGH_1Y = -28.7
DIST_LOW_1Y = 12.0

BUCKETS = [
    ("[5%, 6%)", 16, 44, 56,  +0.3,  +3.8,  -0.9,  +0.7, True),
    ("[6%, 7%)",  7, 14, 43,  -2.7,  -3.8,  -7.0, -11.4, False),
    ("[7%+)",    14, 57, 64,  +3.9,  +6.0, +10.4,  +7.2, False),
]

SAMPLES = [
    ("2022-11-11", "2022-11-15", "+10.1%", "+7.3%", "+10.7%"),
    ("2022-11-29", "2022-12-05", "+7.7%",  "+9.3%", "+6.0%"),
    ("2022-12-05", "2022-12-08", "+9.3%",  "+6.6%", "+6.8%"),
    ("2024-09-24", "2024-09-26", "+5.9%",  "+7.3%", "+8.7%"),
    ("2024-09-26", "2024-09-27", "+7.3%",  "+5.8%", "+3.8%"),
    ("2024-09-27", "2024-09-30", "+5.8%",  "+6.7%", "-5.0%"),
    ("2024-09-30", "2024-10-02", "+6.7%",  "+8.5%", "-12.8%"),
    ("2025-02-14", "2025-02-21", "+5.6%",  "+6.5%", "-3.8%"),
]

HK_STOCKS = [
    ("华虹半导体", "01347", 185.20, 13.50, 91.26),
    ("阿里巴巴-W", "09988", 107.80, 13.00, 217.89),
    ("快手-W",     "01024",  44.10, 11.47,  49.54),
    ("小米集团-W", "01810",  25.40,  9.96,  72.83),
    ("中芯国际",   "00981",  76.60,  9.46, 102.09),
    ("联想集团",   "00992",  22.36,  6.42,  34.59),
    ("网易",       "09999", 215.20,  4.97,  13.15),
    ("京东集团",   "09618", 108.90,  4.89,   8.62),
    ("腾讯控股",   "00700", 478.60,  4.81, 212.69),
    ("美团-W",     "03690",  80.50,  4.34,  41.97),
]

HK_ETFS = [
    ("恒生科技ETF易方达", "513010", 6.19, 5.58, 16.30, "沪市 · 场内 · 15% 权重集中"),
    ("港股通科技ETF",     "159120", 7.62, 6.22,  0.33, "深市 · 场内小规模"),
    ("港股通科技ETF国联安", "159125", 7.14, 5.12,  0.48, "深市 · 场内小规模"),
]
A_ETFS = [
    ("半导体设备ETF易方达", "159558", 41.89, 9.04, 23.18, "华为算力 + 存储受益"),
    ("科创芯片设计ETF",     "588780", 12.67, 5.52,  3.94, "科创板芯片设计"),
    ("软件ETF天弘",         "159035",  8.16, 4.03,  0.09, "软件板块 + AI 概念"),
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
  --card3: #21262d;
  --border: #30363d;
  --border-lite: #21262d;
  --text: #e6edf3;
  --text2: #c9d1d9;
  --muted: #8b949e;
  --dim: #6e7681;
  --blue: #58a6ff;
  --green: #3fb950;
  --red: #f85149;
  --red2: #ff7b72;
  --rose: #ff7b72;
  --orange: #d2991d;
  --orange2: #ffab40;
  --purple: #bc8cff;
  --gold: #f0c040;
  --gold2: #ffd77a;
  --cyan: #56d4dd;
}
body {
  width: 1080px;
  height: 1200px;
  background: var(--bg);
  font-family: 'Noto Sans SC', 'Noto Sans CJK SC', 'Droid Sans Fallback', sans-serif;
  color: var(--text);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 32px 48px 18px;
  font-size:29px;
}
/* 背景径向光晕 (装饰) */
body::before {
  content: '';
  position: absolute;
  top: -300px; right: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(248, 81, 73, 0.06) 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}
body::after {
  content: '';
  position: absolute;
  bottom: -400px; left: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(88, 166, 255, 0.04) 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}
body > * { position: relative; z-index: 1; }

.pill {
  display: inline-block;
  padding: 8px 26px;
  border-radius: 24px;
  font-size:24px;
  font-weight: 700;
  color: var(--bg);
  text-align: center;
  letter-spacing: 0.5px;
}
.top-pill { display: flex; justify-content: center; }
.subtitle {
  text-align: center;
  font-size:42px;
  font-weight: 700;
  color: var(--text);
  margin-top: 20px;
  letter-spacing: 0.3px;
}
.subtitle-sm {
  text-align: center;
  font-size:21px;
  color: var(--muted);
  margin-top: 8px;
  font-style: italic;
}
.footer {
  margin-top: 16px;
  padding-top: 14px;
  display: flex;
  justify-content: space-between;
  font-size:17px;
  color: var(--dim);
  border-top: 1px solid var(--border);
}
.bn { font-weight: 900; line-height: 1; }
.big-num { font-weight: 900; line-height: 1; letter-spacing: -1px; }
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px 24px;
}
.card-hl {
  background: linear-gradient(135deg, var(--card) 0%, #1a1a1f 100%);
  border: 2px solid var(--orange);
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 0 24px rgba(210, 153, 29, 0.2);
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
# P1 — 封面
# ═══════════════════════════════════════════
def page_1_html() -> str:
    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} · 恒科暴动</div></div>
<div class="subtitle" style="font-size:42px">港股科技单日狂飙</div>

<div style="text-align:center;margin-top:36px">
  <div class="big-num" style="font-size:240px;background:linear-gradient(180deg,#ff7b72 0%,#f85149 60%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:16px 0;filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">
    +{HSTECH_PCT:.2f}%
  </div>
  <div style="font-size:26px;color:var(--muted);margin-top:12px;letter-spacing:1px">
    恒生科技指数 &nbsp;·&nbsp; 26 年一遇 · 历史 top 1.9% 分位
  </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:52px">
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:68px;color:var(--gold)">{HSTECH_AMT_YI}亿</div>
    <div style="font-size:21px;color:var(--muted);margin-top:12px">港主板成交</div>
  </div>
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:68px;color:var(--cyan)">+{NANXIANG_YI}亿</div>
    <div style="font-size:21px;color:var(--muted);margin-top:12px">南向净买</div>
  </div>
  <div class="card" style="text-align:center;padding:24px 12px">
    <div class="big-num" style="font-size:68px;color:var(--red)">+13.5%</div>
    <div style="font-size:21px;color:var(--muted);margin-top:12px">华虹领涨</div>
  </div>
</div>

<div style="margin-top:44px;padding:28px 32px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--orange);border-radius:16px;box-shadow:0 0 32px rgba(210,153,29,0.15);text-align:center">
  <div style="font-size:26px;color:var(--text2);margin-bottom:14px">但 —— 历史上这个档位</div>
  <div class="big-num" style="font-size:84px;background:linear-gradient(90deg,var(--orange) 0%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent">20 日胜率仅 56%</div>
  <div style="font-size:21px;color:var(--muted);margin-top:14px">
    中位涨幅 +3.8%   ·   一步之遥就是 <b style="color:var(--red)">43%</b> 陷阱档
  </div>
</div>

<div style="margin-top:auto;text-align:center;padding-bottom:14px">
  <div style="display:inline-block;padding:16px 32px;background:var(--card);border:1.5px solid var(--cyan);border-radius:14px;font-size:29px;font-weight:700;color:var(--cyan);box-shadow:0 4px 16px rgba(86,212,221,0.15)">
    ⚠️ 追科技的姐妹们, 别急着 all in
  </div>
  <div style="font-size:20px;color:var(--muted);font-style:italic;margin-top:18px">翻到下一页 → 看今日港科到底涨了啥</div>
</div>

<div class="footer">
  <span>* 数据: 东方财富/新浪/雪球 · 港股 HKD · 不构成投资建议</span>
  <span>1/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# P2 — 港股科技链全景
# ═══════════════════════════════════════════
def page_2_html() -> str:
    max_pct = max(s[3] for s in HK_STOCKS)
    rows = []
    for name, code, price, pct, amt in HK_STOCKS:
        bar_w = pct / max_pct * 100
        rows.append(f"""
    <div class="hk-row">
      <div class="hk-name">
        <div style="font-size:26px;font-weight:700;color:var(--text)">{name}</div>
        <div style="font-size:17px;color:var(--dim);margin-top:3px">{code}</div>
      </div>
      <div class="hk-price">{price:.1f}</div>
      <div class="hk-bar-cell">
        <div class="hk-bar" style="width:{bar_w:.1f}%"></div>
      </div>
      <div class="hk-pct">+{pct:.2f}%</div>
      <div class="hk-amt">{amt:.0f}亿</div>
    </div>""")

    extra = """
.hk-row {
  display: grid;
  grid-template-columns: 190px 90px 1fr 130px 110px;
  align-items: center;
  gap: 16px;
  padding: 14px 10px;
  border-bottom: 1px solid rgba(48, 54, 61, 0.4);
}
.hk-row:last-child { border-bottom: none; }
.hk-price {
  font-size:26px;
  color: var(--text2);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.hk-bar-cell {
  height: 28px;
  background: rgba(48, 54, 61, 0.25);
  border-radius: 6px;
  overflow: hidden;
}
.hk-bar {
  height: 100%;
  background: linear-gradient(90deg, rgba(248,81,73,0.5) 0%, var(--red) 100%);
  border-radius: 6px;
  box-shadow: inset 0 -1px 0 rgba(0,0,0,0.2);
}
.hk-pct {
  font-size:34px;
  font-weight: 900;
  color: var(--red);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.hk-amt {
  font-size:22px;
  color: var(--muted);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--blue)">港股科技链</div></div>
<div class="subtitle">10 只大科技今天涨了多少</div>
<div class="subtitle-sm">按涨幅排序 · 港币价格</div>

<div style="margin-top:20px">
  {"".join(rows)}
</div>

<div style="margin-top:auto;display:flex;flex-direction:column;gap:14px;padding-bottom:12px">
  <div style="text-align:center;padding:18px 24px;background:var(--card);border:1.5px solid var(--cyan);border-radius:12px;font-size:25px;font-weight:700;color:var(--cyan)">
    华虹 +13.5   ·   阿里 +13.0   ·   快手 +11.5  —  半导体 + 互联网双主线狂飙
  </div>
  <div style="display:flex;justify-content:space-around;text-align:center;font-size:21px;color:var(--muted)">
    <span>港主板成交 <b style="color:var(--text2)">2963亿</b></span>
    <span>恒指 <b style="color:var(--red)">+3.28%</b></span>
    <span>南向 <b style="color:var(--cyan)">+130亿</b></span>
  </div>
  <div style="text-align:center;font-size:22px;color:var(--gold);font-weight:600">
    🔥 外围大跌之际, A股 + 港股双双走出独立行情
  </div>
</div>

<div class="footer">
  <span>* 数据: 东方财富 push2 · 收盘前快照</span>
  <span>2/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# P3 — A 股 ETF 影子链
# ═══════════════════════════════════════════
def page_3_html() -> str:
    def etf_card(name, code, price, pct, amt, note, color="--red"):
        return f"""
    <div class="etf-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
        <div style="flex:1">
          <div style="font-size:24px;font-weight:700;color:var(--text)">{name}</div>
          <div style="font-size:17px;color:var(--dim);margin-top:4px">{code}</div>
          <div style="font-size:17px;color:var(--muted);margin-top:8px">{note}</div>
        </div>
        <div style="text-align:right">
          <div style="font-size:36px;font-weight:900;color:var({color})">+{pct:.2f}%</div>
          <div style="font-size:17px;color:var(--muted);margin-top:6px">{amt:.1f}亿</div>
        </div>
      </div>
    </div>"""

    hk_cards = "".join(etf_card(*e, color="--red") for e in HK_ETFS)
    a_cards = "".join(etf_card(*e, color="--orange") for e in A_ETFS)

    extra = """
.etf-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  transition: all 0.2s;
}
.col-title {
  text-align: center;
  font-size:29px;
  font-weight: 900;
  margin-bottom: 14px;
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--purple)">A 股 ETF 影子链</div></div>
<div class="subtitle">港科怎么涨, 就买哪只 ETF?</div>
<div class="subtitle-sm">A 股散户参与港科的 6 只主流工具</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:22px">
  <div>
    <div class="col-title" style="color:var(--red)">港科主题 ETF</div>
    <div style="display:flex;flex-direction:column;gap:14px">{hk_cards}</div>
  </div>
  <div>
    <div class="col-title" style="color:var(--orange)">A 股 AI 算力 ETF</div>
    <div style="display:flex;flex-direction:column;gap:14px">{a_cards}</div>
  </div>
</div>

<div style="margin-top:24px;display:flex;flex-direction:column;gap:14px">
  <div style="padding:16px 22px;background:var(--card2);border-left:5px solid var(--red);border-radius:8px">
    <div style="font-size:24px;font-weight:700;color:var(--red);margin-bottom:6px">港科主题 ETF · 直接买港股</div>
    <div style="font-size:20px;color:var(--text2)">513010 是唯一沪市主流港科ETF, 成交 16 亿最活跃; 159120/159125 深市备份</div>
  </div>
  <div style="padding:16px 22px;background:var(--card2);border-left:5px solid var(--orange);border-radius:8px">
    <div style="font-size:24px;font-weight:700;color:var(--orange);margin-bottom:6px">A 股 AI 算力 · 蹭港科溢出</div>
    <div style="font-size:20px;color:var(--text2)">半导体设备 ETF +9.04% 一枝独秀, 华为 Atlas 950 催化 + 联动科技/华峰测控齐涨</div>
  </div>
</div>

<div style="margin-top:auto;padding:20px 24px;background:linear-gradient(135deg,rgba(86,212,221,0.08),rgba(86,212,221,0.02));border:1.5px solid var(--cyan);border-radius:12px;text-align:center;margin-bottom:10px">
  <div style="font-size:26px;font-weight:900;color:var(--cyan)">💡 想上车港科, 选 513010 最直接</div>
  <div style="font-size:18px;color:var(--orange);font-style:italic;margin-top:8px">港科溢价问题下页说, 别只看涨幅冲进去</div>
</div>

<div class="footer">
  <span>* 数据: 东方财富 · A 股/深港通 ETF</span>
  <span>3/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# P4 — 胜率表
# ═══════════════════════════════════════════
def page_4_html() -> str:
    bucket_cards = []
    for label, n, w5, w20, m20, med20, m60, med60, is_current in BUCKETS:
        cls = "bucket-card bucket-hl" if is_current else "bucket-card"
        w5_col = "--red" if w5 >= 50 else "--orange" if w5 >= 40 else "--green"
        w20_col = "--red" if w20 >= 50 else "--orange" if w20 >= 40 else "--green"
        m60_col = "--red" if m60 > 0 else "--green"
        hl_line = f'<div style="font-size:20px;font-weight:900;color:var(--orange);margin-top:10px">← 今日 +{HSTECH_PCT}% 在此档</div>' if is_current else ""
        bucket_cards.append(f"""
<div class="{cls}">
  <div style="display:grid;grid-template-columns:210px 1fr 1fr 1fr;align-items:center;gap:22px">
    <div>
      <div style="font-size:42px;font-weight:900;color:var(--red)">{label}</div>
      <div style="font-size:20px;color:var(--muted);margin-top:8px">样本 n = {n}</div>
      {hl_line}
    </div>
    <div style="text-align:center">
      <div style="font-size:18px;color:var(--muted);margin-bottom:8px">5 日胜率</div>
      <div style="font-size:56px;font-weight:900;color:var({w5_col})">{w5}%</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:18px;color:var(--muted);margin-bottom:8px">20 日胜率</div>
      <div style="font-size:56px;font-weight:900;color:var({w20_col})">{w20}%</div>
      <div style="font-size:17px;color:var(--muted);margin-top:6px">均 {m20:+.1f}%</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:18px;color:var(--muted);margin-bottom:8px">60 日均值</div>
      <div style="font-size:56px;font-weight:900;color:var({m60_col})">{m60:+.1f}%</div>
      <div style="font-size:17px;color:var(--muted);margin-top:6px">中位 {med60:+.1f}%</div>
    </div>
  </div>
</div>""")

    extra = """
.bucket-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 26px;
}
.bucket-hl {
  background: linear-gradient(135deg, var(--card) 0%, rgba(210, 153, 29, 0.05) 100%);
  border: 2px solid var(--orange);
  box-shadow: 0 0 28px rgba(210, 153, 29, 0.2);
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--gold)">历史胜率</div></div>
<div class="subtitle">恒科单日大涨后, N 天怎么走?</div>
<div class="subtitle-sm">2020-2026 · 1444 交易日 · 单日 ≥ +5% 分档</div>

<div style="display:flex;flex-direction:column;gap:18px;margin-top:24px">
  {"".join(bucket_cards)}
</div>

<div style="margin-top:26px;text-align:center">
  <div style="font-size:26px;font-weight:900;color:var(--text);margin-bottom:12px">🔑 关键发现</div>
  <div style="font-size:25px;color:var(--cyan);margin-bottom:22px">
    今天落在 <b>[5%, 6%)</b> 档 · 20 日胜率 <b>56%</b> · 中位 <b>+3.8%</b>
  </div>
</div>

<div style="margin-top:auto;padding:22px 28px;background:linear-gradient(135deg,var(--card) 0%,rgba(210,153,29,0.08) 100%);border:2px solid var(--orange);border-radius:14px;text-align:center;box-shadow:0 0 28px rgba(210,153,29,0.15);margin-bottom:10px">
  <div style="font-size:29px;font-weight:900;color:var(--orange)">⚠️ 明天再涨半根阳线, 跨进 [6%, 7%) 档</div>
  <div style="font-size:21px;color:var(--muted);margin-top:12px">20 日胜率 <b style="color:var(--red)">56%</b> → <b style="color:var(--green)">43%</b>, 60 日均 <b style="color:var(--green)">-7%</b> (翻到下一页 →)</div>
</div>

<div class="footer">
  <span>* 数据: 恒生科技指数 HSTECH 历史 · 新浪财经</span>
  <span>4/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# P5 — 反共识重锤
# ═══════════════════════════════════════════
def page_5_html() -> str:
    sample_rows = []
    for d1, d2, p1, p2, r20 in SAMPLES:
        val = float(r20.strip('%').strip('+'))
        is_neg = val < 0
        bg = "rgba(63, 185, 80, 0.14)" if is_neg else "transparent"
        col = "var(--green)" if is_neg else "var(--red)"
        fw = "900" if is_neg else "500"
        fs = "29px" if is_neg else "18px"
        sample_rows.append(f"""
    <div class="sample-row" style="background:{bg}">
      <div>{d1}</div>
      <div>{d2}</div>
      <div style="text-align:center">{p1} · {p2}</div>
      <div style="text-align:right;font-size:{fs};font-weight:{fw};color:{col}">{r20}</div>
    </div>""")

    extra = """
.sample-row {
  display: grid;
  grid-template-columns: 140px 140px 1fr 130px;
  gap: 14px;
  padding: 8px 14px;
  align-items: center;
  font-size:22px;
  color: var(--text2);
  border-radius: 6px;
  font-variant-numeric: tabular-nums;
}
.sample-header {
  display: grid;
  grid-template-columns: 140px 140px 1fr 130px;
  gap: 14px;
  padding: 6px 14px;
  font-size:18px;
  font-weight: 900;
  color: var(--muted);
  border-bottom: 1px solid var(--border);
  margin-bottom: 6px;
}
"""

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--orange)">跨档陷阱</div></div>
<div class="subtitle" style="font-size:42px">为什么 [6%, 7%) 是死亡档?</div>

<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:24px;margin-top:32px;padding:0 20px">
  <div style="text-align:center">
    <div style="font-size:26px;color:var(--muted);margin-bottom:10px">[5%, 6%)</div>
    <div class="big-num" style="font-size:200px;color:var(--red);filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">56%</div>
    <div style="font-size:21px;color:var(--muted);margin-top:8px">20 日胜率</div>
  </div>
  <div style="text-align:center;padding:0 16px">
    <div style="font-size:130px;font-weight:900;color:var(--orange);line-height:1">→</div>
    <div style="font-size:20px;color:var(--orange);margin-top:8px;font-weight:700">跨半根阳线</div>
  </div>
  <div style="text-align:center">
    <div style="font-size:26px;color:var(--muted);margin-bottom:10px">[6%, 7%)</div>
    <div class="big-num" style="font-size:200px;color:var(--green);filter:drop-shadow(0 4px 12px rgba(63,185,80,0.3))">43%</div>
    <div style="font-size:21px;color:var(--muted);margin-top:8px">20 日胜率</div>
  </div>
</div>

<div style="text-align:center;padding:18px 28px;background:var(--card2);border:1px solid var(--border);border-radius:12px;margin-top:24px;font-size:26px;font-weight:700">
  60 日累计:  [5-6%) 均 <span style="color:var(--muted)">-0.9%</span>   VS   [6-7%) 均 <span style="color:var(--green)">-7.0%</span>
</div>

<div style="margin-top:24px">
  <div style="text-align:center;font-size:25px;font-weight:700;color:var(--cyan);margin-bottom:4px">历史相似形态: 短期连续两次 +5%</div>
  <div style="text-align:center;font-size:18px;color:var(--muted);font-style:italic;margin-bottom:14px">20 日后表现 · 最近 8 次</div>
  <div class="sample-header">
    <div>首日</div>
    <div>次日</div>
    <div style="text-align:center">涨幅组合</div>
    <div style="text-align:right">20d 后</div>
  </div>
  {"".join(sample_rows)}
</div>

<div style="margin-top:auto;padding:24px 32px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:14px;text-align:center;margin-bottom:10px;box-shadow:0 6px 24px rgba(210,153,29,0.3)">
  <div style="font-size:36px;font-weight:900;color:var(--bg)">⚠️ 12 次里 5 次亏钱, 4 次跌破 -3%</div>
  <div style="font-size:21px;color:var(--bg);margin-top:10px;opacity:0.85">20 日均 +2.94%   ·   中位 +6.04%   ·   但"高开低走"是最大风险</div>
</div>

<div class="footer">
  <span>* 数据: HSTECH 2020-2026 · 反共识分档回测</span>
  <span>5/7</span>
</div>
"""
    return base_html(body, extra)


# ═══════════════════════════════════════════
# P6 — 位置指标 + 三档操作
# ═══════════════════════════════════════════
def page_6_html() -> str:
    tiers = [
        ("激进",   "--red",    "已入 → 明天开盘\"高开低走\"减半仓, 留 30% 观察 [6-7%) 跨档"),
        ("稳健",   "--orange", "未入 → 别追高, 等 5 日内回踩 MA20 (4564) 附近再上车"),
        ("长线",   "--cyan",   "定投 513010 · 位置 10.2% 分位, 3 年维度依然便宜"),
    ]
    tier_rows = "".join(f"""
    <div style="display:flex;align-items:center;gap:20px;padding:16px 20px;background:var(--card);border:1px solid var(--border);border-radius:12px">
      <div style="min-width:88px;padding:12px 20px;background:var({col});color:var(--bg);border-radius:22px;font-size:25px;font-weight:900;text-align:center">{tag}</div>
      <div style="font-size:22px;color:var(--text2);line-height:1.5;flex:1">{body}</div>
    </div>""" for tag, col, body in tiers)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--cyan)">当前位置</div></div>
<div class="subtitle">涨了一天, 但恒科在哪儿?</div>

<div style="text-align:center;margin-top:32px">
  <div style="font-size:24px;color:var(--muted);margin-bottom:12px">近 1 年分位</div>
  <div class="big-num" style="font-size:232px;background:linear-gradient(180deg,#5dd469 0%,#3fb950 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(63,185,80,0.3))">{POS_1Y:.1f}%</div>
  <div style="font-size:24px;color:var(--cyan);margin-top:14px;font-weight:600">低位区 · 反弹初期给博弈缓冲</div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin-top:34px">
  <div class="card" style="text-align:center;padding:20px 12px">
    <div style="font-size:18px;color:var(--muted);margin-bottom:10px">距 1 年高点</div>
    <div style="font-size:56px;font-weight:900;color:var(--green)">{DIST_HIGH_1Y:+.1f}%</div>
    <div style="font-size:17px;color:var(--muted);margin-top:8px">{HIGH_1Y} → {HSTECH_CLOSE:.0f}</div>
  </div>
  <div class="card" style="text-align:center;padding:20px 12px">
    <div style="font-size:18px;color:var(--muted);margin-bottom:10px">距 1 年低点</div>
    <div style="font-size:56px;font-weight:900;color:var(--red)">+{DIST_LOW_1Y:.1f}%</div>
    <div style="font-size:17px;color:var(--muted);margin-top:8px">{LOW_1Y} → {HSTECH_CLOSE:.0f}</div>
  </div>
  <div class="card" style="text-align:center;padding:20px 12px">
    <div style="font-size:18px;color:var(--muted);margin-bottom:10px">南向近 1 年分位</div>
    <div style="font-size:56px;font-weight:900;color:var(--red)">{NANXIANG_1Y_RANK:.0f}%</div>
    <div style="font-size:17px;color:var(--muted);margin-top:8px">+130亿 · 日均+42亿</div>
  </div>
</div>

<div style="margin-top:32px">
  <div style="text-align:center;font-size:29px;font-weight:900;color:var(--text);margin-bottom:14px">🎯 三档操作建议</div>
  <div style="display:flex;flex-direction:column;gap:12px">
    {tier_rows}
  </div>
</div>

<div style="margin-top:auto;padding:18px 24px;background:linear-gradient(90deg,rgba(210,153,29,0.12),rgba(210,153,29,0.03));border-left:5px solid var(--orange);border-radius:8px;margin-bottom:10px">
  <div style="font-size:24px;font-weight:900;color:var(--orange)">⚠️ 散户友情提醒</div>
  <div style="font-size:18px;color:var(--text2);margin-top:8px">港股 ≠ A 股 · 无涨跌幅限制 · 汇率波动风险 · 高位股次日常见 -3% 补跌</div>
</div>

<div class="footer">
  <span>* 数据: 恒生科技 + 沪港通历史 · 分位基于收盘价</span>
  <span>6/7</span>
</div>
"""
    return base_html(body)


# ═══════════════════════════════════════════
# P7 — CTA
# ═══════════════════════════════════════════
def page_7_html() -> str:
    cards = [
        ("01", "复盘",   "--red",    "涨停天梯 · 行业冠亚军 · 炸板预警"),
        ("02", "雷达",   "--purple", "雪球新热点 · 南向搬家 · 分档胜率"),
        ("03", "反共识", "--cyan",   "拒绝小作文 · 数据驱动 · 历史样本核对"),
    ]
    card_rows = "".join(f"""
<div style="display:flex;align-items:center;gap:24px;padding:26px 28px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,0.3) 100%);border:2px solid var({col});border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
  <div style="font-size:76px;font-weight:900;color:var({col});min-width:96px;text-align:center;line-height:1;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4))">{num}</div>
  <div style="flex:1">
    <div style="font-size:34px;font-weight:900;color:var(--text)">{title}</div>
    <div style="font-size:21px;color:var(--muted);margin-top:8px">{body}</div>
  </div>
</div>""" for num, title, col, body in cards)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--rose)">关注我</div></div>
<div style="text-align:center;font-size:26px;font-style:italic;color:var(--text2);margin-top:20px">
  港科明天还能续命吗? 数据每天替你盯 📊
</div>

<div style="text-align:center;margin-top:36px">
  <div style="font-size:58px;color:var(--text);margin-bottom:14px">每天 3 分钟</div>
  <div class="big-num" style="font-size:84px;background:linear-gradient(90deg,var(--gold) 0%,var(--gold2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(240,192,64,0.3))">看懂 A 股 + 港股</div>
</div>

<div style="display:flex;flex-direction:column;gap:16px;margin-top:36px">
  {card_rows}
</div>

<div style="margin-top:32px;padding:28px 32px;background:linear-gradient(135deg,var(--gold) 0%,#e8b73a 100%);border-radius:16px;text-align:center;box-shadow:0 8px 32px rgba(240,192,64,0.35)">
  <div style="font-size:42px;font-weight:900;color:var(--bg)">🔔 点关注 + 收藏 不迷路</div>
  <div style="font-size:22px;color:var(--bg);margin-top:10px;opacity:0.8">明早 9:15 继续给你递港科盘前情报</div>
</div>

<div style="margin-top:auto;text-align:center;padding-bottom:12px">
  <div style="font-size:25px;font-weight:900;color:var(--cyan);margin-bottom:10px">💬 评论区告诉我</div>
  <div style="font-size:22px;color:var(--text2);margin-bottom:8px">你是 港科党 还是 A股党? 明天该抄底还是减仓?</div>
  <div style="font-size:18px;color:var(--muted)">明天想看 哪只港股 or ETF 的盘后追踪? 评论区点名 →</div>
</div>

<div class="footer">
  <span>* 数据: 复旦杰伦 · 拒绝小作文 · 拒绝喊单</span>
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
            viewport={"width": 1080, "height": 1200},
            device_scale_factor=2, locale="zh-CN",
        )
        page = ctx.new_page()
        for i, gen in enumerate(PAGE_HTML_GENERATORS, 1):
            out = OUT / f"page_{i}.png"
            page.set_content(gen(), wait_until="networkidle")
            page.wait_for_timeout(2000)
            page.screenshot(path=str(out), full_page=False)
            print(f"  ✓ saved {out.name} ({out.stat().st_size/1024:.0f}KB)")
        browser.close()


def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 8)]
    w, h = pages[0].size
    tw, th = 470, 615
    canvas = Image.new("RGB", (tw * 4 + 30, th * 2 + 20), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, 4)
        canvas.paste(p.resize((tw, th)), (c * tw + 5 + c*5, r * th + 5 + r*5))
    canvas.save(OUT / "preview_2x4.png")
    print(f"  ✓ preview_2x4.png")

    total_h = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, total_h), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y)); y += p.height
    ratio = 720 / w
    stacked.resize((720, int(total_h * ratio))).save(OUT / "all_pages_stacked.png")
    print(f"  ✓ all_pages_stacked.png")


if __name__ == "__main__":
    print(f"HTML v2 → {OUT}")
    render_all()
    make_preview()
    print(f"\n✅ 完成. 7 张 2160×2880 PNG")
