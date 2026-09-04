"""Factor Calendar 应付账款周转天数因子。"""

from factor_calendar_runtime import Factor


class AccountsPayableTurnoverDaysFactor(Factor):
    """平均应付账款占营业成本 TTM 的比例乘以 360。"""

    def calculate(self, factors):
        sp_ratio_ttm = factors["sp_ratio_ttm"] + 0
        market_cap = factors["market_cap"] + 0
        operating_revenue = factors["operating_revenue"] + 0
        cost_of_goods_sold = factors["cost_of_goods_sold"] + 0
        accounts_payable = factors["accts_payable"] + 0
        lookback = 252

        revenue_ttm = sp_ratio_ttm * market_cap
        cost_ratio = (cost_of_goods_sold / operating_revenue).where(
            (cost_of_goods_sold >= 0) & (operating_revenue > 0)
        )
        cost_of_goods_sold_ttm = revenue_ttm * cost_ratio
        start_accounts_payable = self.DELAY(accounts_payable, lookback)
        average_accounts_payable = (
            start_accounts_payable + accounts_payable
        ) / 2
        result = (
            average_accounts_payable / cost_of_goods_sold_ttm * 360
        ).where(
            (average_accounts_payable >= 0)
            & (cost_of_goods_sold_ttm > 0)
        )
        result.name = "value"
        return result
