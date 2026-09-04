"""Factor Calendar 分析师一致预期偏差度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AnalystFactor(Factor):
    """使用收盘价相对二十日均线的标准化偏离代理预期偏差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        mean_close = close.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        std_close = close.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).std(ddof=0)
        )
        result = ((close - mean_close) / std_close).where(std_close > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
