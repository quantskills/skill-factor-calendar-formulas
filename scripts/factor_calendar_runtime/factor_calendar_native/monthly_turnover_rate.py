"""Factor Calendar 月均换手率因子。"""

from factor_calendar_runtime import Factor


class MonthlyTurnoverRateFactor(Factor):
    """最近一个月日换手率的滚动平均值。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        window = 21  # 约 1 个自然月

        valid_turnover = turnover.where(turnover >= 0)
        result = (
            valid_turnover.groupby(level="symbol", sort=False)
            .rolling(window=window, min_periods=window)
            .mean()
            .reset_index(level=0, drop=True)
            .reindex(turnover.index)
        )
        result.name = "value"
        return result
