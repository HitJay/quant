"""
医药抄底量化研报 — PDF (reportlab, 中文)
==========================================
读取 biopharma_dipbuy.py 的 summary.json + figures/, 排版为付费研报。

Usage:
    conda activate research
    python analysis/biopharma_dipbuy.py
    python analysis/biopharma_report.py
"""
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

ROOT = Path("./output/2026-06-09/biopharma-dipbuy")
FIGS = ROOT / "figures"
PDF = ROOT / "医药抄底量化研报.pdf"
S_ = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))

FONT = "/usr/share/fonts/google-droid/DroidSansFallback.ttf"
pdfmetrics.registerFont(TTFont("CN", FONT))
pdfmetrics.registerFont(TTFont("CN-B", FONT))
registerFontFamily("CN", normal="CN", bold="CN-B", italic="CN", boldItalic="CN-B")

NAVY = colors.HexColor("#10243e"); GREEN = colors.HexColor("#16a34a")
RED = colors.HexColor("#dc2626"); ORANGE = colors.HexColor("#ea580c")
BLUE = colors.HexColor("#2563eb"); GRAY = colors.HexColor("#666")
LIGHT = colors.HexColor("#eef2f7"); INK = colors.HexColor("#2d2d2d")
TEAL = colors.HexColor("#0e7490")

H1 = ParagraphStyle("H1", fontName="CN-B", fontSize=27, textColor=NAVY, alignment=1, leading=36, spaceAfter=8)
SUB = ParagraphStyle("SUB", fontName="CN", fontSize=13, textColor=GRAY, alignment=1, leading=20)
H2 = ParagraphStyle("H2", fontName="CN-B", fontSize=15, textColor=colors.white, backColor=NAVY,
                    leading=26, spaceBefore=20, spaceAfter=12, leftIndent=8, borderPadding=(6, 6, 6, 8))
H3 = ParagraphStyle("H3", fontName="CN-B", fontSize=12.5, textColor=NAVY, leading=20, spaceBefore=12, spaceAfter=5)
BODY = ParagraphStyle("BODY", fontName="CN", fontSize=10.5, textColor=INK, leading=18, spaceAfter=7, alignment=4)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=2, spaceAfter=5)
NOTE = ParagraphStyle("NOTE", fontName="CN", fontSize=9, textColor=GRAY, leading=14)
CAP = ParagraphStyle("CAP", fontName="CN", fontSize=8.5, textColor=GRAY, alignment=1, leading=12, spaceAfter=10)

AS_OF = S_["as_of"]
cyc = S_["cycles"]; div = S_["diverge"]; knife = S_["knife"]
cur_dd = S_["cur_dd"]; cur_lab = S_["cur_lab"]; rot = S_["rot_metrics"]; sub = S_["sub"]


def pct(x, d=1):
    return f"{x*100:+.{d}f}%" if x == x else "—"


def pct0(x):
    return f"{x*100:.0f}%" if x == x else "—"


def img(name, w_cm=16.0):
    from PIL import Image as PILImage
    p = FIGS / name
    iw, ih = PILImage.open(p).size
    w = w_cm * cm
    return Image(str(p), width=w, height=w * ih / iw)


