"""Factor Calendar 行业日内与隔夜收益率动量因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class IndustryMomentumFactor(Factor):
    """计算二十日日内动量减隔夜动量的综合行业代理信号。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)

        intraday_return = (close / open_price - 1).where(
            (close > 0) & (open_price > 0)
        )
        overnight_return = (open_price / previous_close - 1).where(
            (open_price > 0) & (previous_close > 0)
        )
        intraday_momentum = intraday_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).sum()
        )
        overnight_momentum = overnight_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).sum()
        )

        result = intraday_momentum - overnight_momentum
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
