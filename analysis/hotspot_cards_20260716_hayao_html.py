"""哈药5连板 · 30年首次 — HTML+Playwright 深度量化版.
6 页, 1080×1440, base 27px, min 22px. 全量真实数据填充, 消除大片留白.
"""

from __future__ import annotations
from pathlib import Path

ROOT = Path("/das/user/QYJI/quant")
DATE = "20260716"; DAY_HUM = "2026-07-16"; TOPIC = "hayao_5ban"; VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

ZT_COUNT = 48; ZB_COUNT = 10; SEAL_RATE = 82.8

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">'

BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0d1117; --card: #161b22; --card2: #1c2129; --border: #30363d;
  --text: #e6edf3; --text2: #c9d1d9; --muted: #8b949e; --dim: #6e7681;
  --blue: #58a6ff; --green: #3fb950; --red: #f85149; --rose: #ff7b72;
  --orange: #d2991d; --gold: #f0c040; --cyan: #56d4dd; --purple: #bc8cff;
}
body {
  width: 1080px; height: 1440px;
  background: var(--bg);
  font-family: 'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;
  color: var(--text);
  overflow: hidden; position: relative;
  display: flex; flex-direction: column;
  padding: 32px 42px 22px;
}
body::before {
  content: ''; position: absolute; top: -300px; right: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(248,81,73,0.06) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body::after {
  content: ''; position: absolute; bottom: -400px; left: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(88,166,255,0.04) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body > * { position: relative; z-index: 1; }
.main { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.content-wrap { display: flex; flex-direction: column; gap: 12px; flex: 1; justify-content: space-between; }
.pill { display: inline-block; padding: 6px 22px; border-radius: 22px; font-size: 24px; font-weight: 700; color: var(--bg); text-align: center; }
.top-pill { display: flex; justify-content: center; }
.subtitle { text-align: center; font-size: 32px; font-weight: 700; color: var(--text); margin-top: 8px; }
.subtitle-sm { text-align: center; font-size: 22px; color: var(--muted); margin-top: 2px; font-style: italic; }
.footer { flex-shrink: 0; padding-top: 8px; display: flex; justify-content: space-between; font-size: 22px; color: var(--dim); border-top: 1px solid var(--border); }
.big-num { font-weight: 900; line-height: 1; letter-spacing: -1px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 20px; }
.glow-card { background: linear-gradient(135deg, var(--card) 0%, #1a1a1f 100%); border: 2px solid var(--orange); border-radius: 16px; padding: 18px 24px; box-shadow: 0 0 28px rgba(210,153,29,0.15); }
.hl { padding: 10px 16px; background: linear-gradient(90deg,rgba(210,153,29,0.12),transparent); border-left: 3px solid var(--orange); border-radius: 4px; font-size: 22px; }
.hl-red { padding: 10px 16px; background: linear-gradient(90deg,rgba(248,81,73,0.12),transparent); border-left: 3px solid var(--red); border-radius: 4px; font-size: 22px; }
.hl-cyan { padding: 10px 16px; background: linear-gradient(90deg,rgba(86,212,221,0.12),transparent); border-left: 3px solid var(--cyan); border-radius: 4px; font-size: 22px; }
.hdr { font-size: 22px; font-weight: 700; color: var(--text); }
.hdr-c { font-size: 22px; font-weight: 700; color: var(--text); text-align: center; }
"""

def base_html(main: str, footer_left: str, page_num: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">{FONT_LINK}
<style>{BASE_CSS}</style></head>
<body>
<div class="main">{main}</div>
<div class="footer"><span>{footer_left}</span><span>{page_num}/6</span></div>
</body></html>"""


# ═══════════════════════════════════════════
# P1 — 封面 · 5连板暴涨45%+全景快照
# ═══════════════════════════════════════════
def page_1_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--red)">{DAY_HUM} · 盘中深度</div></div>
<div style="text-align:center;font-size:52px;font-weight:900;margin-top:16px;color:var(--text);letter-spacing:2px">哈药股份 · 600664</div>
<div style="text-align:center;margin-top:14px">
  <div class="big-num" style="font-size:180px;background:linear-gradient(180deg,#ff7b72,#f85149 60%,#c93030);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 12px rgba(248,81,73,0.3))">5 连板</div>
  <div style="font-size:24px;color:var(--muted);margin-top:6px">30年历史首次 · 上市以来最高连板纪录</div>
</div>
<div class="glow-card" style="padding:18px 14px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px">
    <div style="text-align:center">
      <div class="big-num" style="font-size:48px;color:var(--red)">4.49</div>
      <div style="font-size:20px;color:var(--muted);margin-top:6px">最新价 (元)</div>
    </div>
    <div style="text-align:center">
      <div class="big-num" style="font-size:48px;color:var(--red)">+45.3%</div>
      <div style="font-size:20px;color:var(--muted);margin-top:6px">5日涨幅</div>
    </div>
    <div style="text-align:center">
      <div class="big-num" style="font-size:48px;color:var(--orange)">3.61x</div>
      <div style="font-size:20px;color:var(--muted);margin-top:6px">量能倍数</div>
    </div>
    <div style="text-align:center">
      <div class="big-num" style="font-size:48px;color:var(--cyan)">+38.3%</div>
      <div style="font-size:20px;color:var(--muted);margin-top:6px">距MA20</div>
    </div>
  </div>
</div>
<div class="hdr-c" style="margin-top:2px">↓ 30年3次4连板后都发生了什么? ↓</div>
<div class="card" style="padding:10px 18px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;font-size:22px;font-weight:700;color:var(--muted);text-align:center;border-bottom:1px solid var(--border);padding-bottom:6px">
    <div>日期</div><div>连板</div><div>T+1</div><div>T+5</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;font-size:22px;padding:6px 0;text-align:center;border-bottom:1px solid var(--border)">
    <div style="color:var(--text2)">1994-08</div><div style="color:var(--text2)">4连板</div><div style="font-weight:700;color:var(--green)">-18.6%</div><div style="color:var(--text2)">+1.7%</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;font-size:22px;padding:6px 0;text-align:center;border-bottom:1px solid var(--border)">
    <div style="color:var(--text2)">2020-02</div><div style="color:var(--text2)">4连板(疫情)</div><div style="color:var(--text2)">+2.0%</div><div style="font-weight:700;color:var(--green)">-20.7%</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;font-size:22px;padding:6px 0;text-align:center;background:linear-gradient(90deg,rgba(248,81,73,0.12),transparent);border-radius:4px">
    <div style="font-weight:700;color:var(--red)">2026-07</div><div style="font-weight:700;color:var(--red)">5连板!</div><div style="color:var(--cyan)">进行中</div><div style="color:var(--gold)">历史首次</div>
  </div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
  <div class="card" style="text-align:center;padding:10px 8px">
    <div style="font-size:20px;color:var(--muted)">医药链涨停</div>
    <div class="big-num" style="font-size:36px;color:var(--red);margin-top:4px">9只</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 8px">
    <div style="font-size:20px;color:var(--muted)">全市场涨停</div>
    <div class="big-num" style="font-size:36px;color:var(--red);margin-top:4px">{ZT_COUNT}</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 8px">
    <div style="font-size:20px;color:var(--muted)">封板率</div>
    <div class="big-num" style="font-size:36px;color:var(--cyan);margin-top:4px">{SEAL_RATE:.0f}%</div>
  </div>
</div>
<div class="hl-cyan" style="text-align:center">
  <span style="font-weight:700;color:var(--cyan)">30年3次4连板后全部大跌, 这次呢?</span>
  <span style="color:var(--muted);font-style:italic;margin-left:8px">翻页 → 涨停全景 + 历史胜率</span>
</div>
</div>""", "* 数据: 东方财富/雪球/新浪", "1")


# ═══════════════════════════════════════════
# P2 — 涨停天梯 + 历史胜率 + 概念温度
# ═══════════════════════════════════════════
def page_2_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--red)">涨停天梯 + 历史胜率</div></div>
<div class="subtitle">{DAY_HUM} · {ZT_COUNT} 只涨停 · 封板率 {SEAL_RATE:.0f}%</div>
<div class="hdr">连板天梯 TOP6</div>
<div class="card" style="padding:10px 20px;font-size:22px;line-height:1.85">
  · 哈药股份 <b style="color:var(--red)">5连板</b> 化学制药 +10.02% (30年首次)<br>
  · 云创退 <b style="color:var(--orange)">4连板</b> IT服务 +30.00%<br>
  · 艾艾精工 <b style="color:var(--gold)">3连板</b> 塑料 +9.99%<br>
  · 贤丰控股 <b style="color:var(--gold)">3连板</b> 元件 +9.98% (生物疫苗龙头)<br>
  · 九安医疗 <b style="color:var(--gold)">3连板</b> 医疗器械 +10.00%<br>
  · 永安药业 <b style="color:var(--gold)">2连板</b> 化学制药 +10.02%
</div>
<div class="hdr">涨停行业分布 TOP5</div>
<div class="card" style="padding:14px 12px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:8px;text-align:center">
    <div><div style="font-size:20px;color:var(--muted)">消费电子</div><div style="font-size:34px;font-weight:900;color:var(--gold)">5</div></div>
    <div><div style="font-size:20px;color:var(--muted)">化学制药</div><div style="font-size:34px;font-weight:900;color:var(--gold)">3</div></div>
    <div><div style="font-size:20px;color:var(--muted)">塑料</div><div style="font-size:34px;font-weight:900;color:var(--gold)">3</div></div>
    <div><div style="font-size:20px;color:var(--muted)">元件</div><div style="font-size:34px;font-weight:900;color:var(--gold)">3</div></div>
    <div><div style="font-size:20px;color:var(--muted)">医疗服务</div><div style="font-size:34px;font-weight:900;color:var(--gold)">3</div></div>
  </div>
</div>
<div class="hdr-c">哈药4连板历史后续走势</div>
<div class="card" style="padding:10px 20px;font-size:22px">
  <div style="display:grid;grid-template-columns:110px 100px 1fr 90px 130px;gap:6px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:6px">
    <div>开始</div><div>结束</div><div>连板</div><div>期间</div><div>T+1 / T+5</div>
  </div>
  <div style="display:grid;grid-template-columns:110px 100px 1fr 90px 130px;gap:6px;padding:7px 0;border-bottom:1px solid var(--border)">
    <div>1994-08</div><div>08-08</div><div>4连板</div><div>+68.6%</div><div style="color:var(--green)">-18.6% / +1.7%</div>
  </div>
  <div style="display:grid;grid-template-columns:110px 100px 1fr 90px 130px;gap:6px;padding:7px 0;border-bottom:1px solid var(--border)">
    <div>2020-02</div><div>02-06</div><div>4连板(疫情)</div><div>+33.2%</div><div style="color:var(--green)">+2.0% / -20.7%</div>
  </div>
  <div style="display:grid;grid-template-columns:110px 100px 1fr 90px 130px;gap:6px;padding:7px 0;background:linear-gradient(90deg,rgba(248,81,73,0.12),transparent);border-radius:4px">
    <div style="font-weight:700;color:var(--red)">2026-07</div><div>07-16</div><div style="font-weight:700;color:var(--red)">5连板!</div><div>+45.3%</div><div style="color:var(--gold)">30年首次</div>
  </div>
</div>
<div class="hdr-c">全市场概念板块温度 (医药之外)</div>
<div class="card" style="padding:12px 20px">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;font-size:22px;line-height:1.7">
    <div>
      <div style="font-size:22px;font-weight:700;color:var(--red);margin-bottom:4px">涨幅TOP3</div>
      互联网服务 <b style="color:var(--red)">+2.08%</b> (智度股份)<br>
      移动支付 <b style="color:var(--red)">+1.83%</b> (美格智能)<br>
      旅游酒店 <b style="color:var(--red)">+1.82%</b> (*ST西旅)
    </div>
    <div>
      <div style="font-size:22px;font-weight:700;color:var(--green);margin-bottom:4px">跌幅TOP3</div>
      蓝宝石 <b style="color:var(--green)">-2.28%</b> (蓝思科技)<br>
      煤化工 <b style="color:var(--green)">-1.22%</b> (天沃科技)<br>
      新材料 <b style="color:var(--green)">-0.80%</b> (道明光学)
    </div>
  </div>
</div>
<div class="hl">
  <span style="font-weight:700;color:var(--orange)">⚠️</span> 30年仅3次4连板, 前2次T+5后均大跌 (-18.6%/-20.7%)。今天首次5连板, 追高风险极大。
</div>
</div>""", "* 连板数据: 东方财富 / 新浪日线", "2")


# ═══════════════════════════════════════════
# P3 — 医药链四线 + 量化位置
# ═══════════════════════════════════════════
def page_3_html() -> str:
    return base_html("""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--red)">医药链深度</div></div>
<div class="subtitle">四条子线 · 全产业链资金共识</div>
<div class="subtitle-sm">化学制药 / 生物疫苗 / 医疗器械 / 医疗服务</div>
<div style="display:flex;flex-direction:column;gap:8px">
  <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div class="pill" style="background:var(--red);padding:5px 14px;min-width:100px;font-size:22px">化学制药</div>
    <div style="flex:1;font-size:22px">哈药5板 · 永安2板 · 板块涨幅+1.42%</div>
    <div style="text-align:right"><div style="font-size:20px;color:var(--muted)">涨停</div><div style="font-size:30px;font-weight:900;color:var(--red)">3只</div></div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div class="pill" style="background:var(--red);padding:5px 14px;min-width:100px;font-size:22px">生物疫苗</div>
    <div style="flex:1;font-size:22px">贤丰3板 · 概念+1.79% · 净流入-1.8亿</div>
    <div style="text-align:right"><div style="font-size:20px;color:var(--muted)">联动</div><div style="font-size:30px;font-weight:900;color:var(--red)">3只</div></div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div class="pill" style="background:var(--orange);padding:5px 14px;min-width:100px;font-size:22px">医疗器械</div>
    <div style="flex:1;font-size:22px">九安3板 +10.00% · 疫情记忆复苏</div>
    <div style="text-align:right"><div style="font-size:20px;color:var(--muted)">催化</div><div style="font-size:30px;font-weight:900;color:var(--orange)">3只</div></div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div class="pill" style="background:var(--orange);padding:5px 14px;min-width:100px;font-size:22px">医疗服务</div>
    <div style="flex:1;font-size:22px">南华2板 · 昭衍新药+8.49% · CRO</div>
    <div style="text-align:right"><div style="font-size:20px;color:var(--muted)">龙头</div><div style="font-size:30px;font-weight:900;color:var(--orange)">3只</div></div>
  </div>
</div>
<div class="hdr-c">哈药量化位置 · 技术形态极端</div>
<div class="card" style="padding:14px 12px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:20px;color:var(--muted)">距ATH</div>
      <div class="big-num" style="font-size:34px;color:var(--green);margin-top:4px">-61.8%</div>
      <div style="font-size:20px;color:var(--muted);margin-top:2px">2015年11.76元</div>
    </div>
    <div>
      <div style="font-size:20px;color:var(--muted)">52周位置</div>
      <div class="big-num" style="font-size:34px;color:var(--red);margin-top:4px">100%</div>
      <div style="font-size:20px;color:var(--muted);margin-top:2px">刷新新高</div>
    </div>
    <div>
      <div style="font-size:20px;color:var(--muted)">距MA20</div>
      <div class="big-num" style="font-size:34px;color:var(--orange);margin-top:4px">+38.3%</div>
      <div style="font-size:20px;color:var(--muted);margin-top:2px">严重偏离</div>
    </div>
    <div>
      <div style="font-size:20px;color:var(--muted)">量能倍数</div>
      <div class="big-num" style="font-size:34px;color:var(--red);margin-top:4px">3.61x</div>
      <div style="font-size:20px;color:var(--muted);margin-top:2px">巨量放大</div>
    </div>
  </div>
</div>
<div class="hdr-c">医药链主力资金 (今日流向)</div>
<div class="card" style="padding:12px 20px;font-size:22px;line-height:1.7">
  · 生物疫苗净流入 <b style="color:var(--green)">-1.8亿</b> — 涨停多 但主力尚未跟仓<br>
  · 医疗服务净流入 <b style="color:var(--green)">-0.3亿</b> — CRO脉冲式<br>
  · 化学制药净流入 <b style="color:var(--red)">+2.1亿</b> — 哈药单票撬动<br>
  · <b style="color:var(--orange)">结论:</b> 短线游资驱动为主, 机构资金尚未跟进
</div>
<div class="hl-cyan" style="text-align:center">
  <span style="font-weight:700;color:var(--cyan)">从原料药到CRO到终端, 全产业链被扫了一遍</span>
</div>
</div>""", "* 数据: 东方财富 / 新浪日线", "3")


# ═══════════════════════════════════════════
# P4 — 散户情绪 + 封板质量 + 雪球新晋
# ═══════════════════════════════════════════
def page_4_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--purple)">散户情绪 + 封板深度</div></div>
<div class="subtitle">医药股东财人气 · 封板质量</div>
<div class="hdr">东财人气榜医药股 TOP4</div>
<div class="card" style="padding:10px 20px">
  <div style="display:grid;grid-template-columns:60px 130px 1fr 100px 90px;gap:6px;font-size:20px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:6px">
    <div>排名</div><div>名称</div><div>涨幅</div><div>标签</div><div>代码</div>
  </div>
  <div style="display:grid;grid-template-columns:60px 130px 1fr 100px 90px;gap:6px;font-size:22px;padding:8px 0;border-bottom:1px solid var(--border)">
    <div style="font-weight:900;color:var(--orange)">#1</div><div style="font-weight:700">昭衍新药</div><div style="font-weight:700;color:var(--red)">+8.49%</div><div style="font-size:20px;color:var(--cyan)">CRO</div><div style="font-size:20px;color:var(--dim)">603127</div>
  </div>
  <div style="display:grid;grid-template-columns:60px 130px 1fr 100px 90px;gap:6px;font-size:22px;padding:8px 0;border-bottom:1px solid var(--border);background:linear-gradient(90deg,rgba(248,81,73,0.08),transparent)">
    <div style="font-weight:900;color:var(--red)">#2</div><div style="font-weight:700;color:var(--red)">哈药股份</div><div style="font-weight:700;color:var(--red)">+10.02%</div><div style="font-size:20px;color:var(--cyan)">5连板</div><div style="font-size:20px;color:var(--dim)">600664</div>
  </div>
  <div style="display:grid;grid-template-columns:60px 130px 1fr 100px 90px;gap:6px;font-size:22px;padding:8px 0;border-bottom:1px solid var(--border)">
    <div style="font-weight:900;color:var(--orange)">#8</div><div style="font-weight:700">海南海药</div><div style="font-weight:700;color:var(--red)">+10.10%</div><div style="font-size:20px;color:var(--cyan)">涨停</div><div style="font-size:20px;color:var(--dim)">000566</div>
  </div>
  <div style="display:grid;grid-template-columns:60px 130px 1fr 100px 90px;gap:6px;font-size:22px;padding:8px 0">
    <div style="font-weight:900;color:var(--orange)">#9</div><div style="font-weight:700">美诺华</div><div style="font-weight:700;color:var(--red)">+6.54%</div><div style="font-size:20px;color:var(--cyan)">原料药</div><div style="font-size:20px;color:var(--dim)">603538</div>
  </div>
</div>
<div class="hdr-c">封板质量 · 情绪温度</div>
<div class="card" style="padding:14px 20px">
  <div style="display:flex;align-items:center;gap:14px">
    <div style="font-size:22px;font-weight:700;color:var(--muted);min-width:80px">封板率</div>
    <div style="flex:1;height:24px;background:#3d444d;border-radius:12px;overflow:hidden">
      <div style="height:100%;width:{SEAL_RATE:.0f}%;background:linear-gradient(90deg,var(--red),#c93030);border-radius:12px"></div>
    </div>
    <div class="big-num" style="font-size:34px;color:var(--red)">{SEAL_RATE:.0f}%</div>
  </div>
  <div style="font-size:20px;color:var(--muted);text-align:center;margin-top:6px">{ZT_COUNT}封 / {ZT_COUNT+ZB_COUNT}总 · 突破警戒线80% → 情绪偏热, 短线易分化</div>
</div>
<div class="hdr">炸板 {ZB_COUNT}只 · 分行业</div>
<div class="card" style="padding:10px 20px;font-size:22px;line-height:1.7">
  · 香江控股 <span style="color:var(--muted)">房地产</span> <span style="color:var(--green)">炸1次</span> &nbsp;
  · 安迪苏 <span style="color:var(--muted)">化学制品</span> <span style="color:var(--green)">炸2次</span><br>
  · 电声股份 <span style="color:var(--muted)">广告营销</span> <span style="color:var(--green)">炸2次</span> &nbsp;
  · 紫光股份 <span style="color:var(--muted)">IT服务</span> <span style="color:var(--green)">炸2次</span><br>
  · 神州数码 <span style="color:var(--muted)">IT服务</span> <span style="color:var(--green)">炸1次</span> — IT服务连炸 → 科技追高受阻
</div>
<div class="hdr">雪球突然热起来的6只 (讨论榜 vs 长期关注榜差集)</div>
<div class="card" style="padding:10px 20px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:21px;line-height:1.6">
    <div>· <b style="color:var(--purple)">赛力斯</b> 7.2万</div>
    <div>· <b style="color:var(--purple)">寒武纪</b> 3.4万</div>
    <div>· <b style="color:var(--purple)">胜宏科技</b> 3.3万</div>
    <div>· <b style="color:var(--purple)">新易盛</b> 3.2万</div>
    <div>· <b style="color:var(--purple)">药明康德</b> 3.1万</div>
    <div>· <b style="color:var(--purple)">宁德时代</b> 2.9万</div>
  </div>
</div>
<div class="hl-cyan" style="text-align:center">
  <span style="font-weight:700;color:var(--cyan)">药明康德 3.1万讨论量入榜 → 医药热度已从游资蔓延到散户</span>
</div>
</div>""", "* 人气: 东财 / 雪球", "4")


# ═══════════════════════════════════════════
# P5 — 哈药30年史 + 10日K线 + 基本面
# ═══════════════════════════════════════════
def page_5_html() -> str:
    return base_html("""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--orange)">哈药30年连板史 + 近10日</div></div>
<div class="subtitle">30年零6连板 · 从4连板到5连板</div>
<div class="subtitle-sm">连板衰减: 1板72次 → 2板10次 → 3板6次 → 4板3次 → 5板1次</div>
<div style="display:flex;flex-direction:column;gap:8px">
  <div style="display:flex;gap:16px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div style="text-align:center;min-width:90px">
      <div style="font-size:20px;color:var(--muted)">1994-08</div>
      <div style="font-size:26px;font-weight:900;color:var(--muted)">4连板</div>
    </div>
    <div style="flex:1">
      <div style="font-size:22px;font-weight:700">连板期间暴涨68.6%</div>
      <div style="font-size:22px;color:var(--muted)">次日 -18.6% · T+5 +1.7%</div>
      <div style="font-size:20px;color:var(--dim)">早期A股, 涨跌幅限制不同</div>
    </div>
  </div>
  <div style="display:flex;gap:16px;padding:12px 18px;background:var(--card);border:1px solid var(--border);border-radius:10px">
    <div style="text-align:center;min-width:90px">
      <div style="font-size:20px;color:var(--muted)">2020-02</div>
      <div style="font-size:26px;font-weight:900;color:var(--green)">4连板</div>
    </div>
    <div style="flex:1">
      <div style="font-size:22px;font-weight:700">连板期间+33.2%</div>
      <div style="font-size:22px;color:var(--muted)">次日 +2.0% · T+5 <b style="color:var(--green)">-20.7%</b> (追高深埋)</div>
      <div style="font-size:20px;color:var(--dim)">疫情概念驱动</div>
    </div>
  </div>
  <div style="display:flex;gap:16px;padding:12px 18px;background:linear-gradient(135deg,var(--card) 0%,rgba(248,81,73,0.10) 100%);border:2px solid var(--red);border-radius:10px">
    <div style="text-align:center;min-width:90px">
      <div style="font-size:20px;color:var(--muted)">2026-07</div>
      <div style="font-size:26px;font-weight:900;color:var(--red)">5连板!</div>
    </div>
    <div style="flex:1">
      <div style="font-size:22px;font-weight:700;color:var(--red)">连板期间+45.3% · 进行中</div>
      <div style="font-size:22px;color:var(--muted)">历史首次 · 30年里程碑</div>
      <div style="font-size:20px;color:var(--gold);font-weight:700">连板接力还是历史性转折?</div>
    </div>
  </div>
</div>
<div class="hdr-c">近10日 K 线 (从 3.11 到 4.49)</div>
<div class="card" style="padding:10px 18px;font-size:22px;line-height:1.6">
  <div style="display:grid;grid-template-columns:100px 80px 100px 80px;gap:6px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:4px;font-size:20px">
    <div>日期</div><div>收盘</div><div>涨跌幅</div><div>成交</div>
  </div>
  <div style="display:grid;grid-template-columns:100px 80px 100px 80px;gap:6px;font-size:20px;color:var(--text2);line-height:1.5">
    <div>07-07</div><div>3.07</div><div style="color:var(--green)">-3.46%</div><div style="color:var(--dim)">4800万</div>
    <div>07-08</div><div>3.09</div><div style="color:var(--red)">+0.65%</div><div style="color:var(--dim)">3800万</div>
    <div>07-09</div><div>3.06</div><div style="color:var(--green)">-0.97%</div><div style="color:var(--dim)">3800万</div>
    <div>07-10</div><div>3.37</div><div style="color:var(--red);font-weight:700">+10.13%</div><div style="color:var(--orange)">1.0亿</div>
    <div>07-13</div><div>3.71</div><div style="color:var(--red);font-weight:700">+10.09%</div><div style="color:var(--orange)">2.0亿</div>
    <div>07-14</div><div>4.08</div><div style="color:var(--red);font-weight:700">+9.97%</div><div style="color:var(--red)">4.4亿</div>
    <div style="font-weight:700">07-15</div><div style="font-weight:700">4.49</div><div style="color:var(--red);font-weight:700">+10.05%</div><div style="color:var(--red)">1.1亿</div>
  </div>
</div>
<div class="hdr-c">当前基本面 · 4维度量化</div>
<div class="card" style="padding:12px 8px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;text-align:center">
    <div><div style="font-size:20px;color:var(--muted)">市值</div><div style="font-size:28px;font-weight:900;color:var(--text2)">~80亿</div></div>
    <div><div style="font-size:20px;color:var(--muted)">距ATH</div><div style="font-size:28px;font-weight:900;color:var(--green)">-61.8%</div></div>
    <div><div style="font-size:20px;color:var(--muted)">10日涨幅</div><div style="font-size:28px;font-weight:900;color:var(--red)">+45.3%</div></div>
    <div><div style="font-size:20px;color:var(--muted)">量能倍数</div><div style="font-size:28px;font-weight:900;color:var(--orange)">3.61x</div></div>
  </div>
</div>
<div class="hl">
  <span style="font-weight:700;color:var(--orange)">⚠️</span> 小市值+深跌反弹+首次5连板+距MA20 38% = 游资标准剧本 + 极端技术形态。追高性价比极差。
</div>
</div>""", "* 历史: 新浪日线 / akshare", "5")


# ═══════════════════════════════════════════
# P6 — 4段总结 + 明日剧本 + CTA
# ═══════════════════════════════════════════
def page_6_html() -> str:
    return base_html("""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--gold)">今日总结 + 明日剧本</div></div>
