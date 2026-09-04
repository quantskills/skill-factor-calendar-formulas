"""Factor Calendar 月度异常换手率因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import finish, rolling_mean, safe_divide, series


class MonthlyAbnormalTurnoverFactor(Factor):
    """近一月日均换手率相对过去一年日均换手率。"""

    def calculate(self, factors):
        turnover = series(factors, "turnover").where(
            series(factors, "turnover") >= 0
        )
        recent_mean = rolling_mean(turnover, 20)
        annual_mean = rolling_mean(turnover, 250)
        return finish(safe_divide(recent_mean, annual_mean, positive=True))
