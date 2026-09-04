"""Factor Calendar 情绪敏感度因子。"""

import numpy as np
from factor_calendar_runtime import Factor


class SentimentBetaFactor(Factor):
    """回归个股收益对市场量价情绪变化的暴露并取负绝对值。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = returns.groupby(
            level="date", sort=False
        ).transform("mean")
        market_turnover = turnover.groupby(
            level="date", sort=False
        ).transform("mean")
        market_amount = amount.groupby(
            level="date", sort=False
        ).transform("sum")
        turnover_change = market_turnover.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        amount_change = market_amount.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        sentiment_change = (
            market_return
            + turnover_change.clip(-1, 1)
            + amount_change.clip(-1, 1)
        )
        mean_return = returns.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        mean_sentiment = sentiment_change.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        mean_product = (returns * sentiment_change).groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        mean_sentiment_square = (sentiment_change**2).groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).mean()
        )
        covariance = mean_product - mean_return * mean_sentiment
        variance = mean_sentiment_square - mean_sentiment**2
        beta = (covariance / variance).where(variance > 0)
        result = -beta.abs()
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
