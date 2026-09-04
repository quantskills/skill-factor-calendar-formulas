"""Factor Calendar 商品通道指数（CCI）因子。"""

from factor_calendar_runtime import Factor


class CommodityChannelIndexFactor(Factor):
    """典型价格相对其 20 日均值的标准化偏离。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        valid = (high > 0) & (low > 0) & (close > 0) & (high >= low)
        typical_price = ((high + low + close) / 3).where(valid)
        moving_average = typical_price.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        mean_absolute_deviation = typical_price.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).apply(lambda values: abs(values - values.mean()).mean(), raw=True)
        )
        denominator = 0.015 * mean_absolute_deviation
        result = ((typical_price - moving_average) / denominator).where(
            denominator > 0
        )
        result.name = "value"
        return result
