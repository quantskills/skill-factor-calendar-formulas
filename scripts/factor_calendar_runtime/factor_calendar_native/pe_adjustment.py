"""Factor Calendar 预期市盈率调整幅度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class PEAdjustmentFactor(Factor):
    """使用60日市值变化代理预期市盈率调整幅度。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        previous = market_cap.groupby(
            level="symbol", sort=False
        ).shift(60)
        result = ((market_cap - previous) / previous.abs()).where(
            previous > 0
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
