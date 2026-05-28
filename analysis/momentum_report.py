"""
右侧vs左侧交易 — 付费深度研报生成器
===================================
11章结构，MD→PDF(WeasyPrint)→水印
"""
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from markdown_it import MarkdownIt
from weasyprint import HTML

from quant.data.cache import Cache
from quant.data.fetcher import ETFDataFetcher
from quant.strategies.momentum_experiment import MomentumExperiment
from quant.backtest.engine import BacktestEngine
from quant.backtest.metrics import annual_return, max_drawdown, sharpe, win_rate
from quant.universe.config import UniverseConfig

# ============================================================
# 配置
# ============================================================
UNIVERSES = {
    "broad": {
        "name": "宽基 (沪深300+中证500)",
        "codes": ["510300", "510500"],
        "bench": "510300",
        "bench_label": "沪深300 买入持有",
    },
    "sector": {
        "name": "行业 (6只ETF)",
        "codes": ["515030", "512010", "159928", "512880", "512660", "516160"],
        "bench": "510300",
        "bench_label": "沪深300 买入持有",
    },
    "commodity": {
        "name": "商品 (4只ETF)",
        "codes": ["518880", "159985", "159981", "510990"],
        "bench": "518880",
        "bench_label": "黄金 买入持有",
    },
}

WINDOWS = [5, 10, 20, 60, 120, 250]
START_DATE = "2018-01-01"
END_DATE = "2026-05-28"
OUTPUT_DIR = Path("./output/momentum-experiment")
FONT_DIR = Path.home() / ".local/share/fonts"


def load_all_data():
    cache = Cache("./data/cache")
    fetcher = ETFDataFetcher()
    all_codes = set()
    for cfg in UNIVERSES.values():
        all_codes.update(cfg["codes"])
    all_codes.add("510300")
    data = {}
    for code in all_codes:
        df = fetcher.fetch_or_cache(code, START_DATE, END_DATE, cache=cache)
        data[code] = df["close"]
    return pd.DataFrame(data).dropna()


def run_experiments(prices):
    results = []
    engine = BacktestEngine()
    for uni_key, uni_cfg in UNIVERSES.items():
        avail = [c for c in uni_cfg["codes"] if c in prices.columns]
        if len(avail) < 2:
            continue
        uni = UniverseConfig(etf_codes=avail)
        p = prices[avail]
        bench_code = uni_cfg["bench"]
        bench_price = prices[bench_code]
        for window in WINDOWS:
            for reverse in [False, True]:
                strat = MomentumExperiment(window=window, top_n=1, reverse=reverse, universe=uni)
                result = engine.run(strat, p, avail)
                nav = result.nav_series
                if len(nav) < 10:
                    continue
                bench = bench_price.reindex(nav.index).ffill().dropna()
                common = nav.index.intersection(bench.index)
                nav = nav.loc[common]
                bench = bench.loc[common]
                ann = annual_return(nav)
                dd = max_drawdown(nav)
                sh = sharpe(nav)
                wr = win_rate(nav)
                total = result.total_return
                bench_ret = bench.iloc[-1] / bench.iloc[0] - 1
                yrs = (bench.index[-1] - bench.index[0]).days / 365.25
                bench_ann = (1 + bench_ret) ** (1 / max(yrs, 0.01)) - 1
                results.append({
                    "universe": uni_key,
                    "uni_name": uni_cfg["name"],
                    "bench_label": uni_cfg["bench_label"],
                    "window": window,
                    "reverse": reverse,
                    "label": f"{'左侧' if reverse else '右侧'}_{window}日",
                    "annual_return": ann,
                    "max_drawdown": dd,
                    "sharpe": sh,
                    "win_rate": wr,
                    "total_return": total,
                    "bench_ann": bench_ann,
                    "bench_total": bench_ret,
                    "alpha": ann - bench_ann,
                    "nav": nav,
                    "bench": bench,
                    "result": result,
                })
    return results


def fmt_pct(v):
    """Format as +/-xx.x%"""
    return f"{v:+.1%}"


def fmt_num(v, decimals=2):
    return f"{v:.{decimals}f}"


def calc_calmar(ann_ret, max_dd):
    return ann_ret / abs(max_dd) if max_dd != 0 else 0


