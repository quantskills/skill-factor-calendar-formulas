"""Factor Calendar 主力成交额-价格相关性市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class MainForceTradingSentimentFactor(Factor):
    """使用二十日成交额与收盘价相关性代理主力交易情绪。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        close = factors["close"] + 0
        frame = pd.concat({"amount": amount, "close": close}, axis=1)
        result = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(
            lambda item: item["amount"].rolling(
                20, min_periods=10
            ).corr(item["close"])
        ).reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
