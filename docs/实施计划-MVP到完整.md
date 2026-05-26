# Quant 框架实施计划 — MVP + 完整开发

> 原则：TDD驱动、每步smoke test、MVP优先、小步提交
> 策略：先跑通ETF轮动一条链路，再横向扩展

---

## MVP 目标

> 用 AKShare 获取宽基ETF数据 → 计算3个月动量 → 持有动量最强ETF → 回测输出净值曲线

---

## Phase 0：环境准备（一次性）

### Task 0.1：安装依赖

```bash
pip install akshare pandas numpy matplotlib pytest
```

**Smoke Test：**
```python
import akshare as ak
print(ak.__version__)
# 预期：打印版本号，无报错
```

### Task 0.2：项目目录初始化

```bash
mkdir -p src/quant/{data,universe,factors,strategies,backtest,portfolio,monitor}
touch src/quant/__init__.py
touch src/quant/{data,universe,factors,strategies,backtest,portfolio,monitor}/__init__.py
```

**Smoke Test：**
```bash
python -c "from quant.data import fetcher; print('import ok')"
# 预期：无报错（即使fetcher.py还不存在，目录存在即可）
```

---

## Phase 1：数据层 `data/`

### Task 1.1：获取单只ETF历史数据

**文件：** `src/quant/data/fetcher.py`

**TDD — Step 1：写测试**

`tests/test_fetcher.py`：
```python
import pytest
from quant.data.fetcher import ETFDataFetcher

def test_fetch_single_etf():
    fetcher = ETFDataFetcher()
    df = fetcher.fetch("510300", start="2024-01-01", end="2024-06-30")
    assert df is not None
    assert len(df) > 50
    assert "收盘" in df.columns or "close" in df.columns
```

**Step 2：跑测试 → FAIL**

```bash
pytest tests/test_fetcher.py -v
# 预期：FAIL — ETFDataFetcher 不存在
```

**Step 3：实现**

```python
# src/quant/data/fetcher.py
import akshare as ak
import pandas as pd

class ETFDataFetcher:
    """ETF数据获取器"""
    
    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """获取单只ETF历史日线数据（后复权）"""
        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="hfq"  # 后复权
        )
        # 标准化列名
        df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
        }, inplace=True)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df
```

**Step 4：跑测试 → PASS**

```bash
pytest tests/test_fetcher.py -v
# 预期：PASS
```

**Smoke Test：**
```bash
python -c "
from quant.data.fetcher import ETFDataFetcher
f = ETFDataFetcher()
df = f.fetch('510300', '2024-01-01', '2024-03-31')
print(f'获取到 {len(df)} 条数据')
print(f'日期范围: {df.index[0]} ~ {df.index[-1]}')
print(f'列: {list(df.columns)}')
"
# 预期：打印 50+ 条数据，列包含 open/high/low/close/volume
```

---

### Task 1.2：本地Parquet缓存

**文件：** `src/quant/data/cache.py`

**TDD — Step 1：写测试**

`tests/test_cache.py`：
```python
import tempfile, os
import pandas as pd
from quant.data.cache import Cache

def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(cache_dir=tmpdir)
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0]}, index=pd.date_range("2024-01-01", periods=3))
        cache.save(df, "test_etf", "510300")
        
        loaded = cache.load("test_etf", "510300")
        assert loaded is not None
        assert len(loaded) == 3
        assert loaded["close"].tolist() == [1.0, 2.0, 3.0]

def test_load_missing_returns_none():
    cache = Cache(cache_dir="/tmp/nonexistent_quant_cache")
    result = cache.load("nonexistent", "999999")
    assert result is None
```

**Step 2：跑测试 → FAIL**

**Step 3：实现**

```python
# src/quant/data/cache.py
import pandas as pd
from pathlib import Path

class Cache:
    """本地Parquet缓存"""
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _path(self, asset_type: str, symbol: str) -> Path:
        return self.cache_dir / asset_type / f"{symbol}.parquet"
    
    def save(self, df: pd.DataFrame, asset_type: str, symbol: str):
        path = self._path(asset_type, symbol)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path)
    
    def load(self, asset_type: str, symbol: str) -> pd.DataFrame | None:
        path = self._path(asset_type, symbol)
        if not path.exists():
            return None
        return pd.read_parquet(path)
```

