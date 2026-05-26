# ETF Momentum Rotation

## 策略简介

最简单的宽基ETF动量轮动策略。

**逻辑：** 每个月看过去3个月谁涨得多，全仓切过去。

**参数：**
- `momentum_window=63`  — 3个月动量（63个交易日）
- `hold_n=1`            — 全仓持有动量最强的1只
- 标的：`510300`（沪深300ETF）+ `510500`（中证500ETF）
- 调仓频率：月初

**回测区间：** 2013-03 ~ 2026-05（约3200个交易日）

## 绩效

| 指标 | 策略 | 510300 B&H |
|------|------|------------|
| 年化收益 | **+16.0%** | +5.2% |
| 最大回撤 | 62.3% | 48.6% |
| 夏普比率 | 0.36 | 0.15 |
| 总收益 | **+1047.9%** | +98.4% |
| 月度胜率 | 57.4% | 52.1% |

⚠️ 回撤仍然很大，后续加入 FED 模型股债仓位管理可大幅改善。

## 生成报告

```bash
PYTHONPATH=src python3 -c "
from quant.monitor.share_card_html import share_card_html
# ... (see ../../docs/实施计划-MVP到完整.md for full script)
share_card_html(nav, metrics, benchmark=b, theme='dark',
                save_path='./output/etf-momentum-rotation/share_card.html')
"
```

## 文件

- `share_card.html` — HTML/CSS 分享卡片（浏览器打开截图）
- `share_card.png` — PNG 图像版（直接发社交媒体）
- `report.html` — 交互式 Plotly 完整回测报告（缩放、悬停、热力图）

## 改进方向

1. ✅ 基础ETF动量轮动
2. ⬜ 加入FED模型降回撤
3. ⬜ 扩展至5只宽基ETF
4. ⬜ 行业ETF轮动
5. ⬜ 可转债双低轮动
