from quant.universe.etf_map import get_etf_list, get_all_etfs, CATEGORY_NAMES


def test_wide_etfs_not_empty():
    """宽基ETF至少包含沪深300和中证500"""
    wide = get_etf_list("WIDE")
    assert len(wide) >= 3
    assert "510300" in wide
    assert "510500" in wide


def test_all_categories_covered():
    """所有分类都不为空"""
    for cat in CATEGORY_NAMES:
        etfs = get_etf_list(cat)
        assert len(etfs) > 0, f"分类 {cat} 不应为空"


def test_get_all_etfs():
    """get_all_etfs应返回所有ETF"""
    all_etfs = get_all_etfs()
    assert len(all_etfs) >= 15
    assert "510300" in all_etfs
    assert all_etfs["510300"] == "沪深300ETF"


def test_get_all_etfs_filtered():
    """get_all_etfs支持按分类过滤"""
    subset = get_all_etfs(categories=["COMMODITY"])
    assert "518880" in subset  # 黄金ETF
    assert "510300" not in subset  # 不在商品分类
