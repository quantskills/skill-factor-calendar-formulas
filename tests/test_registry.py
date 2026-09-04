from __future__ import annotations

import ast

from factor_calendar_runtime.selector import (
    PUBLIC_PREFIX,
    factor_registry,
    list_factor_records,
    resolve_factor_selection,
)

ALLOWED_IMPORTS = {
    "factor_calendar_runtime",
    "factor_calendar_batch10_utils",
    "numpy",
    "pandas",
}


def test_catalog_contains_241_unique_formulas() -> None:
    registry = factor_registry()

    assert len(registry) == 241
    assert len(set(registry)) == 241
    assert all(factor_id.startswith(PUBLIC_PREFIX) for factor_id in registry)
    assert all(spec.path.is_file() for spec in registry.values())
    assert all(len(spec.sha256) == 64 for spec in registry.values())
    assert len(list_factor_records()) == 241


def test_formula_imports_are_self_contained() -> None:
    for spec in factor_registry().values():
        tree = ast.parse(spec.path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        assert imports <= ALLOWED_IMPORTS, (spec.factor_id, imports - ALLOWED_IMPORTS)


def test_selection_accepts_public_and_local_names() -> None:
    selected = resolve_factor_selection(
        {
            "factor_names": [
                "amount_volatility",
                "factor-calendar.book_to_market_ratio",
            ]
        }
    )

    assert [spec.factor_id for spec in selected] == [
        "factor-calendar.amount_volatility",
        "factor-calendar.book_to_market_ratio",
    ]
