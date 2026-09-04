"""Factor Calendar Fama-French 三因子代理残差动量。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class ResidualMomentumFF3Factor(Factor):
    """用市场、规模和价值风格代理回归残差构造中期动量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0

        previous_close = close.groupby(
            level="symbol", sort=False
        ).shift(1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )

        market_return = stock_return.groupby(
            level="date", sort=False
        ).transform("mean")

        size_rank = market_cap.groupby(
            level="date", sort=False
        ).rank(pct=True)
        small_return = stock_return.where(size_rank <= 0.3).groupby(
            level="date", sort=False
        ).transform("mean")
        big_return = stock_return.where(size_rank >= 0.7).groupby(
            level="date", sort=False
        ).transform("mean")
        size_return = small_return - big_return

        old_close = close.groupby(
            level="symbol", sort=False
        ).shift(252)
        long_term_return = (close / old_close - 1).where(
            (close > 0) & (old_close > 0)
        )
        value_rank = long_term_return.groupby(
            level="date", sort=False
        ).rank(pct=True)
        value_return = stock_return.where(value_rank <= 0.3).groupby(
            level="date", sort=False
        ).transform("mean")
        growth_return = stock_return.where(value_rank >= 0.7).groupby(
            level="date", sort=False
        ).transform("mean")
        value_style_return = value_return - growth_return

        regression_data = pd.concat(
            {
                "stock": stock_return,
                "market": market_return,
                "size": size_return,
                "value": value_style_return,
            },
            axis=1,
        )
        residual_parts = []
        for _, symbol_data in regression_data.groupby(
            level="symbol", sort=False
        ):
            values = symbol_data.to_numpy(dtype=float)
            residual_values = np.full(len(symbol_data), np.nan)
            for position in range(125, len(symbol_data)):
                start = max(0, position - 251)
                sample = values[start:position + 1]
                valid = np.isfinite(sample).all(axis=1)
                if valid.sum() < 126:
                    continue
                target = sample[valid, 0]
                design = np.column_stack(
                    [np.ones(valid.sum()), sample[valid, 1:]]
                )
                if np.linalg.matrix_rank(design) < design.shape[1]:
                    continue
                coefficients = np.linalg.lstsq(
                    design, target, rcond=None
                )[0]
                current = values[position]
                if np.isfinite(current).all():
                    residual_values[position] = current[0] - np.dot(
                        np.r_[1.0, current[1:]], coefficients
                    )
            residual_parts.append(
                pd.Series(residual_values, index=symbol_data.index)
            )

        residual = pd.concat(residual_parts).reindex(close.index)
        lagged_residual = residual.groupby(
            level="symbol", sort=False
        ).shift(21)
        residual_sum = lagged_residual.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(231, min_periods=126).sum()
        )
        residual_square_sum = (lagged_residual**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(231, min_periods=126).sum()
        )
        observation_count = lagged_residual.notna().astype(float).groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(231, min_periods=126).sum()
        )
        centered_square_sum = residual_square_sum - (
            residual_sum**2 / observation_count
        )
        denominator = np.sqrt(
            centered_square_sum.where(centered_square_sum > 0)
        )
        result = (residual_sum / denominator).where(denominator > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
