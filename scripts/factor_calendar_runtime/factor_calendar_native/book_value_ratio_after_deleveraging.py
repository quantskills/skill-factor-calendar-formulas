"""Factor Calendar 去杠杆化账面价值/市值比市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class BookValueRatioAfterDeleveragingFactor(Factor):
    """使用逆对数市值代理去杠杆化账面市值比。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        result = -np.log(market_cap.where(market_cap > 0))
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
