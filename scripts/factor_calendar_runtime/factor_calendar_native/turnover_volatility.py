"""Factor Calendar 换手率波动率因子。"""

from factor_calendar_runtime import Factor


class TurnoverVolatilityFactor(Factor):
    """最近三个月日换手率的样本标准差。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        window = 63

        valid_turnover = turnover.where(turnover >= 0)
        result = valid_turnover.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).std(ddof=1)
        )
        result.name = "value"
        return result
