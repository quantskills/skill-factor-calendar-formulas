"""Factor Calendar 负债权益比市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class QualityDebtToEquityRatioFactor(Factor):
    """以价格风险相对交易承载能力代理财务杠杆。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        returns = close.groupby(level="symbol", sort=False).pct_change()
        volatility = returns.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=2).std(ddof=0)
        )
        trading_capacity = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=1).mean())
        result = volatility / trading_capacity.replace(0, np.nan)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
