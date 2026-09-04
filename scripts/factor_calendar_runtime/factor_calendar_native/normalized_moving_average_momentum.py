"""Factor Calendar 多周期标准化移动平均动量因子。"""

from factor_calendar_runtime import Factor


class NormalizedMovingAverageMomentumFactor(Factor):
    """多个周期移动平均价格与当前收盘价之比的等权均值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        windows = (3, 5, 10, 20, 50, 100, 200)

        normalized_sum = close * 0
        for window in windows:
            normalized_sum = normalized_sum + self.MA(close, window) / close

        result = (normalized_sum / len(windows)).where(close > 0)
        result.name = "value"
        return result
