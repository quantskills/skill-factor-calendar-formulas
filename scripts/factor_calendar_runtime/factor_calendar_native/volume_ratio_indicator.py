"""Factor Calendar 成交量相对强度（VR）因子。"""

from factor_calendar_runtime import Factor


class VolumeRatioIndicatorFactor(Factor):
    """上涨日成交量合计与下跌日成交量合计之比。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        window = 20

        previous_close = self.DELAY(close, 1)
        valid_volume = volume.where(volume >= 0)
        up_volume = valid_volume.where(close > previous_close, 0.0)
        down_volume = valid_volume.where(close < previous_close, 0.0)

        up_volume_sum = self.SUM(up_volume, window)
        down_volume_sum = self.SUM(down_volume, window)
        result = (up_volume_sum / down_volume_sum).where(
            down_volume_sum > 0
        )
        result.name = "value"
        return result
