"""Factor Calendar 简易波动指标（EMV）因子。"""

from factor_calendar_runtime import Factor


class EaseOfMovementValueFactor(Factor):
    """按页面口径衡量价格振幅变化相对于成交量的移动效率。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        volume = factors["volume"] + 0

        valid_price = (high > 0) & (low > 0) & (high >= low)
        valid_high = high.where(valid_price)
        valid_low = low.where(valid_price)
        valid_volume = volume.where(volume > 0)

        price_range = valid_high - valid_low
        previous_range = self.DELAY(valid_high, 1) - self.DELAY(valid_low, 1)
        midpoint_measure = (price_range - previous_range) / 2
        box_ratio = (valid_volume / price_range).where(price_range > 0)

        result = (midpoint_measure / box_ratio).where(box_ratio > 0)
        result.name = "value"
        return result
