"""Factor Calendar 资金流量累积指标（A/D）因子。"""

from factor_calendar_runtime import Factor


class AccumulationDistributionLineFactor(Factor):
    """按收盘价在日内区间的位置加权并累积成交量。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0

        valid = (
            (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= low)
            & (close <= high)
            & (close >= low)
            & (volume >= 0)
        )
        price_range = high - low
        money_flow_multiplier = (
            (2 * close - high - low) / price_range
        ).where(valid & (price_range > 0), 0.0)
        money_flow_volume = (money_flow_multiplier * volume).where(valid, 0.0)
        result = money_flow_volume.groupby(
            level="symbol", sort=False
        ).cumsum()
        result = result.where(valid)
        result.name = "value"
        return result
