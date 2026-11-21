# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Record golden parity data by running the existing Python tests.

The modules being ported are loaded from this checkout's source, the rest of
ifcopenshell (wrapper, fixture-building APIs) from the installed package. Every
call the tests make into a recorded module is captured with the input file
snapshot, arguments, return value and resulting file changes, and written to
golden/<module>.json for tests/python in src/ts/ifcopenshell-js to replay.
"""

import argparse
import datetime
import functools
import hashlib
import importlib.util
import inspect
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
PYTHON_ROOT = HERE.parent.parent / "ifcopenshell-python"
SOURCE = PYTHON_ROOT / "ifcopenshell"
# Tier 1 util modules and api-core packages (see the tiers in PLAN.md).
DEFAULT_MODULES = [
    *(f"util.{m}" for m in ["alignment", "attribute", "brick", "classification", "constraint", "element", "file", "fm"]),
    *(f"util.{m}" for m in ["pset", "resource", "schema", "system", "type", "unit"]),
    *(f"api.{m}" for m in ["aggregate", "attribute", "owner", "pset", "root", "spatial", "type", "unit"]),
    # Dates and numpy (tiers 2 and 3).
    *(f"util.{m}" for m in ["cost", "date", "geolocation", "placement"]),
    *(f"api.{m}" for m in ["control", "cost", "georeference", "grid", "library", "profile", "project", "sequence"]),
]
# Python-side state kept on the file object rather than in the IFC data.
FILE_STATE = ["units"]
# Values that legitimately differ between runs or between the Python and JS builds.
MASKED = {"GlobalId": "$guid", "CreationDate": "$time", "LastModifiedDate": "$time", "Version": "$version"}
# Set from the current time by cost and sequence usecases (IfcLocalTime components in IFC2X3).
MASKED.update({k: "$time" for k in ("UpdateDate", "StartTime", "HourComponent", "MinuteComponent", "SecondComponent")})

# Import the installed binary build before pytest puts the source tree on sys.path.
sys.path = [p for p in sys.path if Path(p or ".").resolve() not in (PYTHON_ROOT.resolve(), HERE.resolve())]
import ifcopenshell  # noqa: E402
import ifcopenshell.ifcopenshell_wrapper  # noqa: E402
import pytest  # noqa: E402


class Unserializable(Exception):
    pass


def overlay(name):
    """Load ifcopenshell.<name> from this checkout's source in place of the installed module."""
    relative = SOURCE.joinpath(*name.split("."))
    is_package = relative.is_dir()
    path = relative / "__init__.py" if is_package else relative.with_suffix(".py")
    full = f"ifcopenshell.{name}"
    spec = importlib.util.spec_from_file_location(
        full, path, submodule_search_locations=[str(relative)] if is_package else None
    )
    module = importlib.util.module_from_spec(spec)
    for stale in [name for name in sys.modules if name.startswith(f"{full}.")]:
        del sys.modules[stale]  # Submodules of the installed package.
    sys.modules[full] = module
    spec.loader.exec_module(module)
    parent, _, child = full.rpartition(".")
    importlib.import_module(parent)
    setattr(sys.modules[parent], child, module)
    return module


@functools.cache
def set_attributes(schema, ifc_class):
    """Names of the attributes declared as SET aggregates."""
    declaration = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema).declaration_by_name(ifc_class).as_entity()
    return {
        a.name()
        for a in declaration.all_attributes()
        if (aggregate := a.type_of_attribute().as_aggregation_type()) and aggregate.type_of_aggregation_string() == "set"
    }


def owner_mode():
    """Which owner settings the Python tests left active: test/bootstrap.py variants or the defaults."""
    settings = sys.modules.get("ifcopenshell.api.owner.settings")
    qualname = getattr(getattr(settings, "get_user", None), "__qualname__", "")
    if qualname.startswith("IFC2X3."):
        return "create"  # Creates a user and application when missing.
    if "<lambda>" in qualname:
        return "existing"  # The first existing user and application, or None.
    return "default"


def file_key(f):
    return hash(f)  # Wrappers of one native file are distinct objects with equal hashes.


