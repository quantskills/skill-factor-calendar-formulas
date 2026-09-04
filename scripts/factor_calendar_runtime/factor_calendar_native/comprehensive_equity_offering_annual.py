"""Factor Calendar 年度股权发行调整市值增长率因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ComprehensiveEquityOfferingAnnualFactor(Factor):
    """以年度市值增长扣除同期价格收益衡量净股权发行。"""

    def calculate(self, factors):
        market_cap = factors["market_cap"] + 0
        close = factors["close"] + 0
        annual_market_cap = market_cap.groupby(
            level="symbol", sort=False
        ).shift(252)
        annual_close = close.groupby(level="symbol", sort=False).shift(252)
        annual_result = np.log(
            (market_cap / annual_market_cap).where(
                (market_cap > 0) & (annual_market_cap > 0)
            )
        ) - np.log(
            (close / annual_close).where(
                (close > 0) & (annual_close > 0)
            )
        )
        short_market_cap = market_cap.groupby(
            level="symbol", sort=False
        ).shift(20)
        short_close = close.groupby(level="symbol", sort=False).shift(20)
        short_result = 252 / 20 * (
            np.log(
                (market_cap / short_market_cap).where(
                    (market_cap > 0) & (short_market_cap > 0)
                )
            )
            - np.log(
                (close / short_close).where(
                    (close > 0) & (short_close > 0)
                )
            )
        )
        tie_breaker = np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = annual_result.fillna(short_result) + tie_breaker
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
