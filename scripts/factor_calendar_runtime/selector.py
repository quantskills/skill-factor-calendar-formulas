from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from .factor_formulas_utils import Factor

RUNTIME_ROOT = Path(__file__).resolve().parent
FORMULA_ROOT = RUNTIME_ROOT / "factor_calendar_native"
CATALOG_PATH = RUNTIME_ROOT / "catalog.json"
PUBLIC_PREFIX = "factor-calendar."
_FORMULA_CLASSES: dict[str, type[Factor]] = {}


@dataclass(frozen=True)
class FactorSpec:
    factor_id: str
    local_name: str
    path: Path
    class_name: str
    required_fields: tuple[str, ...]
    sha256: str

    def public_record(self) -> dict[str, Any]:
        return {
            "factor_id": self.factor_id,
            "required_fields": list(self.required_fields),
            "formula_sha256": self.sha256,
        }


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _required_fields(tree: ast.AST) -> tuple[str, ...]:
    fields: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "factors"
        ):
            value = _literal_string(node.slice)
            if value:
                fields.add(value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "series"
            and len(node.args) > 1
        ):
            value = _literal_string(node.args[1])
            if value:
                fields.add(value)
    return tuple(sorted(fields))


def _factor_class_name(tree: ast.Module, factor_id: str) -> str:
    classes: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if any(
            isinstance(base, ast.Name) and base.id == "Factor" for base in node.bases
        ):
            classes.append(node.name)
    if len(classes) != 1:
        raise RuntimeError(
            f"{factor_id} must define exactly one direct Factor subclass"
        )
    return classes[0]


def catalog_metadata() -> dict[str, Any]:
    payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if payload.get("source") != "factor-calendar":
        raise RuntimeError("catalog source must be factor-calendar")
    factor_ids = payload.get("factor_ids")
    if not isinstance(factor_ids, list) or not factor_ids:
        raise RuntimeError("catalog must contain a non-empty factor_ids list")
    if len(factor_ids) != len(set(factor_ids)):
        raise RuntimeError("catalog contains duplicate factor IDs")
    if payload.get("factor_count") != len(factor_ids):
        raise RuntimeError("catalog factor_count does not match factor_ids")
    if any(not str(value).startswith(PUBLIC_PREFIX) for value in factor_ids):
        raise RuntimeError("catalog factor IDs must use the factor-calendar prefix")
    return payload


@lru_cache(maxsize=1)
def factor_registry() -> dict[str, FactorSpec]:
    payload = catalog_metadata()
    registry: dict[str, FactorSpec] = {}
    for raw_factor_id in payload["factor_ids"]:
        factor_id = str(raw_factor_id)
        local_name = factor_id.removeprefix(PUBLIC_PREFIX)
        path = FORMULA_ROOT / f"{local_name}.py"
        if not path.is_file():
            raise RuntimeError(f"formula file not found for {factor_id}")
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        registry[factor_id] = FactorSpec(
            factor_id=factor_id,
            local_name=local_name,
            path=path,
            class_name=_factor_class_name(tree, factor_id),
            required_fields=_required_fields(tree),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    return registry


def _normalize_name(value: object) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("factor names must not be empty")
    if text.startswith(PUBLIC_PREFIX):
        return text
    return f"{PUBLIC_PREFIX}{text}"


def _name_list(value: Any) -> list[str]:
    if value in (None, "", []):
        return []
    if isinstance(value, str):
        if value.strip().lower() in {"all", "*"}:
            return []
        return [value]
    if not isinstance(value, Sequence):
        raise ValueError("factor names must be a string or sequence")
    return [str(item) for item in value]


def resolve_factor_selection(config: dict[str, Any]) -> list[FactorSpec]:
    registry = factor_registry()
    raw_names = _name_list(config.get("factor_names"))
    selected_ids = (
        list(registry)
        if not raw_names
        else [_normalize_name(value) for value in raw_names]
    )
    excluded = {
        _normalize_name(value)
        for value in _name_list(config.get("exclude_factor_names"))
    }
    selected_ids = [value for value in selected_ids if value not in excluded]
    if not selected_ids:
        raise ValueError("no factors remain after selection")
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("factor_names contains duplicates")
    unknown = sorted(set(selected_ids) - set(registry))
    if unknown:
        raise ValueError(f"unknown factors: {unknown}")
    return [registry[factor_id] for factor_id in selected_ids]


def required_fields(specs: Sequence[FactorSpec]) -> tuple[str, ...]:
    return tuple(sorted({field for spec in specs for field in spec.required_fields}))


def load_formula_class(spec: FactorSpec) -> type[Factor]:
    existing = _FORMULA_CLASSES.get(spec.factor_id)
    if existing is not None:
        return existing
    formula_root = str(FORMULA_ROOT)
    if formula_root not in sys.path:
        sys.path.insert(0, formula_root)
    module_name = f"_factor_calendar_formula_{spec.local_name}"
    module_spec = importlib.util.spec_from_file_location(module_name, spec.path)
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"cannot load formula for {spec.factor_id}")
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    try:
        module_spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    formula_class = getattr(module, spec.class_name, None)
    if not isinstance(formula_class, type) or not issubclass(formula_class, Factor):
        raise RuntimeError(f"invalid formula class for {spec.factor_id}")
    _FORMULA_CLASSES[spec.factor_id] = formula_class
    return formula_class


def list_factor_records() -> list[dict[str, Any]]:
    return [spec.public_record() for spec in factor_registry().values()]
