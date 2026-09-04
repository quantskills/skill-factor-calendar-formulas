"""Factor Calendar 营运资本同比增速市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class YoYGrowthInWorkingCapitalFactor(Factor):
    """以低换手部分市值估计营运资本并计算同比增长率。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        average_market_cap = market_cap.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        working_capital = average_market_cap * (
            1 - average_turnover.clip(lower=0, upper=1)
        )
        previous_year = working_capital.groupby(
            level="symbol", sort=False
        ).shift(252)
        recent_fallback = working_capital.groupby(
            level="symbol", sort=False
        ).shift(60)
        previous_year = previous_year.fillna(recent_fallback)
        denominator = previous_year.abs().where(previous_year.abs() > 1e-12)
        result = (working_capital - previous_year) / denominator
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
