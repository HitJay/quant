"""7/31 风格大切换 · 7 页小红书卡片 (HTML+Playwright)

选题: 复盘类 #2 — 7/31 科技大反攻, 一天之内风格大切换
数据源: 公开财经媒体 (东方财富/每日经济新闻/同花顺) 2026-07-31 收盘 + 周回顾
注: 不编造历史回测胜率, 故无胜率页; 改用 政策三重磅 / 海外催化 两页填充

产出:
  output/hotspot/20260731/xhs_style_switch_html_v1/
    page_1.html .. page_7.html   单页 (1080x1440)
    all_in_one.html              7 页纵向合并预览
    page_1.png  .. page_7.png    (若安装 playwright)
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path("/workspace")
DATE = "20260731"
DAY_HUM = "2026-07-31"
TOPIC = "style_switch"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

# ─── 数据常量 (来自公开财经媒体 2026-07-31) ─────
GEM_PCT = 3.06            # 创业板指
KECHUANG_PCT_STR = "涨超6%"  # 科创综指
TURNOVER_YI = 2.54        # 万亿
TURNOVER_DELTA = 2000     # 亿 放量
MAIN_NET_IN = 763.49      # 亿 全天主力净流入
UP_COUNT = 4700           # 近4700只上涨

# 流入板块 (申万一级, 亿)
INFLOW = [
    ("电子", 307.65, "+3.53%"),
    ("计算机", 97.43, "+5.56%"),
    ("通信", 72.0, "—"),
    ("传媒", 70.0, "+12.81%(周)"),
    ("机械设备", 42.42, "—"),
    ("有色金属", 34.80, "—"),
]
# 流出板块 (风格切换撤防)
OUTFLOW = [
    ("通信设备", -210.0, "周流出第一"),
    ("银行", -26.78, "高位回调"),
    ("煤炭", -18.0, "防御撤防"),
    ("保险", -6.47, "—"),
    ("石油石化", -15.0, "—"),
]

# 概念涨幅
CONCEPTS = [
    ("MCP概念", 10.36, "AI智能体"),
    ("Kimi概念", 9.17, "大模型"),
    ("AI漫剧", 8.64, "AI应用"),
    ("财税数字化", 6.43, "用友/税友涨停"),
    ("算力租赁", 7.8, "美利云/云赛智联涨停"),
]

# 20cm 涨停 + 涨停
STOCKS_20CM = [
    ("中文在线", 20.0, "AI语料"),
    ("荣信文化", 20.0, "AI漫剧"),
    ("蓝色光标", 20.0, "AI营销"),
    ("易点天下", 20.0, "AI营销"),
    ("普联软件", 20.0, "财税数字化"),
    ("宏景科技", 20.0, "财税数字化"),
]
STOCKS_ZT = [
    ("昆仑万维", 10.0, "大模型"),
    ("天娱数科", 10.0, "AI数字人"),
    ("利欧股份", 10.0, "AI营销"),
    ("用友网络", 10.0, "财税SaaS"),
    ("税友股份", 10.0, "财税数字化"),
    ("美利云", 10.0, "算力租赁"),
]

# 个股主力净流入 TOP (亿)
TOP_INFLOW = [
    ("东山精密", 33.44, "中报预增+PCB"),
    ("太极实业", 27.00, "存储龙头"),
    ("蓝色光标", 24.19, "AI应用龙头"),
    ("中国巨石", 20.26, "玻纤/电子布"),
    ("新易盛", 17.99, "光通信回归"),
    ("中际旭创", 17.40, "光通信回归"),
    ("生益科技", 13.50, "PCB覆铜板"),
    ("三环集团", 13.31, "MLCC"),
]

# 政策三重磅
POLICY = [
    ("央行", "8000亿科创再贷款 + 2.1万亿逆回购", "定向半导体/算力/人形机器人融资扩产", "--red"),
    ("证监会", "资本市场韧性建设三动作", "平准基金优化 + 科技并购简化 + 中长期资金加仓", "--cyan"),
    ("四部门", "22条金融治理新规", "穿透监管大股东 + 强化中小投资者保护", "--gold"),
]

# 海外催化
OVERSEAS = [
    ("微软", "+15.5%", "Azure收入+43%, 单日市值+4500亿美元(美股史纪录)"),
    ("美光科技", "+18%", "存储需求持续至2028"),
    ("亚马逊", "2200亿$", "2026资本开支上调, 算力需求至2028"),
    ("韩国KOSPI", "+17.91%", "史上最大单日涨幅, SK海力士+23.9%/三星+20.5%"),
    ("三星电子", "Q2利润+1814%", "预判存储短缺至2028, 长协占比提至60-70%"),
]

# ─── 全局 CSS (沿用本库暗色主题) ─────
BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0d1117; --card: #161b22; --card2: #1c2129;
  --border: #30363d; --text: #e6edf3; --text2: #c9d1d9;
  --muted: #8b949e; --dim: #6e7681;
  --blue: #58a6ff; --green: #3fb950; --red: #f85149; --rose: #ff7b72;
  --orange: #d2991d; --purple: #bc8cff; --gold: #f0c040; --gold2: #ffd77a; --cyan: #56d4dd;
}
body {
  width: 1080px; height: 1440px; background: var(--bg);
  font-family: 'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;
  color: var(--text); overflow: hidden; position: relative;
  display: flex; flex-direction: column; justify-content: space-between;
  padding: 32px 46px 18px; font-size: 27px;
}
body::before { content:''; position:absolute; top:-300px; right:-300px; width:900px; height:900px;
  background: radial-gradient(circle, rgba(248,81,73,0.07) 0%, transparent 60%); pointer-events:none; z-index:0; }
body::after { content:''; position:absolute; bottom:-400px; left:-300px; width:900px; height:900px;
  background: radial-gradient(circle, rgba(86,212,221,0.05) 0%, transparent 60%); pointer-events:none; z-index:0; }
body > * { position: relative; z-index: 1; }
.pill { display:inline-block; padding:8px 26px; border-radius:24px; font-size:28px; font-weight:700; color:var(--bg); text-align:center; letter-spacing:.5px; }
.top-pill { display:flex; justify-content:center; }
.subtitle { text-align:center; font-size:42px; font-weight:700; color:var(--text); margin-top:18px; letter-spacing:.3px; }
.subtitle-sm { text-align:center; font-size:25px; color:var(--muted); margin-top:8px; font-style:italic; }
.footer { margin-top:14px; padding-top:12px; display:flex; justify-content:space-between; font-size:22px; color:var(--dim); border-top:1px solid var(--border); }
.big-num { font-weight:900; line-height:1; letter-spacing:-1px; }
.card { background:var(--card); border:1px solid var(--border); border-radius:14px; padding:18px 22px; }
"""
FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'


