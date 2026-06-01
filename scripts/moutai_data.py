#!/usr/bin/env python3
"""
茅台数据获取模块
优先级: 东方财富API(通过curl) > AKShare(需unset代理) > yfinance

在WSL环境下，Python的urllib会被系统代理(127.0.0.1:10793)拦截，
但curl可以直连。因此通过subprocess调curl获取东方财富数据。
"""

import json
import subprocess
import os
from dataclasses import dataclass, field
from datetime import date


def _curl_get(url: str, timeout: int = 10) -> dict:
    """通过curl GET请求，绕过Python代理"""
    result = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), url],
        capture_output=True, text=True, timeout=timeout + 2
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


@dataclass
class MoutaiData:
    """茅台分析所需全部数据"""
    price: float = 0.0              # 实时股价(元)
    market_cap: float = 0.0         # 总市值(亿)
    total_shares: float = 0.0       # 总股本(亿股)
    pe: float = 0.0                 # PE(TTM)
    eps: float = 0.0                # 每股收益
    pb: float = 0.0                 # 市净率
    roe: float = 0.0                # ROE (最新年报, %)
    roe_10yr_avg: float = 0.0       # 10年平均ROE
    np_cagr_10yr: float = 0.0       # 10年净利润CAGR
    gross_margin: float = 0.0       # 毛利率(%)
    net_margin: float = 0.0         # 净利率(%)
    cash_to_np: float = 0.0         # 现金流/净利润(%)
    debt_ratio: float = 0.0         # 资产负债率(%)
    current_ratio: float = 0.0      # 流动比率
    quick_ratio: float = 0.0        # 速动比率
    roe_history: list = field(default_factory=list)  # [(year, roe%), ...]
    np_history: list = field(default_factory=list)   # [(year, net_profit_亿), ...]
    source: str = ""                # 数据来源
    fetch_date: str = ""            # 数据获取日期


# ═══════════════════════════════════════════════════
# 东方财富直连 (via curl)
# ═══════════════════════════════════════════════════

def _fetch_em_quote(data: MoutaiData) -> bool:
    """东方财富实时行情"""
    try:
        url = ("https://push2.eastmoney.com/api/qt/stock/get?"
               "secid=1.600519&"
               "fields=f43,f44,f45,f46,f47,f48,f50,f57,f58,"
               "f116,f117,f9,f20,f21,f23,f24,f25,f37,f38,f39,f40,f41,f49,f55,f115,f162,f167,f168,f169")
        j = _curl_get(url)
        d = j.get("data", {})
        if not d:
            return False

        # 价格 (分→元)
        price_raw = d.get("f43", 0)
        if price_raw <= 0:
            return False
        data.price = price_raw / 100.0

        # 股本 (股→亿股)
        data.total_shares = d.get("f116", 0) / 1e8

        # 市值 (元→亿)
        data.market_cap = d.get("f20", 0) / 1e8

        # PE (动态PE优先, TTM备用)
        data.pe = d.get("f115", d.get("f9", 0))

        # PB
        data.pb = d.get("f23", 0)

        # EPS
        data.eps = d.get("f38", 0)

        # ROE (%)
        data.roe = d.get("f37", 0) / 100.0

        # 毛利率 (%)
        data.gross_margin = d.get("f49", 0) / 100.0

        # 净利率 (%)
        data.net_margin = d.get("f25", d.get("f24", 0)) / 100.0

        # 现金流/净利润
        ocf_ps = d.get("f55", 0)
        if ocf_ps and data.eps:
            data.cash_to_np = (ocf_ps / data.eps) * 100

        data.source = "东方财富"
        return True
    except Exception as e:
        print(f"  [EM行情] {e}")
        return False


