#!/usr/bin/env python3
"""Look up a native Odoo model in the compact catalog (paths + method names only)."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from index_native import catalog_dir


def load_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(
            f"Missing {path}. Run:\n"
            "  python .cursor/skills/odoo-custom-module/scripts/index_native.py"
        )
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def pick_definition(name_rows: list[dict[str, str]], model: str) -> dict[str, str]:
    if len(name_rows) == 1:
        return name_rows[0]
    prefix = model.split(".")[0]
    by_module = [r for r in name_rows if r["module"] == prefix]
    if by_module:
        return sorted(by_module, key=lambda r: (len(r["file"]), r["file"]))[0]
    if prefix in {"res", "ir", "base"}:
        base = [r for r in name_rows if r["module"] == "base"]
        if base:
            return sorted(base, key=lambda r: r["file"])[0]
    return sorted(name_rows, key=lambda r: (0 if r["module"] == "base" else 1, r["file"]))[0]


def format_methods(raw: str, limit: int = 20) -> str:
    names = [n for n in raw.split(",") if n]
    if not names:
        return "-"
    preferred = [n for n in names if n in {"create", "write", "unlink", "copy"} or n.startswith("action_")]
    rest = [n for n in names if n not in preferred]
    chosen = (preferred + rest)[:limit]
    extra = len(names) - len(chosen)
    suffix = f" (+{extra} more; Grep FILE)" if extra > 0 else ""
    return ",".join(chosen) + suffix


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a native Odoo model to file + method names.")
    parser.add_argument("model", help="Technical name, e.g. sale.order")
    parser.add_argument("-v", "--verbose", action="store_true", help="List every extender file")
    args = parser.parse_args()
    query = args.model.strip()
    catalogs = catalog_dir()
    models = load_tsv(catalogs / "models.tsv")
    modules = {row["module"]: row for row in load_tsv(catalogs / "modules.tsv")}

    name_rows = [r for r in models if r["model"] == query and r["role"] == "name"]
    inherit_rows = [r for r in models if r["model"] == query and r["role"] == "inherit"]

    if not name_rows and not inherit_rows:
        hints = sorted({r["model"] for r in models if r["model"].startswith(query)})[:8]
        extra = f"\nSimilar: {', '.join(hints)}" if hints else ""
        raise SystemExit(f"No catalog hit for {query!r}.{extra}")

    print(f"MODEL\t{query}")
    if name_rows:
        primary = pick_definition(name_rows, query)
        mod = modules.get(primary["module"], {})
        print(f"DEFINED_IN\t{primary['module']}")
        print(f"CLASS\t{primary['class']}")
        print(f"FILE\t{primary['file']}")
        print(f"INHERIT_FROM\t{primary.get('inherit_from') or '-'}")
        print(f"DEPENDS\t{mod.get('depends') or '-'}")
        print(f"METHODS\t{format_methods(primary.get('methods') or '')}")
        others = [r for r in name_rows if r is not primary]
        if others and args.verbose:
            print("OTHER_DEFINITIONS")
            for row in others:
                print(f"\t{row['module']}\t{row['class']}\t{row['file']}")
    else:
        print("DEFINED_IN\t(not in indexed addons; check l10n/theme or a mixin-only inherit)")

    extender_modules = []
    seen: set[str] = set()
    for row in inherit_rows:
        if row["module"] in seen:
            continue
        seen.add(row["module"])
        extender_modules.append(row)
    print(f"EXTENDED_BY_COUNT\t{len(extender_modules)}")
    if args.verbose:
        print("EXTENDED_BY")
        if extender_modules:
            for row in extender_modules:
                print(f"\t{row['module']}\t{row['class']}\t{row['file']}")
        else:
            print("\t-")
    else:
        preview = ",".join(r["module"] for r in extender_modules[:12])
        if len(extender_modules) > 12:
            preview += f" (+{len(extender_modules) - 12})"
        print(f"EXTENDED_BY\t{preview or '-'}")

    print("NEXT\tRead FILE around CLASS (line range). Do not @ the addon folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
