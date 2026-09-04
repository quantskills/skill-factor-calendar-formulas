"""Factor Calendar 长期反转因子。"""

import numpy as np

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import delay, finish, safe_divide, series


class LongTermReversalFactor(Factor):
    """过去第 59 至第 12 个月的累计收益率。"""

    def calculate(self, factors):
        close = series(factors, "close")
        previous_close = delay(close, 1)
        daily_return = safe_divide(close, previous_close, positive=True) - 1
        log_growth = np.log1p(daily_return.where(daily_return > -1))
        delayed_growth = delay(log_growth, 252)
        result = delayed_growth.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(1008, min_periods=1008).sum()
        )
        return finish(np.expm1(result))
