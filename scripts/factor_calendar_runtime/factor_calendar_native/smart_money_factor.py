"""Factor Calendar 机构活跃度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class SmartMoneyFactor(Factor):
    """以收益冲击和成交量构造机构活跃交易价格比率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        returns = close.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        score = (returns.abs() / volume.pow(0.25)).where(volume > 0)
        score_percentile = score.groupby(
            level="date", sort=False
        ).rank(pct=True)
        smart_weight = score_percentile.clip(lower=0).fillna(0) * volume
        smart_numerator = (close * smart_weight).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).sum()
        )
        smart_denominator = smart_weight.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).sum()
        )
        all_numerator = (close * volume).groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).sum()
        )
        all_denominator = volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).sum()
        )
        smart_vwap = (smart_numerator / smart_denominator).where(
            smart_denominator > 0
        )
        all_vwap = (all_numerator / all_denominator).where(
            all_denominator > 0
        )
        result = (smart_vwap / all_vwap).where(all_vwap > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
