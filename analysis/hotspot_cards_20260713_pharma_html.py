"""医药逆势涨停潮 · 深度卡片 (8 页 HTML, 量化加厚版, 复用 semi 模板视觉语言)

题材: 2026-07-13 弱市抱团, 医药(化学制药/化学制品/中药)逆势涨停
数据: output/hotspot/20260713/summary.json + 东财午评 + pharma_winrate.json (项目 winrate 工具)
渲染: playwright chromium -> 2160x2880 PNG (与 hotspot_cards_20260709_semi_html.py 同路线)
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260713"
DAY_HUM = "2026-07-13"
TOPIC = "pharma_rally"
VERSION = "html_v3"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ── 量化数据 (pharma_winrate.json) ──
WR = json.loads((ROOT / f"output/hotspot/{DATE}/pharma_winrate.json").read_text(encoding="utf-8"))
SC = WR["scenarios"]
POS = WR["position"]
SAMPLES = WR.get("samples", [])


def res(sid, hk):
    return SC[sid]["results"].get(hk, {})


ZT_COUNT = 29
MED_ZT = 10
ZT_TOP10 = [
    ("国华退", "软件开发", "+10.87%", "3连板", "退市"),
    ("贵绳股份", "通用设备", "+10.05%", "3连板", "涨停"),
    ("立方制药", "化学制药", "+9.98%", "3连板", "涨停"),
    ("亚联机械", "专用设备", "+9.99%", "3连板", "涨停"),
    ("九丰能源", "燃气Ⅱ", "+10.01%", "2连板", "涨停"),
    ("哈药股份", "化学制药", "+10.09%", "2连板", "涨停"),
    ("华建集团", "工程咨询", "+10.04%", "2连板", "涨停"),
    ("联环药业", "化学制药", "+10.01%", "2连板", "涨停"),
    ("中信重工", "专用设备", "+9.92%", "2连板", "涨停"),
    ("沃顿科技", "塑料", "+10.04%", "2连板", "涨停"),
]
MED_IND = {"化学制药", "化学制品", "中药Ⅱ", "医药商业"}
IND_BOARDS = [
    ("化学制药", 4, "--red"), ("化学制品", 3, "--red"),
    ("中药Ⅱ", 3, "--gold"), ("通用设备", 2, "--muted"), ("IT服务Ⅱ", 2, "--muted"),
]
# 收盘行业涨跌 (东财 push2, 真实收盘) — 数值为百分比
IND_UP = [("中药Ⅱ", "+2.96%"), ("银行Ⅱ", "+2.07%"), ("医药商业", "+0.77%")]
IND_DOWN = [("元件", "-8.48%"), ("国防军工", "-7.59%"), ("光学光电子", "-6.89%")]
RISK_STOCKS = [
    ("国华退", "软件开发", "退市·3连板", "末日轮·极高风险", "--orange"),
    ("星网锐捷", "通信设备", "炸板3次", "追高被埋", "--orange"),
    ("杭氧股份", "化学制品", "炸板", "板块内分歧", "--orange"),
    ("凯美特气", "化学制品", "炸板", "板块内分歧", "--orange"),
    ("国恩股份", "塑料", "炸板", "高位回落", "--orange"),
    ("珠海港", "电力", "炸板", "题材一日游", "--orange"),
]
XQ_TWEET = [("贵州茅台", 122786), ("比亚迪", 110783), ("赛力斯", 78112),
            ("格力电器", 46180), ("东芯股份", 39837)]
# 收盘领跌行业 (替代被墙的东财人气榜, 真实收盘数据)
LEAD_DOWN = [("元件", "-8.48%"), ("国防军工", "-7.59%"), ("光学光电子", "-6.89%")]
# 上车标的 (静态代码, 仅供参考)
ETFS = [("中药ETF", "159647"), ("中药ETF", "562390"), ("医药ETF", "512010"),
        ("医药ETF", "512170"), ("恒瑞医药", "600276")]

BASE_CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0d1117;--card:#161b22;--card2:#1c2129;--border:#30363d;--text:#e6edf3;--text2:#c9d1d9;--muted:#8b949e;--dim:#6e7681;--blue:#58a6ff;--green:#3fb950;--red:#f85149;--rose:#ff7b72;--orange:#d2991d;--gold:#f0c040;--gold2:#ffd77a;--cyan:#56d4dd;--purple:#bc8cff}
body{width:1080px;height:1440px;background:var(--bg);font-family:'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;color:var(--text);overflow:hidden;position:relative;display:flex;flex-direction:column;justify-content:space-between;padding:26px 40px 14px;font-size:36px}
body::before{content:'';position:absolute;top:-300px;right:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(248,81,73,.06) 0%,transparent 60%);pointer-events:none;z-index:0}
body::after{content:'';position:absolute;bottom:-400px;left:-300px;width:900px;height:900px;background:radial-gradient(circle,rgba(88,166,255,.04) 0%,transparent 60%);pointer-events:none;z-index:0}
body>*{position:relative;z-index:1}
.pill{display:inline-block;padding:5px 20px;border-radius:20px;font-size:25px;font-weight:700;color:var(--bg);text-align:center;letter-spacing:.4px}
.top-pill{display:flex;justify-content:center}
.subtitle{text-align:center;font-size:42px;font-weight:700;color:var(--text);margin-top:10px}
.subtitle-sm{text-align:center;font-size:24px;color:var(--muted);margin-top:2px;font-style:italic}
.footer{margin-top:6px;padding-top:6px;display:flex;justify-content:space-between;font-size:23px;color:var(--dim);border-top:1px solid var(--border)}
.big-num{font-weight:900;line-height:1;letter-spacing:-1px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px}
.c-label{font-size:23px;color:var(--muted);font-weight:500}
.c-val{font-size:38px;font-weight:900}
.row{display:grid;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid var(--border);font-size:25px;color:var(--text2)}
.row.head{font-size:22px;font-weight:700;color:var(--muted);background:var(--card2);border-bottom:1.5px solid var(--border)}
.tag{display:inline-block;padding:2px 12px;border-radius:9px;font-size:21px;font-weight:700;color:var(--bg);text-align:center}
.mini{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:10px 6px;background:var(--card);border:1px solid var(--border);border-radius:10px}
.bcard{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:9px 12px}
"""

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'


