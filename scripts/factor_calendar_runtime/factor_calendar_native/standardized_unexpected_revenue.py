"""Factor Calendar 标准化季度营收意外因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class StandardizedUnexpectedRevenueFactor(Factor):
    """以实际营收偏离预期的程度除以八季度历史波动。"""

    def calculate(self, factors):
        if "operating_revenue" in getattr(factors, "data_dict", factors):
            actual_revenue = factors["operating_revenue"] + 0
        else:
            actual_revenue = factors["amount"] + 0
        expected_revenue = None
        for name in (
            "expected_operating_revenue",
            "consensus_operating_revenue",
        ):
            if name in getattr(factors, "data_dict", factors):
                expected_revenue = factors[name] + 0
                break
        if expected_revenue is None:
            expected_revenue = actual_revenue.groupby(
                level="symbol", sort=False
            ).transform(
                lambda item: item.rolling(21, min_periods=5).mean().shift(1)
            )
        surprise = actual_revenue - expected_revenue
        long_std = surprise.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(504, min_periods=63).std(ddof=0)
        )
        short_std = surprise.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(63, min_periods=20).std(ddof=0)
        )
        surprise_std = long_std.fillna(short_std)
        standardized = (surprise / surprise_std).where(surprise_std > 0)
        relative_surprise = (surprise / expected_revenue.abs()).where(
            expected_revenue != 0
        )
        tie_breaker = actual_revenue.groupby(
            level="date", sort=False
        ).rank(pct=True) * 1e-12
        result = standardized.fillna(relative_surprise) + tie_breaker
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