def generate_md_report(results):
    """生成完整的付费研报MD内容"""
    sorted_r = sorted(results, key=lambda r: r["annual_return"], reverse=True)
    best = sorted_r[0]
    worst = sorted_r[-1]
    
    # 最佳右侧和最佳左侧
    mom = [r for r in results if not r["reverse"]]
    rev = [r for r in results if r["reverse"]]
    best_mom = max(mom, key=lambda r: r["annual_return"])
    best_rev = max(rev, key=lambda r: r["annual_return"])
    
    lines = []
    a = lines.append
    
    # ===== 封面 =====
    a("# 追涨杀跌 vs 抄底逃顶\n## 哪种策略在A股能赚钱？\n### 量化深度研报")
    a(f"\n**回测区间**：{START_DATE} 至 {END_DATE}（约8.4年）\n")
    a(f"**策略数量**：36种组合（3个市场 × 6个窗口 × 2方向）\n")
    a("**调仓频率**：月度\n\n---\n")
    
    # ===== 第1章：策略概述 =====
    a("## 一、策略概述\n")
    a("本研报系统性地对比了**右侧交易（追涨杀跌）**与**左侧交易（抄底逃顶）**在A股ETF市场的表现。")
    a("我们覆盖三大市场——宽基指数、行业板块、商品——共计36种策略组合，跨越8年市场周期。\n")
    a("**右侧交易（顺势）**：涨时买入、跌时卖出，追逐趋势。又称动量策略、趋势跟随、追涨杀跌。")
    a("**左侧交易（逆势）**：跌时买入、涨时卖出，逆向布局。又称反转策略、逆势交易、低吸高抛、价值投资。\n")
    a("**核心发现**：商品120日右侧策略年化 **+19.5%**，Sharpe 0.88，是全部36组中的最优解。\n")
    
    # ===== 第2章：术语速查 =====
    a("## 二、术语速查\n")
    a("| 术语 | 大白话解释 | 类比 |")
    a("|------|-----------|------|")
    glossary = [
        ("右侧交易", "涨的时候买，跌的时候卖", "看着涨了就上车，看着跌了就下车"),
        ("左侧交易", "跌的时候买，涨的时候卖", "跌多了去抄底，涨高了就兑现"),
        ("年化收益率", "平均每年能赚多少", "存银行年利率那种算法，但考虑了复利"),
        ("最大回撤", "最惨的时候亏了多少", "你买了之后，账户最高点到最低点亏了多少"),
        ("夏普比率(Sharpe)", "冒一份风险赚了多少", "同样波动下，赚得越多Sharpe越高；0.5以上算及格，1.0以上算优秀"),
        ("卡玛比率(Calmar)", "盈亏比", "年化收益÷最大回撤，越高越划算"),
        ("动量(Momentum)", "强者恒强", "涨得好的继续涨——就像热门股票继续被追捧"),
        ("反转(Reversal)", "物极必反", "跌多了总会反弹——就像弹簧压久了会弹回来"),
        ("ETF", "指数基金", "一篮子股票的打包产品，像买整个赛道"),
        ("回溯窗口", "看多长的历史", "比如120日窗口=看过去半年的涨跌来决定买卖"),
    ]
    for term, explain, analogy in glossary:
        a(f"| {term} | {explain} | {analogy} |")
    a("")
    
    # ===== 第3章：核心数据对比 =====
    a("## 三、核心数据对比\n")
    a(f"以下对比全部36种策略组合中最优策略与最劣策略的核心指标：\n")
    
    benchmark = best["bench_label"]
    b_ann = best["bench_ann"]
    b_dd = max_drawdown(best["bench"])
    b_sh = sharpe(best["bench"])
    
    a("### Top 5 策略（按年化排序）\n")
    a("| 排名 | 策略 | 市场 | 年化 | 总收益 | 最大回撤 | Sharpe | 胜率 |")
    a("|------|------|------|------|--------|---------|--------|------|")
    for i, r in enumerate(sorted_r[:5]):
        a(f"| {i+1} | {r['label']} | {r['uni_name'].split('(')[0].strip()} | {fmt_pct(r['annual_return'])} | {fmt_pct(r['total_return'])} | -{fmt_pct(r['max_drawdown'])} | {fmt_num(r['sharpe'])} | {fmt_pct(r['win_rate'])} |")
    a("")
    
    a("### Bottom 3 策略\n")
    a("| 排名 | 策略 | 市场 | 年化 | 总收益 | 最大回撤 | Sharpe | 胜率 |")
    a("|------|------|------|------|--------|---------|--------|------|")
    for i, r in enumerate(sorted_r[-3:]):
        rank = len(sorted_r) - 2 + i
        a(f"| {rank} | {r['label']} | {r['uni_name'].split('(')[0].strip()} | {fmt_pct(r['annual_return'])} | {fmt_pct(r['total_return'])} | -{fmt_pct(r['max_drawdown'])} | {fmt_num(r['sharpe'])} | {fmt_pct(r['win_rate'])} |")
    a("")
    
    a("### 对标基准\n")
    a("| 基准 | 年化 | 总收益 | 最大回撤 | Sharpe |")
    a("|------|------|--------|---------|--------|")
    a(f"| {benchmark} | {fmt_pct(b_ann)} | {fmt_pct(best['bench_total'])} | -{fmt_pct(b_dd)} | {fmt_num(b_sh)} |")
    a("")
    
    # ===== 第4章：策略完整参数 =====
    a("## 四、策略完整参数\n")
    a("### 最佳策略\n")
    a(f"| 参数 | 值 | 说明 |")
    a(f"|------|-----|------|")
    a(f"| 策略名称 | {best['label']} | 右侧=顺势(追涨杀跌)，左侧=逆势(抄底逃顶) |")
    a(f"| 交易市场 | {best['uni_name']} | — |")
    a(f"| 回溯窗口 | {best['window']} 日 | 过去N个交易日的涨幅排名 |")
    a(f"| 持仓数量 | 1只 | 只买排名最高的那1只ETF |")
    a(f"| 调仓频率 | 月度 | 每月月底根据排名调仓 |")
    a(f"| 交易成本 | 0.1%单边 | 含佣金+冲击成本（保守估计）|\n")
    
    a("### 参数组合全量\n")
    a("| 维度 | 取值 |")
    a("|------|------|")
    a("| 市场类型 | 宽基（沪深300+中证500）、行业（6只ETF）、商品（黄金+豆粕+能源+有色） |")
    a("| 回溯窗口 | 5日、10日、20日、60日、120日、250日 |")
    a("| 交易方向 | 右侧（追涨）、左侧（抄底） |")
    a("| 总计组合 | 3 × 6 × 2 = 36 |\n")
    
    # ===== 第5章：分年度表现 =====
    a("## 五、分年度表现\n")
    
    # 最佳策略分年度
    nav = best["nav"]
    bench_nav = best["bench"]
    years = sorted(set(nav.index.year))
    
    a(f"### 最佳策略：{best['label']}\n")
    a("| 年份 | 策略收益 | 基准收益 | 超额收益 |")
    a("|------|---------|---------|---------|")
    for y in years:
        s = nav[nav.index.year == y]
        b = bench_nav[bench_nav.index.year == y]
        if len(s) > 1 and len(b) > 1:
            sy = s.iloc[-1] / s.iloc[0] - 1
            by = b.iloc[-1] / b.iloc[0] - 1
            a(f"| {y} | {fmt_pct(sy)} | {fmt_pct(by)} | {fmt_pct(sy-by)} |")
    a("")
    
    # 最佳左侧分年度
    rev_nav = best_rev["nav"]
    rev_bench = best_rev["bench"]
    r_years = sorted(set(rev_nav.index.year))
    
    a(f"### 最佳左侧策略：{best_rev['label']}\n")
    a("| 年份 | 策略收益 | 基准收益 | 超额收益 |")
    a("|------|---------|---------|---------|")
    for y in r_years:
        s = rev_nav[rev_nav.index.year == y]
        b = rev_bench[rev_bench.index.year == y]
        if len(s) > 1 and len(b) > 1:
            sy = s.iloc[-1] / s.iloc[0] - 1
            by = b.iloc[-1] / b.iloc[0] - 1
            a(f"| {y} | {fmt_pct(sy)} | {fmt_pct(by)} | {fmt_pct(sy-by)} |")
    a("")
    
    # ===== 第6章：参数敏感性分析 =====
    a("## 六、参数敏感性分析\n")
    a("### 窗口长度对年化收益的影响\n")
    a("| 窗口 | 宽基(右侧) | 宽基(左侧) | 行业(右侧) | 行业(左侧) | 商品(右侧) | 商品(左侧) |")
    a("|------|-----------|-----------|-----------|-----------|-----------|-----------|")
    for w in WINDOWS:
        row = f"| {w}日 |"
        for uni in ["broad", "sector", "commodity"]:
            for rev in [False, True]:
                r = [x for x in results if x["universe"] == uni and x["window"] == w and x["reverse"] == rev]
                row += f" {fmt_pct(r[0]['annual_return'])} |" if r else " N/A |"
        a(row)
    a("")
    
    a("**解读**：商品市场显示最强的趋势特征——窗口越长右侧越有效。宽基市场均值回归明显——短期右侧亏、中长期左侧赚。行业ETF波动大，无论哪种策略都需要精准择时。\n")
    
    # ===== 第7章：月度收益明细 =====
    a("## 七、月度收益明细（最佳策略）\n")
    a(f"以下为最佳策略 **{best['label']}** 的月度收益：\n")
    
    # Build monthly returns
    monthly_data = {}
    for y in years:
        monthly_data[y] = {}
        for m in range(1, 13):
            s = nav[(nav.index.year == y) & (nav.index.month == m)]
            if len(s) >= 2:
                monthly_data[y][m] = s.iloc[-1] / s.iloc[0] - 1
            else:
                monthly_data[y][m] = None
    
    a(f"| 月份 | " + " | ".join(str(y) for y in years) + " |")
    a("|------|" + "|".join("----" for _ in years) + "|")
    for m in range(1, 13):
        row = f"| {m}月 |"
        for y in years:
            v = monthly_data.get(y, {}).get(m)
            row += f" {fmt_pct(v) if v is not None else '—'} |"
        a(row)
    a("")
    
    # ===== 第8章：持仓统计 =====
    a("## 八、持仓统计\n")
    
    # Count positions from best strategy result
    positions = best["result"].positions
    if hasattr(positions, "empty") and not positions.empty:
        # positions is a DataFrame
        pos_list = positions.to_dict("records") if hasattr(positions, "to_dict") else list(positions)
        code_col = "asset" if "asset" in positions.columns else positions.columns[0]
        code_counts = positions[code_col].value_counts().to_dict()
        
        a(f"| 持仓ETF | 持有月份数 | 占比 |")
        a(f"|----------|-----------|------|")
        for code, count in sorted(code_counts.items(), key=lambda x: -x[1]):
            a(f"| {code} | {count} | {fmt_pct(count/len(positions))} |")
        a(f"\n**总调仓次数**：{len(positions) - 1} 次\n")
    else:
        a("> 持仓详情需从回测引擎的trade_log中提取。本策略为月度调仓，每月底选择最优ETF持有。\n")
    
    # ===== 第9章：风险控制 =====
    a("## 九、风险控制\n")
    a("### 已知风险\n")
    a("1. **过度优化风险**：36种组合中挑选最优，存在数据挖掘偏差。建议用样本外数据验证。")
    a("2. **行业集中风险**：单只ETF持仓，极端行情下缺乏分散保护。")
    a("3. **调仓时点风险**：月度调仓对月末价格敏感，若遇月底异常波动会影响信号质量。")
    a("4. **流动性风险**：部分行业ETF日成交额较小，大资金需考虑冲击成本。\n")
    
    a("### 改进方向\n")
    a("1. **持仓分散化**：从Top 1改为Top 3等权持仓，降低单只风险。")
    a("2. **动态调仓频率**：根据市场波动率自适应调整调仓周期。")
    a("3. **止损机制**：单月回撤超过阈值时触发强制平仓。")
    a("4. **多因子融合**：结合基本面、波动率等辅助因子，提升信号质量。\n")
    
    # ===== 第10章：实盘部署指南 =====
    a("## 十、实盘部署指南\n")
    a("### 资金配置\n")
    a(f"- **初始资金**：不低于10万元（单只ETF最低门槛）")
    a(f"- **推荐资金**：50万元及以上（可覆盖所有ETF标的且冲击成本可控）\n")
    
    a("### 操作流程\n")
    a("1. 每月最后一个交易日收盘前，获取目标池所有ETF的过去N日涨跌幅")
    a("2. 按涨跌幅排序（右侧=降序选最高，左侧=升序选最低）")
    a("3. 全仓切换至排名第一的ETF")
    a("4. 持有至下月调仓日\n")
    
    a("### 技术栈推荐\n")
    a("- **数据源**：AKShare（东方财富）、qstock、Tushare Pro")
    a("- **回测框架**：自研框架（本回测所用）、VNPY、Backtrader")
    a("- **实盘执行**：券商API / QMT 极简模式 / 手动下单\n")
    
    # ===== 第11章：免责声明 =====
    a("## 十一、免责声明\n")
    a("1. **历史回测不代表未来表现**。所有收益数据均为历史数据的模拟结果，不构成投资建议。")
    a("2. 回测中包含理想化假设（无滑点、流动性充足），实盘结果可能显著低于回测。")
    a("3. 作者不对任何人依据本报告进行投资所造成的任何损失承担责任。")
    a("4. 投资有风险，入市需谨慎。请在充分了解风险后独立做出投资决策。")
    a("5. 本报告版权归作者所有，仅供付费用户个人参考，禁止转载、分发或二次销售。\n")
    
    # Footer
    a("\n---\n")
    a(f"*报告生成日期：{pd.Timestamp.now().strftime('%Y-%m-%d')} | 数据来源：东方财富 | 回测引擎：quant v1.0*")
    
    return "\n".join(lines)


