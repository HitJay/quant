"""黄金深度分析 — 数据准备 (全量计算 → JSON)."""
import sys
sys.path.insert(0, '/das/user/QYJI/quant/src')
import os
for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(k, None)

import json
from pathlib import Path
import pandas as pd
import numpy as np
from quant.data.fetcher import ETFDataFetcher
from quant.data.cache import Cache

fet = ETFDataFetcher()
cache = Cache()

# ETF 池 (用 ETF 代理黄金股: 159562 黄金股票ETF, 也可以直接用山东黄金 600547)
# ETFDataFetcher 主要拿 ETF, 我们用黄金股票 ETF 替代个股
ETFS = {
    '518880': '黄金ETF',
    '159562': '黄金股票ETF',   # 黄金股 ETF — 跟踪黄金股票指数, 完美代理
    '161226': '白银LOF',
    '511260': '国债10年',
    '510300': '沪深300',
}

DATA = {}
for sym, name in ETFS.items():
    try:
        df = fet.fetch_or_cache(sym, '2013-01-01', '2026-06-23', cache=cache, force=False)
        DATA[name] = df[['close']].rename(columns={'close': name})
        print(f'✓ {sym} {name}: {df.index[0].date()} ~ {df.index[-1].date()} N={len(df)}')
    except Exception as e:
        print(f'✗ {sym} {name}: {e}')

# 对齐
M = pd.concat(DATA.values(), axis=1).sort_index()
M_ffill = M.ffill()

end = M_ffill.index[-1]
OUT = {
    'date': str(end.date()),
    'date_str': end.strftime('%Y-%m-%d'),
    'data_through': str(end.date()),
}

# ─── P1 三大数字 (黄金 ETF 自身) ──────
gold = DATA['黄金ETF']['黄金ETF'].dropna()
high_all = gold.max()
high_dt = gold.idxmax()
cur = gold.iloc[-1]
# 用真实最大回撤 (cummax-based), 不是简单 cur/high_all
cummax = gold.cummax()
dd_series = gold / cummax - 1
max_dd = dd_series.min()           # 真实最大回撤 (历史所有点)
trough_dt = dd_series.idxmin()
# 当前回撤 (从最近峰值算起)
cur_dd = (cur / high_all - 1) * 100

OUT['p1'] = {
    'high_price': round(float(high_all), 3),
    'high_date': high_dt.strftime('%Y-%m-%d'),
    'high_date_human': high_dt.strftime('%Y年%-m月%-d日'),
    'cur_price': round(float(cur), 3),
    'cur_date': end.strftime('%Y-%m-%d'),
    'drawdown_pct': round(float(cur_dd), 1),
    'max_drawdown_pct': round(float(max_dd) * 100, 1),
    'trough_date': trough_dt.strftime('%Y-%m-%d'),
    'trough_human': trough_dt.strftime('%Y年%-m月%-d日'),
    'trough_price': round(float(gold.loc[trough_dt]), 3),
    'days_since_high': (end - high_dt).days,
}

# ─── P2 月度涨跌矩阵 ──────
mo = gold.resample('M').last()
mo_ret = mo.pct_change() * 100
# 取 2024-01 ~ now
mo_data = []
for d, r in mo_ret.loc['2024-01':].dropna().items():
    mo_data.append({
        'month': d.strftime('%Y-%m'),
        'month_short': d.strftime('%-m月') if d.year == end.year else d.strftime('%y/%-m'),
        'ret': round(float(r), 2),
    })

OUT['p2'] = {
    'months': mo_data,
    'best_month': max(mo_data, key=lambda x: x['ret']),
    'worst_month': min(mo_data, key=lambda x: x['ret']),
}

# ─── P3 黄金股 vs 黄金 ETF (单日 + 累计) ──────
gold_stock = DATA['黄金股票ETF']['黄金股票ETF'].dropna()
# 对齐两者公共日期
common = gold.index.intersection(gold_stock.index)
g_etf = gold.loc[common]
g_stk = gold_stock.loc[common]