**Step 4：跑测试 → PASS**

**Smoke Test：**
```bash
python -c "
from quant.data.cache import Cache
import pandas as pd

cache = Cache('./data/cache')
df = pd.DataFrame({'close': [1,2,3]}, index=pd.date_range('2024-01-01', periods=3))
cache.save(df, 'etf', '510300')
loaded = cache.load('etf', '510300')
print(f'缓存测试通过: {len(loaded)} 条')
"
```

---

### Task 1.3：Fetcher + Cache 集成

**文件：** 修改 `src/quant/data/fetcher.py`

添加 `fetch_or_cache` 方法：先读缓存，缓存未命中再拉取。

**TDD — Step 1：写测试**

`tests/test_fetcher.py` 添加：
```python
def test_fetch_or_cache():
    cache = MagicMock()
    cache.load.return_value = None  # 缓存未命中
    
    fetcher = ETFDataFetcher(cache=cache)
    df = fetcher.fetch_or_cache("510300", "2024-01-01", "2024-03-31")
    
    assert len(df) > 0
    cache.save.assert_called_once()
```

**Step 2：实现**
```python
def fetch_or_cache(self, symbol, start, end, force=False):
    if not force:
        cached = self.cache.load("etf", symbol)
        if cached is not None:
            return cached
    df = self.fetch(symbol, start, end)
    self.cache.save(df, "etf", symbol)
    return df
```

**Smoke Test：**
```bash
python -c "
from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher

cache = Cache('./data/cache')
fetcher = ETFDataFetcher(cache=cache)
df1 = fetcher.fetch_or_cache('510300', '2024-01-01', '2024-03-31')
df2 = fetcher.fetch_or_cache('510300', '2024-01-01', '2024-03-31')
print(f'第一次拉取: {len(df1)} 条, 第二次命中缓存: {len(df2)} 条')
"
```

---

## Phase 2：标的管理 `universe/`

### Task 2.1：ETF分类映射表

**文件：** `src/quant/universe/etf_map.py`

**TDD — Step 1：写测试**

`tests/test_etf_map.py`：
```python
from quant.universe.etf_map import ETF_MAP, get_etf_list

def test_wide_etfs_not_empty():
    wide = get_etf_list("WIDE")
    assert len(wide) >= 3
    assert "510300" in wide  # 沪深300

def test_all_categories_covered():
    for cat in ["WIDE", "INDUSTRY", "BOND", "COMMODITY", "CROSS", "MONEY", "STRATEGY"]:
        etfs = get_etf_list(cat)
        assert len(etfs) > 0, f"Category {cat} should not be empty"
```

**Step 2：实现**

```python
# src/quant/universe/etf_map.py
ETF_MAP = {
    "WIDE": {
        "510300": "沪深300ETF",
        "510500": "中证500ETF",
        "510050": "上证50ETF",
        "159949": "创业板50",
        "588000": "科创50ETF",
    },
    "INDUSTRY": {
        "512880": "证券ETF",
        "512690": "酒ETF",
        "159995": "芯片ETF",
        "516160": "新能源ETF",
    },
    "STRATEGY": {
        "510880": "红利ETF",
        "512100": "中证1000ETF",
        "512890": "红利低波ETF",
    },
    "BOND": {
        "511010": "国债ETF",
        "511260": "10年国债ETF",
        "511380": "可转债ETF",
    },
    "COMMODITY": {
        "518880": "黄金ETF",
        "159985": "豆粕ETF",
        "159866": "有色金属ETF",
    },
    "CROSS": {
        "513100": "纳指ETF",
        "159920": "恒生ETF",
    },
    "MONEY": {
        "511990": "华宝添益",
    },
}

def get_etf_list(category: str) -> list[str]:
    """获取指定分类的ETF代码列表"""
    return list(ETF_MAP.get(category, {}).keys())

def get_all_etfs(categories: list[str] | None = None) -> dict[str, str]:
    """获取所有ETF（或指定分类）的 {代码: 名称} 映射"""
    if categories is None:
        categories = list(ETF_MAP.keys())
    result = {}
    for cat in categories:
        result.update(ETF_MAP.get(cat, {}))
    return result
```

