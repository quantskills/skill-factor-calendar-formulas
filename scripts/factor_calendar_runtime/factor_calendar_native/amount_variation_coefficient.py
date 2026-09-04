"""Factor Calendar 成交额变异系数因子（按比赛页面公式实现）。"""

from factor_calendar_runtime import Factor


class AmountVariationCoefficientFactor(Factor):
    """最近 3 个月日成交额均值与标准差之比。"""

    def calculate(self, factors):
        amount = factors["amount"]
        window = 63  # 3 个月约等于 63 个交易日

        mean_amount = self.MA(amount, window)
        std_amount = self.STDDEV(amount, window)

        # 标准差为 0 时该比值无定义，保留为 NaN 供下游节点过滤。
        result = (mean_amount / std_amount).where(std_amount > 0)
        return result