<div class="subtitle">四句话看懂今日医药链行情</div>
<div style="display:flex;align-items:flex-start;gap:16px">
  <div style="font-size:44px;font-weight:900;color:var(--red);min-width:56px;line-height:1">01</div>
  <div>
    <div style="font-size:24px;font-weight:700">30年首次 — 哈药 5 连板</div>
    <div style="font-size:22px;color:var(--muted);margin-top:4px">上市30年 (1993-06 至今) 最高纪录, 10日暴涨 45.3%, 距MA20 +38.3%, 量能 3.61倍。</div>
  </div>
</div>
<div style="height:1px;background:var(--border);margin:2px 0"></div>
<div style="display:flex;align-items:flex-start;gap:16px">
  <div style="font-size:44px;font-weight:900;color:var(--red);min-width:56px;line-height:1">02</div>
  <div>
    <div style="font-size:24px;font-weight:700">全产业链联动, 不是孤妖</div>
    <div style="font-size:22px;color:var(--muted);margin-top:4px">化学制药/生物疫苗/医疗器械/医疗服务齐涨, 9只医药股涨停, 昭衍/药明康德散户共振。</div>
  </div>
</div>
<div style="height:1px;background:var(--border);margin:2px 0"></div>
<div style="display:flex;align-items:flex-start;gap:16px">
  <div style="font-size:44px;font-weight:900;color:var(--orange);min-width:56px;line-height:1">03</div>
  <div>
    <div style="font-size:24px;font-weight:700">封板率83% 情绪偏热</div>
    <div style="font-size:22px;color:var(--muted);margin-top:4px">48涨停10炸板, 紫光/神州科技线连炸2次。互联网服务+2.08%净流入22.3亿, 新材料净流出65.5亿。</div>
  </div>
