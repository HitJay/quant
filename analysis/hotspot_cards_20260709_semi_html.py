"""半导体全线爆发 · 深度回测 (7 页, P2 股票 + P3 ETF/概念拆开)

今日半导体 +6.53%, 主力净入 318.7亿, 13只涨停
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260709"
DAY_HUM = "2026-07-09"
TOPIC = "semi_rally"
VERSION = "v4"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

MAIN_PCT = 6.53
MAIN_NAME = "半导体板块"
NUM1 = ("318.7亿", "主力净入", "--red")
NUM2 = ("+6.53%", "行业涨幅NO.1", "--cyan")
NUM3 = ("13只", "涨停封板", "--gold")

BUCKETS = [
    ("[5%, 6%)", 73, 51, 65, +5.5, +4.1, +1.5, -1.8, False),
    ("[6%, 7%)", 41, 54, 55, +4.5, +2.6, +1.6, -4.2, True),
    ("[7%+)",   33, 67, 67, +1.9, +4.4, +3.8, +0.2, False),
]
CROSS_PCT = 55; CROSS_TRAP = 42; CROSS_60D = -3.0
FAIL_N = 55; FAIL_LOSS = 30; FAIL_DRAWDOWN = 26

SAMPLES = [
    ("2024-09-27", "2024-09-30", "+7.3% % +15.5%", "+15.9%"),
    ("2024-09-30", "2024-10-08", "+15.5% % +16.6%", "+4.4%"),
    ("2025-08-22", "2025-08-28", "+7.7% % +6.7%", "+8.9%"),
    ("2026-05-06", "2026-05-11", "+5.3% % +6.1%", "-1.8%"),
]

POS_3Y = 98.8; HIGH_3Y = 14332; LOW_3Y = 2702
DIST_HIGH = -11.0; DIST_LOW = 372.0

STOCKS = [
    ("华天科技", 23.73, 10.01, 182.5, "涨停"), ("长电科技", 103.52, 10.00, 168.2, "涨停"),
    ("深科技", 56.24, 9.99, 145.8, "涨停"), ("兆易创新", 663.49, 10.00, 128.3, "涨停"),
    ("太极实业", 26.27, 10.01, 95.6, "涨停"), ("通富微电", 72.17, 10.00, 98.7, "涨停"),
    ("有研新材", 59.38, 10.00, 112.4, "涨停"), ("京东方A", 8.15, 6.82, 95.2, "强势"),
    ("紫光股份", 35.68, 6.13, 78.4, "强势"), ("圣邦股份", 312.80, 6.85, 45.3, "强势"),
    ("寒武纪", 1535.01, 5.80, 54.8, "强势"), ("中芯国际", 72.50, 5.12, 88.6, "跟涨"),
]

ETF_LIST = [
    ("512480", "半导体ETF", 1.235, 6.45, 185.6), ("512760", "芯片ETF", 1.412, 6.72, 168.7),
    ("159995", "芯片ETF", 1.385, 6.51, 135.2), ("516640", "半导体材料设备ETF", 1.087, 6.22, 89.5),
]

CONCEPTS = [
    ("蓝宝石", "3.42%", "华工科技"), ("智能穿戴", "3.24%", "同兴达"),
    ("苹果概念", "2.90%", "长电科技"), ("LED概念", "2.71%", "木林森"),
    ("基金重仓", "2.87%", "兆易创新"),
]

BASE_CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2129;--border:#30363d;--text:#e6edf3;--text2:#c9d1d9;--muted:#8b949e;--dim:#6e7681;--blue:#58a6ff;--green:#3fb950;--red:#f85149;--rose:#ff7b72;--orange:#d2991d;--gold:#f0c040;--gold2:#ffd77a;--cyan:#56d4dd;--purple:#bc8cff}
body{width:1080px;height:1440px;background:var(--bg);font-family:'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;color:var(--text);overflow:hidden;position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:28px 42px 16px;font-size:27px}
body::before{content:'';position:absolute;top:-300px;right:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(248,81,73,.06) 0%,transparent 60%);pointer-events:none;z-index:0}
body::after{content:'';position:absolute;bottom:-400px;left:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(88,166,255,.04) 0%,transparent 60%);pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
.pill{display:inline-block;padding:6px 22px;border-radius:22px;font-size:20px;font-weight:700;color:var(--bg);text-align:center;letter-spacing:.4px}
.top-pill{display:flex;justify-content:center}
.subtitle{text-align:center;font-size:28px;font-weight:700;color:var(--text);margin-top:14px}
.subtitle-sm{text-align:center;font-size:18px;color:var(--muted);margin-top:4px;font-style:italic}
.footer{margin-top:10px;padding-top:8px;display:flex;justify-content:space-between;font-size:18px;color:var(--dim);border-top:1px solid var(--border)}
.big-num{font-weight:900;line-height:1;letter-spacing:-1px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px}
.c-label{font-size:18px;color:var(--muted);font-weight:500}
.c-val{font-size:28px;font-weight:900}
"""
FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'

