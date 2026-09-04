"""Factor Calendar 成交量相对强度指标（VRSI）因子。"""

from factor_calendar_runtime import Factor


class VolumeRelativeStrengthFactor(Factor):
    """基于 Wilder 平滑向上、向下成交量的 20 日 VRSI。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        window = 20

        valid_close = close.where(close > 0)
        valid_volume = volume.where(volume >= 0)
        previous_close = self.DELAY(valid_close, 1)
        comparable = previous_close.notna() & valid_volume.notna()
        upward_volume = valid_volume.where(
            valid_close > previous_close, 0.0
        )
        upward_volume = upward_volume.where(
            valid_close != previous_close, valid_volume / 2
        ).where(comparable)
        downward_volume = valid_volume.where(
            valid_close < previous_close, 0.0
        )
        downward_volume = downward_volume.where(
            valid_close != previous_close, valid_volume / 2
        ).where(comparable)

        average_upward = upward_volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                alpha=1 / window,
                adjust=False,
                min_periods=window,
            ).mean()
        )
        average_downward = downward_volume.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                alpha=1 / window,
                adjust=False,
                min_periods=window,
            ).mean()
        )
        total_volume = average_upward + average_downward
        result = (average_upward / total_volume * 100).where(total_volume > 0)
        result.name = "value"
        return result
