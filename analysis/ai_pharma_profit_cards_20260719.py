"""AI 制药盈利模式深度拆解 · 三家公司调研 — HTML+Playwright 小红书卡片.

8 页, 1080×1440, 暗色 GitHub 风. 数据基于 2025 年报 / 2026 Q1 财报 /
公开 BD 公告, 截至 2026-07-19. 数据来源: 公司财报 / HKEX / SEC / 公司公告.
"""
from __future__ import annotations
from pathlib import Path

DATE = "20260719"
DAY_HUM = "2026-07-19"
TOPIC = "ai_pharma_profit"
VERSION = "v1"
ROOT = Path("/workspace")
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_html_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">'

BASE_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg: #0d1117; --card: #161b22; --card2: #1c2129; --border: #30363d;
  --text: #e6edf3; --text2: #c9d1d9; --muted: #8b949e; --dim: #6e7681;
  --blue: #58a6ff; --green: #3fb950; --red: #f85149; --rose: #ff7b72;
  --orange: #d2991d; --gold: #f0c040; --cyan: #56d4dd; --purple: #bc8cff;
  --teal: #2dd4bf; --pink: #f778ba;
}
body {
  width: 1080px; height: 1440px;
  background: var(--bg);
  font-family: 'Noto Sans SC','Noto Sans CJK SC','Droid Sans Fallback',sans-serif;
  color: var(--text);
  overflow: hidden; position: relative;
  display: flex; flex-direction: column;
  padding: 30px 42px 20px;
  font-size: 22px;
}
body::before {
  content: ''; position: absolute; top: -300px; right: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(86,212,221,0.07) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body::after {
  content: ''; position: absolute; bottom: -400px; left: -300px;
  width: 900px; height: 900px;
  background: radial-gradient(circle, rgba(188,140,255,0.05) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}
body > * { position: relative; z-index: 1; }
.main { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.content-wrap { display: flex; flex-direction: column; gap: 10px; flex: 1; justify-content: space-between; }
.pill { display: inline-block; padding: 6px 22px; border-radius: 22px; font-size: 22px; font-weight: 700; color: var(--bg); text-align: center; }
.top-pill { display: flex; justify-content: center; }
.subtitle { text-align: center; font-size: 28px; font-weight: 700; color: var(--text); margin-top: 4px; }
.subtitle-sm { text-align: center; font-size: 19px; color: var(--muted); margin-top: 2px; font-style: italic; }
.footer { flex-shrink: 0; padding-top: 6px; display: flex; justify-content: space-between; font-size: 18px; color: var(--dim); border-top: 1px solid var(--border); }
.big-num { font-weight: 900; line-height: 1; letter-spacing: -1px; }
.mono { font-family: 'JetBrains Mono', monospace; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 18px; }
.card2 { background: var(--card2); border: 1px solid var(--border); border-radius: 12px; padding: 12px 18px; }
.glow-card { background: linear-gradient(135deg, var(--card) 0%, #1a1a1f 100%); border: 2px solid var(--cyan); border-radius: 14px; padding: 14px 20px; box-shadow: 0 0 24px rgba(86,212,221,0.12); }
.hl { padding: 8px 14px; background: linear-gradient(90deg,rgba(210,153,29,0.12),transparent); border-left: 3px solid var(--orange); border-radius: 4px; font-size: 21px; }
.hl-red { padding: 8px 14px; background: linear-gradient(90deg,rgba(248,81,73,0.12),transparent); border-left: 3px solid var(--red); border-radius: 4px; font-size: 21px; }
.hl-cyan { padding: 8px 14px; background: linear-gradient(90deg,rgba(86,212,221,0.12),transparent); border-left: 3px solid var(--cyan); border-radius: 4px; font-size: 21px; }
.hl-green { padding: 8px 14px; background: linear-gradient(90deg,rgba(63,185,80,0.12),transparent); border-left: 3px solid var(--green); border-radius: 4px; font-size: 21px; }
.hl-purple { padding: 8px 14px; background: linear-gradient(90deg,rgba(188,140,255,0.12),transparent); border-left: 3px solid var(--purple); border-radius: 4px; font-size: 21px; }
.hdr { font-size: 22px; font-weight: 700; color: var(--text); }
.hdr-c { font-size: 22px; font-weight: 700; color: var(--text); text-align: center; }
.tag { display: inline-block; padding: 2px 10px; border-radius: 6px; font-size: 18px; font-weight: 700; }
"""


def base_html(main: str, footer_left: str, page_num: str, total: str = "8") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8">{FONT_LINK}
<style>{BASE_CSS}</style></head>
<body>
<div class="main">{main}</div>
<div class="footer"><span>{footer_left}</span><span>{page_num}/{total}</span></div>
</body></html>"""


# ═══════════════════════════════════════════
# P1 — 封面 · AI 制药的"最优解"仍在路上
# ═══════════════════════════════════════════
def page_1_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--cyan)">{DAY_HUM} · 行业深度</div></div>
<div style="text-align:center;font-size:46px;font-weight:900;margin-top:14px;color:var(--text);letter-spacing:1px">AI 制药盈利模式 · 全景拆解</div>
<div style="text-align:center;margin-top:6px">
  <div class="big-num" style="font-size:96px;background:linear-gradient(180deg,#56d4dd,#58a6ff 60%,#bc8cff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 4px 14px rgba(86,212,221,0.25));line-height:1.05">200+ 管线</div>
  <div style="font-size:30px;font-weight:900;color:var(--gold);margin-top:4px">0 款 FDA 获批</div>
  <div style="font-size:21px;color:var(--muted);margin-top:4px">声量与验证脱节 · 谁真正赚到了钱?</div>
</div>
<div class="glow-card" style="padding:14px 12px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;text-align:center">
    <div>
      <div style="font-size:18px;color:var(--muted)">SaaS 龙头</div>
      <div class="big-num" style="font-size:34px;color:var(--cyan);margin-top:2px">Schrödinger</div>
      <div style="font-size:17px;color:var(--dim);margin-top:2px">软件收入 $2.0 亿 · 毛利 74%</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">港股新贵</div>
      <div class="big-num" style="font-size:34px;color:var(--purple);margin-top:2px">英矽智能</div>
      <div style="font-size:17px;color:var(--dim);margin-top:2px">礼来 BD $27.5 亿 · 毛利 84%</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">教训案例</div>
      <div class="big-num" style="font-size:34px;color:var(--rose);margin-top:2px">Recursion</div>
      <div style="font-size:17px;color:var(--dim);margin-top:2px">年亏 $6.45 亿 · CEO 离场</div>
    </div>
  </div>
</div>
<div class="card" style="padding:12px 18px">
  <div style="font-size:21px;font-weight:700;color:var(--cyan);margin-bottom:6px">// 行业拐点信号</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:20px;line-height:1.5">
    <div>
      <div style="color:var(--muted)">临床管线规模</div>
      <div class="big-num" style="font-size:30px;color:var(--blue)">200+ 个</div>
      <div style="font-size:17px;color:var(--dim)">94 个 P1 · 56 个 P2 · 15 个 P3</div>
    </div>
    <div>
      <div style="color:var(--muted)">AI 分子 P1 成功率</div>
      <div class="big-num" style="font-size:30px;color:var(--green)">80-90%</div>
      <div style="font-size:17px;color:var(--dim)">行业平均 ~52% · 显著领先</div>
    </div>
  </div>
</div>
<div class="card2" style="padding:10px 18px">
  <div style="font-size:21px;font-weight:700;color:var(--orange);margin-bottom:4px">// 4 种典型盈利模式</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:19px;line-height:1.5">
    <div>· <b style="color:var(--cyan)">SaaS / 软件授权</b> — 薛定谔、Isomorphic</div>
    <div>· <b style="color:var(--gold)">AI-CRO 服务</b> — 晶泰、Recursion</div>
    <div>· <b style="color:var(--purple)">自研管线 BD</b> — 英矽、Recursion</div>
    <div>· <b style="color:var(--teal)">联合开发</b> — Isomorphic × 礼来/诺华</div>
  </div>
</div>
<div class="hl-cyan" style="text-align:center">
  <span style="font-weight:700;color:var(--cyan)">谁离"临床数据"越近, 谁的商业价值越大</span>
  <span style="color:var(--muted);font-style:italic;margin-left:8px">翻页 → 4 模式横评 + 3 家深度</span>
</div>
</div>""", "* 数据: 公司财报 / HKEX / SEC / 公告", "1")


# ═══════════════════════════════════════════
# P2 — 行业现状 · GPT-2 时刻的悖论
# ═══════════════════════════════════════════
def page_2_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--purple)">行业现状 · GPT-2 时刻的悖论</div></div>
<div class="subtitle">声量爆炸 · 验证滞后 · 资本分化</div>
<div class="hdr">行业 5 大关键信号 · 声量与验证脱节</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:6px">
  <div class="card" style="text-align:center;padding:10px 6px">
    <div style="font-size:16px;color:var(--muted)">AI 衍生分子</div>
    <div class="big-num" style="font-size:28px;color:var(--cyan);margin-top:3px">200+</div>
    <div style="font-size:14px;color:var(--dim);margin-top:2px">临床阶段</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 6px">
    <div style="font-size:16px;color:var(--muted)">P1 临床</div>
    <div class="big-num" style="font-size:28px;color:var(--blue);margin-top:3px">94 个</div>
    <div style="font-size:14px;color:var(--dim);margin-top:2px">2026 初</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 6px">
    <div style="font-size:16px;color:var(--muted)">P2 临床</div>
    <div class="big-num" style="font-size:28px;color:var(--gold);margin-top:3px">56 个</div>
    <div style="font-size:14px;color:var(--dim);margin-top:2px">验证期</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 6px">
    <div style="font-size:16px;color:var(--muted)">P3 临床</div>
    <div class="big-num" style="font-size:28px;color:var(--orange);margin-top:3px">15 个</div>
    <div style="font-size:14px;color:var(--dim);margin-top:2px">冲刺期</div>
  </div>
  <div class="card" style="text-align:center;padding:10px 6px;border:1.5px solid var(--rose)">
    <div style="font-size:16px;color:var(--muted)">FDA 获批</div>
    <div class="big-num" style="font-size:28px;color:var(--rose);margin-top:3px">0 款</div>
    <div style="font-size:14px;color:var(--dim);margin-top:2px">最快 27-28</div>
  </div>
</div>
<div class="hdr-c">2 个标志性数据 · 矛盾的现实</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">// AI P1 成功率</div>
    <div style="display:flex;align-items:baseline;gap:10px;margin-top:4px">
      <div class="big-num" style="font-size:36px;color:var(--green)">80-90%</div>
      <div style="font-size:18px;color:var(--muted)">vs 行业 ~52%</div>
    </div>
    <div style="font-size:16px;color:var(--dim);margin-top:2px">早期信号显著领先 · 但仍需 P2/P3 验证</div>
  </div>
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--orange);font-weight:700">// MNC 专利悬崖</div>
    <div style="display:flex;align-items:baseline;gap:10px;margin-top:4px">
      <div class="big-num" style="font-size:36px;color:var(--rose)">$1150 亿</div>
      <div style="font-size:18px;color:var(--muted)">2035 前损失</div>
    </div>
    <div style="font-size:16px;color:var(--dim);margin-top:2px">倒逼 MNC 转向 AI · 大额 BD 涌现</div>
  </div>
</div>
<div class="hdr-c">三种典型发展路径 · 谁的进度更靠前</div>
<div class="card" style="padding:10px 18px">
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:18px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:5px">
    <div>阶段</div><div style="color:var(--cyan)">英矽智能</div><div style="color:var(--blue)">薛定谔</div><div style="color:var(--rose)">Recursion</div>
  </div>
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:20px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">IIa 临床数据</div><div style="color:var(--green);font-weight:700">✓ Nature Med</div><div style="color:var(--dim)">—</div><div style="color:var(--rose);font-weight:700">✗ 失败</div>
  </div>
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:20px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">单笔 BD 最大</div><div style="color:var(--purple);font-weight:700">$27.5 亿</div><div style="color:var(--gold);font-weight:700">~$1.5 亿</div><div style="color:var(--blue);font-weight:700">$120 亿*</div>
  </div>
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:20px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">2025 收入</div><div style="color:var(--text2)">$5624 万</div><div style="color:var(--cyan);font-weight:700">$2.56 亿</div><div style="color:var(--text2)">$7470 万</div>
  </div>
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:20px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">毛利率</div><div style="color:var(--green);font-weight:700">83.8%</div><div style="color:var(--green);font-weight:700">74%</div><div style="color:var(--orange)">波动大</div>
  </div>
  <div style="display:grid;grid-template-columns:130px 1fr 1fr 1fr;gap:6px;font-size:20px;padding:5px 0;background:linear-gradient(90deg,rgba(210,153,29,0.10),transparent);border-radius:4px">
    <div style="color:var(--muted)">2025 净利</div><div style="color:var(--rose)">-$3.5 亿</div><div style="color:var(--rose)">-$1.0 亿</div><div style="color:var(--rose);font-weight:700">-$6.45 亿</div>
  </div>
</div>
<div style="font-size:18px;color:var(--dim);text-align:center;font-style:italic">* 含潜在里程碑款 · 数据口径见末页</div>
<div class="hl">
  <span style="font-weight:700;color:var(--orange)">⚠️</span> 所有头部 AI 制药公司都还在等待第一次监管批准 · 第一款 AI 发现药物获批最快要 2027-2028 年。
</div>
</div>""", "* 数据: 各公司 2025 年报 / HKEX / SEC 10-K", "2")


# ═══════════════════════════════════════════
# P3 — 四种盈利模式横评
# ═══════════════════════════════════════════
def page_3_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--cyan)">4 种盈利模式横评</div></div>
<div class="subtitle">现金流 · 天花板 · 风险结构对比</div>
<div style="display:flex;flex-direction:column;gap:6px">
  <div class="card" style="border-left:4px solid var(--cyan);padding:10px 16px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:22px;font-weight:700;color:var(--cyan)">模式一 · SaaS / 软件授权</div>
        <div style="font-size:18px;color:var(--muted);margin-top:2px">薛定谔 · Isomorphic Labs — 平台 license + 订阅</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:16px;color:var(--muted)">毛利率</div>
        <div class="big-num" style="font-size:30px;color:var(--green)">74-80%</div>
      </div>
    </div>
    <div style="font-size:18px;line-height:1.5;color:var(--text2);margin-top:4px">
      <b style="color:var(--green)">+ 现金流最稳 · 续签率近 100% · 不依赖管线进展</b><br>
      <b style="color:var(--rose)">- 收入天花板低 · 药企软件预算有限 · 增速持续放缓</b>
    </div>
  </div>
  <div class="card" style="border-left:4px solid var(--gold);padding:10px 16px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:22px;font-weight:700;color:var(--gold)">模式二 · AI-CRO 服务</div>
        <div style="font-size:18px;color:var(--muted);margin-top:2px">晶泰科技 · Recursion — 项目制外包</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:16px;color:var(--muted)">回款周期</div>
        <div class="big-num" style="font-size:28px;color:var(--orange)">中</div>
      </div>
    </div>
    <div style="font-size:18px;line-height:1.5;color:var(--text2);margin-top:4px">
      <b style="color:var(--green)">+ 收入可验证 · 来源相对稳定 · 客户覆盖广</b><br>
      <b style="color:var(--rose)">- 难以靠堆人头突破规模 · 项目制波动大</b>
    </div>
  </div>
  <div class="card" style="border-left:4px solid var(--purple);padding:10px 16px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:22px;font-weight:700;color:var(--purple)">模式三 · 自研管线 BD</div>
        <div style="font-size:18px;color:var(--muted);margin-top:2px">英矽 · Recursion · Generate — 授权换现金</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:16px;color:var(--muted)">单笔弹性</div>
        <div class="big-num" style="font-size:28px;color:var(--green)">数十亿$</div>
      </div>
    </div>
    <div style="font-size:18px;line-height:1.5;color:var(--text2);margin-top:4px">
      <b style="color:var(--green)">+ 弹性极高 · 一笔交易顶 SaaS 十年收入</b><br>
      <b style="color:var(--rose)">- 周期长 · 十年级 · 不确定性极大</b>
    </div>
  </div>
  <div class="card" style="border-left:4px solid var(--teal);padding:10px 16px">
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:22px;font-weight:700;color:var(--teal)">模式四 · 联合开发 (Co-dev)</div>
        <div style="font-size:18px;color:var(--muted);margin-top:2px">Isomorphic × 礼来/诺华 — 共担共享</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:16px;color:var(--muted)">结构</div>
        <div class="big-num" style="font-size:24px;color:var(--teal)">首付+里程+销售</div>
      </div>
    </div>
    <div style="font-size:18px;line-height:1.5;color:var(--text2);margin-top:4px">
      <b style="color:var(--green)">+ 风险共担 · 借力 MNC 商业化渠道 · 行业主流</b><br>
      <b style="color:var(--rose)">- 失败率高 · 管线终止则里程碑归零</b>
    </div>
  </div>
</div>
<div class="hdr-c">3 种模式的"变形记" · 都在向临床数据靠拢</div>
<div class="card2" style="padding:10px 18px;font-size:19px;line-height:1.55">
  · <b style="color:var(--cyan)">SaaS → 寻找管线出口</b>: 薛定谔放弃 Phase 1 后独立临床, 转向合作开发<br>
  · <b style="color:var(--gold)">CRO → 想做管线</b>: 晶泰用服务现金流反哺自研 · Recursion 直接双线作战<br>
  · <b style="color:var(--purple)">管线 BD → 想稳定现金流</b>: 英矽同时做 software solution · Recursion 增 SaaS 订阅
</div>
<div class="hl-cyan">
  <span style="font-weight:700;color:var(--cyan)">软件的天花板有限 · 临床的地平线无垠</span> — 每种模式都在向"临床数据"靠拢
</div>
</div>""", "* 模式分类参考: 新财富 / Sciencenet 行业研报", "3")


# ═══════════════════════════════════════════
# P4 — Schrödinger 深度 (SaaS 龙头)
# ═══════════════════════════════════════════
def page_4_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--cyan)">公司 #1 · Schrödinger (SDGR)</div></div>
<div class="subtitle">SaaS 模式代表 · 唯一现金流为正的玩家</div>
<div class="glow-card" style="padding:12px 14px;border-color:var(--cyan)">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:17px;color:var(--muted)">2025 总收入</div>
      <div class="big-num" style="font-size:32px;color:var(--cyan);margin-top:2px">$2.56 亿</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">+23.3% YoY</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">软件收入</div>
      <div class="big-num" style="font-size:32px;color:var(--cyan);margin-top:2px">$2.00 亿</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">+10.6% YoY</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">软件毛利率</div>
      <div class="big-num" style="font-size:32px;color:var(--green);margin-top:2px">74%</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">Q4 单季 81%</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">净亏损</div>
      <div class="big-num" style="font-size:32px;color:var(--rose);margin-top:2px">-$1.03 亿</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">同比收窄 45%</div>
    </div>
  </div>
</div>
<div class="hdr">核心护城河 · Top 20 Pharma 全覆盖</div>
<div class="card" style="padding:10px 18px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center">
    <div>
      <div style="font-size:18px;color:var(--muted)">Top 20 Pharma ACV</div>
      <div class="big-num" style="font-size:28px;color:var(--cyan)">$80.8M</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">+15.3% YoY</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">大客户续签率</div>
      <div class="big-num" style="font-size:28px;color:var(--green)">100%</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">连续 2 年保持</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">单客户 ACV (>$1M)</div>
      <div class="big-num" style="font-size:28px;color:var(--gold)">$3.9M</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">+16.3% YoY</div>
    </div>
  </div>
</div>
<div class="hdr-c">战略大转向 · 从 Biotech 退回 SaaS</div>
<div class="card2" style="padding:10px 18px;font-size:20px;line-height:1.55">
  · <b style="color:var(--orange)">2025-05 决策</b>: 放弃 SGR-1505 / SGR-3515 Phase 1 后独立临床, 转合作<br>
  · <b style="color:var(--orange)">裁员 7%</b>: 年省 ~$7000 万, 现金延长到 2028 调整后 EBITDA 转正<br>
  · <b style="color:var(--cyan)">商业模式再定位</b>: "药物发现收入是<span style="color:var(--gold);font-weight:700">价值验证器</span>, 而非价值驱动器"<br>
  · <b style="color:var(--cyan)">2026 Q1 ACV +12%</b>: $28.4M · 加速转向 hosted 软件订阅模式<br>
  · <b style="color:var(--purple)">今夏发布 Bunsen</b>: agentic AI co-scientist 自主执行分子发现工作流
</div>
<div class="hdr-c">最大彩蛋 · 礼来 23 亿美元收购 Ajax</div>
<div class="hl-green" style="font-size:20px;line-height:1.5">
  <b style="color:var(--green)">2026-05</b> 礼来宣布 $23 亿收购 Ajax Therapeutics, Schrödinger 持股约 6% → 数亿美元浮盈。再次验证平台分子设计能力 → MNC 用真金白银买单。
</div>
<div class="hl">
  <span style="font-weight:700;color:var(--orange)">⚠️ 风险</span>: 软件增速连续 5 年放缓 · 市场不给管线估值 · PS 仅 4.3 倍
</div>
</div>""", "* 数据: SDGR 2025 10-K / 2026 Q1 财报", "4")


# ═══════════════════════════════════════════
# P5 — 英矽智能深度 (港股新贵)
# ═══════════════════════════════════════════
def page_5_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--purple)">公司 #2 · 英矽智能 (3696.HK)</div></div>
<div class="subtitle">自研管线 BD 代表 · 行业临床兑现最接近者</div>
<div class="glow-card" style="padding:12px 14px;border-color:var(--purple)">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:17px;color:var(--muted)">2025 收入</div>
      <div class="big-num" style="font-size:30px;color:var(--purple);margin-top:2px">$5624 万</div>
      <div style="font-size:16px;color:var(--rose);margin-top:2px">-35% YoY</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">毛利率</div>
      <div class="big-num" style="font-size:30px;color:var(--green);margin-top:2px">83.8%</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">业内最高</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">累计 PCC</div>
      <div class="big-num" style="font-size:30px;color:var(--cyan);margin-top:2px">28 个</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">2025 新增 6 个</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">现金储备</div>
      <div class="big-num" style="font-size:30px;color:var(--gold);margin-top:2px">$3.93 亿</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">+IPO 募资</div>
    </div>
  </div>
