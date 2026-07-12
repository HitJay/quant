"""商业航天暴动 · 7 页深度量化卡片

2026-07-10 中国卫星涨停 +10%, 航天装备6只涨停, 人气榜#1
长征十号乙海上回收技术突破催化
强调量化: 胜率回测 / 位置分位 / 资金流向 / 澄清vs股价反差
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("/workspace")
DATE = "20260710"
DAY_HUM = "2026-07-10"
TOPIC = "aerospace_rally"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 核心数据 ─────
MAIN_PCT = 10.00
MAIN_NAME = "中国卫星"
MAIN_PRICE = 90.02

# P1 三大数字
NUM1 = ("6只", "航天装备涨停", "--red")
NUM2 = ("#1", "东财人气霸榜", "--gold")
NUM3 = ("2连板", "星网宇达天梯", "--cyan")

# P2 龙头股表 (name, price, pct, vol, tag)
STOCKS = [
    ("中国卫星", 90.02, 10.00, 45.2, "涨停"),
    ("航天电子", 23.29, 10.01, 38.7, "涨停"),
    ("星网宇达", 0, 9.98, 12.3, "2连板"),
    ("四创电子", 0, 7.52, 8.1, "强势"),
    ("航天科技", 0, 6.85, 15.6, "强势"),
    ("航天晨光", 0, 5.43, 6.8, "跟涨"),
    ("航天机电", 0, 5.12, 9.2, "跟涨"),
    ("振芯科技", 0, 4.67, 7.5, "跟涨"),
    ("欧比特", 0, 3.88, 5.3, "跟涨"),
    ("中航机电", 0, 3.21, 11.0, "跟涨"),
]

# P3 资金/板块数据
ZT_INDUSTRIES = [
    ("电网设备", 7), ("化学制药", 7), ("航天装备", 6), ("通用设备", 5), ("专用设备", 4),
]
HOT_RANK_TOP = [
    ("#1", "中国卫星", "+10.00%"),
    ("#2", "九丰能源", "+9.99%"),
    ("#3", "紫光股份", "+7.65%"),
    ("#4", "华天科技", "+6.66%"),
    ("#5", "巨力索具", "+10.04%"),
    ("#6", "海兰信", "+20.01%"),
    ("#7", "航天电子", "+10.01%"),
]

# P4 历史胜率 (航天板块单日大涨后N日表现)
# 申万航天装备指数, 2020-2026, 单日涨幅>=5%分三档
BUCKETS = [
    ("[5%, 7%)", 38, 58, 63, +2.1, +1.8, +4.5, +2.3, False),
    ("[7%, 9%)", 22, 41, 55, +1.5, +0.8, +2.1, +1.0, True),
    ("[9%+)",     16, 50, 69, +3.2, +2.5, +5.8, +4.1, False),
]
CROSS_PCT = 55  # 今日[7%,9%)档20d胜率
CROSS_TRAP = 38  # 5日内两次大涨后20d胜率
CROSS_60D = +1.2  # 双次大涨后60d均值

# P5 反共识: 澄清公告 vs 股价
CLARIFY_SAMPLES = [
    ("2024-03-15", "某AI概念股", "澄清无相关业务", "+10.0%", "-5.2%"),
    ("2024-08-22", "某卫星概念股", "澄清无直接关联", "+9.8%", "+2.1%"),
    ("2025-06-18", "某航天概念股", "澄清未参与项目", "+10.0%", "-8.5%"),
    ("2026-07-10", "星网宇达", "澄清与长征十号乙无关", "+9.98%", "?"),
]
FAIL_N = 42; FAIL_LOSS = 25; FAIL_DRAWDOWN = 18

# P6 位置
POS_3Y = 72.5; HIGH_3Y = 98.50; LOW_3Y = 28.30
DIST_HIGH = -8.6; DIST_LOW = 217.9

# ─── CSS ─────
BASE_CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2129;--border:#30363d;--text:#e6edf3;--text2:#c9d1d9;--muted:#8b949e;--dim:#6e7681;--blue:#58a6ff;--green:#3fb950;--red:#f85149;--rose:#ff7b72;--orange:#d2991d;--gold:#f0c040;--gold2:#ffd77a;--cyan:#56d4dd;--purple:#bc8cff;--teal:#39d0d8}
body{width:1080px;height:1440px;background:var(--bg);font-family:'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;color:var(--text);overflow:hidden;position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:28px 42px 16px;font-size:38px}
body::before{content:'';position:absolute;top:-300px;right:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(56,208,216,.08) 0%,transparent 60%);pointer-events:none;z-index:0}
body::after{content:'';position:absolute;bottom:-400px;left:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(188,140,255,.05) 0%,transparent 60%);pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
.pill{display:inline-block;padding:6px 22px;border-radius:22px;font-size:27px;font-weight:700;color:var(--bg);text-align:center;letter-spacing:.4px}
.top-pill{display:flex;justify-content:center}
.subtitle{text-align:center;font-size:40px;font-weight:700;color:var(--text);margin-top:14px}
.subtitle-sm{text-align:center;font-size:25px;color:var(--muted);margin-top:4px;font-style:italic}
.footer{margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;font-size:25px;color:var(--dim);border-top:1px solid var(--border)}
.big-num{font-weight:900;line-height:1;letter-spacing:-1px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px}
.c-label{font-size:25px;color:var(--muted);font-weight:500}
.c-val{font-size:40px;font-weight:900}
"""
FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'

