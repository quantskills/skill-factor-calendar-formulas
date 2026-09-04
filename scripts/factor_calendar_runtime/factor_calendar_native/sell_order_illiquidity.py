"""Factor Calendar 卖方冲击成本市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SellOrderIlliquidityFactor(Factor):
    """使用负收益相对成交额的二十日均值代理卖方价格冲击。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        negative_return = (-returns).where(returns < 0, 0)
        daily_impact = (negative_return / amount).where(amount > 0)
        result = daily_impact.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
