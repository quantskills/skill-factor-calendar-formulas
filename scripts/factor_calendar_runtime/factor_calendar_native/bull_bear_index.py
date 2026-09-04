import pandas as pd

from factor_calendar_runtime import Factor


class BullBearIndexFactor(Factor):
    """Factor Calendar 多空意愿指标（BBI）因子：

    定义：3、6、12、20 日收盘价简单移动平均（SMA）的算术平均。
    公式：BBI = (SMA(C,3) + SMA(C,6) + SMA(C,12) + SMA(C,20)) / 4
    """

    def calculate(self, factors):
        # 取收盘价，+0 确保为数值类型
        close = factors["close"] + 0

        # 仅对大于 0 的价格计算均线，其他位置视为缺失
        valid_close = close.where(close > 0)

        # 直接利用引擎内置的 MA 算子按窗口计算简单移动平均
        ma3 = valid_close.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(3, min_periods=1).mean()
        )
        ma6 = valid_close.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(6, min_periods=1).mean()
        )
        ma12 = valid_close.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(12, min_periods=1).mean()
        )
        ma20 = valid_close.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=1).mean()
        )

        # BBI 为四条均线的算术平均
        result = (ma3 + ma6 + ma12 + ma20) / 4.0

        # 处理可能的无穷值（理论上不会出现，这里做稳健防护）
        result = result.replace([float("inf"), float("-inf")], 0)

        # 引擎会处理 name，可不强制设置；如需要可保留
        result.name = "value"
        return result
