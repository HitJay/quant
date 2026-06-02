"""
PE/PB估值择时 — 付费研报生成器
===============================
生成: README.md + paid_report.md → PDF + 水印PDF
"""

import os, sys, json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "output/pe_pb_research"
HOME = Path.home()
FONT_DIR = HOME / ".local/share/fonts"
XHS_ID = "复旦杰伦"


def load_data():
    with open(DATA_DIR / "results.json") as f:
        return json.load(f)


def build_paid_md(data):
    """生成付费研报Markdown"""
    mt = data["market_timing"]
    sr = data["sector_rotation"]
    pe_now = data["pe_now"]
    pb_now = data["pb_now"]

    lines = []
    lines.append(f"# PE/PB估值分位择时 — 深度研报")
    lines.append(f"")
    lines.append(f"**发布日期**: 2026年6月")
    lines.append(f"**作者**: {XHS_ID}")
    lines.append(f"**数据周期**: 2013-2026 · 宽基(沪深300+国债) / 2021-2026 · 行业(5只ETF)")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Chapter 1: Market Overview
    lines.append(f"## 1. 当前估值水位")
    lines.append(f"")
    lines.append(f"| 指标 | 当前值 | 历史分位 | 历史最低 | 历史最高 |")
    lines.append(f"|------|--------|----------|----------|----------|")
    lines.append(f"| PE(TTM) | {pe_now['value']:.2f} | {pe_now['pct']:.1f}% | {pe_now['min']:.2f} | {pe_now['max']:.2f} |")
    lines.append(f"| PB | {pb_now['value']:.2f} | {pb_now['pct']:.1f}% | {pb_now['min']:.2f} | {pb_now['max']:.2f} |")
    lines.append(f"")
    lines.append(f"**解读**: 当前沪深300 PE处于历史{pe_now['pct']:.0f}分位，PB处于{pb_now['pct']:.0f}分位。")
    if pe_now['pct'] < 30:
        lines.append(f"PE处于历史偏低水平，整体市场估值合理偏低。")
    elif pe_now['pct'] < 70:
        lines.append(f"PE处于历史中等水平，估值中性。")
    else:
        lines.append(f"PE处于历史偏高水平，需注意估值风险。")
    lines.append(f"")

    # Chapter 2: Market-Level PE/PB Timing
    lines.append(f"## 2. 宽基PE/PB估值择时 — 回测结果")
    lines.append(f"")
    lines.append(f"**回测周期**: 2013-04 ~ 2026-06 · 标的: 510300(沪深300ETF) + 511010(国债ETF)")
    lines.append(f"**调仓频率**: 月频 · **策略**: 估值分位低→满仓权益，分位高→转向债券")
    lines.append(f"")
    lines.append(f"### 2.1 核心绩效对比")
    lines.append(f"")
    lines.append(f"| 策略 | 年化收益 | 最大回撤 | 夏普比率 | 卡玛比率 | 胜率 |")
    lines.append(f"|------|----------|----------|----------|----------|------|")

    # Key strategies to display
    key_strats = ["买入持有", "60/40固定", "PE_5y_30_70", "PB_10y_30_70", "PE+PB联合_5y_30_70"]
    for k in key_strats:
        if k in mt and "error" not in mt[k]:
            v = mt[k]
            lines.append(f"| {k.replace('_', ' ')} | {v['annual_return']:.1f}% | {v['max_drawdown']:.1f}% | {v['sharpe']:.2f} | {v['calmar']:.2f} | {v['win_rate']:.1f}% |")
    lines.append(f"")

    # Find best PB and PE
    best_pb = max([(k, v) for k, v in mt.items() if "PB_" in k and "error" not in v],
                  key=lambda x: x[1]["annual_return"], default=(None, None))
    best_pe = max([(k, v) for k, v in mt.items() if "PE_" in k and "error" not in v],
                  key=lambda x: x[1]["annual_return"], default=(None, None))

    lines.append(f"### 2.2 关键发现")
    lines.append(f"")
    if best_pb[1]:
        lines.append(f"**PB择时大幅胜出**: 最佳参数PB_10y_30_70年化{best_pb[1]['annual_return']:.1f}%，回撤{best_pb[1]['max_drawdown']:.1f}%，夏普{best_pb[1]['sharpe']:.2f}。")
        lines.append(f"相比买入持有(年化5.2%/回撤46.3%)，收益提升{best_pb[1]['annual_return']-5.2:.1f}个百分点，回撤减半。")
    lines.append(f"")
    if best_pe[1]:
        lines.append(f"**PE择时效果一般**: 最佳PE参数年化{best_pe[1]['annual_return']:.1f}%，仅略优于买入持有。PE受盈利周期影响大——盈利下滑时PE反而升高，"
                     f"给出错误的卖出信号。")
    lines.append(f"")
    lines.append(f"**核心结论**: A股宽基指数择时，PB是比PE更好的估值指标。PB=净资产是磐石(稳定)，PE=盈利是流水(波动)。")
    lines.append(f"")

    # Chapter 3: PE/PB parameter sweep
    lines.append(f"### 2.3 PE参数扫描")
    lines.append(f"")
    lines.append(f"| 窗口 | 阈值 | 年化收益 | 回撤 | 夏普 |")
    lines.append(f"|------|------|----------|------|------|")
    for k, v in sorted(mt.items()):
        if "PE_" in k and "error" not in v:
            parts = k.split("_")
            lines.append(f"| {parts[1]} | {parts[2]} | {v['annual_return']:.1f}% | {v['max_drawdown']:.1f}% | {v['sharpe']:.2f} |")
    lines.append(f"")

    lines.append(f"### 2.4 PB参数扫描")
    lines.append(f"")
    lines.append(f"| 窗口 | 阈值 | 年化收益 | 回撤 | 夏普 |")
    lines.append(f"|------|------|----------|------|------|")
    for k, v in sorted(mt.items()):
        if "PB_" in k and "error" not in v:
            parts = k.split("_")
            lines.append(f"| {parts[1]} | {parts[2]} | {v['annual_return']:.1f}% | {v['max_drawdown']:.1f}% | {v['sharpe']:.2f} |")
    lines.append(f"")

    # Chapter 4: Sector Level
    lines.append(f"## 3. 行业层面 — 估值代理(反转) vs 动量")
    lines.append(f"")
    lines.append(f"**回测周期**: 2021-02 ~ 2026-06 · 标的: 证券/酒/芯片/新能源/传媒 ETF")
    lines.append(f"**说明**: 行业ETF没有PE/PB时间序列，用反转策略(买入跌最惨的行业)作为低估值代理。")
    lines.append(f"")
    lines.append(f"### 3.1 策略对比")
    lines.append(f"")
    lines.append(f"| 策略 | 年化收益 | 回撤 | 夏普 | 卡玛 |")
    lines.append(f"|------|----------|------|------|------|")

    key_sector = ["等权持有", "反转1月_hold3", "反转6月_hold3", "动量12月_hold2", "动量6月_hold3"]
    for k in key_sector:
        if k in sr and "error" not in sr[k]:
            v = sr[k]
            lines.append(f"| {k.replace('_', ' ')} | {v['annual_return']:.1f}% | {v['max_drawdown']:.1f}% | {v['sharpe']:.2f} | {v['calmar']:.2f} |")
    lines.append(f"")

    lines.append(f"### 3.2 全量参数扫描")
    lines.append(f"")
    lines.append(f"| 策略 | 回看窗口 | 持仓数 | 年化收益 | 回撤 | 夏普 |")
    lines.append(f"|------|----------|--------|----------|------|------|")
    for k, v in sorted(sr.items()):
        if "error" not in v and k != "等权持有" and "_" in k:
            parts = k.split("_")
            if len(parts) >= 3:
                lines.append(f"| {parts[0]} | {parts[1]} | {parts[2]} | {v['annual_return']:.1f}% | {v['max_drawdown']:.1f}% | {v['sharpe']:.2f} |")
    lines.append(f"")

    lines.append(f"### 3.3 行业层面结论")
    lines.append(f"")
    lines.append(f"- 在2021-2026这段A股熊市中，反转策略(买超跌行业)整体优于动量策略(买强势行业)")
    lines.append(f"- 最佳组合: 反转1月hold3 — 年化11.6%，回撤41.2%，夏普0.39")
    lines.append(f"- 但注意数据周期仅5年，结论的统计显著性有限")
    lines.append(f"- 行业层面的PE/PB时间序列缺失，是估值研究的瓶颈")
    lines.append(f"")

    # Chapter 5: 实盘建议
    lines.append(f"## 4. 实盘部署建议")
    lines.append(f"")
    lines.append(f"### 宽基估值择时")
    lines.append(f"1. **监控沪深300 PB分位** (推荐10年窗口): PB<30%分位 → 加大权益仓位，PB>70%分位 → 降低权益仓位")
    lines.append(f"2. **PE/PB联合使用**: PE和PB信号取均值，降低单一指标误判")
    lines.append(f"3. **不要频繁调仓**: 月频足够，日频会过度交易")
    lines.append(f"4. **债券端**: 国债ETF(511010)作为防御资产")
    lines.append(f"")
    lines.append(f"### 行业配置")
    lines.append(f"1. **不要仅看PE/PB选行业**: 行业PE低可能是盈利陷阱(如周期股盈利见顶)")
    lines.append(f"2. **结合动量和质量**: 低PB+正向动量+ROE质量 = 更稳健的多因子框架")
    lines.append(f"3. **注意数据周期**: 5年行业回测太短，结论需保守对待")
    lines.append(f"")

    # Disclaimer
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 免责声明")
    lines.append(f"")
    lines.append(f"⚠️ **本报告仅供研究参考，不构成任何投资建议。**")
    lines.append(f"")
    lines.append(f"- 历史回测不代表未来表现")
    lines.append(f"- 策略参数可能过拟合")
    lines.append(f"- 实际交易存在滑点、流动性、冲击成本等")
    lines.append(f"- 投资有风险，入市需谨慎")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*本报告由AI量化研究系统自动生成 · {XHS_ID}*")
    lines.append(f"")

    return "\n".join(lines)


