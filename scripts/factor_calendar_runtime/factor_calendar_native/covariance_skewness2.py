"""Factor Calendar 系统偏度风险溢价因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class CovarianceSkewness2Factor(Factor):
    """计算个股市场模型残差与市场收益平方的滚动协偏度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        stock_wide = stock_return.unstack("symbol")
        market_return = stock_return.groupby(level="date", sort=False).mean()

        mean_stock = stock_wide.rolling(50, min_periods=25).mean()
        mean_market = market_return.rolling(50, min_periods=25).mean()
        covariance = stock_wide.mul(market_return, axis=0).rolling(
            50, min_periods=25
        ).mean() - mean_stock.mul(mean_market, axis=0)
        market_variance = (market_return**2).rolling(
            50, min_periods=25
        ).mean() - mean_market**2
        beta = covariance.div(market_variance, axis=0).where(
            market_variance > 0, axis=0
        )
        centered_market = market_return - mean_market
        residual = stock_wide - mean_stock - beta.mul(centered_market, axis=0)
        numerator = residual.mul(centered_market**2, axis=0).rolling(
            50, min_periods=25
        ).mean()
        residual_variance = (residual**2).rolling(
            50, min_periods=25
        ).mean()
        market_second_moment = (centered_market**2).rolling(
            50, min_periods=25
        ).mean()
        denominator = np.sqrt(
            residual_variance.mul(market_second_moment, axis=0)
        )
        result_wide = numerator.div(denominator).where(denominator > 0)
        try:
            result = result_wide.stack(future_stack=True)
        except TypeError:
            result = result_wide.stack(dropna=False)
        result = result.reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
