"""Factor Calendar 科波克曲线（Coppock Curve）因子。"""

from factor_calendar_runtime import Factor


class CoppockCurveFactor(Factor):
    """14 日与 11 日价格变动率之和的 10 日加权移动平均。"""

    def calculate(self, factors):
        close = factors["close"] + 0
        short_window = 14
        medium_window = 11
        smooth_window = 10

        short_close = self.DELAY(close, short_window)
        medium_close = self.DELAY(close, medium_window)
        short_roc = ((close / short_close - 1) * 100).where(
            (close > 0) & (short_close > 0)
        )
        medium_roc = ((close / medium_close - 1) * 100).where(
            (close > 0) & (medium_close > 0)
        )
        combined_roc = short_roc + medium_roc
        result = combined_roc.groupby(
            level="symbol", sort=False
        ).transform(
            lambda series: series.rolling(
                window=smooth_window,
                min_periods=smooth_window,
            ).apply(
                lambda values: values[::-1].cumsum().sum()
                * 2
                / smooth_window
                / (smooth_window + 1),
                raw=True,
            )
        )
        result.name = "value"
        return result
