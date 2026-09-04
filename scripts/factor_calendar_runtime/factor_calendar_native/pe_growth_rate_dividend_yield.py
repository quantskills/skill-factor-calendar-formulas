"""Factor Calendar 市盈率增长率-股息收益率比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class PEGrowthRateDividendYieldFactor(Factor):
    """以规模估值、60日增长及低换手收益代理 PEG-DY。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        growth = (close / previous - 1).where(previous > 0)
        peg_proxy = np.log(market_cap.where(market_cap > 0)) / growth.abs().clip(
            lower=0.01
        )
        turnover_mean = turnover.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        dividend_yield_proxy = 1 / (1 + turnover_mean.abs())
        result = (peg_proxy / dividend_yield_proxy).where(growth.notna())
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