def table(data, cw, fs=9.5, hl=None):
    t = Table(data, colWidths=cw, hAlign="CENTER")
    st = [("FONTNAME", (0, 0), (-1, -1), "CN"), ("FONTSIZE", (0, 0), (-1, -1), fs),
          ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("FONTNAME", (0, 0), (-1, 0), "CN-B"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ccc")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    if hl:
        for r in hl:
            st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fff3d6")))
            st.append(("FONTNAME", (0, r), (-1, r), "CN-B"))
    t.setStyle(TableStyle(st))
    return t


def watermark(c, d):
    c.saveState(); c.setFont("CN", 58); c.setFillColor(colors.HexColor("#eef0f3"))
    c.translate(A4[0] / 2, A4[1] / 2); c.rotate(45)
    c.drawCentredString(0, 0, "付费研报 PAID"); c.restoreState()


def on_first(c, d):
    watermark(c, d); c.saveState(); c.setFont("CN", 8.5); c.setFillColor(GRAY)
    c.drawCentredString(A4[0] / 2, 1.2 * cm, "本报告为付费内容 · 仅供个人参考 · 不构成投资建议"); c.restoreState()


def on_later(c, d):
    watermark(c, d); c.saveState(); c.setStrokeColor(colors.HexColor("#ddd")); c.setLineWidth(0.5)
    c.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    c.setFont("CN", 8); c.setFillColor(GRAY)
    c.drawString(2 * cm, A4[1] - 1.25 * cm, "医药抄底量化研报")
    c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, f"数据截止 {AS_OF}")
    c.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    c.drawCentredString(A4[0] / 2, 0.95 * cm, f"第 {d.page} 页 · 付费内容 · 不构成投资建议")
    c.restoreState()


S = []
# 封面
S.append(Spacer(1, 3.0 * cm))
S.append(Paragraph("医药跌了三年，现在能抄底吗？", H1))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph("创新药/生物医药 政策周期 × 抄底胜率 × 子板块分化 量化研究", SUB))
S.append(Spacer(1, 0.8 * cm))
S.append(HRFlowable(width="60%", thickness=1.2, color=NAVY, hAlign="CENTER"))
S.append(Spacer(1, 0.8 * cm))
ck = [["医药距一年高", "当前档1年胜率", "跌透(≤-40%)胜率"],
      [pct0(cur_dd), pct0([k["win"] for k in knife if k["lab"] == cur_lab][0]), pct0(knife[0]["win"])]]
ct = Table(ck, colWidths=[5.2 * cm] * 3, hAlign="CENTER")
ct.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, 0), "CN"), ("FONTSIZE", (0, 0), (-1, 0), 11), ("TEXTCOLOR", (0, 0), (-1, 0), GRAY),
    ("FONTNAME", (0, 1), (-1, 1), "CN-B"), ("FONTSIZE", (0, 1), (-1, 1), 22), ("TEXTCOLOR", (0, 1), (0, 1), RED),
    ("TEXTCOLOR", (1, 1), (1, 1), ORANGE), ("TEXTCOLOR", (2, 1), (2, 1), GREEN),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 1), (-1, 1), 6)]))
S.append(ct)
S.append(Spacer(1, 1.0 * cm))
S.append(Paragraph("基于 AKShare 12年医药ETF日线 · 政策周期 · 抄底胜率 · 子板块分化 · 轮动回测", SUB))
S.append(Spacer(1, 2.4 * cm))
S.append(Paragraph("出品：量化研究笔记（作者背景：药物发现计算科学家）　|　数据截止 " + AS_OF, CAP))
S.append(PageBreak())

# 摘要
S.append(Paragraph("摘要与核心结论", H2))
win_cur = [k["win"] for k in knife if k["lab"] == cur_lab][0]
S.append(Paragraph(
    f"医药板块自2021年中见顶后历经三年深熊，当前距一年高点{pct(cur_dd)}。市场再现\"医药跌够了该抄底\""
    f"的讨论，又恰逢2024-25年中国创新药出海（License-out/BD）逻辑兴起。本报告用12年医药ETF日线，"
    f"量化医药的政策周期规律、深跌抄底的真实胜率、以及\"买宽基医药\"与\"买创新药出海\"的巨大差异，"
    f"给出基于数据、且与流行叙事不同的判断。", BODY))
concl = [
    f"<b>政策是医药最大的择时变量</b>：2018集采冲击医药{pct(cyc[0]['med'],0)}，2019-21随创新与景气"
    f"大涨{pct(cyc[1]['med'],0)}，2021年中集采扩围+CDE新政后深熊{pct(cyc[2]['med'],0)}。",
    f"<b>买医药 ≠ 买创新药出海</b>：2024-09反转以来，宽基医药仅{pct(div['宽基医药'],0)}，"
    f"而创新药{pct(div['创新药'],0)}、港股创新药{pct(div['港股创新药'],0)}，同期沪深300 {pct(div['沪深300'],0)}——"
    f"出海行情高度集中在创新药子板块，宽基ETF被CXO/器械/仿制/中药稀释。",
    f"<b>当前-27%回撤是历史上胜率最低的尴尬区间</b>：持有1年上涨概率仅{pct0(win_cur)}（中位为负）；"
    f"真正高胜率的抄底点是跌透（≤-40%档胜率{pct0(knife[0]['win'])}、均值{pct(knife[0]['avg'],0)}）。",
    f"<b>医药内部追动量是灾难</b>：子板块月度动量轮动2020-06以来总收益{pct(rot['动量轮动']['total'],0)}，"
    f"远差于等权{pct(rot['医药等权']['total'],0)}与沪深300 {pct(rot['沪深300']['total'],0)}。",
    f"<b>一句话结论</b>：可以关注，但<b>别买宽基赌出海、别在-27%急着抄底、别追动量</b>——"
    f"分板块（创新药/港股创新药纯度高）、等跌透或政策催化确认、用纪律分批。",
]
for c in concl:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph("* 结论基于历史回测与价格数据，重叠样本统计反映条件期望，不代表未来。", NOTE))
S.append(PageBreak())