class Call:
    """Serializes one call; files are referenced by index into self.files."""

    def __init__(self):
        self.files = []

    def file_index(self, f):
        key = file_key(f)
        for i, existing in enumerate(self.files):
            if file_key(existing) == key:
                return i
        self.files.append(f)
        return len(self.files) - 1

    def value(self, v, in_args=True):
        if v is None or isinstance(v, (bool, str)):
            return v
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return v if math.isfinite(v) else {"$float": repr(v)}
        if isinstance(v, ifcopenshell.file):
            return {"$file": self.file_index(v)}
        if isinstance(v, ifcopenshell.entity_instance):
            if v.id() == 0:
                return {"$type": v.is_a(), "value": self.value(v.wrappedValue, in_args)}
            ref = {"#": v.id(), "type": v.is_a()}
            if in_args:
                ref["$f"] = self.file_index(v.file)
            return ref
        if isinstance(v, tuple) and hasattr(v, "_fields"):
            return {"$fields": list(v._fields), "$tuple": [self.value(x, in_args) for x in v]}
        if isinstance(v, (list, tuple)):
            return [self.value(x, in_args) for x in v]
        if isinstance(v, (set, frozenset)):
            return {"$set": [self.value(x, in_args) for x in v]}
        if isinstance(v, dict):
            return {"$dict": [[self.value(k, in_args), self.value(x, in_args)] for k, x in v.items()]}
        if isinstance(v, datetime.datetime):
            return {"$datetime": v.isoformat()}
        if isinstance(v, datetime.date):
            return {"$date": v.isoformat()}
        if isinstance(v, datetime.time):
            return {"$time": v.isoformat()}
        if isinstance(v, datetime.timedelta):
            return {"$timedelta": [v.days, v.seconds, v.microseconds]}
        if type(v).__name__ == "Duration" and hasattr(v, "tdelta"):  # isodate
            return {"$duration": [float(v.years), float(v.months), v.tdelta.days, v.tdelta.seconds, v.tdelta.microseconds]}
        if type(v).__name__ == "ndarray":
            return {"$ndarray": self.value(v.tolist(), in_args)}
        if hasattr(v, "tolist"):  # numpy scalars
            return self.value(v.tolist(), in_args)
        if hasattr(v, "numerator") and hasattr(v, "denominator"):  # Fraction
            return float(v)
        raise Unserializable(type(v).__name__)

    def graph(self, f):
        """Every entity's flat attributes, with non-deterministic values masked and SETs unordered."""
        entities = []
        for entity in sorted(f, key=lambda e: e.id()):
            info = entity.get_info(include_identifier=True, recursive=False)
            sets = set_attributes(f.schema_identifier, entity.is_a())
            entities.append(
                {
                    k: (
                        MASKED[k]
                        if k in MASKED and x is not None
                        else {"$set": sorted(self.value(list(x), False), key=json.dumps)}
                        if k in sets and isinstance(x, (list, tuple))
                        else self.value(x, False)
                    )
                    for k, x in info.items()
                }
            )
        return entities

    def changes(self, before_text, after):
        """Entities added or modified by a call, and ids removed, relative to the snapshot."""
        before = {e["id"]: e for e in self.graph(ifcopenshell.file.from_string(before_text))}
        current = {e["id"]: e for e in self.graph(after)}
        return {
            "changed": [e for i, e in current.items() if before.get(i) != e],
            "removed": sorted(set(before) - set(current)),
        }

    def state(self, f, in_args):
        return {name: self.value(getattr(f, name), in_args) for name in FILE_STATE if hasattr(f, name)}


