"""创新药三巨头商业模式详解 · 7 页小红书卡片 (matplotlib, 复用 xhs_card_template)

题材: 恒瑞医药 / 药明康德 / 百济神州 — 三种创新药商业模式拆解 + 量化未来趋势
数据: 2025 年报 + 2026 一季报 + 卖方一致预期 (2026.07 汇总)
渲染: xhs_card_template.XHSCard -> 1440x1920 PNG (3:4)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT))
from xhs_card_template import XHSCard, COLORS, Metric

DATE = "20260715"
DAY_HUM = "2026-07-15"
TOPIC = "innovadrug_bizmodel"
VERSION = "v1"
OUT = ROOT / f"output/hotspot/{DATE}/xhs_{TOPIC}_{VERSION}"
OUT.mkdir(parents=True, exist_ok=True)

CARD = XHSCard(total_pages=7, brand="复旦杰伦", source="公司财报/卖方一致预期")

# ── 三家公司核心数据 ──
# 恒瑞医药 600276: 自研创新药 + License-out + NewCo
# 药明康德 603259: 一体化 CRDMO 卖水人
# 百济神州 688235: 全球自主商业化 (去CRO化临床 + 自营欧美销售)


# ════════════════════════════════════════════════════════════════════════
# 通用绘制工具
# ════════════════════════════════════════════════════════════════════════
def kpi_card(ax, x, y, w, h, label, value, sub, color="text", vsize=30, lsize=12.5):
    """小指标卡: 左上标签, 中部大数字, 底部注释"""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
                 facecolor=COLORS["panel"], edgecolor=COLORS["border"], linewidth=1.2,
                 transform=ax.transAxes))
    ax.text(x + w / 2, y + h - 0.030, label, ha="center", va="center", fontsize=lsize,
            color=COLORS["muted"], transform=ax.transAxes)
    ax.text(x + w / 2, y + h * 0.50, value, ha="center", va="center", fontsize=vsize,
            fontweight="bold", color=COLORS[color], transform=ax.transAxes)
    if sub:
        ax.text(x + w / 2, y + 0.026, sub, ha="center", va="center", fontsize=10.5,
                color=COLORS[color], transform=ax.transAxes)


def model_block(ax, x, y, w, h, tag, tag_color, title, lines):
    """商业模式拆解块: 顶部标签+标题, 下方多行要点"""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
                 facecolor=COLORS["panel"], edgecolor=COLORS[tag_color], linewidth=1.6,
                 transform=ax.transAxes))
    ax.text(x + 0.022, y + h - 0.034, tag, ha="left", va="center", fontsize=10.5,
            fontweight="bold", color=COLORS["ink"],
            bbox=dict(boxstyle="round,pad=0.28", fc=COLORS[tag_color], ec="none"),
            transform=ax.transAxes)
    ax.text(x + 0.085, y + h - 0.034, title, ha="left", va="center", fontsize=15.5,
            fontweight="bold", color=COLORS["text"], transform=ax.transAxes)
    for i, ln in enumerate(lines):
        ax.plot(x + 0.030, y + h - 0.082 - i * 0.043, marker="o", markersize=3.2,
                color=COLORS[tag_color], transform=ax.transAxes)
        ax.text(x + 0.045, y + h - 0.082 - i * 0.043, ln, ha="left", va="center",
                fontsize=11.8, color=COLORS["text"], transform=ax.transAxes)


def metric_row4(ax, metrics, y=0.40):
    xs = [0.145, 0.378, 0.611, 0.845]
    for x, m in zip(xs, metrics):
        ax.text(x, y, m.value, ha="center", va="center", fontsize=27, fontweight="bold",
                color=COLORS[m.color], transform=ax.transAxes)
        ax.text(x, y - 0.045, m.label, ha="center", va="center", fontsize=12,
                color=COLORS["muted"], transform=ax.transAxes)
        if m.sublabel:
            ax.text(x, y - 0.078, m.sublabel, ha="center", va="center", fontsize=10,
                    color=COLORS[m.color], transform=ax.transAxes)


def bar_compare(ax, companies, values, colors, maxv, y_top=0.70, h=0.052, gap=0.13, unit="亿"):
    """横向条形对比: 公司名 + 条 + 数值"""
    for i, (name, val, c) in enumerate(zip(companies, values, colors)):
        y = y_top - i * gap
        ax.text(0.075, y, name, ha="left", va="center", fontsize=14, fontweight="bold",
                color=COLORS["text"], transform=ax.transAxes)
        bw = 0.55 * (val / maxv)
        ax.add_patch(Rectangle((0.275, y - h / 2), bw, h, fc=COLORS[c], alpha=0.85,
                     ec="none", transform=ax.transAxes))
        ax.text(0.275 + bw + 0.012, y, f"{val:.0f}{unit}", ha="left", va="center",
                fontsize=14, fontweight="bold", color=COLORS[c], transform=ax.transAxes)


# ════════════════════════════════════════════════════════════════════════
# P1 封面
# ════════════════════════════════════════════════════════════════════════
def page_1():
    fig, ax = CARD.canvas()
    CARD.title(ax, "创新药 · 深度", "三巨头商业模式", "详解 & 量化未来趋势",
               accent="gold", y1=0.82, size1=30, size2=50)

    ax.text(0.5, 0.695, "同是创新药，赚钱姿势完全不同", ha="center", va="center",
            fontsize=16, color=COLORS["muted"], transform=ax.transAxes)

    # 三家公司定位卡
    comps = [
        ("恒瑞医药", "600276", "自研+授权出海", "red"),
        ("药明康德", "603259", "CRDMO 卖水人", "blue"),
        ("百济神州", "688235", "全球自主商业化", "purple"),
    ]
    for i, (name, code, model, c) in enumerate(comps):
        x = 0.08 + i * 0.307
        ax.add_patch(FancyBboxPatch((x, 0.55), 0.275, 0.135,
                     boxstyle="round,pad=0.012,rounding_size=0.012",
                     facecolor=COLORS["panel"], edgecolor=COLORS[c], linewidth=1.6,
                     transform=ax.transAxes))
        ax.text(x + 0.137, y := 0.55 + 0.115, name, ha="center", va="center", fontsize=16,
                fontweight="bold", color=COLORS["text"], transform=ax.transAxes)
        ax.text(x + 0.137, 0.55 + 0.083, code, ha="center", va="center", fontsize=11,
                color=COLORS["muted"], transform=ax.transAxes)
        ax.text(x + 0.137, 0.55 + 0.040, model, ha="center", va="center", fontsize=12.5,
                fontweight="bold", color=COLORS[c], transform=ax.transAxes)

    # 核心量化指标四连
    metric_row4(ax, [
        Metric("454亿", "药明营收", "blue", "2025 最高"),
        Metric("73%", "百济海外", "purple", "收入全球化"),
        Metric("61.7%", "恒瑞创新药", "red", "占比首破60%"),
        Metric("270亿$", "恒瑞BD", "gold", "授权总盘"),
    ], y=0.44)

    # 趋势金句
    CARD.insight_box(ax, "从「卖青苗」到「自主出海」",
                     "中国创新药正经历三种路径的分野与兑现",
                     bottom=0.20, height=0.13, edge="gold")

    CARD.cta(ax, "详解 3 种商业模式 · 量化未来 3 年趋势", y=0.13, color="cyan", size=17)
    CARD.footer(ax, 1, "公司财报/卖方一致预期 · 不构成投资建议")
    return CARD.save(fig, OUT, 1)


# ════════════════════════════════════════════════════════════════════════
# P2 行业全景: 三大商业模式定位
# ════════════════════════════════════════════════════════════════════════
def page_2():
    fig, ax = CARD.canvas()
    CARD.header(ax, "行业全景 · 三种路径", "同是创新药，三种活法",
                "盈利模式 · 客户结构 · 核心壁垒 一图看懂")

    # 三大模式对比表
    ax.add_patch(FancyBboxPatch((0.06, 0.46), 0.88, 0.34,
                 boxstyle="round,pad=0.012,rounding_size=0.012",
                 facecolor=COLORS["panel"], edgecolor=COLORS["border"], linewidth=1.2,
                 transform=ax.transAxes))
    # 表头
    cols = [("公司", 0.085), ("盈利模式", 0.235), ("客户/市场", 0.475), ("核心壁垒", 0.735)]
    for name, x in cols:
        ax.text(x, 0.785, name, ha="left", va="center", fontsize=12, fontweight="bold",
                color=COLORS["muted"], transform=ax.transAxes)
    ax.plot([0.07, 0.93], [0.765, 0.765], color=COLORS["border"], lw=0.8, transform=ax.transAxes)

    rows = [
        ("恒瑞医药", "自研药国内销售", "red", "国内医院+药企", "24款创新药·研发体系"),
        ("  +授权", "License-out 里程碑", "gold", "GSK/BMS/MSD", "270亿$ 授权盘"),
        ("药明康德", "CRDMO 全链条服务费", "blue", "全球药企(美占72%)", "R→D 飞轮·订单598亿"),
        ("百济神州", "自研药全球自营销售", "purple", "欧美处方集(海外63%)", "去CRO临床·自营渠道"),
    ]
    for i, (name, model, c, client, moat) in enumerate(rows):
        y = 0.715 - i * 0.072
        ax.text(0.085, y, name, ha="left", va="center", fontsize=13.5, fontweight="bold",
                color=COLORS[c], transform=ax.transAxes)
        ax.text(0.235, y, model, ha="left", va="center", fontsize=12.5, color=COLORS["text"],
                transform=ax.transAxes)
        ax.text(0.475, y, client, ha="left", va="center", fontsize=12.5, color=COLORS["muted"],
                transform=ax.transAxes)
        ax.text(0.735, y, moat, ha="left", va="center", fontsize=12.5, color=COLORS["text"],
                transform=ax.transAxes)
        if i < len(rows) - 1:
            ax.plot([0.07, 0.93], [y - 0.035, y - 0.035], color=COLORS["border"], lw=0.4,
                    alpha=0.5, transform=ax.transAxes)

    # 三种模式一句话画像
    cards = [
        ("恒瑞", "转型派", "以前仿制药养研发\n现在创新药养退休金", "red"),
        ("药明", "卖水人", "你研发新药我收服务费\nGLP-1 卖铲人", "blue"),
        ("百济", "出海派", "不做国内内卷\n直接卖到欧美处方集", "purple"),
    ]
    for i, (name, role, desc, c) in enumerate(cards):
        x = 0.06 + i * 0.31
        ax.add_patch(Rectangle((x, 0.25), 0.285, 0.165, fc=COLORS[c], alpha=0.14,
                     ec=COLORS[c], lw=1.6, transform=ax.transAxes))
        ax.text(x + 0.142, 0.395, name, ha="center", va="center", fontsize=16,
                fontweight="bold", color=COLORS[c], transform=ax.transAxes)
        ax.text(x + 0.142, 0.355, role, ha="center", va="center", fontsize=12.5,
                color=COLORS["muted"], transform=ax.transAxes)
        ax.text(x + 0.142, 0.305, desc, ha="center", va="center", fontsize=11.5,
                color=COLORS["text"], transform=ax.transAxes)

    CARD.insight_box(ax, "创新药 ≠ 一种生意",
                     "卖药 / 卖服务 / 卖全球 — 选哪条路决定估值天花板",
                     bottom=0.075, height=0.12, edge="gold")
    CARD.footer(ax, 2)
    return CARD.save(fig, OUT, 2)


# ════════════════════════════════════════════════════════════════════════
# P3 恒瑞医药
# ════════════════════════════════════════════════════════════════════════
def page_3():
    fig, ax = CARD.canvas()
    CARD.header(ax, "① 恒瑞医药 600276", "自研 + 授权出海 + NewCo",
                "传统龙头转型创新 · BD 成第二增长曲线")

    # 商业模式拆解块
    model_block(ax, 0.06, 0.52, 0.88, 0.30, "商业模式", "red",
                "三驾马车驱动",
                ["① 自研创新药国内销售 — 24款1类新药，覆盖2.5万家医疗机构",
                 "② License-out 授权出海 — GSK/BMS/MSD，累计潜在270亿$",
                 "③ NewCo 合资出海 — GLP-1组合授权Kailera(已赴美上市)",
                 "国内现金流养海外临床，BD收入已成常态化来源"])

    # KPI 四连
    metric_row4(ax, [
        Metric("316亿", "2025营收", "red", "+13.0%"),
        Metric("77亿", "归母净利", "red", "+21.7%"),
        Metric("87亿", "研发投入", "gold", "占营收27.6%"),
        Metric("33.9亿", "BD收入", "gold", "+25.6%"),
    ], y=0.40)

    # 结构质变 + 估值 (双卡)
    kpi_card(ax, 0.06, 0.20, 0.42, 0.115, "创新药占比", "61.7%", "2026Q1 首破60%", color="red", vsize=30)
    kpi_card(ax, 0.52, 0.20, 0.42, 0.115, "A股 PE", "≈45x", "估值对标Biopharma", color="blue", vsize=30)

    CARD.insight_box(ax, "非肿瘤创新药 +92% 爆发",
                     "代谢/自免破除肿瘤依赖 · GLP-1瑞普泊肽Q4有望获批",
                     bottom=0.07, height=0.10, edge="red")
    CARD.footer(ax, 3)
    return CARD.save(fig, OUT, 3)


# ════════════════════════════════════════════════════════════════════════
# P4 药明康德
# ════════════════════════════════════════════════════════════════════════
def page_4():
    fig, ax = CARD.canvas()
    CARD.header(ax, "② 药明康德 603259", "一体化 CRDMO 卖水人",
                "发现→开发→生产全链条 · 飞轮效应锁定客户")

    model_block(ax, 0.06, 0.52, 0.88, 0.30, "商业模式", "blue",
                "飞轮 + 卖铲人",
                ["① 前端药物发现(R) — 低成本流量入口，年交付42万新化合物",
                 "② R→D 转化 — 310个分子(占新增37%)，领先行业30%",
                 "③ 后端生产(M) — 小分子管线3550个，复购率高、利润厚",
                 "TIDES多肽业务深度绑定GLP-1，反应釜超10万升"])

    metric_row4(ax, [
        Metric("455亿", "2025营收", "blue", "全球CXO前三"),
        Metric("598亿", "在手订单", "blue", "+23.6% 覆盖18月"),
        Metric("113.7亿", "TIDES收入", "cyan", "+96% 翻倍"),
        Metric("72%", "美国客户", "gold", "海外占75%+"),
    ], y=0.40)

    CARD.contrast_boxes(ax,
        {"title": "Q1 毛利率", "value": "50.4%", "color": "blue", "note": "首破50% 历史新高"},
        {"title": "A股 PE", "value": "≈19x", "color": "green", "note": "历史6.9%分位"},
        y=0.175, h=0.155)

    CARD.insight_box(ax, "卖铲人吃尽 GLP-1 红利",
                     "多肽/寡核苷酸业务至少延续3年 · 估值修复空间20-25%",
                     bottom=0.065, height=0.095, edge="blue")
    CARD.footer(ax, 4)
    return CARD.save(fig, OUT, 4)


# ════════════════════════════════════════════════════════════════════════
# P5 百济神州
# ════════════════════════════════════════════════════════════════════════
def page_5():
    fig, ax = CARD.canvas()
    CARD.header(ax, "③ 百济神州 688235", "全球自主商业化标杆",
                "去CRO化临床 + 自营欧美销售 · 2025 首次年度盈利")

    model_block(ax, 0.06, 0.52, 0.88, 0.30, "商业模式", "purple",
                "全球全链条自主",
                ["① 自研创新药 — 靶点发现到全球销售全链条自主运营",
                 "② 去CRO化临床 — 3700人内部团队，覆盖6大洲40+国",
                 "③ 自营欧美渠道 — 自建血液瘤/肿瘤专科销售网络",
                 "海外收入占比超63%，对冲国内PD-1内卷与集采"])

    metric_row4(ax, [
        Metric("382亿", "2025营收", "purple", "+40.5%"),
        Metric("14.6亿", "归母净利", "green", "首次年度盈利"),
        Metric("281亿", "泽布替尼", "purple", "+48.8% 占73%"),
        Metric("75国", "获批市场", "gold", "美国BTK第一"),
    ], y=0.40)

    kpi_card(ax, 0.06, 0.20, 0.42, 0.115, "2026Q1 净利", "16.1亿", "单季超去年全年", color="green", vsize=30)
    kpi_card(ax, 0.52, 0.20, 0.42, 0.115, "2026 指引", "63-65亿$", "经营利润7-8亿$", color="purple", vsize=27)

    CARD.insight_box(ax, "泽布替尼 = 全球BTK销冠",
                     "美国处方份额超伊布替尼/阿卡替尼 · BCL-2开启第二曲线",
                     bottom=0.07, height=0.10, edge="purple")
    CARD.footer(ax, 5)
    return CARD.save(fig, OUT, 5)


# ════════════════════════════════════════════════════════════════════════
# P6 量化未来趋势对比
# ════════════════════════════════════════════════════════════════════════
def page_6():
    fig, ax = CARD.canvas()
    CARD.header(ax, "量化未来 · 三家对比", "未来 1-3 年趋势量化",
                "营收预测 · 利润弹性 · 估值水位 · 增长引擎")

    # 营收预测条形对比 2025 → 2026E
    ax.text(0.06, 0.745, "营收预测 (亿元)", ha="left", va="center", fontsize=14,
            fontweight="bold", color=COLORS["text"], transform=ax.transAxes)
    bar_compare(ax,
                ["恒瑞医药", "药明康德", "百济神州"],
                [316, 455, 382], ["red", "blue", "purple"], maxv=530, y_top=0.70, gap=0.065)
    ax.text(0.06, 0.505, "→ 2026E 营收", ha="left", va="center", fontsize=12,
            color=COLORS["muted"], transform=ax.transAxes)
    bar_compare(ax,
                ["恒瑞 ≈360", "药明 513-530", "百济 450-465"],
                [360, 522, 458], ["red", "blue", "purple"], maxv=530,
                y_top=0.465, gap=0.058, unit="亿")

    # 四维雷达式对比卡 (底部)
    dims = [
        ("利润弹性", [("恒瑞", "+22%", "red"), ("药明", "+83%", "blue"), ("百济", "扭亏→暴增", "purple")]),
        ("估值PE", [("恒瑞", "45x", "red"), ("药明", "19x", "green"), ("百济", "35x", "purple")]),
        ("研发强度", [("恒瑞", "28%", "gold"), ("药明", "含费", "blue"), ("百济", "41%", "purple")]),
        ("催化主线", [("恒瑞", "GLP-1", "red"), ("药明", "TIDES", "cyan"), ("百济", "ADC/双抗", "purple")]),
    ]
    for i, (dim, items) in enumerate(dims):
        x = 0.06 + (i % 2) * 0.47
        y = 0.285 - (i // 2) * 0.12
        ax.add_patch(FancyBboxPatch((x, y), 0.44, 0.105,
                     boxstyle="round,pad=0.01,rounding_size=0.01",
                     facecolor=COLORS["panel"], edgecolor=COLORS["border"], linewidth=1.0,
                     transform=ax.transAxes))
        ax.text(x + 0.018, y + 0.083, dim, ha="left", va="center", fontsize=11.5,
                fontweight="bold", color=COLORS["muted"], transform=ax.transAxes)
        for j, (name, val, c) in enumerate(items):
            cx = x + 0.105 + j * 0.115
            ax.text(cx, y + 0.060, name, ha="center", va="center", fontsize=9.5,
                    color=COLORS["muted"], transform=ax.transAxes)
            ax.text(cx, y + 0.030, val, ha="center", va="center", fontsize=11.5,
                    fontweight="bold", color=COLORS[c], transform=ax.transAxes)

    CARD.insight_box(ax, "三种节奏，三种赔率",
                     "恒瑞=稳健成长 · 药明=低估值修复 · 百济=盈利拐点弹性",
                     bottom=0.055, height=0.09, edge="gold")
    CARD.footer(ax, 6)
    return CARD.save(fig, OUT, 6)


# ════════════════════════════════════════════════════════════════════════
# P7 投资思考 + 风险 + CTA
# ════════════════════════════════════════════════════════════════════════
def page_7():
    fig, ax = CARD.canvas()
    CARD.header(ax, "投资思考 · 风险与选择", "看清路径，再选赔率",
                "三家公司各自的确定性、弹性与软肋")

    # 三家公司画像: 适合人群 + 核心风险
    comps = [
        ("恒瑞医药", "red",
         "稳健成长 · 长期配置",
         "创新药占比跨过60%拐点\nBD常态化+GLP-1催化",
         "Fast-follow为主\n无FDA自主获批(瑞维鲁胺闯欧盟中)"),
        ("药明康德", "blue",
         "低估值修复 · 确定性底仓",
         "订单598亿覆盖18月\nPE 19x 历史6.9%分位",
         "美国1260H名单风险\n极端影响约10%营收"),
        ("百济神州", "purple",
         "盈利拐点 · 高弹性",
         "泽布替尼全球销冠\n2025扭亏 2026利润加速",
         "单品依赖73%\n2027起专利到期"),
    ]
    for i, (name, c, role, bull, risk) in enumerate(comps):
        y = 0.71 - i * 0.205
        ax.add_patch(FancyBboxPatch((0.06, y), 0.88, 0.185,
                     boxstyle="round,pad=0.012,rounding_size=0.012",
                     facecolor=COLORS["panel"], edgecolor=COLORS[c], linewidth=1.4,
                     transform=ax.transAxes))
        ax.text(0.085, y + 0.155, name, ha="left", va="center", fontsize=15,
                fontweight="bold", color=COLORS[c], transform=ax.transAxes)
        ax.text(0.085, y + 0.122, role, ha="left", va="center", fontsize=11,
                color=COLORS["muted"], transform=ax.transAxes)
        ax.text(0.40, y + 0.140, "▲ 看点", ha="left", va="center", fontsize=10.5,
                fontweight="bold", color=COLORS["green"], transform=ax.transAxes)
        ax.text(0.40, y + 0.100, bull, ha="left", va="center", fontsize=10.5,
                color=COLORS["text"], transform=ax.transAxes)
        ax.text(0.40, y + 0.060, "▼ 风险", ha="left", va="center", fontsize=10.5,
                fontweight="bold", color=COLORS["red"], transform=ax.transAxes)
        ax.text(0.40, y + 0.030, risk, ha="left", va="center", fontsize=10.5,
                color=COLORS["text"], transform=ax.transAxes)

    CARD.insight_box(ax, "没有最好，只有最合适",
                     "看确定性选药明 · 看成长选恒瑞 · 看弹性选百济",
                     bottom=0.075, height=0.10, edge="gold")

    CARD.cta(ax, "关注+收藏 · 三分钟看懂创新药三种生意", y=0.13, color="cyan", size=16)
    CARD.footer(ax, 7, "财报/卖方预期 · 不构成投资建议")
    return CARD.save(fig, OUT, 7)


# ════════════════════════════════════════════════════════════════════════
# 预览拼图
# ════════════════════════════════════════════════════════════════════════
def make_preview():
    from PIL import Image
    pages = [Image.open(OUT / f"page_{i:02d}.png") for i in range(1, 8)]
    w, h = pages[0].size
    cols, rows = 4, 2
    tw, th = 360, int(360 * h / w)
    canvas = Image.new("RGB", (cols * tw + (cols - 1) * 6, rows * th + (rows - 1) * 6),
                       color=(13, 17, 23))
    for i, im in enumerate(pages):
        r, c = divmod(i, cols)
        canvas.paste(im.resize((tw, th)), (c * (tw + 6), r * (th + 6)))
    canvas.save(OUT / "preview_4x2.png")
    print("  saved preview_4x2.png")
    # 竖排长图(便于浏览)
    stacked = Image.new("RGB", (w, h * len(pages)), color=(13, 17, 23))
    y = 0
    for im in pages:
        stacked.paste(im, (0, y)); y += h
    stacked.resize((720, int(h * len(pages) * 720 / w))).save(OUT / "all_pages_stacked.png")
    print("  saved all_pages_stacked.png")


PAGE_GENERATORS = [page_1, page_2, page_3, page_4, page_5, page_6, page_7]


def render_all():
    for gen in PAGE_GENERATORS:
        p = gen()
        print(f"  saved {p.name} ({p.stat().st_size / 1024:.0f}KB)")


if __name__ == "__main__":
    print(f"创新药三巨头商业模式 7 页卡片 -> {OUT}")
    render_all()
    make_preview()
    print("\n完成. 7 张 1440x1920 PNG")
