"""Factor Calendar 集合竞价成交量占比复合因子（日频基础行情代理）。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class VolumeRatioFactor(Factor):
    """以开盘缺口和收盘涨幅结合相对成交量代理竞价活跃度。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        mean_volume = volume.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(20, min_periods=20).mean())
        relative_volume = (volume / mean_volume).where(
            (volume >= 0) & (mean_volume > 0)
        )
        opening_gap = (open_price / previous_close - 1).abs().where(
            (open_price > 0) & (previous_close > 0)
        )
        closing_move = (close / open_price - 1).abs().where(
            (close > 0) & (open_price > 0)
        )
        opening_proxy = opening_gap * relative_volume
        closing_proxy = closing_move * relative_volume
        composite = (opening_proxy + closing_proxy) / 2
        delayed_composite = composite.groupby(
            level="symbol", sort=False
        ).shift(1)
        result = delayed_composite.groupby(
            level="symbol", sort=False
        ).transform(lambda values: values.rolling(5, min_periods=5).mean())
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
