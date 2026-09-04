"""Factor Calendar 盈余公告超额收益率因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EarningsAnnouncementReturnFactor(Factor):
    """计算公告事件日个股收益率减基准收益率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        benchmark_return = stock_return.groupby(
            level="date", sort=False
        ).transform("mean")
        result = stock_return - benchmark_return
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
