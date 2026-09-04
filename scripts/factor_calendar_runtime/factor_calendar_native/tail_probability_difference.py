"""Factor Calendar 尾部非对称概率差因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import (
    finish,
    rolling_mean,
    rolling_residuals,
    rolling_std,
    stock_and_market_returns,
)


class TailProbabilityDifferenceFactor(Factor):
    """一年 CAPM 残差中正负 2 倍标准差尾部概率之差。"""

    def calculate(self, factors):
        stock_return, market_return = stock_and_market_returns(factors["close"] + 0)
        residual = rolling_residuals(stock_return, market_return, 60)
        mean = rolling_mean(residual, 252)
        standard_deviation = rolling_std(residual, 252)
        standardized = (residual - mean) / standard_deviation.where(
            standard_deviation > 0
        )
        valid = standardized.notna()
        right_tail = rolling_mean(
            (standardized >= 2).where(valid).astype(float), 252
        )
        left_tail = rolling_mean(
            (standardized <= -2).where(valid).astype(float), 252
        )
        return finish(right_tail - left_tail)