**Smoke Test：**
```bash
python -c "
from quant.universe.etf_map import get_etf_list, get_all_etfs
print('宽基ETF:', get_etf_list('WIDE'))
print('商品ETF:', get_etf_list('COMMODITY'))
print('总计:', len(get_all_etfs()), '只ETF')
"
```

---

## Phase 3：因子库 `factors/`

### Task 3.1：动量因子

**文件：** `src/quant/factors/momentum.py`

**TDD — Step 1：写测试**

`tests/test_factors_momentum.py`：
```python
import pandas as pd
import numpy as np
from quant.factors.momentum import momentum

def test_momentum_upward():
    # 模拟上涨：从10涨到15，窗口=5天
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    result = momentum(prices, window=5)
    assert result > 0.3
    assert abs(result - 0.5) < 0.01  # (15-10)/10 = 0.5

def test_momentum_downward():
    prices = pd.Series([15.0, 14.0, 13.0, 12.0, 11.0, 10.0])
    result = momentum(prices, window=5)
    assert result < -0.2
```

**Step 2：实现**

```python
# src/quant/factors/momentum.py
import pandas as pd
import numpy as np

def momentum(prices: pd.Series, window: int = 63) -> float:
    """计算动量：过去window天的收益率
    window=63为约3个月（交易日）
    """
    if len(prices) < window + 1:
        return np.nan
    return (prices.iloc[-1] / prices.iloc[-(window + 1)]) - 1.0

def momentum_scores(price_df, symbols, date, window=63):
    """批量计算多个标的的动量得分"""
    scores = {}
    for sym in symbols:
        if sym not in price_df.columns:
            continue
        close = price_df[sym].dropna()
        if len(close) >= window + 1:
            scores[sym] = momentum(close.iloc[-(window + 1):], window)
    return scores
```

**Smoke Test：**
```bash
python -c "
import pandas as pd
from quant.factors.momentum import momentum, momentum_scores

# 单因子测试
s = pd.Series([10, 10.5, 11, 11.5, 12, 12.5])
print('动量(5d):', momentum(s, window=5))

# 批量测试
prices = pd.DataFrame({
    'A': [10, 10.5, 11, 11.5, 12, 12.5, 13],
    'B': [10, 9.5, 9, 8.5, 8, 7.5, 7],
})
scores = momentum_scores(prices, ['A', 'B'], None, window=5)
print('A动量:', round(scores['A'], 3), '| B动量:', round(scores['B'], 3))
"
# 预期：A动量正、B动量负
```

---

## Phase 4：MVP 策略 `strategies/` ＋ 回测 `backtest/`

### Task 4.1：策略基类 + Signal

**文件：** `src/quant/strategies/base.py`

```python
from dataclasses import dataclass

@dataclass
class Signal:
    date: str
    weights: dict[str, float]

class Strategy:
    def rebalance(self, date, universe, data) -> Signal:
        raise NotImplementedError
```

---

### Task 4.2：ETF 动量轮动策略

**文件：** `src/quant/strategies/etf_rotation.py`

**TDD — Step 1：写测试**

`tests/test_etf_rotation.py`：
```python
import pandas as pd
import numpy as np
from quant.strategies.etf_rotation import ETF_Rotation

def make_mock_prices():
    """模拟两只ETF 200天价格：
    A: 从10涨到20（强动量）
    B: 从10跌到8（弱动量）
    """
    dates = pd.date_range("2024-01-01", periods=200, freq="B")
    a = np.linspace(10, 20, 200) + np.random.normal(0, 0.2, 200)
    b = np.linspace(10, 8, 200) + np.random.normal(0, 0.1, 200)
    return pd.DataFrame({"A": a, "B": b}, index=dates)

def test_etf_rotation_picks_strongest():
    prices = make_mock_prices()
    strategy = ETF_Rotation(momentum_window=63, hold_n=1)
    signal = strategy.rebalance(
        date=prices.index[-1],
        symbols=["A", "B"],
        prices=prices
    )
    assert "A" in signal.weights
    assert signal.weights.get("A", 0) > 0.5  # A应该占主导
```

