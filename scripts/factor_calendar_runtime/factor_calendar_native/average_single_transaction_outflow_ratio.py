"""Factor Calendar 日均负向成交额占比相对强度市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AverageSingleTransactionOutflowRatioFactor(Factor):
    """以负收益日成交强度估计单笔负向成交额并相对市场标准化。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        volume = factors["volume"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        average_trade_proxy = (amount / volume).where(volume > 0)
        negative_trade = average_trade_proxy * (-returns).clip(lower=0)
        negative_mean = negative_trade.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        total_mean = average_trade_proxy.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        stock_ratio = (negative_mean / total_mean).where(total_mean > 0)
        market_ratio = stock_ratio.groupby(
            level="date", sort=False
        ).transform("mean")
        result = (stock_ratio / market_ratio).where(market_ratio > 0)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