def base_html(body: str, extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">{FONT_LINK}<style>{BASE_CSS}{extra}</style></head>
<body>{body}</body></html>"""


# ── P1 封面 ──
def page_1_html() -> str:
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} 弱市抱团</div></div>
<div class="subtitle" style="font-size:50px">医药逆势涨停潮</div>
<div style="text-align:center;margin-top:10px">
  <div class="big-num" style="font-size:192px;background:linear-gradient(180deg,#ff7b72 0%,#f85149 60%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:8px 0;filter:drop-shadow(0 4px 12px rgba(248,81,73,.3))">{MED_ZT} 只</div>
  <div style="font-size:28px;color:var(--muted);margin-top:2px">医药系涨停 % 占全天 {ZT_COUNT} 只约 1/3</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:18px">
  <div class="card" style="text-align:center;padding:22px 6px"><div class="big-num" style="font-size:66px;color:var(--green)">-1.54%</div><div style="font-size:26px;color:var(--muted);margin-top:6px">沪指</div></div>
  <div class="card" style="text-align:center;padding:22px 6px"><div class="big-num" style="font-size:66px;color:var(--red)">{ZT_COUNT}只</div><div style="font-size:26px;color:var(--muted);margin-top:6px">涨停</div></div>
  <div class="card" style="text-align:center;padding:22px 6px"><div class="big-num" style="font-size:66px;color:var(--gold)">3连板</div><div style="font-size:26px;color:var(--muted);margin-top:6px">立方制药</div></div>
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:16px">
  <div class="mini"><div style="font-size:17px;color:var(--muted)">深成指</div><div style="font-size:40px;font-weight:900;color:var(--green)">-2.61%</div></div>
  <div class="mini"><div style="font-size:17px;color:var(--muted)">创业板</div><div style="font-size:40px;font-weight:900;color:var(--green)">-2.38%</div></div>
  <div class="mini"><div style="font-size:17px;color:var(--muted)">下跌</div><div style="font-size:40px;font-weight:900;color:var(--green)">4573</div></div>
  <div class="mini"><div style="font-size:17px;color:var(--muted)">上涨</div><div style="font-size:40px;font-weight:900;color:var(--red)">892</div></div>
</div>
<div style="padding:14px 22px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--orange);border-radius:12px;box-shadow:0 0 20px rgba(210,153,29,.15);text-align:center;margin-top:12px">
  <div style="font-size:25px;color:var(--text2)">普跌日, <b style="color:var(--red)">中药 / 化学制药 / 医药商业</b> 逆势走强</div>
  <div style="font-size:23px;color:var(--muted);margin-top:4px">关键词: 医药抱团 · 科技退潮 · 避险升温</div>
</div>
<div class="footer"><span>* 东方财富涨停池 + 午评</span><span>1/8</span></div>"""
    return base_html(body)


# ── P2 涨停天梯全貌 ──
def page_2_html() -> str:
    MAXREF = 22.0
    rows = []
    for name, ind, pct, board, tag in ZT_TOP10:
        is_med = ind in MED_IND
        bc = "var(--red)" if is_med else ("var(--gold)" if tag == "退市" else "var(--muted)")
        hl = "background:rgba(248,81,73,.08);" if is_med else ""
        name_c = "var(--red)" if is_med else "var(--text)"
        val = float(pct.replace("%", "").replace("+", ""))
        wpct = f"{min(val / MAXREF * 100, 98):.0f}%"
        rows.append(f"""<div class="row" style="grid-template-columns:130px 104px 1fr 76px 80px;{hl}">
<div style="font-size:27px;font-weight:700;color:{name_c}">{name}</div>
<div style="font-size:23px;color:var(--muted)">{ind}</div>
<div style="display:flex;align-items:center;gap:8px"><div style="width:{wpct};height:18px;background:linear-gradient(90deg,{bc} 0%,rgba(248,81,73,.25) 100%);border-radius:3px;min-width:6px"></div><div style="font-size:25px;font-weight:900;color:{bc}">{pct}</div></div>
<div style="font-size:23px;color:var(--text2);text-align:center">{board}</div>
<div style="text-align:center"><span class="tag" style="background:{bc}">{tag}</span></div></div>""")
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--blue)">涨停天梯</div></div>
<div class="subtitle">全天涨停全貌</div>
<div class="subtitle-sm">红字 = 医药系 (化学制药 / 化学制品 / 中药)</div>
<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:10px">
<div class="row head" style="grid-template-columns:130px 104px 1fr 76px 80px"><div>名称</div><div>行业</div><div>涨幅</div><div style="text-align:center">连板</div><div style="text-align:center">标签</div></div>
{"".join(rows)}</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:12px">
  <div class="card" style="text-align:center;padding:14px 8px"><div class="c-label" style="font-size:22px;color:var(--muted)">化学制药</div><div class="c-val" style="font-size:52px;color:var(--red)">4只</div></div>
  <div class="card" style="text-align:center;padding:14px 8px"><div class="c-label" style="font-size:22px;color:var(--muted)">化学制品</div><div class="c-val" style="font-size:52px;color:var(--red)">3只</div></div>
  <div class="card" style="text-align:center;padding:14px 8px"><div class="c-label" style="font-size:22px;color:var(--muted)">中药</div><div class="c-val" style="font-size:52px;color:var(--gold)">3只</div></div>
