"""Factor Calendar 多层客户关系加权动量市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class MultiLayerCustomerMomentumFactor(Factor):
    """组合短中期市场网络中心性与动量代理多层客户关系。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = returns.groupby(
            level="date", sort=False
        ).transform("mean")
        frame = pd.concat(
            {"stock": returns, "market": market_return}, axis=1
        )

        def rolling_correlation(group, window, minimum):
            return group["stock"].rolling(
                window, min_periods=minimum
            ).corr(group["market"])

        short_centrality = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(
            lambda item: rolling_correlation(item, 20, 10)
        ).reindex(close.index)
        long_centrality = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(
            lambda item: rolling_correlation(item, 60, 20)
        ).reindex(close.index)
        short_close = close.groupby(level="symbol", sort=False).shift(20)
        long_close = close.groupby(level="symbol", sort=False).shift(60)
        short_momentum = (close / short_close - 1).where(
            (close > 0) & (short_close > 0)
        )
        long_momentum = (close / long_close - 1).where(
            (close > 0) & (long_close > 0)
        )
        result = 0.6 * short_centrality * short_momentum
        result += 0.4 * long_centrality * long_momentum
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