def build_readme(data):
    """生成免费版README"""
    mt = data["market_timing"]
    sr = data["sector_rotation"]

    best_pb = max([(k, v) for k, v in mt.items() if "PB_" in k and "error" not in v],
                  key=lambda x: x[1]["annual_return"], default=(None, None))
    best_sector = max([(k, v) for k, v in sr.items() if "error" not in v and "反转" in k],
                      key=lambda x: x[1]["annual_return"], default=(None, None))

    lines = []
    lines.append("# PE/PB估值择时研究 — PE/PB判断行业买点靠谱吗？")
    lines.append("")
    lines.append("## 一句话结论")
    lines.append("")
    lines.append(f"**PB比PE靠谱得多！** 宽基PB 10年分位择时年化{best_pb[1]['annual_return']:.1f}%，回撤减半。行业层面反转策略(买超跌)优于动量。")
    lines.append("")
    lines.append("## 核心数据")
    lines.append("")
    lines.append("| | PB择时 | PE择时 | 买入持有 |")
    lines.append("|---|---|---|---|")
    pb_val = mt.get("PB_10y_30_70", {})
    pe_val = mt.get("PE_5y_30_70", {})
    bh_val = mt.get("买入持有", {})
    lines.append(f"| 年化收益 | {pb_val.get('annual_return', 0):.1f}% | {pe_val.get('annual_return', 0):.1f}% | {bh_val.get('annual_return', 0):.1f}% |")
    lines.append(f"| 最大回撤 | {pb_val.get('max_drawdown', 0):.1f}% | {pe_val.get('max_drawdown', 0):.1f}% | {bh_val.get('max_drawdown', 0):.1f}% |")
    lines.append(f"| 夏普 | {pb_val.get('sharpe', 0):.2f} | {pe_val.get('sharpe', 0):.2f} | {bh_val.get('sharpe', 0):.2f} |")
    lines.append("")
    lines.append("## 9张小红书卡片")
    lines.append("")
    for i, card in enumerate(["封面", "科普", "PE/PB热力图", "PB最佳净值", "PE最差净值",
                                "行业反转vs动量", "分年度对比", "结论", "排行榜"], 1):
        fn = [f for f in sorted((DATA_DIR / "xhs_cards").glob("*.png")) if f"0{i-1 if i>1 else '0'}" in f.stem]
        if fn:
            lines.append(f"{i}. {card} — `{fn[0].name}`")
    lines.append("")
    lines.append(f"## 文件清单")
    lines.append(f"")
    lines.append(f"```")
    lines.append(f"output/pe_pb_research/")
    lines.append(f"├── results.json          # 全量回测结果")
    lines.append(f"├── README.md             # 本文件 (免费)")
    lines.append(f"├── paid_report.md        # 付费研报Markdown")
    lines.append(f"├── paid_report.pdf       # 无水印PDF")
    lines.append(f"├── watermarked.pdf       # 水印版PDF")
    lines.append(f"├── xhs_cards/            # 9张小红书卡片PNG")
    lines.append(f"└── xhs_copy.md           # 小红书文案")
    lines.append(f"```")
    lines.append("")
    lines.append("---")
    lines.append(f"*{XHS_ID} · 2026年6月*")

    return "\n".join(lines)


