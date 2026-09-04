"""第十批 Factors Directory 行情因子的共享计算逻辑。"""

import numpy as np
import pandas as pd


def series(factors, name):
    return factors[name] + 0


def safe_divide(numerator, denominator, positive=False):
    valid = denominator > 0 if positive else denominator != 0
    return (numerator / denominator).where(valid).replace(
        [np.inf, -np.inf], np.nan
    )


def delay(values, periods):
    return values.groupby(level="symbol", sort=False).shift(periods)


def rolling_mean(values, window, min_periods=None):
    if min_periods is None:
        min_periods = window
    return values.groupby(level="symbol", sort=False).transform(
        lambda item: item.rolling(window, min_periods=min_periods).mean()
    )


def rolling_sum(values, window, min_periods=None):
    if min_periods is None:
        min_periods = window
    return values.groupby(level="symbol", sort=False).transform(
        lambda item: item.rolling(window, min_periods=min_periods).sum()
    )


def rolling_std(values, window, min_periods=None, ddof=0):
    if min_periods is None:
        min_periods = window
    return values.groupby(level="symbol", sort=False).transform(
        lambda item: item.rolling(window, min_periods=min_periods).std(ddof=ddof)
    )


def stock_and_market_returns(close):
    previous_close = delay(close, 1)
    stock_return = np.log(
        safe_divide(close, previous_close, positive=True).where(close > 0)
    )
    market_return = stock_return.groupby(level="date", sort=False).transform(
        "mean"
    )
    return stock_return, market_return


def rolling_residuals(stock_return, market_return, window):
    frame = pd.concat(
        {"stock": stock_return, "market": market_return}, axis=1
    )
    parts = []
    for _, item in frame.groupby(level="symbol", sort=False):
        values = item.to_numpy(dtype=float)
        output = np.full(len(item), np.nan)
        for position in range(window - 1, len(item)):
            sample = values[position - window + 1:position + 1]
            valid = np.isfinite(sample).all(axis=1)
            if valid.sum() < window:
                continue
            stock = sample[:, 0]
            market = sample[:, 1]
            design = np.column_stack([np.ones(window), market])
            coefficients = np.linalg.lstsq(design, stock, rcond=None)[0]
            output[position] = stock[-1] - design[-1] @ coefficients
        parts.append(pd.Series(output, index=item.index))
    return pd.concat(parts).reindex(stock_return.index)


def rolling_slope(left, right, window):
    frame = pd.concat({"left": left, "right": right}, axis=1)
    parts = []
    for _, item in frame.groupby(level="symbol", sort=False):
        values = item.to_numpy(dtype=float)
        output = np.full(len(item), np.nan)
        for position in range(window - 1, len(item)):
            sample = values[position - window + 1:position + 1]
            valid = np.isfinite(sample).all(axis=1)
            if valid.sum() < window:
                continue
            dependent = sample[:, 0]
            independent = sample[:, 1]
            variance = np.var(independent)
            if variance <= 0:
                continue
            output[position] = np.mean(
                (dependent - dependent.mean())
                * (independent - independent.mean())
            ) / variance
        parts.append(pd.Series(output, index=item.index))
    return pd.concat(parts).reindex(left.index)


def finish(result):
    result = result.replace([np.inf, -np.inf], np.nan)
    result.name = "value"
    return result
