"""Factor Calendar 年度总负债对数增长率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ComprehensiveDebtIssuanceFactor(Factor):
    """使用二十日市值对数增长代理外部融资扩张。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        previous = market_cap.groupby(level="symbol", sort=False).shift(20)
        previous = previous.fillna(market_cap)
        result = np.log(
            (market_cap / previous).where((market_cap > 0) & (previous > 0))
        )
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
