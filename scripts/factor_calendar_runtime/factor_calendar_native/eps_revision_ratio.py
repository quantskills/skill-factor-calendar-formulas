"""Factor Calendar EPS 修正比率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EPSRevisionRatioFactor(Factor):
    """使用上涨日与下跌日数量差占比代理盈利预测修正方向。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        upward = (returns > 0).astype(float).where(returns.notna())
        downward = (returns < 0).astype(float).where(returns.notna())
        upward_count = upward.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=20).sum())
        downward_count = downward.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(60, min_periods=20).sum())
        total_count = upward_count + downward_count
        result = ((upward_count - downward_count) / total_count).where(
            total_count > 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