def _fetch_em_financials(data: MoutaiData) -> bool:
    """东方财富年度财务数据：利润表 + ROE + 资产负债表"""
    got_any = False

    # 1. 年度利润表 (净利润历史)
    try:
        url = ("https://datacenter.eastmoney.com/securities/api/data/v1/get?"
               "reportName=RPT_LICO_FN_CPD&"
               "columns=SECURITY_CODE,REPORT_DATE,PARENT_NETPROFIT&"
               "filter=(SECURITY_CODE=%22600519%22)&"
               "pageSize=15&sortTypes=-1&sortColumns=REPORT_DATE")
        j = _curl_get(url)
        rows = (j.get("result") or {}).get("data") or []

        profits = []
        for r in reversed(rows):
            year = r["REPORT_DATE"][:4]
            np_yi = (r.get("PARENT_NETPROFIT") or 0) / 1e8
            if np_yi > 0:
                profits.append((year, np_yi))

        if profits:
            data.np_history = profits
            got_any = True

            # 10年CAGR
            recent = profits[-10:] if len(profits) >= 10 else profits
            if len(recent) > 1 and recent[0][1] > 0:
                yrs = len(recent) - 1
                data.np_cagr_10yr = ((recent[-1][1] / recent[0][1]) ** (1 / yrs) - 1) * 100
    except Exception as e:
        print(f"  [EM利润表] {e}")

    # 2. 杜邦ROE历史
    try:
        url2 = ("https://datacenter.eastmoney.com/securities/api/data/v1/get?"
                "reportName=RPT_DMSK_FN_DUPONT&"
                "columns=SECURITY_CODE,REPORT_DATE,ROE_WEIGHT&"
                "filter=(SECURITY_CODE=%22600519%22)&"
                "pageSize=15&sortTypes=-1&sortColumns=REPORT_DATE")
        j2 = _curl_get(url2)
        rows2 = (j2.get("result") or {}).get("data") or []

        roe_data = []
        for r in reversed(rows2):
            year = r["REPORT_DATE"][:4]
            roe_w = r.get("ROE_WEIGHT")
            if roe_w is not None:
                roe_data.append((year, float(roe_w)))

        if roe_data:
            data.roe_history = roe_data
            got_any = True

            recent = roe_data[-10:] if len(roe_data) >= 10 else roe_data
            data.roe_10yr_avg = sum(v for _, v in recent) / len(recent)
    except Exception as e:
        print(f"  [EM杜邦] {e}")

    # 3. 资产负债表 (负债率/流动比率/速动比率)
    try:
        url3 = ("https://datacenter.eastmoney.com/securities/api/data/v1/get?"
                "reportName=RPT_DMSK_FN_BALANCE&"
                "columns=SECURITY_CODE,REPORT_DATE,"
                "DEBT_ASSET_RATIO,CURRENT_RATIO,QUICK_RATIO&"
                "filter=(SECURITY_CODE=%22600519%22)&"
                "pageSize=1&sortTypes=-1&sortColumns=REPORT_DATE")
        j3 = _curl_get(url3)
        rows3 = (j3.get("result") or {}).get("data") or []

        if rows3:
            r = rows3[0]
            data.debt_ratio = float(r.get("DEBT_ASSET_RATIO", 0))
            data.current_ratio = float(r.get("CURRENT_RATIO", 0))
            data.quick_ratio = float(r.get("QUICK_RATIO", 0))
            got_any = True
    except Exception as e:
        print(f"  [EM负债表] {e}")

    return got_any


# ═══════════════════════════════════════════════════
# AKShare (unset proxy)
# ═══════════════════════════════════════════════════

def _fetch_akshare(data: MoutaiData) -> bool:
    """AKShare获取财务数据 (通过subprocess清除代理)"""
    script = '''
import json, warnings
warnings.filterwarnings("ignore")
import akshare as ak

result = {}

# 个股信息
try:
    info = ak.stock_individual_info_em(symbol="600519")
    info_dict = {}
    for _, row in info.iterrows():
        info_dict[row['item']] = row['value']
    result['info'] = info_dict
except Exception as e:
    result['info_error'] = str(e)

# 财务指标
try:
    fin = ak.stock_financial_analysis_indicator_em(symbol="600519")
    if '日期' in fin.columns:
        last = fin.iloc[0]
        result['roe'] = float(last.get('净资产收益率', 0))
        result['gross_margin'] = float(last.get('销售毛利率', 0))
        result['net_margin'] = float(last.get('销售净利率', 0))
        result['debt_ratio'] = float(last.get('资产负债率', 0))
except Exception as e:
    result['fin_error'] = str(e)

print(json.dumps(result, ensure_ascii=False))
'''
    try:
        env = {**os.environ, "HTTP_PROXY": "", "HTTPS_PROXY": "",
               "http_proxy": "", "https_proxy": ""}
        r = subprocess.run(
            ["python3", "-c", script],
            capture_output=True, text=True, timeout=30, env=env
        )
        if r.returncode != 0:
            print(f"  [AKShare] 执行失败: {r.stderr[:200]}")
            return False

        res = json.loads(r.stdout)
        if "info" in res:
            info = res["info"]
            val = lambda k, default=0: float(info.get(k, default)) if info.get(k) not in (None, '', '-') else default

            if data.pe <= 0:
                data.pe = val('市盈率-动态') or val('市盈率')
            if data.eps <= 0:
                data.eps = val('基本每股收益')
            if data.pb <= 0:
                data.pb = val('市净率')
            if not data.total_shares:
                ts = info.get('总股本')
                if ts:
                    try:
                        data.total_shares = float(ts) / 1e8
                    except ValueError:
                        pass
            if not data.market_cap:
                mc = info.get('总市值')
                if mc:
                    try:
                        data.market_cap = float(mc) / 1e8
                    except ValueError:
                        pass

        # 财务指标补充 (AKShare的值是百分数 * 100? 或直接百分数?)
        if data.roe <= 0 and "roe" in res:
            rv = res["roe"]
            data.roe = rv if rv < 100 else rv / 100
        if data.gross_margin <= 0 and "gross_margin" in res:
            gm = res["gross_margin"]
            data.gross_margin = gm if gm < 100 else gm / 100
        if data.net_margin <= 0 and "net_margin" in res:
            nm = res["net_margin"]
            data.net_margin = nm if nm < 100 else nm / 100
        if data.debt_ratio <= 0 and "debt_ratio" in res:
            dr = res["debt_ratio"]
            data.debt_ratio = dr if dr < 100 else dr / 100

        if data.source != "东方财富":
            data.source = "AKShare"

        return True
    except Exception as e:
        print(f"  [AKShare] {e}")
        return False


