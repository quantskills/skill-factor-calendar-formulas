"""Factor Calendar 价格成交量趋势（PVT）因子。"""

from factor_calendar_runtime import Factor


class PriceVolumeTrendFactor(Factor):
    """按照日收益率加权并累积成交量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0

        previous_close = self.DELAY(close, 1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        weighted_volume = (daily_return * volume).where(volume >= 0)
        weighted_volume = weighted_volume.where(
            daily_return.notna(), 0.0
        )
        result = weighted_volume.groupby(
            level="symbol", sort=False
        ).cumsum()
        result = result.where((close > 0) & (volume >= 0))
        result.name = "value"
        return result
