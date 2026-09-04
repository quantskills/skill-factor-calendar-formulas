"""Factor Calendar 换手率波动率系数因子。"""

from factor_calendar_runtime import Factor


class TurnoverVolatilityCoefficientFactor(Factor):
    """最近 3 个月日换手率的标准差与均值之比。"""

    def calculate(self, factors):
        turnover = factors["turnover"]
        window = 63  # 3 个月约等于 63 个交易日

        mean_turnover = self.MA(turnover, window)
        std_turnover = self.STDDEV(turnover, window)

        result = (std_turnover / mean_turnover).where(mean_turnover > 0)
        return result
