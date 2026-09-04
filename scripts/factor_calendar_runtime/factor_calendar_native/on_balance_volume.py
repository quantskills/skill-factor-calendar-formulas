"""Factor Calendar 成交量能量潮（OBV）因子。"""

from factor_calendar_runtime import Factor


class OnBalanceVolumeFactor(Factor):
    """按照收盘价涨跌方向累积成交量。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0

        previous_close = self.DELAY(close, 1)
        valid_volume = volume.where(volume >= 0)
        signed_volume = valid_volume.where(
            close > previous_close, 0.0
        ) - valid_volume.where(close < previous_close, 0.0)
        signed_volume = signed_volume.where(previous_close.notna(), 0.0)
        result = signed_volume.groupby(
            level="symbol", sort=False
        ).cumsum()
        result = result.where((close > 0) & (volume >= 0))
        result.name = "value"
        return result
