"""Factor Calendar 条件流动性冲击因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class ConditionalLiquidityShockFactor(Factor):
    """滚动估计 Amihud 非流动性 ARMA(1,1) 模型的当期残差。"""

    @staticmethod
    def _rolling_sums(values, window):
        cumulative = np.vstack(
            [np.zeros((1, values.shape[1])), np.cumsum(values, axis=0)]
        )
        ends = np.arange(1, len(values) + 1)
        starts = np.maximum(ends - window, 0)
        return cumulative[ends] - cumulative[starts]

    @classmethod
    def _symbol_shocks(cls, values, window=252, minimum_observations=60):
        values = np.asarray(values, dtype=float)
        result = np.full(len(values), np.nan)
        finite_values = values[np.isfinite(values)]
        if len(finite_values) < minimum_observations:
            return result

        scale = np.std(finite_values)
        if not np.isfinite(scale) or scale <= 0:
            return result
        normalized = values / scale

        lagged = normalized[:-1]
        current = normalized[1:]
        valid_ar = np.isfinite(lagged) & np.isfinite(current)
        ar_rows = np.column_stack(
            [
                valid_ar.astype(float),
                np.where(valid_ar, lagged, 0.0),
                np.where(valid_ar, current, 0.0),
                np.where(valid_ar, lagged * lagged, 0.0),
                np.where(valid_ar, lagged * current, 0.0),
            ]
        )
        ar_sums = cls._rolling_sums(ar_rows, window - 1)
        counts, sum_x, sum_y, sum_xx, sum_xy = ar_sums.T
        denominator = counts * sum_xx - sum_x * sum_x
        valid_coefficients = (counts >= 3) & (np.abs(denominator) > 1e-12)

        intercept = np.full(len(current), np.nan)
        autoregressive = np.full(len(current), np.nan)
        autoregressive[valid_coefficients] = (
            counts[valid_coefficients] * sum_xy[valid_coefficients]
            - sum_x[valid_coefficients] * sum_y[valid_coefficients]
        ) / denominator[valid_coefficients]
        intercept[valid_coefficients] = (
            sum_y[valid_coefficients]
            - autoregressive[valid_coefficients] * sum_x[valid_coefficients]
        ) / counts[valid_coefficients]

        innovations = np.full(len(normalized), np.nan)
        valid_innovations = valid_coefficients & valid_ar
        innovations[1:][valid_innovations] = current[valid_innovations] - (
            intercept[valid_innovations]
            + autoregressive[valid_innovations] * lagged[valid_innovations]
        )

        lagged_innovation = innovations[:-1]
        valid_arma = (
            np.isfinite(lagged)
            & np.isfinite(lagged_innovation)
            & np.isfinite(current)
        )
        x1 = np.where(valid_arma, lagged, 0.0)
        x2 = np.where(valid_arma, lagged_innovation, 0.0)
        y = np.where(valid_arma, current, 0.0)
        arma_rows = np.column_stack(
            [
                valid_arma.astype(float),
                x1,
                x2,
                y,
                x1 * x1,
                x2 * x2,
                x1 * x2,
                x1 * y,
                x2 * y,
            ]
        )
        arma_sums = cls._rolling_sums(arma_rows, window - 1)
        (
            counts,
            sum_x1,
            sum_x2,
            sum_y,
            sum_x1x1,
            sum_x2x2,
            sum_x1x2,
            sum_x1y,
            sum_x2y,
        ) = arma_sums.T

        matrices = np.empty((len(current), 3, 3), dtype=float)
        matrices[:, 0, 0] = counts
        matrices[:, 0, 1] = matrices[:, 1, 0] = sum_x1
        matrices[:, 0, 2] = matrices[:, 2, 0] = sum_x2
        matrices[:, 1, 1] = sum_x1x1
        matrices[:, 1, 2] = matrices[:, 2, 1] = sum_x1x2
        matrices[:, 2, 2] = sum_x2x2
        targets = np.column_stack([sum_y, sum_x1y, sum_x2y])

        determinants = np.linalg.det(matrices)
        eligible = (
            (counts >= minimum_observations - 1)
            & valid_arma
            & np.isfinite(determinants)
            & (np.abs(determinants) > 1e-10)
        )
        coefficients = np.full((len(current), 3), np.nan)
        coefficients[eligible] = np.linalg.solve(
            matrices[eligible], targets[eligible, :, None]
        )[:, :, 0]
        predicted = (
            coefficients[:, 0]
            + coefficients[:, 1] * lagged
            + coefficients[:, 2] * lagged_innovation
        )
        result[1:] = np.where(eligible, current - predicted, np.nan) * scale
        return result

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        daily_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        daily_illiquidity = (daily_return.abs() / amount).where(amount > 0)

        values = daily_illiquidity.to_numpy(dtype=float, copy=False)
        output = np.full(len(values), np.nan)
        for positions in daily_illiquidity.groupby(
            level="symbol", sort=False
        ).indices.values():
            output[positions] = self._symbol_shocks(values[positions])

        result = daily_illiquidity.copy()
        result.iloc[:] = output
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