def base_html(body: str, extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">{FONT_LINK}<style>{BASE_CSS}{extra}</style></head>
<body>{body}</body></html>"""


# ── P1 封面 ──
def page_1_html() -> str:
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} % 板块暴动</div></div>
<div class="subtitle" style="font-size:30px">半导体全线爆发 % 今日主角</div>
<div style="text-align:center;margin-top:24px">
  <div class="big-num" style="font-size:180px;background:linear-gradient(180deg,#ff7b72 0%,#f85149 60%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:12px 0;filter:drop-shadow(0 4px 12px rgba(248,81,73,.3))">+{MAIN_PCT:.2f}%</div>
  <div style="font-size:22px;color:var(--muted);margin-top:6px;letter-spacing:1px">半导体 % 申万二级 % 近 3 年第 1.2% 分位</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:28px">
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:42px;color:var({NUM1[2]})">{NUM1[0]}</div><div style="font-size:18px;color:var(--muted);margin-top:6px">{NUM1[1]}</div></div>
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:42px;color:var({NUM2[2]})">{NUM2[0]}</div><div style="font-size:18px;color:var(--muted);margin-top:6px">{NUM2[1]}</div></div>
  <div class="card" style="text-align:center;padding:16px 10px"><div class="big-num" style="font-size:42px;color:var({NUM3[2]})">{NUM3[0]}</div><div style="font-size:18px;color:var(--muted);margin-top:6px">{NUM3[1]}</div></div>
</div>
<div style="padding:20px 24px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--orange);border-radius:12px;box-shadow:0 0 20px rgba(210,153,29,.15);text-align:center">
  <div style="font-size:21px;color:var(--text2);margin-bottom:8px">但历史数据显示</div>
  <div class="big-num" style="font-size:56px;background:linear-gradient(90deg,var(--orange) 0%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent">[6%,7%) 档 20d 胜率 {CROSS_PCT}%</div>
  <div style="font-size:21px;color:var(--muted);margin-top:8px">[5%,6%) 档反而是 <b style="color:var(--red)">65%</b> ! 多涨半根阳线反而胜率更低?</div>
</div>
<div style="text-align:center;margin-top:10px">
  <div style="display:inline-block;padding:12px 24px;background:var(--card);border:1.5px solid var(--cyan);border-radius:12px;font-size:22px;font-weight:700;color:var(--cyan);box-shadow:0 4px 14px rgba(86,212,221,.15)">半导体的反直觉规律</div>
  <div style="font-size:19px;color:var(--muted);font-style:italic;margin-top:12px">翻到下一页</div>
</div>
<div class="footer"><span>* 申万二级 801081 / 6407 天</span><span>1/7</span></div>"""
    return base_html(body)


# ── P2 12 只龙头股表 ──
def page_2_html() -> str:
    max_pct = max(s[2] for s in STOCKS)
    def stock_col(stocks):
        rows = []
        for name, price, pct_chg, vol, tag in stocks:
            bar_w = (pct_chg / max_pct) * 0.22
            pct_str = f"+{pct_chg:.2f}%"
            bc = "--red" if tag == "涨停" else "--orange"
            tag_bg = "var(--red)" if tag == "涨停" else "var(--orange)" if tag == "强势" else "var(--muted)"
            rows.append(f"""<div style="display:grid;grid-template-columns:80px 55px 1fr 65px 55px;align-items:center;gap:4px;padding:7px 8px;border-bottom:1px solid var(--border)">
<div style="font-size:18px;color:var(--text2);font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{name}</div>
<div style="font-size:17px;color:var(--muted);text-align:right">{price:.2f}</div>
<div style="height:18px"><div style="width:{bar_w};height:16px;background:linear-gradient(90deg,var({bc}) 0%,rgba(248,81,73,.2) 100%);border-radius:2px;min-width:3px"></div></div>
<div style="font-size:20px;font-weight:900;color:var({bc});text-align:right">{pct_str}</div>
<div style="padding:2px 10px;border-radius:8px;font-size:15px;font-weight:600;text-align:center;background:{tag_bg};color:var(--bg)">{tag}</div></div>""")
        return "".join(rows)
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--blue)">今日龙头</div></div>
<div class="subtitle">12 只半导体龙头放量涨停</div>
<div class="subtitle-sm">涨幅排序 % 涨停 7 只 % 主力净入 318.7 亿</div>
<div style="flex:1">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px">
<div><div style="display:grid;grid-template-columns:80px 55px 1fr 65px 55px;align-items:center;gap:4px;padding:5px 8px;font-size:16px;font-weight:700;color:var(--muted);border-bottom:2px solid var(--border);background:var(--card2);border-radius:6px 6px 0 0"><div>名称</div><div style="text-align:right">价格</div><div style="text-align:center">涨</div><div style="text-align:right">涨幅</div><div style="text-align:center">标签</div></div>{stock_col(STOCKS[:6])}</div>
<div><div style="display:grid;grid-template-columns:80px 55px 1fr 65px 55px;align-items:center;gap:4px;padding:5px 8px;font-size:16px;font-weight:700;color:var(--muted);border-bottom:2px solid var(--border);background:var(--card2);border-radius:6px 6px 0 0"><div>名称</div><div style="text-align:right">价格</div><div style="text-align:center">涨</div><div style="text-align:right">涨幅</div><div style="text-align:center">标签</div></div>{stock_col(STOCKS[6:])}</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:14px;padding:12px 16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="text-align:center"><div class="c-label" style="font-size:16px;color:var(--muted)">涨停家数</div><div class="c-val" style="font-size:36px;color:var(--red)">13</div></div>
<div style="text-align:center"><div class="c-label" style="font-size:16px;color:var(--muted)">主力净入</div><div class="c-val" style="font-size:36px;color:var(--red)">318.7亿</div></div>
<div style="text-align:center"><div class="c-label" style="font-size:16px;color:var(--muted)">东财人气</div><div class="c-val" style="font-size:36px;color:var(--gold)">7/10</div></div>
</div>
<div style="margin-top:8px;font-size:17px;color:var(--muted);text-align:center;padding:6px;background:var(--card2);border-radius:8px">
  其余涨停: 领先股份 · 旭光电子 · 同兴达 · 木林森 · 上海贝岭 · 宝鼎科技 · 中芯国际
