import pytest
from quant.data.fetcher import ETFDataFetcher

def test_fetch_single_etf():
    """获取单只ETF历史数据：沪深300ETF"""
    fetcher = ETFDataFetcher()
    df = fetcher.fetch("510300", start="2024-01-01", end="2024-06-30")
    
    assert df is not None, "应返回DataFrame"
    assert len(df) > 50, f"应有>50条数据，实际{len(df)}"
    assert "close" in df.columns, f"应包含close列，实际列: {list(df.columns)}"
    assert "open" in df.columns

def test_fetch_returns_consistent_columns():
    """不同ETF应有统一列名"""
    fetcher = ETFDataFetcher()
    df = fetcher.fetch("510500", start="2024-01-01", end="2024-03-31")
    expected_cols = {"open", "high", "low", "close", "volume"}
    assert expected_cols.issubset(set(df.columns)), \
        f"缺少列: {expected_cols - set(df.columns)}"
    assert df.index.name is None or df.index.name == "date"
