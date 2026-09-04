# Input Schema

The CLI accepts a JSON file:

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json
```

Optional output override:

```bash
python scripts/compute_factor_calendar_factors.py --input examples/compute_input.json --output outputs/my_run
```

## Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| market_data_path | string | yes | Long-form CSV or Parquet path. Relative paths are resolved from the input JSON directory, then the Skill root. |
| output_dir | string | no | Output directory. Relative paths in JSON are resolved from the Skill root. |
| factor_names | list/string | no | Empty means all 241 formulas. Accepts local names or qualified factor-calendar names. |
| exclude_factor_names | list/string | no | Formulas to exclude after selection. |
| column_mapping | object | no | Maps canonical field names to source columns. |
| load_start_date | string | no | Inclusive history-load start date. |
| load_end_date | string | no | Inclusive history-load end date. |
| start_date | string | no | Inclusive output start date applied after factor calculation. |
| end_date | string | no | Inclusive output end date applied after factor calculation. |
| symbols | list[string] | no | Optional stock-universe filter. Empty means all symbols. |
| output_format | string | no | csv or parquet. Default is csv. |
| output_layout | string | no | wide, long, or both. Default is wide. |
| n_jobs | integer | no | Formula worker count. Default is the machine logical CPU count. |
| strict | boolean | no | Stop on a missing input or formula failure. Default is false. |
| show_progress | boolean | no | Print formula progress. Default is true. |

For compatibility, market_data_csv_path and panel_path are accepted as aliases of market_data_path. load_start, load_end, output_start, and output_end are accepted as aliases of the corresponding date fields.

## Panel Keys

Every input panel must include:

```text
date, symbol
```

Dates may use YYYYMMDD, YYYY-MM-DD, or another Pandas-compatible date representation. Each date-symbol pair must be unique. Symbols are preserved as strings, including leading zeros.

## Canonical Value Fields

Selected formulas require a subset of:

```text
open, high, low, close, volume, amount, turnover, market_cap,
accts_payable, bs_money_cap, bs_total_assets,
cash_flow_from_operating_activities, cost_of_goods_sold,
current_assets, current_liabilities, equity_parent_company,
financing_expense, net_fixed_assets, net_profit_parent,
operating_revenue, pe_ratio_ttm, sp_ratio_ttm, total_assets,
total_equity, total_liabilities
```

The selected formula requirements are recorded in factor_manifest.json. Missing inputs are written to skipped_factors.json unless strict is true.

## Column Mapping

Map canonical names to source columns without rewriting the source file:

```json
{
  "column_mapping": {
    "date": "trade_date",
    "symbol": "instrument",
    "market_cap": "total_market_value"
  }
}
```

Fundamental values must already be aligned to the date on which they became available. The runtime does not infer announcement dates.
