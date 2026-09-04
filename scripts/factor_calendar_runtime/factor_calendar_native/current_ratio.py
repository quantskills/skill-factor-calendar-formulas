"""Factor Calendar 流动比率因子。"""

from factor_calendar_runtime import Factor


class CurrentRatioFactor(Factor):
    """流动资产与流动负债之比。"""

    def calculate(self, factors):
        current_assets = factors["current_assets"]
        current_liabilities = factors["current_liabilities"]

        result = (current_assets / current_liabilities).where(current_liabilities > 0)
        return result