class Recorder:
    def __init__(self, modules):
        self.modules = modules
        self.depth = 0
        self.test = None
        self.calls = []
        self.tests = {m: [] for m in modules}
        self.snapshots = {m: {} for m in modules}

    def wrap(self, module_name, module):
        for name, function in list(vars(module).items()):
            if not inspect.isfunction(function):
                continue
            if module_name.startswith("api."):
                # Usecases are re-wrapped with listeners by wrap_usecases, which hides
                # their signature; take it from the function in the usecase submodule.
                usecase = getattr(sys.modules.get(f"{module.__name__}.{name}"), name, None)
                if usecase is None:
                    continue
                signature = inspect.signature(usecase)
            elif function.__module__ == module.__name__:
                signature = inspect.signature(function)
            else:
                continue
            setattr(module, name, self.wrapper(module_name, name, function, signature))

    def wrapper(self, module_name, name, function, signature):
        def recorded(*args, **kwargs):
            if self.depth or self.test is None or kwargs.get("should_run_listeners") is False:
                return function(*args, **kwargs)
            entry = {"module": module_name, "function": name}
            call = Call()
            try:
                bound = signature.bind(*args, **kwargs)
                # Same convention as the generated code: required parameters are positional,
                # parameters with defaults and keyword-only parameters go into an options object.
                positional, options = [], {}
                for parameter in signature.parameters.values():
                    if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                        if parameter.name in bound.arguments:
                            raise Unserializable(f"*{parameter.name}")
                    elif parameter.kind != parameter.KEYWORD_ONLY and parameter.default is parameter.empty:
                        positional.append(call.value(bound.arguments[parameter.name]))
                    elif parameter.name in bound.arguments:
                        options[parameter.name] = call.value(bound.arguments[parameter.name])
                entry["args"] = positional
                if options:
                    entry["options"] = options
                before = [f.to_string() for f in call.files]
                entry["files"] = [self.snapshot(module_name, s) for s in before]
                entry["state"] = [call.state(f, True) for f in call.files]
                entry["max_ids"] = [f.get_max_id() for f in call.files]
                entry["owner"] = owner_mode()
            except Exception as error:  # Unserializable values, or files that cannot be snapshotted.
                entry = {"module": module_name, "function": name, "skip": f"unserializable argument: {error}"}
                self.calls.append(entry)
                return self.call(function, args, kwargs)[0]
            result, error = self.call(function, args, kwargs)
            try:
                if error is not None:
                    entry["raises"] = type(error).__name__
                else:
                    entry["expected"] = call.value(result, in_args=False)
                entry["after"] = [
                    {"state": call.state(f, False), **({"changes": call.changes(text, f)} if f.to_string() != text else {})}
                    for f, text in zip(call.files, before)
                ]
            except Exception as unserializable:
                entry = {"module": module_name, "function": name, "skip": f"unserializable result: {unserializable}"}
            self.calls.append(entry)
            if error is not None:
                raise error
            return result

        recorded.__wrapped__ = function
        return recorded

    def call(self, function, args, kwargs):
        self.depth += 1
        try:
            return function(*args, **kwargs), None
        except Exception as error:
            return None, error
        finally:
            self.depth -= 1

    def snapshot(self, module_name, text):
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
        self.snapshots[module_name][digest] = text
        return digest

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item):
        self.test, self.calls, self.outcome = item.nodeid, [], "passed"
        yield
        for module_name in self.modules:
            calls = [{k: v for k, v in c.items() if k != "module"} for c in self.calls if c["module"] == module_name]
            if calls:
                self.tests[module_name].append({"test": self.test, "outcome": self.outcome, "calls": calls})
        self.test = None

    def pytest_runtest_logreport(self, report):
        if report.failed:
            self.outcome = "failed"
        elif report.skipped and self.outcome == "passed":
            self.outcome = "skipped"


def test_paths(module_name):
    scope, name = module_name.split(".")
    path = PYTHON_ROOT / "test" / scope / (f"test_{name}.py" if scope == "util" else name)
    return [str(path)] if path.exists() else []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="*", default=DEFAULT_MODULES, help="for example util.unit api.root")
    parser.add_argument("-k", help="pytest -k expression")
    args = parser.parse_args()

    recorder = Recorder(args.modules)
    # Load all of util and api from this checkout, so recorded modules and the code they
    # call agree; keep the installed version of any module that does not import here.
    skipped = []
    candidates = [f"util.{p.stem}" for p in sorted(SOURCE.glob("util/*.py")) if p.stem != "__init__"]
    candidates += [f"api.{p.name}" for p in sorted(SOURCE.glob("api/*")) if (p / "__init__.py").exists()]
    for module_name in candidates:
        try:
            overlay(module_name)
        except Exception as error:
            skipped.append(f"{module_name} ({type(error).__name__}: {error})")
    for module_name in args.modules:
        recorder.wrap(module_name, sys.modules[f"ifcopenshell.{module_name}"])
    for line in skipped:
        print(f"Using installed ifcopenshell.{line}")
    paths = sorted({p for m in DEFAULT_MODULES + args.modules for p in test_paths(m) if m in args.modules})
    pytest_args = ["-q", "-p", "no:cacheprovider", "--rootdir", str(PYTHON_ROOT), *paths]
    if args.k:
        pytest_args += ["-k", args.k]
    pytest.main(pytest_args, plugins=[recorder])

    (HERE / "golden").mkdir(exist_ok=True)
    for module_name in args.modules:
        tests = recorder.tests[module_name]
        calls = [c for t in tests for c in t["calls"]]
        # Snapshots share most of their STEP lines; store each line once.
        index = {}
        files = {
            digest: [index.setdefault(line, len(index)) for line in text.split("\n")]
            for digest, text in recorder.snapshots[module_name].items()
        }
        golden = {
            "module": module_name,
            "ifcopenshell": ifcopenshell.version,
            "lines": list(index),
            "files": files,
            "tests": tests,
        }
        path = HERE / "golden" / f"{module_name}.json"
        path.write_text(json.dumps(golden, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
        skipped = sum("skip" in c for c in calls)
        print(f"{module_name}: {len(tests)} tests, {len(calls)} calls ({skipped} unserializable) -> {path.name}")


if __name__ == "__main__":
    main()
