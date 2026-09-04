"""Factor Calendar 蔡金波动率指标（CVI）因子。"""

from factor_calendar_runtime import Factor


class ChaikinVolatilityIndexFactor(Factor):
    """20 日高低价差 EMA 相对其 20 日前数值的变化率。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        window = 20

        price_range = (high - low).where(
            (high > 0) & (low > 0) & (high >= low)
        )
        range_ema = price_range.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=window,
                adjust=False,
                min_periods=window,
            ).mean()
        )
        lagged_ema = self.DELAY(range_ema, window)
        result = ((range_ema - lagged_ema) / range_ema * 100).where(
            (range_ema > 0) & lagged_ema.notna()
        )
        result.name = "value"
        return result
