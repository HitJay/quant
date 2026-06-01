# A股择时机制深度研究方案

> **目标:** 系统性研究A股主流择时信号的有效性，找到可落地的择时框架，回答"散户/量化小资金能否通过择时增强收益或控制回撤"。

**核心假设:** A股波动大、牛熊鲜明，择时的alpha空间可能大于成熟市场。

---

## 研究框架

### 择时 vs 轮动 vs 选股

| | 择时 (Timing) | 轮动 (Rotation) | 选股 (Selection) |
|---|---|---|---|
| 回答什么 | **何时**入场/离场 | **买哪个**资产 | **买哪只**股票 |
| 信号类型 | 仓位信号 (0%~100%) | 权重信号 | 打分/排序 |
| 本研究关注 | ✅ | 可结合 | 不涉及 |

### 研究问题

1. **哪类择时信号在A股有效？** 技术面 vs 基本面 vs 情绪面 vs 宏观面
2. **单一信号 vs 复合信号？** 各信号独立表现 + 组合后是否更强
3. **择时频率？** 日频调仓 vs 周频 vs 月频
4. **适用资产？** 宽基ETF(沪深300) vs 中小盘(中证500/1000)
5. **实操约束？** 信号延迟、交易成本、税收对择时收益的侵蚀

---

## 择时信号清单

### 第一类：技术面择时 (Price-based)

| # | 信号名称 | 逻辑 | 数据需求 | 优先级 |
|---|----------|------|----------|--------|
| T1 | **均线择时** (MA) | 价格 > MA(N) 则满仓，否则空仓 | 日线收盘价 | ⭐⭐⭐ |
| T2 | **双均线交叉** | MA(短) > MA(长) 做多 | 日线收盘价 | ⭐⭐⭐ |
| T3 | **动量强度** | N日收益率 > 阈值则入场 | 日线收盘价 | ⭐⭐ |
| T4 | **波动率择时** | 低波做多，高波减仓/对冲 | 日线收盘价 | ⭐⭐⭐ |
| T5 | **趋势强度 (ADX)** | ADX > 25 顺趋势，< 20 减仓 | 日线OHLC | ⭐⭐ |
| T6 | **布林带突破** | 突破上轨加仓，跌破下轨减仓 | 日线收盘价 | ⭐⭐ |

### 第二类：估值/基本面择时 (Valuation-based)

| # | 信号名称 | 逻辑 | 数据需求 | 优先级 |
|---|----------|------|----------|--------|
| V1 | **PE百分位** | PE < 历史30%分位满仓，> 70%减仓 | 指数PE历史 | ⭐⭐⭐ |
| V2 | **股债性价比 (ERP)** | E/P - 国债收益率 > 2% 满仓 | PE + 10Y国债 | ⭐⭐⭐ |
| V3 | **巴菲特指标** | 总市值/GDP < 阈值 | 总市值 + GDP | ⭐⭐ |
| V4 | **股息率择时** | 中证红利股息率 > 阈值 | 指数股息率 | ⭐⭐ |

### 第三类：情绪/资金面择时 (Sentiment/Flow)

| # | 信号名称 | 逻辑 | 数据需求 | 优先级 |
|---|----------|------|----------|--------|
| S1 | **换手率** | 全A换手率处于极端高/低位 | 市场换手率 | ⭐⭐⭐ |
| S2 | **融资余额变化** | 融资余额增速 > 阈值做多 | 两融数据 | ⭐⭐ |
| S3 | **新基金发行** | 发行量极大=见顶信号 | 基金发行数据 | ⭐ |
| S4 | **北向资金流** | 北向净流入持续正向 | 北向资金日数据 | ⭐⭐ |

### 第四类：宏观面择时 (Macro)

