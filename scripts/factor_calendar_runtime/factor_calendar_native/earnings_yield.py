"""Factor Calendar 盈利收益率因子。"""

from factor_calendar_runtime import Factor


class EarningsYieldFactor(Factor):
    """TTM 市盈率的倒数，即净利润 TTM 与总市值之比。"""

    def calculate(self, factors):
        pe_ratio_ttm = factors["pe_ratio_ttm"] + 0

        result = (1.0 / pe_ratio_ttm).where(
            pe_ratio_ttm.notna() & (pe_ratio_ttm != 0)
        )
        result.name = "value"
        return result
