# Output Contract

The Skill writes outputs under output_dir.

## Files

| File | Description |
| --- | --- |
| factor_calendar_values.csv or .parquet | Wide factor values. Present for wide or both output. |
| factor_calendar_panel.csv or .parquet | Long factor values. Present for long or both output. |
| factor_compute_summary.json | Run summary with counts, date range, output paths, and worker count. |
| skipped_factors.json | Formulas skipped because of missing fields, import errors, or calculation errors. |
| factor_manifest.json | Selected factor IDs, required fields, and formula SHA-256 hashes. |
| run_config.json | Effective configuration used for the run. |

## Wide Layout

```text
date,symbol,factor-calendar.amount_volatility,...
```

Each row is one date-symbol observation and each factor is one column. Warm-up periods remain NaN.

## Long Layout

```text
instrument_id,timestamp,factor_id,value
```

Rows with unavailable values are omitted from the long layout.

## Skipped Factor Record

```json
{
  "factor_id": "factor-calendar.book_to_market_ratio",
  "error_type": "MissingFields",
  "error": "missing canonical fields: ['market_cap']"
}
```

Skipped formulas are omitted from the factor-value output. A completed non-strict run can therefore have skipped_factor_count greater than zero.

## Value Semantics

Outputs are raw formula values. The runtime does not apply empirical direction, winsorization, cross-sectional standardization, industry neutralization, IC evaluation, or a backtest unless the formula definition itself contains that operation.