</div>
<div class="hdr">里程碑 · 行业多个"第一"</div>
<div class="card2" style="padding:10px 18px;font-size:20px;line-height:1.55">
  · <b style="color:var(--green)">2025-06</b>: Rentosertib (ISM001-055) IIa 期数据登 <b style="color:var(--cyan)">Nature Medicine</b><br>
  · <b style="color:var(--cyan)">行业首例</b>: AI 全流程 (靶点→分子) 设计药物走到 II 期且数据阳性<br>
  · <b style="color:var(--purple)">18 个月</b>: 从靶点发现到 PCC · 行业平均 2-3 年<br>
  · <b style="color:var(--gold)">2025-12-30 港股 IPO</b>: 募资 22.77 亿港元 · 超额认购 <b style="color:var(--cyan)">1427 倍</b><br>
  · <b style="color:var(--purple)">15 家基石投资者</b>: 礼来 / 腾讯 / 淡马锡 / 瑞银 AM / 橡树资本 等
</div>
<div class="hdr-c">2026-03 礼来 $27.5 亿合作 · 行业最大单笔 BD</div>
<div class="card" style="padding:12px 18px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:18px;color:var(--muted)">首付款</div>
      <div class="big-num" style="font-size:32px;color:var(--green)">$1.15 亿</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">已锁定</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">潜在总金额</div>
      <div class="big-num" style="font-size:32px;color:var(--purple)">$27.5 亿</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">含里程碑+销售分成</div>
    </div>
    <div>
      <div style="font-size:18px;color:var(--muted)">累计 BD 总额</div>
      <div class="big-num" style="font-size:32px;color:var(--cyan)">$46 亿+</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">2021 以来合作</div>
    </div>
  </div>
