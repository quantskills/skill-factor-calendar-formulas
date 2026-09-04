"""Factor Calendar 流动性调整成交量零值比率因子。"""

from factor_calendar_runtime import Factor

from factor_calendar_batch10_utils import finish, rolling_mean, rolling_sum, safe_divide, series


class LiquidityAdjustedVolumeFactor(Factor):
    """一年零成交量天数、平均换手率和有效交易天数的组合。"""

    def calculate(self, factors):
        volume = series(factors, "volume")
        turnover = series(factors, "turnover")
        window = 250
        zero_days = rolling_sum((volume == 0).astype(float), window)
        average_turnover = rolling_mean(turnover.where(turnover >= 0), window)
        trading_days = rolling_sum(volume.notna().astype(float), window)
        scale = 1_000_000
        result = (
            zero_days / scale
            + safe_divide(1, average_turnover, positive=True)
            - safe_divide(2 * window, trading_days, positive=True)
        )
        return finish(result)
