"""Factor Calendar 残差资金流强度因子（日频基础行情代理）。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class ResidualFundFlowIntensityFactor(Factor):
    """以资金流量乘数代理资金流，并剔除二十日动量影响。"""

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
        momentum = (close / delayed_close - 1).where(
            (close > 0) & (delayed_close > 0)
        )
        mean_strength = flow_strength.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        mean_momentum = momentum.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        )
        covariance = (flow_strength * momentum).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - mean_strength * mean_momentum
        variance = (momentum**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).mean()
        ) - mean_momentum**2
        beta = (covariance / variance).where(variance > 0)
        alpha = mean_strength - beta * mean_momentum
        result = flow_strength - alpha - beta * momentum
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