def base_html(body: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">{FONT_LINK}
<style>{BASE_CSS}{extra_css}</style></head><body>{body}</body></html>"""


# ═══ P1 封面 ═══
def page_1_html() -> str:
    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} · 风格大切换</div></div>
<div class="subtitle" style="font-size:40px">7月最后一天, A股一天内权力洗牌</div>

<div style="text-align:center;margin-top:30px">
  <div style="font-size:26px;color:var(--muted);margin-bottom:6px">创业板指 收盘</div>
  <div class="big-num" style="font-size:200px;background:linear-gradient(180deg,#ff7b72 0%,#f85149 60%,#c93030 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;padding:10px 0;filter:drop-shadow(0 4px 12px rgba(248,81,73,.3))">+{GEM_PCT:.2f}%</div>
  <div style="font-size:28px;color:var(--cyan);margin-top:10px;font-weight:600">科创综指 {KECHUANG_PCT_STR} · 近 4700 只个股上涨</div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:40px">
  <div class="card" style="text-align:center;padding:22px 12px"><div class="big-num" style="font-size:62px;color:var(--gold)">{TURNOVER_YI}万亿</div><div style="font-size:24px;color:var(--muted);margin-top:8px">两市成交 · 放量{TURNOVER_DELTA}亿</div></div>
  <div class="card" style="text-align:center;padding:22px 12px"><div class="big-num" style="font-size:62px;color:var(--red)">+{MAIN_NET_IN}亿</div><div style="font-size:24px;color:var(--muted);margin-top:8px">主力净流入 · 22行业净入</div></div>
  <div class="card" style="text-align:center;padding:22px 12px"><div class="big-num" style="font-size:62px;color:var(--purple)">+307.65亿</div><div style="font-size:24px;color:var(--muted);margin-top:8px">电子行业 · 全市场NO.1</div></div>
</div>

<div style="margin-top:34px;padding:26px 30px;background:linear-gradient(135deg,var(--card) 0%,#1a1a1f 100%);border:2px solid var(--orange);border-radius:16px;box-shadow:0 0 28px rgba(210,153,29,.15);text-align:center">
  <div style="font-size:30px;color:var(--text2);margin-bottom:12px">钱从哪里来 → 钱去哪里</div>
  <div class="big-num" style="font-size:60px;background:linear-gradient(90deg,var(--cyan) 0%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent">银行 / 煤炭 / 保险 撤退</div>
  <div style="font-size:28px;color:var(--red);margin-top:12px;font-weight:700">→ 半导体 · AI应用 · 机器人 接管</div>
</div>

<div style="margin-top:auto;text-align:center;padding-bottom:10px">
  <div style="display:inline-block;padding:14px 30px;background:var(--card);border:1.5px solid var(--cyan);border-radius:14px;font-size:28px;font-weight:700;color:var(--cyan);box-shadow:0 4px 16px rgba(86,212,221,.15)">一天之内, 老经济撤、新科技上</div>
  <div style="font-size:24px;color:var(--muted);font-style:italic;margin-top:14px">翻到下一页 → 看资金搬家实证</div>
</div>

<div class="footer"><span>* 数据: 东方财富/每日经济新闻 · 不构成投资建议</span><span>1/7</span></div>"""
    return base_html(body)


# ═══ P2 资金搬家: 流入 vs 流出 ═══
def page_2_html() -> str:
    max_in = max(i[1] for i in INFLOW)
    max_out = abs(min(o[1] for o in OUTFLOW))
    in_rows = []
    for name, amt, tag in INFLOW:
        bar_w = amt / max_in * 100
        in_rows.append(f"""<div style="display:grid;grid-template-columns:150px 1fr 130px;align-items:center;gap:12px;padding:11px 10px;border-bottom:1px solid rgba(48,54,61,.4)">
<div style="font-size:30px;font-weight:700;color:var(--text)">{name}</div>
<div style="height:24px;background:rgba(48,54,61,.25);border-radius:6px;overflow:hidden"><div style="width:{bar_w:.1f}%;height:100%;background:linear-gradient(90deg,rgba(248,81,73,.5),var(--red));border-radius:6px"></div></div>
<div style="font-size:30px;font-weight:900;color:var(--red);text-align:right">+{amt:.1f}亿</div></div>""")
    out_rows = []
    for name, amt, tag in OUTFLOW:
        bar_w = abs(amt) / max_out * 100
        out_rows.append(f"""<div style="display:grid;grid-template-columns:150px 1fr 130px;align-items:center;gap:12px;padding:11px 10px;border-bottom:1px solid rgba(48,54,61,.4)">
<div style="font-size:30px;font-weight:700;color:var(--text2)">{name}</div>
<div style="height:24px;background:rgba(48,54,61,.25);border-radius:6px;overflow:hidden"><div style="width:{bar_w:.1f}%;height:100%;background:linear-gradient(90deg,rgba(63,185,80,.5),var(--green));border-radius:6px"></div></div>
<div style="font-size:30px;font-weight:900;color:var(--green);text-align:right">{amt:.1f}亿</div></div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--blue)">资金搬家</div></div>
<div class="subtitle">一天之内, 主力在买谁、卖谁?</div>
<div class="subtitle-sm">申万一级行业 · 主力净流入 / 流出</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px">
  <div>
    <div style="text-align:center;font-size:30px;font-weight:900;color:var(--red);margin-bottom:10px">▲ 流入 TOP6</div>
    <div class="card" style="padding:8px 14px">{"".join(in_rows)}</div>
  </div>
  <div>
    <div style="text-align:center;font-size:30px;font-weight:900;color:var(--green);margin-bottom:10px">▼ 流出 TOP5</div>
    <div class="card" style="padding:8px 14px">{"".join(out_rows)}</div>
  </div>
</div>

<div style="margin-top:22px;padding:20px 26px;background:var(--card2);border-left:5px solid var(--orange);border-radius:10px">
  <div style="font-size:28px;font-weight:900;color:var(--orange);margin-bottom:6px">一句话定性</div>
  <div style="font-size:25px;color:var(--text2);line-height:1.5">钱从 <b style="color:var(--green)">"光模块+高股息"</b> 撤出, 灌进 <b style="color:var(--red)">"半导体设备材料 + AI应用 + 低位制造"</b>。这是"成长再平衡", 不是长期撤防。</div>
</div>

<div style="margin-top:auto;padding:18px 24px;background:linear-gradient(135deg,rgba(86,212,221,.1),rgba(86,212,221,.02));border:1.5px solid var(--cyan);border-radius:12px;text-align:center;margin-bottom:8px">
  <div style="font-size:30px;font-weight:900;color:var(--cyan)">电子 +307.65亿 = 全市场 40% 净流入</div>
  <div style="font-size:24px;color:var(--muted);margin-top:8px;font-style:italic">下一页 → 这波科技涨的是硬件还是应用?</div>
</div>

<div class="footer"><span>* 数据: 同花顺/东方财富 申万一级</span><span>2/7</span></div>"""
    return base_html(body)


# ═══ P3 AI应用爆发 + 个股净流入 ═══
def page_3_html() -> str:
    cm_rows = []
    for name, pct, tag in CONCEPTS:
        cm_rows.append(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:9px 16px;border-bottom:1px solid var(--border)">
<div style="font-size:27px;color:var(--text2);font-weight:500">{name}<span style="font-size:21px;color:var(--dim);margin-left:8px">{tag}</span></div>
<div style="font-size:28px;font-weight:900;color:var(--red)">+{pct:.2f}%</div></div>""")
    stk_rows = []
    for name, amt, tag in TOP_INFLOW:
        stk_rows.append(f"""<div style="display:grid;grid-template-columns:140px 110px 1fr;align-items:center;gap:10px;padding:8px 14px;border-bottom:1px solid rgba(48,54,61,.4)">
<div style="font-size:27px;font-weight:700;color:var(--text)">{name}</div>
<div style="font-size:28px;font-weight:900;color:var(--red);text-align:right">+{amt:.2f}亿</div>
<div style="font-size:22px;color:var(--muted)">{tag}</div></div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--purple)">AI应用爆发</div></div>
<div class="subtitle">这次涨的是"应用", 不是"硬件"</div>
<div class="subtitle-sm">20cm 涨停潮 · 软件ETF +5.68% · 米奥会展 +90%</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:22px">
  <div>
    <div style="text-align:center;font-size:28px;font-weight:900;color:var(--gold);margin-bottom:8px">概念涨幅 TOP5</div>
    <div class="card" style="padding:6px 12px">{"".join(cm_rows)}</div>
    <div style="margin-top:12px;padding:12px 16px;background:var(--card2);border:1px solid var(--border);border-radius:10px;font-size:23px;color:var(--text2);line-height:1.5">
      20cm涨停: <b style="color:var(--red)">中文在线 / 荣信文化 / 蓝色光标 / 易点天下</b><br>涨停: 昆仑万维 · 天娱数科 · 利欧股份
    </div>
  </div>
  <div>
    <div style="text-align:center;font-size:28px;font-weight:900;color:var(--cyan);margin-bottom:8px">个股净流入 TOP8</div>
    <div class="card" style="padding:6px 12px">{"".join(stk_rows)}</div>
  </div>
</div>

<div style="margin-top:22px;padding:20px 26px;background:linear-gradient(135deg,var(--card) 0%,rgba(188,140,255,.08) 100%);border:2px solid var(--purple);border-radius:14px;text-align:center;box-shadow:0 0 24px rgba(188,140,255,.15)">
  <div style="font-size:30px;font-weight:900;color:var(--purple)">为什么是"应用"赢?</div>
  <div style="font-size:25px;color:var(--text2);margin-top:8px;line-height:1.5">OpenAI发Presence智能体平台 + 中国大模型全球份额 <b style="color:var(--gold)">63.5%</b> 反超美国</div>
  <div style="font-size:23px;color:var(--muted);margin-top:6px">机构卖"翻几倍的老AI硬件", 买"超跌新半导体+应用端"</div>
</div>

<div class="footer"><span>* 数据: 东方财富概念板块 + 个股资金流</span><span>3/7</span></div>"""
    return base_html(body)


# ═══ P4 政策三重磅 ═══
def page_4_html() -> str:
    cards = []
    for who, title, desc, col in POLICY:
        cards.append(f"""<div style="display:flex;gap:20px;padding:22px 24px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,.3) 100%);border:2px solid var({col});border-radius:14px;box-shadow:0 4px 18px rgba(0,0,0,.3)">
<div style="min-width:120px;padding:14px 18px;background:var({col});color:var(--bg);border-radius:18px;font-size:30px;font-weight:900;text-align:center;align-self:flex-start">{who}</div>
<div style="flex:1">
  <div style="font-size:32px;font-weight:900;color:var(--text)">{title}</div>
  <div style="font-size:25px;color:var(--muted);margin-top:6px;line-height:1.4">{desc}</div>
</div>
</div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--gold)">政策三重磅</div></div>
<div class="subtitle">7/31 傍晚, 央行证监会同步出手</div>
<div class="subtitle-sm">流动性打底 · 制度完善 · 长期资金托底</div>

<div style="display:flex;flex-direction:column;gap:16px;margin-top:26px">
  {"".join(cards)}
</div>

<div style="margin-top:24px;padding:22px 28px;background:linear-gradient(135deg,var(--card) 0%,rgba(240,192,64,.08) 100%);border:2px solid var(--gold);border-radius:14px;text-align:center;box-shadow:0 0 24px rgba(240,192,64,.15)">
  <div style="font-size:30px;font-weight:900;color:var(--gold)">三条消息层层递进</div>
  <div style="font-size:25px;color:var(--text2);margin-top:10px;line-height:1.5">央行解决 <b style="color:var(--cyan)">"钱从哪来"</b> · 证监会解决 <b style="color:var(--cyan)">"钱往哪去"</b></div>
  <div style="font-size:24px;color:var(--muted);margin-top:8px">8000亿科创再贷款定向: 半导体 · 算力中心 · 人形机器人 · 高端制造</div>
</div>

<div style="margin-top:auto;padding:16px 22px;background:var(--card2);border-left:5px solid var(--cyan);border-radius:8px;margin-bottom:8px">
  <div style="font-size:26px;font-weight:900;color:var(--cyan)">政策底信号</div>
  <div style="font-size:23px;color:var(--text2);margin-top:4px">盘后傍晚多部门同步出政策, 从来不是短期情绪消息, 是重塑下半年市场底层逻辑的催化</div>
</div>

<div class="footer"><span>* 数据: 央行/证监会公开公告 2026-07-31</span><span>4/7</span></div>"""
    return base_html(body)


# ═══ P5 海外催化链 ═══
def page_5_html() -> str:
    rows = []
    for name, pct, desc in OVERSEAS:
        col = "--red" if "+" in pct or "亿" in pct else "--gold"
        rows.append(f"""<div style="display:grid;grid-template-columns:170px 160px 1fr;align-items:center;gap:14px;padding:13px 16px;border-bottom:1px solid var(--border)">
<div style="font-size:30px;font-weight:900;color:var(--text)">{name}</div>
<div style="font-size:30px;font-weight:900;color:var({col});text-align:center">{pct}</div>
<div style="font-size:23px;color:var(--muted);line-height:1.4">{desc}</div></div>""")

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--red)">海外催化</div></div>
<div class="subtitle">隔夜全球科技股集体暴动</div>
<div class="subtitle-sm">A股7/31反攻的外部导火索</div>

<div style="margin-top:24px" class="card">
  <div style="display:grid;grid-template-columns:170px 160px 1fr;gap:14px;padding:8px 16px;font-size:22px;font-weight:900;color:var(--muted);border-bottom:1.5px solid var(--border)">
    <div>标的</div><div style="text-align:center">涨跌/数据</div><div>关键信息</div></div>
  {"".join(rows)}
</div>

<div style="margin-top:22px;display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div class="card" style="text-align:center;padding:18px 12px">
    <div style="font-size:24px;color:var(--muted);margin-bottom:6px">亚马逊 2026 资本开支</div>
    <div class="big-num" style="font-size:54px;color:var(--gold)">2200亿$</div>
    <div style="font-size:21px;color:var(--muted);margin-top:4px">CEO: 算力需求持续至2028</div>
  </div>
  <div class="card" style="text-align:center;padding:18px 12px">
    <div style="font-size:24px;color:var(--muted);margin-bottom:6px">中国大模型全球份额</div>
    <div class="big-num" style="font-size:54px;color:var(--purple)">63.5%</div>
    <div style="font-size:21px;color:var(--muted);margin-top:4px">反超美国(35.5%) · OpenRouter</div>
  </div>
</div>

<div style="margin-top:auto;padding:20px 26px;background:linear-gradient(135deg,var(--red) 0%,#c93030 100%);border-radius:14px;text-align:center;box-shadow:0 6px 24px rgba(248,81,73,.3);margin-bottom:8px">
  <div style="font-size:32px;font-weight:900;color:var(--bg)">外部暴涨 + 内部政策 + 产业超跌修复</div>
  <div style="font-size:25px;color:var(--bg);margin-top:8px;opacity:.85">三者共振, 才有了科技成长全线反攻</div>
</div>

<div class="footer"><span>* 数据: 美股/韩股公开行情 2026-07-30~31</span><span>5/7</span></div>"""
    return base_html(body)


# ═══ P6 风险提示 + 三档操作 ═══
def page_6_html() -> str:
    tiers = [
        ("激进", "--red", "已入AI应用 → 别恋战, 按事件驱动做, 破5日线走人, 不走连板就持有"),
        ("稳健", "--orange", "未入 → 别追首日大阳, 等3日内回踩MA10/MA20分批, 5G/算力租赁方向优先"),
        ("长线", "--cyan", "定投科创50ETF(588280)/科创芯片ETF(588290) · 月定投, 不看单日波动"),
    ]
    tier_rows = "".join(f"""<div style="display:flex;align-items:center;gap:18px;padding:16px 20px;background:var(--card);border:1px solid var(--border);border-radius:12px">
<div style="min-width:84px;padding:12px 18px;background:var({col});color:var(--bg);border-radius:22px;font-size:28px;font-weight:900;text-align:center">{tag}</div>
<div style="font-size:25px;color:var(--text2);line-height:1.5;flex:1">{b}</div>
</div>""" for tag, col, b in tiers)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--cyan)">操作建议</div></div>
<div class="subtitle">涨了一天, 散户该怎么动?</div>

