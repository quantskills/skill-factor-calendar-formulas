"""Factor Calendar 残差偏度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class IdiosyncraticSkewnessFactor(Factor):
    """以市场平均收益为基准计算短窗口 CAPM 残差偏度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        stock_return = close.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        market_return = stock_return.groupby(
            level="date", sort=False
        ).transform("mean")
        stock_mean = stock_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        market_mean = market_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        covariance = (stock_return * market_return).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - stock_mean * market_mean
        variance = (market_return**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - market_mean**2
        beta = (covariance / variance).where(variance > 0)
        alpha = stock_mean - beta * market_mean
        residual = stock_return - alpha - beta * market_return
        result = residual.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).skew()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