# 一、背景
S.append(Paragraph("一、市场背景：医药的三年深熊与当下", H2))
S.append(Paragraph(
    "医药曾是A股核心资产之一，2019-2021年在创新药放量、CXO景气、疫情催化下走出翻倍行情；"
    "但2021年中起，集采常态化扩围、CDE《以临床价值为导向》新政、医保控费等政策压制，"
    "叠加高估值消化，板块进入长达三年的深熊。2024年9月政策与流动性反转后，市场风险偏好回升，"
    "但医药内部分化极大。下表为六个代表性医药ETF截至报告日的状态。", BODY))
mkt = [["板块", "代码", "近1年", "距一年高", "年化(上市来)", "最大回撤"]]
order = sorted(sub, key=lambda c: sub[c]["dd"], reverse=True)
for c in order:
    s = sub[c]
    mkt.append([s["name"], c, pct(s["ret1y"], 0), pct(s["dd"], 0), pct(s["ann"]), pct0(s["mdd"])])
S.append(table(mkt, [3.0 * cm, 2.0 * cm, 2.2 * cm, 2.4 * cm, 3.0 * cm, 2.4 * cm]))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    "解读：全部子板块距一年高点回撤在-27%~-39%之间，深度回调中。"
    "其中港股创新药近1年最抗跌（出海纯度最高），"
    "宽基与器械/CXO相对弱。这种分化正是本报告的核心议题。", BODY))
S.append(PageBreak())

# 二、方法
S.append(Paragraph("二、研究方法与数据", H2))
S.append(Paragraph("2.1 数据", H3))
S.append(Paragraph(
    "数据来源为 AKShare 的ETF后复权日线收盘价。长序列医药ETF(159929)回溯至2013年，"
    "完整覆盖2018集采、2021估值顶、2021-24深熊、2024-25反转全周期；创新药(159992)、"
    "医疗(512170)、生物医药(512290)等子板块自2019-2020上市起；港股创新药(513120)自2022年起。"
    "数据截止" + AS_OF + "。", BODY))
S.append(Paragraph("2.2 方法", H3))
for c in [
    "<b>政策周期分段</b>：按集采/新政/反转关键节点切分区间，统计各段医药与沪深300收益。",
    "<b>深跌抄底胜率</b>：对每个交易日计算距过去252日高点的回撤(dd)，按档位\"买入\"持有252个交易日(约1年)，统计上涨概率与平均收益。逐日重叠样本，反映条件期望。",
    "<b>子板块分化</b>：以2024-09-23反转日为起点，比较宽基医药、创新药、港股创新药与沪深300的累计收益。",
    "<b>动量轮动回测</b>：医药四个子板块，月频按3个月动量持有最强2个，对比等权与沪深300（仓位法、T+1、现金零利率）。",
]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(PageBreak())

# 三、政策周期
S.append(Paragraph("三、政策驱动的牛熊全周期", H2))
S.append(img("fig_full_cycle.png", 16))
S.append(Paragraph("图1　医药(159929) vs 沪深300，标注集采/新政/反转关键节点", CAP))
seg_t = [["周期", "区间", "医药", "沪深300", "超额"]]
labels = ["2018集采冲击", "2019-21大牛", "2021-24深熊", "2024-25反转"]
ranges = ["2018.05~2019.01", "2019.01~2021.07", "2021.07~2024.09", "2024.09~至今"]
for lab, rg, cs in zip(labels, ranges, cyc):
    seg_t.append([lab, rg, pct(cs["med"], 0), pct(cs["b300"], 0), pct(cs["med"] - cs["b300"], 0)])
