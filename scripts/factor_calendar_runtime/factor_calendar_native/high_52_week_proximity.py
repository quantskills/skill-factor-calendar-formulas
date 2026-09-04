"""Factor Calendar 52 周最高价逼近度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class High52WeekProximityFactor(Factor):
    """当前收盘价与过去 52 周最高收盘价之比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 252
        minimum_observations = 20

        valid_close = close.where(close > 0)
        sorted_close = valid_close.sort_index(level=["symbol", "date"])
        close_values = sorted_close.to_numpy(dtype=float, copy=False)
        rolling_high_values = np.full(len(sorted_close), np.nan)
        for positions in sorted_close.groupby(
            level="symbol", sort=False
        ).indices.values():
            rolling_high_values[positions] = pd.Series(
                close_values[positions]
            ).rolling(
                window=window,
                min_periods=minimum_observations,
            ).max().to_numpy()

        result = sorted_close.copy()
        result.iloc[:] = np.divide(
            close_values,
            rolling_high_values,
            out=np.full(len(sorted_close), np.nan),
            where=rolling_high_values > 0,
        )
        result = result.reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