</div>
<div class="hdr-c">Pharma.AI 平台 · 端到端生成式 AI</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
  <div class="card" style="padding:8px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">PandaOmics</div>
    <div style="font-size:17px;color:var(--muted);margin-top:2px">靶点发现 · 4 项新评分指标</div>
  </div>
  <div class="card" style="padding:8px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">Chemistry42</div>
    <div style="font-size:17px;color:var(--muted);margin-top:2px">分子生成 · GAN + 物理预测</div>
  </div>
  <div class="card" style="padding:8px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">Medicine42</div>
    <div style="font-size:17px;color:var(--muted);margin-top:2px">inClinico · 临床 Digital Twin</div>
  </div>
  <div class="card" style="padding:8px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">MMAI Gym</div>
    <div style="font-size:17px;color:var(--muted);margin-top:2px">靶点成功率 20% → 70%</div>
  </div>
</div>
<div class="hl-purple">
  <span style="font-weight:700;color:var(--purple)">关键看点</span>: Rentosertib IIb 期能否持续兑现 · 决定 AI 制药行业级叙事走向
</div>
</div>""", "* 数据: 英矽智能 2025 年报 / HKEX 公告 / 公司公告", "5")


# ═══════════════════════════════════════════
# P6 — Recursion 深度 (教训与转型)
# ═══════════════════════════════════════════
def page_6_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--rose)">公司 #3 · Recursion (RXRX)</div></div>
<div class="subtitle">混合模式代表 · 教训案例 · 抱团取暖</div>
<div class="glow-card" style="padding:12px 14px;border-color:var(--rose)">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:17px;color:var(--muted)">2025 收入</div>
      <div class="big-num" style="font-size:30px;color:var(--text2);margin-top:2px">$7470 万</div>
      <div style="font-size:16px;color:var(--green);margin-top:2px">+27% YoY</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">净亏损</div>
      <div class="big-num" style="font-size:30px;color:var(--rose);margin-top:2px">-$6.45 亿</div>
      <div style="font-size:16px;color:var(--rose);margin-top:2px">创纪录</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">现金储备</div>
      <div class="big-num" style="font-size:30px;color:var(--gold);margin-top:2px">$7.54 亿</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">支撑到 2028 初</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">Q1 2026 收入</div>
      <div class="big-num" style="font-size:30px;color:var(--rose);margin-top:2px">$650 万</div>
      <div style="font-size:16px;color:var(--rose);margin-top:2px">-56% YoY</div>
    </div>
  </div>
</div>
<div class="hdr">三重收入模式 · 资本已分化</div>
<div class="card2" style="padding:10px 18px;font-size:19px;line-height:1.55">
  · <b style="color:var(--cyan)">短期 · 战略合作</b>: 罗氏/赛诺菲/拜耳, 累计 $5 亿+ 预付+里程款<br>
  · <b style="color:var(--gold)">中期 · 平台订阅 SaaS</b>: 2025 启动 · 目标 2028 占比 20%<br>
  · <b style="color:var(--purple)">长期 · 自研管线商业化</b>: 2028 首药上市 · 长期净利率目标 30%+
</div>
<div class="hdr-c">戏剧性事件 · 12 年一梦</div>
<div class="card" style="padding:10px 18px;font-size:19px;line-height:1.55">
  <div style="display:grid;grid-template-columns:130px 1fr;gap:6px">
    <div style="color:var(--rose);font-weight:700">2024-08</div><div>与 Exscientia 合并 ($6.88 亿) · 12 年老牌玩家消失</div>
    <div style="color:var(--rose);font-weight:700">2025 Q1</div><div>裁撤 1/3 临床管线 · REC-994 / REC-2282 II 期失败终止</div>
    <div style="color:var(--rose);font-weight:700">2025-02</div><div>创始人 CEO <b>Chris Gibson 离场</b> · 英伟达 Q4 清仓 (曾持 4%)</div>
    <div style="color:var(--green);font-weight:700">2025</div><div><b>ARK 基金逆势加仓</b> · 持仓 3730 万股 · 价值 ~$1.37 亿</div>
    <div style="color:var(--cyan);font-weight:700">2026-05</div><div>Q1 2026 收入 $650 万 · 但 REC-4881 II 期出现疗效信号 · 与 FDA 沟通注册路径</div>
  </div>
</div>
<div class="hdr-c">数据壁垒 · 50 PB 专有数据 + 超算</div>
<div class="card" style="padding:10px 18px">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;text-align:center">
    <div>
      <div style="font-size:17px;color:var(--muted)">专有数据集</div>
      <div class="big-num" style="font-size:30px;color:var(--purple)">50 PB</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">多模态生物数据</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">超级计算机</div>
      <div class="big-num" style="font-size:24px;color:var(--cyan)">BioHive-2</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">63 × DGX H100</div>
    </div>
    <div>
      <div style="font-size:17px;color:var(--muted)">合作潜在总金额</div>
      <div class="big-num" style="font-size:30px;color:var(--blue)">$172 亿</div>
      <div style="font-size:16px;color:var(--dim);margin-top:2px">罗氏 120 + 赛诺菲 52</div>
    </div>
  </div>
</div>
<div class="hl-red">
  <span style="font-weight:700;color:var(--rose)">⚠️ 关键风险</span>: 2025 净亏 $6.45 亿 · 创始人离场 · 临床接连失败 · 估值靠"信仰溢价"
</div>
<div class="hl-cyan">
  <span style="font-weight:700;color:var(--cyan)">反向信号</span>: 现金撑到 2028 · ARK 逆势加仓 · REC-4881 II 期出现疗效信号
</div>
</div>""", "* 数据: Recursion 2025 年报 / 13F / 公司公告", "6")