</div>
</div>
<div class="footer"><span>* 东财人气榜 + 涨停池</span><span>2/7</span></div>"""
    return base_html(body)


# ── P3 ETF + 概念 + 统计 ──
def page_3_html() -> str:
    e_rows = []
    for code, name, price, pct, vol in ETF_LIST:
        e_rows.append(f"""<div class="card" style="text-align:center;padding:18px 12px">
<div style="font-size:16px;color:var(--muted)">{code}</div>
<div style="font-size:22px;font-weight:700;color:var(--text);margin:4px 0">{name}</div>
<div class="big-num" style="font-size:30px;color:var(--red)">+{pct:.2f}%</div>
<div style="font-size:17px;color:var(--muted);margin-top:2px">{price:.3f}元</div>
</div>""")

    c_rows = "".join(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:7px 16px;border-bottom:1px solid var(--border)">
<div style="font-size:18px;color:var(--text2);font-weight:500">{c[0]}</div>
<div style="font-size:20px;font-weight:900;color:var(--red)">+{c[1]}</div>
<div style="font-size:16px;color:var(--muted)">{c[2]}领涨</div>
</div>""" for c in CONCEPTS)

    body = f"""<div class="top-pill"><div class="pill" style="background:var(--purple)">相关概念 & ETF</div></div>
<div class="subtitle">半导体带火哪些方向?</div>
<div style="flex:1">

<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:28px">
  {"".join(e_rows[:2])}
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px">
  {"".join(e_rows[2:])}
</div>

<div style="margin-top:28px">
  <div style="font-size:20px;color:var(--muted);font-weight:600;margin-bottom:6px;padding-left:2px">概念涨幅 TOP5</div>
  <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden">{c_rows}</div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px">
<div style="text-align:center;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="font-size:17px;color:var(--muted);margin-bottom:6px">半导体涨停占全天</div>
<div class="big-num" style="font-size:42px;color:var(--red)">17%</div>
<div style="font-size:16px;color:var(--muted);margin-top:4px">75 只涨停中 13 只</div>
</div>
<div style="text-align:center;padding:16px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="font-size:17px;color:var(--muted);margin-bottom:6px">电子板块总主力净入</div>
<div class="big-num" style="font-size:42px;color:var(--gold)">438.8亿</div>
<div style="font-size:16px;color:var(--muted);margin-top:4px">全行业第一</div>
</div>
</div>

<div class="footer"><span>* 数据: push2 板块 + 概念</span><span>3/7</span></div>"""
    return base_html(body)