</div>
<div style="height:1px;background:var(--border);margin:2px 0"></div>
<div style="display:flex;align-items:flex-start;gap:16px">
  <div style="font-size:44px;font-weight:900;color:var(--purple);min-width:56px;line-height:1">04</div>
  <div>
    <div style="font-size:24px;font-weight:700">前车之鉴: 4连板后皆大跌</div>
    <div style="font-size:22px;color:var(--muted);margin-top:4px">1994次日-18.6%, 2020 T+5 -20.7%, 平均T+5亏损 -9.5%。5连板追高历史胜率 0%。</div>
  </div>
</div>
<div class="hdr-c">明日剧本 · 3种可能</div>
<div class="card" style="padding:12px 20px;font-size:22px;line-height:1.7">
  · <b style="color:var(--red)">A剧本 6连板 (30%)</b>: 30年历史无先例, 天量换手, 情绪彻底点燃<br>
  · <b style="color:var(--orange)">B剧本 断板高位 (50%)</b>: T字或大阴, 医药链其他票补涨接棒<br>
  · <b style="color:var(--green)">C剧本 断板杀跌 (20%)</b>: -10%~-20%, 复刻2020剧本
</div>
<div class="hl">
  <span style="font-weight:700;color:var(--orange)">散户友情提醒</span> 5连板后追高历史胜率 0%, 距MA20 38%极端偏离。看戏 &gt; 参与。
