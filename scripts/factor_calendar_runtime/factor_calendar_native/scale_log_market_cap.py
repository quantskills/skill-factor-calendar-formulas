"""Factor Calendar 对数自由流通市值因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ScaleLogMarketCapFactor(Factor):
    """自由流通市值的自然对数。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0

        result = np.log(market_cap.where(market_cap > 0))
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
