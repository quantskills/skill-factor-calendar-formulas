"""Factor Calendar 二阶动量加速度因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AccelerationMomentumFactor(Factor):
    """对最近 20 日收盘价做二次拟合并取二次项系数。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 20
        time_index = np.arange(1, window + 1, dtype=float)

        valid_close = close.where(close > 0)
        result = valid_close.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).apply(
                lambda values: np.polyfit(time_index, values, 2)[0],
                raw=True,
            )
        )
        result.name = "value"
        return result
