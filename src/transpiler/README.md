<!-- This file was generated with the assistance of an AI coding tool. -->

# Python to TypeScript transpiler

Transpiles `ifcopenshell.util` and `ifcopenshell.api` into the `ifcopenshell` npm
package (`src/ts/ifcopenshell-js`), as `ifcopenshell/util/<module>` and
`ifcopenshell/api/<package>`. [PLAN.md](PLAN.md) describes the design, the status and
what remains. From the repository root (Python dependencies: `requirements.txt`):

```shell
python src/transpiler/generate.py            # write src/ts/ifcopenshell-js/src/python/{util,api}
python src/transpiler/generate.py --report   # also print coverage and the top unsupported constructs
python src/transpiler/transpile.py src/ifcopenshell-python/ifcopenshell/util/unit.py   # one module to stdout
```

The generated code is build output and not committed. Unsupported functions become
throwing stubs, listed with the first unsupported construct in
`src/ts/ifcopenshell-js/src/python/transpile.json`. Unsupported module-level code makes
the whole file a module of throwing functions rather than disappearing.
`precomputed.json` holds the results of the functions listed under `precomputed` in
`ts.yaml`; refresh it with `generate.py --precompute`, which needs an installed
ifcopenshell close to this checkout.

## How it works

`transpile.py` parses Python, discovers bindings, matches patterns and renders
Jinja templates. All translation rules, including types, syntax, API names,
imports and data-shape inference, live in `ts.yaml`. Rules emit native TypeScript operations where the types are known, and
call the runtime modules below where Python semantics need it.
Pass `--rules another.yaml` to use a different rule set. Treat rule files as trusted code.

Patterns use Python AST field names, with `node` specifying the AST class.
`$name` captures a field; lists match exactly; omitted fields are unconstrained.
Rules run in order, first match wins. `where` optionally restricts a captured
receiver to a Python parameter annotation. `when` is a Jinja expression that
can further restrict a match. Templates use `emit` for recursive translation,
`type` for annotations, and `literal` for JSON literals. `kind` queries the
YAML inference rules. The engine propagates those results through bindings;
it does not choose target-language operations. YAML tables such as `methods`
and `operators` are also available to templates and conditions.

For example, the comprehension rule translates this restricted expression:

```python
[u for u in ifc_file.by_type("IfcNamedUnit") if u.UnitType == unit_type]
```

```typescript
ifc_file.byType("IfcNamedUnit").filter((u: any) => (u.UnitType === unit_type))
```

Specific comparison rules select `.includes()` for strings/arrays and
`Object.hasOwn()` for dictionaries. Tuple equality uses `.every()`. Dictionary
iteration uses `Object.keys()`/`Object.entries()`, and `range` loops use a native
counter. `condition` and `iterable` template filters select rules with the
matching `context`; these handle empty arrays/dictionaries at their use sites.
Scalar short-circuit expressions use `&&`/`||`; optional collections use `??`.

Select the exploratory C++ target explicitly:

```powershell
python src/transpiler/transpile.py src/ifcopenshell-python/ifcopenshell/util/unit.py --rules src/transpiler/cpp.yaml -o src/transpiler/unit.cpp
```

`ts.yaml` remains the default. `cpp.yaml` uses the same engine, with its own
indented rules and copies of the source data-shape inference rules. No inheritance
from the TypeScript target is required.

The C++20 sketch uses `std::map`, `std::vector`, `std::array`, `std::optional`,
range loops, structured bindings, and immediately invoked lambdas to materialize
comprehensions. Boost string algorithms keep string rewrites concise. IFC mappings
reference this checkout's `ifcopenshell::file`, `instances_by_type`, value-like
`express::entity`, and `get_value<T>` interfaces.

`unit.cpp` is a design artifact, not a compilable implementation. It renders bodies
for 21 of the 33 functions and emits throwing stubs for the rest. TODOs expose
unresolved local declaration scopes, optional unwrapping, container conversions,
recursive variants and operand-valued short-circuiting. Forward declarations,
string/enum decoding, attribute writes, caches and schema-specific casts also
need decisions. Dynamic attribute types currently come from a small explicit
YAML table. No C++ compilation or runtime validation was attempted.

## Runtime modules

Python libraries without a direct JS equivalent are ported by hand once, in
`src/ts/ifcopenshell-js/src/python/_*.ts`, and `ts.yaml` maps imports of them there
(`runtime_modules`): `_py.ts` (Python semantics: truthiness, operators, indexing,
`str.format`, ...), `_numpy.ts`, `_datetime.ts`, `_isodate.ts`, `_dateutil.ts`,
`_os.ts` and `_itertools.ts`. They contain what the generated code uses, and are
checked against values computed with Python in
`src/ts/ifcopenshell-js/tests/python/runtime.test.ts`.

## Running the tests

The tests are part of `src/ts/ifcopenshell-js` and run against its build (`dist/`):

| Test | Checks | Needs |
|---|---|---|
| `tests/python/runtime.test.ts` | the runtime modules against values computed with Python | a build |
| `tests/python/parity.test.ts` | replays every call the Python tests of the recorded util and api modules make | also the generated code, the WASM build and recordings |

### Once

1. Get a WASM build of IfcOpenShell and point `IFCOPENSHELL_WASM_DIR` at the folder
   containing `ifcopenshell_wasm.wasm`, as for the other tests of `ifcopenshell-js`.
   Either download the `ifcopenshell-native-wasm` artifact of the
   `build-ifcopenshell-native-wasm.yml` workflow
   (`gh run download <run id> --repo IfcOpenShell/IfcOpenShell --name ifcopenshell-native-wasm`),
   use `/opt/ifcopenshell-wasm` in the Docker image (see `docker/README.md`), or build it
   with `nix/build-all.py --native-wasm`. Then stage it:
   `cd src/ts/ifcopenshell-wasm && npm ci && npm run stage`.
2. Install the generator's dependencies: `pip install -r src/transpiler/requirements.txt`.
   Recording also needs `pytest` and an installed `ifcopenshell` close to this checkout
   (`pip install ifcopenshell pytest`; the numbers in [PLAN.md](PLAN.md) use 0.9.0.post1).

### Each time

```shell
cd src/ts/ifcopenshell-js
npm ci
npm run generate   # transpile into src/python/util and src/python/api
npm run build      # type-checks and compiles the generated code into dist/python
npm run record     # run the Python tests, write src/transpiler/parity/golden/*.json
npm test           # all tests of the package, including tests/python
```

Neither the generated code nor the recordings are committed, so run `generate` and `build`
after changing the rules, the runtime or the Python source, and `record` after changing the
Python source or its tests. Without `IFCOPENSHELL_WASM_DIR`, or without recordings, the
replay is skipped.

- **Only these tests:** `npx vitest run tests/python`.
- **One module:** `npx vitest run tests/python -t util.date` replays one recorded module, and
  `python ../../transpiler/parity/record.py util.date` records one. The modules recorded by
  default are `DEFAULT_MODULES` in `parity/record.py`.
- **Skipped calls:** a call is skipped, with the reason in its test name, when its Python
  test failed, its function is a stub, its module did not transpile, or its arguments could
  not be recorded. Skips are what is still to be ported.
