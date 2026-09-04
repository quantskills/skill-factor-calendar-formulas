"""Factor Calendar 一致预期收益率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ConsistentExpectedReturnRateFactor(Factor):
    """使用二十日价格趋势代理市场一致预期收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        result = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
