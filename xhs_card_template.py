"""Reusable dark XHS card template for A-share deep-dive cards.

The default visual language follows the FCF contrarian series: full-bleed
dark canvas, left-aligned page headers, dense data modules, bottom insight
boxes, and a right-bottom creator signature.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle


COLORS = {
    "bg": "#0d1117",
    "panel": "#161b22",
    "panel2": "#1c2129",
    "border": "#30363d",
    "text": "#c9d1d9",
    "muted": "#8b949e",
    "dim": "#6e7681",
    "blue": "#58a6ff",
    "green": "#3fb950",
    "red": "#f85149",
    "orange": "#d2991d",
    "purple": "#bc8cff",
    "gold": "#f0c040",
    "cyan": "#56d4dd",
    "rose": "#ff7b72",
    "pink": "#ff7b72",
    "up": "#f85149",
    "down": "#3fb950",
    "ink": "#0d1117",
}

CARD_W, CARD_H, DPI = 7.2, 9.6, 200

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Droid Sans Fallback", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.weight"] = "regular"


def wrap_text(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(str(text), width=width, break_long_words=True, replace_whitespace=False))


def money_text(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1e8:
        return f"{number / 1e8:.1f}亿"
    if abs(number) >= 1e4:
        return f"{number / 1e4:.0f}万"
    return f"{number:.0f}"


@dataclass(frozen=True)
class Metric:
    value: str
    label: str
    color: str = "text"
    sublabel: str = ""


class XHSCard:
    """Small drawing helper for 3:4 XHS cards."""

    def __init__(self, total_pages: int, brand: str = "复旦杰伦", source: str = "东方财富/雪球"):
        self.total_pages = total_pages
        self.brand = brand
        self.source = source

    def canvas(self):
        fig, ax = plt.subplots(figsize=(CARD_W, CARD_H), dpi=DPI, facecolor=COLORS["bg"])
        fig.patch.set_facecolor(COLORS["bg"])
        ax.set_facecolor(COLORS["bg"])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        return fig, ax

    def save(self, fig, output_dir: Path, page: int) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"page_{page:02d}.png"
        fig.savefig(path, dpi=DPI, facecolor=COLORS["bg"], edgecolor="none", bbox_inches=None, pad_inches=0)
        plt.close(fig)
        return path

    def header(self, ax, eyebrow: str, title: str, subtitle: str | None = None) -> None:
        ax.text(
            0.06,
            0.955,
            eyebrow,
            fontsize=13,
            color=COLORS["muted"],
            fontweight="bold",
            transform=ax.transAxes,
        )
        ax.text(
            0.06,
            0.905,
            title,
            fontsize=26,
            color=COLORS["text"],
            fontweight="bold",
            transform=ax.transAxes,
        )
        if subtitle:
            ax.text(
                0.06,
                0.865,
                subtitle,
                fontsize=14.5,
                color=COLORS["muted"],
                transform=ax.transAxes,
            )

    def footer(self, ax, page: int, note: str = "盘中数据仅供复盘 · 不构成投资建议") -> None:
        ax.axhline(0.04, xmin=0.06, xmax=0.94, color=COLORS["border"], lw=0.5, alpha=0.5)
        ax.text(
            0.06,
            0.018,
            f"* {note}",
            fontsize=10,
            color=COLORS["muted"],
            transform=ax.transAxes,
        )
        ax.text(
            0.94,
            0.038,
            f"@{self.brand}",
            fontsize=10,
            color=COLORS["muted"],
            ha="right",
            fontstyle="italic",
            transform=ax.transAxes,
        )
        ax.text(
            0.94,
            0.018,
            f"{page}/{self.total_pages}",
            fontsize=10.5,
            color=COLORS["muted"],
            ha="right",
            transform=ax.transAxes,
        )

    def pill(self, ax, x: float, y: float, text: str, color: str = "gold", size: int = 11) -> None:
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=size,
            fontweight="bold",
            color=COLORS["ink"],
            bbox=dict(boxstyle="round,pad=0.42", fc=COLORS[color], ec="none"),
            transform=ax.transAxes,
        )

    def panel(self, ax, left: float, bottom: float, width: float, height: float,
              edge: str = "border", face: str = "panel", lw: float = 1.2, alpha: float = 1.0) -> None:
        ax.add_patch(
            FancyBboxPatch(
                (left, bottom),
                width,
                height,
                boxstyle="round,pad=0.014,rounding_size=0.014",
                facecolor=COLORS[face],
                edgecolor=COLORS[edge],
                linewidth=lw,
                alpha=alpha,
                transform=ax.transAxes,
            )
        )

    def insight_box(self, ax, text: str, subtext: str = "", bottom: float = 0.08,
                    height: float = 0.11, edge: str = "gold", face: str = "panel") -> None:
        self.panel(ax, 0.06, bottom, 0.88, height, edge=edge, face=face, lw=1.2)
        ax.text(0.5, bottom + height * 0.63, text, ha="center", va="center",
                fontsize=15, fontweight="bold", color=COLORS[edge], transform=ax.transAxes)
        if subtext:
            ax.text(0.5, bottom + height * 0.32, subtext, ha="center", va="center",
                    fontsize=11.5, color=COLORS["text"], transform=ax.transAxes)

    def title(self, ax, tag: str, line1: str, line2: str = "", accent: str = "gold",
              y1: float = 0.86, size1: int = 34, size2: int = 50) -> None:
        self.pill(ax, 0.5, 0.945, f"  {tag}  ", accent, 11)
        if line2:
            ax.text(0.5, y1, line1, ha="center", va="center", fontsize=size1,
                    color=COLORS["text"], transform=ax.transAxes)
            ax.text(0.5, y1 - 0.08, line2, ha="center", va="center", fontsize=size2,
                    fontweight="bold", color=COLORS[accent], transform=ax.transAxes)
        else:
            ax.text(0.5, y1 - 0.02, line1, ha="center", va="center", fontsize=size2,
                    fontweight="bold", color=COLORS["text"], transform=ax.transAxes)

    def contrast_boxes(self, ax, left: dict, right: dict, y: float = 0.49, h: float = 0.24) -> None:
        boxes = [(0.07, left), (0.56, right)]
        for x, item in boxes:
            edge = item.get("color", "green")
            ax.add_patch(Rectangle((x, y), 0.37, h, fc=COLORS[edge], alpha=0.14,
                                   ec=COLORS[edge], lw=1.8, transform=ax.transAxes))
            ax.text(x + 0.185, y + h - 0.045, item.get("title", ""), ha="center",
                    va="center", fontsize=15, color=COLORS["text"], transform=ax.transAxes)
            ax.text(x + 0.185, y + h * 0.53, item.get("value", ""), ha="center",
                    va="center", fontsize=item.get("value_size", 42), fontweight="bold",
                    color=COLORS[edge], transform=ax.transAxes)
            ax.text(x + 0.185, y + 0.055, item.get("note", ""), ha="center",
                    va="center", fontsize=10, color=COLORS["muted"], transform=ax.transAxes)
        ax.text(0.50, y + h * 0.51, "VS", ha="center", va="center", fontsize=18,
                fontweight="bold", color=COLORS["ink"],
                bbox=dict(boxstyle="circle,pad=0.45", fc=COLORS["gold"], ec="none"),
                transform=ax.transAxes)

    def metrics_row(self, ax, metrics: list[Metric], y: float = 0.36) -> None:
        xs = [0.2, 0.5, 0.8] if len(metrics) == 3 else [0.14, 0.38, 0.62, 0.86]
        for x, metric in zip(xs, metrics):
            ax.text(x, y, metric.value, ha="center", va="center", fontsize=43,
                    fontweight="bold", color=COLORS[metric.color], transform=ax.transAxes)
            ax.text(x, y - 0.065, metric.label, ha="center", va="center", fontsize=12,
                    color=COLORS["muted"], transform=ax.transAxes)
            if metric.sublabel:
                ax.text(x, y - 0.105, metric.sublabel, ha="center", va="center", fontsize=9.5,
                        color=COLORS[metric.color], transform=ax.transAxes)

    def cta(self, ax, text: str, y: float = 0.16, color: str = "cyan", size: int = 16) -> None:
        ax.text(0.5, y, text, ha="center", va="center", fontsize=size, fontweight="bold",
                color=COLORS[color],
                bbox=dict(boxstyle="round,pad=0.48", fc=COLORS["panel"], ec=COLORS["border"], lw=1.4),
                transform=ax.transAxes)

    def split_rank_bars(self, ax, left_items: list[dict], right_items: list[dict],
                        left_title: str = "涨幅榜 TOP5", right_title: str = "跌幅榜 TOP5") -> None:
        ax.text(0.27, 0.78, left_title, ha="center", fontsize=18, fontweight="bold",
                color=COLORS["green"], transform=ax.transAxes)
        ax.text(0.74, 0.78, right_title, ha="center", fontsize=18, fontweight="bold",
                color=COLORS["red"], transform=ax.transAxes)
        ax.plot([0.52, 0.52], [0.26, 0.74], color=COLORS["border"], lw=1.0, transform=ax.transAxes)
        max_value = max(
            [abs(float(item.get("value", 0))) for item in left_items + right_items] or [1]
        )
        for i, y in enumerate([0.69, 0.61, 0.53, 0.45, 0.37]):
            if i < len(left_items):
                item = left_items[i]
                width = 0.16 * abs(float(item.get("value", 0))) / max_value
                ax.text(0.06, y, item["name"], ha="left", va="center", fontsize=14,
                        color=COLORS["text"], transform=ax.transAxes)
                ax.text(0.49, y, item["label"], ha="right", va="center", fontsize=16,
                        color=COLORS["green"], transform=ax.transAxes)
                ax.add_patch(Rectangle((0.50 - width, y - 0.018), width, 0.030,
                                       fc=COLORS["green"], alpha=0.22, ec="none", transform=ax.transAxes))
            if i < len(right_items):
                item = right_items[i]
                width = 0.16 * abs(float(item.get("value", 0))) / max_value
                ax.text(0.95, y, item["name"], ha="right", va="center", fontsize=14,
                        color=COLORS["text"], transform=ax.transAxes)
                ax.text(0.55, y, item["label"], ha="left", va="center", fontsize=16,
                        color=COLORS["red"], transform=ax.transAxes)
                ax.add_patch(Rectangle((0.54, y - 0.018), width, 0.030,
                                       fc=COLORS["red"], alpha=0.22, ec="none", transform=ax.transAxes))

    def stock_grid(self, ax, cards: list[dict], top: float = 0.70, bottom: float = 0.28) -> None:
        positions = [(0.08, top - 0.18), (0.55, top - 0.18), (0.08, bottom), (0.55, bottom)]
        for (x, y), item in zip(positions, cards):
            edge = item.get("color", "border")
            self.panel(ax, x, y, 0.37, 0.17, edge=edge, face="panel", lw=1.2)
            ax.text(x + 0.04, y + 0.125, item.get("tag", ""), ha="left", va="center",
                    fontsize=8, fontweight="bold", color=COLORS["ink"],
                    bbox=dict(boxstyle="round,pad=0.25", fc=COLORS[edge], ec="none"),
                    transform=ax.transAxes)
            ax.text(x + 0.185, y + 0.125, item.get("name", ""), ha="center", va="center",
                    fontsize=18, fontweight="bold", color=COLORS["text"], transform=ax.transAxes)
            ax.text(x + 0.185, y + 0.082, item.get("value", ""), ha="center", va="center",
                    fontsize=17, color=COLORS[edge], transform=ax.transAxes)
            ax.text(x + 0.185, y + 0.040, item.get("note", ""), ha="center", va="center",
                    fontsize=10, color=COLORS["muted"], transform=ax.transAxes)