S.append(table(seg_t, [3.2 * cm, 4.0 * cm, 2.6 * cm, 2.8 * cm, 2.6 * cm]))
S.append(Paragraph(
    "解读：医药的弹性远大于大盘——牛市能涨133%（约为沪深300的两倍），熊市也能跌60%。"
    "驱动力高度依赖政策：集采是最强的利空（压制仿制药/高值耗材定价），"
    "而创新与出海（License-out）是最强的利多。看懂政策周期，比追涨杀跌重要得多。", BODY))
S.append(PageBreak())

# 四、分化
S.append(Paragraph("四、买医药 ≠ 买创新药出海", H2))
S.append(Paragraph(
    f"这是本报告最反直觉、也最重要的发现。流行叙事是\"2024-25创新药出海大牛市\"，"
    f"但如果你买的是宽基医药ETF，几乎没赚到这波钱。", BODY))
dv = [["标的", "2024-09反转以来收益"]]
for k in ["宽基医药", "创新药", "港股创新药", "沪深300"]:
    dv.append([k, pct(div[k], 0)])
S.append(table(dv, [8.0 * cm, 7.0 * cm, ], fs=11))
S.append(Spacer(1, 0.15 * cm))
S.append(Paragraph(
    f"宽基医药仅{pct(div['宽基医药'],0)}，被CXO、医疗器械、仿制药、中药等非出海方向严重拖累；"
    f"而创新药{pct(div['创新药'],0)}、港股创新药{pct(div['港股创新药'],0)}（港股18A聚集了最多真正具备"
    f"海外授权能力的Biotech）。<b>结论：在医药里，选对子板块（甚至个股）比择时更决定收益。"
    f"想押注出海逻辑，就不该买宽基医药ETF。</b>", BODY))
S.append(Paragraph(
    "（领域视角）真正的出海beta来自具备First-in-class/Best-in-class管线、能与跨国药企达成大额BD的企业，"
    "其价值由靶点稀缺性、临床数据强度、合作方质量决定——这类标的在宽基指数里权重很低。", NOTE))
S.append(PageBreak())

# 五、抄底胜率
S.append(Paragraph("五、深跌抄底胜率：现在是好时机吗", H2))
S.append(img("fig_dipbuy_winrate.png", 15))
S.append(Paragraph("图2　医药按回撤档位买入、持有1年的上涨概率（2013至今）", CAP))
kf = [["回撤档位", "样本", "1年胜率", "1年均值"]]
hl = []
for i, k in enumerate(knife, start=1):
    if k["win"] != k["win"]:
        continue
    kf.append([k["lab"], str(k["n"]), pct0(k["win"]), pct(k["avg"], 0)])
    if k["lab"] == cur_lab:
        hl.append(len(kf) - 1)
S.append(table(kf, [3.4 * cm, 3.0 * cm, 3.2 * cm, 3.2 * cm], hl=hl))
S.append(Paragraph("（高亮行为当前所处档位）", NOTE))
S.append(Paragraph(
    f"胜率曲线呈U型：跌得最透（≤-40%）时抄底，持有1年胜率高达{pct0(knife[0]['win'])}、均值{pct(knife[0]['avg'],0)}；"
    f"而当前所处的-30~-20%档，胜率仅{pct0(win_cur)}、中位为负——这是\"不上不下\"的尴尬区间，"
    f"往往是下跌途中而非底部。接近高点（-10~0%）反而胜率回升至{pct0(knife[-1]['win'])}（强趋势延续）。"
    f"<b>含义：医药现在跌了27%，并不是历史上最优的抄底点；真正的黄金坑需要跌透，或等到政策/出海催化确认。</b>", BODY))
S.append(PageBreak())

# 六、动量
S.append(Paragraph("六、医药里追动量为何是灾难", H2))
S.append(img("fig_rotation.png", 16))
S.append(Paragraph("图3　医药子板块动量轮动 vs 等权 vs 沪深300", CAP))
rt = [["策略", "总收益", "年化", "最大回撤", "夏普"]]
for nm in ["动量轮动", "医药等权", "沪深300"]:
    m = rot[nm]
    rt.append([nm, pct(m["total"], 0), pct(m["ann"]), pct0(m["mdd"]), f"{m['sharpe']:.2f}"])
