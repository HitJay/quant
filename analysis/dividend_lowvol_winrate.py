"""红利低波胜率分析 — 基于历史回撤后的前瞻收益统计"""

import sys
sys.path.insert(0, "src")

import pandas as pd
import numpy as np

# ============================================================
# 1. 数据获取（新浪源，无需东财API）
# ============================================================
import akshare as ak
from pathlib import Path

CACHE_DIR = Path("./data/cache/etf")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = {
    "512890": ("红利低波ETF", "sh512890"),
    "510880": ("红利ETF", "sh510880"),
    "510300": ("沪深300ETF", "sh510300"),
}


def get_data(symbol: str, name: str, sina_code: str) -> pd.DataFrame | None:
    """获取数据，优先parquet缓存，否则从新浪拉取"""
    cache_path = CACHE_DIR / f"{symbol}.parquet"
    if cache_path.exists():
        df = pd.read_parquet(cache_path)
        if len(df) > 100:
            print(f"  {symbol} ({name}) 从缓存加载, {len(df)} 行")
            return df

    print(f"  {symbol} ({name}) 从新浪拉取...")
    try:
        df = ak.fund_etf_hist_sina(symbol=sina_code)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        df.to_parquet(cache_path)
        print(f"  {symbol} 已缓存, {len(df)} 行")
        return df
    except Exception as e:
        print(f"  ⚠ {symbol} ({name}) 获取失败: {e}")
        return None


print("=" * 60)
print("红利低波 胜率分析")
print("=" * 60)
print("\n[1] 拉取数据...")
data = {}
for sym, (name, sina_code) in SYMBOLS.items():
    df = get_data(sym, name, sina_code)
    if df is not None:
        data[sym] = df

if "512890" not in data:
    print("\n❌ 红利低波ETF(512890)数据获取失败，无法分析")
    sys.exit(1)

# ============================================================
# 2. 当前回撤分析（使用后复权净值）
# ============================================================
print("\n[2] 当前回撤分析...")
close = data["512890"]["close"]
close.index = pd.to_datetime(close.index)

# 新浪数据是未复权的，需要排除除权日重建后复权净值
ret = close.pct_change()
# 除权日：单日跌幅>15%的异常值（红利类ETF分红导致）
ex_div_dates = ret[ret < -0.15].index
if len(ex_div_dates) > 0:
    print(f"  检测到除权日: {[d.strftime('%Y-%m-%d') for d in ex_div_dates]}")
    print(f"  使用后复权净值（排除除权跳水）进行分析")

ret_adj = ret.copy()
ret_adj.iloc[0] = 0  # 第一天无收益
ret_adj[ex_div_dates] = 0  # 除权日收益率归零（分红再投入假设）
nav = (1 + ret_adj).cumprod()

# 用后复权净值计算回撤
peak = nav.expanding().max()
drawdown = (nav - peak) / peak
current_dd = drawdown.iloc[-1]
peak_date = nav.idxmax()
current_date = nav.index[-1]
current_nav = nav.iloc[-1]
peak_nav = peak.iloc[-1]

# 从最高点下跌了多少天
days_since_peak = (current_date - peak_date).days

print(f"  当前净值(后复权): {current_nav:.4f}")
print(f"  历史高点净值: {peak_nav:.4f} ({peak_date.strftime('%Y-%m-%d')})")
print(f"  当前回撤: {current_dd*100:.2f}%")
print(f"  距高点天数: {days_since_peak} 天")
print(f"  总收益(含分红): {(current_nav-1)*100:.1f}%")

# ============================================================
# 3. 历史回撤后的前瞻胜率
# ============================================================
print("\n[3] 历史回撤后胜率分析...")
print("  (当回撤达到当前水平时，未来N个月的正收益概率)")

def forward_returns(prices: pd.Series, periods: list[int]) -> pd.DataFrame:
    """计算每个时间点的前瞻N日收益率"""
    result = {}
    for p in periods:
        result[f"{p}d"] = prices.pct_change(p).shift(-p)
    return pd.DataFrame(result, index=prices.index)

# 计算前瞻收益（基于后复权净值）
periods = [20, 60, 120, 250]  # 1月、3月、6月、1年
fwd = forward_returns(nav, periods)

# 在不同回撤区间的条件胜率
dd_thresholds = [-0.03, -0.05, -0.08, -0.10, -0.15, -0.20]

print(f"\n  {'回撤区间':<12} {'样本数':<8} {'1月胜率':<10} {'3月胜率':<10} {'6月胜率':<10} {'1年胜率':<10} {'1年均值':<10}")
print(f"  {'-'*72}")

for i, thresh in enumerate(dd_thresholds):
    upper = dd_thresholds[i-1] if i > 0 else 0
    mask = (drawdown <= thresh) & (drawdown > (dd_thresholds[i+1] if i+1 < len(dd_thresholds) else -1.0))
    
    n_samples = mask.sum()
    if n_samples < 5:
        continue
    
    row = f"  {thresh*100:>5.0f}%~{upper*100:.0f}%  "
    row += f"{n_samples:<8}"
    
    for col in fwd.columns:
        subset = fwd.loc[mask, col].dropna()
        if len(subset) > 0:
            win_rate = (subset > 0).mean()
            row += f"{win_rate*100:>6.1f}%   "
        else:
            row += f"{'N/A':>6}   "
    
    # 1年均值
    subset_1y = fwd.loc[mask, "250d"].dropna()
    if len(subset_1y) > 0:
        row += f"{subset_1y.mean()*100:>6.1f}%"
    
    print(row)

