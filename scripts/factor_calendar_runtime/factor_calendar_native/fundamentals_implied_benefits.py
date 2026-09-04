"""Factor Calendar 基本面趋势预期收益率市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class FundamentalsImpliedBenefitsFactor(Factor):
    """合成价格趋势、活跃度趋势和价值规模代理。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / previous_close - 1).replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0.0)
        short_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(5, min_periods=1).mean())
        long_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        activity = (short_turnover / long_turnover - 1).replace(
            [np.inf, -np.inf], np.nan
        ).fillna(0.0)
        value = -np.log(market_cap.where(market_cap > 0)).fillna(0.0)
        components = pd.concat([momentum, activity, value], axis=1)
        ranks = components.groupby(level="date", sort=False).rank(pct=True)
        result = ranks.mean(axis=1).fillna(0.0)
        result.name = "value"
        return result
