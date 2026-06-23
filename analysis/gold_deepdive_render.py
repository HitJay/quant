"""黄金深度分析 — Jinja2 模板 → Playwright 截图渲染器."""
from __future__ import annotations
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = Path('/das/user/QYJI/quant')
TPL_DIR = ROOT / 'analysis' / 'gold_deepdive_templates'
OUT = ROOT / 'output' / 'research' / 'gold_deepdive_v1'
OUT.mkdir(parents=True, exist_ok=True)

DATA = json.loads((OUT / 'data.json').read_text())

env = Environment(loader=FileSystemLoader(TPL_DIR), autoescape=False)

# 自定义 filters
def signed(x, dp=2):
    return f"{x:+.{dp}f}" if isinstance(x, (int, float)) else str(x)
env.filters['signed'] = signed


PAGES = [
    ('page_1.html', 'P1 封面'),
    ('page_2.html', 'P2 月度时间线'),
    ('page_3.html', 'P3 黄金股 vs 黄金 ETF'),
    ('page_4.html', 'P4 横向收益矩阵'),
    ('page_5.html', 'P5 历史回撤复盘'),
    ('page_6.html', 'P6 当前买点'),
    ('page_7.html', 'P7 CTA'),
]


def render():
    """编译 HTML + 截图为 PNG."""
    html_dir = OUT / '_html'
    html_dir.mkdir(exist_ok=True)

    # 1. 编译 HTML
    for tpl_name, label in PAGES:
        tpl_path = TPL_DIR / tpl_name
        if not tpl_path.exists():
            print(f'  ⊘ {tpl_name} 不存在, 跳过')
            continue
        page_num = int(tpl_name.replace('page_', '').replace('.html', ''))
        tpl = env.get_template(tpl_name)
        html = tpl.render(data=DATA, page_num=page_num, title=label)
        out_html = html_dir / tpl_name
        out_html.write_text(html, encoding='utf-8')

    # 2. Playwright 截图
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={'width': 1080, 'height': 1440},
            device_scale_factor=2,   # 2x DPR → 2160x2880 PNG
        )
        for tpl_name, label in PAGES:
            html_path = html_dir / tpl_name
            if not html_path.exists():
                continue
            page = ctx.new_page()
            page.goto(f'file://{html_path.absolute()}')
            # 等 Tailwind / Chart.js 渲染完
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(800)
            out_png = OUT / tpl_name.replace('.html', '.png')
            page.screenshot(path=str(out_png), full_page=False,
                          clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1440})
            print(f'✓ {label} → {out_png.name}')
            page.close()
        browser.close()

    print(f'\n✅ 全部完成. PNG 在 {OUT}')


if __name__ == '__main__':
    render()
