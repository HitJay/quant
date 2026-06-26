"""现金流反共识 — 付费深度研报 PDF (reportlab) — 2026-06-26.

输入: output/2026-06-26/fcf-contrarian/data/summary.json + figures/*.png
输出: output/2026-06-26/fcf-contrarian/现金流反共识深度研报.pdf
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

ROOT = Path("/das/user/QYJI/quant/output/2026-06-26/fcf-contrarian")
FIGS = ROOT / "figures"
DATA = ROOT / "data"
PDF = ROOT / "现金流反共识深度研报.pdf"
S = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

# ── 配色 ──
NAVY = colors.HexColor("#10243e")
# A 股配色: 红 = 涨/正, 绿 = 跌/负 (与美股相反)
# RED/GREEN 这两个名字保留 (避免大规模重命名), 但语义已对齐 A 股
# RED 字面是红色 hex, 用于涨幅/正值; GREEN 字面是绿色 hex, 用于跌幅/负值
RED = colors.HexColor("#dc2626")    # 涨幅 / 正值 / 利好
GREEN = colors.HexColor("#16a34a")  # 跌幅 / 负值 / 警示
ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb")
GOLD = colors.HexColor("#b8860b")
GRAY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#eef2f7")
CREAM = colors.HexColor("#fff8e7")
INK = colors.HexColor("#2d2d2d")

# ── 样式 ──
H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=24, textColor=NAVY,
                    alignment=1, leading=32, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=12.5, textColor=GRAY,
                     alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white,
                    backColor=NAVY, leading=26, spaceBefore=18, spaceAfter=12,
                    leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY,
                    leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK,
                      leading=18, spaceAfter=7, alignment=0)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16,
                        bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY,
                     alignment=1, leading=12, spaceAfter=10)
QUOTE = ParagraphStyle("QUOTE", fontName="CN", fontSize=10.5, textColor=NAVY,
                       leading=18, leftIndent=14, rightIndent=14, spaceAfter=8,
                       borderPadding=(8, 8, 8, 10), backColor=CREAM,
                       borderColor=GOLD, borderWidth=0)


def pct(v, digits=1):
    if v is None:
        return "N/A"
    return f"{v*100:+.{digits}f}%"


def watermark(c, d):
    c.saveState()
    c.setFont("CN", 60)
    c.setFillColor(colors.HexColor("#eef0f3"))
    c.translate(A4[0] / 2, A4[1] / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "付费研报 PAID")
    c.restoreState()


def on_first(c, d):
    watermark(c, d)
    # 顶部线
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.line(2 * cm, A4[1] - 1.5 * cm, A4[0] - 2 * cm, A4[1] - 1.5 * cm)
    # 底部
    c.setFont("CN", 8)
    c.setFillColor(GRAY)
    c.drawString(2 * cm, 1.2 * cm, "现金流反共识深度研报 · 复旦杰伦 · 2026-06-26")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"第 {d.page} 页")
    c.setFont("CN", 7.5)
    c.drawString(2 * cm, 0.8 * cm,
                 "* 本报告基于公开数据回测分析 · 不构成投资建议 · 投资有风险, 入市需谨慎")


def on_later(c, d):
    watermark(c, d)
    # 页眉
    c.setStrokeColor(GRAY)
    c.setLineWidth(0.4)
    c.line(2 * cm, A4[1] - 1.2 * cm, A4[0] - 2 * cm, A4[1] - 1.2 * cm)
    c.setFont("CN", 8.5)
    c.setFillColor(NAVY)
    c.drawString(2 * cm, A4[1] - 0.9 * cm, "现金流反共识深度研报")
    c.setFillColor(GRAY)
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 0.9 * cm,
                      "数据截至 2026-06-25  ·  复旦杰伦")
    # 页脚
    c.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    c.setFont("CN", 8)
    c.setFillColor(GRAY)
    c.drawString(2 * cm, 1.0 * cm,
                 "* 历史回测不代表未来 · 不构成投资建议 · 投资有风险, 入市需谨慎")
    c.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f"第 {d.page} 页")


# ============ Build flowables ============
story = []

# ============ Page 1: 封面 ============
story.append(Spacer(1, 1.8 * cm))
story.append(Paragraph("自由现金流 ETF 反共识深度研报", H1))
story.append(Paragraph("发布即顶点 · 同名实异 · 散户被名字坑惨了", SUB))
story.append(Spacer(1, 1.5 * cm))

# 三个核心数字大字
hero_data = [[
    Paragraph(f'<font name="CN-B" size="34" color="#16a34a">{pct(S["headline"]["fcf_index_60d"])}</font>', BODY),
    Paragraph(f'<font name="CN-B" size="34" color="#2563eb">{pct(S["headline"]["fcf_index_dd"])}</font>', BODY),
    Paragraph(f'<font name="CN-B" size="34" color="#b8860b">{pct(S["headline"]["dvd_lowvol_60d"])}</font>', BODY),
], [
    Paragraph('<font size="9" color="#666">国证 现金流指数<br/>近 60 日</font>', BODY),
    Paragraph('<font size="9" color="#666">距 ATH<br/>2026-03 见顶</font>', BODY),
    Paragraph('<font size="9" color="#666">红利低波 100<br/>同期对比</font>', BODY),
]]
ht = Table(hero_data, colWidths=[5.5 * cm] * 3, rowHeights=[2.0 * cm, 1.1 * cm])
ht.setStyle(TableStyle([
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafbfc")),
]))
story.append(ht)
story.append(Spacer(1, 1.5 * cm))

story.append(Paragraph(
    '本报告系统量化了 5 只\"自由现金流 ETF\"在近期市场剧烈分化背后的真相: '
    '它们看似同质, 实际跟踪不同指数、持仓行业差异巨大; 国证自由现金流指数自'
    '2024-12 发布以来即见顶, 短短 3 个月回撤 22.9%, 远跑输沪深300 (+12.1%) '
    '与红利低波 100 (+21.9%)。本文以数据为核心论据, 拆解\"现金流 = 红利升级版\"的认知误区, '
    '给出可执行的操作策略。',
    BODY
))
story.append(Spacer(1, 0.8 * cm))
story.append(Paragraph(
    '<para alignment="center"><font size="9" color="#666">'
    '数据范围: 2024-12-31 ~ 2026-06-25 · '
    '数据源: akshare (sina/eastmoney)<br/>'
    '作者: 复旦杰伦 (RIC) · 发布日期: 2026-06-26'
    '</font></para>',
    NOTE
))
story.append(PageBreak())

# ============ Page 2: 摘要与核心结论 ============
story.append(Paragraph("一、摘要与核心结论", H2))

bullets = [
    f'<b>结论 1 · 名字 ≠ 因子。</b> 5 只\"自由现金流 ETF\"持仓行业差异最高达 60 个百分点 '
    f'(嘉实 159218 — 军工占比 63% / 易方达 159201 — 汽车+石油石化+家电+航运+钢铁占比 50%+); '
    f'本质是不同的策略, 不能用同一个标签买。',

    f'<b>结论 2 · 发布即顶点。</b> 国证自由现金流指数 2024-12 发布, ETF 集中 2025 年上市 '
    f'(易方达 2-月, 华夏 4-月, 嘉实 5-月, 国新 10-月), 上市后基金抱团推升至 2026-03 顶点 6227, '
    f'随后 3 个月回撤 {pct(S["headline"]["fcf_index_dd"])}, 击穿历史所有回撤深度。',

    f'<b>结论 3 · 现金流 ≠ 红利。</b> 国证现金流 与中证红利低波 100 的 120 日相关性仅 '
    f'{S["correlation_fcf_vs_bench"]["vs_dividend_lowvol"]:.2f}, 跑势差距 '
    f'{(S["headline"]["fcf_index_60d"] - S["headline"]["dvd_lowvol_60d"])*100:.1f} 个百分点; '
    f'连\"红利打沪深300\"在 14 年长跑里都不成立 (红利年化 +3.2% < 沪深300 +4.8%), 何况 现金流。',

    f'<b>结论 4 · 当前不是无脑抄底位。</b> 国证 现金流指数发布以来仅 18 个月样本, 当前回撤 '
    f'-22.9% 已是历史最深, 但样本不足无法判断这是\"地板\"还是\"半山腰\"; '
    f'真实风险在持仓: 159201/159222 的周期权重 50%+, 与全球大宗商品周期高度绑定。',

    f'<b>结论 5 · 区分产品 + 分批进场 + 红利低波对冲。</b> 想吃 现金流因子选大池子 (980092 跟踪标的 '
    f'159201/159222 重合 90%); 避开\"伪"现金流"\" (159218 实际军工); 不要一次性梭哈, 分批进场, '
    f'仓位与红利低波 100 配对降低风格切换风险。',
]
for b in bullets:
    story.append(Paragraph(f"• {b}", BULLET))

story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph(
    "<b>诚实声明:</b> 国证自由现金流指数 (sz980092) 发布日为 2024-12-23, 至今仅 363 个交易日 (~18 个月), "
    "样本量严重不足, 本报告无法做严格意义的长期胜率回测; 所有结论以\"近期表现 + 持仓归因 + 跨资产对比\""
    "为主要证据。读者应将本报告视为\"风险揭示\"而非\"未来收益预测\"。",
    QUOTE
))
story.append(PageBreak())

# ============ Page 3: 研究方法与数据 ============
story.append(Paragraph("二、研究方法与数据", H2))

story.append(Paragraph("2.1 数据来源", H3))
story.append(Paragraph(
    "本报告全部数据来自 akshare 公开接口, 抓取于 2026-06-26:", BODY))
story.append(Paragraph("• ETF 日线 (后复权): ak.fund_etf_hist_sina (新浪源, HPC 稳定)", BULLET))
story.append(Paragraph("• 指数日线: ak.stock_zh_index_daily (新浪源)", BULLET))
story.append(Paragraph("• ETF 持仓: ak.fund_portfolio_hold_em (东财, 2026 Q1 季报)", BULLET))
story.append(Paragraph(
    f"• 样本范围: 现金流 ETF 自上市日至 2026-06-25; 沪深300/红利 ETF 共同窗口 "
    f"{S['long_term_dvd_vs_300']['window_start']} ~ {S['long_term_dvd_vs_300']['window_end']} ({S['long_term_dvd_vs_300']['years']} 年)",
    BULLET
))

story.append(Paragraph("2.2 分析方法", H3))
story.append(Paragraph(
    "本报告采用三层分析框架:", BODY))
story.append(Paragraph(
    "<b>① 表现分层:</b> 对 5 只 现金流 ETF 计算 1d/5d/20d/60d/YTD 涨跌幅 + 距 ATH 回撤, "
    "对比沪深300/红利 ETF/红利低波 100/煤炭 ETF/资源 ETF 5 个基准。", BULLET))
story.append(Paragraph(
    "<b>② 持仓归因:</b> 提取每只 ETF 2026 Q1 季报前 10 大持仓, "
    "按申万行业手动映射, 计算行业权重分布; 揭示\"同名实异\"的本质。", BULLET))
story.append(Paragraph(
    "<b>③ 风格相关性:</b> 取最近 120 个交易日各 ETF 日收益率, 计算与基准的 Pearson 相关系数, "
    "判断 现金流 究竟更接近哪一类风格。", BULLET))

story.append(Paragraph("2.3 分析的局限", H3))
story.append(Paragraph(
    "(1) 现金流指数样本期仅 18 个月, 无法做严格滚动起点胜率回测; "
    "(2) 持仓数据基于 2026 Q1 季报, 存在 1-3 个月滞后, "
    "实际持仓可能已有变动; "
    "(3) 行业映射基于手动 SECTOR_MAP 覆盖前 10 大持仓, 未覆盖的尾部持仓被归类为\"未披露\"; "
    "(4) 跨样本期的相关性窗口 120 日是惯例选择, 改窗口 (60/250 日) 结果可能不同; "
    "(5) 本报告不构成投资建议, 历史规律不代表未来。",
    NOTE
))
story.append(PageBreak())

# ============ Page 4: 表现分层 ============
story.append(Paragraph("三、主结论① 5 只 ETF 表现两极分化", H2))

story.append(Image(str(FIGS / "fig_5etfs.png"), width=16 * cm, height=8.8 * cm))
story.append(Paragraph("图 1 · 5 只 现金流 ETF 近 60 日表现 (浅色版)", CAP))

# 表格: 5 只 + 6 项指标
tab_data = [
    ["代码", "名称", "20d", "60d", "YTD", "距 ATH"],
]
for code, name, brand in [
    ("562340", "中证自由现金流ETF", "华泰柏瑞"),
    ("159201", "国证自由现金流ETF", "易方达"),
    ("159222", "自由现金流ETF华夏", "华夏"),
    ("159218", "自由现金流ETF", "嘉实"),
    ("563690", "国新央企现金流ETF", "国新"),
]:
    sym_key = f"sh{code}" if code in ("562340", "563690") else f"sz{code}"
    p = S["fcf_etfs"][sym_key]
    tab_data.append([
        code, name,
        pct(p["ret_20d"]), pct(p["ret_60d"]),
        pct(p["ret_ytd"]), pct(p["cur_dd"]),
    ])

t = Table(tab_data, colWidths=[1.6 * cm, 5.0 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.4 * cm])
ts = TableStyle([
    ("FONT", (0, 0), (-1, -1), "CN", 9.5),
    ("FONT", (0, 0), (-1, 0), "CN-B", 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ALIGN", (1, 1), (1, -1), "LEFT"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
])
# A 股配色: 负值标绿, 正值标红
for i in range(1, len(tab_data)):
    for j in [2, 3, 4, 5]:
        v = tab_data[i][j]
        if v.startswith("-"):
            ts.add("TEXTCOLOR", (j, i), (j, i), GREEN)
        elif v.startswith("+"):
            ts.add("TEXTCOLOR", (j, i), (j, i), RED)
t.setStyle(ts)
story.append(t)
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph(
    f"<b>关键观察:</b> 华泰柏瑞 562340 (跟踪中证自由现金流) 60 日 +17.6%, "
    f"易方达/华夏 (跟踪国证自由现金流) 60 日 ~ -17%, "
    f"两组差距 35 个百分点。同样叫\"自由现金流 ETF\", 表现可以差到\"一个吃肉一个买单\", "
    f"问题根源在跟踪指数不同 + 成份股不同。",
    BODY
))
story.append(PageBreak())

# ============ Page 5: 持仓归因 ============
story.append(Paragraph("四、主结论② 持仓行业归因 — 同名实异", H2))

story.append(Image(str(FIGS / "fig_holdings.png"), width=17 * cm, height=7.7 * cm))
story.append(Paragraph("图 2 · 5 只 现金流 ETF 前 10 大持仓行业归类 (灰色为未披露/前 10 之外)", CAP))

story.append(Paragraph(
    "持仓数据 (2026 Q1 季报) 揭示了\"同名实异\"的本质:", BODY))

story.append(Paragraph(
    "<b>组 A · 国证流派 (易方达 159201 + 华夏 159222):</b> "
    "前 10 大持仓重合度 90% — 上汽集团 9.9% + 中国海油 9.8% + 格力电器 9.6% + "
    "中远海控 4.6% + 长城汽车 3.6% + 宝钢 3.3% + 中国铝业 3.0% + 中国联通 3.0% + 潍柴动力 2.9%。"
    "汽车 + 石油石化 + 家电 + 航运 + 钢铁 + 有色合计 50%+, 是周期股扎堆的\"红利+周期\"混合组合。",
    BULLET
))
story.append(Paragraph(
    "<b>组 B · 嘉实流派 (159218):</b> 前 10 大持仓 63% 是军工 — 航天电子 12.7% + "
    "中国卫星 11.8% + 中国卫通 6.8% + ST臻镭 6.2% + 中科星图 6.0% + 国博电子 4.9% + "
    "华测导航 4.5% + 北斗星通 4.0% + 北方导航 3.8% + 四维图新 2.7%。"
    "本质是\"卫星+导航+军工\"产业链, 与现金流因子的关联非常弱。",
    BULLET
))
story.append(Paragraph(
    "<b>组 C · 华泰柏瑞流派 (562340):</b> 跟踪中证自由现金流指数 (区别于国证), "
    "重仓有色金属 + 半导体 — 厦门钨业 + 天山铝业 + 西部矿业 + 湖南黄金 (合计 10%+) + "
    "通富微电 + 睿创微纳 (半导体)。这是\"有色+半导体\"双因子组合。",
    BULLET
))
story.append(Paragraph(
    "<b>组 D · 央企流派 (563690):</b> 前 10 大持仓集中在央企银行 + 央企能源 — "
    "上海银行 + 南京银行 + 平安银行 + 沪农商行 + 中国海油 + 中国石油, 银行占比 12.7%+。"
    "本质是\"央企红利+央企能源\"组合, 与红利 ETF 重叠度最高。",
    BULLET
))
story.append(Paragraph(
    "<b>提示:</b> 4 个流派对应 4 类完全不同的风险敞口。投资前必须看穿名字, "
    "查跟踪指数 + 看前 10 持仓 + 看行业权重 — 这是基本动作。",
    QUOTE
))
story.append(PageBreak())

# ============ Page 6: 净值对比 + 发布即顶 ============
story.append(Paragraph("五、主结论③ 发布即顶点 — 净值曲线还原", H2))

story.append(Image(str(FIGS / "fig_nav.png"), width=16 * cm, height=8.8 * cm))
story.append(Paragraph("图 3 · 国证 现金流指数 vs 沪深300 vs 红利低波 100 净值 (起点对齐 = 100)", CAP))

story.append(Paragraph(
    "国证自由现金流指数 (sz980092) 自 2024-12-23 发布起的 18 个月轨迹:",
    BODY
))
events_data = [
    ["日期", "事件", "指数"],
    ["2024-12-23", "国证自由现金流指数发布", "6010"],
    ["2025-02-27", "易方达 159201 上市", "5400"],
    ["2025-04-17", "华夏 159222 上市", "5700"],
    ["2025-05-22", "嘉实 159218 上市", "5500"],
    ["2025-10-10", "国新 563690 上市", "5800"],
    ["2026-03-12", "指数到顶 ATH 6227", "6227"],
    ["2026-06-25", "今日 (距 ATH -22.9%)", "4799"],
]
et = Table(events_data, colWidths=[3.0 * cm, 9.0 * cm, 3.0 * cm])
et.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), "CN", 9.5),
    ("FONT", (0, 0), (-1, 0), "CN-B", 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ALIGN", (1, 1), (1, -1), "LEFT"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    # 关键节点高亮
    ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#fef3c7")),
    ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#fee2e2")),
]))
story.append(et)
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph(
    "<b>叙事:</b> 指数发布后小幅震荡, ETF 集中 2025 年上市, 资金推升指数, "
    "至 2026-03-12 创出 ATH 6227, 随后 3 个多月回撤 22.9% 至 4799。"
    "整个生命周期中, 散户在 ETF 上市后买入的占大多数 — "
    "如果在 2026-03 顶点附近建仓, 到 2026-06-25 已浮亏 22-23%。",
    BODY
))

story.append(Paragraph(
    "<b>这是\"回测过拟合 + 实盘踩坑\"的教科书案例。</b> "
    "指数编制机构基于历史数据做出来的高夏普因子组合, 发布之后真实资金涌入, 估值被快速推升, "
    "随后基本面不及预期 + 风格切换, 估值回归 — 这是网红指数的常见命运。",
    QUOTE
))
story.append(PageBreak())

# ============ Page 7: 回撤诊断 ============
story.append(Paragraph("六、主结论④ 当前位置诊断", H2))

story.append(Image(str(FIGS / "fig_drawdown.png"), width=17 * cm, height=10 * cm))
story.append(Paragraph("图 4 · 国证 现金流指数价格 + 回撤双面板", CAP))

dd_stats = S["fcf_index_drawdown_stats"]
story.append(Paragraph(
    f"<b>当前回撤 {dd_stats['current_dd']*100:+.2f}%</b>, 是指数发布以来"
    f" {dd_stats['sample_days']} 个交易日中最深的回撤; "
    f"历史 (短样本) 回撤中位 {dd_stats['median_dd']*100:+.2f}%, "
    f"当前已击穿所有历史样本的深度。",
    BODY
))

story.append(Paragraph("6.1 三个客观信号", H3))
sig_data = [
    ["信号", "数值", "解读", "评级"],
    ["回撤深度", f"{dd_stats['current_dd']*100:+.1f}%",
     "已超指数发布以来全部回撤", "WARN"],
    ["与红利低波相关性",
     f"{S['correlation_fcf_vs_bench']['vs_dividend_lowvol']:.2f}",
     "弱相关 · 现金流 不能替代红利", "NEUTRAL"],
    ["与煤炭 ETF 相关性",
     f"{S['correlation_fcf_vs_bench']['vs_coal']:.2f}",
     "弱-中相关 · 周期股暴露",  "WATCH"],
    ["与沪深 300 相关性",
     f"{S['correlation_fcf_vs_bench']['vs_hs300']:.2f}",
     "中相关 · 大盘风险敞口", "NEUTRAL"],
]
st = Table(sig_data, colWidths=[4.0 * cm, 3.0 * cm, 6.5 * cm, 2.5 * cm])
st.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), "CN", 9.5),
    ("FONT", (0, 0), (-1, 0), "CN-B", 9.5),
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("ALIGN", (2, 1), (2, -1), "LEFT"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    # 警示色
    ("TEXTCOLOR", (3, 1), (3, 1), ORANGE),
    ("TEXTCOLOR", (3, 2), (3, 2), BLUE),
    ("TEXTCOLOR", (3, 3), (3, 3), ORANGE),
    ("TEXTCOLOR", (3, 4), (3, 4), BLUE),
]))
story.append(st)
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph(
    "<b>结论:</b> 不能机械地用\"回撤 22.9% 即抄底\"做判断。样本不足 18 个月, "
    "我们既看不到\"历史这个深度入场后 1/3/5 年的胜率\", 也无法判断这是周期股估值回归的中段还是末段。"
    "更糟的是, 159201/159222 的持仓中, 周期股 + 资源股 + 汽车合计占 50%+, "
    "如果全球大宗商品周期进一步下行, 仍有进一步下跌空间。",
    BODY
))
story.append(PageBreak())

# ============ Page 8: 操作策略 ============
story.append(Paragraph("七、给个人投资者的实操手册", H2))

story.append(Paragraph("7.1 买之前必做的 3 个动作", H3))
story.append(Paragraph(
    "<b>① 查跟踪指数。</b> 5 只 现金流 ETF 跟踪 3 条不同指数 (国证 980092 / 中证自由现金流 / "
    "国新央企现金流), 跟踪指数决定一切, 名字只是营销。",
    BULLET))
story.append(Paragraph(
    "<b>② 看前 10 持仓 + 行业归类。</b> 在天天基金/各家公司官网查最新季报, "
    "把前 10 持仓按行业聚合, 看你想买的到底是周期/军工/有色/还是央企。",
    BULLET))
story.append(Paragraph(
    "<b>③ 对比规模与流动性。</b> 易方达 159201 + 华夏 159222 是双胞胎 (跟踪同一指数), "
    "选规模大的那只 (流动性好, 折溢价小)。",
    BULLET))

story.append(Paragraph("7.2 仓位与节奏", H3))
story.append(Paragraph(
    "鉴于当前样本不足无法判断真正底部, 建议:", BODY))
story.append(Paragraph(
    "<b>不要单笔重仓。</b> 想配置者, 从当前价分批进场:", BULLET))
story.append(Paragraph(
    "&nbsp;&nbsp;&nbsp;&nbsp;首批 50% — 现价 (4799 附近)<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;第二批 30% — 再跌 10% (~4320) 加仓<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;第三批 20% — 再跌 10% (~3890) 补仓",
    BODY
))
story.append(Paragraph(
    "<b>用红利低波 100 (sz159211) 做风格对冲。</b> 相关性 0.42, 是良好的负相关性对冲标的。"
    "现金流与红利低波 1:1 配对, 可在风格切换中降低净值波动。",
    BULLET
))

story.append(Paragraph("7.3 退出信号", H3))
story.append(Paragraph(
    "<b>止损:</b> 国证 现金流指数跌破 4500 (距今再跌 6%, 距 ATH -28%) 触发减仓; "
    "跌破 4000 (距今 -17%, 距 ATH -36%) 触发全部清仓。",
    BULLET))
story.append(Paragraph(
    "<b>止盈:</b> 单次反弹 +15% 减仓 1/3; 国证现金流 重回 5500 (距 ATH -12%) 减仓一半; "
    "重回 6000 以上分批清仓。",
    BULLET))
story.append(Paragraph(
    "<b>风格切换信号:</b> 红利低波 ETF 跑输 现金流 超过 5pp 连续 1 个月 → 风格切换, 全部转入现金流; "
    "反之亦然。",
    BULLET))

story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    "<b>核心原则:</b> 任何\"网红 ETF\" — 在指数发布后 12 个月内成立的产品都要警惕, "
    "因为它的指数没有任何真实 out-of-sample 数据。等过了 2-3 个完整的市场周期, "
    "再判断这个因子是真本事还是回测过拟合。",
    QUOTE
))
story.append(PageBreak())

# ============ Page 9: 局限 + 免责 + 复现说明 ============
story.append(Paragraph("八、局限、免责与复现说明", H2))

story.append(Paragraph("8.1 报告局限", H3))
story.append(Paragraph(
    "(1) <b>样本严重不足:</b> 国证自由现金流指数发布以来 18 个月, 全部数据点都在同一个市场周期内, "
    "无法做跨周期胜率回测; 任何\"历史规律\"声明在此处都不可靠。",
    BULLET))
story.append(Paragraph(
    "(2) <b>持仓滞后:</b> 2026 Q1 季报数据有 1-3 个月滞后, "
    "实际持仓可能已经因为基金经理调仓而变化, 行业归因结论仅供参考。",
    BULLET))
story.append(Paragraph(
    "(3) <b>行业映射粗糙:</b> SECTOR_MAP 是手动维护的简化映射, "
    "未覆盖的尾部持仓 (前 10 之外) 全部归类\"未披露/其他\"; 实际行业分布可能与图表略有差异。",
    BULLET))
story.append(Paragraph(
    "(4) <b>相关性窗口主观:</b> 120 日是惯例选择, 改窗口 (60 / 250 日) 数字会变, "
    "但不影响 现金流 ≠ 红利的核心结论。",
    BULLET))
story.append(Paragraph(
    "(5) <b>未做条件胜率:</b> 因为样本不足以分位回测, 本报告未包含\"回撤 X% 入场后 N 年胜率\""
    "的传统条件胜率分析。",
    BULLET))

story.append(Paragraph("8.2 免责声明", H3))
story.append(Paragraph(
    "本报告基于公开数据 (akshare 接口) 的量化分析, 数据可能存在抓取错误、接口口径变化等问题。"
    "所有结论和数字仅为研究性观点, <b>不构成任何投资建议或买卖推荐</b>。"
    "投资有风险, 入市需谨慎。读者应根据自身风险承受能力和投资目标独立决策, "
    "并在必要时咨询专业投资顾问。本报告作者不对依据本报告所做的任何投资决策及其后果承担责任。",
    BODY
))

story.append(Paragraph("8.3 复现说明", H3))
story.append(Paragraph(
    "本报告完全基于以下代码可复现:", BODY))
story.append(Paragraph(
    "<font name=\"CN\" size=\"9.5\">"
    "&nbsp;&nbsp;&nbsp;&nbsp;analysis/fcf_contrarian_fetch.py   # 数据抓取<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;analysis/fcf_contrarian_analyze.py # 分析+summary.json<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;analysis/fcf_contrarian_figures.py # 浅色研报图<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;analysis/fcf_contrarian_cards.py   # 深色小红书卡片<br/>"
    "&nbsp;&nbsp;&nbsp;&nbsp;analysis/fcf_contrarian_report.py  # 本 PDF (reportlab)"
    "</font>",
    BODY
))
story.append(Paragraph(
    "环境: conda env 'research' (Python 3.11, akshare, pandas, matplotlib, reportlab)。"
    "运行需要 HPC 网络环境 + Droid Sans Fallback 字体 + 新浪财经接口可达。",
    NOTE
))

story.append(Spacer(1, 0.4 * cm))
story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    '<para alignment="center"><font size="9" color="#666">'
    '现金流反共识深度研报 · 复旦杰伦 (RIC)<br/>'
    '数据截至 2026-06-25 · 发布日期 2026-06-26<br/>'
    '联系方式: 小红书 @复旦杰伦'
    '</font></para>',
    NOTE
))

# Build PDF
doc = SimpleDocTemplate(
    str(PDF), pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2.2 * cm, bottomMargin=2 * cm,
)
doc.build(story, onFirstPage=on_first, onLaterPages=on_later)

import os
size_kb = os.path.getsize(PDF) / 1024
print(f"[OK] PDF -> {PDF}  ({size_kb:.1f} KB)")
