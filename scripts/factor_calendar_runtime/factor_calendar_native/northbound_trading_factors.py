"""Factor Calendar 北向资金交易行为量化市场代理因子。"""

import numpy as np
import pandas as pd

from factor_calendar_runtime import Factor


class NorthboundTradingFactorsFactor(Factor):
    """组合持仓规模、流入稳定性及高价高量日资金流代理指标。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        volume = factors["volume"] + 0
        amount = factors["amount"] + 0
        market_cap = factors["market_cap"] + 0
        previous_close = close.groupby(level="symbol", sort=False).shift(1)
        returns = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        signed_flow = np.sign(returns).fillna(0) * amount
        holding_value = market_cap.where(market_cap > 0)
        mean_holding = holding_value.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        mean_flow = signed_flow.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        flow_std = signed_flow.groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).std()
        )
        mean_abs_flow = signed_flow.abs().groupby(
            level="symbol", sort=False
        ).transform(
            lambda item: item.rolling(20, min_periods=10).mean()
        )
        frame = pd.concat(
            {"close": close, "volume": volume, "flow": signed_flow},
            axis=1,
        )

        def peak_flows(group):
            prices = group["close"].to_numpy(dtype=float)
            volumes = group["volume"].to_numpy(dtype=float)
            flows = group["flow"].to_numpy(dtype=float)
            output = np.full((len(group), 2), np.nan)
            for position in range(9, len(group)):
                start = max(0, position - 19)
                sample_prices = prices[start : position + 1]
                sample_volumes = volumes[start : position + 1]
                sample_flows = flows[start : position + 1]
                valid = (
                    np.isfinite(sample_prices)
                    & np.isfinite(sample_volumes)
                    & np.isfinite(sample_flows)
                )
                if valid.sum() < 10:
                    continue
                sample_prices = sample_prices[valid]
                sample_volumes = sample_volumes[valid]
                sample_flows = sample_flows[valid]
                price_positions = np.argpartition(
                    sample_prices, -3
                )[-3:]
                volume_positions = np.argpartition(
                    sample_volumes, -3
                )[-3:]
                output[position, 0] = sample_flows[
                    price_positions
                ].mean()
                output[position, 1] = sample_flows[
                    volume_positions
                ].mean()
            return pd.DataFrame(output, index=group.index)

        peak_flow = frame.groupby(
            level="symbol", sort=False, group_keys=False
        ).apply(peak_flows).reindex(close.index)
        components = pd.concat(
            [
                mean_holding,
                (mean_flow / flow_std).where(flow_std > 0),
                (peak_flow.iloc[:, 0] / mean_holding).where(
                    mean_holding > 0
                ),
                (peak_flow.iloc[:, 1] / mean_abs_flow).where(
                    mean_abs_flow > 0
                ),
            ],
            axis=1,
        )
        ranked = components.groupby(level="date", sort=False).rank(pct=True)
        result = ranked.mean(axis=1)
        result = result.replace([np.inf, -np.inf], np.nan)
        result.name = "value"
        return result
