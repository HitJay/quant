import tempfile
import pandas as pd
from quant.data.cache import Cache


def test_save_and_load():
    """缓存写入后再读取，数据应一致"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(cache_dir=tmpdir)
        df = pd.DataFrame(
            {"close": [1.0, 2.0, 3.0]},
            index=pd.date_range("2024-01-01", periods=3),
        )
        cache.save(df, "test_etf", "510300")

        loaded = cache.load("test_etf", "510300")
        assert loaded is not None
        assert len(loaded) == 3
        assert loaded["close"].tolist() == [1.0, 2.0, 3.0]


def test_load_missing_returns_none():
    """不存在的缓存应返回None"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(cache_dir=tmpdir)
        result = cache.load("nonexistent", "999999")
        assert result is None


def test_save_overwrites():
    """重复save应覆盖旧数据"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = Cache(cache_dir=tmpdir)
        df1 = pd.DataFrame({"close": [1.0]}, index=pd.date_range("2024-01-01", periods=1))
        df2 = pd.DataFrame({"close": [9.0]}, index=pd.date_range("2024-01-02", periods=1))

        cache.save(df1, "etf", "test")
        cache.save(df2, "etf", "test")

        loaded = cache.load("etf", "test")
        assert loaded["close"].iloc[0] == 9.0
