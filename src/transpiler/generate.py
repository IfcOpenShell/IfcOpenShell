# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Transpile ifcopenshell.util and ifcopenshell.api into the ifcopenshell npm package.

Writes src/python/util and src/python/api of src/ts/ifcopenshell-js, which are build output
and not committed, from this checkout's Python source, the rules and precomputed.json.
src/python/transpile.json lists each module's untranslated functions; `--report` also prints
coverage per module and the most frequent unsupported constructs. Needs only PyYAML and
Jinja2 (requirements.txt). `--precompute` refreshes precomputed.json, which needs an
installed ifcopenshell close to this checkout.
"""

import argparse
import ast
import collections
import json
import re
import shutil
from pathlib import Path

import yaml

from transpile import PACKAGE, Transpiler, build_index, camel, module_name

HERE = Path(__file__).parent
OUTPUT = HERE.parent / "ts" / "ifcopenshell-js" / "src" / "python"
PRECOMPUTED = HERE / "precomputed.json"
# Documentation and developer scripts, not ported; other modules import them, so their functions throw.
SKIP = {"doc", "ifc4x3dev_scrape_data_for_docs", "generate_pset_templates", "profiler"}
HEADER = "// This file was generated with the assistance of an AI coding tool.\n// SPDX-License-Identifier: LGPL-3.0-or-later\n"


def sources():
    for path in sorted(PACKAGE.glob("util/*.py")):
        if path.stem != "__init__":
            yield path, Path("util") / f"{path.stem}.ts"
    for path in sorted(PACKAGE.glob("api/*/*.py")):
        if path.stem != "__init__":
            yield path, Path("api") / path.parent.name / f"{path.stem}.ts"


def stub_module(source, reason):
    """Every top-level function throws, so other modules still import and type-check against it."""
    names = list(dict.fromkeys(n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)))
    message = json.dumps(f"Not transpiled: {reason}")
    return HEADER + "".join(
        f"\nexport function {camel(name)}(..._args: any[]): any {{\n  throw new Error({message});\n}}\n" for name in names
    )


def precompute(rules):
    """Run the functions listed under `precomputed` in the rules, from this checkout's source."""
    import importlib.util

    import ifcopenshell  # The installed build provides the wrapper the source needs.

    results = {}
    for qualified, arguments in rules.get("precomputed", {}).items():
        module_path, name = qualified.rsplit(".", 1)
        spec = importlib.util.spec_from_file_location(f"_precompute.{module_path}", PACKAGE.joinpath(*module_path.split(".")).with_suffix(".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        results[qualified] = {argument: getattr(module, name)(argument) for argument in arguments}
    return results


def report(manifest):
    """Coverage per util module and api package, and the most frequent unsupported constructs."""
    totals = collections.defaultdict(lambda: [0, 0])
    blockers = collections.Counter()
    for key, entry in manifest.items():
        group = key if key.startswith("util/") else "/".join(key.split("/")[:2])
        functions = entry["functions"]
        stubs = functions if "error" in entry else len(entry.get("stubs", {}))
        totals[group][0] += functions - stubs
        totals[group][1] += functions
        for reason in [entry["error"]] if "error" in entry else entry.get("stubs", {}).values():
            blockers[re.sub(r"^No \w+ rule at line \d+: ", "", reason)[:80]] += 1
    for group, (done, total) in sorted(totals.items()):
        if done < total:
            print(f"  {group}: {done}/{total}")
    print("Most frequent unsupported constructs:")
    for reason, count in blockers.most_common(15):
        print(f"  {count:4} {reason}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=HERE / "ts.yaml")
    parser.add_argument("--precompute", action="store_true", help=f"only refresh {PRECOMPUTED.name}")
    parser.add_argument("--report", action="store_true", help="also print coverage per module and top blockers")
    args = parser.parse_args()

    rules = yaml.safe_load(args.rules.read_text(encoding="utf-8"))
    if args.precompute:
        PRECOMPUTED.write_text(json.dumps(precompute(rules), sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {PRECOMPUTED}")
        return
    precomputed = json.loads(PRECOMPUTED.read_text(encoding="utf-8"))
    missing = set(rules.get("precomputed", {})) - set(precomputed)
    if missing:
        raise SystemExit(f"{PRECOMPUTED.name} lacks {', '.join(sorted(missing))}; run generate.py --precompute")
    compiler = Transpiler(args.rules, build_index(), precomputed)
    manifest = {}
    modules = set()  # API modules that are not a usecase (no function of their name), as settings.
    for scope in ("util", "api"):
        shutil.rmtree(OUTPUT / scope, ignore_errors=True)
    for source_path, relative in sources():
        name = module_name(source_path)
        output = OUTPUT / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        source = source_path.read_text(encoding="utf-8")
        if name.startswith("api.") and source_path.stem not in {n.name for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}:
            modules.add(relative.with_suffix("").as_posix())
        entry = {
            "source": f"ifcopenshell/{source_path.relative_to(PACKAGE).as_posix()}",
            "functions": sum(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in ast.parse(source).body),
        }
        if name.startswith("util.") and source_path.stem in SKIP:
            entry["error"] = "not ported"
            code = stub_module(source, entry["error"])
        else:
            try:
                code = compiler.translate(source, name)
                entry["stubs"] = {u.split(": ", 1)[0]: u.split(": ", 1)[1] for u in compiler.unsupported}
            except Exception as error:  # Module-level constructs stop the whole file.
                entry["error"] = str(error).splitlines()[0]
                code = stub_module(source, entry["error"])
        output.write_text(code, encoding="utf-8")
        manifest[relative.with_suffix("").as_posix()] = entry

    # Data files that generated code opens next to itself, as the Python modules do.
    (OUTPUT / "util" / "schema").mkdir()
    for path in sorted((PACKAGE / "util" / "schema").glob("Pset_*.ifc")):
        shutil.copyfile(path, OUTPUT / "util" / "schema" / path.name)
    for path in sorted((PACKAGE / "util").glob("*.json")):
        shutil.copyfile(path, OUTPUT / "util" / path.name)

    # Each API package re-exports its usecases and other modules, as ifcopenshell.api.<package> does.
    for package in sorted({k.split("/")[1] for k in manifest if k.startswith("api/")}):
        usecases = sorted(k.split("/")[2] for k in manifest if k.startswith(f"api/{package}/") and not k.split("/")[2].startswith("_"))
        lines = [f'export {{ {camel(u)} }} from "./{u}.js";' for u in usecases if f"api/{package}/{u}" not in modules]
        lines += [f'export * as {u} from "./{u}.js";' for u in usecases if f"api/{package}/{u}" in modules]
        (OUTPUT / "api" / package / "index.ts").write_text(HEADER + "\n" + "\n".join(lines) + "\n", encoding="utf-8")

    (OUTPUT / "transpile.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for scope in ("util", "api"):
        entries = [e for k, e in manifest.items() if k.startswith(f"{scope}/")]
        functions = sum(e["functions"] for e in entries)
        stubs = sum(e["functions"] if "error" in e else len(e.get("stubs", {})) for e in entries)
        failed = sum("error" in e for e in entries)
        print(f"ifcopenshell.{scope}: {len(entries) - failed}/{len(entries)} files, {functions - stubs}/{functions} functions translated")
    if args.report:
        report(manifest)


if __name__ == "__main__":
    main()
