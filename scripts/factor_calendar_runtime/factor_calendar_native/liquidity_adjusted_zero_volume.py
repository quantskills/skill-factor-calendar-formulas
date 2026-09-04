"""Factor Calendar 流动性调整成交量零值天数比率因子。"""

from factor_calendar_runtime import Factor


class LiquidityAdjustedZeroVolumeFactor(Factor):
    """结合零成交量天数和平均换手率倒数的三个月流动性指标。"""

    def calculate(self, factors):
        volume = factors["volume"] + 0
        turnover = factors["turnover"] + 0
        lookback_months = 3
        trading_days = 63
        scale = 1

        zero_volume_day = (volume == 0).astype(float).where(volume >= 0)
        zero_volume_count = zero_volume_day.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=trading_days, min_periods=trading_days
            ).sum()
        )
        average_turnover = turnover.where(turnover >= 0).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=trading_days, min_periods=trading_days
            ).mean()
        )
        result = (
            zero_volume_count / scale
            + 1 / average_turnover
            - 2 * lookback_months / trading_days
        ).where(average_turnover > 0)
        result.name = "value"
        return result
