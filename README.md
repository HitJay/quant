# Quant

A股股债商全覆盖量化框架，面向长线操作。

## 项目结构

```
quant/
├── src/quant/             # 核心代码
│   ├── data/              # 数据获取（akshare多源自动切换）+ 缓存 + 清洗
│   ├── universe/          # 标的管理（ETF分类映射 + 标的范围控制）
│   ├── factors/           # 因子库（动量/价值/质量/波动率/可转债/宏观）
│   ├── strategies/        # 策略（ETF轮动/行业轮动/可转债双低/FED/商品轮动）
│   ├── backtest/          # 回测引擎 + 绩效指标
│   ├── portfolio/         # 组合再平衡 + 风险平价
│   └── monitor/           # 可视化（HTML交互式报告 + 小红书分享卡片）
├── tests/                 # 35个测试
├── output/                # 策略输出（每个策略独立子文件夹）
│   ├── etf-momentum-rotation/   年化 +16.0%
│   ├── commodity-rotation/      年化 +17.7% ⭐
│   ├── industry-rotation/       年化 +6.4%
│   ├── wide-etf-rotation/       年化 -4.9%
│   └── cards/              收藏图库
├── docs/                  # 调研报告 + 设计文档 + 实施计划
└── data/                  # ETF历史数据缓存（Parquet）
```

## 快速开始

```bash
# 安装依赖（WSL用 --break-system-packages）
pip install akshare pandas numpy matplotlib pytest plotly pyarrow
export PYTHONPATH=src

# 运行测试
pytest tests/ -v

# 生成一份回测报告
unset http_proxy https_proxy
python3 -c "
from quant.monitor.share_card_html import share_card_html
# ... 传入 nav, metrics, benchmark
share_card_html(nav, metrics, benchmark=b, theme='dark')
# 浏览器打开 output/share_card.html
"
```

## 策略回测一览

| 策略 | 标的 | 年化 | 总收益 |
|------|------|------|--------|
| 商品轮动 | 黄金/豆粕/有色 + 国债防御 | **+17.7%** | +131% |
| ETF动量为 | 510300+510500 | **+16.0%** | +1050% |
| 行业轮动 | 5大行业(证券/酒/芯片/新能源/传媒) | +6.4% | +39% |
| 5只宽基 | 沪深300/中证500/上证50/创业板50/科创50 | -4.9% | -24% |

## 功能

- ✅ 数据获取：akshare双源自动切换（东方财富 + 新浪）
- ✅ 本地缓存：Parquet 格式，增量更新
- ✅ ETF分类：7大类20+ETF映射表
- ✅ 标的控制：UniverseConfig 按分类/代码/数量过滤
- ✅ 回测引擎：月频调仓 + 交易成本 + 现金管理
- ✅ 绩效指标：年化/夏普/卡玛/最大回撤/月胜率
- ✅ 因子库：动量/PE/PB/ROE/波动率/可转债双低/ERP
- ✅ 策略5个：ETF轮动/行业轮动/可转债双低/FED模型/商品轮动
- ✅ 可视化1：Plotly交互式 HTML 报告（暗色主题+KPI+热力图+滚动收益）
- ✅ 可视化2：HTML/CSS Flexbox 小红书分享卡片（双主题自动排版）
- ✅ 组合管理：等权/风险平价/定时阈值再平衡

## 技术栈

- **数据源：** AKShare（免费），双源自动切换
- **核心：** Python 3.14, pandas, numpy, matplotlib
- **可视化1（报告）：** Plotly 交互式 HTML（暗色主题，597KB自包含）
- **可视化2（卡片）：** HTML+CSS Flexbox 自包含（72KB，浏览器打开截图）
- **测试：** pytest, 35 tests all PASS

## 可视化输出

| 文件 | 格式 | 说明 |
|------|------|------|
| `output/*/report.html` | HTML | Plotly交互式（净值/回撤/年度/月度/滚动收益） |
| `output/*/share_card.html` | HTML | 小红书风格卡片（CSS Flexbox自动排版） |
| `output/*/share_card.png` | PNG | 暗色图像版 |

## 开发规范

- 策略输出到 `output/<策略名>/` 子目录，4个统一文件
- 每步 TDD + smoke test
- YAGNI：只实现需要的，不做过度设计

## Docs

- [A股量化调研报告](docs/A股量化调研报告.md)
- [v2调研-股债商全覆盖](docs/A股量化调研报告-v2-股债商.md)
- [模块设计文档](docs/模块设计文档.md)
- [实施计划](docs/实施计划-MVP到完整.md)