# ═══════════════════════════════════════════
# P7 — 三家横向对比 + 关键洞察
# ═══════════════════════════════════════════
def page_7_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--gold)">3 家横向对比 · 谁离临床最近</div></div>
<div class="subtitle">同行业 · 不同命运 · 6 维度量化对比</div>
<div class="card" style="padding:10px 16px">
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:18px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:5px">
    <div>指标</div><div style="color:var(--cyan)">Schrödinger</div><div style="color:var(--purple)">英矽智能</div><div style="color:var(--rose)">Recursion</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">商业模式</div><div>SaaS + Drug Disc.</div><div>管线 BD + Software</div><div>CRO + 管线 + SaaS</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">2025 收入</div><div style="color:var(--green);font-weight:700">$2.56 亿</div><div>$5624 万</div><div>$7470 万</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">2025 净亏</div><div style="color:var(--green)">-$1.03 亿</div><div>-$3.52 亿</div><div style="color:var(--rose);font-weight:700">-$6.45 亿</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">毛利率</div><div style="color:var(--green)">74%</div><div style="color:var(--green);font-weight:700">83.8%</div><div style="color:var(--orange)">波动大</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">现金储备</div><div>$4.02 亿</div><div>$3.93 亿</div><div style="color:var(--green);font-weight:700">$7.54 亿</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">单笔 BD 最大</div><div style="color:var(--gold)">~$1.5 亿</div><div style="color:var(--purple);font-weight:700">$27.5 亿</div><div style="color:var(--blue)">$120 亿*</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;border-bottom:1px solid var(--border)">
    <div style="color:var(--muted)">临床最进度</div><div style="color:var(--orange)">合作 P3 (TAK-279)</div><div style="color:var(--green);font-weight:700">IIa 数据阳性</div><div style="color:var(--rose)">P1 / P2 失败</div>
  </div>
  <div style="display:grid;grid-template-columns:140px 1fr 1fr 1fr;gap:6px;font-size:19px;padding:5px 0;background:linear-gradient(90deg,rgba(210,153,29,0.10),transparent);border-radius:4px">
    <div style="color:var(--muted)">市值</div><div>~$12 亿</div><div style="color:var(--purple);font-weight:700">~$33 亿</div><div style="color:var(--rose);font-weight:700">~$19 亿</div>
  </div>
