"""Factor Calendar 一致性下跌成交量比率因子。"""

from factor_calendar_runtime import Factor


class ConsistentDownVolumeRatioFactor(Factor):
    """过去 10 日一致性下跌成交量相对当日成交量的负向比率。"""

    def calculate(self, factors):
        open_price = factors["open"] + 0
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        alpha = 0.3
        window = 10

        body = (close - open_price).abs()
        price_range = (high - low).abs()
        consistent_fall = (
            (close < open_price)
            & (price_range > 0)
            & (body <= alpha * price_range)
        )
        consistent_fall_volume = volume.where(consistent_fall, 0.0)
        lagged_volume = self.DELAY(consistent_fall_volume, 1)
        volume_sum = self.SUM(lagged_volume, window)
        result = -(volume_sum / (window * volume))
        result = result.where(volume > 0).replace(
            [float("inf"), float("-inf")], 0.0
        )
        result.name = "value"
        return result