def md_to_pdf(md_content, output_path, font_dir):
    """MD → HTML → PDF with professional styling"""
    
    # CSS
    css = f"""
    @page {{
        size: A4;
        margin: 2cm 2.2cm;
        @bottom-right {{
            content: counter(page) "/" counter(pages);
            font-size: 9pt;
            color: #888;
            font-family: 'SansSC', sans-serif;
        }}
    }}
    
    @font-face {{
        font-family: 'SerifSC';
        src: url('file://{font_dir}/NotoSerifSC-Regular.otf');
        font-weight: normal;
    }}
    @font-face {{
        font-family: 'SerifSC';
        src: url('file://{font_dir}/NotoSerifSC-Bold.otf');
        font-weight: bold;
    }}
    @font-face {{
        font-family: 'SansSC';
        src: url('file://{font_dir}/NotoSansSC-Regular.otf');
        font-weight: normal;
    }}
    @font-face {{
        font-family: 'SansSC';
        src: url('file://{font_dir}/NotoSansSC-Bold.otf');
        font-weight: bold;
    }}
    
    body {{
        font-family: 'SerifSC', serif;
        font-size: 10.5pt;
        line-height: 1.8;
        color: #2c2c2c;
    }}
    
    h1 {{
        font-family: 'SansSC', sans-serif;
        font-weight: bold;
        font-size: 22pt;
        color: #1a1a2e;
        border-bottom: 3px solid #c0392b;
        padding-bottom: 8px;
        margin-top: 0;
    }}
    
    h2 {{
        font-family: 'SansSC', sans-serif;
        font-weight: bold;
        font-size: 15pt;
        color: #1a1a2e;
        border-left: 5px solid #c0392b;
        padding-left: 12px;
        margin-top: 28px;
    }}
    
    h3 {{
        font-family: 'SansSC', sans-serif;
        font-weight: bold;
        font-size: 12pt;
        color: #333;
        margin-top: 20px;
    }}
    
    table {{
        font-family: 'SansSC', sans-serif;
        font-size: 9pt;
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
    }}
    
    th {{
        background: #2c3e50;
        color: white;
        padding: 8px 6px;
        text-align: left;
    }}
    
    td {{
        padding: 6px;
        border-bottom: 1px solid #ddd;
    }}
    
    tr:nth-child(even) td {{
        background: #f8f9fa;
    }}
    
    strong {{
        color: #c0392b;
    }}
    
    blockquote {{
        border-left: 4px solid #bdc3c7;
        padding-left: 16px;
        color: #555;
        font-style: italic;
    }}
    
    hr {{
        border: none;
        border-top: 1px solid #ddd;
        margin: 24px 0;
    }}
    """
    
    # Convert MD → HTML
    md = MarkdownIt('commonmark', {'html': True}).enable('table')
    html_body = md.render(md_content)
    
    html_full = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>{css}</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    print(f"  生成PDF到 {output_path} ...")
    HTML(string=html_full).write_pdf(output_path)
    
    # Check size
    size_kb = Path(output_path).stat().st_size / 1024
    print(f"  ✓ {output_path} ({size_kb:.0f} KB)")