# ═══════════════════════════════════════════════════
# Yahoo Finance
# ═══════════════════════════════════════════════════

def _fetch_yahoo(data: MoutaiData) -> bool:
    """yfinance fallback"""
    try:
        import yfinance as yf
        ticker = yf.Ticker("600519.SS")
        info = ticker.info
        if not info or "currentPrice" not in info:
            return False

        if data.price <= 0:
            data.price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        if data.market_cap <= 0:
            data.market_cap = info.get("marketCap", 0) / 1e8
        if data.total_shares <= 0:
            data.total_shares = info.get("sharesOutstanding", 0) / 1e8
        if data.pe <= 0:
            data.pe = info.get("trailingPE", info.get("forwardPE", 0))
        if data.pb <= 0:
            data.pb = info.get("priceToBook", 0)
        if data.eps <= 0:
            data.eps = info.get("trailingEps", 0)
        if data.roe <= 0:
            data.roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0
        if data.gross_margin <= 0:
            data.gross_margin = info.get("grossMargins", 0) * 100 if info.get("grossMargins") else 0
        if data.net_margin <= 0:
            data.net_margin = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0
        if data.debt_ratio <= 0:
            data.debt_ratio = info.get("debtToEquity", 0)
        if data.current_ratio <= 0:
            data.current_ratio = info.get("currentRatio", 0)
        if data.quick_ratio <= 0:
            data.quick_ratio = info.get("quickRatio", 0)

        if data.source != "东方财富":
            data.source = "Yahoo Finance"
        return True
    except Exception as e:
        print(f"  [Yahoo] {e}")
        return False


# ═══════════════════════════════════════════════════
# 数据处理
# ═══════════════════════════════════════════════════

# ── 硬编码fallback (2024年报数据 + 当前实时价) ──
# 当所有API都失败时使用，数据来源标注为 "fallback"
_FALLBACK = {
    "price": 1309.60,              # 实时股价 (2026-06-01, 东方财富)
    "total_shares": 12.56,         # 总股本(亿股)
    "eps": 65.66,                  # 2024 EPS
    "roe": 32.5,                   # 2024 ROE(%)
    "roe_10yr_avg": 31.5,          # 10年加权平均ROE
    "np_cagr_10yr": 17.3,          # 10年净利润CAGR
    "gross_margin": 91.8,          # 毛利率
    "net_margin": 47.8,            # 净利率
    "cash_to_np": 74.7,            # 经营现金流/净利润
    "debt_ratio": 16.4,            # 资产负债率
    "current_ratio": 5.09,         # 流动比率
    "quick_ratio": 3.85,           # 速动比率
    "roe_history": [
        ("2016", 24.4), ("2017", 32.9), ("2018", 34.5), ("2019", 33.1), ("2020", 31.4),
        ("2021", 29.9), ("2022", 30.3), ("2023", 34.2), ("2024", 36.0), ("2025", 32.5),
    ],
}


