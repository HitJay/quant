"""生成小红书封面 - 商品轮动策略对比黄金"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np

# 使用Windows字体
font_path = '/mnt/c/Windows/Fonts/simhei.ttf'
ZH_FONT = FontProperties(fname=font_path)
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(9, 12), facecolor='#1a1a2e')

# 顶部标题区域 (y: 0.7-1.0)
# 主标题 - 超大字体，黄色高亮
ax.text(0.5, 0.92, '黄金暴跌-25%', 
        transform=ax.transAxes, fontsize=58, fontweight='bold',
        color='#FFD700', ha='center', va='center', fontproperties=ZH_FONT,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#2d2d44', edgecolor='#FFD700', linewidth=3))

ax.text(0.5, 0.82, '这个策略却赚了...', 
        transform=ax.transAxes, fontsize=42, fontweight='bold',
        color='#00ff88', ha='center', va='center', fontproperties=ZH_FONT)

# 副标题
ax.text(0.5, 0.73, '商品轮动 vs 买入持有', 
        transform=ax.transAxes, fontsize=28,
        color='#cccccc', ha='center', va='center', fontproperties=ZH_FONT)

# 中间对比区域 (y: 0.35-0.7)
# 左边：策略
ax.add_patch(patches.Rectangle((0.08, 0.38), 0.38, 0.30, 
                               transform=ax.transAxes,
                               facecolor='#00ff88', alpha=0.15,
                               edgecolor='#00ff88', linewidth=2))

ax.text(0.27, 0.63, '商品轮动策略', 
        transform=ax.transAxes, fontsize=24, fontweight='bold',
        color='#00ff88', ha='center', va='center', fontproperties=ZH_FONT)

ax.text(0.27, 0.52, '+134%', 
        transform=ax.transAxes, fontsize=72, fontweight='bold',
        color='#00ff88', ha='center', va='center')

ax.text(0.27, 0.42, '年化 +19.4%', 
        transform=ax.transAxes, fontsize=20,
        color='#88ffaa', ha='center', va='center', fontproperties=ZH_FONT)

# 右边：黄金
ax.add_patch(patches.Rectangle((0.54, 0.38), 0.38, 0.30, 
                               transform=ax.transAxes,
                               facecolor='#FFD700', alpha=0.15,
                               edgecolor='#FFD700', linewidth=2))

ax.text(0.73, 0.63, '买入黄金', 
        transform=ax.transAxes, fontsize=24, fontweight='bold',
        color='#FFD700', ha='center', va='center', fontproperties=ZH_FONT)

ax.text(0.73, 0.52, '+53%', 
        transform=ax.transAxes, fontsize=72, fontweight='bold',
        color='#FFD700', ha='center', va='center')

ax.text(0.73, 0.42, '年化 +8.9%', 
        transform=ax.transAxes, fontsize=20,
        color='#ffed99', ha='center', va='center', fontproperties=ZH_FONT)

# VS 标志
ax.text(0.5, 0.53, 'VS', 
        transform=ax.transAxes, fontsize=36, fontweight='bold',
        color='#ffffff', ha='center', va='center',
        bbox=dict(boxstyle='circle,pad=0.2', facecolor='#ff4444', edgecolor='white', linewidth=3))

# 底部信息区域 (y: 0.05-0.35)
# 时间范围
ax.text(0.5, 0.30, '2021.08 - 2026.05 | 5年实测数据', 
        transform=ax.transAxes, fontsize=18,
        color='#888888', ha='center', va='center', fontproperties=ZH_FONT)

# 三个关键点
points = [
    ('>>', '黄金弱势期照样跑赢'),
    ('!!', '2026年1月回撤-54%'),
    ('**', '3个商品轮动策略')
]

y_positions = [0.20, 0.13, 0.06]
for (marker, text), y_pos in zip(points, y_positions):
    ax.text(0.5, y_pos, f'{marker} {text}', 
            transform=ax.transAxes, fontsize=20, fontweight='bold',
            color='#ffffff', ha='center', va='center', fontproperties=ZH_FONT)

# 隐藏坐标轴
ax.axis('off')

# 添加边框
ax.add_patch(patches.Rectangle((0.02, 0.02), 0.96, 0.96, 
                               transform=ax.transAxes,
                               facecolor='none', edgecolor='#00ff88', 
                               linewidth=4, alpha=0.5))

plt.tight_layout(pad=0)
plt.savefig('output/commodity-rotation/cover_xiaohongshu.png', 
            dpi=200, bbox_inches='tight', facecolor='#1a1a2e')
plt.close()

print("✅ 封面已生成: output/commodity-rotation/cover_xiaohongshu.png")