**Step 2：实现**

```python
# src/quant/strategies/etf_rotation.py
from quant.strategies.base import Strategy, Signal
from quant.factors.momentum import momentum_scores

class ETF_Rotation(Strategy):
    def __init__(self, momentum_window=63, hold_n=2):
        self.momentum_window = momentum_window
        self.hold_n = hold_n
    
    def rebalance(self, date, symbols, prices) -> Signal:
        scores = momentum_scores(prices, symbols, date, self.momentum_window)
        ranked = sorted(scores, key=scores.get, reverse=True)
        top = ranked[:self.hold_n]
        weight = 1.0 / len(top)
        weights = {s: weight for s in top}
        return Signal(date=str(date), weights=weights)
```

**Smoke Test：**
```bash
python -c "
import pandas as pd; import numpy as np
from quant.strategies.etf_rotation import ETF_Rotation

dates = pd.date_range('2024-01-01', periods=100, freq='B')
prices = pd.DataFrame({
    'ETF_A': np.linspace(10, 15, 100) + np.random.normal(0,0.3,100),
    'ETF_B': np.linspace(10, 12, 100) + np.random.normal(0,0.3,100),
    'ETF_C': np.linspace(10, 8,  100) + np.random.normal(0,0.3,100),
})
s = ETF_Rotation(momentum_window=63, hold_n=2)
signal = s.rebalance(dates[-1], ['ETF_A','ETF_B','ETF_C'], prices)
print(f'选中: {signal.weights}')
"
# 预期：选中 ETF_A 和 ETF_B
```

---

### Task 4.3：回测引擎

**文件：** `src/quant/backtest/engine.py`

**TDD — Step 1：写测试**

`tests/test_backtest_engine.py`：
```python
import pandas as pd
import numpy as np
from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.strategies.base import Signal

def make_mock_strategy():
    class MockStrategy:
        def rebalance(self, date, symbols, prices):
            return Signal(date=str(date), weights={"A": 1.0})
    return MockStrategy()

def make_mock_prices():
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    return pd.DataFrame({
        "A": np.linspace(100, 120, 100),
        "CASH": np.ones(100),  # 货币ETF，价格恒为1
    }, index=dates)

def test_backtest_positive_return():
    prices = make_mock_prices()
    strategy = make_mock_strategy()
    config = BacktestConfig(initial_capital=100000, etf_commission=0)
    
    engine = BacktestEngine(config)
    result = engine.run(strategy, prices, symbols=["A", "CASH"])
    
    assert result.total_return > 0.1  # 涨了20%应该有正收益
    assert result.nav_series.iloc[-1] > 100000
```

**Step 2：实现**

```python
# src/quant/backtest/engine.py
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

@dataclass
class BacktestConfig:
    initial_capital: float = 1_000_000
    etf_commission: float = 0.0001  # 万分之一
    stamp_duty: float = 0.0005      # 印花税
    stock_commission: float = 0.0003
    min_commission: float = 5
    slippage: float = 0.001
    cash_symbol: str = "CASH"

@dataclass
class BacktestResult:
    nav_series: pd.Series
    positions: pd.DataFrame
    trades: list
    initial_capital: float
    
    @property
    def final_value(self) -> float:
        return self.nav_series.iloc[-1]
    
    @property
    def total_return(self) -> float:
        return self.final_value / self.initial_capital - 1

class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
    
    def run(self, strategy, prices, symbols) -> BacktestResult:
        dates = prices.index
        nav = pd.Series(index=dates, dtype=float)
        positions = pd.DataFrame(0.0, index=dates, columns=symbols)
        trades = []
        
        cash = self.config.initial_capital
        holdings = {s: 0.0 for s in symbols}
        holdings[self.config.cash_symbol] = cash
        
        for i, date in enumerate(dates):
            # 生成信号（月度调仓，只在月初执行）
            if i == 0 or date.month != dates[i-1].month:
                signal = strategy.rebalance(date, symbols, prices.loc[:date])
                target_weights = signal.weights
            
            # 计算目标持仓
            current_prices = {s: prices.loc[date, s] for s in symbols}
            total_value = sum(
                holdings[s] * current_prices.get(s, holdings.get(s, 0))
                for s in holdings
            )
            
            # 记录净值
            nav[date] = total_value
            
            # 记录持仓
            for s in symbols:
                positions.loc[date, s] = holdings.get(s, 0)
        
        # 确保CASH也被追踪
        # nav中已包含cash
        
        return BacktestResult(
            nav_series=nav,
            positions=positions,
            trades=trades,
            initial_capital=self.config.initial_capital
        )
```

