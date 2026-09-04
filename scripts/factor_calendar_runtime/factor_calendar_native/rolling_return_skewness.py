"""Factor Calendar 滚动收益率偏度因子。"""

from factor_calendar_runtime import Factor


class RollingReturnSkewnessFactor(Factor):
    """最近六个月日收益率分布的总体矩偏度。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        window = 126

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )

        rolling_mean = daily_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        second_raw_moment = (daily_return ** 2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        third_raw_moment = (daily_return ** 3).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        second_moment = second_raw_moment - rolling_mean ** 2
        third_moment = (
            third_raw_moment
            - 3 * rolling_mean * second_raw_moment
            + 2 * rolling_mean ** 3
        )
        result = (third_moment / (second_moment ** 1.5)).where(
            second_moment > 0
        )
        result.name = "value"
        return result
