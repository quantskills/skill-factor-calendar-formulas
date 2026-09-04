"""Factor Calendar 非对称价格冲击偏度因子（日频基础行情代理）。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class PriceImpactBiasFactor(Factor):
    """比较上涨日和下跌日单位成交额价格冲击并进行标准化。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        daily_impact = (daily_return.abs() / amount).where(amount > 0)
        upward_impact = daily_impact.where(daily_return > 0, 0)
        downward_impact = daily_impact.where(daily_return < 0, 0)
        upward_count = (daily_return > 0).astype(float)
        downward_count = (daily_return < 0).astype(float)
        upward_sum = upward_impact.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=5).sum())
        downward_sum = downward_impact.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=5).sum())
        upward_number = upward_count.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=5).sum())
        downward_number = downward_count.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=5).sum())
        upward_mean = (upward_sum / upward_number).where(upward_number > 0)
        downward_mean = (downward_sum / downward_number).where(
            downward_number > 0
        )
        impact_difference = upward_mean - downward_mean
        scale = daily_impact.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(20, min_periods=5).std(ddof=0)
        )
        result = (impact_difference / scale).where(scale > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
