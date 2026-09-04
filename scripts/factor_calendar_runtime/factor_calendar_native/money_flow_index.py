"""Factor Calendar 资金流量指标（MFI）因子。"""

from factor_calendar_runtime import Factor


class MoneyFlowIndexFactor(Factor):
    """基于典型价格与成交量的 14 日资金流量振荡指标。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        window = 14

        valid = (
            (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= low)
            & (volume >= 0)
        )
        typical_price = ((high + low + close) / 3).where(valid)
        raw_money_flow = typical_price * volume.where(volume >= 0)
        previous_typical_price = self.DELAY(typical_price, 1)
        positive_flow = raw_money_flow.where(
            typical_price > previous_typical_price, 0.0
        ).where(previous_typical_price.notna())
        negative_flow = raw_money_flow.where(
            typical_price <= previous_typical_price, 0.0
        ).where(previous_typical_price.notna())
        positive_sum = positive_flow.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        negative_sum = negative_flow.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).sum()
        )
        total_flow = positive_sum + negative_sum
        result = (100 * positive_sum / total_flow).where(total_flow > 0)
        result.name = "value"
        return result
