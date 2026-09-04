from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd

SKILL_ROOT = Path(__file__).resolve().parents[2]
KEY_FIELDS = ("date", "symbol")


def resolve_input_path(value: object, *, config_dir: Path) -> Path:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("market_data_path is required")
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path
    config_relative = (config_dir / path).resolve()
    if config_relative.exists():
        return config_relative
    return (SKILL_ROOT / path).resolve()


def resolve_output_path(value: object) -> Path:
    raw = str(value or "outputs/factor-calendar").strip()
    path = Path(raw).expanduser()
    return path if path.is_absolute() else (SKILL_ROOT / path).resolve()


def _normalize_dates(values: pd.Series, *, label: str) -> pd.Series:
    text = values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    dates = pd.to_datetime(text, errors="coerce")
    if dates.isna().any():
        count = int(dates.isna().sum())
        raise ValueError(f"{label} contains {count} invalid date values")
    if getattr(dates.dt, "tz", None) is not None:
        dates = dates.dt.tz_localize(None)
    return dates.dt.normalize()


def normalize_date_value(value: object, *, label: str) -> pd.Timestamp | None:
    text = str(value or "").strip()
    if not text:
        return None
    date = pd.to_datetime(text)
    if date.tzinfo is not None:
        date = date.tz_localize(None)
    return date.normalize()


def _load_table(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"market_data_path not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, dtype="string", low_memory=False)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError("market_data_path must use .csv, .parquet, or .pq")


def _apply_column_mapping(
    frame: pd.DataFrame,
    mapping: object,
) -> pd.DataFrame:
    if mapping in (None, {}):
        return frame.copy()
    if not isinstance(mapping, dict):
        raise ValueError("column_mapping must be an object")
    result = frame.copy()
    for canonical, source in mapping.items():
        canonical_name = str(canonical).strip()
        source_name = str(source).strip()
        if not canonical_name or not source_name:
            raise ValueError("column_mapping keys and values must not be empty")
        if source_name not in frame:
            raise ValueError(f"column_mapping source column not found: {source_name}")
        result[canonical_name] = frame[source_name]
    return result


def load_panel(
    config: dict[str, Any],
    *,
    config_dir: Path,
    value_fields: Sequence[str],
) -> tuple[pd.DataFrame, Path]:
    path_value = config.get(
        "market_data_path",
        config.get("market_data_csv_path", config.get("panel_path")),
    )
    path = resolve_input_path(path_value, config_dir=config_dir)
    frame = _apply_column_mapping(_load_table(path), config.get("column_mapping"))
    missing_keys = sorted(set(KEY_FIELDS) - set(frame.columns))
    if missing_keys:
        raise ValueError(f"panel is missing required key fields: {missing_keys}")
    available_fields = sorted(set(value_fields).intersection(frame.columns))
    frame = frame.loc[:, [*KEY_FIELDS, *available_fields]].copy()
    frame["date"] = _normalize_dates(frame["date"], label="panel date")
    if frame["symbol"].isna().any():
        raise ValueError("panel symbol contains missing values")
    frame["symbol"] = frame["symbol"].astype("string").str.strip()
    if frame["symbol"].eq("").any():
        raise ValueError("panel symbol contains empty values")
    if frame.duplicated(list(KEY_FIELDS)).any():
        raise ValueError("panel contains duplicate (date, symbol) rows")

    for field in available_fields:
        numeric = pd.to_numeric(frame[field], errors="coerce")
        invalid = frame[field].notna() & numeric.isna()
        if invalid.any():
            raise ValueError(
                f"panel field {field} contains {int(invalid.sum())} non-numeric values"
            )
        frame[field] = numeric.astype("float64")

    load_start = normalize_date_value(
        config.get("load_start_date") or config.get("load_start"),
        label="load_start_date",
    )
    load_end = normalize_date_value(
        config.get("load_end_date") or config.get("load_end"),
        label="load_end_date",
    )
    if load_start is not None:
        frame = frame.loc[frame["date"] >= load_start]
    if load_end is not None:
        frame = frame.loc[frame["date"] <= load_end]

    symbols = config.get("symbols") or []
    if isinstance(symbols, str):
        symbols = [symbols]
    if symbols:
        symbol_set = {str(value).strip() for value in symbols}
        frame = frame.loc[frame["symbol"].isin(symbol_set)]
    if frame.empty:
        raise ValueError("no panel rows remain after input filters")

    panel = frame.sort_values(["symbol", "date"], kind="stable").set_index(
        ["symbol", "date"]
    )
    return panel, path


def trim_output(
    values: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    dates = values.index.get_level_values("date")
    start = normalize_date_value(
        config.get("start_date") or config.get("output_start"),
        label="start_date",
    )
    end = normalize_date_value(
        config.get("end_date") or config.get("output_end"),
        label="end_date",
    )
    mask = pd.Series(True, index=values.index)
    if start is not None:
        mask &= dates >= start
    if end is not None:
        mask &= dates <= end
    result = values.loc[mask.to_numpy()]
    if result.empty:
        raise ValueError("no factor rows remain after output date filters")
    return result
