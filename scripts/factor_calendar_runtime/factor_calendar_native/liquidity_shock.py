"""Factor Calendar Amihud 非流动性冲击因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class LiquidityShockFactor(Factor):
    """当前非流动性相对过去十二个月均值的反向变化。"""

    @staticmethod
    def _rolling_mean(values, window, minimum_observations):
        valid = np.isfinite(values)
        safe_values = np.where(valid, values, 0.0)
        cumulative_sum = np.concatenate(
            ([0.0], np.cumsum(safe_values))
        )
        cumulative_count = np.concatenate(
            ([0], np.cumsum(valid.astype(np.int64)))
        )
        ends = np.arange(1, len(values) + 1)
        starts = np.maximum(ends - window, 0)
        rolling_sum = cumulative_sum[ends] - cumulative_sum[starts]
        rolling_count = cumulative_count[ends] - cumulative_count[starts]
        return np.divide(
            rolling_sum,
            rolling_count,
            out=np.full(len(values), np.nan),
            where=rolling_count >= minimum_observations,
        )

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0

        frame = close.to_frame("close")
        frame["amount"] = amount
        frame = frame.sort_index(level=["symbol", "date"])
        close_values = frame["close"].to_numpy(dtype=float, copy=False)
        amount_values = frame["amount"].to_numpy(dtype=float, copy=False)
        output = np.full(len(frame), np.nan)

        for positions in frame.groupby(
            level="symbol", sort=False
        ).indices.values():
            symbol_close = close_values[positions]
            symbol_amount = amount_values[positions]
            previous_close = np.empty(len(positions), dtype=float)
            previous_close[0] = np.nan
            previous_close[1:] = symbol_close[:-1]
            valid = (
                np.isfinite(symbol_close)
                & np.isfinite(previous_close)
                & np.isfinite(symbol_amount)
                & (symbol_close > 0)
                & (previous_close > 0)
                & (symbol_amount > 0)
            )
            daily_illiquidity = np.full(len(positions), np.nan)
            daily_illiquidity[valid] = (
                np.abs(symbol_close[valid] / previous_close[valid] - 1.0)
                / symbol_amount[valid]
            )
            current_illiquidity = self._rolling_mean(
                daily_illiquidity, 21, 10
            )
            previous_illiquidity = np.empty(len(positions), dtype=float)
            previous_illiquidity[0] = np.nan
            previous_illiquidity[1:] = current_illiquidity[:-1]
            historical_average = self._rolling_mean(
                previous_illiquidity, 252, 21
            )
            output[positions] = historical_average - current_illiquidity

        result = frame["close"].copy()
        result.iloc[:] = output
        result = result.reindex(close.index)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
