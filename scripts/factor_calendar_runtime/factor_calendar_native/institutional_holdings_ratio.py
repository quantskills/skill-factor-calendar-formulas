"""Factor Calendar 机构投资者持股比例市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class InstitutionalHoldingsRatioFactor(Factor):
    """优先使用机构持股字段，缺失时以规模和收益稳定性代理。"""

    def calculate(self, factors):
        for name in (
            "institutional_holdings_ratio",
            "institution_holding_ratio",
        ):
            if name in getattr(factors, "data_dict", factors):
                result = factors[name] + 0
                if "market_cap" in getattr(factors, "data_dict", factors):
                    market_cap = factors["market_cap"] + 0
                    result = result + np.log(
                        market_cap.where(market_cap > 0)
                    ) * 1e-12
                result = result.replace([np.inf, -np.inf], np.nan)
                result.name = "value"
                return result
        close = factors["close"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        volatility = returns.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(60, min_periods=20).std(ddof=0)
        )
        size_rank = market_cap.groupby(
            level="date", sort=False
        ).rank(pct=True)
        stability_rank = (-volatility).groupby(
            level="date", sort=False
        ).rank(pct=True)
        tie_breaker = np.log(market_cap.where(market_cap > 0)) * 1e-12
        result = 0.6 * size_rank + 0.4 * stability_rank + tie_breaker
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
