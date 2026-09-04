"""Factor Calendar 基于排序的动量因子。"""

from factor_calendar_runtime import Factor


class RankMomentumFactor(Factor):
    """过去六个月、跳过最近一个月的日收益率标准化排名均值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        lookback = 126
        skip = 21

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        ranks = daily_return.groupby(level="date", sort=False).rank(
            method="average"
        )
        counts = daily_return.groupby(level="date", sort=False).transform(
            "count"
        )
        denominator = (((counts + 1) * (counts - 1)) / 12) ** 0.5
        standardized_rank = (
            ranks - (counts + 1) / 2
        ) / denominator
        standardized_rank = standardized_rank.where(counts > 1)
        result = self.DELAY(self.MA(standardized_rank, lookback), skip)
        result.name = "value"
        return result
