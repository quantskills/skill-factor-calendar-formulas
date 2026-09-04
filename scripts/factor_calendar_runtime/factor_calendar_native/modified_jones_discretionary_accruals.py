"""Factor Calendar 修正琼斯模型操纵性应计盈余市场代理因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class ModifiedJonesDiscretionaryAccrualsFactor(Factor):
    """以价量背离与特质波动代理操纵性应计盈余风险。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        previous_volume = volume.groupby(level="symbol", sort=False).shift(1)
        returns = close / previous_close - 1
        volume_change = np.log((volume / previous_volume).where((volume > 0) & (previous_volume > 0)))
        correlation = returns.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).corr(volume_change.loc[item.index]))
        volatility = returns.groupby(level="symbol", sort=False).transform(lambda item: item.rolling(60, min_periods=20).std(ddof=0))
        divergence_rank = (-correlation).groupby(level="date", sort=False).rank(pct=True)
        volatility_rank = volatility.groupby(level="date", sort=False).rank(pct=True)
        result = 0.6 * divergence_rank + 0.4 * volatility_rank
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