<div style="margin-top:22px;padding:20px 24px;background:linear-gradient(135deg,rgba(210,153,29,.12),rgba(210,153,29,.03));border-left:5px solid var(--orange);border-radius:10px">
  <div style="font-size:28px;font-weight:900;color:var(--orange);margin-bottom:8px">先看 4 个风险</div>
  <div style="font-size:24px;color:var(--text2);line-height:1.6">
    1. 双创月度跌幅仍超 <b style="color:var(--red)">20%</b>, 一根阳线不改趋势<br>
    2. 通信设备周流出 <b style="color:var(--green)">-210亿</b>, 光模块筹码松动未解<br>
    3. 长鑫上市首日换手 <b style="color:var(--red)">66%+</b>, 次日巨震概率大<br>
    4. 7/31是<b style="color:var(--orange)">月末收官</b>, 8月初风格可能再漂移
  </div>
</div>

<div style="margin-top:22px">
  <div style="text-align:center;font-size:29px;font-weight:900;color:var(--text);margin-bottom:12px">三档操作建议</div>
  <div style="display:flex;flex-direction:column;gap:12px">{tier_rows}</div>
</div>

<div style="margin-top:auto;padding:18px 24px;background:var(--card2);border:1.5px solid var(--red);border-radius:12px;margin-bottom:8px">
  <div style="font-size:27px;font-weight:900;color:var(--red);margin-bottom:6px">核心判断</div>
  <div style="font-size:24px;color:var(--text2);line-height:1.5">这是<b style="color:var(--orange)">"成长再平衡"</b>, 不是趋势反转。高位AI硬件(易中天)别接飞刀, 低位应用/半导体材料可逢回踩埋伏。中报窗口看利润兑现, 别听故事。</div>
