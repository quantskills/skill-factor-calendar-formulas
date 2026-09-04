"""Factor Calendar 十大股东持股分散度标准差市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class Top10ShareholderDispersionFactor(Factor):
    """使用月度换手率波动代理主要股东持股分散程度。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        result = turnover.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=10).std()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
