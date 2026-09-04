"""Factor Calendar 盈余公告日次日开盘跳空幅度因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EarningsAnnouncementStockJumpFactor(Factor):
    """计算次日开盘价相对公告日收盘价的跳空收益。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        result = (open_price / previous_close - 1).where(
            (open_price > 0) & (previous_close > 0)
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
