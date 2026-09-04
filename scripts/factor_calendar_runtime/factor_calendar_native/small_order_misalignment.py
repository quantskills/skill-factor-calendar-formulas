"""Factor Calendar 小单错位自相关性市场代理因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class SmallOrderMisalignmentFactor(Factor):
    """计算成交量代理小单净流入序列的一阶错位等级相关性。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        small_order_flow = np.sign(returns).fillna(0) * np.sqrt(
            volume.clip(lower=0)
        )

        def average_ranks(values):
            order = np.argsort(values, kind="mergesort")
            sorted_values = values[order]
            ranks = np.empty(len(values), dtype=float)
            start = 0
            while start < len(values):
                end = start + 1
                while (
                    end < len(values)
                    and sorted_values[end] == sorted_values[start]
                ):
                    end += 1
                ranks[order[start:end]] = (start + end - 1) / 2
                start = end
            return ranks

        def rank_correlation(window):
            first_values = np.asarray(window[:-1], dtype=float)
            second_values = np.asarray(window[1:], dtype=float)
            if not np.isfinite(first_values).all() or not np.isfinite(
                second_values
            ).all():
                return np.nan
            first_ranks = average_ranks(first_values)
            second_ranks = average_ranks(second_values)
            first_ranks -= first_ranks.mean()
            second_ranks -= second_ranks.mean()
            denominator = np.sqrt(
                np.dot(first_ranks, first_ranks)
                * np.dot(second_ranks, second_ranks)
            )
            if denominator <= 0:
                return np.nan
            return np.dot(first_ranks, second_ranks) / denominator

        result = small_order_flow.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(21, min_periods=11).apply(
                rank_correlation, raw=True
            )
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