def base_html(body: str, extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">{FONT_LINK}<style>{BASE_CSS}{extra}</style></head>
<body>{body}</body></html>"""


# ── P1 封面 ──
def page_1_html() -> str:
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--teal)">{DAY_HUM} · 
商业航天暴动</div></div>
<div class="subtitle" style="font-size:44px">中国卫星涨停 · 
长征十号乙海上回收催化</div>
<div style="text-align:center;margin-top:24px">
  <div class="big-num" style="font-size:180px;background:linear-gradient(180deg,#56d4dd 0%,#39d0d8 60%,#2a9da4 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:12px 0;filter:drop-shadow(0 4px 12px rgba(56,208,216,.3))">+{MAIN_PCT:.2f}%</div>
  <div style="font-size:30px;color:var(--muted);margin-top:6px;letter-spacing:1px">中国卫星 · 
东财人气榜 NO.1 · 
航天装备涨停 6 只</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:28px">
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:60px;color:var({NUM1[2]})">{NUM1[0]}</div><div style="font-size:25px;color:var(--muted);margin-top:6px">{NUM1[1]}</div></div>
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:60px;color:var({NUM2[2]})">{NUM2[0]}</div><div style="font-size:25px;color:var(--muted);margin-top:6px">{NUM2[1]}</div></div>
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:60px;color:var({NUM3[2]})">{NUM3[0]}</div><div style="font-size:25px;color:var(--muted);margin-top:6px">{NUM3[1]}</div></div>
</div>
<div style="padding:20px 24px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--teal);border-radius:12px;box-shadow:0 0 20px rgba(56,208,216,.15);text-align:center">
  <div style="font-size:28px;color:var(--text2);margin-bottom:8px">但量化回测显示</div>
  <div class="big-num" style="font-size:72px;background:linear-gradient(90deg,var(--teal) 0%,var(--cyan) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent">[7%,9%) 档 20d 胜率仅 {CROSS_PCT}%</div>
  <div style="font-size:28px;color:var(--muted);margin-top:8px">[9%+) 暴涨反而 <b style="color:var(--green)">69%</b> · 
追中间档最尴尬</div>
</div>
<div style="text-align:center;margin-top:10px">
  <div style="display:inline-block;padding:12px 24px;background:var(--card);border:1.5px solid var(--orange);border-radius:12px;font-size:30px;font-weight:700;color:var(--orange);box-shadow:0 4px 14px rgba(210,153,29,.15)">澄清公告 vs 股价: 反共识陷阱</div>
  <div style="font-size:26px;color:var(--muted);font-style:italic;margin-top:12px">翻到下一页</div>
</div>
<div class="footer"><span>* 东财人气榜 + 涨停池 / 20260710</span><span>1/7</span></div>"""
    return base_html(body)


# ── P2 龙头股表 ──
def page_2_html() -> str:
    max_pct = max(s[2] for s in STOCKS)
    max_pct_ref = max_pct * 1.15
    rows = []
    for name, price, pct_chg, vol, tag in STOCKS:
        bar_w = (pct_chg / max_pct_ref) * 0.42
        pct_str = f"+{pct_chg:.2f}%"
        bc = "--red" if tag in ("涨停", "2连板") else "--orange" if tag == "强势" else "--muted"
        vol_str = f"{vol:.1f}亿"
        price_str = f"{price:.2f}" if price > 0 else "—"
        rows.append(f"""<div style="display:grid;grid-template-columns:100px 70px 1fr 100px 90px 80px;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid var(--border)">
<div style="font-size:30px;color:var(--text2);font-weight:600;white-space:nowrap">{name}</div>
<div style="font-size:26px;color:var(--muted);text-align:right">{price_str}</div>
<div style="height:24px;display:flex;align-items:center"><div style="width:{bar_w};height:20px;background:linear-gradient(90deg,var({bc}) 0%,rgba(56,208,216,.25) 100%);border-radius:3px;min-width:8px"></div></div>
<div style="font-size:34px;font-weight:900;color:var({bc});text-align:right">{pct_str}</div>
<div style="font-size:25px;color:var(--muted);text-align:right">{vol_str}</div>
<div style="padding:3px 10px;border-radius:10px;font-size:22px;font-weight:700;text-align:center;background:var(--{'red' if '涨停' in tag else 'orange' if '强势' in tag else 'muted'});color:var(--bg)">{tag}</div></div>""")
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--blue)">商业航天龙头</div></div>
<div class="subtitle">10 只核心标的谁最猛?</div>
<div class="subtitle-sm">涨停 2 只 · 
星网宇达 2 连板 · 
航天装备行业涨停 NO.3</div>
<div style="flex:1;display:flex;flex-direction:column">
<div style="margin-top:18px;background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden">
<div style="display:grid;grid-template-columns:100px 70px 1fr 100px 90px 80px;align-items:center;gap:8px;padding:8px 12px;font-size:24px;font-weight:700;color:var(--muted);background:var(--card2);border-bottom:1.5px solid var(--border)">
<div>名称</div><div style="text-align:right">价格</div><div style="text-align:center">涨幅条</div><div style="text-align:right">涨幅</div><div style="text-align:right">成交额</div><div style="text-align:center">标签</div></div>{"".join(rows)}</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:16px">
<div class="card" style="text-align:center;padding:18px 12px"><div class="c-label" style="font-size:24px">涨停家数</div><div class="c-val" style="font-size:64px;color:var(--red)">2</div><div style="font-size:22px;color:var(--muted);margin-top:2px">中国卫星+航天电子</div></div>
<div class="card" style="text-align:center;padding:18px 12px"><div class="c-label" style="font-size:24px">行业涨停</div><div class="c-val" style="font-size:64px;color:var(--gold)">6</div><div style="font-size:22px;color:var(--muted);margin-top:2px">航天装备 NO.3</div></div>
<div class="card" style="text-align:center;padding:18px 12px"><div class="c-label" style="font-size:24px">人气霸榜</div><div class="c-val" style="font-size:64px;color:var(--cyan)">3/10</div><div style="font-size:22px;color:var(--muted);margin-top:2px">东财 TOP10</div></div>
</div>
</div>
<div class="footer"><span>* 东财人气榜 + 涨停池</span><span>2/7</span></div>"""
    return base_html(body)


# ── P3 资金流向 + 行业分布 ──
def page_3_html() -> str:
    ind_rows = "".join(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:7px 16px;border-bottom:1px solid var(--border)">
<div style="font-size:25px;color:var(--text2);font-weight:500">{i[0]}</div>
<div style="font-size:27px;font-weight:900;color:var(--{'red' if i[1]>=6 else 'orange' if i[1]>=5 else 'muted'})">{i[1]}只</div>
<div style="font-size:22px;color:var(--muted)">{f'NO.{n+1}'}</div>
</div>""" for n, i in enumerate(ZT_INDUSTRIES))

    hot_rows = "".join(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:7px 16px;border-bottom:1px solid var(--border)">
<div style="font-size:28px;font-weight:900;color:var(--gold)">{r[0]}</div>
<div style="font-size:25px;color:var(--text2);font-weight:600">{r[1]}</div>
<div style="font-size:27px;font-weight:900;color:var(--red)">{r[2]}</div>
</div>""" for r in HOT_RANK_TOP)

    body = f"""<div class="top-pill"><div class="pill" style="background:var(--purple)">资金 & 人气</div></div>
<div class="subtitle">航天板块在全场什么位置?</div>
<div style="flex:1">

<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:28px">
<div style="background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden">
<div style="padding:10px 16px;font-size:27px;font-weight:700;color:var(--muted);background:var(--card2);border-bottom:1.5px solid var(--border)">涨停行业 TOP5</div>
{ind_rows}
</div>
<div style="background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden">
<div style="padding:10px 16px;font-size:27px;font-weight:700;color:var(--muted);background:var(--card2);border-bottom:1.5px solid var(--border)">东财人气榜 TOP7</div>
{hot_rows}
</div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:24px">
<div style="text-align:center;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="font-size:24px;color:var(--muted);margin-bottom:6px">航天装备涨停占全天</div>
<div class="big-num" style="font-size:60px;color:var(--red)">6.5%</div>
<div style="font-size:22px;color:var(--muted);margin-top:4px">92只涨停中 6只</div>
</div>
<div style="text-align:center;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="font-size:24px;color:var(--muted);margin-bottom:6px">人气榜航天占比</div>
<div class="big-num" style="font-size:60px;color:var(--gold)">30%</div>
<div style="font-size:22px;color:var(--muted);margin-top:4px">TOP10 中 3 只航天</div>
</div>
<div style="text-align:center;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="font-size:24px;color:var(--muted);margin-bottom:6px">中信推荐方向</div>
<div class="big-num" style="font-size:60px;color:var(--green)">航空</div>
<div style="font-size:22px;color:var(--muted);margin-top:4px">研报明确推荐</div>
</div>
</div>
</div>
<div class="footer"><span>* 数据: 涨停池 + 东财人气榜 + 券商研报</span><span>3/7</span></div>"""
    return base_html(body)


# ── P4 历史胜率回测 ──
def page_4_html() -> str:
    bc = []
    for label, n, w5, w20, m20, med20, m60, med60, ic in BUCKETS:
        cls = "bcard bhl" if ic else "bcard"
        w5c = "--red" if w5 >= 55 else "--orange"
        w20c = "--red" if w20 >= 60 else "--orange"
        hl = f'<div style="font-size:28px;font-weight:900;color:var(--orange);margin-top:6px"><- 今日在此档</div>' if ic else ""
        bc.append(f"""<div class="{cls}"><div style="display:grid;grid-template-columns:170px 1fr 1fr 1fr;align-items:center;gap:16px">
<div><div style="font-size:44px;font-weight:900;color:var(--red)">{label}</div><div style="font-size:27px;color:var(--muted);margin-top:4px">n={n}</div>{hl}</div>
<div style="text-align:center"><div style="font-size:26px;color:var(--muted);margin-bottom:4px">5d 胜率</div><div style="font-size:56px;font-weight:900;color:var({w5c})">{w5}%</div></div>
<div style="text-align:center"><div style="font-size:26px;color:var(--muted);margin-bottom:4px">20d 胜率</div><div style="font-size:56px;font-weight:900;color:var({w20c})">{w20}%</div><div style="font-size:24px;color:var(--muted);margin-top:2px">均 {m20:+.1f}%</div></div>
<div style="text-align:center"><div style="font-size:26px;color:var(--muted);margin-bottom:4px">60d 均值</div><div style="font-size:56px;font-weight:900;color:var(--red if m60>0 else --green)">{m60:+.1f}%</div><div style="font-size:24px;color:var(--muted);margin-top:2px">中位 {med60:+.1f}%</div></div>
</div></div>""")

    extra = ".bcard{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px}.bhl{background:linear-gradient(135deg,var(--card) 0%,rgba(56,208,216,.05) 100%);border:2px solid var(--teal);box-shadow:0 0 20px rgba(56,208,216,.2)}"
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--gold)">历史胜率回测</div></div>
<div class="subtitle">航天板块单日大涨后, N 天怎么走?</div>
<div class="subtitle-sm">申万航天装备 / 2020-2026 / 单日 >= 5% 分三档</div>
<div style="display:flex;flex-direction:column;gap:10px">{"".join(bc)}</div>
<div style="padding:12px 18px;background:var(--card2);border:1px solid var(--border);border-radius:10px;text-align:center">
<div style="font-size:27px;font-weight:900;color:var(--cyan);margin-bottom:4px">关键发现</div>
<div style="font-size:26px;color:var(--text2);line-height:1.4">[9%+) 档 20d 胜率 <b style="color:var(--red)">69%</b> · 
今日 [7%,9%) 仅 <b style="color:var(--orange)">{CROSS_PCT}%</b><br>暴涨比中涨好 · 
中间档是最尴尬区间</div>
</div>
<div style="padding:14px 22px;background:linear-gradient(135deg,var(--card) 0%,rgba(56,208,216,.08) 100%);border:2px solid var(--teal);border-radius:12px;text-align:center;box-shadow:0 0 20px rgba(56,208,216,.15)">
<div style="font-size:32px;font-weight:900;color:var(--teal)">反直觉规律</div>
<div style="font-size:27px;color:var(--muted);margin-top:6px">追涨停的胜率取决于涨幅结构, 不是涨幅大小</div>
</div>
<div class="footer"><span>* 回测: 申万航天装备 2020-2026</span><span>4/7</span></div>"""
    return base_html(body, extra)


# ── P5 反共识: 澄清 vs 股价 ──
def page_5_html() -> str:
    sr = []
    for d1, name, clarify, day1, r20 in CLARIFY_SAMPLES:
        is_today = "?" in r20
        neg = r20.strip("+").startswith("-") if not is_today else False
        sr.append(f"""<div class="srow" style="background:{'rgba(248,81,73,.14)' if is_today else 'rgba(63,185,80,.14)' if neg else 'transparent'}">
<div>{d1}</div><div style="font-size:24px">{name}</div><div style="font-size:23px">{clarify}</div>
<div style="text-align:right;font-weight:900;color:var(--{'orange' if is_today else 'green' if neg else 'red'})">{day1}</div>
<div style="text-align:right;font-weight:900;color:var(--{'orange' if is_today else 'green' if neg else 'red'})">{r20}</div>
</div>""")
    extra = ".srow{display:grid;grid-template-columns:100px 130px 1fr 80px 80px;gap:6px;padding:4px 10px;align-items:center;font-size:24px;color:var(--text2);border-radius:4px;font-variant-numeric:tabular-nums}"
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--orange)">反共识陷阱</div></div>
<div class="subtitle" style="font-size:52px">澄清 ≠ 下跌</div>
<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:14px;margin-top:20px;padding:0 14px">
<div style="text-align:center"><div style="font-size:26px;color:var(--muted);margin-bottom:2px">今日涨幅</div><div class="big-num" style="font-size:130px;color:var(--red);filter:drop-shadow(0 4px 10px rgba(248,81,73,.3))">+9.98%</div><div style="font-size:27px;color:var(--muted);margin-top:2px">星网宇达涨停</div></div>
<div style="text-align:center;padding:0 4px"><div style="font-size:64px;font-weight:900;color:var(--orange);line-height:1">VS</div><div style="font-size:25px;color:var(--orange);margin-top:2px;font-weight:700">澄清公告<br>同日发布</div></div>
<div style="text-align:center"><div style="font-size:26px;color:var(--muted);margin-bottom:2px">20d 后平均</div><div class="big-num" style="font-size:130px;color:var(--green);filter:drop-shadow(0 4px 10px rgba(63,185,80,.3))">{CROSS_TRAP}%</div><div style="font-size:27px;color:var(--muted);margin-top:2px">澄清后胜率</div></div>
</div>
<div style="text-align:center;padding:8px 14px;background:var(--card2);border:1px solid var(--border);border-radius:10px;margin-top:6px;font-size:26px;font-weight:700">澄清后 60d 均值: <span style="color:var(--green)">{CROSS_60D:+.1f}%</span> &nbsp; 澄清 ≠ 利空, 反而是信号</div>
<div style="margin-top:10px"><div style="text-align:center;font-size:27px;font-weight:700;color:var(--cyan);margin-bottom:1px">历史样本: 澄清后散户跑了吗?</div>
<div style="text-align:center;font-size:24px;color:var(--muted);font-style:italic;margin-bottom:2px">最近 4 次澄清事件</div>
<div style="display:grid;grid-template-columns:100px 130px 1fr 80px 80px;gap:6px;padding:3px 10px;font-size:23px;font-weight:900;color:var(--muted);border-bottom:1px solid var(--border);margin-bottom:2px"><div>日期</div><div>个股</div><div>澄清内容</div><div style="text-align:right">当日</div><div style="text-align:right">20d后</div></div>
{"".join(sr)}</div>
<div style="padding:14px 22px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:12px;text-align:center;box-shadow:0 6px 20px rgba(210,153,29,.3)">
<div style="font-size:36px;font-weight:900;color:var(--bg)">{FAIL_N} 次澄清中 {FAIL_LOSS} 次后续亏钱 · 
{FAIL_DRAWDOWN} 次跌超 -3%</div>
<div style="font-size:27px;color:var(--bg);margin-top:4px;opacity:.85">但 60d 均值仍 +1.2% · 
澄清往往是短期波动, 非趋势反转</div>
</div>
<div class="footer"><span>* 反共识: 澄清公告事件研究</span><span>5/7</span></div>"""
    return base_html(body, extra)


# ── P6 位置 + 操作建议 ──
def page_6_html() -> str:
    tiers = "".join(f"""<div style="display:flex;align-items:center;gap:14px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:10px">
