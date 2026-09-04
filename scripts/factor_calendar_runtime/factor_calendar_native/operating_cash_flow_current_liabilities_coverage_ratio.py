"""Factor Calendar 经营现金流流动负债覆盖率因子。"""

from factor_calendar_runtime import Factor


class OperatingCashFlowCurrentLiabilitiesCoverageRatioFactor(Factor):
    """经营活动现金流量净额与平均流动负债之比。"""

    def calculate(self, factors):
        operating_cash_flow = factors["cash_flow_from_operating_activities"]
        current_liabilities = factors["current_liabilities"]
        lookback = 252  # 约 12 个月

        start_current_liabilities = self.DELAY(current_liabilities, lookback)
        average_current_liabilities = (
            start_current_liabilities + current_liabilities
        ) / 2

        result = (operating_cash_flow / average_current_liabilities).where(
            average_current_liabilities > 0
        )
        return result