| # | 信号名称 | 逻辑 | 数据需求 | 优先级 |
|---|----------|------|----------|--------|
| M1 | **M2增速-社融** | 信用扩张周期做多 | M2/社融月度 | ⭐⭐ |
| M2 | **PMI** | PMI > 50 + 环比上升 做多 | PMI月度 | ⭐⭐ |
| M3 | **利率周期** | 降息周期做多 | Shibor/国债收益率 | ⭐⭐ |
| M4 | **汇率信号** | 人民币升值周期利好A股 | USD/CNY | ⭐ |

### 第五类：复合择时 (Composite)

| # | 信号名称 | 逻辑 | 优先级 |
|---|----------|------|--------|
| C1 | **多信号投票** | N个信号中≥K个看多则做多 | ⭐⭐⭐ |
| C2 | **信号加权** | 按历史IR加权 | ⭐⭐ |
| C3 | **regime识别** | HMM/聚类识别牛熊状态 | ⭐⭐ |

---

## 实施计划

### Phase 0: 数据基础设施增强 (Day 1)

**目标:** 让系统能获取择时所需的全部数据

#### 新建: `src/quant/data/macro_fetcher.py`

```python
class MacroFetcher:
    """宏观/情绪数据获取器，基于akshare"""
    
    def get_index_pe(symbol, start_date) -> pd.DataFrame:
        """获取指数PE/PB历史 (乐咕乐股/akshare)"""
    
    def get_bond_yield(tenor='10Y') -> pd.DataFrame:
        """中国国债收益率曲线"""
    
    def get_margin_balance() -> pd.DataFrame:
        """两融余额"""
    
    def get_turnover_rate() -> pd.DataFrame:
        """全A换手率"""
    
    def get_northbound_flow() -> pd.DataFrame:
        """北向资金净流入"""
    
    def get_m2_growth() -> pd.DataFrame:
        """M2同比增速"""
    
    def get_pmi() -> pd.DataFrame:
        """制造业PMI"""
```

#### 新建: `src/quant/data/index_fetcher.py`

```python
class IndexFetcher:
    """指数行情获取（用于择时研究的标的）"""
    
    def get_index_daily(symbol='000300', start='2005-01-01') -> pd.DataFrame:
        """获取指数日线（沪深300/中证500/中证1000等）"""
```

---

### Phase 1: 择时因子库 (Day 1-2)

**目标:** 实现所有择时信号的计算逻辑

#### 新建: `src/quant/factors/timing.py`

```python
"""
择时因子库 — 将各类信号统一为 position_signal ∈ [0.0, 1.0]
0.0 = 空仓/纯债
1.0 = 满仓权益
"""

# --- 技术面 ---
def ma_timing(prices: pd.Series, window: int = 200) -> pd.Series:
    """均线择时: price > MA(N) → 1.0, else → 0.0"""

def dual_ma_timing(prices: pd.Series, fast: int = 20, slow: int = 60) -> pd.Series:
    """双均线: MA(fast) > MA(slow) → 1.0"""

def volatility_timing(prices: pd.Series, window: int = 20, threshold: float = 0.25) -> pd.Series:
    """波动率择时: 年化波动率 < threshold → 1.0, 线性衰减"""

def momentum_timing(prices: pd.Series, window: int = 60, threshold: float = 0.0) -> pd.Series:
    """动量择时: N日收益率 > threshold → 1.0"""

def bollinger_timing(prices: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.Series:
    """布林带: 在带内1.0，跌破下轨0.0"""

# --- 估值面 ---
def pe_percentile_timing(pe_series: pd.Series, low: float = 0.3, high: float = 0.7) -> pd.Series:
    """PE百分位: < low → 1.0, > high → 0.0, 之间线性"""

def erp_timing(pe_series: pd.Series, bond_yield: pd.Series) -> pd.Series:
    """股债性价比择时"""

# --- 情绪面 ---
def turnover_timing(turnover: pd.Series, window: int = 250) -> pd.Series:
    """换手率择时: 极低换手看多，极高换手看空"""

def margin_timing(margin_balance: pd.Series, window: int = 60) -> pd.Series:
    """融资余额变化率择时"""

# --- 复合 ---
def composite_vote(signals: list[pd.Series], threshold: float = 0.5) -> pd.Series:
    """多信号投票: mean(signals) > threshold → 1.0"""

def composite_weighted(signals: list[pd.Series], weights: list[float]) -> pd.Series:
    """加权复合信号"""
```

