"""Factor Calendar 时间加权平均相对价格位置因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class TimeWeightedAverageStockRelativePricePositionFactor(Factor):
    """以日 K 线 OHLC 均价代理 TWAP 的相对价格位置。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        twap_proxy = (open_price + high + low + close) / 4
        result = ((twap_proxy - low) / (high - low)).where(high > low)
        result = result.clip(0, 1).replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
