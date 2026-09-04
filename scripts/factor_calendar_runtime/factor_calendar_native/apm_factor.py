"""Factor Calendar 日内信息不对称强度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class APMFactor(Factor):
    """隔夜与日内市场调整残差差异的动量中性统计量。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        overnight = (open_price / previous_close - 1).where(
            (open_price > 0) & (previous_close > 0)
        )
        intraday = (close / open_price - 1).where(
            (close > 0) & (open_price > 0)
        )
        market_overnight = overnight.groupby(
            level="date", sort=False
        ).transform("mean")
        market_intraday = intraday.groupby(
            level="date", sort=False
        ).transform("mean")

        def residual(y_values, x_values):
            mean_y = y_values.groupby(
                level="symbol", sort=False
            ).transform(
                lambda values: values.rolling(20, min_periods=5).mean()
            )
            mean_x = x_values.groupby(
                level="symbol", sort=False
            ).transform(
                lambda values: values.rolling(20, min_periods=5).mean()
            )
            covariance = (y_values * x_values).groupby(
                level="symbol", sort=False
            ).transform(
                lambda values: values.rolling(20, min_periods=5).mean()
            ) - mean_y * mean_x
            variance = (x_values**2).groupby(
                level="symbol", sort=False
            ).transform(
                lambda values: values.rolling(20, min_periods=5).mean()
            ) - mean_x**2
            beta = (covariance / variance).where(variance > 0)
            alpha = mean_y - beta * mean_x
            return y_values - alpha - beta * x_values

        difference = residual(
            overnight, market_overnight
        ) - residual(intraday, market_intraday)
        difference_mean = difference.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).mean()
        )
        difference_std = difference.groupby(
            level="symbol", sort=False
        ).transform(
            lambda values: values.rolling(10, min_periods=3).std(ddof=1)
        )
        statistic = (difference_mean * np.sqrt(10) / difference_std).where(
            difference_std > 0
        )
        delayed_close = close.groupby(level="symbol", sort=False).shift(20)
        momentum = (close / delayed_close - 1).where(
            (close > 0) & (delayed_close > 0)
        )
        frame = pd.concat({"stat": statistic, "momentum": momentum}, axis=1)

        def neutralize(group):
            output = pd.Series(np.nan, index=group.index, dtype=float)
            valid = group.dropna()
            if len(valid) < 3 or valid["momentum"].var(ddof=0) <= 0:
                output.loc[valid.index] = valid["stat"]
                return output
            design = np.column_stack(
                [
                    np.ones(len(valid)),
                    valid["momentum"].to_numpy(dtype=float),
                ]
            )
            coefficients = np.linalg.lstsq(
                design, valid["stat"].to_numpy(dtype=float), rcond=None
            )[0]
            output.loc[valid.index] = valid["stat"] - design @ coefficients
            return output

        result = frame.groupby(
            level="date", sort=False, group_keys=False
        ).apply(neutralize).reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