---

### Phase 2: 择时回测引擎增强 (Day 2)

**目标:** 支持仓位信号 (0~1) 的回测，而非仅资产轮动

#### 新建: `src/quant/strategies/timing_strategy.py`

```python
class TimingStrategy(Strategy):
    """
    择时策略 — 基于仓位信号在 equity_etf 和 bond_etf/cash 之间切换
    
    signal=1.0 → 100% equity_etf
    signal=0.0 → 100% bond_etf (或 cash)
    """
    def __init__(self, 
                 signal_func,          # 择时因子函数
                 signal_params: dict,  # 因子参数
                 equity_etf='510300',  # 权益标的
                 bond_etf='511010',    # 债券标的(国债ETF)
                 rebalance_freq='daily'):  # 调仓频率
        ...
    
    def rebalance(self, date, symbols, prices) -> Signal:
        """根据择时信号决定权益/债券配比"""
```

#### 增强回测引擎: 支持日频/周频调仓

当前引擎只支持月度调仓，择时研究需要更高频的调仓支持。

```python
# engine.py 增强
class BacktestEngine:
    def __init__(self, ..., rebalance_freq='monthly'):
        # 支持 'daily', 'weekly', 'monthly'
```

---

### Phase 3: 批量实验与统计检验 (Day 2-3)

**目标:** 系统性跑所有信号组合，评估有效性

#### 新建: `analysis/timing_experiment.py`

```python
"""
择时信号大规模回测实验
输出: 各信号独立表现 + 最优参数 + 复合信号表现
"""

# 实验矩阵
EXPERIMENTS = {
    # 技术面
    'MA_20': {'func': ma_timing, 'params': {'window': 20}},
    'MA_60': {'func': ma_timing, 'params': {'window': 60}},
    'MA_120': {'func': ma_timing, 'params': {'window': 120}},
    'MA_250': {'func': ma_timing, 'params': {'window': 250}},
    'DualMA_5_20': {'func': dual_ma_timing, 'params': {'fast': 5, 'slow': 20}},
    'DualMA_10_60': {'func': dual_ma_timing, 'params': {'fast': 10, 'slow': 60}},
    'DualMA_20_120': {'func': dual_ma_timing, 'params': {'fast': 20, 'slow': 120}},
    'Vol_20': {'func': volatility_timing, 'params': {'window': 20}},
    'Vol_60': {'func': volatility_timing, 'params': {'window': 60}},
    # 估值面
    'PE_Pct': {'func': pe_percentile_timing, 'params': {}},
    'ERP': {'func': erp_timing, 'params': {}},
    # 情绪面
    'Turnover': {'func': turnover_timing, 'params': {}},
    'Margin': {'func': margin_timing, 'params': {}},
    # 复合
    'Composite_Vote': {'func': composite_vote, 'params': {}},
}

# 每个实验输出
@dataclass
class TimingResult:
    name: str
    annual_return: float
    max_drawdown: float
    sharpe: float
    calmar: float
    win_rate: float           # 月度胜率
    timing_accuracy: float    # 择时准确率(信号方向与市场方向一致的比率)
    avg_holding_days: float   # 平均持仓天数
    trade_count: int          # 调仓次数
    nav_series: pd.Series
    signal_series: pd.Series
```

#### 统计检验

```python
def bootstrap_sharpe(nav, n_boot=1000) -> (float, float):
    """Bootstrap Sharpe置信区间，判断是否显著>0"""

def compare_vs_buyhold(timing_nav, buyhold_nav) -> dict:
    """择时 vs 买入持有的统计对比"""

def out_of_sample_test(signal_func, params, split_date='2022-01-01') -> dict:
    """样本内/外分割检验，防过拟合"""
```

