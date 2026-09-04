from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .data import (
    load_panel,
    resolve_output_path,
    trim_output,
)
from .factor_compute import compute_factors, default_factor_n_jobs
from .selector import (
    FactorSpec,
    catalog_metadata,
    required_fields,
    resolve_factor_selection,
)


def _load_config(path_value: str | Path) -> tuple[dict[str, Any], Path]:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"input configuration not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("input configuration must be a JSON object")
    return payload, path


def _positive_int(value: object, *, label: str, default: int) -> int:
    if value in (None, ""):
        return default
    parsed = int(value)
    if parsed < 1:
        raise ValueError(f"{label} must be at least 1")
    return parsed


def _boolean(value: object, *, label: str, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ValueError(f"{label} must be a boolean")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_table(frame: pd.DataFrame, path: Path, output_format: str) -> None:
    if output_format == "csv":
        frame.to_csv(path, index=False)
    else:
        frame.to_parquet(path, index=False)


def _wide_output(values: pd.DataFrame) -> pd.DataFrame:
    frame = values.reset_index()
    frame["date"] = frame["date"].dt.strftime("%Y%m%d")
    frame["symbol"] = frame["symbol"].astype(str)
    factor_ids = list(values.columns)
    return frame.loc[:, ["date", "symbol", *factor_ids]]


def _long_output(values: pd.DataFrame) -> pd.DataFrame:
    wide = values.reset_index()
    result = wide.melt(
        id_vars=["symbol", "date"],
        var_name="factor_id",
        value_name="value",
    ).dropna(subset=["value"])
    result = result.rename(columns={"symbol": "instrument_id", "date": "timestamp"})
    result["instrument_id"] = result["instrument_id"].astype(str)
    result["timestamp"] = result["timestamp"].dt.strftime("%Y-%m-%d")
    return result.loc[:, ["instrument_id", "timestamp", "factor_id", "value"]]


def _manifest(specs: list[FactorSpec]) -> dict[str, Any]:
    return {
        "catalog_version": catalog_metadata()["version"],
        "factor_count": len(specs),
        "value_semantics": "raw_formula_output",
        "factors": [
            {
                "factor_id": spec.factor_id,
                "required_fields": list(spec.required_fields),
                "formula_sha256": spec.sha256,
            }
            for spec in specs
        ],
    }


def run_factor_compute(
    input_path: str | Path,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    config, config_path = _load_config(input_path)
    specs = resolve_factor_selection(config)
    fields = required_fields(specs)
    panel, panel_path = load_panel(
        config,
        config_dir=config_path.parent,
        value_fields=fields,
    )

    n_jobs = _positive_int(
        config.get("n_jobs", config.get("workers")),
        label="n_jobs",
        default=default_factor_n_jobs(),
    )
    strict = _boolean(config.get("strict"), label="strict", default=False)
    show_progress = _boolean(
        config.get("show_progress"),
        label="show_progress",
        default=True,
    )
    values, failures = compute_factors(
        panel,
        specs,
        n_jobs=n_jobs,
        strict=strict,
        show_progress=show_progress,
    )
    values = trim_output(values, config)

    output_format = str(config.get("output_format", "csv")).strip().lower()
    if output_format not in {"csv", "parquet"}:
        raise ValueError("output_format must be csv or parquet")
    output_layout = str(config.get("output_layout", "wide")).strip().lower()
    if output_layout not in {"wide", "long", "both"}:
        raise ValueError("output_layout must be wide, long, or both")

    if output_dir is not None:
        cli_target = Path(output_dir).expanduser()
        target = (
            cli_target.resolve()
            if cli_target.is_absolute()
            else (Path.cwd() / cli_target).resolve()
        )
    else:
        target = resolve_output_path(
            config.get("output_dir", "outputs/factor_calendar_compute_example")
        )
    target.mkdir(parents=True, exist_ok=True)
    extension = "csv" if output_format == "csv" else "parquet"
    output_files: dict[str, str] = {}

    if output_layout in {"wide", "both"}:
        path = target / f"factor_calendar_values.{extension}"
        _write_table(_wide_output(values), path, output_format)
        output_files["factor_calendar_values_path"] = str(path)
    if output_layout in {"long", "both"}:
        path = target / f"factor_calendar_panel.{extension}"
        _write_table(_long_output(values), path, output_format)
        output_files["factor_calendar_panel_path"] = str(path)

    effective_config = dict(config)
    effective_config.update(
        {
            "market_data_path": str(panel_path),
            "output_dir": str(target),
            "output_format": output_format,
            "output_layout": output_layout,
            "n_jobs": n_jobs,
            "strict": strict,
            "show_progress": show_progress,
        }
    )
    _write_json(target / "run_config.json", effective_config)
    _write_json(
        target / "skipped_factors.json",
        [failure.as_dict() for failure in failures],
    )
    _write_json(target / "factor_manifest.json", _manifest(specs))

    dates = values.index.get_level_values("date")
    computed_ids = list(values.columns)
    summary = {
        "ok": True,
        "input_path": str(config_path),
        "output_dir": str(target),
        "catalog_version": catalog_metadata()["version"],
        "market_data_row_count": len(panel),
        "symbol_count": int(panel.index.get_level_values("symbol").nunique()),
        "date_range": [
            dates.min().strftime("%Y%m%d"),
            dates.max().strftime("%Y%m%d"),
        ],
        "requested_factor_count": len(specs),
        "computed_factor_count": len(computed_ids),
        "skipped_factor_count": len(failures),
        "observation_count": len(values),
        "date_start": dates.min().strftime("%Y%m%d"),
        "date_end": dates.max().strftime("%Y%m%d"),
        "value_semantics": "raw_formula_output",
        "output_layout": output_layout,
        "output_format": output_format,
        "output_files": output_files,
        "summary_path": str(target / "factor_compute_summary.json"),
        "skipped_factors_path": str(target / "skipped_factors.json"),
        "manifest_path": str(target / "factor_manifest.json"),
        "run_config_path": str(target / "run_config.json"),
        "n_jobs": n_jobs,
    }
    _write_json(target / "factor_compute_summary.json", summary)
    return summary
