from quant.universe.config import UniverseConfig
from quant.universe.etf_map import get_etf_list


def test_universe_config_default():
    """默认配置：使用全部宽基ETF"""
    config = UniverseConfig()
    symbols = config.get_symbols()
    assert len(symbols) >= 3
    assert "510300" in symbols


def test_universe_config_custom_etfs():
    """自定义ETF列表"""
    config = UniverseConfig(etf_codes=["510300", "510500"])
    symbols = config.get_symbols()
    assert symbols == ["510300", "510500"]


def test_universe_config_with_filters():
    """带过滤条件的配置"""
    config = UniverseConfig(
        etf_codes=["510300", "510500", "510050", "159949"],
        max_symbols=2,
    )
    symbols = config.get_symbols()
    assert len(symbols) == 2


def test_universe_config_categories():
    """按分类选择ETF"""
    config = UniverseConfig(etf_categories=["COMMODITY"])
    symbols = config.get_symbols()
    assert "518880" in symbols  # 黄金ETF
    assert "510300" not in symbols  # 不含宽基


def test_universe_config_categories_override_codes():
    """categories和codes同时设置时，codes优先"""
    config = UniverseConfig(etf_categories=["COMMODITY"], etf_codes=["510300"])
    symbols = config.get_symbols()
    assert symbols == ["510300"]


def test_stock_filter_exclude_st():
    """股票筛选：排除ST"""
    from quant.universe.stock_filter import StockFilter
    f = StockFilter(exclude_st=True, min_price=5)
    # 模拟数据
    stocks = {
        "000001": {"name": "平安银行", "is_st": False, "close": 12.5},
        "600000": {"name": "浦发银行", "is_st": False, "close": 8.0},
        "000005": {"name": "*ST星源", "is_st": True, "close": 3.0},
    }
    result = f.filter(stocks)
    assert "000005" not in result  # ST被排除
    assert "000001" in result