</div>
<div style="text-align:center;margin-top:4px">
  <div style="display:inline-block;padding:12px 28px;background:var(--card);border:1.5px solid var(--cyan);border-radius:12px;font-size:24px;font-weight:700;color:var(--cyan)">
    评论区聊聊 → 哈药明天是6连板还是断板?
  </div>
</div>
</div>""", "* 数据: 东方财富/雪球/新浪/akshare", "6")


PAGE_HTML_GENERATORS = [page_1_html, page_2_html, page_3_html, page_4_html, page_5_html, page_6_html]


def render_all():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1080, "height": 1440}, device_scale_factor=2, locale="zh-CN")
        page = ctx.new_page()
        for i, gen in enumerate(PAGE_HTML_GENERATORS, 1):
            out = OUT / f"page_{i}.png"
            page.set_content(gen(), wait_until="networkidle")
            page.wait_for_timeout(1800)
            page.screenshot(path=str(out), full_page=False)
            print(f"  ✓ {out.name} ({out.stat().st_size/1024:.0f}KB)")
        browser.close()


def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 7)]
    w, h = pages[0].size; tw, th = 470, 615
    canvas = Image.new("RGB", (tw * 3 + 20, th * 2 + 10), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, 3)
        canvas.paste(p.resize((tw, th)), (c * tw + 5 + c*5, r * th + 5 + r*5))
    canvas.save(OUT / "preview_2x3.png")
    total_h = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, total_h), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y)); y += p.height
    stacked.resize((720, int(total_h * 720 / w))).save(OUT / "all_pages_stacked.png")


def check_layout():
    from PIL import Image; import numpy as np
    BG = np.array([13, 17, 23])
    for pn in range(1, 7):
        arr = np.array(Image.open(OUT / f"page_{pn}.png"))[:, :, :3]
        h, w = arr.shape[:2]
        non_bg = (np.abs(arr.astype(int) - BG).sum(axis=2) > 30)
        rd = non_bg.sum(axis=1) / w
        den = non_bg.mean() * 100
        gaps = []; gs = -1; ig = 0
        for i, v in enumerate(rd):
            if v < 0.02:
                if not ig: ig = 1; gs = i
            else:
                if ig and i - gs > 200: gaps.append((gs, i, i - gs))
                ig = 0
        if ig == 1 and h - gs > 200: gaps.append((gs, h, h - gs))
        gap_str = " ".join(f"空白{g[2]}px" for g in gaps) if gaps else "无大空白"
        print(f"  P{pn}: 密度{den:.0f}% {gap_str}")


if __name__ == "__main__":
    print(f"HTML 6页深度卡片 → {OUT}")
    render_all(); make_preview(); check_layout()
    print("\n✅ 完成!")
