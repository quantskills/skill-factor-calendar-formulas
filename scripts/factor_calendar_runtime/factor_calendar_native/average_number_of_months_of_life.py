"""Factor Calendar 近五年平均专利寿命月数市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AverageNumberOfMonthsOfLifeFactor(Factor):
    """以样本存续月数、收益稳定性和规模估计专利寿命。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        observations = close.notna().astype(float).groupby(
            level="symbol", sort=False
        ).cumsum()
        sample_months = (observations / 21).clip(upper=60)
        daily_return = close.groupby(
            level="symbol", sort=False
        ).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=10).std())
        stability_rank = (-volatility).groupby(
            level="date", sort=False
        ).rank(pct=True)
        size_rank = market_cap.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = sample_months * (
            0.5 + 0.3 * stability_rank + 0.2 * size_rank
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
