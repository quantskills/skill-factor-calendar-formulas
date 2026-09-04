"""Factor Calendar 分析师预期 EPS 调整幅度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ExpectedEPSAdjustmentFactor(Factor):
    """使用三个月价格变化代理分析师预期 EPS 调整幅度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(60)
        result = ((close - previous_close) / previous_close.abs()).where(
            previous_close != 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