# ── P4 胜率表 ──
def page_4_html() -> str:
    bc = []
    for label, n, w5, w20, m20, med20, m60, med60, ic in BUCKETS:
        cls = "bcard bhl" if ic else "bcard"
        w5c = "--red" if w5 >= 65 else "--orange"
        w20c = "--red" if w20 >= 65 else "--orange"
        hl = f'<div style="font-size:21px;font-weight:900;color:var(--orange);margin-top:6px"><- 今日在此档</div>' if ic else ""
        bc.append(f"""<div class="{cls}"><div style="display:grid;grid-template-columns:170px 1fr 1fr 1fr;align-items:center;gap:16px">
<div><div style="font-size:30px;font-weight:900;color:var(--red)">{label}</div><div style="font-size:20px;color:var(--muted);margin-top:4px">n={n}</div>{hl}</div>
<div style="text-align:center"><div style="font-size:19px;color:var(--muted);margin-bottom:4px">5d 胜率</div><div style="font-size:38px;font-weight:900;color:var({w5c})">{w5}%</div></div>
<div style="text-align:center"><div style="font-size:19px;color:var(--muted);margin-bottom:4px">20d 胜率</div><div style="font-size:38px;font-weight:900;color:var({w20c})">{w20}%</div><div style="font-size:17px;color:var(--muted);margin-top:2px">均 {m20:+.1f}%</div></div>
<div style="text-align:center"><div style="font-size:19px;color:var(--muted);margin-bottom:4px">60d 均值</div><div style="font-size:38px;font-weight:900;color:var(--red if m60>0 else --green)">{m60:+.1f}%</div><div style="font-size:17px;color:var(--muted);margin-top:2px">中位 {med60:+.1f}%</div></div>
</div></div>""")

    extra = ".bcard{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px}.bhl{background:linear-gradient(135deg,var(--card) 0%,rgba(210,153,29,.05) 100%);border:2px solid var(--orange);box-shadow:0 0 20px rgba(210,153,29,.2)}"
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--gold)">历史胜率</div></div>
<div class="subtitle">单日大涨后, N 天怎么走?</div>
<div class="subtitle-sm">SW 801081 / 6407 交易日 / 单日 >= 5% 分三档</div>
<div style="display:flex;flex-direction:column;gap:10px">{"".join(bc)}</div>
<div style="padding:12px 18px;background:var(--card2);border:1px solid var(--border);border-radius:10px;text-align:center">
<div style="font-size:20px;font-weight:900;color:var(--cyan);margin-bottom:4px">关键发现</div>
<div style="font-size:19px;color:var(--text2);line-height:1.4">[5%,6%) 档 20d 胜率 <b style="color:var(--red)">65%</b> % 今日 [6%,7%) 仅 <b style="color:var(--orange)">55%</b><br>7%+ 暴涨反而 67% — [6%,7%) 是最尴尬中档</div>
</div>
<div style="padding:14px 22px;background:linear-gradient(135deg,var(--card) 0%,rgba(210,153,29,.08) 100%);border:2px solid var(--orange);border-radius:12px;text-align:center;box-shadow:0 0 20px rgba(210,153,29,.15)">
<div style="font-size:23px;font-weight:900;color:var(--orange)">反直觉规律</div>
<div style="font-size:20px;color:var(--muted);margin-top:6px">最强是 [5%,6%) 和 [7%+), 中间档反而弱 — 看结构不看涨幅 (翻到下一页)</div>
</div>
<div class="footer"><span>* 回测: 1999-12 至今</span><span>4/7</span></div>"""
    return base_html(body, extra)


# ── P5 反共识陷阱 ──
def page_5_html() -> str:
    sr = []
    for d1, d2, combo, r20 in SAMPLES:
        v = float(r20.strip("%").strip("+"))
        neg = v < 0
        sr.append(f"""<div class="srow" style="background:{'rgba(63,185,80,.14)' if neg else 'transparent'}">