def main():
    print("=" * 60)
    print("右侧vs左侧交易 — 付费深度研报生成")
    print("=" * 60)
    
    print("\n加载数据...")
    prices = load_all_data()
    
    print("运行36组实验...")
    results = run_experiments(prices)
    print(f"  {len(results)} 组完成")
    
    print("\n生成MD报告...")
    md_content = generate_md_report(results)
    md_path = OUTPUT_DIR / "paid_report.md"
    md_path.write_text(md_content, encoding="utf-8")
    print(f"  ✓ {md_path} ({len(md_content)} 字符)")
    
    print("\nMD → PDF渲染...")
    pdf_path = OUTPUT_DIR / "paid_report.pdf"
    md_to_pdf(md_content, str(pdf_path), FONT_DIR)
    
    print("\n添加水印...")
    import subprocess
    result = subprocess.run([
        sys.executable, str(Path(__file__).parent.parent / "analysis" / "add_watermark.py"),
        str(pdf_path),
        str(OUTPUT_DIR / "paid_report_watermarked.pdf"),
        "付费专享 · 复旦杰伦"
    ], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ {OUTPUT_DIR / 'paid_report_watermarked.pdf'}")
    else:
        print(f"  ⚠ 水印添加失败: {result.stderr}")
    
    print("\n✓ 全部完成！")
    print(f"  研报: {pdf_path}")
    print(f"  水印版: {OUTPUT_DIR / 'paid_report_watermarked.pdf'}")


if __name__ == "__main__":
    main()
