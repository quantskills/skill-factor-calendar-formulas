"""Factor Calendar 资产市值比因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AssetToMarketCapRatioFactor(Factor):
    """最近报告期总资产与当日总市值之比。"""

    def calculate(self, factors):
        total_assets = factors["total_assets"] + 0
        market_cap = factors["market_cap"] + 0

        result = (total_assets / market_cap).where(
            (total_assets >= 0) & (market_cap > 0)
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
