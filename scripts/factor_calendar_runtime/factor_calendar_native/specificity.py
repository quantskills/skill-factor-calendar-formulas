"""Factor Calendar 特异性收益波动因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SpecificityFactor(Factor):
    """用市场、规模和动量解释度估计特异性收益波动。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = np.log(
            (close / previous_close).where((close > 0) & (previous_close > 0))
        )
        returns_wide = returns.unstack("symbol")
        market_return = returns.groupby(level="date", sort=False).mean()

        size_rank = market_cap.groupby(level="date", sort=False).rank(pct=True)
        small_return = returns.where(size_rank <= 0.3).groupby(
            level="date", sort=False
        ).mean()
        big_return = returns.where(size_rank >= 0.7).groupby(
            level="date", sort=False
        ).mean()
        size_return = small_return - big_return

        previous_month_close = close.groupby(
            level="symbol", sort=False
        ).shift(20)
        momentum = (close / previous_month_close - 1).where(
            (close > 0) & (previous_month_close > 0)
        )
        momentum_rank = momentum.groupby(level="date", sort=False).rank(pct=True)
        winner_return = returns.where(momentum_rank >= 0.7).groupby(
            level="date", sort=False
        ).mean()
        loser_return = returns.where(momentum_rank <= 0.3).groupby(
            level="date", sort=False
        ).mean()
        momentum_return = winner_return - loser_return

        def rolling_correlation(factor_return):
            factor_return = factor_return.reindex(returns_wide.index)
            mean_stock = returns_wide.rolling(50, min_periods=25).mean()
            mean_factor = factor_return.rolling(50, min_periods=25).mean()
            covariance = returns_wide.mul(factor_return, axis=0).rolling(
                50, min_periods=25
            ).mean() - mean_stock.mul(mean_factor, axis=0)
            stock_variance = (returns_wide**2).rolling(
                50, min_periods=25
            ).mean() - mean_stock**2
            factor_variance = (factor_return**2).rolling(
                50, min_periods=25
            ).mean() - mean_factor**2
            denominator = np.sqrt(
                stock_variance.mul(factor_variance, axis=0)
            )
            return covariance.div(denominator).where(denominator > 0)

        market_r2 = rolling_correlation(market_return) ** 2
        size_r2 = rolling_correlation(size_return) ** 2
        momentum_r2 = rolling_correlation(momentum_return) ** 2
        result_wide = (1 - market_r2.clip(0, 1)) * (
            1 - size_r2.clip(0, 1)
        ) * (1 - momentum_r2.clip(0, 1))
        try:
            result = result_wide.stack(future_stack=True)
        except TypeError:
            result = result_wide.stack(dropna=False)
        result = result.reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
