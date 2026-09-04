from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


def _by_symbol_rolling(
    series: pd.Series,
    window: int,
    operation: str,
    *,
    min_periods: int,
) -> pd.Series:
    grouped = series.groupby(level="symbol", group_keys=False, sort=False)

    def calculate(values: pd.Series) -> pd.Series:
        ordered = values.sort_index(level="date")
        rolling = ordered.rolling(window=window, min_periods=min_periods)
        return getattr(rolling, operation)()

    return grouped.apply(calculate).reindex(series.index)


class Factor(ABC):
    """Base class and operators required by the bundled formula modules."""

    @abstractmethod
    def calculate(self, factors: dict[str, pd.Series]) -> pd.Series:
        """Calculate one factor from canonical input series."""

    @staticmethod
    def STDDEV(series: pd.Series, window: int = 20) -> pd.Series:
        return _by_symbol_rolling(
            series,
            window,
            "std",
            min_periods=max(2, window // 4),
        )

    @staticmethod
    def CORRELATION(
        series1: pd.Series,
        series2: pd.Series,
        window: int = 20,
    ) -> pd.Series:
        output = pd.Series(np.nan, index=series1.index, dtype="float64")
        symbols = series1.index.get_level_values("symbol").unique()
        for symbol in symbols:
            left = series1.xs(symbol, level="symbol", drop_level=False)
            right = series2.xs(symbol, level="symbol", drop_level=False)
            left, right = left.align(right)
            ordered = pd.concat({"left": left, "right": right}, axis=1).sort_index(
                level="date"
            )
            values = ordered["left"].rolling(window=window).corr(ordered["right"])
            output.loc[values.index] = values
        return output

    @staticmethod
    def DELAY(series: pd.Series, period: int = 1) -> pd.Series:
        return series.groupby(level="symbol", sort=False).shift(period)

    @staticmethod
    def LOG(series: pd.Series) -> pd.Series:
        return pd.Series(np.log(series), index=series.index)

    @staticmethod
    def MA(series: pd.Series, window: int) -> pd.Series:
        return _by_symbol_rolling(
            series,
            window,
            "mean",
            min_periods=window,
        )

    @staticmethod
    def SUM(series: pd.Series, window: int = 20) -> pd.Series:
        return _by_symbol_rolling(
            series,
            window,
            "sum",
            min_periods=1,
        )

    @staticmethod
    def TS_MAX(series: pd.Series, window: int = 20) -> pd.Series:
        return _by_symbol_rolling(
            series,
            window,
            "max",
            min_periods=1,
        )

    @staticmethod
    def TS_MIN(series: pd.Series, window: int = 20) -> pd.Series:
        return _by_symbol_rolling(
            series,
            window,
            "min",
            min_periods=1,
        )
