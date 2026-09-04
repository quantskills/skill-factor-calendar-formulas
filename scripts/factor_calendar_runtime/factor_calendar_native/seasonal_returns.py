"""Factor Calendar 月度收益季节性动量因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class SeasonalReturnsFactor(Factor):
    """组合去年同月与过去二至五年同月的月度超额收益。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_month_close = close.groupby(
            level="symbol", sort=False
        ).shift(21)
        monthly_return = (close / previous_month_close - 1).where(
            (close > 0) & (previous_month_close > 0)
        )
        market_monthly_return = monthly_return.groupby(
            level="date", sort=False
        ).transform("mean")
        excess_return = monthly_return - market_monthly_return
        seasonal_lags = [
            excess_return.groupby(level="symbol", sort=False).shift(period)
            for period in (252, 504, 756, 1008, 1260)
        ]
        seasonal_frame = pd.concat(seasonal_lags, axis=1)
        long_history_result = seasonal_frame.mean(axis=1, skipna=True)
        long_history_result = long_history_result.where(
            seasonal_frame.notna().any(axis=1)
        )
        short_history_result = excess_return.groupby(
            level="symbol", sort=False
        ).shift(21)
        tie_breaker = close.groupby(level="date", sort=False).rank(
            pct=True
        ) * 1e-12
        result = long_history_result.fillna(short_history_result)
        result = result + tie_breaker
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
