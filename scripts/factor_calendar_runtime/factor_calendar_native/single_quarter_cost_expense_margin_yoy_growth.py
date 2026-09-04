"""Factor Calendar 单季度成本费用利润率同比增速市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class SingleQuarterCostExpenseMarginYoYGrowthFactor(Factor):
    """以短期价格效率相对长期基准的改善代理利润率同比增长。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        intraday_efficiency = ((close - open_price) / open_price).where(open_price > 0)
        weighted_efficiency = intraday_efficiency * np.log1p(amount.clip(lower=0))
        short_margin = weighted_efficiency.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(20, min_periods=5).mean())
        long_margin = weighted_efficiency.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(252, min_periods=60).mean())
        result = (short_margin - long_margin) / long_margin.abs().replace(0, np.nan)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
