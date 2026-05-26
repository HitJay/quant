"""本地Parquet缓存"""

import pandas as pd
from pathlib import Path


class Cache:
    """本地Parquet缓存，按 asset_type/symbol.parquet 组织"""

    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, asset_type: str, symbol: str) -> Path:
        return self.cache_dir / asset_type / f"{symbol}.parquet"

    def save(self, df: pd.DataFrame, asset_type: str, symbol: str):
        """保存DataFrame到缓存"""
        path = self._path(asset_type, symbol)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path)

    def load(self, asset_type: str, symbol: str) -> pd.DataFrame | None:
        """从缓存读取，不存在返回None"""
        path = self._path(asset_type, symbol)
        if not path.exists():
            return None
        return pd.read_parquet(path)
