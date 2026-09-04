"""Factor Calendar 单笔成交金额分位偏离度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SingleTransactionAmountQuantileFactor(Factor):
    """按二十日成交额分布计算十分位数相对极差的位置。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        rolling_min = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=10).min()
        )
        rolling_max = amount.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=10).max()
        )
        lower_quantile = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).quantile(0.1)
        )
        spread = rolling_max - rolling_min
        result = ((lower_quantile - rolling_min) / spread).where(spread > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
