"""Factor Calendar Frazzini-Pedersen 调整贝塔因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import (
    delay,
    finish,
    rolling_std,
    safe_divide,
    stock_and_market_returns,
)


class FrazziniPedersenBetaFactor(Factor):
    """五年三日重叠收益相关系数乘一年波动率比。"""

    def calculate(self, factors):
        stock_return, market_return = stock_and_market_returns(factors["close"] + 0)
        stock_overlap = (
            stock_return + delay(stock_return, 1) + delay(stock_return, 2)
        ) / 3
        market_overlap = (
            market_return + delay(market_return, 1) + delay(market_return, 2)
        ) / 3
        correlation = stock_overlap.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(750, min_periods=750).corr(
                market_overlap.loc[item.index]
            )
        )
        stock_volatility = rolling_std(stock_return, 252, ddof=1)
        market_volatility = rolling_std(market_return, 252, ddof=1)
        volatility_ratio = safe_divide(
            stock_volatility, market_volatility, positive=True
        )
        return finish(correlation * volatility_ratio)