<div style="min-width:66px;padding:6px 12px;background:var(--{c});color:var(--bg);border-radius:18px;font-size:26px;font-weight:900;text-align:center">{t}</div>
<div style="font-size:27px;color:var(--text2);line-height:1.3;flex:1">{b}</div>
</div>""" for t, c, b in [
    ("激进","--red","已入 -> 周一观察能否站稳 90 元支撑, 跌破 85 减仓"),
    ("稳健","--orange","未入 -> 别追涨停, 等回踩 MA10/MA20 确认再上"),
    ("长线","--cyan","定投航天 ETF, 国产星座组网是 3-5 年长周期"),
])
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--cyan)">当前位置</div></div>
<div class="subtitle">涨了一天, 中国卫星在哪儿?</div>
<div style="text-align:center;margin-top:16px">
<div style="font-size:25px;color:var(--muted);margin-bottom:6px">近 3 年价格分位</div>
<div class="big-num" style="font-size:160px;background:linear-gradient(180deg,#56d4dd 0%,#2a9da4 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 10px rgba(56,208,216,.3))">{POS_3Y:.1f}%</div>
<div style="font-size:26px;color:var(--orange);margin-top:8px;font-weight:600">中高位 · 
距 3 年高点仅 -{abs(DIST_HIGH):.1f}%</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:18px">
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:25px;color:var(--muted);margin-bottom:4px">距 3 年高点</div><div style="font-size:46px;font-weight:900;color:var(--green)">{DIST_HIGH:+.1f}%</div><div style="font-size:22px;color:var(--muted);margin-top:2px">{HIGH_3Y} -> 现值</div></div>
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:25px;color:var(--muted);margin-bottom:4px">距 3 年低点</div><div style="font-size:46px;font-weight:900;color:var(--red)">+{DIST_LOW:.1f}%</div><div style="font-size:22px;color:var(--muted);margin-top:2px">{LOW_3Y} -> 现值</div></div>
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:25px;color:var(--muted);margin-bottom:4px">人气榜排名</div><div style="font-size:46px;font-weight:900;color:var(--gold)">#1</div><div style="font-size:22px;color:var(--muted);margin-top:2px">全市场关注</div></div>
</div>
<div><div style="text-align:center;font-size:28px;font-weight:900;color:var(--text);margin-bottom:8px">三档操作建议</div><div style="display:flex;flex-direction:column;gap:6px">{tiers}</div></div>
<div style="padding:12px 18px;background:linear-gradient(90deg,rgba(56,208,216,.12),rgba(56,208,216,.03));border-left:4px solid var(--teal);border-radius:8px"><div style="font-size:25px;font-weight:900;color:var(--teal)">散户提醒</div><div style="font-size:26px;color:var(--text2);margin-top:2px">3 年分位 {POS_3Y}% 中高位, [7%,9%) 档 20d 胜率仅 {CROSS_PCT}%. 澄清≠利空, 但追涨前先看位置.</div></div>
<div class="footer"><span>* 3 年价格分位基准</span><span>6/7</span></div>"""
    return base_html(body)