**Smoke Test：**
```bash
python -c "
import pandas as pd; import numpy as np
from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.strategies.etf_rotation import ETF_Rotation

# 模拟数据
dates = pd.date_range('2024-01-01', periods=100, freq='B')
np.random.seed(42)
prices = pd.DataFrame({
    'ETF_A': np.cumprod(1 + np.random.normal(0.001, 0.015, 100)),
    'ETF_B': np.cumprod(1 + np.random.normal(0.0005, 0.01, 100)),
    'CASH': np.ones(100),
}, index=dates) * 100

config = BacktestConfig(initial_capital=1000000, etf_commission=0)
strategy = ETF_Rotation(momentum_window=20, hold_n=1)
engine = BacktestEngine(config)
result = engine.run(strategy, prices, ['ETF_A', 'ETF_B', 'CASH'])

print(f'最终净值: {result.final_value:.2f}')
print(f'总收益: {result.total_return*100:.2f}%')
print(f'净值曲线前5: {result.nav_series.head().tolist()}')
print(f'净值曲线后5: {result.nav_series.tail().tolist()}')
"
# 预期：打印净值数据，正常运行
```

---

### Task 4.4：绩效指标

**文件：** `src/quant/backtest/metrics.py`

```python
import pandas as pd
import numpy as np

def annual_return(nav: pd.Series) -> float:
    """年化收益率"""
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    total = nav.iloc[-1] / nav.iloc[0] - 1
    return (1 + total) ** (1 / years) - 1

def max_drawdown(nav: pd.Series) -> float:
    """最大回撤"""
    peak = nav.expanding().max()
    dd = (nav - peak) / peak
    return abs(dd.min())

def sharpe(nav: pd.Series, risk_free=0.02) -> float:
    """夏普比率"""
    daily_ret = nav.pct_change().dropna()
    excess = daily_ret.mean() * 252 - risk_free
    vol = daily_ret.std() * np.sqrt(252)
    return excess / vol if vol > 0 else 0

def calmar(nav: pd.Series) -> float:
    """卡玛比率"""
    ann = annual_return(nav)
    mdd = max_drawdown(nav)
    return ann / mdd if mdd > 0 else 0
```

**Smoke Test：**
```bash
python -c "
import pandas as pd; import numpy as np
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, calmar

# 模拟净值：年化8%波动15%
dates = pd.date_range('2020-01-01', periods=1260, freq='B')
np.random.seed(42)
ret = np.random.normal(0.08/252, 0.15/np.sqrt(252), 1260)
nav = pd.Series(np.cumprod(1+ret), index=dates) * 100

print(f'年化收益: {annual_return(nav)*100:.2f}%')
print(f'最大回撤: {max_drawdown(nav)*100:.2f}%')
print(f'夏普比率: {sharpe(nav):.2f}')
print(f'卡玛比率: {calmar(nav):.2f}')
"
```

---

### 🏁 MVP 端到端 Smoke Test

