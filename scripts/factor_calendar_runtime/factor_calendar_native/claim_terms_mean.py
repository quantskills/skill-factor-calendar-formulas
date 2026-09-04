"""Factor Calendar 近五年新公开专利平均权利要求项数市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class ClaimTermsMeanFactor(Factor):
    """以长期成长、成交投入和技术复杂度估计平均权利要求项数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(
            level="symbol", sort=False
        ).shift(252)
        fallback_close = close.groupby(
            level="symbol", sort=False
        ).shift(60)
        previous_close = previous_close.fillna(fallback_close)
        growth = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        investment_intensity = (amount / market_cap).where(market_cap > 0)
        average_investment = investment_intensity.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=10).mean())
        technical_complexity = ((high - low) / close).where(close > 0)
        average_complexity = technical_complexity.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=10).mean())
        components = pd.concat(
            [growth, average_investment, average_complexity], axis=1
        )
        ranks = components.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = 5 + 25 * ranks.mean(axis=1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
