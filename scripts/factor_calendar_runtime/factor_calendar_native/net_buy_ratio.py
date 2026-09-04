"""Factor Calendar 开盘时段主动净买额占比因子。"""

import numpy as np

from factor_calendar_runtime import Factor


class NetBuyRatioFactor(Factor):
    """优先使用主动买卖成交额，缺失时使用日K线方向代理。"""

    def calculate(self, factors):
        buy_names = [
            "active_buy_amount_large_mid",
            "active_buy_amount_small",
        ]
        sell_names = [
            "active_sell_amount_large_mid",
            "active_sell_amount_small",
        ]
        if all(name in getattr(factors, "data_dict", factors) for name in buy_names + sell_names):
            buy_amount = sum((factors[name] + 0 for name in buy_names))
            sell_amount = sum((factors[name] + 0 for name in sell_names))
            total_amount = buy_amount + sell_amount
            daily_ratio = ((buy_amount - sell_amount) / total_amount).where(
                total_amount > 0
            )
        else:
            open_price = factors["open"] + 0
            high = factors["high"] + 0
            low = factors["low"] + 0
            close = factors["close"] + 0
            price_range = high - low
            daily_ratio = ((close - open_price) / price_range).where(
                price_range > 0
            )
        result = daily_ratio.groupby(level="symbol", sort=False).transform(
            lambda item: item.rolling(20, min_periods=5).mean()
        )
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
