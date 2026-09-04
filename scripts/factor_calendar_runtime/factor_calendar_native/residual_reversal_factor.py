"""Factor Calendar 成交量加权残差反转因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class ResidualReversalFactor(Factor):
    """以日频资金流代理剔除资金流影响后的二十日反转残差。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        price_range = high - low
        flow = (
            (2 * close - high - low) / price_range * amount
        ).where((price_range > 0) & (amount > 0))
        flow_sum = flow.groupby(level="symbol", sort=False).transform(
            lambda values: values.rolling(5, min_periods=2).sum()
        )
        absolute_flow_sum = flow.abs().groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(5, min_periods=2).sum()
        )
        flow_strength = (flow_sum / absolute_flow_sum).where(
            absolute_flow_sum > 0
        )
        delayed_close = close.groupby(level="symbol", sort=False).shift(20)
        reversal = (close / delayed_close - 1).where(
            (close > 0) & (delayed_close > 0)
        )
        mean_return = reversal.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        mean_flow = flow_strength.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        covariance = (reversal * flow_strength).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - mean_return * mean_flow
        variance = (flow_strength**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - mean_flow**2
        beta = (covariance / variance).where(variance > 0)
        alpha = mean_return - beta * mean_flow
        result = reversal - alpha - beta * flow_strength
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
