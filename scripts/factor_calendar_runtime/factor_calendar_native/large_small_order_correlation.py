"""Factor Calendar 超大单-小单资金流同步秩相关性因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class LargeSmallOrderCorrelationFactor(Factor):
    """计算二十日超大单与小单净流入的 Spearman 秩相关。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        volume = factors["volume"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        average_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        average_volume = volume.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        large_flow = returns * (amount / average_amount).where(average_amount > 0)
        small_flow = returns * (volume / average_volume).where(average_volume > 0)
        large_rank = large_flow.groupby(level="date", sort=False).rank(pct=True)
        small_rank = small_flow.groupby(level="date", sort=False).rank(pct=True)
        large_wide = large_rank.unstack("symbol")
        small_wide = small_rank.unstack("symbol")
        correlation = large_wide.rolling(20, min_periods=10).corr(
            small_wide, pairwise=False
        )
        try:
            result = correlation.stack(future_stack=True)
        except TypeError:
            result = correlation.stack(dropna=False)
        result = result.reindex(small_flow.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
