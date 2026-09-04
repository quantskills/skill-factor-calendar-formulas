from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .selector import FactorSpec, load_formula_class


@dataclass(frozen=True)
class FormulaFailure:
    factor_id: str
    error_type: str
    error: str

    def as_dict(self) -> dict[str, str]:
        return {
            "factor_id": self.factor_id,
            "error_type": self.error_type,
            "error": self.error,
        }


def default_factor_n_jobs() -> int:
    """Return the available logical CPU count for factor computation."""
    return max(1, os.cpu_count() or 1)


def _calculate_one(panel: pd.DataFrame, spec: FactorSpec) -> pd.Series:
    formula_class = load_formula_class(spec)
    inputs = {field: panel[field] for field in spec.required_fields}
    result = formula_class().calculate(inputs)
    if hasattr(result, "series"):
        result = result.series
    if isinstance(result, pd.DataFrame):
        if result.shape[1] != 1:
            raise ValueError("formula returned multiple columns")
        result = result.iloc[:, 0]
    if not isinstance(result, pd.Series):
        result = pd.Series(result, index=panel.index[: len(result)])
    if result.index.has_duplicates:
        raise ValueError("formula returned a duplicate index")
    if not isinstance(result.index, pd.MultiIndex):
        if len(result) != len(panel):
            raise ValueError("formula returned an incompatible result length")
        result = pd.Series(result.to_numpy(), index=panel.index)
    numeric = pd.to_numeric(result.reindex(panel.index), errors="coerce")
    return numeric.astype("float64").replace([np.inf, -np.inf], np.nan)


def compute_factors(
    panel: pd.DataFrame,
    specs: Sequence[FactorSpec],
    *,
    n_jobs: int = 1,
    strict: bool = False,
    show_progress: bool = True,
) -> tuple[pd.DataFrame, list[FormulaFailure]]:
    if n_jobs < 1:
        raise ValueError("n_jobs must be at least 1")

    available: list[FactorSpec] = []
    failures: list[FormulaFailure] = []
    columns = set(panel.columns)
    for spec in specs:
        missing = sorted(set(spec.required_fields) - columns)
        if missing:
            failures.append(
                FormulaFailure(
                    factor_id=spec.factor_id,
                    error_type="MissingFields",
                    error=f"missing canonical fields: {missing}",
                )
            )
        else:
            available.append(spec)

    if strict and failures:
        raise ValueError(failures[0].error)

    importable: list[FactorSpec] = []
    for spec in available:
        try:
            load_formula_class(spec)
            importable.append(spec)
        except Exception as exc:
            failures.append(
                FormulaFailure(spec.factor_id, type(exc).__name__, str(exc))
            )
            if strict:
                raise RuntimeError(f"{spec.factor_id} import failed: {exc}") from exc

    results: dict[str, pd.Series] = {}
    completed = 0
    total = len(importable)
    workers = min(n_jobs, max(1, total))

    def finish(
        spec: FactorSpec, series: pd.Series | None, exc: Exception | None
    ) -> None:
        nonlocal completed
        completed += 1
        if exc is None and series is not None:
            results[spec.factor_id] = series
        else:
            assert exc is not None
            failures.append(
                FormulaFailure(spec.factor_id, type(exc).__name__, str(exc))
            )
        if show_progress:
            state = "ok" if exc is None else "failed"
            print(
                f"[{completed}/{total}] {state} {spec.factor_id}",
                file=sys.stderr,
                flush=True,
            )

    if n_jobs == 1:
        for spec in importable:
            try:
                finish(spec, _calculate_one(panel, spec), None)
            except Exception as exc:
                finish(spec, None, exc)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(_calculate_one, panel, spec): spec
                for spec in importable
            }
            for future in as_completed(futures):
                spec = futures[future]
                try:
                    finish(spec, future.result(), None)
                except Exception as exc:
                    finish(spec, None, exc)

    if strict and failures:
        first = failures[0]
        raise RuntimeError(f"{first.factor_id} failed: {first.error}")

    ordered_ids = [spec.factor_id for spec in specs if spec.factor_id in results]
    values = pd.DataFrame(
        {factor_id: results[factor_id] for factor_id in ordered_ids},
        index=panel.index,
    )
    return values, failures
