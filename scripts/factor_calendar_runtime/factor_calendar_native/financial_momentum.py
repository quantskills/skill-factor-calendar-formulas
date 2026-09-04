"""Factor Calendar 财务相似度加权收益动量因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class FinancialMomentumFactor(Factor):
    """以横截面财务余弦相似度加权同业月度收益。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(20)
        monthly_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_cap = factors["market_cap"] + 0
        turnover = factors["turnover"] + 0
        amount = factors["amount"] + 0
        daily_return = close / close.groupby(
            level="symbol", sort=False
        ).shift(1) - 1
        volatility = daily_return.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=10).std(ddof=0))
        average_amount = amount.groupby(
            level="symbol", sort=False
        ).transform(lambda item: item.rolling(20, min_periods=5).mean())
        def cross_section_zscore(values):
            mean = values.groupby(level="date", sort=False).transform("mean")
            std = values.groupby(level="date", sort=False).transform(
                lambda item: item.std(ddof=0)
            )
            return ((values - mean) / std).where(std > 0)

        similarity_score = (
            cross_section_zscore(np.log(market_cap.where(market_cap > 0)))
            + cross_section_zscore(turnover)
            + cross_section_zscore(
                np.log(average_amount.where(average_amount > 0))
            )
            - cross_section_zscore(volatility)
        ) / 4
        similarity_rank = similarity_score.groupby(
            level="date", sort=False
        ).rank(pct=True)
        similarity_bucket = np.floor(similarity_rank * 20).clip(0, 19)
        dates = monthly_return.index.get_level_values("date")
        peer_sum = monthly_return.groupby(
            [dates, similarity_bucket], sort=False
        ).transform("sum")
        peer_count = monthly_return.groupby(
            [dates, similarity_bucket], sort=False
        ).transform("count")
        peer_return = ((peer_sum - monthly_return) / (peer_count - 1)).where(
            peer_count > 1
        )
        market_return = monthly_return.groupby(
            level="date", sort=False
        ).transform("mean")
        result = peer_return.fillna(market_return) + 1e-4 * (
            similarity_rank - 0.5
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
