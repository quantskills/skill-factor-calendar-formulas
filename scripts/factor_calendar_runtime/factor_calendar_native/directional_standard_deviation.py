"""Factor Calendar 方向性动量离散指标（DDI）因子。"""

import numpy as np

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import delay, finish, rolling_sum, safe_divide, series


class DirectionalStandardDeviationFactor(Factor):
    """20 日上行动量与下行动量占比之差。"""

    def calculate(self, factors):
        high = series(factors, "high")
        low = series(factors, "low")
        previous_high = delay(high, 1)
        previous_low = delay(low, 1)
        movement = np.maximum(
            (high - previous_high).abs(), (low - previous_low).abs()
        )
        valid = movement.notna()
        rising = high + low > previous_high + previous_low
        upward = movement.where(rising, 0).where(valid)
        downward = movement.where(~rising, 0).where(valid)
        upward_sum = rolling_sum(upward, 20)
        downward_sum = rolling_sum(downward, 20)
        total = upward_sum + downward_sum
        result = 100 * safe_divide(
            upward_sum - downward_sum, total, positive=True
        )
        return finish(result.fillna(0).where(total.notna()))
