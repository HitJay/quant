#!/data/user/QYJI/miniforge3/envs/research/bin/python
"""赛力斯(601127) 量化分析脚本"""
import pandas as pd
import numpy as np
import akshare as ak
import requests
import warnings
warnings.filterwarnings('ignore')

# ========= 1. 赛力斯全历史分析 =========
print("正在拉取赛力斯(601127)日线数据 ...")
df = ak.stock_zh_a_daily(symbol='sh601127', adjust='qfq')
df = df.sort_values('date').reset_index(drop=True)

latest = df.iloc[-1]
ath = df['close'].max()
ath_idx = df['close'].idxmax()
ath_date = df.loc[ath_idx, 'date']

# 当前回撤
cur_dd = latest['close'] / ath - 1
print(f"\n{'='*55}")
print(f"【赛力斯 601127】2026-07-20 量化诊断")
print(f"{'='*55}")
print(f"数据范围: {df.date.iloc[0]} ~ {df.date.iloc[-1]} ({len(df)}天)")
print(f"")

# 近期走势
n90 = df.tail(90)
n90_ret = (latest['close'] / n90.iloc[0]['close'] - 1) * 100
y252 = df.tail(252) if len(df) >= 252 else df
y1_ret = (latest['close'] / y252.iloc[0]['close'] - 1) * 100
w52_high = y252['close'].max()
w52_low = y252['close'].min()
pct_from_52w_high = (latest['close'] / w52_high - 1) * 100

print(f"  ╔═══════════════════════╤═══════════════╗")
print(f"  ║ 指标                 │ 数值          ║")
print(f"  ╟───────────────────────┼───────────────╢")
print(f"  ║ 当前价              │ {latest['close']:<13.2f}║")
print(f"  ║ 历史最高(ATH)       │ {ath:<13.2f} ({ath_date})║")
print(f"  ║ 距ATH回撤           │ {cur_dd*100:<12.1f}%       ║")
print(f"  ║ 52周最高            │ {w52_high:<13.2f}║")
print(f"  ║ 距52周高            │ {pct_from_52w_high:<11.1f}%       ║")
print(f"  ║ 52周最低            │ {w52_low:<13.2f}║")
print(f"  ║ 52周振幅            │ {(w52_high/w52_low-1)*100:<11.1f}%       ║")
print(f"  ║ 近90日涨跌          │ {n90_ret:<12.1f}%       ║")
print(f"  ║ 近1年涨跌           │ {y1_ret:<12.1f}%       ║")
print(f"  ╚═══════════════════════╧═══════════════╝")

# 上周暴跌
print(f"\n【上周走势: 从59.9到54.3】")
jul10 = df[df.date == '2026-07-10']
jul13 = df[df.date == '2026-07-13']
jul17 = df[df.date == '2026-07-17']
if len(jul10) > 0 and len(jul13) > 0 and len(jul17) > 0:
    mon_drop = (jul13.close.iloc[0] / jul10.close.iloc[0] - 1) * 100
    week_drop = (jul17.close.iloc[0] / jul10.close.iloc[0] - 1) * 100
    print(f"  7/10(五)收盘: {jul10.close.iloc[0]:.2f}")
    print(f"  7/13(一): {jul13.close.iloc[0]:.2f} (单日跳水 {mon_drop:.1f}%)")
    print(f"  7/17(五)收盘: {jul17.close.iloc[0]:.2f}")
    print(f"  当周累计: {week_drop:.1f}% (近90日中最大单周跌幅)")
    # 成交额放大
    avg_vol = df.tail(60)['amount'].mean()
    week_vol = df[(df.date >= '2026-07-13') & (df.date <= '2026-07-17')]['amount'].mean()
    print(f"  周均成交额: {week_vol/1e8:.1f}亿 (vs 60日均 {avg_vol/1e8:.1f}亿, {'放量' if week_vol > avg_vol*1.3 else '正常'}!)")

# 波动率
ret = df['close'].pct_change().dropna()
vol_20d = ret.tail(20).std() * np.sqrt(252) * 100
vol_60d = ret.tail(60).std() * np.sqrt(252) * 100
print(f"\n【波动率】")
print(f"  20日年化波动率: {vol_20d:.1f}%")
print(f"  60日年化波动率: {vol_60d:.1f}%")
print(f"  对比: 沪深300长期年化波动~20-25%")
print(f"  结论: {'极端高波动' if vol_20d > 60 else '高波动' if vol_20d > 40 else '中等偏上'}")

# ========= 2. 重大回撤事件 =========
print(f"\n【历史大回撤事件】")
peak = df['close'].expanding().max()
dd = df['close'] / peak - 1
max_dd = dd.min()
max_dd_idx = dd.idxmin()
max_dd_date = df.loc[max_dd_idx, 'date']
print(f"  历史最深回撤: {max_dd*100:.1f}% ({max_dd_date})")

# 找到最近 >20% 的回撤事件
big_dd_mask = dd < -0.20
events = []
in_event = False
start = None
for i in range(len(df)):
    if dd.iloc[i] < -0.20 and not in_event:
        in_event = True
        start = i
    elif dd.iloc[i] >= -0.20 and in_event:
        events.append({
            'start': str(df.loc[start, 'date']),
            'end': str(df.loc[i-1, 'date']),
            'depth': round(dd.iloc[i-1]*100, 1),
            'days': i - start,
            'bottom': df.loc[i-1, 'close']
        })
        in_event = False
