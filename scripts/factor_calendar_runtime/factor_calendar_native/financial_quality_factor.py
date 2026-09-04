"""Factor Calendar 综合财务质量市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class FinancialQualityFactor(Factor):
    """合成收益稳定性、成交效率和换手稳定性代理财务质量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        volume = factors["volume"] + 0
        turnover = factors["turnover"] + 0
        daily_return = close.groupby(level="symbol", sort=False).pct_change()
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        average_price = (amount / volume).where(volume > 0)
        price_efficiency = close / average_price.where(average_price > 0)
        turnover_stability = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=2).std())
        components = pd.concat(
            [-volatility, price_efficiency, -turnover_stability], axis=1
        )
        ranks = components.groupby(level="date", sort=False).rank(pct=True)
        result = ranks.mean(axis=1).fillna(0.0)
        result.name = "value"
        return result
