"""Factor Calendar 成交量动量摆动指标（KVO）因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class KlingerVolumeOscillatorFactor(Factor):
    """成交量波动力的 34 日与 55 日 EMA 之差。"""

    def calculate(self, factors):
        high = factors["high"] + 0
        low = factors["low"] + 0
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        short_window = 34
        long_window = 55

        valid_price = (
            (high > 0)
            & (low > 0)
            & (close > 0)
            & (high >= close)
            & (close >= low)
            & (volume >= 0)
        )
        valid_high = high.where(valid_price)
        valid_low = low.where(valid_price)
        valid_close = close.where(valid_price)
        daily_momentum = valid_high - valid_low
        typical_price_sum = valid_high + valid_low + valid_close
        previous_typical_price_sum = self.DELAY(typical_price_sum, 1)
        trend = pd.Series(
            np.where(typical_price_sum > previous_typical_price_sum, 1.0, -1.0),
            index=high.index,
        ).where(previous_typical_price_sum.notna() & typical_price_sum.notna())

        cumulative_values = np.full(len(daily_momentum), np.nan, dtype=float)
        grouped_positions = daily_momentum.groupby(
            level="symbol", sort=False
        ).indices
        momentum_values = daily_momentum.to_numpy(dtype=float)
        trend_values = trend.to_numpy(dtype=float)
        for positions in grouped_positions.values():
            previous_trend = np.nan
            previous_momentum = np.nan
            previous_cumulative = np.nan
            for position in positions:
                current_momentum = momentum_values[position]
                current_trend = trend_values[position]
                if not np.isfinite(current_momentum):
                    previous_momentum = np.nan
                    previous_trend = np.nan
                    previous_cumulative = np.nan
                    continue
                if not np.isfinite(current_trend):
                    previous_momentum = current_momentum
                    continue
                if (
                    np.isfinite(previous_trend)
                    and current_trend == previous_trend
                    and np.isfinite(previous_cumulative)
                ):
                    current_cumulative = previous_cumulative + current_momentum
                elif np.isfinite(previous_momentum):
                    current_cumulative = previous_momentum + current_momentum
                else:
                    current_cumulative = current_momentum
                cumulative_values[position] = current_cumulative
                previous_trend = current_trend
                previous_momentum = current_momentum
                previous_cumulative = current_cumulative

        cumulative_momentum = pd.Series(
            cumulative_values, index=daily_momentum.index
        )
        volume_force = (
            volume
            * (2 * (daily_momentum / cumulative_momentum - 1)).abs()
            * trend
            * 100
        ).where((volume >= 0) & (cumulative_momentum > 0))
        short_ema = volume_force.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=short_window,
                adjust=False,
                min_periods=short_window,
            ).mean()
        )
        long_ema = volume_force.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.ewm(
                span=long_window,
                adjust=False,
                min_periods=long_window,
            ).mean()
        )
        result = short_ema - long_ema
        result.name = "value"
        return result