def save_files():
    data = load_data()

    # Save README
    readme_md = build_readme(data)
    (DATA_DIR / "README.md").write_text(readme_md, encoding="utf-8")
    print(f"✓ README.md")

    # Save paid report markdown
    paid_md = build_paid_md(data)
    (DATA_DIR / "paid_report.md").write_text(paid_md, encoding="utf-8")
    print(f"✓ paid_report.md")

    return data


def md_to_pdf():
    """Convert paid_report.md to PDF using weasyprint"""
    from markdown_it import MarkdownIt
    from weasyprint import HTML

    md_content = (DATA_DIR / "paid_report.md").read_text(encoding="utf-8")
    md = MarkdownIt('commonmark', {'html': True}).enable('table')
    html_body = md.render(md_content)

    font_dir = str(FONT_DIR)
    css = f"""
    @page {{ size: A4; margin: 2cm; }}
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
        font-size: 12pt;
        line-height: 1.8;
        color: #1a1a1a;
    }}
    h1, h2, h3 {{
        font-family: 'SansSC', sans-serif;
        color: #2c3e50;
    }}
    h1 {{ font-size: 22pt; border-bottom: 3px solid #f0b866; padding-bottom: 8px; }}
    h2 {{ font-size: 16pt; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }}
    h3 {{ font-size: 14pt; margin-top: 20px; }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 10pt;
        font-family: 'SansSC', sans-serif;
    }}
    th, td {{
        border: 1px solid #ddd;
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
    }}
    tr:nth-child(even) {{ background-color: #f8f9fa; }}
    strong {{ color: #e67e22; }}
    blockquote {{
        border-left: 4px solid #f0b866;
        padding-left: 16px;
        color: #555;
        margin: 16px 0;
    }}
    hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
    """

    html_full = f"<!DOCTYPE html><html><head><meta charset=\"utf-8\"><style>{css}</style></head><body>{html_body}</body></html>"

    pdf_path = DATA_DIR / "paid_report.pdf"
    HTML(string=html_full).write_pdf(str(pdf_path))
    size_kb = pdf_path.stat().st_size / 1024
    print(f"✓ paid_report.pdf ({size_kb:.0f} KB)")


def add_watermark():
    """Add watermark to PDF"""
    # Check if watermark script exists
    wm_script = Path(__file__).parent / "add_watermark.py"
    if wm_script.exists():
        sys.path.insert(0, str(wm_script.parent))
        from add_watermark import add_watermark_to_pdf
        src = str(DATA_DIR / "paid_report.pdf")
        dst = str(DATA_DIR / "watermarked.pdf")
        add_watermark_to_pdf(src, dst, f"付费专享 · {XHS_ID}")
        size_kb = Path(dst).stat().st_size / 1024
        print(f"✓ watermarked.pdf ({size_kb:.0f} KB)")
    else:
        print("⚠ watermark script not found, skipping")


def main():
    print("📝 Generating PE/PB Research Paid Report...")
    print()

    save_files()
    print()

    try:
        md_to_pdf()
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()

    print()

    try:
        add_watermark()
    except Exception as e:
        print(f"❌ Watermark failed: {e}")


if __name__ == "__main__":
    main()