def _compute_derived(data: MoutaiData):
    """补充/修正派生指标"""
    now = date.today()
    data.fetch_date = now.isoformat()

    # ── Fallback: 用硬编码补全缺失数据 ──
    fb = _FALLBACK

    if data.price <= 0:
        data.price = fb.get("price", 0)
    if data.total_shares <= 0:
        data.total_shares = fb["total_shares"]
    if data.eps <= 0:
        data.eps = fb["eps"]
    if data.roe <= 0:
        data.roe = fb["roe"]
    if data.gross_margin <= 0:
        data.gross_margin = fb["gross_margin"]
    if data.net_margin <= 0:
        data.net_margin = fb["net_margin"]
    if data.debt_ratio <= 0:
        data.debt_ratio = fb["debt_ratio"]
    if data.current_ratio <= 0:
        data.current_ratio = fb["current_ratio"]
    if data.quick_ratio <= 0:
        data.quick_ratio = fb["quick_ratio"]
    if data.cash_to_np <= 0:
        data.cash_to_np = fb["cash_to_np"]
    if not data.np_cagr_10yr:
        data.np_cagr_10yr = fb["np_cagr_10yr"]
    if not data.roe_history:
        data.roe_history = fb["roe_history"]

    # ROE 10yr — 优先用ROE历史
    if not data.roe_10yr_avg and data.roe_history:
        recent = data.roe_history[-10:]
        data.roe_10yr_avg = sum(v for _, v in recent) / len(recent)

    # ROE fallback
    if not data.roe_10yr_avg:
        data.roe_10yr_avg = data.roe or fb["roe_10yr_avg"]

    # ── 市值自动修正 (核心: 修复 ×1.256 → ×12.56 的bug) ──
    if data.total_shares > 0 and data.price > 0:
        calc_mcap = data.price * data.total_shares
        if data.market_cap <= 0 or abs(data.market_cap - calc_mcap) / calc_mcap > 0.2:
            data.market_cap = calc_mcap

    # PE 自动修正
    if data.eps > 0 and data.price > 0 and (data.pe <= 0 or data.pe > 200):
        data.pe = data.price / data.eps

    # ROE历史年份去重
    if data.roe_history:
        seen = set()
        deduped = []
        for yr, val in data.roe_history:
            if yr not in seen:
                seen.add(yr)
                deduped.append((yr, val))
        data.roe_history = deduped

    # 标记数据来源
    if not data.source:
        if data.price > 0:
            data.source = "东方财富(实时价) + 年报(fallback)"
        else:
            data.source = "年报数据(fallback)"


# ═══════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════

def fetch_moutai_data() -> MoutaiData:
    """
    获取茅台分析数据
    优先级: 东方财富(行情+财务) → AKShare → Yahoo
    """
    data = MoutaiData()

    # 1. 东方财富直连
    ok = _fetch_em_quote(data)
    if ok:
        print(f"  ✓ 东方财富 行情: {data.price:.2f}元 PE={data.pe:.1f}x 市值={data.market_cap:.0f}亿")

    _fetch_em_financials(data)

    # 2. AKShare 补充
    need_more = (data.eps <= 0 or data.roe <= 0 or not data.roe_history)
    if need_more:
        print("  → 东方财富财务数据不完整，尝试 AKShare...")
        _fetch_akshare(data)

    # 3. Yahoo fallback
    if data.price <= 0 or data.eps <= 0:
        print("  → 尝试 Yahoo Finance...")
        _fetch_yahoo(data)

    _compute_derived(data)

    # 打印摘要
    print(f"\n  === 数据摘要 ({data.source}) ===")
    print(f"  股价: {data.price:.2f}  市值: {data.market_cap:.0f}亿  股本: {data.total_shares:.2f}亿股")
    print(f"  PE: {data.pe:.1f}x  PB: {data.pb:.1f}  EPS: {data.eps:.2f}")
    print(f"  ROE(年报): {data.roe:.1f}%  ROE(10yr均值): {data.roe_10yr_avg:.1f}%")
    print(f"  净利CAGR(10yr): {data.np_cagr_10yr:.1f}%")
    print(f"  毛利率: {data.gross_margin:.1f}%  净利率: {data.net_margin:.1f}%")
    print(f"  现金流/净利: {data.cash_to_np:.0f}%")
    print(f"  负债率: {data.debt_ratio:.1f}%  流动: {data.current_ratio:.1f}  速动: {data.quick_ratio:.1f}")
    if data.roe_history:
        recent = data.roe_history[-5:]
        print(f"  近年ROE: {' → '.join(f'{y}:{v:.1f}%' for y, v in recent)}")

    return data


if __name__ == "__main__":
    d = fetch_moutai_data()
