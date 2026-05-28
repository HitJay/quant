# 追涨杀跌在A股是否可行 — 研究方案

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 用回测数据回答"追涨杀跌在A股到底能不能赚钱"，输出研究报告 + 小红书卡片系列。

**Architecture:** 在现有回测框架上新建一个参数化动量策略类 `MomentumExperiment`，用不同回溯窗口(5/10/20/60/120/250日)跑截面轮动，横向对比宽基/行业/商品三个ETF池，最终生成对比报告和小红书卡片。

**Tech Stack:** Python 3.14, pandas, akshare, matplotlib, 现有 quant 框架

---

## 研究设计

### 核心问题

"追涨杀跌" = 动量策略(Momentum)：买入过去一段时间涨得最多的标的，卖出涨得最少/跌得最多的。

我们要回答：
1. **哪个时间尺度有效？** 短期(5-20日) vs 中期(60-120日) vs 长期(250日)
2. **哪个市场有效？** 宽基ETF vs 行业ETF vs 商品ETF
3. **追涨 vs 杀跌 vs 反向？** 动量 vs 反转 vs 买入持有
4. **加入止损后效果如何？** 纯动量 vs 动量+止损

### 实验矩阵

| 维度 | 变量 |
|------|------|
| 回溯窗口 | 5日, 10日, 20日, 60日, 120日, 250日 |
| ETF池 | 宽基(2只), 行业(6只), 商品(4只) |
| 调仓频率 | 月度(默认), 周度(短期窗口加测) |
| 策略类型 | 动量(追涨), 反转(抄底), Buy&Hold |

总计约 6×3×2 = 36 组实验（去掉不合理的组合，约 25 组有效实验）。

### 标的池

```python
UNIVERSES = {
    "broad": {
        "name": "Broad Market (CSI300+CSI500)",
        "codes": ["510300", "510500"],
        "bench": "510300",
    },
    "sector": {
        "name": "Sector ETFs",
        "codes": ["515030", "512010", "159928", "512880", "512660", "516160"],
        "bench": "510300",
    },
    "commodity": {
        "name": "Commodity ETFs",
        "codes": ["518880", "159985", "159981", "510990"],
        "bench": "518880",
    },
}
```

- 宽基：沪深300 + 中证500
- 行业：新能源车、医药、消费、券商、军工、新能源
- 商品：黄金、豆粕、能源化工、沪深港通商品

### 回测区间

2018-01-01 ~ 2026-05-28（约8年，覆盖牛熊转换）

---

## 实施计划

### Phase 1: 策略模块 (新建文件)

**新建:** `src/quant/strategies/momentum_experiment.py`

```python
class MomentumExperiment(Strategy):
    """参数化动量/反转实验策略"""
    def __init__(self, window=60, top_n=1, reverse=False, universe=None):
        self.window = window      # 回溯窗口(交易日)
        self.top_n = top_n        # 持有前N只
        self.reverse = reverse    # True=反转(抄底), False=动量(追涨)
        self.universe = universe

    def rebalance(self, date, symbols, prices):
        scores = momentum_scores(prices, symbols, date, self.window)
        # 排序，取top_n
        sorted_syms = sorted(scores, key=scores.get, reverse=not self.reverse)
        selected = sorted_syms[:self.top_n]
        weight = 1.0 / len(selected)
        return Signal(date=str(date), weights={s: weight for s in selected})
```

### Phase 2: 批量实验Runner (新建文件)

**新建:** `analysis/momentum_experiment.py`

主脚本：
1. 拉数据（akshare，三个ETF池）
2. 遍历实验矩阵，跑回测
3. 收集所有结果到 DataFrame
4. 生成对比图表

### Phase 3: 可视化 & 报告

**新建:** `output/momentum-experiment/` 目录下输出

1. **HTML交互报告** — 所有策略净值曲线叠加对比
2. **小红书卡片 (7张)**:
   - 00_cover: 封面卡（"追涨杀跌能赚钱吗？"+ 最佳策略年化收益大字）
   - 01_heatmap: 热力图（窗口×市场 → 年化收益，一眼看出哪些组合赚钱）
   - 02_best_nav: 最佳策略净值曲线 vs Buy&Hold
   - 03_worst_nav: 最差策略净值曲线（展示追涨杀跌的坑）
   - 04_annual: 最佳策略分年度收益柱状图
   - 05_momentum_vs_reversal: 动量 vs 反转对比
   - 06_conclusion: 结论卡（关键发现总结）

3. **付费PDF报告** — 完整研究报告（含数据、方法论、分年度表格、结论）

### Phase 4: 小红书文案

**标题方向:**
- "用8年数据告诉你：A股追涨杀跌到底能不能赚钱"
- "散户最爱追涨杀跌，我回测了25种组合，结果…"

**正文角度:**
- 故事线：大家都说追涨杀跌亏钱，但量化回测发现有些组合竟然年化XX%
- 数据线：25组实验热力图，短期追涨=亏钱，中期动量=赚钱，关键在时间尺度
- 结论线：追涨杀跌不是不能做，关键是选对标的池和回溯窗口

---

## 文件清单

| 操作 | 文件 |
|------|------|
| 新建 | `src/quant/strategies/momentum_experiment.py` |
| 新建 | `tests/test_momentum_experiment.py` |
| 新建 | `analysis/momentum_experiment.py` (主runner脚本) |
| 新建 | `output/momentum-experiment/` (输出目录) |
| 修改 | `src/quant/strategies/__init__.py` (导出新策略) |

## 预期产出

1. `output/momentum-experiment/report.html` — 交互式对比报告
2. `output/momentum-experiment/xhs_cards/` — 7张小红书卡片PNG
3. `output/momentum-experiment/share_card.html` — 最佳策略分享卡
4. `output/momentum-experiment/paid_report.md` — 付费报告Markdown
5. `output/momentum-experiment/paid_report.pdf` — 付费报告PDF

## 执行顺序

1. Phase 1: 写策略 + 测试 (TDD)
2. Phase 2: 写runner脚本，跑通一个组合做smoke test
3. Phase 2: 跑全矩阵，收集数据
4. Phase 3: 生成报告和卡片
5. Phase 4: 写小红书文案

---

预计总工作量：Phase 1-2 约1小时，Phase 3-4 约30分钟。

要开始实现吗？
