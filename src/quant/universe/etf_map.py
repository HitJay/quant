"""ETF分类映射表 — 管理可投资的ETF代码"""

CATEGORY_NAMES = ["WIDE", "INDUSTRY", "STRATEGY", "BOND", "COMMODITY", "CROSS", "MONEY"]

# ETF分类映射：分类 → {代码: 名称}
ETF_MAP: dict[str, dict[str, str]] = {
    "WIDE": {
        "510300": "沪深300ETF",
        "510500": "中证500ETF",
        "510050": "上证50ETF",
        "159949": "创业板50",
        "588000": "科创50ETF",
    },
    "INDUSTRY": {
        "512880": "证券ETF",
        "512690": "酒ETF",
        "159995": "芯片ETF",
        "516160": "新能源ETF",
        "512980": "传媒ETF",
    },
    "STRATEGY": {
        "510880": "红利ETF",
        "512100": "中证1000ETF",
        "512890": "红利低波ETF",
    },
    "BOND": {
        "511010": "国债ETF",
        "511260": "10年国债ETF",
        "511380": "可转债ETF",
    },
    "COMMODITY": {
        "518880": "黄金ETF",
        "159985": "豆粕ETF",
        "159866": "有色金属ETF",
    },
    "CROSS": {
        "513100": "纳指ETF",
        "159920": "恒生ETF",
    },
    "MONEY": {
        "511990": "华宝添益",
    },
}


def get_etf_list(category: str) -> list[str]:
    """获取指定分类的ETF代码列表"""
    return list(ETF_MAP.get(category, {}).keys())


def get_all_etfs(categories: list[str] | None = None) -> dict[str, str]:
    """获取所有ETF {代码: 名称}，可按分类过滤"""
    if categories is None:
        categories = list(ETF_MAP.keys())
    result: dict[str, str] = {}
    for cat in categories:
        result.update(ETF_MAP.get(cat, {}))
    return result
