"""Factor Calendar 应付账款周转率（TTM）因子。"""

from factor_calendar_runtime import Factor


class AccountsPayableTurnoverRatioTTMFactor(Factor):
    """营业成本 TTM 与期初、期末应付账款平均值之比。"""

    def calculate(self, factors):
        sp_ratio_ttm = factors["sp_ratio_ttm"]
        market_cap = factors["market_cap"]
        operating_revenue = factors["operating_revenue"]
        cost_of_goods_sold = factors["cost_of_goods_sold"]
        accounts_payable = factors["accts_payable"]
        lookback = 252  # 约 12 个月

        revenue_ttm = sp_ratio_ttm * market_cap
        cost_ratio = (cost_of_goods_sold / operating_revenue).where(operating_revenue > 0)
        cost_of_goods_sold_ttm = revenue_ttm * cost_ratio
        start_accounts_payable = self.DELAY(accounts_payable, lookback)
        average_accounts_payable = (start_accounts_payable + accounts_payable) / 2

        result = (cost_of_goods_sold_ttm / average_accounts_payable).where(average_accounts_payable > 0)
        return result
