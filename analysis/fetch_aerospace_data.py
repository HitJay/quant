"""拉取商业航天相关个股数据 — 用于卡片量化素材"""
from __future__ import annotations
import sys
import json
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

# 商业航天核心标的
STOCKS = {
    "600118": "中国卫星",
    "002829": "星网宇达",
    "600879": "航天电子",
    "600990": "四创电子",
    "002013": "中航机电",
    "600677": "航天通信",
    "000901": "航天科技",
    "600271": "航天信息",
    "600501": "航天晨光",
    "600151": "航天机电",
    "600118": "中国卫星",
    "300024": "机器人",
    "300053": "欧比特",
    "300565": "科信技术",
    "300101": "振芯科技",
    "300853": "申昊科技",
}

# 商业航天概念股
CONCEPT_STOCKS = {
    "600118": "中国卫星",
    "002829": "星网宇达",
    "600879": "航天电子",
    "600990": "四创电子",
    "000901": "航天科技",
    "600501": "航天晨光",
    "600151": "航天机电",
    "300101": "振芯科技",
    "300053": "欧比特",
    "002013": "中航机电",
}

results = {}

for code, name in CONCEPT_STOCKS.items():
    try:
        # 拉取历史行情
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date="20230601", end_date="20260712", adjust="qfq")
        if df is None or len(df) == 0:
            print(f"{code} {name}: 无数据")
            continue
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').reset_index(drop=True)
        latest = df.iloc[-1]
        close = float(latest['收盘'])
        pct = float(latest['涨跌幅'])
        vol = float(latest['成交额'])
        # 计算 3 年分位
        close_3y = df[df['日期'] >= '2023-07-12']['收盘']
        pct_rank = (close_3y < close).sum() / len(close_3y) * 100
        # 计算距 3 年高低点
        high_3y = float(close_3y.max())
        low_3y = float(close_3y.min())
        dist_high = (close - high_3y) / high_3y * 100
        dist_low = (close - low_3y) / low_3y * 100
        # 20日涨幅
        if len(df) >= 21:
            ret_20d = (close / df.iloc[-21]['收盘'] - 1) * 100
        else:
            ret_20d = 0
        # 60日涨幅
        if len(df) >= 61:
            ret_60d = (close / df.iloc[-61]['收盘'] - 1) * 100
        else:
            ret_60d = 0
        # 5日涨幅
        if len(df) >= 6:
            ret_5d = (close / df.iloc[-6]['收盘'] - 1) * 100
        else:
            ret_5d = 0
        # 换手率 (如果有)
        turnover = float(latest.get('换手率', 0))
        results[code] = {
            "name": name,
            "code": code,
            "close": round(close, 2),
            "pct_chg": round(pct, 2),
            "volume_yi": round(vol / 1e8, 2),
            "pct_rank_3y": round(pct_rank, 1),
            "dist_high_3y": round(dist_high, 1),
            "dist_low_3y": round(dist_low, 1),
            "high_3y": round(high_3y, 2),
            "low_3y": round(low_3y, 2),
            "ret_5d": round(ret_5d, 1),
            "ret_20d": round(ret_20d, 1),
            "ret_60d": round(ret_60d, 1),
            "turnover": round(turnover, 2),
        }
        print(f"{code} {name}: +{pct:.2f}%, 3年分位{pct_rank:.1f}%, 距高{dist_high:.1f}%, 20日{ret_20d:+.1f}%")
    except Exception as e:
        print(f"{code} {name}: 失败 {e}")

# 保存
out = "/workspace/output/hotspot/20260710/aerospace_stocks.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n保存到 {out}")
print(f"共 {len(results)} 只股票")