# 各周期累计涨幅 (公共起始日)
windows = [
    ('近 1 天', 1),
    ('近 1 周', 5),
    ('近 1 月', 21),
    ('近 3 月', 63),
    ('近 1 年', 252),
    ('近 3 年', 252 * 3),
]
p3_compare = []
for wn, wd in windows:
    if wd >= len(g_etf):
        continue
    etf_ret = (g_etf.iloc[-1] / g_etf.iloc[-1-wd] - 1) * 100
    stk_ret = (g_stk.iloc[-1] / g_stk.iloc[-1-wd] - 1) * 100
    p3_compare.append({
        'window': wn,
        'etf_ret': round(float(etf_ret), 2),
        'stk_ret': round(float(stk_ret), 2),
        'gap': round(float(stk_ret - etf_ret), 2),
    })

# 单日数据
today_etf = (g_etf.iloc[-1] / g_etf.iloc[-2] - 1) * 100
today_stk = (g_stk.iloc[-1] / g_stk.iloc[-2] - 1) * 100

OUT['p3'] = {
    'compare': p3_compare,
    'today_etf_ret': round(float(today_etf), 2),
    'today_stk_ret': round(float(today_stk), 2),
    'today_gap': round(float(today_stk - today_etf), 2),
    'common_start': common[0].strftime('%Y-%m-%d'),
}

# ─── P4 横向收益矩阵 ──────
# 用各自最新真实数据 (不强行对齐到 5/27 的国债日期), 但回望窗口用 ffill 容忍滞后
# 关键: 国债 ETF 数据滞后是真实情况, 要么标注要么剔除短期窗口
common4 = M_ffill.dropna()
p4 = []
windows_p4 = [
    ('近 1 月', 21),
    ('近 3 月', 63),
    ('近 6 月', 126),
    ('近 1 年', 252),
    ('近 3 年', 252 * 3),
]
for wn, wd in windows_p4:
    if wd >= len(common4):
        continue
    row = {'window': wn}
    for name in ['黄金ETF', '白银LOF', '国债10年', '沪深300']:
        ret = (common4[name].iloc[-1] / common4[name].iloc[-1-wd] - 1) * 100
        row[name] = round(float(ret), 2)
    p4.append(row)

# 1 年相关性
last1y = common4.tail(252)
ret_daily = last1y.pct_change().dropna()
corr_with_gold = ret_daily.corr()['黄金ETF']
OUT['p4'] = {
    'matrix': p4,
    'corr_1y': {
        name: round(float(corr_with_gold[name]), 3)
        for name in ['白银LOF', '国债10年', '沪深300']
    },
    'gold_vs_hs300_corr': round(float(corr_with_gold['沪深300']), 3),
    'gold_vs_bond_corr': round(float(corr_with_gold['国债10年']), 3),
}

# ─── P5 历史回撤复盘 ──────
# 找历史上从 ATH 回撤 ≥ 20% 的事件 + 回本日期
def find_drawdown_episodes(s, min_dd=0.20):
    """找出从历史新高跌 ≥ min_dd 的事件, 返回 (high_date, trough_date, recover_date, dd, days_to_recover)."""
    cummax = s.cummax()
    dd = s / cummax - 1
    episodes = []

    in_dd = False
    cur_high_date = None
    cur_trough_date = None
    cur_trough_val = 0

    for i, (d, v) in enumerate(dd.items()):
        if not in_dd:
            if v <= -min_dd:
                # 进入回撤
                in_dd = True
                cur_high_date = cummax.iloc[:i+1].idxmax()
                cur_trough_date = d
                cur_trough_val = v
        else:
            # 已经在回撤中
            if v < cur_trough_val:
                cur_trough_val = v
                cur_trough_date = d
            if v >= 0:
                # 回本
                episodes.append({
                    'high_date': cur_high_date,
                    'trough_date': cur_trough_date,
                    'recover_date': d,
                    'max_dd': cur_trough_val,
                    'days_to_recover': (d - cur_high_date).days,
                })
                in_dd = False
                cur_high_date = None

    # 如果当前还在回撤中
    if in_dd:
        episodes.append({
            'high_date': cur_high_date,
            'trough_date': cur_trough_date,
            'recover_date': None,
            'max_dd': cur_trough_val,
            'days_to_recover': None,
        })
    return episodes

