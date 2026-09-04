"""Factor Calendar 分析师覆盖度残差市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class AnalystCoverageAnomalyFactor(Factor):
    """成交额关注度剔除市值、换手率和动量后的横截面残差。"""

    def calculate(self, factors):
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        close = factors["close"] + 0
        attention = amount.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        average_turnover = turnover.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        previous_close = close.groupby(level="symbol", sort=False).shift(60)
        momentum = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        frame = pd.DataFrame(
            {
                "y": np.log(attention.where(attention > 0)),
                "log_size": np.log(market_cap.where(market_cap > 0)),
                "log_turnover": np.log(
                    average_turnover.where(average_turnover > 0)
                ),
                "momentum": momentum,
            }
        )
        result = pd.Series(np.nan, index=close.index, dtype=float)
        for date, group in frame.groupby(level="date", sort=False):
            valid = group.replace([np.inf, -np.inf], np.nan).dropna()
            if len(valid) < 5:
                continue
            design = np.column_stack(
                [
                    np.ones(len(valid)),
                    valid["log_size"].to_numpy(dtype=float),
                    valid["log_turnover"].to_numpy(dtype=float),
                    valid["momentum"].to_numpy(dtype=float),
                ]
            )
            if np.linalg.matrix_rank(design) < design.shape[1]:
                continue
            coefficients = np.linalg.lstsq(
                design, valid["y"].to_numpy(dtype=float), rcond=None
            )[0]
            result.loc[valid.index] = (
                valid["y"].to_numpy(dtype=float) - design @ coefficients
            )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
