"""Factor Calendar 集合竞价成交量占比因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class EmotionVolumeRatioFactor(Factor):
    """以价差强度和成交量活跃度代理集合竞价成交量占比。"""

    def calculate(self, factors):
        volume = factors["volume"] + 0
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        average_volume = volume.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        volume_intensity = (volume / average_volume).where(average_volume > 0)
        opening_ratio = (
            (open_price / previous_close - 1).abs() * volume_intensity
        ).clip(upper=1)
        closing_ratio = (
            (close / open_price - 1).abs() * volume_intensity
        ).clip(upper=1)
        opening_mean = opening_ratio.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(5, min_periods=3).mean())
        closing_mean = closing_ratio.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(5, min_periods=3).mean())
        result = 0.5 * opening_mean + 0.5 * closing_mean
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
