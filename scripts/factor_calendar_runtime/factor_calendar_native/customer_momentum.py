"""Factor Calendar 客户销售占比加权月度动量因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class CustomerMomentumFactor(Factor):
    """以成交额暴露代理客户销售占比，计算客户组合月度动量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0

        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        monthly_momentum = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        sales_exposure = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        ).where(amount >= 0)

        weighted_momentum = sales_exposure * monthly_momentum
        total_exposure = sales_exposure.groupby(
            level="date", sort=False
        ).transform("sum")
        total_weighted_momentum = weighted_momentum.groupby(
            level="date", sort=False
        ).transform("sum")

        customer_exposure = total_exposure - sales_exposure
        customer_momentum = (
            total_weighted_momentum - weighted_momentum
        ) / customer_exposure
        result = customer_momentum.where(customer_exposure > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