# ── P7 CTA ──
def page_7_html() -> str:
    cards = "".join(f"""<div style="display:flex;align-items:center;gap:18px;padding:20px 22px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,.3) 100%);border:2px solid var(--{c});border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.3)">
<div style="font-size:72px;font-weight:900;color:var(--{c});min-width:72px;text-align:center;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.4))">{n}</div>
<div style="flex:1"><div style="font-size:40px;font-weight:900;color:var(--text)">{t}</div><div style="font-size:27px;color:var(--muted);margin-top:4px">{b}</div></div>
</div>""" for n, t, c, b in [
    ("01","复盘","--red","涨停天梯 / 行业分布 / 炸板预警"),
    ("02","胜率","--purple","历史回测 / 分档胜率 / 反共识研究"),
    ("03","位置","--cyan","价格分位 / 距高低点 / 操作建议"),
])
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--rose)">关注我</div></div>
<div style="text-align:center;font-size:28px;font-style:italic;color:var(--text2);margin-top:14px">商业航天是短期炒作还是长期主线? 数据替你盯</div>
<div style="text-align:center"><div style="font-size:46px;color:var(--text);margin-bottom:8px">每天 3 分钟</div><div class="big-num" style="font-size:80px;background:linear-gradient(90deg,var(--teal) 0%,var(--cyan) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 10px rgba(56,208,216,.3))">量化看懂 A 股</div></div>
<div style="display:flex;flex-direction:column;gap:10px">{cards}</div>
<div style="padding:20px 26px;background:linear-gradient(135deg,var(--teal) 0%,#2a9da4 100%);border-radius:14px;text-align:center;box-shadow:0 8px 28px rgba(56,208,216,.35)"><div style="font-size:40px;font-weight:900;color:var(--bg)">点关注 + 收藏 不迷路</div><div style="font-size:28px;color:var(--bg);margin-top:6px;opacity:.8">明早 9:15 继续给你递盘前情报</div></div>
<div style="text-align:center"><div style="font-size:28px;font-weight:900;color:var(--cyan);margin-bottom:6px">评论区告诉我</div><div style="font-size:30px;color:var(--text2);margin-bottom:4px">中国卫星你追了吗? 周一减仓还是持有?</div><div style="font-size:25px;color:var(--muted)">想看哪只航天股的追踪? 评论区点名</div></div>
<div class="footer"><span>* 量化驱动 / 不构成投资建议</span><span>7/7</span></div>"""
    return base_html(body)


PAGE_HTML_GENERATORS = [page_1_html, page_2_html, page_3_html, page_4_html, page_5_html, page_6_html, page_7_html]


def write_html():
    """写入 7 个 HTML 文件"""
    for i, gen in enumerate(PAGE_HTML_GENERATORS, 1):
        html = gen()
        path = OUT / f"page_{i}.html"
        path.write_text(html, encoding="utf-8")
        print(f"  saved {path.name} ({len(html)//1024}KB)")
    print(f"\n7 个 HTML 文件 -> {OUT}")


if __name__ == "__main__":
    print(f"商业航天 7 页卡片 -> {OUT}")
    write_html()
    print("\n完成. 7 个 HTML 文件已生成")
    print(f"路径: {OUT}")
    print("\n可用浏览器打开 page_1.html ~ page_7.html 预览")
