"""Factor Calendar 科技关联加权动量因子（日频基础行情代理）。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class TechnologyMomentumFactor(Factor):
    """以股票和成交额加权市场的收益相关性代理科技关联度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        valid_amount = amount.where((amount > 0) & stock_return.notna())
        weighted_return = stock_return * valid_amount
        market_numerator = weighted_return.groupby(
            level="date", sort=False
        ).transform("sum")
        market_denominator = valid_amount.groupby(
            level="date", sort=False
        ).transform("sum")
        market_return = (market_numerator / market_denominator).where(
            market_denominator > 0
        )

        mean_stock = stock_return.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=20).mean())
        mean_market = market_return.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=20).mean())
        mean_product = (stock_return * market_return).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=20).mean()
        )
        stock_variance = (stock_return**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=20).mean()
        ) - mean_stock**2
        market_variance = (market_return**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=20).mean()
        ) - mean_market**2
        covariance = mean_product - mean_stock * mean_market
        correlation = (
            covariance / (stock_variance * market_variance) ** 0.5
        ).where((stock_variance > 0) & (market_variance > 0))
        market_momentum = market_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: (1 + values).rolling(
                20, min_periods=20
            ).apply(np.prod, raw=True)
            - 1
        )
        result = correlation * market_momentum
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
