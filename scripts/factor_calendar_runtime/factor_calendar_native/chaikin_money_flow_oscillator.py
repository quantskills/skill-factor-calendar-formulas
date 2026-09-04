"""Factor Calendar 蔡金资金流量震荡指标因子。"""

from factor_calendar_runtime import Factor


class ChaikinMoneyFlowOscillatorFactor(Factor):
    """按页面口径计算累积资金流量的 10 日与 3 日 EMA 之差。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        long_window = 10
        short_window = 3

        denominator = high + low
        valid = (
            (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= close)
            & (close >= low)
            & (denominator > 0)
            & (volume >= 0)
        )
        money_flow_volume = (
            volume * (2 * close - high - low) / denominator
        ).where(valid)
        accumulation = money_flow_volume.groupby(
            level="symbol", sort=False
        ).transform(lambda series: series.cumsum())
        long_ema = accumulation.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=long_window,
                adjust=False,
                min_periods=long_window,
            ).mean()
        )
        short_ema = accumulation.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=short_window,
                adjust=False,
                min_periods=short_window,
            ).mean()
        )
        result = long_ema - short_ema
        result.name = "value"
        return result
