# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Transpile ifcopenshell.util and ifcopenshell.api into the @ifcopenshell/util and @ifcopenshell/api packages.

The packages' src/ folders are build output: they are not committed, and are written here from
this checkout's Python source, the rules, the hand-written runtime (ifcopenshell-util/runtime)
and precomputed.json. Needs only PyYAML and Jinja2 (requirements.txt). `--precompute` refreshes
precomputed.json, which needs an installed ifcopenshell close to this checkout.
"""

import argparse
import ast
import json
import shutil
from pathlib import Path

import yaml

from transpile import PACKAGE, Transpiler, build_index, camel, module_name

HERE = Path(__file__).parent
TS = HERE.parent / "ts"
TARGETS = {"util": TS / "ifcopenshell-util", "api": TS / "ifcopenshell-api"}
RUNTIME = TARGETS["util"] / "runtime"
PRECOMPUTED = HERE / "precomputed.json"
HEADER = "// This file was generated with the assistance of an AI coding tool.\n// SPDX-License-Identifier: LGPL-3.0-or-later\n"


def sources():
    for path in sorted(PACKAGE.glob("util/*.py")):
        if path.stem != "__init__":
            yield path, Path(f"{path.stem}.ts")
    for path in sorted(PACKAGE.glob("api/*/*.py")):
        if path.stem != "__init__":
            yield path, Path(path.parent.name) / f"{path.stem}.ts"


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=HERE / "ts.yaml")
    parser.add_argument("--precompute", action="store_true", help=f"only refresh {PRECOMPUTED.name}")
    args = parser.parse_args()
    tracking = yaml.safe_load((HERE / "tracking.yaml").read_text(encoding="utf-8"))
    skip = {name for name, info in tracking["util"].items() if info.get("tier") == "skip"}

    rules = yaml.safe_load(args.rules.read_text(encoding="utf-8"))
    if args.precompute:
        PRECOMPUTED.write_text(json.dumps(precompute(rules), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {PRECOMPUTED}")
        return
    precomputed = json.loads(PRECOMPUTED.read_text(encoding="utf-8"))
    missing = set(rules.get("precomputed", {})) - set(precomputed)
    if missing:
        raise SystemExit(f"{PRECOMPUTED.name} lacks {', '.join(sorted(missing))}; run generate.py --precompute")
    compiler = Transpiler(args.rules, build_index(), precomputed)
    manifests = {scope: {} for scope in TARGETS}
    for target in TARGETS.values():
        shutil.rmtree(target / "src", ignore_errors=True)
        (target / "src").mkdir()
    for runtime in sorted(RUNTIME.glob("*.ts")):
        shutil.copyfile(runtime, TARGETS["util"] / "src" / runtime.name)
    for source_path, relative in sources():
        name = module_name(source_path)
        scope = name.split(".")[0]
        output = TARGETS[scope] / "src" / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        source = source_path.read_text(encoding="utf-8")
        entry = {"source": f"ifcopenshell/{source_path.relative_to(PACKAGE).as_posix()}"}
        if source_path.stem in skip and scope == "util":
            # Not ported, but other modules import it, so its functions exist and throw.
            entry["error"] = "not ported (tier skip)"
            output.write_text(stub_module(source, entry["error"]), encoding="utf-8")
            manifests[scope][relative.with_suffix("").as_posix()] = entry
            continue
        try:
            code = compiler.translate(source, name)
            entry["functions"] = sum(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in ast.parse(source).body)
            entry["stubs"] = {u.split(": ", 1)[0]: u.split(": ", 1)[1] for u in compiler.unsupported}
        except Exception as error:  # Module-level constructs stop the whole file.
            entry["error"] = str(error).splitlines()[0]
            code = stub_module(source, entry["error"])
        output.write_text(code, encoding="utf-8")
        manifests[scope][relative.with_suffix("").as_posix()] = entry

    # Data files that generated code opens next to itself, as the Python modules do.
    data = TARGETS["util"] / "src" / "schema"
    data.mkdir(exist_ok=True)
    for path in sorted((PACKAGE / "util" / "schema").glob("Pset_*.ifc")):
        shutil.copyfile(path, data / path.name)
    for path in sorted((PACKAGE / "util").glob("*.json")):
        shutil.copyfile(path, TARGETS["util"] / "src" / path.name)

    # Each API package re-exports its usecases, as ifcopenshell.api.<package> does.
    for package in sorted({Path(k).parts[0] for k in manifests["api"]}):
        usecases = sorted(Path(k).name for k in manifests["api"] if Path(k).parts[0] == package)
        lines = [f'export {{ {camel(u)} }} from "./{u}.js";' for u in usecases if not u.startswith("_") and u != "settings"]
        lines += [f'export * as {u} from "./{u}.js";' for u in usecases if u == "settings"]
        (TARGETS["api"] / "src" / package / "index.ts").write_text(HEADER + "\n" + "\n".join(lines) + "\n", encoding="utf-8")

    for scope, target in TARGETS.items():
        manifest = manifests[scope]
        (target / "transpile.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        files = len(manifest)
        failed = sum("error" in e for e in manifest.values())
        functions = sum(e.get("functions", 0) for e in manifest.values())
        stubs = sum(len(e.get("stubs", {})) for e in manifest.values())
        print(f"@ifcopenshell/{scope}: {files - failed}/{files} files, {functions - stubs}/{functions} functions translated")


if __name__ == "__main__":
    main()