</div>
<div style="padding:12px 20px;background:linear-gradient(135deg,var(--card) 0%,rgba(248,81,73,.06) 100%);border:1.5px solid var(--red);border-radius:12px;text-align:center;margin-top:10px">
  <div style="font-size:24px;color:var(--text2)">3 连板天梯里医药独占 3 席 (立方制药 / 哈药股份 / 联环药业) · 弱市最整齐梯队</div>
</div>
<div class="footer"><span>* 东财涨停池 TOP10</span><span>2/8</span></div>"""
    return base_html(body)


# ── P3 行业分布 + 避险逻辑 ──
def page_3_html() -> str:
    maxc = max(c for _, c, _ in IND_BOARDS)
    bar_rows = []
    for name, cnt, color in IND_BOARDS:
        w = (cnt / maxc) * 0.42
        bar_rows.append(f"""<div style="display:flex;align-items:center;gap:12px;padding:7px 0">
<div style="width:120px;font-size:25px;color:var(--text2);font-weight:600;text-align:right">{name}</div>
<div style="flex:1;height:24px;background:var(--card2);border-radius:6px;overflow:hidden"><div style="width:{w};height:100%;background:linear-gradient(90deg,var({color}) 0%,rgba(248,81,73,.2) 100%);border-radius:6px;min-width:10px"></div></div>
<div style="width:74px;font-size:28px;font-weight:900;color:var({color})">{cnt}只</div></div>""")
    reasons = [
        ("防御属性", "跌时抗跌, 弱市资金天然偏好"),
        ("低位补涨", "医药调整充分, 估值处历史低位"),
        ("中报预期", "业绩确定性 + 创新药催化临近"),
    ]
    rc = "".join(f"""<div style="flex:1;padding:12px;background:var(--card);border:1px solid var(--border);border-radius:10px">