S.append(table(rt, [3.6 * cm, 2.8 * cm, 2.6 * cm, 2.8 * cm, 2.2 * cm]))
S.append(Paragraph(
    f"在2020-06以来以震荡下行为主的医药板块里，追逐近期最强子板块（动量轮动）总收益{pct(rot['动量轮动']['total'],0)}，"
    f"反而比简单等权{pct(rot['医药等权']['total'],0)}更差，更远不及沪深300。原因：板块在政策反复中频繁切换风格，"
    f"动量信号被反复\"打脸\"（买在反弹高点、卖在恐慌低点）。这与作者此前在科技板块的发现一致——"
    f"<b>在弱趋势/震荡品种里，纪律性分批与逆向，胜过机械追强。</b>", BODY))
S.append(PageBreak())

# 七、实操
S.append(Paragraph("七、实操建议", H2))
S.append(Paragraph("7.1 选对子板块（比择时更重要）", H3))
for c in ["押注创新药出海逻辑 → 优先创新药(159992)/港股创新药(513120)，而非宽基医药；",
          "要稳健配置 → 宽基医药卫生(512010)波动相对小但弹性也低；",
          "看好CXO/器械修复 → 医疗(512170)，但需景气度确认。"]:
    S.append(Paragraph(c, BULLET, bulletText="▪"))
S.append(Paragraph("7.2 抄底节奏（别在尴尬区间满仓）", H3))
for c in ["当前-27%档胜率仅44%，不宜重仓抢反弹；",
          "分批纪律：每跌一档加一档，给\"跌透\"留子弹；",
          "把政策/出海催化（集采落地、医保谈判温和、重磅BD）作为加仓确认信号。"]:
    S.append(Paragraph(c, BULLET, bulletText="▪"))
S.append(Paragraph("7.3 通用资金框架", H3))
fw = [["距高点回撤", "建议累计仓位", "动作"],
      ["-10%~-20%", "20%~30%", "试探(胜率低,轻仓)"],
      ["-20%~-30%", "30%~45%", "分批(当前位置)"],
      ["-30%~-40%", "50%~70%", "主力(胜率回升)"],
      ["≤-40%", "70%~90%", "重仓(历史黄金坑)"]]
S.append(table(fw, [4.0 * cm, 5.0 * cm, 6.0 * cm]))
S.append(Paragraph("通用铁律：分板块 · 分批进场 · 留子弹等跌透 · 看政策催化 · 不追动量。", BODY))
S.append(PageBreak())

# 八、风险 + 附录
S.append(Paragraph("八、风险提示与免责声明", H2))
for c in ["历史回测不代表未来，政策与产业环境可能发生结构性变化；",
          "条件胜率为逐日重叠样本，存在自相关，统计显著性弱于独立样本；",
          "ETF口径无法完全捕捉个股出海行情，真正的出海beta需个股层面研究；",
          "港股创新药受汇率、海外市场与18A流动性影响；",
          "本报告为付费研究内容，仅供个人学习参考，不构成任何投资建议，据此操作风险自负。"]:
    S.append(Paragraph(c, BULLET, bulletText="•"))
S.append(Paragraph("附录：数据来源与复现", H2))
S.append(Paragraph("数据：AKShare 后复权ETF日线。工具链：本仓库 quant.data / quant.backtest.metrics。", BODY))
appx = [["交付文件", "说明"],
        ["cards/01~07_*.png", "小红书7张分享卡片(1440×1920)"],
        ["医药抄底量化研报.pdf", "本研报(付费内容)"],
        ["figures/*.png", "研报图表(全周期/抄底胜率/轮动/相对强弱)"],
        ["data/*.csv", "周期收益/抄底胜率/子板块/轮动指标"],
        ["summary.json", "全部关键数字"],
        ["code/biopharma_*.py", "首看分析+卡片+本PDF 复现脚本"]]
S.append(table(appx, [5.6 * cm, 10.2 * cm]))
S.append(Spacer(1, 0.2 * cm))
S.append(Paragraph(
    "复现：<br/>conda activate research<br/>python analysis/biopharma_dipbuy.py<br/>python analysis/biopharma_report.py", NOTE))
S.append(Spacer(1, 0.3 * cm))
S.append(Paragraph("延伸（下一阶段）：创新药出海/License-out 事件驱动深度研究——"
                   "统计重大BD公告前后的超额收益，结合管线与靶点的专业点评。", NOTE))

doc = SimpleDocTemplate(str(PDF), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
                        title="医药抄底量化研报", author="量化研究笔记")
doc.build(S, onFirstPage=on_first, onLaterPages=on_later)
print(f"PDF 已生成 → {PDF}  ({PDF.stat().st_size//1024} KB)")