</div>
<div style="font-size:17px;color:var(--dim);text-align:center;font-style:italic">* Recursion $120 亿为罗氏合作潜在总额 · 含全部里程碑 · 实际首付款较低</div>
<div class="hdr-c">关键洞察 · 4 条核心结论</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--cyan);font-weight:700">// 01 估值逻辑分裂</div>
    <div style="font-size:17px;color:var(--text2);margin-top:4px;line-height:1.45">薛定谔 PS 4.3 倍 (SaaS 估值) · Recursion PS 267 倍 (信仰溢价) · 同行业用 6 种不同估值逻辑</div>
  </div>
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--purple);font-weight:700">// 02 临床数据 = 估值锚</div>
    <div style="font-size:17px;color:var(--text2);margin-top:4px;line-height:1.45">英矽 IIa 数据登 Nature Medicine → 港股 IPO 超额认购 1427 倍 · 临床数据是商业价值硬通货</div>
  </div>
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--orange);font-weight:700">// 03 BD 弹性远超 SaaS</div>
    <div style="font-size:17px;color:var(--text2);margin-top:4px;line-height:1.45">英矽单笔 $27.5 亿 = 薛定谔 10 年软件收入总和 · 管线 BD 天花板远高于 SaaS</div>
  </div>
  <div class="card2" style="padding:10px 14px">
    <div style="font-size:18px;color:var(--rose);font-weight:700">// 04 现金流决定生死</div>
    <div style="font-size:17px;color:var(--text2);margin-top:4px;line-height:1.45">薛定谔靠 SaaS 活下来 · Recursion 靠 BD 续命到 2028 · 现金 runway 比 GPU 更稀缺</div>
  </div>