```bash
python -c "
import pandas as pd
import numpy as np
from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher
from quant.universe.etf_map import get_etf_list
from quant.strategies.etf_rotation import ETF_Rotation
from quant.backtest.engine import BacktestEngine, BacktestConfig
from quant.backtest.metrics import annual_return, max_drawdown, sharpe

# 1. 获取真实数据
cache = Cache('./data/cache')
fetcher = ETFDataFetcher(cache=cache)
symbols = get_etf_list('WIDE')
print(f'宽基ETF: {symbols}')

all_data = {}
for sym in symbols[:3]:  # MVP只取前3只
    try:
        df = fetcher.fetch_or_cache(sym, '2023-01-01', '2025-12-31')
        all_data[sym] = df['close']
        print(f'  {sym}: {len(df)} 条')
    except Exception as e:
        print(f'  {sym}: 获取失败 - {e}')

if len(all_data) < 2:
    print('数据不足，跳过回测')
else:
    # 构建价格矩阵
    prices = pd.DataFrame(all_data)
    prices['CASH'] = 1.0  # 现金等价物
    
    # 运行策略
    strategy = ETF_Rotation(momentum_window=63, hold_n=1)
    config = BacktestConfig(initial_capital=1000000, etf_commission=0.0001)
    engine = BacktestEngine(config)
    result = engine.run(strategy, prices, list(all_data.keys()) + ['CASH'])
    
    print(f'\n=== 回测结果 ===')
    print(f'初始资金: {config.initial_capital:,.0f}')
    print(f'最终净值: {result.final_value:,.0f}')
    print(f'总收益: {result.total_return*100:.2f}%')
    print(f'年化收益: {annual_return(result.nav_series)*100:.2f}%')
    print(f'最大回撤: {max_drawdown(result.nav_series)*100:.2f}%')
    print(f'夏普比率: {sharpe(result.nav_series):.2f}')
"
```

**MVP完成标志：** 上述脚本跑通，输出真实回测结果！

---

## Phase 5-8：完整开发（MVP后再做）

### Phase 5：更多因子

| Task | 文件 | 说明 |
|------|------|------|
| 5.1 | `factors/stock/value.py` | PE/PB/PS/股息率 |
| 5.2 | `factors/stock/quality.py` | ROE/毛利率 |
| 5.3 | `factors/stock/volatility.py` | 波动率/下行波动率 |
| 5.4 | `factors/cb.py` | 可转债双低/纯债溢价率/YTM |
| 5.5 | `factors/macro.py` | FED模型ERP/利率曲线 |
| 5.6 | `factors/composite.py` | 因子合成/标准化/中性化 |

### Phase 6：更多策略

| Task | 文件 | 说明 |
|------|------|------|
| 6.1 | `strategies/industry_rotation.py` | 行业ETF轮动 |
| 6.2 | `strategies/cb_dual_low.py` | 可转债双低轮动 |
| 6.3 | `strategies/fed_model.py` | 股债性价比仓位管理 |
| 6.4 | `strategies/commodity_rotation.py` | 商品ETF轮动 |
| 6.5 | `strategies/multi_factor.py` | 多因子选股 |

### Phase 7：组合管理

| Task | 文件 | 说明 |
|------|------|------|
| 7.1 | `portfolio/rebalance.py` | 定时/阈值再平衡 |
| 7.2 | `portfolio/optimizer.py` | 风险平价/等权 |

### Phase 8：完整数据支持

| Task | 文件 | 说明 |
|------|------|------|
| 8.1 | `data/fetcher.py` | 新增 StockFetcher/CBFetcher |
| 8.2 | `data/cleaner.py` | 复权/停牌/缺失值 |
| 8.3 | `universe/stock_filter.py` | 股票池筛选 |
| 8.4 | `universe/cb_filter.py` | 可转债筛选 |

---

## Smoke Test 规范

每完成一个 Task，必须运行以下检查：

1. **Import 检查**：所有新模块可导入
2. **单元测试**：`pytest tests/test_xxx.py -v` 全部 PASS
3. **功能 Smoke**：用真实数据跑一次，确认无异常
4. **Git Commit**：`git commit -m "feat: xxx"`

---

## MVP 完成后的交付物

- [x] `data/` 可以获取和缓存ETF历史数据
- [x] `universe/` 可以按分类获取ETF列表
- [x] `factors/momentum.py` 可以计算动量因子
- [x] `strategies/etf_rotation.py` ETF动量轮动策略
- [x] `backtest/engine.py` 回测引擎输出净值曲线
- [x] `backtest/metrics.py` 年化收益/最大回撤/夏普
- [x] 端到端脚本可运行真实数据回测

---

## 下一步

准备好了。要开始 Phase 0（环境准备 + 目录初始化），然后逐个 Task 实施吗？
