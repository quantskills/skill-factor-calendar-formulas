"""Factor Calendar 流通市值对数因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class MarketCapFactor(Factor):
    """Factor Calendar 市值基础字段的自然对数。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0

        result = np.log(market_cap.where(market_cap > 0))
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
