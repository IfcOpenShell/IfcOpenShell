<!-- This file was generated with the assistance of an AI coding tool. -->

# Python Ã¢â€ â€™ TypeScript prototype

From the repository root (Python dependencies: `pip install PyYAML Jinja2`):

```powershell
python src/transpiler/transpile.py src/ifcopenshell-python/ifcopenshell/util/unit.py -o src/transpiler/unit.ts
```

The generated TypeScript targets the `ifcopenshell` npm package's
[Core API](https://docs.ifcopenshell.org/output/typescript-api/Core.html).
The caller initializes IfcOpenShell and supplies the file.

The whole module is processed, including top-level data and type aliases.
Currently 27 of `unit.py`'s 33 functions translate. Unsupported functions become
exported throwing stubs, with the first unsupported construct reported to stderr.
Unsupported top-level data aborts translation rather than disappearing.

`transpile.py` parses Python, discovers bindings, matches patterns and renders
Jinja templates. All translation rules, including types, syntax, API names,
imports and data-shape inference, live in `ts.yaml`. There is no preamble or
runtime compatibility library: rules emit native TypeScript operations directly.
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

The unit cache remains a property on the normal `ifcopenshell.File` object.
No utility-specific file type or module augmentation is generated. Properties
missing from the target API may produce TypeScript typing errors; those need
resolution in the source/API rather than synthetic types in the transpiler.
Loops, defaults, keyword calls to local functions, unpacking, comprehensions and
unit conversions are supported. Unknown calls are rejected. Inference and API mappings cover
the patterns in this module, rather than general Python semantics. In particular,
dictionary `.get()` uses `??` for these tables' non-null values, and collection
equality handles the flat numeric tuples used for dimensions.

Remaining stubs: `get_property_unit`, `calculate_unit_scale`, `format_length`,
`is_attr_type`, `iter_element_and_attributes_per_type`, `convert_file_length_units`.
These reach unmapped schema reflection, formatting or external Python modules.
`get_property_table_unit` requires an explicit `ifc_file`; `entity.file` has no mapping yet.

This is a prototype: dynamic locals still use `any`; narrow tuple/literal return
types occasionally need targeted assertions. Literal-union parameters become
strings when the Python body manipulates them as strings. General formatting,
parenthesis cleanup, nested scopes and general imports remain future work.
No Python or WASM code is executed during translation.

Manually verified: 61 calls against Python, all 10 data tables, and IFC graph
smoke checks with JS stand-ins. The emitted code intentionally exposes the
Python file's `units` property, which is absent from the current JS `File` type.
Full type checking also requires generated WASM declarations missing from this
checkout. No test suite was added.


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

## Porting plan and tracking

[PLAN.md](PLAN.md) describes the plan for porting all of `ifcopenshell.util` and
`ifcopenshell.api`, including the testing layers. `python src/transpiler/generate.py`
writes the `src/` of both packages (`src/ts/ifcopenshell-util`, `src/ts/ifcopenshell-api`),
which are build output and not committed; it needs only the packages in `requirements.txt`.
The sections above describe the original single-module prototype. `TRACKING.md` is
written by `python src/transpiler/status.py` from `tracking.yaml` (not committed either).
`precomputed.json` holds the results of the functions listed under `precomputed` in
`ts.yaml`; refresh it with `python src/transpiler/generate.py --precompute`, which needs an
installed ifcopenshell close to this checkout.

## Runtime modules

Python libraries without a direct JS equivalent are ported by hand once, in
`src/ts/ifcopenshell-util/runtime/_*.ts`, and `ts.yaml` maps imports of them there
(`runtime_modules`): `_py.ts` (Python semantics: truthiness, operators, indexing,
`str.format`, ...), `_numpy.ts`, `_datetime.ts`, `_isodate.ts`, `_dateutil.ts`,
`_os.ts` and `_itertools.ts`. `generate.py` copies them into the package's `src/`. Their
behaviour is checked against values computed with Python in
`src/ts/ifcopenshell-util/tests/runtime.test.ts`, and through the parity tests
of the modules that use them.

## Running the tests

The tests live with the packages they test, as in `ifcopenshell-js`:

| Package | Tests | Needs |
|---|---|---|
| `src/ts/ifcopenshell-util` | `tests/runtime.test.ts`: the hand-written runtime (`_py`, `_numpy`, `_datetime`, ...) against values computed with Python | built `ifcopenshell-js` |
| | `tests/parity.test.ts`: replays the calls the Python tests of `ifcopenshell.util` make | also the WASM build and recordings |
| `src/ts/ifcopenshell-api` | `tests/parity.test.ts`: the same for `ifcopenshell.api`, with the replay code of the util package (`tests/parity/replay.ts`) | the WASM build and recordings |

### Once

1. Get a WASM build of IfcOpenShell and point `IFCOPENSHELL_WASM_DIR` at the folder
   containing `ifcopenshell_wasm.wasm`, as for the tests of `ifcopenshell-js`. Either
   download the `ifcopenshell-native-wasm` artifact of the
   `build-ifcopenshell-native-wasm.yml` workflow
   (`gh run download <run id> --repo IfcOpenShell/IfcOpenShell --name ifcopenshell-native-wasm`),
   use `/opt/ifcopenshell-wasm` in the Docker image (see `docker/README.md`), or build it
   with `nix/build-all.py --native-wasm`.
2. Stage it and build the wrapper the generated code imports:

   ```shell
   cd src/ts/ifcopenshell-wasm && npm ci && npm run stage
   cd ../ifcopenshell-js && npm ci && npm run build
   ```

3. Install the generator's dependencies: `pip install -r src/transpiler/requirements.txt`.
   Recording also needs `pytest` and an installed `ifcopenshell` close to this checkout
   (`pip install ifcopenshell pytest`; the numbers in [PLAN.md](PLAN.md) use 0.9.0.post1).

### Each time

```shell
cd src/ts/ifcopenshell-util
npm ci
npm run generate   # writes src/ of both @ifcopenshell/util and @ifcopenshell/api
npm run record     # runs the Python tests of ifcopenshell.util, writes src/transpiler/parity/golden/util.*.json
npm test           # runtime tests, then the replay

cd ../ifcopenshell-api
npm ci
npm run record     # the same for ifcopenshell.api
npm test
```

Neither the generated sources nor the recordings are committed, so run `generate` after
changing the rules, the runtime or the Python source, and `record` after changing the
Python source or its tests. Without `IFCOPENSHELL_WASM_DIR`, or without recordings, the
replay is skipped and only the runtime tests run.

- **One module:** `npm test -- -t util.date` replays one recorded module, and
  `python ../../transpiler/parity/record.py util.date` (from a package folder) records one.
  The modules recorded by default are `DEFAULT_MODULES` in `parity/record.py`.
- **Skipped calls:** a call is skipped, with the reason in its test name, when its Python
  test failed, its function is a stub, its module did not transpile, or its arguments could
  not be recorded. Skips are what is still to be ported.
- **Type check:** `npm run build` in `ifcopenshell-util`, then `npm run typecheck` in
  `ifcopenshell-api`, whose types resolve `@ifcopenshell/util` from the util package's `dist/`.
- **Coverage:** `python src/transpiler/status.py` writes `TRACKING.md`.
