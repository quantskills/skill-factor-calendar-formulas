"""Factor Calendar 年度员工总数增长率市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EmployeeGrowthRateFactor(Factor):
    """以60日成交量扩张率代理企业人员和经营规模增长。"""

    def calculate(self, factors):
        volume = factors["volume"] + 0
        current = volume.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        previous = current.groupby(level="symbol", sort=False).shift(60)
        average = (current + previous) / 2
        result = ((current - previous) / average).where(average > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