</div>
<div class="hl-cyan">
  <span style="font-weight:700;color:var(--cyan)">同一行业 · 6 种估值逻辑 · 谁能跑通临床验证, 谁就能定义下一个时代</span>
</div>
</div>""", "* 数据: 各公司 2025 年报 / 市值截至 2026 Q2", "7")


# ═══════════════════════════════════════════
# P8 — 投资启示 + 风险提示 + 结语
# ═══════════════════════════════════════════
def page_8_html() -> str:
    return base_html(f"""<div class="content-wrap">
<div class="top-pill"><div class="pill" style="background:var(--gold)">投资启示 + 风险提示</div></div>
<div class="subtitle">AI 制药仍在 "GPT-2 时刻" · 长期信仰 + 短期谨慎</div>
<div class="hdr">3 大投资启示</div>
<div style="display:flex;flex-direction:column;gap:6px">
  <div class="card" style="border-left:4px solid var(--cyan);padding:10px 16px">
    <div style="display:flex;gap:12px;align-items:flex-start">
      <div style="font-size:32px;font-weight:900;color:var(--cyan);min-width:42px;line-height:1">01</div>
      <div>
        <div style="font-size:21px;font-weight:700">看临床节点, 不看 PPT 叙事</div>
        <div style="font-size:18px;color:var(--muted);margin-top:3px;line-height:1.45">英矽 Rentosertib IIa 数据登 Nature Medicine 比任何融资新闻都重要。下一个关键节点: IIb / III 期 + 2027-2028 首款 AI 药获批。</div>
      </div>
    </div>
  </div>
  <div class="card" style="border-left:4px solid var(--purple);padding:10px 16px">
    <div style="display:flex;gap:12px;align-items:flex-start">
      <div style="font-size:32px;font-weight:900;color:var(--purple);min-width:42px;line-height:1">02</div>
      <div>
        <div style="font-size:21px;font-weight:700">分散押注 4 种商业模式</div>
        <div style="font-size:18px;color:var(--muted);margin-top:3px;line-height:1.45">SaaS (现金流稳) + CRO (收入可验证) + 管线 BD (弹性高) + 联合开发 (MNC 背书)。每种模式都有独特的风险结构, 不应单一押注。</div>
      </div>
    </div>
  </div>
  <div class="card" style="border-left:4px solid var(--orange);padding:10px 16px">
    <div style="display:flex;gap:12px;align-items:flex-start">
      <div style="font-size:32px;font-weight:900;color:var(--orange);min-width:42px;line-height:1">03</div>
      <div>
        <div style="font-size:21px;font-weight:700">关注现金跑道 & BD 兑现节奏</div>
        <div style="font-size:18px;color:var(--muted);margin-top:3px;line-height:1.45">薛定谔 2028 EBITDA 转正 · 英矽礼来首付 $1.15 亿已锁定 · Recursion 撑到 2028 初。在 0 获批时代, 现金流是活下来的硬指标。</div>
      </div>
    </div>
  </div>
