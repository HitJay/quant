"""HotspotFetcher smoke test — 真实网络拉取，验证字段不丢"""

import pytest
import pandas as pd

from quant.data.hotspot_fetcher import HotspotFetcher, _last_trading_day_str


@pytest.fixture(scope="module")
def fetcher(tmp_path_factory):
    cache = tmp_path_factory.mktemp("hotspot_cache")
    return HotspotFetcher(cache_dir=str(cache))


@pytest.mark.network
def test_zt_pool_has_required_cols(fetcher):
    df = fetcher.zt_pool(date=_last_trading_day_str())
    assert isinstance(df, pd.DataFrame)
    if len(df) == 0:
        pytest.skip("非交易日或源端无数据")
    for col in ["代码", "名称", "连板数", "所属行业"]:
        assert col in df.columns, f"涨停池缺少字段: {col}"


@pytest.mark.network
def test_xueqiu_hot_tweet(fetcher):
    df = fetcher.xueqiu_hot(by="tweet")
    if len(df) == 0:
        pytest.skip("源端无数据")
    assert {"股票代码", "股票简称", "关注"} <= set(df.columns)
    assert len(df) > 100  # 雪球榜单一般有几千条


@pytest.mark.network
def test_em_hot_rank(fetcher):
    df = fetcher.em_hot_rank()
    if len(df) == 0:
        pytest.skip("源端无数据")
    assert {"当前排名", "代码", "股票名称"} <= set(df.columns)


@pytest.mark.network
def test_concept_board_via_push2(fetcher):
    df = fetcher.concept_board()
    if len(df) == 0:
        pytest.skip("源端无数据")
    assert {"name", "pct_chg", "main_net_in", "leader_name"} <= set(df.columns)
    # 应该按涨幅排
    if len(df) >= 2:
        assert df["pct_chg"].iloc[0] >= df["pct_chg"].iloc[-1]


@pytest.mark.network
def test_em_global_news_has_time(fetcher):
    df = fetcher.em_global_news(limit=20)
    if len(df) == 0:
        pytest.skip("源端无数据")
    assert "标题" in df.columns
    assert "发布时间" in df.columns
    assert len(df) <= 20


@pytest.mark.network
def test_fetch_all_returns_dict(fetcher):
    data = fetcher.fetch_all()
    assert isinstance(data, dict)
    expected_keys = {
        "zt_pool", "zt_zbgc", "zt_strong",
        "xueqiu_follow", "xueqiu_tweet", "em_hot_rank",
        "lhb", "concept_board", "industry_board", "em_global_news",
    }
    assert expected_keys <= set(data.keys())
    # 至少一半源应该活
    alive = sum(1 for v in data.values() if len(v) > 0)
    assert alive >= len(expected_keys) // 2, f"只有 {alive}/{len(expected_keys)} 个源活着"


def test_cache_roundtrip(fetcher, tmp_path):
    """脱网测：写入缓存后能读回"""
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    fetcher._save_cache(df, "unittest", "20260101")
    loaded = fetcher._load_cache("unittest", "20260101")
    assert loaded is not None
    assert len(loaded) == 3
    assert list(loaded.columns) == ["a", "b"]
