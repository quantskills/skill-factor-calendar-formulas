"""Factor Calendar 系统性尾部风险暴露因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class TailRiskFactor(Factor):
    """估计个股收益对滞后市场尾部风险度量的滚动暴露。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        daily_market = stock_return.groupby(level="date", sort=False).mean()
        threshold = daily_market.rolling(21, min_periods=10).quantile(0.25)

        def tail_measure(position):
            start = max(0, position - 20)
            sample = daily_market.iloc[start : position + 1].dropna()
            quantile = threshold.iloc[position]
            if not np.isfinite(quantile) or quantile == 0:
                return np.nan
            tail = sample[sample < quantile]
            if tail.empty:
                return np.nan
            return tail.mean() / quantile

        market_tail = pd.Series(
            [tail_measure(position) for position in range(len(daily_market))],
            index=daily_market.index,
        ).shift(5)
        tail_panel = pd.Series(
            close.index.get_level_values("date").map(market_tail), index=close.index
        )
        frame = pd.concat({"return": stock_return, "tail": tail_panel}, axis=1)

        def rolling_beta(group):
            mean_return = group["return"].rolling(50, min_periods=25).mean()
            mean_tail = group["tail"].rolling(50, min_periods=25).mean()
            covariance = (group["return"] * group["tail"]).rolling(
                50, min_periods=25
            ).mean() - mean_return * mean_tail
            variance = (group["tail"] ** 2).rolling(
                50, min_periods=25
            ).mean() - mean_tail**2
            return (covariance / variance).where(variance > 0)

        result = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(rolling_beta).reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
