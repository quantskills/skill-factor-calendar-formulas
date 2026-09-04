"""Factor Calendar 净员工流失率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EmployeeTurnoverRateFactor(Factor):
    """使用成交量净变化的反向值代理净员工流失情绪。"""

    def calculate(self, factors):
        volume = factors["volume"] + 0
        previous_volume = volume.groupby(
            level="symbol", sort=False
        ).shift(20)
        result = -((volume / previous_volume) - 1).where(
            (volume >= 0) & (previous_volume > 0)
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
