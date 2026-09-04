"""Factor Calendar 成交量价背离度因子。"""

from factor_calendar_runtime import Factor


class VolumePriceDivergenceFactor(Factor):
    """日度 VWAP 与成交量的 20 日滚动 Pearson 相关系数。"""

    def calculate(self, factors):
        amount = factors["amount"]
        volume = factors["volume"]

        # Factor Calendar 没有直接提供日度 VWAP 字段，使用成交额/成交量构造。
        # 无成交量时保留为 NaN，避免停牌日产生无效价格。
        daily_vwap = (amount / volume).where(volume > 0)

        return self.CORRELATION(daily_vwap, volume, 20)
