"""Factor Calendar 蔡金资金流向指标（CMF）因子。"""

from factor_calendar_runtime import Factor


class ChaikinMoneyFlowFactor(Factor):
    """20 日成交量加权收盘位置强度。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        window = 20

        valid = (
            (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= close)
            & (close >= low)
            & (volume >= 0)
        )
        price_range = (high - low).where(valid)
        valid_volume = volume.where(valid)
        multiplier = ((2 * close - high - low) / price_range).where(
            price_range > 0, 0.0
        )
        multiplier = multiplier.where(valid)
        money_flow_volume = multiplier * valid_volume

        flow_sum = money_flow_volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        volume_sum = valid_volume.groupby(level="symbol", sort=False).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        result = (flow_sum / volume_sum * 100).where(volume_sum > 0)
        result.name = "value"
        return result
