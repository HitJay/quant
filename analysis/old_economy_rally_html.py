"""老登股反攻：白酒/医药/保险核心资产修复 - HTML卡片与深度研报。

输出目录：output/2026-06-22/old-economy-rally-html/
卡片路线：HTML/CSS -> Chromium screenshot -> PNG。
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

sys.path.insert(0, "src")

try:
    from quant.data.hotspot_fetcher import HotspotFetcher
except Exception:  # pragma: no cover
    HotspotFetcher = None  # type: ignore


DATE_DIR = "2026-06-22"
ROOT = Path(f"output/{DATE_DIR}/old-economy-rally-html")
HTML_DIR = ROOT / "cards_html"
CARDS_DIR = ROOT / "cards"
DATA_DIR = ROOT / "data"
for folder in (ROOT, HTML_DIR, CARDS_DIR, DATA_DIR):
    folder.mkdir(parents=True, exist_ok=True)

CHROME = Path("/home/QYJI/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome")
CARD_W = 1440
CARD_H = 1920
TOTAL = 8

QUOTE_ITEMS = {
    "1.510300": ("沪深300ETF", "宽基"),
    "1.510880": ("红利ETF", "防御"),
    "1.512690": ("酒ETF", "白酒"),
    "1.512010": ("医药ETF", "医药"),
    "1.512170": ("医疗ETF", "医药"),
    "0.159992": ("创新药ETF", "医药"),
    "1.600519": ("贵州茅台", "白酒"),
    "0.000858": ("五粮液", "白酒"),
    "1.600276": ("恒瑞医药", "医药"),
    "1.603259": ("药明康德", "医药"),
    "0.300760": ("迈瑞医疗", "医药"),
    "1.601318": ("中国平安", "金融"),
    "1.600887": ("伊利股份", "消费"),
    "1.601888": ("中国中免", "消费"),
}

FALLBACK_QUOTES = [
    {"label": "中国平安", "group": "金融", "name": "中国平安", "code": "601318", "pct": 5.41, "amount": 7.469e9},
    {"label": "药明康德", "group": "医药", "name": "药明康德", "code": "603259", "pct": 3.39, "amount": 4.937e9},
    {"label": "贵州茅台", "group": "白酒", "name": "贵州茅台", "code": "600519", "pct": 2.67, "amount": 6.247e9},
    {"label": "沪深300ETF", "group": "宽基", "name": "沪深300ETF华泰柏瑞", "code": "510300", "pct": 1.93, "amount": 6.372e9},
    {"label": "伊利股份", "group": "消费", "name": "伊利股份", "code": "600887", "pct": 1.57, "amount": 1.560e9},
    {"label": "中国中免", "group": "消费", "name": "中国中免", "code": "601888", "pct": 1.54, "amount": 2.606e9},
    {"label": "恒瑞医药", "group": "医药", "name": "恒瑞医药", "code": "600276", "pct": 1.53, "amount": 3.679e9},
    {"label": "医药ETF", "group": "医药", "name": "医药ETF易方达", "code": "512010", "pct": 1.53, "amount": 4.599e8},
    {"label": "五粮液", "group": "白酒", "name": "五粮液", "code": "000858", "pct": 1.07, "amount": 2.353e9},
    {"label": "迈瑞医疗", "group": "医药", "name": "迈瑞医疗", "code": "300760", "pct": 0.80, "amount": 1.267e9},
    {"label": "酒ETF", "group": "白酒", "name": "酒ETF鹏华", "code": "512690", "pct": 0.74, "amount": 8.292e8},
    {"label": "红利ETF", "group": "防御", "name": "红利ETF华泰柏瑞", "code": "510880", "pct": 0.65, "amount": 1.005e9},
    {"label": "医疗ETF", "group": "医药", "name": "医疗ETF华宝", "code": "512170", "pct": 0.34, "amount": 6.081e8},
    {"label": "创新药ETF", "group": "医药", "name": "创新药ETF银华", "code": "159992", "pct": 0.00, "amount": 6.202e8},
]

FALLBACK_CONCEPTS = [
    {"name": "稀缺资源", "pct_chg": 4.08, "leader_name": "锌业股份", "main_net_in": 7.84e9},
    {"name": "参股期货", "pct_chg": 3.44, "leader_name": "中科金财", "main_net_in": 6.43e9},
    {"name": "化工原料", "pct_chg": 3.43, "leader_name": "川发龙蟒", "main_net_in": 3.06e9},
    {"name": "互联网金融", "pct_chg": 3.31, "leader_name": "中科金财", "main_net_in": 10.38e9},
    {"name": "蓝宝石", "pct_chg": 3.16, "leader_name": "三安光电", "main_net_in": -3.08e9},
    {"name": "黄金概念", "pct_chg": 2.75, "leader_name": "株冶集团", "main_net_in": 4.13e9},
    {"name": "上证50", "pct_chg": 2.71, "leader_name": "中国人寿", "main_net_in": 2.34e9},
    {"name": "上证180", "pct_chg": 2.16, "leader_name": "新华保险", "main_net_in": -0.05e9},
    {"name": "沪深300", "pct_chg": 2.13, "leader_name": "广发证券", "main_net_in": -11.46e9},
]


def pct(value: Any, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):+.{digits}f}%"


def money(value: Any) -> str:
    if value is None or pd.isna(value):
        return "-"
    value = float(value)
    return f"{value / 1e8:.1f}亿" if abs(value) >= 1e8 else f"{value / 1e4:.0f}万"


def em_quote(secid: str) -> dict[str, Any]:
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {"secid": secid, "fields": "f57,f58,f43,f169,f170,f48,f86"}
    resp = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}, timeout=8)
    resp.raise_for_status()
    data = resp.json().get("data") or {}
    return {
        "name": data.get("f58"),
        "code": data.get("f57"),
        "pct": float(data["f170"]) / 100 if isinstance(data.get("f170"), (int, float)) else None,
        "amount": data.get("f48"),
        "timestamp": data.get("f86"),
    }


def collect_quotes() -> pd.DataFrame:
    rows = []
    for secid, (label, group) in QUOTE_ITEMS.items():
        try:
            row = em_quote(secid)
            row.update({"secid": secid, "label": label, "group": group})
            if row.get("pct") is not None:
                rows.append(row)
        except Exception as exc:
            print(f"  quote failed {label}: {type(exc).__name__} {str(exc)[:80]}")
    if len(rows) < 10:
        rows = FALLBACK_QUOTES
    df = pd.DataFrame(rows)
    df["pct"] = pd.to_numeric(df["pct"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.sort_values("pct", ascending=False).reset_index(drop=True)
    df.to_csv(DATA_DIR / "selected_quotes.csv", index=False, encoding="utf-8-sig")
    return df


def collect_concepts() -> pd.DataFrame:
    if HotspotFetcher is None:
        df = pd.DataFrame(FALLBACK_CONCEPTS)
    else:
        try:
            fetcher = HotspotFetcher("./data/cache/hotspot")
            df = fetcher.concept_board(use_cache=True)
            if df is None or len(df) == 0:
                df = pd.DataFrame(FALLBACK_CONCEPTS)
        except Exception as exc:
            print(f"  concept fetch failed: {type(exc).__name__} {str(exc)[:80]}")
            df = pd.DataFrame(FALLBACK_CONCEPTS)
    df = df.head(18).copy()
    df.to_csv(DATA_DIR / "concept_board.csv", index=False, encoding="utf-8-sig")
    return df


def q(summary: dict[str, Any], label: str) -> dict[str, Any]:
    for row in summary["quotes"]:
        if row.get("label") == label:
            return row
    return {}


def build_summary(quotes: pd.DataFrame, concepts: pd.DataFrame) -> dict[str, Any]:
    quotes_list = quotes.to_dict("records")
    temp = {"quotes": quotes_list}
    hs300 = q(temp, "沪深300ETF").get("pct") or 0
    red = q(temp, "红利ETF").get("pct") or 0
    summary = {
        "topic": "老登股反攻：白酒医药保险等核心资产修复",
        "date": DATE_DIR,
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source_note": "东财实时 quote + 东财概念榜；接口失败时使用本次会话已验证快照。",
        "hs300_pct": hs300,
        "red_pct": red,
        "style_spread": hs300 - red,
        "leaders": quotes.head(6).to_dict("records"),
        "quotes": quotes_list,
        "concept_top": concepts.head(10).to_dict("records"),
    }
    (ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


CSS = """
:root{--bg:#0b1116;--panel:#141d25;--panel2:#1d2933;--line:#33414f;--text:#edf4f8;--muted:#91a1af;--dim:#667481;--gold:#f4c95d;--green:#49d17d;--red:#ff6b76;--blue:#65aaff;--cyan:#59d6df;--orange:#f4a64e;--purple:#b792ff;}
*{box-sizing:border-box}html,body{margin:0;width:1440px;height:1920px;overflow:hidden}body{background:var(--bg);font-family:"Noto Sans CJK SC","Droid Sans Fallback","Microsoft YaHei",sans-serif;color:var(--text)}
.card{width:1440px;height:1920px;position:relative;padding:88px 96px;background:radial-gradient(circle at 80% 8%,rgba(244,201,93,.16),transparent 30%),linear-gradient(135deg,#0b1116 0%,#101a23 58%,#070c11 100%)}
.eyebrow{display:inline-flex;padding:12px 28px;border-radius:999px;background:var(--gold);color:#101419;font-weight:950;font-size:30px}.title{margin-top:38px;font-size:76px;line-height:1.08;font-weight:950}.subtitle{margin-top:22px;font-size:30px;color:var(--muted);line-height:1.5}.panel{border:2px solid var(--line);border-radius:26px;background:rgba(20,29,37,.94);box-shadow:0 18px 50px rgba(0,0,0,.28)}.soft{background:rgba(29,41,51,.88)}.muted{color:var(--muted)}.dim{color:var(--dim)}.gold{color:var(--gold)}.green{color:var(--green)}.red{color:var(--red)}.blue{color:var(--blue)}.cyan{color:var(--cyan)}.orange{color:var(--orange)}.purple{color:var(--purple)}.footer{position:absolute;left:96px;right:96px;bottom:48px;color:var(--dim);font-size:22px;display:flex;justify-content:space-between}.pill{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;border:2px solid currentColor;padding:12px 22px;font-size:25px;font-weight:900}.label{font-size:24px;color:var(--muted)}.small{font-size:24px}.body{font-size:30px;line-height:1.55}.row{display:flex;align-items:center;justify-content:space-between;gap:18px}.hr{height:2px;background:var(--line);opacity:.75}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:24px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.big{font-size:96px;line-height:1;font-weight:950;font-variant-numeric:tabular-nums}
"""


def shell(inner: str, page: int) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><section class="card">{inner}<div class="footer"><span>数据来源: 东方财富 / AKShare · 不构成投资建议</span><span>{page}/{TOTAL}</span></div></section></body></html>"""


def quote_rows(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    html = ""
    for row in rows:
        color = "green" if (row.get("pct") or 0) >= 0 else "red"
        html += f"<div class='row' style='padding:22px 0;border-bottom:1px solid var(--line)'><div><div style='font-size:34px;font-weight:950'>{row.get('label')}</div><div class='muted small'>{row.get('group','')} · 成交额 {money(row.get('amount'))}</div></div><div class='{color}' style='font-size:46px;font-weight:950'>{pct(row.get('pct'),2)}</div></div>"
    return html


def build_cards(summary: dict[str, Any]) -> list[tuple[str, str]]:
    cards: list[tuple[str, str]] = []
    leaders = summary["quotes"][:8]
    concepts = summary["concept_top"][:7]
    hs300 = summary["hs300_pct"]
    red = summary["red_pct"]
    spread = summary["style_spread"]

    cards.append(("01_cover", shell(f"""
<div class="eyebrow">2026-06-22 · 核心资产反攻</div><div class="title">老登股<br>突然又香了？</div><div class="subtitle">白酒、医药、保险一起反弹。今天不是单点行情，而是核心资产修复。</div>
<div style="position:absolute;left:96px;right:96px;top:650px;display:flex;gap:20px;flex-wrap:wrap;align-items:center">
    <span class="pill green">中国平安 {pct(q(summary,'中国平安').get('pct'),2)}</span>
    <span class="pill gold">贵州茅台 {pct(q(summary,'贵州茅台').get('pct'),2)}</span>
    <span class="pill cyan">药明康德 {pct(q(summary,'药明康德').get('pct'),2)}</span>
    <span class="pill blue">沪深300ETF {pct(hs300,2)}</span>
</div>
<div class="panel soft" style="position:absolute;left:96px;right:96px;top:800px;padding:30px 42px;border-color:var(--gold)"><div class="row"><div><div style="font-size:34px;font-weight:950">今天的风格信号</div><div class="muted small">核心资产跑赢红利防御，资金从躲避风险切向修复弹性</div></div><div class="gold" style="font-size:54px;font-weight:950">{pct(spread,2)}</div></div></div>
<div class="panel" style="position:absolute;left:96px;right:96px;bottom:250px;padding:44px 52px"><div class="row"><div><div class="label">今日最强代表</div><div style="font-size:48px;font-weight:950">中国平安</div></div><div class="green" style="font-size:120px;font-weight:950">{pct(q(summary,'中国平安').get('pct'),2)}</div></div><div class="hr" style="margin:28px 0"></div><div class="grid3"><div><div class="label">贵州茅台</div><div class="green" style="font-size:44px;font-weight:950">{pct(q(summary,'贵州茅台').get('pct'),2)}</div></div><div><div class="label">药明康德</div><div class="green" style="font-size:44px;font-weight:950">{pct(q(summary,'药明康德').get('pct'),2)}</div></div><div><div class="label">沪深300ETF</div><div class="green" style="font-size:44px;font-weight:950">{pct(hs300,2)}</div></div></div></div>
""", 1)))

    cards.append(("02_tape", shell(f"""
<div class="eyebrow">盘面证据</div><div class="title" style="font-size:62px">谁真的在涨？</div><div class="subtitle">白酒、医药有表现，但更强的是大盘核心资产和金融权重。</div><div class="panel" style="margin-top:46px;padding:22px 46px">{quote_rows(summary, leaders)}</div>
""", 2)))

    concept_html = ""
    for row in concepts:
        concept_html += f"<div class='row' style='padding:20px 0;border-bottom:1px solid var(--line)'><div><div style='font-size:32px;font-weight:950'>{row.get('name')}</div><div class='muted small'>领涨: {row.get('leader_name','-')} · 主力 {money(row.get('main_net_in'))}</div></div><div class='green' style='font-size:42px;font-weight:950'>{pct(row.get('pct_chg'),2)}</div></div>"
    cards.append(("03_style", shell(f"""
<div class="eyebrow">不是单纯喝酒吃药</div><div class="title" style="font-size:60px">今天主线更像<br>权重修复</div><div class="subtitle">概念榜靠前的是稀缺资源、金融、上证50、沪深300。白酒医药是“老登股”的情绪代表。</div><div class="panel" style="margin-top:38px;padding:24px 46px">{concept_html}</div>
""", 3)))

    cards.append(("04_reasons", shell(f"""
<div class="eyebrow">原因拆解</div><div class="title" style="font-size:62px">为什么今天轮到<br>老登股？</div><div class="grid3" style="margin-top:48px"><div class="panel" style="padding:34px 28px;height:410px"><div class="gold" style="font-size:56px;font-weight:950">01</div><div style="font-size:34px;font-weight:950;margin-top:18px">风格切换</div><div class="muted body" style="font-size:25px;margin-top:18px">沪深300ETF {pct(hs300,2)}，红利ETF {pct(red,2)}，大盘权重明显占优。</div></div><div class="panel" style="padding:34px 28px;height:410px"><div class="green" style="font-size:56px;font-weight:950">02</div><div style="font-size:34px;font-weight:950;margin-top:18px">估值修复</div><div class="muted body" style="font-size:25px;margin-top:18px">白酒、医药前期被压制，反弹更像低位修复。</div></div><div class="panel" style="padding:34px 28px;height:410px"><div class="cyan" style="font-size:56px;font-weight:950">03</div><div style="font-size:34px;font-weight:950;margin-top:18px">仓位回补</div><div class="muted body" style="font-size:25px;margin-top:18px">资金从高股息防守，切向核心资产 beta。</div></div></div><div class="panel soft" style="margin-top:36px;padding:30px 40px"><span class="gold" style="font-size:34px;font-weight:950">关键判断：</span><span class="body">这是“跌多了有人回补”，不是“新牛市确认”。</span></div><div class="grid3" style="position:absolute;left:96px;right:96px;top:1135px"><div class="panel" style="padding:26px 30px"><div class="label">核心/红利差</div><div class="gold" style="font-size:42px;font-weight:950">{pct(spread,2)}</div></div><div class="panel" style="padding:26px 30px"><div class="label">最强成交</div><div class="green" style="font-size:42px;font-weight:950">平安74.7亿</div></div><div class="panel" style="padding:26px 30px"><div class="label">主线性质</div><div class="cyan" style="font-size:42px;font-weight:950">权重修复</div></div></div><div class="panel" style="position:absolute;left:96px;right:96px;bottom:150px;padding:34px 42px"><div style="font-size:34px;font-weight:950;margin-bottom:24px">后面盯三件事</div><div class="grid3"><div><div class="label">风格</div><div class="green" style="font-size:38px;font-weight:950">300继续强于红利</div></div><div><div class="label">资金</div><div class="cyan" style="font-size:38px;font-weight:950">成交不缩回去</div></div><div><div class="label">价格</div><div class="gold" style="font-size:38px;font-weight:950">回踩有人接</div></div></div></div>
""", 4)))

    cards.append(("05_baijiu", shell(f"""
<div class="eyebrow">白酒怎么看</div><div class="title" style="font-size:62px">茅台拉起来了<br>但别急着喊反转</div><div class="grid2" style="margin-top:46px"><div class="panel" style="padding:42px"><div class="label">贵州茅台</div><div class="big green">{pct(q(summary,'贵州茅台').get('pct'),2)}</div><div class="muted small">成交额 {money(q(summary,'贵州茅台').get('amount'))}</div></div><div class="panel" style="padding:42px"><div class="label">酒ETF</div><div class="big green">{pct(q(summary,'酒ETF').get('pct'),2)}</div><div class="muted small">弱于茅台，说明资金更偏确定性权重。</div></div></div><div class="panel" style="margin-top:40px;padding:34px 44px"><div style="font-size:36px;font-weight:950">确认信号看三件事</div><div class="body muted" style="margin-top:16px">1. 茅台能否连续跑赢沪深300<br>2. 酒ETF成交放大后不回落<br>3. 消费数据或渠道预期跟上</div></div><div class="grid3" style="position:absolute;left:96px;right:96px;top:1135px"><div class="panel" style="padding:26px 30px"><div class="label">强弱排序</div><div class="green" style="font-size:38px;font-weight:950">茅台 > 酒ETF</div></div><div class="panel" style="padding:26px 30px"><div class="label">资金偏好</div><div class="gold" style="font-size:38px;font-weight:950">买确定性</div></div><div class="panel" style="padding:26px 30px"><div class="label">追涨风险</div><div class="red" style="font-size:38px;font-weight:950">ETF跟不上</div></div></div><div class="panel soft" style="position:absolute;left:96px;right:96px;bottom:150px;padding:34px 42px"><div style="font-size:34px;font-weight:950;margin-bottom:20px">白酒这根阳线怎么用？</div><div class="grid3"><div><div class="label">已经持有</div><div class="gold" style="font-size:35px;font-weight:950">看能否跑赢300</div></div><div><div class="label">准备买入</div><div class="cyan" style="font-size:35px;font-weight:950">等回踩不破</div></div><div><div class="label">最怕什么</div><div class="red" style="font-size:35px;font-weight:950">放量冲高回落</div></div></div></div>
""", 5)))

    cards.append(("06_pharma", shell(f"""
<div class="eyebrow">医药怎么看</div><div class="title" style="font-size:62px">医药不是一块涨<br>创新药更有弹性</div><div class="grid3" style="margin-top:46px"><div class="panel" style="padding:34px 28px"><div class="label">药明康德</div><div class="green" style="font-size:64px;font-weight:950">{pct(q(summary,'药明康德').get('pct'),2)}</div><div class="muted small">CXO弹性代表</div></div><div class="panel" style="padding:34px 28px"><div class="label">恒瑞医药</div><div class="green" style="font-size:64px;font-weight:950">{pct(q(summary,'恒瑞医药').get('pct'),2)}</div><div class="muted small">创新药龙头</div></div><div class="panel" style="padding:34px 28px"><div class="label">医疗ETF</div><div class="green" style="font-size:64px;font-weight:950">{pct(q(summary,'医疗ETF').get('pct'),2)}</div><div class="muted small">器械/服务偏弱</div></div></div><div class="panel soft" style="margin-top:42px;padding:34px 44px"><div class="body">医药今天的重点不是“全行业反转”，而是被压太久的龙头和创新药链条先修复。</div></div><div class="grid3" style="position:absolute;left:96px;right:96px;top:1135px"><div class="panel" style="padding:26px 30px"><div class="label">弹性来源</div><div class="green" style="font-size:38px;font-weight:950">CXO先动</div></div><div class="panel" style="padding:26px 30px"><div class="label">确认信号</div><div class="cyan" style="font-size:38px;font-weight:950">创新药扩散</div></div><div class="panel" style="padding:26px 30px"><div class="label">反证信号</div><div class="red" style="font-size:38px;font-weight:950">器械继续弱</div></div></div><div class="panel" style="position:absolute;left:96px;right:96px;bottom:150px;padding:34px 42px"><div style="font-size:34px;font-weight:950;margin-bottom:20px">医药内部强弱分层</div><div class="grid3"><div><div class="label">最强</div><div class="green" style="font-size:38px;font-weight:950">CXO / 创新药</div></div><div><div class="label">一般</div><div class="gold" style="font-size:38px;font-weight:950">宽医药ETF</div></div><div><div class="label">偏弱</div><div class="red" style="font-size:38px;font-weight:950">器械服务</div></div></div></div>
""", 6)))

    cards.append(("07_playbook", shell(f"""
<div class="eyebrow">操作框架</div><div class="title" style="font-size:62px">追不追？<br>看三条线</div><div class="panel" style="margin-top:42px;padding:40px 48px"><div class="row"><div><div style="font-size:36px;font-weight:950">1日冲高</div><div class="muted small">只说明情绪来了</div></div><div class="pill orange">不追满</div></div><div class="hr" style="margin:26px 0"></div><div class="row"><div><div style="font-size:36px;font-weight:950">3日不回吐</div><div class="muted small">确认不是一日游</div></div><div class="pill cyan">可试仓</div></div><div class="hr" style="margin:26px 0"></div><div class="row"><div><div style="font-size:36px;font-weight:950">跑赢沪深300</div><div class="muted small">才算板块真强</div></div><div class="pill green">再加仓</div></div></div><div class="panel soft" style="margin-top:40px;padding:32px 44px"><span class="gold" style="font-size:34px;font-weight:950">我的结论：</span><span class="body">白酒医药可以看，但今天更适合等回踩确认，不适合一根阳线就信仰充值。</span></div><div class="grid3" style="position:absolute;left:96px;right:96px;top:1135px"><div class="panel" style="padding:26px 30px"><div class="label">买入前</div><div class="orange" style="font-size:38px;font-weight:950">先看3天</div></div><div class="panel" style="padding:26px 30px"><div class="label">买入后</div><div class="cyan" style="font-size:38px;font-weight:950">破低撤退</div></div><div class="panel" style="padding:26px 30px"><div class="label">加仓时</div><div class="green" style="font-size:38px;font-weight:950">跑赢再加</div></div></div><div class="panel" style="position:absolute;left:96px;right:96px;bottom:150px;padding:34px 42px"><div style="font-size:34px;font-weight:950;margin-bottom:20px">分批动作表</div><div class="grid3"><div><div class="label">0-1天</div><div class="orange" style="font-size:38px;font-weight:950">看戏</div></div><div><div class="label">3天不回吐</div><div class="cyan" style="font-size:38px;font-weight:950">试仓20%</div></div><div><div class="label">持续跑赢</div><div class="green" style="font-size:38px;font-weight:950">再加到40%</div></div></div></div>
""", 7)))

    cards.append(("08_cta", shell(f"""
<div class="eyebrow">最后总结</div><div class="title" style="font-size:60px">三句话看懂<br>老登股反攻</div><div style="margin-top:54px"><div class="row" style="padding:26px 0;border-bottom:2px solid var(--line)"><div class="gold" style="font-size:58px;font-weight:950">01</div><div style="flex:1"><div style="font-size:36px;font-weight:950">今天是核心资产修复</div><div class="muted small">不是只有白酒医药，保险/上证50/沪深300更关键</div></div></div><div class="row" style="padding:26px 0;border-bottom:2px solid var(--line)"><div class="green" style="font-size:58px;font-weight:950">02</div><div style="flex:1"><div style="font-size:36px;font-weight:950">反弹不等于反转</div><div class="muted small">跌多了回补仓位，基本面还要等验证</div></div></div><div class="row" style="padding:26px 0"><div class="red" style="font-size:58px;font-weight:950">03</div><div style="flex:1"><div style="font-size:36px;font-weight:950">追涨看纪律</div><div class="muted small">3日不回吐 + 跑赢300，再考虑加仓</div></div></div></div><div class="panel" style="margin-top:48px;padding:34px 44px;border-color:var(--orange)"><div style="text-align:center;font-size:34px;font-weight:950">你今天是哪种？</div><div class="grid3" style="margin-top:26px"><div class="pill blue">买了白酒</div><div class="pill green">买了医药</div><div class="pill">继续观望</div></div></div><div class="panel soft" style="margin-top:40px;padding:28px;border-color:var(--cyan);text-align:center"><div class="cyan" style="font-size:42px;font-weight:950">评论区打「老登股」↓</div><div class="muted small" style="margin-top:12px">我把完整数据和研报整理好了</div></div><div style="position:absolute;left:170px;right:170px;bottom:122px;text-align:center"><span class="pill gold" style="font-size:25px">关注我：每周拆一个A股ETF/板块胜率</span></div>
""", 8)))
    return cards


def write_cards(cards: list[tuple[str, str]]) -> None:
    links = []
    for idx, (name, html) in enumerate(cards, 1):
        path = HTML_DIR / f"{idx:02d}_{name}.html"
        path.write_text(html, encoding="utf-8")
        links.append(f"<li><a href='{path.name}'>{idx:02d} {name}</a></li>")
    (HTML_DIR / "index.html").write_text("<html><body><ul>" + "".join(links) + "</ul></body></html>", encoding="utf-8")


def chrome_args() -> list[str]:
    if not CHROME.exists():
        raise RuntimeError(f"Chromium not found: {CHROME}")
    return [str(CHROME), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars"]


def render_cards(cards: list[tuple[str, str]]) -> None:
    for idx, (name, _) in enumerate(cards, 1):
        html = (HTML_DIR / f"{idx:02d}_{name}.html").resolve().as_uri()
        out = (CARDS_DIR / f"{idx:02d}_{name}.png").resolve()
        cmd = chrome_args() + [f"--window-size={CARD_W},{CARD_H}", f"--screenshot={out}", html]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  {out.name}")


def report_html(summary: dict[str, Any]) -> str:
    quote_tr = "".join(
        f"<tr><td>{r.get('label')}</td><td>{r.get('code')}</td><td>{r.get('group')}</td><td class='pos'>{pct(r.get('pct'),2)}</td><td>{money(r.get('amount'))}</td></tr>"
        for r in summary["quotes"]
    )
    concept_tr = "".join(
        f"<tr><td>{r.get('name')}</td><td class='pos'>{pct(r.get('pct_chg'),2)}</td><td>{r.get('leader_name','-')}</td><td>{money(r.get('main_net_in'))}</td></tr>"
        for r in summary["concept_top"][:12]
    )
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>body{{font-family:'Noto Sans CJK SC','Droid Sans Fallback',sans-serif;background:#f4f6f9;margin:0;color:#263342}}.page{{max-width:980px;margin:0 auto;background:white;padding:54px 66px}}h1{{font-size:34px;color:#10243e;margin:0 0 8px}}h2{{background:#10243e;color:white;padding:10px 14px;font-size:20px;margin-top:32px}}p,li{{font-size:15px;line-height:1.75}}table{{width:100%;border-collapse:collapse;font-size:13px;margin:16px 0}}td,th{{border:1px solid #d7dee8;padding:8px;text-align:center}}th{{background:#e9eef5}}.pos{{color:#16803a;font-weight:800}}.note{{color:#667085;font-size:12px}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}}.kpi{{background:#f8fafc;border:1px solid #d9e1ea;border-radius:8px;padding:16px}}.v{{font-size:28px;font-weight:850}}</style></head><body><main class='page'><h1>{summary['topic']}</h1><p class='note'>生成时间：{summary['generated']}｜{summary['source_note']}</p><div class='kpis'><div class='kpi'>沪深300ETF<div class='v pos'>{pct(summary['hs300_pct'],2)}</div></div><div class='kpi'>红利ETF<div class='v pos'>{pct(summary['red_pct'],2)}</div></div><div class='kpi'>核心/红利差<div class='v pos'>{pct(summary['style_spread'],2)}</div></div><div class='kpi'>最强代表<div class='v pos'>{pct(summary['leaders'][0].get('pct'),2)}</div></div></div><h2>一、摘要判断</h2><p>今天白酒、医药、保险等所谓“老登股”一起修复，但更准确的标签不是“白酒医药大涨”，而是核心资产与大盘权重修复。代表证据是：沪深300ETF上涨 {pct(summary['hs300_pct'],2)}，中国平安上涨 {pct(q(summary,'中国平安').get('pct'),2)}，贵州茅台上涨 {pct(q(summary,'贵州茅台').get('pct'),2)}，药明康德上涨 {pct(q(summary,'药明康德').get('pct'),2)}。</p><p>这轮上涨更像估值和仓位修复，而不是基本面一夜反转。白酒和医药是最容易被散户感知的“老登股”标签，但从概念榜看，稀缺资源、金融、上证50、沪深300同样靠前。</p><h2>二、盘面证据</h2><table><thead><tr><th>标的</th><th>代码</th><th>分组</th><th>涨跌幅</th><th>成交额</th></tr></thead><tbody>{quote_tr}</tbody></table><h2>三、板块风格证据</h2><table><thead><tr><th>概念/风格</th><th>涨跌幅</th><th>领涨股</th><th>主力净流入</th></tr></thead><tbody>{concept_tr}</tbody></table><h2>四、原因拆解</h2><ul><li>风格切换：红利ETF上涨 {pct(summary['red_pct'],2)}，沪深300ETF上涨 {pct(summary['hs300_pct'],2)}，大盘核心资产占优。</li><li>估值修复：白酒和医药被压制时间长，风险偏好回来时容易先弹。</li><li>仓位回补：今天更像“跌多了有人回补”，不是行业基本面一夜反转。</li></ul><h2>五、后续观察</h2><ul><li>连续3日不回吐，才说明不是一日游。</li><li>持续跑赢沪深300，才说明行业自身强度恢复。</li><li>成交放大后回踩有资金接，才适合继续跟踪。</li></ul><p class='note'>风险提示：以上为市场数据复盘和量化观察，不构成投资建议。实时行情可能随交易时段变化。</p></main></body></html>"""


def write_report(summary: dict[str, Any]) -> None:
    html_path = ROOT / "老登股反攻_白酒医药核心资产修复_深度研报.html"
    pdf_path = ROOT / "老登股反攻_白酒医药核心资产修复_深度研报.pdf"
    html_path.write_text(report_html(summary), encoding="utf-8")
    cmd = chrome_args() + ["--no-pdf-header-footer", f"--print-to-pdf={pdf_path.resolve()}", html_path.resolve().as_uri()]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def write_xhs_copy(summary: dict[str, Any]) -> None:
    text = f"""# 小红书发布文案｜老登股反攻

## 标题备选
1. 老登股突然反攻，白酒医药又香了？
2. 茅台、药明、平安一起涨，今天发生了什么？
3. 白酒医药大涨，是反转还是反弹？
4. 核心资产回来了？我拆了今天的盘面

## 正文
今天很多老登股突然支棱起来了。

白酒、医药、保险这些过去几年让人又爱又恨的核心资产，今天集体修复。代表数据：贵州茅台 {pct(q(summary,'贵州茅台').get('pct'),2)}，药明康德 {pct(q(summary,'药明康德').get('pct'),2)}，恒瑞医药 {pct(q(summary,'恒瑞医药').get('pct'),2)}，中国平安 {pct(q(summary,'中国平安').get('pct'),2)}。

但我觉得今天不能简单说成“白酒医药大涨”。更准确地说，是核心资产和大盘权重修复：沪深300ETF涨 {pct(summary['hs300_pct'],2)}，红利ETF只涨 {pct(summary['red_pct'],2)}，说明资金不是继续躲在高股息防御里，而是在往核心权重切。

原因大概有三条：第一，风格切换；第二，估值修复；第三，仓位回补。今天更像“跌多了有人回补”，不是基本面一夜反转。

后面看三件事：能不能连续3天不回吐；能不能持续跑赢沪深300；成交放大后回踩有没有资金接。

一句话：今天可以重视，但不适合无脑追。反弹来了，反转还要等确认。

## 标签
#老登股 #白酒 #医药 #贵州茅台 #恒瑞医药 #药明康德 #中国平安 #核心资产 #A股复盘 #ETF投资
"""
    (ROOT / "小红书发布文案.md").write_text(text, encoding="utf-8")


def main() -> None:
    print("[1] data")
    quotes = collect_quotes()
    concepts = collect_concepts()
    summary = build_summary(quotes, concepts)
    print("[2] cards html")
    cards = build_cards(summary)
    write_cards(cards)
    print("[3] render png")
    render_cards(cards)
    print("[4] report")
    write_report(summary)
    print("[5] xhs copy")
    write_xhs_copy(summary)
    print(f"Done: {ROOT}")


if __name__ == "__main__":
    main()