"""Factor Calendar 融资成本营收占比因子。"""

from factor_calendar_runtime import Factor


class FinancingCostToOperatingRevenueRatioTTMFactor(Factor):
    """财务费用与营业收入之比。"""

    def calculate(self, factors):
        financing_cost = factors["financing_expense"]
        operating_revenue = factors["operating_revenue"]

        result = (financing_cost / operating_revenue).where(
            operating_revenue > 0
        )
        return result