<div style="font-size:25px;font-weight:900;color:var(--cyan);margin-bottom:4px">{t}</div>
<div style="font-size:22px;color:var(--text2);line-height:1.35">{b}</div></div>""" for t, b in reasons)
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--purple)">行业 & 避险</div></div>
<div class="subtitle">为什么是医药?</div>
<div class="subtitle-sm">涨停行业分布 · 医药占前三</div>
<div style="background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 18px;margin-top:10px">{"".join(bar_rows)}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px">
  <div style="padding:14px;background:rgba(63,185,80,.12);border:1.5px solid var(--green);border-radius:12px">
    <div style="font-size:25px;font-weight:900;color:var(--green);margin-bottom:6px">收盘居前(逆势)</div>
    <div style="font-size:24px;color:var(--text2);line-height:1.6">中药 <b style="color:var(--green)">{IND_UP[0][1]}</b><br>银行 <b style="color:var(--green)">{IND_UP[1][1]}</b><br>医药商业 <b style="color:var(--green)">{IND_UP[2][1]}</b></div></div>
  <div style="padding:14px;background:rgba(248,81,73,.12);border:1.5px solid var(--red);border-radius:12px">
    <div style="font-size:25px;font-weight:900;color:var(--red);margin-bottom:6px">收盘领跌</div>
    <div style="font-size:24px;color:var(--text2);line-height:1.6">元件 <b style="color:var(--red)">{IND_DOWN[0][1]}</b><br>国防军工 <b style="color:var(--red)">{IND_DOWN[1][1]}</b><br>光学光电子 <b style="color:var(--red)">{IND_DOWN[2][1]}</b></div></div>
</div>
<div style="display:flex;gap:10px;margin-top:12px">{rc}</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px">
  <div class="mini"><div style="font-size:14px;color:var(--muted)">医药占涨停</div><div style="font-size:34px;font-weight:900;color:var(--red)">34%</div><div style="font-size:18px;color:var(--muted)">10 / 29 只</div></div>
  <div class="mini"><div style="font-size:14px;color:var(--muted)">全市场下跌</div><div style="font-size:34px;font-weight:900;color:var(--green)">4573</div><div style="font-size:18px;color:var(--muted)">仅 892 涨</div></div>
  <div class="mini"><div style="font-size:14px;color:var(--muted)">涨停 : 跌停</div><div style="font-size:34px;font-weight:900;color:var(--orange)">29 : 45</div><div style="font-size:18px;color:var(--muted)">风险偏好降</div></div>
</div>
<div style="padding:10px 18px;background:linear-gradient(135deg,var(--card) 0%,rgba(88,166,255,.05) 100%);border:1.5px solid var(--blue);border-radius:10px;text-align:center;margin-top:10px">
  <div style="font-size:22px;color:var(--text2)">风险偏好骤降, 资金从高位科技切向 <b style="color:var(--red)">低位医药 + 红利</b> 避险</div>
</div>
<div class="footer"><span>* 午评行业强弱 + 涨停池</span><span>3/8</span></div>"""
    return base_html(body)


