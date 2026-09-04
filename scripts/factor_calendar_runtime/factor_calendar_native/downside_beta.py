"""Factor Calendar 下行风险贝塔因子。"""

from factor_calendar_runtime import Factor


class DownsideBetaFactor(Factor):
    """市场收益低于滚动均值时的 252 日条件贝塔。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        previous_close = self.DELAY(close, 1)
        stock_return = (close / previous_close - 1).where(
            (close > 0) & (previous_close > 0)
        )
        market_return = stock_return.groupby(
            level="date", sort=False
        ).transform("mean")
        market_mean = market_return.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).mean()
        )
        selected = (
            (market_return < market_mean)
            & stock_return.notna()
            & market_return.notna()
        )

        count = selected.astype(float).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).sum()
        )
        selected_stock = stock_return.where(selected, 0.0)
        selected_market = market_return.where(selected, 0.0)

        sum_stock = selected_stock.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).sum()
        )
        sum_market = selected_market.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).sum()
        )
        sum_product = (selected_stock * selected_market).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).sum()
        )
        sum_market_squared = (selected_market * selected_market).groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(252, min_periods=252).sum()
        )

        covariance_numerator = sum_product - sum_stock * sum_market / count
        variance_numerator = sum_market_squared - sum_market * sum_market / count
        result = (covariance_numerator / variance_numerator).where(
            (count >= 20) & (variance_numerator > 0)
        )
        result.name = "value"
        return result
