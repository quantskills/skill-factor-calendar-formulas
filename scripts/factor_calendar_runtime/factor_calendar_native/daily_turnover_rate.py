"""Factor Calendar 日均换手率因子。"""

from factor_calendar_runtime import Factor


class DailyTurnoverRateFactor(Factor):
    """返回平台提供的当日换手率。"""

    def calculate(self, factors):
        turnover = factors["turnover"]

        return turnover
