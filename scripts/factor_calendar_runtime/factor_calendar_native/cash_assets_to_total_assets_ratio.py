"""Factor Calendar 现金资产占总资产比率因子。"""

from factor_calendar_runtime import Factor


class CashAssetsToTotalAssetsRatioFactor(Factor):
    """当前报告期货币资金与平均总资产之比。"""

    def calculate(self, factors):
        cash_assets = factors["bs_money_cap"] + 0
        if "total_assets" in getattr(factors, "data_dict", factors):
            total_assets = factors["total_assets"] + 0
            if "bs_total_assets" in getattr(factors, "data_dict", factors):
                total_assets = total_assets.fillna(
                    factors["bs_total_assets"] + 0
                )
        else:
            total_assets = factors["bs_total_assets"] + 0
        lookback = 252

        start_total_assets = self.DELAY(total_assets, lookback)
        start_total_assets = start_total_assets.fillna(total_assets)
        average_total_assets = (start_total_assets + total_assets) / 2

        valid = (average_total_assets > 0) & (cash_assets >= 0)
        result = (cash_assets / average_total_assets).where(valid)
        result.name = "value"
        return result