</div>
<div class="hdr-c">4 大风险提示</div>
<div class="card2" style="padding:10px 18px;font-size:19px;line-height:1.55">
  · <b style="color:var(--rose)">临床失败</b>: Recursion REC-994 / REC-2282 已失败 · 临床数据是双刃剑<br>
  · <b style="color:var(--rose)">资本周期</b>: 2024-2025 行业融资寒冬 · 头部公司股价较巅峰跌 90%<br>
  · <b style="color:var(--rose)">估值锚缺失</b>: 0 获批 → 无可参照商业化路径 · 全靠"信仰溢价"<br>
  · <b style="color:var(--rose)">大股东分歧</b>: 英伟达清仓 Recursion · ARK 逆势加仓 · 资本对战激烈
</div>
<div class="hdr-c">未来 18 个月关键节点</div>
<div class="card" style="padding:10px 18px;font-size:19px;line-height:1.55">
  · <b style="color:var(--cyan)">2026 H2</b>: Recursion REC-4881 与 FDA 沟通注册路径 · 薛定谔发布 Bunsen AI agent<br>
  · <b style="color:var(--purple)">2026-2027</b>: 英矽 Rentosertib 启动 IIb / III 期 · 多个 PCC 对外授权<br>
  · <b style="color:var(--gold)">2027-2028</b>: 行业首款 AI 发现药物有望 FDA 获批 · 决定行业叙事走向<br>
  · <b style="color:var(--green)">2028</b>: 薛定谔调整后 EBITDA 转正 · 行业首批公司开始盈利验证
