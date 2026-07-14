"""炸板科普 v2 — Jinja2 + Playwright 渲染器."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = Path('/das/user/QYJI/quant')
TPL_DIR = ROOT / 'analysis' / 'zhaban_edu_templates'
OUT = ROOT / 'output' / 'hotspot' / '20260714' / 'xhs_zhaban_edu_v2_html'
OUT.mkdir(parents=True, exist_ok=True)

DATA = json.loads((OUT / 'data.json').read_text())
env = Environment(loader=FileSystemLoader(TPL_DIR), autoescape=False)

PAGES = [
    ('page_1.html', 'P1 钩子封面 (81/21/74%)'),
    ('page_2.html', 'P2 炸板机制三步'),
    ('page_3.html', 'P3 今日案例 (今天国际 3 炸)'),
    ('page_4.html', 'P4 三大散户陷阱'),
    ('page_5.html', 'P5 封板率温度计'),
    ('page_6.html', 'P6 总结 + CTA'),
    ('page_7.html', 'P7 打板策略量化回测'),
]


def render(only: list[str] | None = None):
    html_dir = OUT / '_html'
    html_dir.mkdir(exist_ok=True)

    # 1. 编译
    tpls_to_render = [(n, l) for n, l in PAGES if only is None or n in only]
    for tpl_name, label in tpls_to_render:
        tpl_path = TPL_DIR / tpl_name
        if not tpl_path.exists():
            print(f'  ⊘ {tpl_name} 不存在, 跳过')
            continue
        page_num = int(tpl_name.replace('page_', '').replace('.html', ''))
        tpl = env.get_template(tpl_name)
        html = tpl.render(data=DATA, page_num=page_num, title=label)
        (html_dir / tpl_name).write_text(html, encoding='utf-8')

    # 2. Playwright 截图
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={'width': 1080, 'height': 1440},
            device_scale_factor=2,
        )
        for tpl_name, label in tpls_to_render:
            html_path = html_dir / tpl_name
            if not html_path.exists():
                continue
            page = ctx.new_page()
            page.goto(f'file://{html_path.absolute()}')
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(600)
            out_png = OUT / tpl_name.replace('.html', '.png')
            page.screenshot(
                path=str(out_png),
                full_page=False,
                clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1440},
            )
            print(f'✓ {label} → {out_png.name}')
            page.close()
        browser.close()

    print(f'\n✅ 完成. PNG 在 {OUT}')


if __name__ == '__main__':
    args = sys.argv[1:]
    render(only=args if args else None)