---

### Phase 4: 可视化与报告 (Day 3-4)

#### 新建: `analysis/timing_report.py`

输出内容:
1. **信号有效性排行榜** — 所有信号按Sharpe/Calmar排序
2. **各信号净值曲线对比图** — vs 买入持有
3. **回撤控制能力** — 择时策略在2015/2018/2022下跌中的表现
4. **信号时序图** — 信号变化 + 对应涨跌的叠加图
5. **参数敏感度分析** — 同一类信号不同参数的表现热力图
6. **复合信号 vs 单信号** — 组合是否优于最优单信号
7. **交易成本敏感度** — 不同交易频率下的成本侵蚀

---

### Phase 5: 结论与策略落地 (Day 4)

根据回测结果:
1. 筛选样本外表现稳健的信号 (2-3个)
2. 构建实盘可用的复合择时模型
3. 集成到现有 monitor 模块，输出每日/每周择时建议
4. 生成小红书系列卡片（类似之前的动量研究）

---

## 回测基准与评价标准

### 基准策略
- **Buy & Hold 沪深300** — 最基本基准
- **Buy & Hold 60/40 (股债)** — 被动配置基准
- **年度再平衡 60/40** — 纪律性配置基准

### 评价指标（择时策略需满足）
- Sharpe > Buy&Hold + 0.2 (有实质性提升)
- 最大回撤 < Buy&Hold × 0.7 (回撤控制能力)
- 样本外(2022-2026)表现不显著弱于样本内
- 年调仓次数 < 20 (可操作性)
- 考虑交易成本后仍有效

### 回测区间
- **全样本:** 2010-01-01 ~ 2026-05-31 (16年)
- **样本内:** 2010-01-01 ~ 2021-12-31
- **样本外:** 2022-01-01 ~ 2026-05-31

---

## 代码开发顺序

```
Day 1 (基础):
  ├── src/quant/data/macro_fetcher.py      # 宏观数据获取
  ├── src/quant/data/index_fetcher.py      # 指数数据获取
  └── src/quant/factors/timing.py          # 择时因子库

Day 2 (引擎):
  ├── src/quant/strategies/timing_strategy.py  # 择时策略类
  ├── src/quant/backtest/engine.py (增强)      # 支持日/周频
  └── tests/test_timing.py                     # 单元测试

Day 3 (实验):
  ├── analysis/timing_experiment.py        # 批量回测
  └── analysis/timing_report.py            # 报告生成

Day 4 (总结):
  ├── output/timing-research/              # 图表+结论
  └── src/quant/monitor/ (集成)            # 实盘信号
```

---

## 关键风险与注意事项

1. **过拟合风险** — 参数多+A股数据短，容易拟合到特定牛熊周期
   - 对策: 严格样本内/外分割，Bootstrap检验
2. **数据偷看 (Look-ahead bias)** — PE/宏观数据有发布延迟
   - 对策: 所有信号延迟1-2天使用
3. **幸存者偏差** — ETF存续时间短
   - 对策: 用指数数据做长期研究，ETF做近期验证
4. **交易成本侵蚀** — 高频调仓择时成本可能吃掉alpha
   - 对策: 设置最低调仓阈值（仓位变化 < 10% 不动）
5. **择时与情绪的矛盾** — 择时信号往往在最恐慌时要求加仓
   - 这是研究的价值所在：量化纪律 vs 人性弱点

---

## 预期产出

1. **研究报告** (Markdown) — 各信号表现总结 + 推荐策略
2. **可视化图表** — 净值曲线、信号时序、参数热力图
3. **策略代码** — 可直接用于实盘跟踪的择时模块
4. **小红书卡片** — 系列科普内容（"A股择时到底有没有用"）
