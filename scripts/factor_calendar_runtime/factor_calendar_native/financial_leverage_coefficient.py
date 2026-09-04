"""Factor Calendar 财务杠杆系数（权益乘数）因子。"""

from factor_calendar_runtime import Factor


class FinancialLeverageCoefficientFactor(Factor):
    """平均总资产与平均归属于母公司股东权益之比。"""

    def calculate(self, factors):
        total_assets = factors["total_assets"]
        equity_parent_company = factors["equity_parent_company"]
        lookback = 252  # 约 12 个月

        start_total_assets = self.DELAY(total_assets, lookback)
        start_equity_parent_company = self.DELAY(
            equity_parent_company, lookback
        )

        average_total_assets = (start_total_assets + total_assets) / 2
        average_equity_parent_company = (
            start_equity_parent_company + equity_parent_company
        ) / 2

        valid = (average_total_assets > 0) & (
            average_equity_parent_company > 0
        )
        result = (
            average_total_assets / average_equity_parent_company
        ).where(valid)
        return result