</div>

<div class="footer"><span>* 仅供参考, 不构成投资建议</span><span>6/7</span></div>"""
    return base_html(body)


# ═══ P7 CTA ═══
def page_7_html() -> str:
    cards = [
        ("01", "复盘", "--red", "涨停天梯 · 资金搬家 · 风格切换追踪"),
        ("02", "雷达", "--purple", "AI应用 vs 硬件 · 主力净流入榜单"),
        ("03", "反共识", "--cyan", "拒绝小作文 · 数据驱动 · 拒绝喊单"),
    ]
    card_rows = "".join(f"""<div style="display:flex;align-items:center;gap:22px;padding:24px 26px;background:linear-gradient(135deg,var(--card) 0%,rgba(0,0,0,.3) 100%);border:2px solid var({col});border-radius:16px;box-shadow:0 4px 20px rgba(0,0,0,.3)">
<div style="font-size:72px;font-weight:900;color:var({col});min-width:90px;text-align:center;line-height:1;filter:drop-shadow(0 2px 8px rgba(0,0,0,.4))">{num}</div>
<div style="flex:1"><div style="font-size:34px;font-weight:900;color:var(--text)">{title}</div><div style="font-size:25px;color:var(--muted);margin-top:6px">{b}</div></div>
</div>""" for num, title, col, b in cards)

    body = f"""
