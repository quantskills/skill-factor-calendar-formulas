"""Factor Calendar 理想振幅因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class IdealAmplitudeFactor(Factor):
    """20 日内高价与低价四分位交易日的平均振幅之差。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        window = 20

        frame = close.to_frame("close")
        frame["high"] = high
        frame["low"] = low
        frame = frame.sort_index(level=["symbol", "date"])
        close_values = frame["close"].to_numpy(dtype=float, copy=False)
        high_values = frame["high"].to_numpy(dtype=float, copy=False)
        low_values = frame["low"].to_numpy(dtype=float, copy=False)
        output = np.full(len(frame), np.nan)
        bucket_size = window // 4

        for positions in frame.groupby(
            level="symbol", sort=False
        ).indices.values():
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
            symbol_amplitude = np.full(len(positions), np.nan)
            symbol_amplitude[valid] = (
                symbol_high[valid] / symbol_low[valid] - 1.0
            )

            for end in range(window - 1, len(positions)):
                start = end - window + 1
                close_window = symbol_close[start : end + 1]
                amplitude_window = symbol_amplitude[start : end + 1]
                if not np.isfinite(amplitude_window).all():
                    continue
                low_indices = np.argpartition(
                    close_window, bucket_size - 1
                )[:bucket_size]
                high_indices = np.argpartition(
                    close_window, -bucket_size
                )[-bucket_size:]
                output[positions[end]] = (
                    amplitude_window[high_indices].mean()
                    - amplitude_window[low_indices].mean()
                )

        result = frame["close"].copy()
        result.iloc[:] = output
        result = result.reindex(close.index)
        result.name = "value"
        return result
