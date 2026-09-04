"""Factor Calendar 负收益偏度系数（NCSKEW）因子。"""

import numpy as np

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import delay, finish, safe_divide, series


class NegativeSkewnessCoefficientFactor(Factor):
    """最近 60 日对数收益率的有限样本负偏度。"""

    def calculate(self, factors):
        close = series(factors, "close")
        previous_close = delay(close, 1)
        daily_return = safe_divide(close, previous_close, positive=True)
        daily_return = np.log(daily_return.where(daily_return > 0))
        window = 60

        def ncskew(item):
            def calculate_window(values):
                centered = values - values.mean()
                second_sum = (centered**2).sum()
                if second_sum <= 0:
                    return float("nan")
                numerator = -((window * (window - 1)) ** 1.5) * (
                    centered**3
                ).sum()
                denominator = (window - 1) * (window - 2) * (
                    second_sum**1.5
                )
                return numerator / denominator

            return item.rolling(window, min_periods=window).apply(
                calculate_window, raw=True
            )

        result = daily_return.groupby(level="symbol", sort=False).transform(
            ncskew
        )
        return finish(result)
