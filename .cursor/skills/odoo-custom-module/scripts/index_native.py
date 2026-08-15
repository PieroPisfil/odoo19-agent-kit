#!/usr/bin/env python3
"""Build compact TSV catalogs of native Odoo models (no source bodies)."""

from __future__ import annotations

import ast
import csv
import sys
from pathlib import Path

SKIP_DIR_NAMES = frozenset(
    {
        "i18n",
        "static",
        "tests",
        "doc",
        "lib",
        "__pycache__",
        ".git",
    }
)
SKIP_MODULE_PREFIXES = ("l10n_", "theme_", "hw_", "test_")


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "AGENTS.md").is_file() or (parent / "odoo" / "addons").is_dir():
            return parent
    return Path.cwd()


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def catalog_dir() -> Path:
    return skill_dir() / "catalogs"


def addon_roots(root: Path) -> list[Path]:
    candidates = [root / "odoo" / "addons", root / "odoo" / "odoo" / "addons"]
    return [p for p in candidates if p.is_dir()]


def const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def str_list(node: ast.AST | None) -> list[str]:
    if node is None:
        return []
    if isinstance(node, (ast.List, ast.Tuple)):
        out: list[str] = []
        for elt in node.elts:
            value = const_str(elt)
            if value:
                out.append(value)
        return out
    value = const_str(node)
    return [value] if value else []


def dict_keys(node: ast.AST | None) -> list[str]:
    if not isinstance(node, ast.Dict):
        return []
    keys: list[str] = []
    for key in node.keys:
        value = const_str(key)
        if value:
            keys.append(value)
    return keys


def assign_target_name(target: ast.AST) -> str | None:
    if isinstance(target, ast.Name):
        return target.id
    return None


def class_assigns(class_node: ast.ClassDef) -> dict[str, ast.AST]:
    found: dict[str, ast.AST] = {}
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                name = assign_target_name(target)
                if name in {"_name", "_inherit", "_inherits", "_description"}:
                    found[name] = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
            name = assign_target_name(stmt.target)
            if name in {"_name", "_inherit", "_inherits", "_description"}:
                found[name] = stmt.value
    return found


def method_names(class_node: ast.ClassDef) -> list[str]:
    names: list[str] = []
    for stmt in class_node.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(stmt.name)
    return names


def parse_manifest(path: Path) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    for stmt in tree.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Dict):
            try:
                value = ast.literal_eval(stmt.value)
            except (ValueError, TypeError):
                return {}
            return value if isinstance(value, dict) else {}
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Dict):
            try:
                value = ast.literal_eval(stmt.value)
            except (ValueError, TypeError):
                return {}
            return value if isinstance(value, dict) else {}
    return {}


def iter_module_dirs(addons_root: Path) -> list[Path]:
    modules: list[Path] = []
    for child in sorted(addons_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(SKIP_MODULE_PREFIXES):
            continue
        if not (child / "__manifest__.py").is_file():
            continue
        modules.append(child)
    return modules


def iter_python_files(module_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in module_dir.rglob("*.py"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        files.append(path)
    return files


def extract_models(py_path: Path, module: str, root: Path) -> list[dict[str, str]]:
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8", errors="replace"), filename=str(py_path))
    except SyntaxError:
        return []
    rel = py_path.relative_to(root).as_posix()
    rows: list[dict[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        assigns = class_assigns(node)
        name = const_str(assigns.get("_name"))
        inherit = str_list(assigns.get("_inherit"))
        delegates = dict_keys(assigns.get("_inherits"))
        inherit_from = inherit + [f"delegates:{d}" for d in delegates]
        inherit_joined = ",".join(inherit_from)
        methods = ",".join(method_names(node))
        # `_name` + `_inherit` including the same model is a mixin extension, not the original.
        if name and name not in inherit:
            rows.append(
                {
                    "model": name,
                    "role": "name",
                    "module": module,
                    "class": node.name,
                    "file": rel,
                    "inherit_from": inherit_joined,
                    "methods": methods,
                }
            )
        if name and name in inherit:
            rows.append(
                {
                    "model": name,
                    "role": "inherit",
                    "module": module,
                    "class": node.name,
                    "file": rel,
                    "inherit_from": inherit_joined,
                    "methods": methods,
                }
            )
        elif not name and inherit:
            for target in inherit:
                rows.append(
                    {
                        "model": target,
                        "role": "inherit",
                        "module": module,
                        "class": node.name,
                        "file": rel,
                        "inherit_from": inherit_joined,
                        "methods": methods,
                    }
                )
    return rows


def build_catalogs(root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    model_rows: list[dict[str, str]] = []
    module_rows: list[dict[str, str]] = []
    roots = addon_roots(root)
    if not roots:
        raise SystemExit(
            f"No Odoo addons found under {root / 'odoo'}. Clone Community 19.0 into odoo/ first."
        )
    for addons in roots:
        for module_dir in iter_module_dirs(addons):
            manifest = parse_manifest(module_dir / "__manifest__.py")
            depends = manifest.get("depends") or []
            if not isinstance(depends, list):
                depends = []
            depends_s = ",".join(str(d) for d in depends)
            version = str(manifest.get("version") or "")
            summary = str(manifest.get("summary") or manifest.get("name") or "")
            summary = summary.replace("\t", " ").replace("\n", " ")
            module_rows.append(
                {
                    "module": module_dir.name,
                    "path": module_dir.relative_to(root).as_posix(),
                    "depends": depends_s,
                    "version": version,
                    "summary": summary,
                }
            )
            for py_path in iter_python_files(module_dir):
                model_rows.extend(extract_models(py_path, module_dir.name, root))
    model_rows.sort(key=lambda r: (r["model"], r["role"], r["module"], r["file"]))
    module_rows.sort(key=lambda r: r["module"])
    return model_rows, module_rows


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    root = repo_root()
    out = catalog_dir()
    model_rows, module_rows = build_catalogs(root)
    write_tsv(
        out / "models.tsv",
        ["model", "role", "module", "class", "file", "inherit_from", "methods"],
        model_rows,
    )
    write_tsv(
        out / "modules.tsv",
        ["module", "path", "depends", "version", "summary"],
        module_rows,
    )
    print(f"Wrote {len(model_rows)} model rows -> {out / 'models.tsv'}")
    print(f"Wrote {len(module_rows)} modules -> {out / 'modules.tsv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
