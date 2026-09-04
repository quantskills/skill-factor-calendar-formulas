"""Factor Calendar 分析师目标价隐含收益率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class TargetPriceImpliedReturnFactor(Factor):
    """使用六十日最高价相对当前价格的空间代理目标价收益率。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        close = factors["close"] + 0
        target_price = high.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).max()
        )
        result = (target_price / close - 1).where(close > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
