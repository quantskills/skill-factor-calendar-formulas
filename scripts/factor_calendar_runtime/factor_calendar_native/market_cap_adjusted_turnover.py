"""Factor Calendar 市值中性化换手率残差因子。"""

from factor_calendar_runtime import Factor


class MarketCapAdjustedTurnoverFactor(Factor):
    """日均换手率对市值对数做每日横截面回归后的残差。"""

    def calculate(self, factors):
        turnover = factors["turnover"] + 0
        market_cap = factors["market_cap"] + 0
        window = 21

        average_turnover = turnover.where(turnover >= 0).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=window, min_periods=window
            ).mean()
        )
        log_turnover = self.LOG(average_turnover.where(average_turnover > 0))
        log_market_cap = self.LOG(market_cap.where(market_cap > 0))
        valid = log_turnover.notna() & log_market_cap.notna()
        x = log_market_cap.where(valid)
        y = log_turnover.where(valid)

        x_mean = x.groupby(level="date", sort=False).transform("mean")
        y_mean = y.groupby(level="date", sort=False).transform("mean")
        x_centered = x - x_mean
        y_centered = y - y_mean
        covariance = (x_centered * y_centered).groupby(
            level="date", sort=False
        ).transform("mean")
        variance = (x_centered * x_centered).groupby(
            level="date", sort=False
        ).transform("mean")
        counts = valid.groupby(level="date", sort=False).transform("sum")
        slope = (covariance / variance).where((variance > 0) & (counts >= 3))
        result = y_centered - slope * x_centered
        result.name = "value"
        return result
