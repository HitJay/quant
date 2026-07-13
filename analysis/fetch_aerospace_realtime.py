"""拉取商业航天个股实时行情 — 用 push2 直连绕过 akshare 历史接口"""
import requests
import json

_EM = "https://push2.eastmoney.com/api/qt/stock/get"
_EM_LIST = "https://push2.eastmoney.com/api/qt/clist/get"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

# 商业航天核心标的 (secid 格式: 1.沪 0.深)
STOCKS = [
    ("1.600118", "600118", "中国卫星"),
    ("0.002829", "002829", "星网宇达"),
    ("1.600879", "600879", "航天电子"),
    ("1.600990", "600990", "四创电子"),
    ("0.000901", "000901", "航天科技"),
    ("1.600501", "600501", "航天晨光"),
    ("1.600151", "600151", "航天机电"),
    ("0.300101", "300101", "振芯科技"),
    ("0.300053", "300053", "欧比特"),
    ("0.002013", "002013", "中航机电"),
]

results = []
for secid, code, name in STOCKS:
    try:
        r = requests.get(_EM, params={
            "secid": secid,
            "fields": "f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f168,f169,f170,f171,f297",
            "ut": "fa5fd1943c7b386f172d6893dbbd1",
        }, headers=_HEADERS, timeout=10)
        r.raise_for_status()
        d = r.json().get("data", {})
        if not d:
            print(f"{code} {name}: 空数据")
            continue
        # f43=最新价 f44=最高 f45=最低 f46=今开 f47=成交量(手) f48=成交额
        # f50=量比 f57=代码 f58=名称 f60=昨收 f168=换手率 f169=涨跌额 f170=涨跌幅 f171=振幅
        close = d.get("f43", 0) / 100  # 价格×100
        pct = d.get("f170", 0) / 100   # 涨跌幅×100
        vol_yi = d.get("f48", 0) / 1e8  # 成交额(元) → 亿
        turnover = d.get("f168", 0) / 100  # 换手率×100
        amplitude = d.get("f171", 0) / 100  # 振幅×100
        results.append({
            "code": code,
            "name": name,
            "close": round(close, 2),
            "pct_chg": round(pct, 2),
            "volume_yi": round(vol_yi, 2),
            "turnover": round(turnover, 2),
            "amplitude": round(amplitude, 2),
        })
        print(f"{code} {name}: {close:.2f} {pct:+.2f}% 成交{vol_yi:.1f}亿 换手{turnover:.1f}%")
    except Exception as e:
        print(f"{code} {name}: {e}")

# 按涨跌幅排序
results.sort(key=lambda x: x["pct_chg"], reverse=True)

out = "/workspace/output/hotspot/20260710/aerospace_realtime.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n保存 {len(results)} 只到 {out}")