# ── P4 量化·分档胜率 ──
def page_4_html() -> str:
    b1 = res("zy_bucket_1_2", "hold20d"); b2 = res("zy_bucket_2_3", "hold20d"); b3 = res("zy_bucket_3p", "hold20d")
    b1_60 = res("zy_bucket_1_2", "hold60d"); b2_60 = res("zy_bucket_2_3", "hold60d"); b3_60 = res("zy_bucket_3p", "hold60d")
    yiyao = res("yiyao_surge_self", "hold20d"); hs300 = res("zhongyao_surge_hs300", "hold20d")
    rows = [
        ("中药涨 [1%,2%)", b1, b1_60, "--muted"),
        ("中药涨 [2%,3%)", b2, b2_60, "--orange"),
        ("中药涨 [3%+)", b3, b3_60, "--red"),
    ]
    tr = []
    for label, r20, r60, color in rows:
        tr.append(f"""<div class="bcard" style="display:grid;grid-template-columns:200px 1fr 1fr 1fr;gap:10px;align-items:center;margin-bottom:8px">
<div style="font-size:25px;font-weight:700;color:var({color})">{label}</div>
<div style="text-align:center"><div style="font-size:20px;color:var(--muted)">20d胜率</div><div style="font-size:40px;font-weight:900;color:var({color})">{r20['win_pct']}%</div></div>
<div style="text-align:center"><div style="font-size:20px;color:var(--muted)">60d胜率</div><div style="font-size:40px;font-weight:900;color:var({color})">{r60['win_pct']}%</div></div>
<div style="text-align:center"><div style="font-size:20px;color:var(--muted)">60d均值</div><div style="font-size:34px;font-weight:900;color:var(--green)">{r60['mean_pct']:+.1f}%</div></div></div>""")
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--gold)">量化 · 胜率</div></div>
<div class="subtitle">中药单日大涨后, 怎么走?</div>
<div class="subtitle-sm">申万中药 · {SC['zhongyao_surge_self']['trigger_count']} 次样本 · 持有 N 日胜率</div>
<div style="margin-top:12px">{"".join(tr)}</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px">
  <div class="card" style="text-align:center;padding:12px 6px"><div class="c-label" style="font-size:21px">中药&gt;2%→中药 20d</div><div class="c-val" style="font-size:44px;color:var(--red)">{res('zhongyao_surge_self','hold20d')['win_pct']}%</div></div>
  <div class="card" style="text-align:center;padding:12px 6px"><div class="c-label" style="font-size:21px">医药生物 20d</div><div class="c-val" style="font-size:44px;color:var(--red)">{yiyao['win_pct']}%</div></div>
  <div class="card" style="text-align:center;padding:12px 6px"><div class="c-label" style="font-size:21px">中药→沪深300 20d</div><div class="c-val" style="font-size:44px;color:var(--orange)">{hs300['win_pct']}%</div></div>
</div>
<div style="padding:12px 20px;background:linear-gradient(135deg,var(--card) 0%,rgba(210,153,29,.06) 100%);border:2px solid var(--orange);border-radius:12px;text-align:center;margin-top:10px">
  <div style="font-size:23px;font-weight:900;color:var(--orange)">关键发现</div>
  <div style="font-size:22px;color:var(--text2);margin-top:3px">涨越猛([3%+]) 短线胜率越高(63%) 但 60 日回落至 54% — 强者恒强是短线逻辑</div>
  <div style="font-size:22px;color:var(--text2)">医药生物(低位) 20d 胜率 59.5% &gt; 中药(高位) 57.9%, 位置越低越抗跌</div>
</div>
<div class="footer"><span>* 回测: 申万中药/医药生物 日线</span><span>4/8</span></div>"""
    return base_html(body)


# ── P5 量化·历史样本 + 位置分位 ──
def page_5_html() -> str:
    sr = []
    for s in SAMPLES:
        neg = s["ret20"] < 0
        col = "var(--green)" if neg else "var(--red)"
        sr.append(f"""<div class="row" style="grid-template-columns:150px 1fr 1fr;background:{'rgba(63,185,80,.12)' if neg else 'transparent'}">