<div>{d1}</div><div>{d2}</div><div style="text-align:center">{combo}</div>
<div style="text-align:right;font-size:{'23px' if neg else '19px'};font-weight:{'900' if neg else '500'};color:var(--green if neg else --red)">{r20}</div>
</div>""")
    extra = ".srow{display:grid;grid-template-columns:110px 110px 1fr 100px;gap:6px;padding:3px 10px;align-items:center;font-size:19px;color:var(--text2);border-radius:4px;font-variant-numeric:tabular-nums}"
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--orange)">反共识陷阱</div></div>
<div class="subtitle" style="font-size:36px">换挡不如换结构</div>
<div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:14px;margin-top:20px;padding:0 14px">
<div style="text-align:center"><div style="font-size:19px;color:var(--muted);margin-bottom:2px">今日档 [6%,7%)</div><div class="big-num" style="font-size:130px;color:var(--red);filter:drop-shadow(0 4px 10px rgba(248,81,73,.3))">{CROSS_PCT}%</div><div style="font-size:20px;color:var(--muted);margin-top:2px">20d 胜率</div></div>
<div style="text-align:center;padding:0 4px"><div style="font-size:44px;font-weight:900;color:var(--orange);line-height:1">-></div><div style="font-size:18px;color:var(--orange);margin-top:2px;font-weight:700">若 5 日内<br>两次 +5%</div></div>
<div style="text-align:center"><div style="font-size:19px;color:var(--muted);margin-bottom:2px">双次大涨后</div><div class="big-num" style="font-size:130px;color:var(--green);filter:drop-shadow(0 4px 10px rgba(63,185,80,.3))">{CROSS_TRAP}%</div><div style="font-size:20px;color:var(--muted);margin-top:2px">20d 胜率</div></div>
</div>
<div style="text-align:center;padding:8px 14px;background:var(--card2);border:1px solid var(--border);border-radius:10px;margin-top:6px;font-size:19px;font-weight:700">60d 均值: 单次大涨 +1.6% &nbsp;VS&nbsp; 双次大涨后 <span style="color:var(--green)">{CROSS_60D:+.1f}%</span></div>
<div style="margin-top:10px"><div style="text-align:center;font-size:20px;font-weight:700;color:var(--cyan);margin-bottom:1px">追过第二次的姐妹最后怎样了?</div>
<div style="text-align:center;font-size:17px;color:var(--muted);font-style:italic;margin-bottom:2px">最近 4 次</div>
<div style="display:grid;grid-template-columns:110px 110px 1fr 100px;gap:6px;padding:3px 10px;font-size:18px;font-weight:900;color:var(--muted);border-bottom:1px solid var(--border);margin-bottom:2px"><div>首日</div><div>次日</div><div style="text-align:center">两次涨幅</div><div style="text-align:right">20d 后</div></div>
{"".join(sr)}</div>
<div style="padding:14px 22px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:12px;text-align:center;box-shadow:0 6px 20px rgba(210,153,29,.3)">
<div style="font-size:26px;font-weight:900;color:var(--bg)">{FAIL_N} 次双涨中 {FAIL_LOSS} 次亏钱 % {FAIL_DRAWDOWN} 次跌超 -3%</div>
<div style="font-size:20px;color:var(--bg);margin-top:4px;opacity:.85">20d 均 -3.0% % 中位 -2.9%</div>
</div>
<div class="footer"><span>* 反共识: 5 日内两次 >= +5%</span><span>5/7</span></div>"""
    return base_html(body, extra)


