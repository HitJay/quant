"""
炸板潮反共识帖 · 数据汇总
2026-06-26 早盘 11:30 后跑.
输入: output/hotspot/20260626/raw/*.parquet
输出: output/2026-06-26/morning-card/{summary.json, data/*.csv}
"""

import json
import pandas as pd
from pathlib import Path

OUT = Path("/das/user/QYJI/quant/output/2026-06-26/morning-card")
RAW = Path("/das/user/QYJI/quant/output/hotspot/20260626/raw")
(OUT / "data").mkdir(parents=True, exist_ok=True)

# ---------- 读 ----------
zt = pd.read_parquet(RAW / "zt_pool.parquet")        # 39 只涨停
zb = pd.read_parquet(RAW / "zt_zbgc.parquet")        # 36 只炸板 (未守住)
strong = pd.read_parquet(RAW / "zt_strong.parquet")  # 256 只强势股
ind = pd.read_parquet(RAW / "industry_board.parquet")
news = pd.read_parquet(RAW / "em_global_news.parquet")

# ---------- 核心数字 ----------
n_zt = len(zt)
n_zb = len(zb)
n_zt_with_open = int((zt["炸板次数"] >= 1).sum())   # 涨停股中曾经被打开过的
n_zt_open_3plus = int((zt["炸板次数"] >= 3).sum())  # 炸过 3 次以上
zt_open_pct = n_zt_with_open / n_zt * 100
max_open_count = int(zt["炸板次数"].max())
max_open_name = zt.loc[zt["炸板次数"].idxmax(), "名称"]
max_open_code = zt.loc[zt["炸板次数"].idxmax(), "代码"]

# 连板分布
lb_dist = zt["连板数"].value_counts().sort_index().to_dict()
first_board = int(lb_dist.get(1, 0))
first_board_pct = first_board / n_zt * 100
top_lb_row = zt.loc[zt["连板数"].idxmax()]
top_lb_name = top_lb_row["名称"]
top_lb_code = top_lb_row["代码"]
top_lb_n = int(top_lb_row["连板数"])

# 炸板池振幅 (这些是上午冲过涨停但没守住的, 振幅大说明套人深)
zb_amp_top10 = (zb.nlargest(10, "振幅")[["代码","名称","涨跌幅","炸板次数","振幅","所属行业"]]
                .reset_index(drop=True))
zb_amp_max = float(zb["振幅"].max())
zb_amp_max_name = zb.loc[zb["振幅"].idxmax(), "名称"]
zb_amp_gt10 = int((zb["振幅"] > 10).sum())
zb_below_zero = int((zb["涨跌幅"] < 0).sum())   # 炸板后翻绿
zb_mean_chg = float(zb["涨跌幅"].mean())        # 炸板后平均涨幅

# 涨停池炸板次数 TOP10
zt_open_top10 = (zt.nlargest(10, "炸板次数")[["代码","名称","涨跌幅","炸板次数","连板数","所属行业"]]
                 .reset_index(drop=True))

# 涨停行业分布
zt_ind = zt["所属行业"].value_counts().head(8).to_dict()
zb_ind = zb["所属行业"].value_counts().head(8).to_dict()

# 大盘宏观背景 (从 news 抽数字)
# 沪指 -2.14%, 深成指 -3.04%, 创业板 -3.72%, 4600 跌, 两市半日 2.43 万亿
macro = {
    "sh_chg_pct": -2.14,
    "sh_pt": 4032.3,
    "sz_chg_pct": -3.04,
    "sz_pt": 15846.98,
    "cyb_chg_pct": -3.72,
    "cyb_pt": 4209.29,
    "n_decline": 4600,
    "halfday_amount_yi": 24300,
    "note": "from em_global_news 11:33 午评/11:35 午盘"
}

# 行业跌幅 TOP5 (来自 industry_board)
ind_loss = ind.sort_values("pct_chg").head(8)[["name","pct_chg","main_net_in"]].reset_index(drop=True)
ind_loss.columns = ["板块名称","涨跌幅","主力净流入"]

# ---------- summary ----------
summary = {
    "title": "炸板潮反共识帖 — 涨停 39 vs 炸板 36",
    "date": "2026-06-26",
    "snapshot_time": "11:30 早盘后",
    "headline_numbers": {
        "n_zt": n_zt,
        "n_zb": n_zb,
        "n_zt_with_open": n_zt_with_open,
        "zt_open_pct": round(zt_open_pct, 1),
        "n_zt_open_3plus": n_zt_open_3plus,
        "max_open_count": max_open_count,
        "max_open_name": max_open_name,
        "max_open_code": max_open_code,
        "first_board": first_board,
        "first_board_pct": round(first_board_pct, 1),
        "top_lb": {"name": top_lb_name, "code": top_lb_code, "n": top_lb_n},
        "zb_amp_max": round(zb_amp_max, 1),
        "zb_amp_max_name": zb_amp_max_name,
        "zb_amp_gt10": zb_amp_gt10,
        "zb_below_zero": zb_below_zero,
        "zb_mean_chg": round(zb_mean_chg, 2),
    },
    "lb_distribution": {int(k): int(v) for k, v in lb_dist.items()},
    "zt_open_top10": zt_open_top10.to_dict(orient="records"),
    "zb_amp_top10": zb_amp_top10.to_dict(orient="records"),
    "zt_industry_top": zt_ind,
    "zb_industry_top": zb_ind,
    "macro": macro,
    "industry_loss_top": ind_loss.to_dict(orient="records"),
    "core_narrative": (
        f"大盘 {macro['sh_chg_pct']}% / 创业板 {macro['cyb_chg_pct']}%, {macro['n_decline']} 只跌, "
        f"但涨停 {n_zt} 只 + 炸板 {n_zb} 只. "
        f"散户共识: 题材在, 追涨停. "
        f"数据真相: {n_zt_with_open}/{n_zt} ({zt_open_pct:.0f}%) 当日炸过封板, "
        f"{n_zt_open_3plus} 只炸 ≥3 次, {max_open_name}炸 {max_open_count} 次, "
        f"{first_board}/{n_zt} ({first_board_pct:.0f}%) 是首板无龙头, "
        f"另外 {n_zb} 只今早曾涨停的股最终被打下来. "
        f"接近 1:1 的涨停 vs 炸板比例 — 你以为有 39 个赢家, 实际有 36 个被埋 + 21 个心跳冲浪手."
    ),
}

with open(OUT / "summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

# ---------- CSV ----------
zt_open_top10.to_csv(OUT / "data" / "zt_open_top10.csv", index=False, encoding="utf-8-sig")
zb_amp_top10.to_csv(OUT / "data" / "zb_amp_top10.csv", index=False, encoding="utf-8-sig")
pd.DataFrame.from_dict(lb_dist, orient="index", columns=["count"]).to_csv(
    OUT / "data" / "lb_distribution.csv", encoding="utf-8-sig"
)
zt.to_csv(OUT / "data" / "zt_pool_full.csv", index=False, encoding="utf-8-sig")
zb.to_csv(OUT / "data" / "zb_full.csv", index=False, encoding="utf-8-sig")
ind_loss.to_csv(OUT / "data" / "industry_loss_top.csv", index=False, encoding="utf-8-sig")

print("=== 核心数字 ===")
for k, v in summary["headline_numbers"].items():
    print(f"  {k}: {v}")
print(f"\n=== 连板分布 ===\n  {lb_dist}")
print(f"\n=== Output ===\n  {OUT}/summary.json")
print(f"  {OUT}/data/*.csv (6 个)")
