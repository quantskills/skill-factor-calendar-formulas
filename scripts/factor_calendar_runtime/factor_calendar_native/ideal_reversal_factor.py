"""Factor Calendar 成交额分位数反转强度因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class IdealReversalFactor(Factor):
    """滚动窗口内高成交额日与低成交额日收益之差。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        amount = factors["amount"] + 0
        daily_return = close.groupby(
            level="symbol", sort=False
        ).pct_change(fill_method=None)
        frame = pd.concat({"amount": amount, "return": daily_return}, axis=1)
        result = pd.Series(np.nan, index=frame.index, dtype=float)
        for positions in frame.groupby(
            level="symbol", sort=False
        ).indices.values():
            values = frame.iloc[positions].to_numpy(dtype=float)
            for offset in range(9, len(positions)):
                start = max(0, offset - 19)
                window = values[start : offset + 1]
                valid = window[np.isfinite(window).all(axis=1)]
                if len(valid) < 10:
                    continue
                order = np.argsort(valid[:, 0])
                bucket = max(1, min(10, len(valid) // 2))
                returns = valid[:, 1]
                result.iloc[positions[offset]] = (
                    returns[order[-bucket:]].sum()
                    - returns[order[:bucket]].sum()
                )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
