"""Factor Calendar 线性回归残差净利润市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class LinearPurifiedNetProfitFactor(Factor):
    """使用收益率剔除成交活跃度后的截面残差信号。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        stock_return = close.groupby(level="symbol", sort=False).pct_change()
        return_rank = stock_return.groupby(
            level="date", sort=False
        ).rank(pct=True)
        turnover_rank = turnover.groupby(
            level="date", sort=False
        ).rank(pct=True)
        result = return_rank - turnover_rank
        result = result.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=1).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        result.name = "value"
        return result