<div style="font-size:25px;color:var(--text2);font-weight:600">{s['date']}</div>
<div style="text-align:center;font-size:27px;font-weight:900;color:var(--red)">+{s['day_ret']}%</div>
<div style="text-align:center;font-size:27px;font-weight:900;color:{col}">{s['ret20']:+.2f}%</div></div>""")
    zy = POS["sw801151"]; yy = POS["sw801150"]
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--cyan)">量化 · 样本 & 位置</div></div>
<div class="subtitle">最近 5 次中药大涨后</div>
<div class="subtitle-sm">当日涨幅 → 其后 20 个交易日真实表现</div>
<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:10px">
<div class="row head" style="grid-template-columns:150px 1fr 1fr"><div>日期</div><div style="text-align:center">当日</div><div style="text-align:center">20日后</div></div>
{"".join(sr)}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px">
  <div style="text-align:center;padding:14px;background:var(--card);border:1.5px solid var(--red);border-radius:12px">
    <div style="font-size:23px;color:var(--muted)">申万中药 3年分位</div>
    <div class="big-num" style="font-size:64px;color:var(--red)">{zy['pct_3y']}%</div>
    <div style="font-size:22px;color:var(--muted);margin-top:2px">距高点 {zy['dist_high']:+.1f}%</div></div>
  <div style="text-align:center;padding:14px;background:var(--card);border:1.5px solid var(--green);border-radius:12px">
    <div style="font-size:23px;color:var(--muted)">医药生物 3年分位</div>
    <div class="big-num" style="font-size:64px;color:var(--green)">{yy['pct_3y']}%</div>
    <div style="font-size:22px;color:var(--muted);margin-top:2px">距高点 {yy['dist_high']:+.1f}%</div></div>
</div>
<div style="padding:12px 20px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:12px;text-align:center;margin-top:10px;box-shadow:0 6px 20px rgba(210,153,29,.3)">
  <div style="font-size:24px;font-weight:900;color:var(--bg)">反共识: 弱市抱团不一定延续</div>
  <div style="font-size:22px;color:var(--bg);margin-top:3px;opacity:.9">创业板跌+中药涨 → 沪深300 20d 胜率仅 40% (中位 -1.27%) · 近期样本多回调</div>
</div>
<div class="footer"><span>* 申万指数 / 近 5 次触发</span><span>5/8</span></div>"""
    return base_html(body)


# ── P6 风险警示 ──
def page_6_html() -> str:
    rows = []
    for name, ind, signal, note, color in RISK_STOCKS:
        rows.append(f"""<div class="row" style="grid-template-columns:140px 120px 1fr 1fr">
<div style="font-size:27px;font-weight:700;color:var(--text)">{name}</div>
<div style="font-size:23px;color:var(--muted)">{ind}</div>
<div style="font-size:26px;font-weight:900;color:var({color});text-align:right">{signal}</div>
<div style="font-size:22px;color:var(--muted);text-align:right">{note}</div></div>""")
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--orange)">风险提示</div></div>
<div class="subtitle">追高之前看一眼</div>
<div style="text-align:center;margin-top:8px">
  <div style="font-size:24px;color:var(--muted)">炸板率 (14 炸板 / {ZT_COUNT} 涨停)</div>
  <div class="big-num" style="font-size:135px;background:linear-gradient(180deg,#ffd77a 0%,#d2991d 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 10px rgba(210,153,29,.3))">48%</div>
</div>
<div style="background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:4px">
<div class="row head" style="grid-template-columns:140px 120px 1fr 1fr"><div>名称</div><div>行业</div><div style="text-align:right">信号</div><div style="text-align:right">提示</div></div>
{"".join(rows)}</div>
<div style="padding:12px 20px;background:linear-gradient(135deg,var(--orange) 0%,#c48819 100%);border-radius:12px;text-align:center;margin-top:10px;box-shadow:0 6px 20px rgba(210,153,29,.3)">
  <div style="font-size:26px;font-weight:900;color:var(--bg)">国华退 = 退市股末日轮, 3连板纯博弈</div>
  <div style="font-size:22px;color:var(--bg);margin-top:3px;opacity:.9">连板越高越危险 · 炸板=追高被套 · 仓位第一</div>