if in_event:
    events.append({
        'start': str(df.loc[start, 'date']),
        'end': str(df.loc[len(df)-1, 'date']),
        'depth': round(dd.iloc[len(df)-1]*100, 1),
        'days': len(df) - start,
        'bottom': df.loc[len(df)-1, 'close']
    })

print(f"  历史上共{len(events)}次回撤超过20%")
for e in events[-5:]:
    rec_pct = round((latest['close'] / e['bottom'] - 1) * 100, 1)
    print(f"  🔴 {e['start']} ~ {e['end']}")
    print(f"     最深回撤 {e['depth']}% 持续 {e['days']} 天")
    print(f"     从坑底反弹至今日: {rec_pct:+.1f}%")
    print()

# ========= 3. 板块对比 =========
print(f"\n【板块对比: 申万汽车指数 vs 赛力斯】")
try:
    auto_idx = ak.index_hist_sw(symbol="801880")
    auto_idx = auto_idx.sort_values('date').reset_index(drop=True)
    auto_y = auto_idx.tail(252)
    auto_y1_ret = (auto_y['close'].iloc[-1] / auto_y['close'].iloc[0] - 1) * 100

    # 本周板块 vs 赛力斯
    auto_recent = auto_idx.tail(20)
    print(f"  申万汽车指数(801880) 近1年: {auto_y1_ret:+.1f}%")
    print(f"  赛力斯 近1年: {y1_ret:+.1f}%")
    gap = y1_ret - auto_y1_ret
    if abs(gap) > 5:
        print(f"  差距: {gap:+.1f}pp — 赛力斯{'远跑赢' if gap > 5 else '远跑输'}汽车板块,个股独立走势明显")
    else:
        print(f"  差距: {gap:+.1f}pp — 赛力斯与板块走势基本一致")
except Exception as e:
    print(f"  汽车板块数据异常: {e}")

# ========= 4. 近期概念板块情况 =========
print(f"\n【今日新能源汽车/汽车概念板块行情】")
try:
    r = requests.get(
        "https://push2.eastmoney.com/api/qt/clist/get",
        params={"pn": "1", "pz": "500", "po": "1", "np": "1",
                "fs": "m:90 t:3 f:!50", "fields": "f12,f14,f3,f62,f184"},
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                 "Referer": "https://quote.eastmoney.com/"},
        timeout=15)
    data = r.json().get("data", {}).get("diff", [])
    rel_concepts = [x for x in data if any(k in x.get('f14','') for k in ['新能源车','汽车','整车','华为','无人驾驶'])]
    for c in rel_concepts[:8]:
        pct = c['f3']/100
        inflow = c.get('f62', 0)/1e8
        print(f"  {c['f14']:　<12} 涨幅 {pct:>+6.2f}%  主力净入 {inflow:>+7.1f}亿")
    if not rel_concepts:
        print(f"  未找到相关板块 (push2返回空, 可能接口抖动)")
except Exception as e:
    print(f"  概念板块数据不可用: {e}")

# ========= 5. 极端点位入场胜率 =========
print(f"\n【当前位置定性 —— 极端回撤入场历史胜率】")
# 当前位置已从ATH跌 -62.9%, 找历史上同等回撤深度入场的情况
threshold = -0.60  # 当前约-62.9%
deep_dd = dd[dd < threshold]
print(f"  当前回撤: {cur_dd*100:.1f}%")
print(f"  历史上回撤超过60%的交易日: {len(deep_dd)} 天")

# 把这些深坑位置后的后续表现拉出来
if len(deep_dd) > 0:
    horizons = [5, 20, 60, 120, 250]
    print(f"\n  深坑入场后前瞻回报 (回撤<-60%时买入持有):")
    print(f"  {'持有期':<10} {'样本数':<8} {'胜率':<8} {'中位数':<10} {'均值':<10}")
    print(f"  {'-'*46}")
    vals = df['close'].values
    entries = [df.index.get_loc(dd[dd < threshold].index[i]) for i in range(len(deep_dd))]
    for h in horizons:
        fwd = []
        for idx in entries:
            if idx + h < len(vals):
                fwd.append(vals[idx + h] / vals[idx] - 1)
        fwd = np.array(fwd)
        if len(fwd) > 0:
            wr = (fwd > 0).mean() * 100
            md = np.median(fwd) * 100
            mn = fwd.mean() * 100
            print(f"  {'T+'+str(h):<10} {len(fwd):<8} {wr:<7.1f}% {md:<+8.1f}% {mn:<+8.1f}%")
    
    # 最极端那一次
    worst_idx = dd.idxmin()
    worst_close = df.loc[worst_idx, 'close']
    worst_date = df.loc[worst_idx, 'date']
    # 从最低点到现在
    if worst_idx < len(df) - 1:
        recovery = (df['close'].iloc[-1] / worst_close - 1) * 100
        recovery_days = len(df) - 1 - worst_idx
        print(f"\n  最深坑({worst_date}): 价{worst_close:.2f}")
        print(f"  至今{recovery_days}天, 反弹{recovery:+.1f}% {'(还没回本)' if recovery <= 0 else '(从坑底爬出来了)'}")

print(f"\n{'='*55}")
print("分析完毕")