# ── P6 位置 + 三档操作 ──
def page_6_html() -> str:
    tiers = "".join(f"""<div style="display:flex;align-items:center;gap:14px;padding:10px 14px;background:var(--card);border:1px solid var(--border);border-radius:10px">
<div style="min-width:66px;padding:6px 12px;background:var(--{c});color:var(--bg);border-radius:18px;font-size:19px;font-weight:900;text-align:center">{t}</div>
<div style="font-size:20px;color:var(--text2);line-height:1.3;flex:1">{b}</div>
</div>""" for t, c, b in [
    ("激进","--red","已入 -> 明天观察能否站稳 +5% 支撑, 跌破减仓"),
    ("稳健","--orange","未入 -> 别追高, 等回踩 MA20 确认再上"),
    ("长线","--cyan","定投半导体 ETF, 分位虽高但长期向上"),
])
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--cyan)">当前位置</div></div>
<div class="subtitle">涨了一天, 半导体在哪儿?</div>
<div style="text-align:center;margin-top:16px">
<div style="font-size:18px;color:var(--muted);margin-bottom:6px">近 3 年分位</div>
<div class="big-num" style="font-size:160px;background:linear-gradient(180deg,#f85149 0%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 10px rgba(248,81,73,.3))">{POS_3Y:.1f}%</div>
<div style="font-size:19px;color:var(--orange);margin-top:8px;font-weight:600">高位区 % 距 3 年高点仅 -{abs(DIST_HIGH):.0f}%</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:18px">
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:18px;color:var(--muted);margin-bottom:4px">距 3 年高点</div><div style="font-size:32px;font-weight:900;color:var(--green)">{DIST_HIGH:+.1f}%</div><div style="font-size:16px;color:var(--muted);margin-top:2px">{HIGH_3Y} -> 现值</div></div>
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:18px;color:var(--muted);margin-bottom:4px">距 3 年低点</div><div style="font-size:32px;font-weight:900;color:var(--red)">+{DIST_LOW:.0f}%</div><div style="font-size:16px;color:var(--muted);margin-top:2px">{LOW_3Y} -> 现值</div></div>
<div class="card" style="text-align:center;padding:12px 8px"><div style="font-size:18px;color:var(--muted);margin-bottom:4px">主力净入</div><div style="font-size:32px;font-weight:900;color:var(--red)">318.7亿</div><div style="font-size:16px;color:var(--muted);margin-top:2px">单日 NO.1</div></div>
</div>
<div><div style="text-align:center;font-size:21px;font-weight:900;color:var(--text);margin-bottom:8px">三档操作建议</div><div style="display:flex;flex-direction:column;gap:6px">{tiers}</div></div>
<div style="padding:12px 18px;background:linear-gradient(90deg,rgba(210,153,29,.12),rgba(210,153,29,.03));border-left:4px solid var(--orange);border-radius:8px"><div style="font-size:18px;font-weight:900;color:var(--orange)">散户提醒</div><div style="font-size:19px;color:var(--text2);margin-top:2px">3 年分位 {POS_3Y}% 已是高位区, [6%,7%) 档 20d 胜率仅 55%. 追涨前先看位置.</div></div>
<div class="footer"><span>* 3 年分位基准</span><span>6/7</span></div>"""
    return base_html(body)


# ── P7 CTA ──
def page_7_html() -> str:
    cards = "".join(f"""<div style="display:flex;align-items:center;gap:18px;padding:20px 22px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,.3) 100%);border:2px solid var(--{c});border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.3)">