</div>
<div class="hl">
  <span style="font-weight:700;color:var(--gold)">核心结论</span>: 谁离"临床数据"越近, 谁的商业价值越大。AI 制药不是伪命题, 但也早已不是单一叙事 — 是 4 种模式 + 6 种估值逻辑 + 0 款获批的现实战场。
</div>
<div style="text-align:center;font-size:18px;color:var(--dim);font-style:italic;margin-top:2px">
  非投资建议 · 仅供参考 · 数据截至 2026-07-19
</div>
</div>""", "* 调研: 公司财报 / HKEX / SEC / 公开 BD 公告", "8")


PAGE_HTML_GENERATORS = [
    page_1_html, page_2_html, page_3_html, page_4_html,
    page_5_html, page_6_html, page_7_html, page_8_html,
]


def render_all():
    """渲染所有 8 页 HTML → PNG."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1080, "height": 1440},
            device_scale_factor=2, locale="zh-CN"
        )
        page = ctx.new_page()
        for i, gen in enumerate(PAGE_HTML_GENERATORS, 1):
            html = gen()
            # 同时保存 HTML 便于浏览器查看
            (OUT / f"page_{i}.html").write_text(html, encoding="utf-8")
            page.set_content(html, wait_until="networkidle")
            page.wait_for_timeout(1800)
            out_png = OUT / f"page_{i}.png"
            page.screenshot(path=str(out_png), full_page=False)
            print(f"  ✓ page_{i}.png ({out_png.stat().st_size/1024:.0f}KB)")
        browser.close()


def make_preview():
    """生成预览图: 4×2 网格 + 8 页竖排."""
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i}.png") for i in range(1, 9)]
    w, h = pages[0].size
    # 4×2 网格预览
    tw, th = 480, 640
    canvas = Image.new("RGB", (tw * 4 + 30, th * 2 + 20), color=(13, 17, 23))
    for i, p in enumerate(pages):
        r, c = divmod(i, 4)
        canvas.paste(p.resize((tw, th)), (c * tw + 5 + c * 5, r * th + 5 + r * 5))
    canvas.save(OUT / "preview_4x2.png")
    # 8 页竖排预览
    total_h = sum(p.height for p in pages)
    stacked = Image.new("RGB", (w, total_h), color=(13, 17, 23))
    y = 0
    for p in pages:
        stacked.paste(p, (0, y))
        y += p.height
    stacked.resize((720, int(total_h * 720 / w))).save(OUT / "all_pages_stacked.png")


def check_layout():
    """检测每页留白情况."""
    from PIL import Image
    import numpy as np
    BG = np.array([13, 17, 23])
    for pn in range(1, 9):
        arr = np.array(Image.open(OUT / f"page_{pn}.png"))[:, :, :3]
        h, w = arr.shape[:2]
        non_bg = (np.abs(arr.astype(int) - BG).sum(axis=2) > 30)
        rd = non_bg.sum(axis=1) / w
        den = non_bg.mean() * 100
        gaps = []
        gs = -1
        ig = 0
        for i, v in enumerate(rd):
            if v < 0.02:
                if not ig:
                    ig = 1
                    gs = i
            else:
                if ig and i - gs > 200:
                    gaps.append((gs, i, i - gs))
                ig = 0
        if ig == 1 and h - gs > 200:
            gaps.append((gs, h, h - gs))
        gap_str = " ".join(f"空白{g[2]}px" for g in gaps) if gaps else "无大空白"
        print(f"  P{pn}: 密度{den:.0f}% {gap_str}")


if __name__ == "__main__":
    print(f"AI 制药盈利模式 8 页深度卡片 → {OUT}")
    render_all()
    make_preview()
    print("\n--- 布局检查 ---")
    check_layout()
    print("\n✅ 完成!")
    print(f"📁 PNG 文件: {OUT}")
    print(f"🖼  预览图: {OUT / 'preview_4x2.png'}")
    print(f"📜 竖排图: {OUT / 'all_pages_stacked.png'}")
