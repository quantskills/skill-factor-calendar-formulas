# Validation Notes

## Scope

- This Skill is a deterministic factor-library computation tool.
- It does not call an LLM and does not require API keys.
- Supported inputs are long-form CSV and Parquet; outputs may be wide or long CSV and Parquet.
- verified means formula migration integrity, complete-catalog runtime execution, and CLI contract tests. It does not mean predictive-performance or trading-performance verification.

## Formula Validation

- The catalog contains 241 unique factor-calendar IDs and 241 matching native modules.
- Migrated formula modules are checked by SHA-256 against the source formula snapshot.
- Every native module imports only the bundled runtime, NumPy, Pandas, or the bundled helper module.
- All 241 formulas execute without exceptions on a deterministic 320-business-day, eight-symbol synthetic panel.
- Selected-factor runs, column mapping, leading-zero symbols, output layouts, missing-field skips, and future-row invariance are covered by tests.

## Known Boundaries

- Rolling formulas require enough pre-window history; start_date and end_date only trim output after calculation.
- Some formulas need fields not normally present in an OHLCV-only panel and will be skipped when strict is false.
- Vendor definitions, units, adjustment methods, accounting conventions, and missing-value policies can change formula values.
- Synthetic execution establishes software behavior, not IC, returns, robustness, or future profitability.