# 当前回撤所在区间的具体胜率
print(f"\n  ★ 当前回撤 {current_dd*100:.1f}% 对应的历史胜率:")
# 找到当前回撤最接近的区间
current_mask = (drawdown >= current_dd - 0.025) & (drawdown <= current_dd + 0.025)
n_similar = current_mask.sum()
print(f"    相似回撤样本 (±2.5%区间): {n_similar} 个交易日")

if n_similar > 10:
    for col, label in zip(fwd.columns, ["1个月", "3个月", "6个月", "1年"]):
        subset = fwd.loc[current_mask, col].dropna()
        if len(subset) > 0:
            win_rate = (subset > 0).mean()
            avg_ret = subset.mean()
            median_ret = subset.median()
            worst = subset.min()
            best = subset.max()
            print(f"    {label}: 胜率 {win_rate*100:.1f}% | 均值 {avg_ret*100:+.1f}% | 中位数 {median_ret*100:+.1f}% | 最差 {worst*100:+.1f}% | 最好 {best*100:+.1f}%")

# ============================================================
# 4. 净值分位数（后复权）
# ============================================================
print("\n[4] 历史分位数(后复权)...")
# 净值在历史中的位置
pct_rank = (nav <= current_nav).mean()
print(f"  当前净值分位数: {pct_rank*100:.1f}% (历史上有{pct_rank*100:.1f}%的时间净值低于当前)")

# 近1年、3年分位
if len(nav) > 250:
    recent_1y = nav.iloc[-250:]
    rank_1y = (recent_1y <= current_nav).mean()
    print(f"  近1年分位数: {rank_1y*100:.1f}%")
if len(nav) > 750:
    recent_3y = nav.iloc[-750:]
    rank_3y = (recent_3y <= current_nav).mean()
    print(f"  近3年分位数: {rank_3y*100:.1f}%")

# ============================================================
# 5. 动量与趋势
# ============================================================
print("\n[5] 动量与趋势信号(后复权)...")
ma20 = nav.rolling(20).mean().iloc[-1]
ma60 = nav.rolling(60).mean().iloc[-1]
ma120 = nav.rolling(120).mean().iloc[-1]
ma250 = nav.rolling(250).mean().iloc[-1] if len(nav) > 250 else np.nan

print(f"  MA20:  {ma20:.4f} ({'↑' if current_nav > ma20 else '↓'} {'站上' if current_nav > ma20 else '跌破'})")
print(f"  MA60:  {ma60:.4f} ({'↑' if current_nav > ma60 else '↓'} {'站上' if current_nav > ma60 else '跌破'})")
print(f"  MA120: {ma120:.4f} ({'↑' if current_nav > ma120 else '↓'} {'站上' if current_nav > ma120 else '跌破'})")
if not np.isnan(ma250):
    print(f"  MA250: {ma250:.4f} ({'↑' if current_nav > ma250 else '↓'} {'站上' if current_nav > ma250 else '跌破'})")

# 20日动量
mom_20 = (current_nav / nav.iloc[-21] - 1) if len(nav) > 21 else np.nan
mom_60 = (current_nav / nav.iloc[-61] - 1) if len(nav) > 61 else np.nan
print(f"  20日动量: {mom_20*100:+.2f}%")
print(f"  60日动量: {mom_60*100:+.2f}%")

# ============================================================
# 6. 与沪深300对比
# ============================================================
if "510300" in data:
    print("\n[6] 相对沪深300表现(后复权)...")
    hs300 = data["510300"]["close"]
    hs300.index = pd.to_datetime(hs300.index)
    
    # 对齐日期
    common_idx = nav.index.intersection(hs300.index)
    if len(common_idx) > 250:
        c1 = nav.reindex(common_idx)
        c2 = hs300.reindex(common_idx)
        
        # 近1年超额
        excess_1y = (c1.iloc[-1]/c1.iloc[-250] - 1) - (c2.iloc[-1]/c2.iloc[-250] - 1)
        excess_3y = (c1.iloc[-1]/c1.iloc[-750] - 1) - (c2.iloc[-1]/c2.iloc[-750] - 1) if len(common_idx) > 750 else np.nan
        
        print(f"  近1年超额收益(vs沪深300): {excess_1y*100:+.2f}%")
        if not np.isnan(excess_3y):
            print(f"  近3年超额收益(vs沪深300): {excess_3y*100:+.2f}%")

# ============================================================
# 7. 综合结论
# ============================================================
print("\n" + "=" * 60)
print("综合评估")
print("=" * 60)
print(f"""
  回撤深度: {current_dd*100:.1f}%  (距高点 {days_since_peak} 天)
  净值分位: {pct_rank*100:.1f}%
  动量方向: 20日 {mom_20*100:+.1f}% / 60日 {mom_60*100:+.1f}%
  
  基于历史统计的前瞻胜率(回撤约{current_dd*100:.0f}%时买入):
""")

if n_similar > 10:
    for col, label, horizon in zip(fwd.columns, ["1个月", "3个月", "6个月", "1年"], periods):
        subset = fwd.loc[current_mask, col].dropna()
        if len(subset) > 0:
            wr = (subset > 0).mean()
            avg = subset.mean()
            print(f"    {label}胜率: {wr*100:.0f}% (平均收益 {avg*100:+.1f}%)")

print("""
  ⚠ 注意事项:
  1. 历史不代表未来，以上为统计参考
  2. 红利低波适合长期配置，短期择时效果有限
  3. 需结合宏观环境（利率、市场风格）综合判断
""")
