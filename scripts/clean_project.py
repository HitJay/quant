#!/usr/bin/env python3
"""清理项目：迭代产物旧版 + .venv __pycache__ + 根目录误放文件"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

PROJECT = Path("/das/user/QYJI/quant")


def clean_hotspot_iterations():
    """
    output/hotspot/<date>/ 下保留每个系列的最新 vN，删掉旧版。
    例如 xhs_hstech_rally_html_v1/v2/v3/v4/v5 → 只保留 v5
    """
    hotspot = PROJECT / "output" / "hotspot"
    if not hotspot.exists():
        return 0

    total_freed = 0
    total_dirs = 0

    for date_dir in sorted(hotspot.iterdir()):
        if not date_dir.is_dir():
            continue

        # 按系列分组：取 "xhs_xxx_v1" 中的 base="xhs_xxx" 和版本号
        groups = defaultdict(list)
        for d in date_dir.iterdir():
            if not d.is_dir():
                continue
            name = d.name
            m = re.match(r"^(.+?)_v(\d+)$", name)
            if m:
                base = m.group(1)
                ver = int(m.group(2))
                groups[base].append((ver, d))

        for base, entries in groups.items():
            entries.sort(key=lambda x: x[0])
            keep_dir = entries[-1][1]  # 最大版本
            for ver, old_dir in entries[:-1]:
                size = sum(f.stat().st_size for f in old_dir.rglob("*") if f.is_file())
                shutil.rmtree(old_dir)
                total_freed += size
                total_dirs += 1
                print(f"  🗑  删旧版: {old_dir.relative_to(PROJECT)}  ({size/1024:.0f} KB)")

    if total_dirs:
        print(f"  ✅ 清理 {total_dirs} 个旧版目录，释放 {total_freed/1024/1024:.1f} MB")
    else:
        print(f"  ℹ️   无旧版需要清理")
    return total_freed


def clean_venv_pycache():
    """清理 .venv 下第三方库的 __pycache__"""
    site_pkgs = list(PROJECT.glob(".venv/lib/python*/site-packages"))
    if not site_pkgs:
        print("  ℹ️   未找到 site-packages")
        return 0

    site_pkg = site_pkgs[0]
    total_freed = 0
    count = 0

    for pycache in site_pkg.rglob("__pycache__"):
        if pycache.is_dir():
            size = sum(f.stat().st_size for f in pycache.rglob("*") if f.is_file())
            shutil.rmtree(pycache)
            total_freed += size
            count += 1

    # 也清理 .venv 根目录下面的 __pycache__
    root_pycache = PROJECT / ".venv" / "__pycache__"
    if root_pycache.exists():
        size = sum(f.stat().st_size for f in root_pycache.rglob("*") if f.is_file())
        shutil.rmtree(root_pycache)
        total_freed += size
        count += 1

    if count:
        print(f"  ✅ 清理 {count} 个第三方 __pycache__，释放 {total_freed/1024/1024:.1f} MB")
    else:
        print(f"  ℹ️   无 __pycache__ 需要清理")
    return total_freed


def clean_root_junk():
    """删掉根目录误放的截图"""
    junk = [
        PROJECT / "image.png",
        PROJECT / "image copy.png",
    ]
    total_freed = 0
    for f in junk:
        if f.exists():
            sz = f.stat().st_size
            f.unlink()
            total_freed += sz
            print(f"  🗑  删除: {f.name}  ({sz/1024:.0f} KB)")

    if total_freed:
        print(f"  ✅ 释放 {total_freed/1024/1024:.1f} MB")
    else:
        print(f"  ℹ️   无垃圾文件需要清理")
    return total_freed


def main():
    print("=" * 50)
    print("  🧹 项目清理")
    print("=" * 50)
    print()

    print("[1/3] 清理 output/hotspot/ 旧版迭代产物...")
    freed1 = clean_hotspot_iterations()
    print()

    print("[2/3] 清理 .venv 第三方 __pycache__...")
    freed2 = clean_venv_pycache()
    print()

    print("[3/3] 清理根目录误放文件...")
    freed3 = clean_root_junk()
    print()

    total = freed1 + freed2 + freed3
    print("=" * 50)
    print(f"  🎉 总计释放 {total/1024/1024:.1f} MB")
    print("=" * 50)


if __name__ == "__main__":
    main()