<div style="font-size:56px;font-weight:900;color:var(--{c});min-width:72px;text-align:center;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.4))">{n}</div>
<div style="flex:1"><div style="font-size:28px;font-weight:900;color:var(--text)">{t}</div><div style="font-size:20px;color:var(--muted);margin-top:4px">{b}</div></div>
</div>""" for n, t, c, b in [
    ("01","复盘","--red","涨停天梯 / 行业冠亚军 / 炸板预警"),
    ("02","雷达","--purple","雪球新热点 / 资金搬家 / 分档胜率"),
    ("03","反共识","--cyan","数据驱动 / 历史样本核对 / 拒绝小作文"),
])
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--rose)">关注我</div></div>
<div style="text-align:center;font-size:21px;font-style:italic;color:var(--text2);margin-top:14px">明天半导体还能续命吗? 数据每天替你盯</div>
<div style="text-align:center"><div style="font-size:32px;color:var(--text);margin-bottom:8px">每天 3 分钟</div><div class="big-num" style="font-size:64px;background:linear-gradient(90deg,var(--gold) 0%,var(--gold2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 10px rgba(240,192,64,.3))">看懂 A 股</div></div>
<div style="display:flex;flex-direction:column;gap:10px">{cards}</div>
<div style="padding:20px 26px;background:linear-gradient(135deg,var(--gold) 0%,#e8b73a 100%);border-radius:14px;text-align:center;box-shadow:0 8px 28px rgba(240,192,64,.35)"><div style="font-size:28px;font-weight:900;color:var(--bg)">点关注 + 收藏 不迷路</div><div style="font-size:21px;color:var(--bg);margin-top:6px;opacity:.8">明早 9:15 继续给你递盘前情报</div></div>
<div style="text-align:center"><div style="font-size:21px;font-weight:900;color:var(--cyan);margin-bottom:6px">评论区告诉我</div><div style="font-size:22px;color:var(--text2);margin-bottom:4px">半导体今天你追了吗? 明天减仓还是持有?</div><div style="font-size:18px;color:var(--muted)">明天想看哪只票的追踪? 评论区点名</div></div>
<div class="footer"><span>* 复旦杰伦 / 数据驱动 / 不构成投资建议</span><span>7/7</span></div>"""
    return base_html(body)


PAGE_HTML_GENERATORS = [page_1_html, page_2_html, page_3_html, page_4_html, page_5_html, page_6_html, page_7_html]


def render_all():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1080, "height": 1440}, device_scale_factor=2, locale="zh-CN")
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
    cols, rows = 4, 2
    tw, th = 420, 540
    canvas = Image.new("RGB", (cols * tw + (cols-1)*4, rows * th + (rows-1)*4), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, cols)
        canvas.paste(p.resize((tw, th)), (c * (tw + 4), r * (th + 4)))
    canvas.save(OUT / "preview_2x4.png")
    print(f"  saved preview_2x4.png")
    th = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, th), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y)); y += p.height
    stacked.resize((720, int(th * 720 / w))).save(OUT / "all_pages_stacked.png")
    print(f"  saved all_pages_stacked.png")


if __name__ == "__main__":
    print(f"HTML 7 页深度回测 -> {OUT}")
    render_all()
    make_preview()
    print("\n完成. 7 张 2160x2880 PNG")
