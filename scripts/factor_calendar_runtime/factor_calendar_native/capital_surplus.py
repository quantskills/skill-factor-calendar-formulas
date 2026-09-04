"""Factor Calendar 已实现资本盈余比率因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class CapitalSurplusFactor(Factor):
    """按换手率加权历史成本计算已实现资本盈余比率。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        turnover = factors["turnover"] + 0
        frame = pd.concat(
            {"close": close, "turnover": turnover.clip(0, 1)}, axis=1
        )

        def calculate_group(group):
            prices = group["close"].to_numpy(dtype=float)
            rates = group["turnover"].to_numpy(dtype=float)
            output = np.full(len(group), np.nan)
            for position in range(20, len(group)):
                start = max(0, position - 260)
                historical_prices = prices[start:position]
                historical_rates = rates[start:position]
                valid = np.isfinite(historical_prices) & np.isfinite(
                    historical_rates
                )
                if valid.sum() < 20:
                    continue
                historical_prices = historical_prices[valid]
                historical_rates = historical_rates[valid]
                weights = np.empty(len(historical_rates), dtype=float)
                survival = 1.0
                for index in range(len(historical_rates) - 1, -1, -1):
                    weights[index] = historical_rates[index] * survival
                    survival *= 1 - historical_rates[index]
                total_weight = weights.sum()
                previous_price = prices[position - 1]
                if total_weight <= 0 or previous_price <= 0:
                    continue
                reference_price = np.dot(
                    weights, historical_prices
                ) / total_weight
                output[position] = (
                    previous_price - reference_price
                ) / previous_price
            return pd.Series(output, index=group.index)

        result = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(calculate_group).reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