</div>
<div class="footer"><span>* 东财炸板池 + 涨停池</span><span>6/8</span></div>"""
    return base_html(body)


# ── P7 情绪照妖镜 ──
def page_7_html() -> str:
    xq = "".join(f"""<div style="display:flex;justify-content:space-between;padding:8px 14px;border-bottom:1px solid var(--border);font-size:25px;color:var(--text2)">
<div>{n}</div><div style="font-weight:900;color:var({'gold' if n=='赛力斯' else 'muted'})">{v:,}</div></div>""" for n, v in XQ_TWEET)
    down = "".join(f"""<div style="display:flex;justify-content:space-between;padding:8px 14px;border-bottom:1px solid var(--border);font-size:25px;color:var(--text2)">
<div>{n}</div><div style="font-weight:900;color:var(--red)">{p}</div></div>""" for n, p in LEAD_DOWN)
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--purple)">情绪照妖镜</div></div>
<div class="subtitle">真主线 vs 假热度</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px">
  <div style="padding:14px;background:rgba(248,81,73,.12);border:2px solid var(--red);border-radius:12px">
    <div style="font-size:25px;font-weight:900;color:var(--red);margin-bottom:6px">真主线 · 医药</div>
    <div style="font-size:23px;color:var(--text2);line-height:1.5">逆势涨停, 没人聊却天天涨<br>资金用脚投票, 弱市抱团</div></div>
  <div style="padding:14px;background:rgba(63,185,80,.12);border:2px solid var(--green);border-radius:12px">
    <div style="font-size:25px;font-weight:900;color:var(--green);margin-bottom:6px">假热度 · 科技</div>
    <div style="font-size:23px;color:var(--text2);line-height:1.5">讨论榜霸屏半导体/算力<br>收盘却集体暴跌</div></div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px">
  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden"><div style="padding:8px 14px;font-size:23px;font-weight:700;color:var(--purple);background:var(--card2)">雪球讨论榜 TOP5</div>{xq}</div>
  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden"><div style="padding:8px 14px;font-size:23px;font-weight:700;color:var(--red);background:var(--card2)">收盘领跌行业</div>{down}</div>
</div>
<div style="padding:12px 20px;background:linear-gradient(135deg,var(--card) 0%,rgba(188,140,255,.08) 100%);border:2px solid var(--purple);border-radius:12px;text-align:center;margin-top:10px">
  <div style="font-size:24px;font-weight:900;color:var(--purple)">人气高 ≠ 会涨 · 赛力斯突冲讨论#3 成新热点</div>
  <div style="font-size:22px;color:var(--text2);margin-top:3px">逆势涨停的才是真主线 · 元件 -8.48% / 国防军工 -7.59% 收盘领跌</div>
</div>
<div class="footer"><span>* 雪球讨论榜 + 东财行业收盘</span><span>7/8</span></div>"""
    return base_html(body)


