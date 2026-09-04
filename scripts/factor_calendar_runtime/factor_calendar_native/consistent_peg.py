"""Factor Calendar 一致预期 PEG 比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ConsistentPEGFactor(Factor):
    """以规模估值代理除以60日价格增长率构造 PEG。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous = close.groupby(level="symbol", sort=False).shift(60)
        expected_growth = (close / previous - 1).where(previous > 0)
        valuation_proxy = np.log(market_cap.where(market_cap > 0))
        result = (
            valuation_proxy / expected_growth.abs().clip(lower=0.01)
        ).where(expected_growth.notna())
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
