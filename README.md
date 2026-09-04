# skill-factor-calendar-formulas

**简体中文** | [English](README.en.md)

> Factor Calendar 公式因子库：从长表日频行情与时点基本面数据批量计算 241 个原始因子值。

<p align="center">
  <img alt="library" src="https://img.shields.io/badge/library-Factor%20Calendar-blue">
  <img alt="factors" src="https://img.shields.io/badge/factors-241-brightgreen">
  <img alt="type" src="https://img.shields.io/badge/type-factor--library-blue">
  <img alt="platform" src="https://img.shields.io/badge/platform-Codex-9cf">
  <img alt="status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <img alt="validation" src="https://img.shields.io/badge/validation-L3%20verified-success">
  <img alt="license" src="https://img.shields.io/badge/license-GPLv3-blue">
</p>

skill-factor-calendar-formulas 是一个独立公式因子库 Skill，用于计算 [Factors Directory](https://factors.directory/zh) 收录的量价、流动性、情绪与基本面因子。

这个仓库适合用于研究：

- 241 个 Factor Calendar 公式因子的批量生成
- 从日频行情与时点基本面长表构建因子矩阵
- 后续因子评价、因子筛选、模型训练或回测前的数据准备
- Codex 对话中触发确定性因子计算工作流

本仓库只负责计算原始因子值，不调用 LLM，不读取 API key，也不输出 IC、ICIR、方向翻转、回测收益或交易建议。

## 仓库内容

| 因子库 | 数量 | 输出文件 | 说明 |
|---|---:|---|---|
| Factor Calendar | 241 | factor_calendar_values.csv | 量价、流动性、情绪与基本面公式 |
| Factor Calendar Long | 241 | factor_calendar_panel.csv | 可选的标准长表输出 |

每个因子使用稳定 ID，例如 factor-calendar.amount_volatility。公式位于内置 native 目录，运行时不依赖其他因子 Skill。

输入字段不足时，相关因子不会终止非严格模式下的整个任务，而是记录到 skipped_factors.json。

## 目录结构

```text
skill-factor-calendar-formulas/
├── SKILL.md
├── README.md
├── README.en.md
├── agents/
│   └── openai.yaml
├── examples/
│   ├── compute_input.json
│   └── toy_market_data.csv
├── references/
│   ├── input_schema.md
│   ├── output_contract.md
│   ├── source_boundary.md
│   └── validation_notes.md
└── scripts/
    ├── compute_factor_calendar_factors.py
    └── factor_calendar_runtime/
        ├── catalog.json
        ├── data.py
        ├── factor_calendar_native/
        ├── factor_compute.py
        ├── factor_formulas_utils.py
        ├── runtime.py
        └── selector.py
```

## 数据要求

输入为长表 CSV 或 Parquet，每一行是一只证券在一个交易日的记录。

必需键字段：

```text
date, symbol
```

量价字段按所选公式使用：

```text
open, high, low, close, volume, amount, turnover, market_cap
```

基本面字段按所选公式使用：

```text
accts_payable, bs_money_cap, bs_total_assets,
cash_flow_from_operating_activities, cost_of_goods_sold,
current_assets, current_liabilities, equity_parent_company,
financing_expense, net_fixed_assets, net_profit_parent,
operating_revenue, pe_ratio_ttm, sp_ratio_ttm,
total_assets, total_equity, total_liabilities
```

处理规则：

| 字段/规则 | 说明 |
|---|---|
| date | 支持 YYYYMMDD、YYYY-MM-DD 或其他可解析日期 |
| symbol | 按字符串处理，保留前导零 |
| column_mapping | 将源文件列名映射到标准字段 |
| load_start_date / load_end_date | 控制公式计算使用的历史数据 |
| start_date / end_date | 公式计算后裁剪输出区间 |
| 缺少公式字段 | 非严格模式跳过对应因子，严格模式终止 |

财务数据必须由使用者按实际披露可得时间提前对齐，运行时不会推断公告日。

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

运行示例配置：

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json
```

指定输出目录：

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json --output outputs/my_factor_run
```

--output 会覆盖 JSON 中的 output_dir。

## 输入配置

示例见 [examples/compute_input.json](examples/compute_input.json)。

```json
{
  "market_data_path": "toy_market_data.csv",
  "output_dir": "outputs/factor_calendar_compute_example",
  "factor_names": [
    "factor-calendar.amount_volatility",
    "factor-calendar.book_to_market_ratio"
  ],
  "exclude_factor_names": [],
  "column_mapping": {},
  "load_start_date": "",
  "load_end_date": "",
  "start_date": "",
  "end_date": "",
  "symbols": [],
  "output_format": "csv",
  "output_layout": "wide",
  "n_jobs": 1,
  "strict": true,
  "show_progress": true
}
```

核心字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| market_data_path | string | 长表 CSV 或 Parquet；相对路径依次按输入 JSON 目录、Skill 根目录解析 |
| output_dir | string | 输出目录；JSON 内相对路径按 Skill 根目录解析 |
| factor_names | list/string | 为空表示计算全部 241 个因子；支持完整 ID 或短名称 |
| exclude_factor_names | list/string | 在选择后排除指定因子 |
| column_mapping | object | 标准字段到源字段的映射 |
| load_start_date / load_end_date | string | 可选的历史加载闭区间 |
| start_date / end_date | string | 可选的输出闭区间 |
| symbols | list[string] | 可选证券池，空列表表示全部证券 |
| output_format | string | csv 或 parquet |
| output_layout | string | wide、long 或 both |
| n_jobs | integer | 并行 worker 数，缺省为机器逻辑 CPU 数 |
| strict | bool | 是否在缺少字段或公式失败时终止 |
| show_progress | bool | 是否打印计算进度 |

## 因子选择方式

计算全部因子：

```json
{
  "factor_names": []
}
```

只计算指定因子：

```json
{
  "factor_names": [
    "amount_volatility",
    "factor-calendar.book_to_market_ratio"
  ]
}
```

排除指定因子：

```json
{
  "factor_names": [],
  "exclude_factor_names": [
    "factor-calendar.news_volume"
  ]
}
```

## 输出文件

运行结果写入 output_dir：

```text
outputs/factor_calendar_compute_example/
├── factor_calendar_values.csv
├── factor_calendar_panel.csv
├── factor_compute_summary.json
├── skipped_factors.json
├── factor_manifest.json
└── run_config.json
```

| 文件 | 内容 |
|---|---|
| factor_calendar_values.csv 或 .parquet | 宽表因子值，仅在 wide 或 both 模式生成 |
| factor_calendar_panel.csv 或 .parquet | 标准长表因子值，仅在 long 或 both 模式生成 |
| factor_compute_summary.json | 输入、输出、样本区间、因子数量和跳过数量摘要 |
| skipped_factors.json | 缺字段、导入失败或计算失败的因子 |
| factor_manifest.json | 因子 ID、所需字段和公式 SHA-256 |
| run_config.json | 本次运行的有效配置 |

宽表格式：

```text
date,symbol,factor-calendar.amount_volatility,...
```

长表格式：

```text
instrument_id,timestamp,factor_id,value
```

## 运行大样本时的建议

全市场、长时间区间和 241 个因子会产生较大的内存与写盘压力。建议：

- 先用少量因子和短区间执行 smoke test。
- 使用 load_start_date 保留滚动窗口预热数据，再用 start_date 裁剪输出。
- n_jobs 不要盲目设为机器最大核数；并行越高，内存压力越大。
- 基本面与纯量价因子可分批运行，减少一次加载的字段数量。

## 验证口径

当前验证等级为 L3 verified。这里的 verified 指公式迁移完整性、全量运行完整性和 CLI 契约验证，不代表预测收益或交易收益验证。

已验证内容：

- 目录包含 241 个唯一因子 ID 和 241 个对应 native 公式模块。
- 241 个公式在 320 个交易日、8 只证券的确定性合成面板上全部执行成功。
- 公式模块只依赖仓库内运行时、NumPy 和 Pandas。
- 指定因子、字段映射、股票代码前导零、缺字段跳过、宽长表输出和未来数据不变性通过测试。

未声明内容：

- 不声明 IC、ICIR、Rank IC 或多空收益有效。
- 不声明信号方向、交易收益或投资可用性。
- 不包含物化生产因子值或历史回测结果。

## 项目状态与风险边界

- **项目状态**：Community Project，未经 QUANTSKILLS 官方审核、认证或背书。
- **数据来源**：仓库只包含 toy data；真实行情与基本面数据由使用者提供并负责许可与合规。
- **公式来源**：参考 Factors Directory 的公开数学定义及其链接的公开文献。
- **核心假设**：输入为日频长表；基本面值已按实际可得时间对齐。
- **已知限制**：数据商口径、单位、复权方式、股票池、交易日历和缺失值规则会影响结果。
- **风险边界**：输出仅为原始公式因子值，不代表预测能力、交易信号、组合收益或生产可用性。
- **用途**：仅供量化研究、教育和方法论参考，不构成投资建议、调仓建议或收益承诺。

## 边界

| 边界 | 说明 |
|---|---|
| Factor Library | 只计算 241 个 Factor Calendar 原始因子值 |
| 无外部 Skill 依赖 | 不依赖 Alpha101/Alpha191 或其他因子 Skill |
| 无 LLM 依赖 | 不调用模型，不读取 API key |
| 无因子评价 | 不计算 IC、ICIR、方向翻转、分组收益或回测收益 |
| 无交易建议 | 不输出投资建议、调仓建议或收益承诺 |

## License

This repository is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).