<div class="top-pill"><div class="pill" style="background:var(--rose)">关注我</div></div>
<div style="text-align:center;font-size:30px;font-style:italic;color:var(--text2);margin-top:18px">8月科技还能续命吗? 数据每天替你盯</div>

<div style="text-align:center;margin-top:30px">
  <div style="font-size:54px;color:var(--text);margin-bottom:12px">每天 3 分钟</div>
  <div class="big-num" style="font-size:80px;background:linear-gradient(90deg,var(--gold) 0%,var(--gold2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(240,192,64,.3))">看懂 A 股风格</div>
</div>

<div style="display:flex;flex-direction:column;gap:14px;margin-top:30px">{card_rows}</div>

<div style="margin-top:28px;padding:26px 30px;background:linear-gradient(135deg,var(--gold) 0%,#e8b73a 100%);border-radius:16px;text-align:center;box-shadow:0 8px 32px rgba(240,192,64,.35)">
  <div style="font-size:40px;font-weight:900;color:var(--bg)">点关注 + 收藏 不迷路</div>
  <div style="font-size:26px;color:var(--bg);margin-top:8px;opacity:.8">明早 9:15 继续给你递盘前情报</div>
</div>

<div style="margin-top:auto;text-align:center;padding-bottom:10px">
  <div style="font-size:28px;font-weight:900;color:var(--cyan);margin-bottom:8px">评论区告诉我</div>
  <div style="font-size:26px;color:var(--text2);margin-bottom:6px">7/31你回血了吗? 8月押科技还是押红利?</div>
  <div style="font-size:22px;color:var(--muted)">明天想看哪个方向追踪? 评论区点名</div>