# ── P8 操作三档 + 标的 + CTA ──
def page_8_html() -> str:
    tiers = "".join(f"""<div style="display:flex;align-items:center;gap:14px;padding:11px 16px;background:var(--card);border:1px solid var(--border);border-radius:12px;margin-bottom:8px">
<div style="min-width:74px;padding:6px 11px;background:var(--{c});color:var(--bg);border-radius:16px;font-size:25px;font-weight:900;text-align:center">{t}</div>
<div style="font-size:24px;color:var(--text2);line-height:1.3;flex:1">{b}</div></div>""" for t, c, b in [
    ("激进", "--red", "已持有 → 盯立方制药/哈药封单, 断板即减仓, 不恋战"),
    ("稳健", "--orange", "未持有 → 别追高, 等回踩 MA20 确认再上车"),
    ("长线", "--cyan", "定投医药/中药 ETF, 防御+低位, 恒瑞医药居关注榜#10"),
])
    etf = "".join(f"""<div style="text-align:center;padding:9px 6px;background:var(--card2);border:1px solid var(--border);border-radius:9px">
<div style="font-size:23px;font-weight:700;color:var(--text)">{n}</div><div style="font-size:22px;color:var(--cyan);font-weight:700;margin-top:2px">{c}</div></div>""" for n, c in ETFS)
    body = f"""<div class="top-pill"><div class="pill" style="background:var(--cyan)">操作指南</div></div>
<div class="subtitle">三档怎么上?</div>
<div style="margin-top:10px">{tiers}</div>
<div style="margin-top:10px"><div style="font-size:23px;font-weight:700;color:var(--muted);margin-bottom:6px;padding-left:2px">上车标的参考 (ETF / 权重)</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px">{etf}</div></div>
    <div style="padding:12px 20px;background:linear-gradient(90deg,rgba(210,153,29,.12),rgba(210,153,29,.03));border-left:4px solid var(--orange);border-radius:8px;margin-top:10px">
  <div style="font-size:23px;font-weight:900;color:var(--orange)">散户提醒</div>
  <div style="font-size:23px;color:var(--text2);margin-top:2px">弱市抱团有持续性, 但中药已处 3 年 78% 高位 — 连板高位控仓, 节奏 &gt; 方向</div>
</div>
<div style="display:flex;gap:8px;margin-top:10px">
  <div style="flex:1;text-align:center;padding:9px 4px;background:var(--card2);border:1px solid var(--border);border-radius:9px"><div style="font-size:24px;font-weight:900;color:var(--gold)">盘前情报</div><div style="font-size:19px;color:var(--muted);margin-top:1px">9:15 递给你</div></div>
  <div style="flex:1;text-align:center;padding:9px 4px;background:var(--card2);border:1px solid var(--border);border-radius:9px"><div style="font-size:24px;font-weight:900;color:var(--red)">涨停复盘</div><div style="font-size:19px;color:var(--muted);margin-top:1px">天梯/炸板</div></div>
  <div style="flex:1;text-align:center;padding:9px 4px;background:var(--card2);border:1px solid var(--border);border-radius:9px"><div style="font-size:24px;font-weight:900;color:var(--purple)">真假热度</div><div style="font-size:19px;color:var(--muted);margin-top:1px">照妖镜</div></div>
</div>
<div style="padding:14px 20px;background:linear-gradient(135deg,var(--gold) 0%,#e8b73a 100%);border-radius:12px;text-align:center;margin-top:10px;box-shadow:0 6px 20px rgba(240,192,64,.3)">
  <div style="font-size:30px;font-weight:900;color:var(--bg)">点关注 + 收藏, 每天 3 分钟看懂 A 股</div>
  <div style="font-size:23px;color:var(--bg);margin-top:4px;opacity:.9">明早 9:15 盘前情报 · 涨停复盘 · 真假热度雷达</div>
</div>
<div style="text-align:center;margin-top:8px">
  <div style="font-size:25px;font-weight:900;color:var(--cyan)">评论区告诉我</div>
  <div style="font-size:24px;color:var(--text2)">医药今天你上了吗? 明天减仓还是持有? 想看哪只点名 💬</div>
</div>
<div class="footer"><span>* 复旦杰伦 / 数据驱动 / 不构成投资建议</span><span>8/8</span></div>"""
    return base_html(body)


PAGE_HTML_GENERATORS = [page_1_html, page_2_html, page_3_html, page_4_html, page_5_html,
                        page_6_html, page_7_html, page_8_html]


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
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 9)]
    w, h = pages[0].size
    cols, rows = 4, 2
    tw, th = 420, 540
    canvas = Image.new("RGB", (cols * tw + (cols - 1) * 4, rows * th + (rows - 1) * 4), color=(13, 17, 23))
    for i, im in enumerate(pages):
        r, c = divmod(i, cols)
        canvas.paste(im.resize((tw, th)), (c * (tw + 4), r * (th + 4)))
    canvas.save(OUT / "preview_2x4.png")
    print("  saved preview_2x4.png")
    th = sum(im.height for im in pages)
    stacked = Image.new("RGB", (w, th), color=(13, 17, 23))
    y = 0
    for im in pages:
        stacked.paste(im, (0, y)); y += im.height
    stacked.resize((720, int(th * 720 / w))).save(OUT / "all_pages_stacked.png")
    print("  saved all_pages_stacked.png")


if __name__ == "__main__":
    print(f"HTML 8 页深度卡片 -> {OUT}")
    render_all()
    make_preview()
    print("\n完成. 8 张 2160x2880 PNG")
