"""Factor Calendar 振幅切割动量累积因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class AmplitudeCuttingMomentumFactor(Factor):
    """最近 20 日最低振幅 60% 交易日的简单收益率之和。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20
        selected_count = int(np.ceil(window * 0.60))

        frame = close.to_frame("close")
        frame["high"] = high
        frame["low"] = low
        frame = frame.sort_index(level=["symbol", "date"])
        close_values = frame["close"].to_numpy(dtype=float, copy=False)
        high_values = frame["high"].to_numpy(dtype=float, copy=False)
        low_values = frame["low"].to_numpy(dtype=float, copy=False)
        output = np.full(len(frame), np.nan)

        for positions in frame.groupby(
            level="symbol", sort=False
        ).indices.values():
            if len(positions) < window:
                continue

            symbol_close = close_values[positions]
            symbol_high = high_values[positions]
            symbol_low = low_values[positions]
            valid = (
                np.isfinite(symbol_close)
                & np.isfinite(symbol_high)
                & np.isfinite(symbol_low)
                & (symbol_close > 0)
                & (symbol_high > 0)
                & (symbol_low > 0)
                & (symbol_high >= symbol_low)
            )
            previous_close = np.empty(len(positions), dtype=float)
            previous_close[0] = np.nan
            previous_close[1:] = symbol_close[:-1]
            valid_returns = (
                valid
                & np.concatenate(([False], valid[:-1]))
                & np.isfinite(previous_close)
                & (previous_close > 0)
            )
            daily_return = np.full(len(positions), np.nan)
            daily_return[valid_returns] = (
                symbol_close[valid_returns]
                / previous_close[valid_returns]
                - 1.0
            )
            amplitude = np.full(len(positions), np.nan)
            amplitude[valid] = (
                symbol_high[valid] / symbol_low[valid] - 1.0
            )

            amplitude_windows = np.lib.stride_tricks.sliding_window_view(
                amplitude, window_shape=window
            )
            return_windows = np.lib.stride_tricks.sliding_window_view(
                daily_return, window_shape=window
            )
            valid_windows = np.isfinite(amplitude_windows).all(axis=1)
            valid_windows &= np.isfinite(return_windows).all(axis=1)
            if not valid_windows.any():
                continue

            selected_indices = np.argsort(
                amplitude_windows[valid_windows], axis=1, kind="stable"
            )[:, :selected_count]
            selected_returns = np.take_along_axis(
                return_windows[valid_windows], selected_indices, axis=1
            )
            values = np.full(len(amplitude_windows), np.nan)
            values[valid_windows] = selected_returns.sum(axis=1)
            output[positions[window - 1 :]] = values

        result = frame["close"].copy()
        result.iloc[:] = output
        result = result.reindex(close.index)
        result.name = "value"
        return result
