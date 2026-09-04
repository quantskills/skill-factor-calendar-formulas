"""Factor Calendar 市盈率相对盈利增长率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class PEGrowthFactor(Factor):
    """以规模估值代理除以60日价格增长率构造相对增长估值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        growth = (close / previous - 1).where(previous > 0)
        result = (
            np.log(market_cap.where(market_cap > 0))
            / growth.abs().clip(lower=0.01)
        ).where(growth.notna())
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
