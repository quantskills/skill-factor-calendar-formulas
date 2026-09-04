# skill-factor-calendar-formulas

[简体中文](README.md) | **English**

> Factor Calendar formula library: compute 241 raw daily factor values from long-form market and point-in-time fundamental data.

<p align="center">
  <img alt="library" src="https://img.shields.io/badge/library-Factor%20Calendar-blue">
  <img alt="factors" src="https://img.shields.io/badge/factors-241-brightgreen">
  <img alt="type" src="https://img.shields.io/badge/type-factor--library-blue">
  <img alt="platform" src="https://img.shields.io/badge/platform-Codex-9cf">
  <img alt="status" src="https://img.shields.io/badge/status-stable-brightgreen">
  <img alt="validation" src="https://img.shields.io/badge/validation-L3%20verified-success">
  <img alt="license" src="https://img.shields.io/badge/license-GPLv3-blue">
</p>

skill-factor-calendar-formulas is an independent formula-library Skill for computing market, liquidity, sentiment, and fundamental factors documented by [Factors Directory](https://factors.directory/en).

This repository is suitable for:

- Batch generation of 241 Factor Calendar formulas
- Building factor matrices from daily market and point-in-time fundamental panels
- Preparing data for downstream factor evaluation, selection, model training, or backtesting
- Triggering deterministic factor computation workflows from Codex conversations

This repository only computes raw factor values. It does not call LLMs, read API keys, calculate IC or ICIR, orient signals, run backtests, or provide trading recommendations.

## Repository Contents

| Library | Count | Output file | Description |
|---|---:|---|---|
| Factor Calendar | 241 | factor_calendar_values.csv | Market, liquidity, sentiment, and fundamental formulas |
| Factor Calendar Long | 241 | factor_calendar_panel.csv | Optional standard long-form output |

Each formula has a stable ID such as factor-calendar.amount_volatility. Formula modules are bundled in a native directory and require no other factor Skill at runtime.

When inputs are missing, affected formulas are recorded in skipped_factors.json instead of stopping a non-strict run.

## Repository Structure

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

## Data Requirements

Input is a long-form CSV or Parquet file with one security-date observation per row.

Required keys:

```text
date, symbol
```

Market fields are required according to the selected formulas:

```text
open, high, low, close, volume, amount, turnover, market_cap
```

Fundamental fields are required according to the selected formulas:

```text
accts_payable, bs_money_cap, bs_total_assets,
cash_flow_from_operating_activities, cost_of_goods_sold,
current_assets, current_liabilities, equity_parent_company,
financing_expense, net_fixed_assets, net_profit_parent,
operating_revenue, pe_ratio_ttm, sp_ratio_ttm,
total_assets, total_equity, total_liabilities
```

Runtime rules:

| Field / rule | Description |
|---|---|
| date | Accepts YYYYMMDD, YYYY-MM-DD, or another parseable date |
| symbol | Treated as a string, preserving leading zeros |
| column_mapping | Maps source columns to canonical fields |
| load_start_date / load_end_date | Controls history loaded for formula calculation |
| start_date / end_date | Trims the output after formula calculation |
| Missing formula field | Skips the formula in non-strict mode and stops in strict mode |

Financial data must be aligned to actual availability dates before use. The runtime does not infer announcement dates.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the example config:

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json
```

Override the output directory:

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json --output outputs/my_factor_run
```

--output overrides output_dir in the input JSON.

## Input Config

See [examples/compute_input.json](examples/compute_input.json).

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

Core fields:

| Field | Type | Description |
|---|---|---|
| market_data_path | string | Long-form CSV or Parquet; relative paths resolve from the input JSON directory and then the Skill root |
| output_dir | string | Output directory; relative JSON paths resolve from the Skill root |
| factor_names | list/string | Empty computes all 241 formulas; full IDs and short names are supported |
| exclude_factor_names | list/string | Removes formulas after selection |
| column_mapping | object | Canonical-field to source-column mapping |
| load_start_date / load_end_date | string | Optional inclusive history-load range |
| start_date / end_date | string | Optional inclusive output range |
| symbols | list[string] | Optional universe; empty means all symbols |
| output_format | string | csv or parquet |
| output_layout | string | wide, long, or both |
| n_jobs | integer | Worker count; defaults to the logical CPU count |
| strict | bool | Stops on missing fields or formula failures |
| show_progress | bool | Prints formula progress |

## Factor Selection

Compute all formulas:

```json
{
  "factor_names": []
}
```

Compute selected formulas:

```json
{
  "factor_names": [
    "amount_volatility",
    "factor-calendar.book_to_market_ratio"
  ]
}
```

Exclude a formula:

```json
{
  "factor_names": [],
  "exclude_factor_names": [
    "factor-calendar.news_volume"
  ]
}
```

## Output Files

The run writes outputs under output_dir:

```text
outputs/factor_calendar_compute_example/
├── factor_calendar_values.csv
├── factor_calendar_panel.csv
├── factor_compute_summary.json
├── skipped_factors.json
├── factor_manifest.json
└── run_config.json
```

| File | Description |
|---|---|
| factor_calendar_values.csv or .parquet | Wide values, generated for wide or both output |
| factor_calendar_panel.csv or .parquet | Standard long values, generated for long or both output |
| factor_compute_summary.json | Input, output, date range, factor counts, and skipped count |
| skipped_factors.json | Missing-field, import, or calculation failures |
| factor_manifest.json | Factor IDs, required fields, and formula SHA-256 hashes |
| run_config.json | Effective run configuration |

Wide layout:

```text
date,symbol,factor-calendar.amount_volatility,...
```

Long layout:

```text
instrument_id,timestamp,factor_id,value
```

## Large-Sample Recommendations

A full-market, long-range, 241-factor run can create substantial memory and IO pressure. Recommended practice:

- Start with a short range and a small formula subset.
- Keep rolling-window warm-up data through load_start_date and trim results with start_date.
- Do not blindly set n_jobs to the machine maximum; more workers increase memory pressure.
- Run fundamental and market-only formulas separately to reduce the fields loaded at once.

## Validation Scope

The current validation level is L3 verified. Here, verified means migration integrity, complete-catalog runtime execution, and CLI contract validation. It does not mean predictive or trading performance validation.

Verified scope:

- The catalog contains 241 unique IDs and 241 matching native formula modules.
- All 241 formulas execute on a deterministic 320-business-day, eight-symbol synthetic panel.
- Formula modules import only the bundled runtime, NumPy, Pandas, or the bundled helper.
- Selected formulas, column mapping, leading-zero symbols, missing-field skips, output layouts, and future-row invariance are tested.

Not claimed:

- No claim about IC, ICIR, Rank IC, or long-short returns.
- No claim about signal direction, trading performance, or investment usability.
- No materialized production factor values or historical backtest results are included.

## Project Status and Risk Boundaries

- **Project status**: Community Project, not officially reviewed, certified, or endorsed by QUANTSKILLS.
- **Data source**: The repository includes toy data only. Users provide real market and fundamental data and remain responsible for licensing and compliance.
- **Formula source**: Public mathematical definitions and linked public literature documented by Factors Directory.
- **Core assumptions**: Input is daily long-form data and fundamental fields are point-in-time aligned.
- **Known limitations**: Vendor conventions, units, price adjustment, universe, calendar, and missing-value rules affect results.
- **Risk boundary**: Outputs are raw formula values and do not imply predictive power, trading signals, portfolio returns, or production readiness.
- **Use**: For quantitative research, education, and methodology reference only. Not investment advice, rebalance advice, or a return guarantee.

## Boundaries

| Boundary | Description |
|---|---|
| Factor Library | Computes 241 raw Factor Calendar values only |
| No external Skill dependency | Does not require Alpha101/Alpha191 or another factor Skill |
| No LLM dependency | Does not call models or read API keys |
| No factor evaluation | Does not compute IC, ICIR, direction, group returns, or backtest returns |
| No trading advice | Does not provide investment advice, rebalance recommendations, or performance guarantees |

## License

This repository is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).
