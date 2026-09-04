"""Factor Calendar 企业上市时长市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class EnterpriseAgeFactor(Factor):
    """以当前数据样本内累计交易月数衡量上市时长。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        observations = close.notna().astype(float).groupby(level="symbol", sort=False).cumsum()
        result = observations / 21.0
        result = result + close.groupby(level="date", sort=False).rank(pct=True) * 1e-6
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
