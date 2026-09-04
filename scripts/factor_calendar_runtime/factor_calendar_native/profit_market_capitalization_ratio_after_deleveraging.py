"""Factor Calendar 去杠杆经营性资产盈利收益率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ProfitMarketCapitalizationRatioAfterDeleveragingFactor(Factor):
    """使用二十日成交额相对市值代理经营性资产盈利收益率。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        average_amount = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=1).mean()
        )
        result = (average_amount / market_cap).where(market_cap > 0)
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
