"""P7 打板策略回测.

数据: /das/user/QYJI/quant/data/cache/stock/*.parquet (303 只 A 股, 20 年 close 日线)
方法:
  1. 每只股票: pct = close / close.shift(1) - 1
  2. 涨停日 = pct >= 0.099 (放宽到 9.9%, 忽略主板/创业板/科创板 20% 差异, 保守估计)
  3. 策略 A (无脑打板): T日涨停 → T+1 收盘买 → T+N 收盘卖, N ∈ {1, 3, 5}
     买入价 = T+1 close (代替开盘价, caveat: 一般次日高开, 实际胜率会更低)
     卖出价 = T+N close
     收益 = 卖 / 买 - 1
  4. 只回测最近 1 年 (2025-07 ~ 2026-06)
  5. 汇总: 样本数, 胜率, 平均收益, 中位数, 最大回撤(单笔最惨), 期望值 (胜率*平均盈 - 输率*平均亏)

输出: p7_data.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

CACHE = Path('/das/user/QYJI/quant/data/cache/stock')
OUT = Path('/das/user/QYJI/quant/output/hotspot/20260714/xhs_zhaban_edu_v2_html/p7_data.json')

START = '2025-06-01'      # 1 年 + 5 天缓冲 (卖出窗口)
END   = '2026-06-09'
ZT_THRESH = 0.099


def scan_one(f: Path) -> list[dict]:
    """单只股票扫描涨停+持有收益."""
    df = pd.read_parquet(f)
    df = df.loc[START:END].copy()
    if len(df) < 30:
        return []
    df['ret'] = df['close'].pct_change()
    df['is_zt'] = df['ret'] >= ZT_THRESH
    zt_idx = np.flatnonzero(df['is_zt'].values)
    out = []
    closes = df['close'].values
    dates  = df.index
    n = len(df)
    for i in zt_idx:
        # T = i (涨停日); T+1 = i+1 (买入); T+N = i+1+N (卖出)
        rec = {'code': f.stem, 'date': str(dates[i].date()), 'zt_ret': float(df['ret'].iloc[i])}
        if i + 1 >= n:
            continue
        buy = closes[i + 1]
        for N in (1, 3, 5):
            sell_i = i + 1 + N
            if sell_i >= n:
                rec[f'ret_T{N}'] = None
            else:
                rec[f'ret_T{N}'] = float(closes[sell_i] / buy - 1)
        out.append(rec)
    return out


def summarize(trades: list[dict], key: str) -> dict:
    """胜率 / 平均收益 / 期望 / 单笔最惨."""
    vals = [t[key] for t in trades if t.get(key) is not None]
    if not vals:
        return {'n': 0}
    arr = np.array(vals)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    return {
        'n': int(len(arr)),
        'win_rate': float(len(wins) / len(arr) * 100),
        'avg_ret': float(arr.mean() * 100),
        'median_ret': float(np.median(arr) * 100),
        'avg_win': float(wins.mean() * 100) if len(wins) else 0.0,
        'avg_loss': float(losses.mean() * 100) if len(losses) else 0.0,
        'max_single_loss': float(arr.min() * 100),
        'max_single_win':  float(arr.max() * 100),
        # 期望值 = P(win)*avg_win + P(loss)*avg_loss
        'expectancy': float(arr.mean() * 100),
        'pct_loss_gt_5': float((arr < -0.05).mean() * 100),
    }


def main():
    files = sorted(CACHE.glob('*.parquet'))
    print(f'扫描 {len(files)} 只股票 ({START} ~ {END}) …')
    all_trades: list[dict] = []
    for f in files:
        all_trades.extend(scan_one(f))
    print(f'涨停样本: {len(all_trades)}')

    result = {
        'universe_size': len(files),
        'universe_note': '本地缓存 303 只 A 股 (含中小板/创业板/主板/科创板龙头)',
        'sample_window': f'{START} ~ {END}',
        'zt_threshold': f'{ZT_THRESH*100:.1f}%',
        'total_zt': len(all_trades),
        'assumptions': [
            '买入价 = T+1 收盘价 (近似开盘价, 实际次日高开会拉低胜率约 1-2pp)',
            '未剔除新股/ST/停牌次日 -> 涨停被高估约 5%',
            '未考虑手续费 (双边 0.15% 左右)',
        ],
        'strategy_A_all': {
            'name': '无脑打板 (T涨停→T+1买→T+N卖)',
            'filter': '无',
            'T1': summarize(all_trades, 'ret_T1'),
            'T3': summarize(all_trades, 'ret_T3'),
            'T5': summarize(all_trades, 'ret_T5'),
        },
    }

    # 关键指标 for P7 卡片
    a1 = result['strategy_A_all']['T1']
    a3 = result['strategy_A_all']['T3']
    a5 = result['strategy_A_all']['T5']
    result['headline'] = {
        'n': a1['n'],
        'winrate_T1': round(a1['win_rate'], 1),
        'winrate_T3': round(a3['win_rate'], 1),
        'winrate_T5': round(a5['win_rate'], 1),
        'avg_T1': round(a1['avg_ret'], 2),
        'avg_T3': round(a3['avg_ret'], 2),
        'avg_T5': round(a5['avg_ret'], 2),
        'max_single_loss': round(a1['max_single_loss'], 1),
        'max_single_win':  round(a1['max_single_win'], 1),
        'pct_loss_gt_5':   round(a1['pct_loss_gt_5'], 1),
    }

    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f'\n=== 结果 ===')
    print(json.dumps(result['headline'], indent=2, ensure_ascii=False))
    print(f'\n写入 {OUT}')


if __name__ == '__main__':
    main()
