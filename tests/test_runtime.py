from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from factor_calendar_runtime.factor_compute import compute_factors
from factor_calendar_runtime.runtime import run_factor_compute
from factor_calendar_runtime.selector import (
    factor_registry,
    resolve_factor_selection,
)
from pandas.testing import assert_series_equal


def make_full_panel(periods: int = 320, symbol_count: int = 8) -> pd.DataFrame:
    dates = pd.bdate_range("2023-01-02", periods=periods)
    symbols = [f"{value:06d}" for value in range(1, symbol_count + 1)]
    index = pd.MultiIndex.from_product(
        [symbols, dates],
        names=["symbol", "date"],
    )
    day = np.tile(np.arange(len(dates), dtype=float), len(symbols))
    symbol = np.repeat(np.arange(len(symbols), dtype=float), len(dates))
    wave = np.sin(day / 11 + symbol * 0.4)
    close = 10 + symbol * 2 + day * 0.015 + wave * 0.3

    frame = pd.DataFrame(index=index)
    frame["close"] = close
    frame["open"] = close * (1 + 0.002 * np.cos(day / 7 + symbol))
    frame["high"] = np.maximum(frame["open"], frame["close"]) * (1.01 + symbol * 0.0001)
    frame["low"] = np.minimum(frame["open"], frame["close"]) * (0.99 - symbol * 0.0001)
    frame["volume"] = (
        1_000_000 + symbol * 50_000 + day * 1_000 + 20_000 * np.cos(day / 5 + symbol)
    )
    frame["amount"] = frame["close"] * frame["volume"]
    frame["turnover"] = 0.01 + symbol * 0.0005 + 0.002 * (1 + np.sin(day / 9))
    frame["market_cap"] = frame["close"] * (100_000_000 + symbol * 5_000_000)
    frame["accts_payable"] = 1e8 + symbol * 2e6 + day * 2e4
    frame["bs_money_cap"] = 2e8 + symbol * 3e6 + day * 3e4
    frame["bs_total_assets"] = 2e9 + symbol * 2e7 + day * 2e5
    frame["cash_flow_from_operating_activities"] = 2e8 + symbol * 3e6 + day * 1e5
    frame["cost_of_goods_sold"] = 5e8 + symbol * 8e6 + day * 2e5
    frame["current_assets"] = 8e8 + symbol * 9e6 + day * 2e5
    frame["current_liabilities"] = 4e8 + symbol * 5e6 + day * 1e5
    frame["equity_parent_company"] = 1.1e9 + symbol * 1e7 + day * 1e5
    frame["financing_expense"] = 2e7 + symbol * 2e5 + day * 1e4
    frame["net_fixed_assets"] = 6e8 + symbol * 5e6 + day * 1e5
    frame["net_profit_parent"] = 1e8 + symbol * 2e6 + day * 5e4
    frame["operating_revenue"] = 1e9 + symbol * 1e7 + day * 4e5
    frame["pe_ratio_ttm"] = 12 + symbol * 0.8 + 0.2 * np.sin(day / 17)
    frame["sp_ratio_ttm"] = 1.2 + symbol * 0.05 + 0.02 * np.cos(day / 13)
    frame["total_assets"] = frame["bs_total_assets"]
    frame["total_equity"] = 1.2e9 + symbol * 1.2e7 + day * 1e5
    frame["total_liabilities"] = frame["total_assets"] - frame["total_equity"]
    return frame


def test_complete_catalog_executes() -> None:
    panel = make_full_panel()
    specs = list(factor_registry().values())

    values, failures = compute_factors(
        panel,
        specs,
        n_jobs=4,
        strict=True,
        show_progress=False,
    )

    assert failures == []
    assert values.shape == (len(panel), 241)
    assert int(values.notna().any().sum()) >= 230


def test_appending_future_rows_does_not_change_history() -> None:
    panel = make_full_panel(periods=40, symbol_count=3)
    specs = resolve_factor_selection({"factor_names": ["amount_volatility"]})
    historical, failures = compute_factors(
        panel,
        specs,
        show_progress=False,
        strict=True,
    )
    assert failures == []

    extended = make_full_panel(periods=45, symbol_count=3)
    with_future, failures = compute_factors(
        extended,
        specs,
        show_progress=False,
        strict=True,
    )
    assert failures == []
    assert_series_equal(
        historical.iloc[:, 0],
        with_future.reindex(historical.index).iloc[:, 0],
    )


def test_column_mapping_and_output_contract(tmp_path: Path) -> None:
    dates = pd.bdate_range("2024-01-02", periods=8)
    rows = [
        {
            "trade_day": date.strftime("%Y%m%d"),
            "instrument": symbol,
            "trading_amount": 1_000_000 + day * scale,
        }
        for day, date in enumerate(dates)
        for symbol, scale in (("000001", 1000), ("000002", 1800))
    ]
    panel_path = tmp_path / "panel.csv"
    pd.DataFrame(rows).to_csv(panel_path, index=False)
    config_path = tmp_path / "compute.json"
    config_path.write_text(
        json.dumps(
            {
                "market_data_path": "panel.csv",
                "factor_names": ["amount_volatility"],
                "column_mapping": {
                    "date": "trade_day",
                    "symbol": "instrument",
                    "amount": "trading_amount",
                },
                "output_layout": "both",
                "output_format": "csv",
                "strict": True,
                "show_progress": False,
            }
        ),
        encoding="utf-8",
    )

    summary = run_factor_compute(config_path, output_dir=tmp_path / "output")

    assert summary["ok"] is True
    assert summary["computed_factor_count"] == 1
    assert (tmp_path / "output" / "factor_calendar_values.csv").is_file()
    assert (tmp_path / "output" / "factor_calendar_panel.csv").is_file()
    assert (tmp_path / "output" / "factor_manifest.json").is_file()
    wide = pd.read_csv(
        tmp_path / "output" / "factor_calendar_values.csv",
        dtype={"symbol": "string"},
    )
    assert wide.columns[:2].tolist() == ["date", "symbol"]
    assert wide["symbol"].str.len().eq(6).all()


def test_missing_fields_are_skipped_in_non_strict_mode() -> None:
    panel = make_full_panel(periods=20, symbol_count=2).loc[:, ["close"]]
    specs = resolve_factor_selection(
        {"factor_names": ["short_term_reversal", "book_to_market_ratio"]}
    )

    values, failures = compute_factors(
        panel,
        specs,
        strict=False,
        show_progress=False,
    )

    assert list(values) == ["factor-calendar.short_term_reversal"]
    assert [failure.factor_id for failure in failures] == [
        "factor-calendar.book_to_market_ratio"
    ]