</div>

<div class="footer"><span>* 数据驱动 · 拒绝小作文 · 不构成投资建议</span><span>7/7</span></div>"""
    return base_html(body)


PAGE_GENERATORS = [page_1_html, page_2_html, page_3_html, page_4_html, page_5_html, page_6_html, page_7_html]


def write_html_only():
    """无 playwright 时: 输出 7 个独立 HTML + 一个合并预览"""
    pages = [g() for g in PAGE_GENERATORS]
    for i, html in enumerate(pages, 1):
        (OUT / f"page_{i}.html").write_text(html, encoding="utf-8")
    # 合并预览: 7 页纵向排列
    combined = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">{FONT_LINK}
<style>{BASE_CSS}
body{{width:auto;height:auto;display:block;padding:20px;background:#000}}
.page{{width:1080px;height:1440px;margin:0 auto 24px;box-shadow:0 4px 24px rgba(0,0,0,.6);border-radius:8px;overflow:hidden}}
</style></head><body>
{"".join(f'<div class="page">{html.split("<body>")[1].split("</body>")[0]}</div>' for html in pages)}
</body></html>"""
    (OUT / "all_in_one.html").write_text(combined, encoding="utf-8")
    print(f"  HTML 7 页 + 合并预览 -> {OUT}")


def render_png():
    """有 playwright 时: 渲染 7 张 PNG"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [skip] playwright 未安装, 仅输出 HTML")
        return False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1080, "height": 1440}, device_scale_factor=2, locale="zh-CN")
        page = ctx.new_page()
        for i, gen in enumerate(PAGE_GENERATORS, 1):
            out = OUT / f"page_{i}.png"
            page.set_content(gen(), wait_until="networkidle")
            page.wait_for_timeout(1500)
            page.screenshot(path=str(out), full_page=False)
            print(f"  saved page_{i}.png ({out.stat().st_size/1024:.0f}KB)")
        browser.close()
    return True


if __name__ == "__main__":
    print(f"7/31 风格大切换 · 7 页卡片 -> {OUT}")
    write_html_only()
    render_png()
    print("\n完成. HTML 可浏览器打开 all_in_one.html 预览全部 7 页")
