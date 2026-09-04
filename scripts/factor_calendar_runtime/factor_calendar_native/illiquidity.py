"""Factor Calendar 高频波动率路径长度加权非流动性因子（日频代理）。"""

import numpy as np

from factor_calendar_runtime import Factor


class IlliquidityFactor(Factor):
    """以日 K 线波动路径成交额比的二十日均值代理高频原始因子。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0

        valid = (
            (open_price > 0)
            & (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= low)
            & (high >= open_price)
            & (high >= close)
            & (low <= open_price)
            & (low <= close)
            & (amount > 0)
        )
        path_length = 2 * (high - low) - (close - open_price).abs()
        daily_illiquidity = (path_length / amount).where(
            valid & (path_length >= 0)
        )
        result = (
            daily_illiquidity.groupby(level="symbol", sort=False)
            .rolling(window=20, min_periods=20)
            .mean()
            .droplevel(0)
            .reindex(daily_illiquidity.index)
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