eps = find_drawdown_episodes(gold, min_dd=0.20)
p5_eps = []
for e in eps:
    p5_eps.append({
        'high_date': e['high_date'].strftime('%Y-%m-%d') if e['high_date'] else None,
        'high_human': e['high_date'].strftime('%Y年%-m月') if e['high_date'] else None,
        'trough_date': e['trough_date'].strftime('%Y-%m-%d') if e['trough_date'] else None,
        'trough_human': e['trough_date'].strftime('%Y年%-m月') if e['trough_date'] else None,
        'recover_date': e['recover_date'].strftime('%Y-%m-%d') if e['recover_date'] else None,
        'recover_human': e['recover_date'].strftime('%Y年%-m月') if e['recover_date'] else None,
        'max_dd_pct': round(float(e['max_dd']) * 100, 1),
        'days_to_recover': e['days_to_recover'],
        'is_current': e['recover_date'] is None,
    })

OUT['p5'] = {
    'episodes': p5_eps,
    'history_avg_recover_days': int(np.mean([e['days_to_recover'] for e in p5_eps if e['days_to_recover']])) if any(e['days_to_recover'] for e in p5_eps) else None,
}

# ─── P6 当前买点判断 (MA200 + 距低点 + RSI) ──────
ma200 = gold.rolling(200).mean()
ma50 = gold.rolling(50).mean()

# RSI(14)
delta = gold.diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
rsi = 100 - 100 / (1 + rs)

cur_rsi = float(rsi.iloc[-1])
cur_ma200 = float(ma200.iloc[-1])
cur_ma50 = float(ma50.iloc[-1])
cur_price = float(gold.iloc[-1])

# 1 年低点
low1y = float(gold.tail(252).min())
low1y_dt = gold.tail(252).idxmin()
dist_to_low1y = (cur_price / low1y - 1) * 100

# 价格距 MA200 / MA50
dist_ma200 = (cur_price / cur_ma200 - 1) * 100
dist_ma50 = (cur_price / cur_ma50 - 1) * 100

OUT['p6'] = {
    'cur_price': round(cur_price, 3),
    'ma200': round(cur_ma200, 3),
    'ma50': round(cur_ma50, 3),
    'dist_ma200_pct': round(dist_ma200, 1),
    'dist_ma50_pct': round(dist_ma50, 1),
    'rsi14': round(cur_rsi, 1),
    'low1y': round(low1y, 3),
    'low1y_date': low1y_dt.strftime('%Y-%m-%d'),
    'low1y_human': low1y_dt.strftime('%Y年%-m月%-d日'),
    'dist_to_low1y_pct': round(dist_to_low1y, 1),
    'high_all': round(float(high_all), 3),
    'dist_to_high_pct': round(cur_dd, 1),
    # 60d 价格序列 (给图表)
    'price_60d': [
        {'d': d.strftime('%m-%d'), 'p': round(float(v), 3),
         'ma200': round(float(ma200.loc[d]), 3) if pd.notna(ma200.loc[d]) else None,
         'ma50': round(float(ma50.loc[d]), 3) if pd.notna(ma50.loc[d]) else None}
        for d, v in gold.tail(60).items()
    ],
}

# ─── 保存 ──────
outdir = Path('/das/user/QYJI/quant/output/research/gold_deepdive_v1')
outdir.mkdir(parents=True, exist_ok=True)
out_path = outdir / 'data.json'
out_path.write_text(json.dumps(OUT, ensure_ascii=False, indent=2))
print(f'\n✓ 数据已落盘: {out_path}')
print(f'  P1 黄金ETF 距 ATH: {OUT["p1"]["drawdown_pct"]}%')
print(f'  P2 月度数据: {len(mo_data)} 个月')
print(f'  P3 周期对比: {len(p3_compare)} 行')
print(f'  P4 横向矩阵: {len(p4)} 行')
print(f'  P5 历史回撤: {len(p5_eps)} 次 (含当前)')
print(f'  P6 MA200={OUT["p6"]["ma200"]}, RSI={OUT["p6"]["rsi14"]}, 距 1Y 低 +{OUT["p6"]["dist_to_low1y_pct"]}%')
