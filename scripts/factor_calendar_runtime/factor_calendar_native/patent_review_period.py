"""Factor Calendar 近五年发明专利平均审查周期市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class PatentReviewPeriodFactor(Factor):
    """以长期信息复杂度、价格调整速度和规模估计审查月数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        daily_return = close.groupby(
            level="symbol", sort=False
        ).pct_change()
        information_complexity = daily_return.abs().groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(120, min_periods=20).mean())
        short_momentum = close / close.groupby(
            level="symbol", sort=False
        ).shift(20) - 1
        long_momentum = close / close.groupby(
            level="symbol", sort=False
        ).shift(60) - 1
        price_adjustment_delay = (short_momentum - long_momentum / 3).abs()
        components = pd.concat(
            [information_complexity, price_adjustment_delay, market_cap],
            axis=1,
        )
        ranks = components.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = 6 + 30 * ranks.mean(axis=1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
