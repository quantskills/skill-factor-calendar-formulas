"""Factor Calendar 负收益成交额加权非流动性因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import delay, finish, safe_divide, series


class NegativeReturnIlliquidityFactor(Factor):
    """近一个月负收益日的绝对收益成交额比均值。"""

    def calculate(self, factors):
        close = series(factors, "close")
        amount = series(factors, "amount")
        previous_close = delay(close, 1)
        daily_return = safe_divide(close, previous_close, positive=True) - 1
        negative_illiquidity = safe_divide(
            daily_return.abs(), amount, positive=True
        ).where(daily_return < 0)
        result = negative_illiquidity.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        return finish(result)
