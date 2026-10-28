

# Porting `ifcopenshell.util` and `ifcopenshell.api` to TypeScript

## Goal

Ship `ifcopenshell.util` and `ifcopenshell.api` in the `ifcopenshell` npm package
(`src/ts/ifcopenshell-js`), generated from the Python sources by `transpile.py`.
Python stays the source of truth: the TypeScript is regenerated on every change,
never edited by hand. Modules that cannot be expressed as reusable rules are
ported manually and tracked the same way.

Progress is tracked in `TRACKING.md`, written by `status.py` (not committed).

## Scope

Measured by `status.py` on the current checkout:


| Scope | Size                                                      | Python tests            |
| ----- | --------------------------------------------------------- | ----------------------- |
| util  | 29 modules, ~14.7k lines, 383 functions/classes           | 21 files in `test/util` |
| api   | 35 packages, 385 files, ~39k lines, 531 functions/classes | 234 files in `test/api` |


The api calls util heavily (`util.element` 383 references, `util.unit` 92,
`util.date` 72, `util.representation` 59) and itself (329 api files call
other api functions). Porting must therefore go bottom-up.

## Principles

1. **Rules over modules.** A new construct gets a general rule in `ts.yaml`.
  If a module mostly needs rules nothing else uses, port it by hand instead.
2. **No silent gaps.** Unsupported functions stay throwing stubs with a reason;
  unsupported module-level code fails the run. `TRACKING.md` reports both.
3. **Fix the bindings, not the transpiler.** Missing JS API (schema reflection,
  `entity.file`, `get_total_inverses`, ...) is added to the WASM bindings or
   `src/ts/ifcopenshell-js`, not faked in generated code.
4. **Every stage is tested automatically.** A module only advances a stage when
  the corresponding check passes in CI.



## Decisions (milestone 1, done)

| Topic | Decision |
|---|---|
| Packages | `@ifcopenshell/util` (`src/ts/ifcopenshell-util`) and `@ifcopenshell/api` (`src/ts/ifcopenshell-api`), with `ifcopenshell` as a peer dependency. One import path per Python module: `@ifcopenshell/util/unit`, `@ifcopenshell/api/root`. |
| Naming | camelCase functions and module data (`getProjectUnit`, `unitNames`); CONSTANT_CASE and `_private` names are kept. Locals keep their Python names; JS reserved words get a trailing `_`. |
| Arguments | Required parameters stay positional; parameters with defaults and keyword-only parameters go into a trailing options object with camelCase keys, as in the core package (`getInfo({ recursive })`). |
| Cross-module calls | A project-wide index of util and api functions resolves `ifcopenshell.util.x.f(...)`, `from ... import f` and local calls, and binds their arguments with Python semantics. Imports are generated: `./element.js` within util, `@ifcopenshell/util/element` from api, `../owner/index.js` between api packages. |
| Classes | Module classes (the `Usecase` pattern) become TS classes; `self.method()` and calls on local instances bind against the method signature. |
| Runtime | `src/ts/ifcopenshell-util/runtime/_py.ts`, hand-written: Python truthiness, `len`, `in`, `remove` and `pop`, used only where a value's type cannot be inferred. Generators become functions returning arrays. |
| Core fixes | In `ifcopenshell` (JS): one canonical wrapper per entity (so `===`, `Set` and `Map` follow Python entity equality), `entity.file()`, iterating and indexing entities, `entity.walk`, positional `file.create(cls, [...])`, `ifcopenshell.guid`, `File.units`, `schemaByName("IFC4X3")`. |
| Overridable modules | `ifcopenshell.api.owner.settings` gets an `overrides` object, since Python users assign to its functions. |
| Output | The `src/` of both packages and their `transpile.json` (stubs and module-level errors) are build output of `generate.py` and are not committed. Only the inputs are: the Python source, `ts.yaml`, the runtime in `ifcopenshell-util/runtime/`, and `precomputed.json`. `generate.py` needs only PyYAML and Jinja2 (`requirements.txt`); the npm publish workflow runs it before building the packages. |
| Typing | Python public annotations become TS types; locals are `any`. Generated packages compile with `strict: false`, as Python does not track None. |

## Decisions (milestone 6: runtime modules)

| Topic | Decision |
|---|---|
| Runtime modules | `runtime_modules` in `ts.yaml` maps a Python module to a hand-written TS module in `@ifcopenshell/util`: `datetime` → `_datetime.ts`, `isodate` → `_isodate.ts`, `dateutil` → `_dateutil.ts`, `numpy` → `_numpy.ts`, `os` → `_os.ts`, `itertools` → `_itertools.ts`. `import x as y` and `from x import z` resolve to that module's members in camelCase (`np.zeros_like` is `np.zerosLike`); keyword arguments become a trailing options object, as everywhere else. `math` maps onto `Math` through `math_functions`. |
| Python data model | Arrays and dates overload operators, so `+ - * / // % ** @`, unary `-`, `==` and subscripts dispatch at runtime (`py.add`, `py.getitem`, ...) to `__add__`/`__radd__`, `__getitem__` and so on. This applies to values inferred as `ndarray`/`pyobject`, and to values of unknown type in modules that import an overloading module; elsewhere the generated code is unchanged. |
| numpy | `NDArray` stores data with shape, strides and offset, so basic indexing and slicing return views, as in numpy (`for axis in axes: axis[:2] = ...` writes into `axes`). Broadcasting, integer and boolean array indices, `np.newaxis`, and the ~70 functions the Python code calls. JS has no numpy scalars: functions returning a scalar return a JS number. |
| Dates | `date`, `datetime`, `time`, `timedelta` and fixed-offset `timezone` follow Python's arithmetic, comparison (`valueOf`), `str()`, `isoformat()` and `strftime()`. Naive datetimes are local time, as in Python. `isodate` durations and `dateutil.parser` (ISO plus common day/month/year forms) are ported from the installed versions. Classes are callable without `new`. |
| Data files | `json.load(open(path))`, `with open(path) as f` and `os.path` read through `ifcopenshell.readResource`, which reads from Node's file system or from bytes registered with `registerResource()`. The module directory (`os.path.dirname(__file__)`) is a `file:` URL. `generate.py` copies `util/*.json` next to the generated modules. |
| Python constructs | Dataclasses (constructor from fields, `field(default_factory=...)`, `asdict`, `Cls(**kwargs)` via `fromKwargs`), classmethods (static methods with `cls` bound to the class), context managers (`__enter__`/`__exit__` in try/finally), TypedDicts (object types), `*args`, star-arguments filling optional parameters, `str.format` with format specs, `zip`, `iter`/`next`, `slice`, `divmod`, `reversed`, `deque`, `min`/`max` with Python ordering and `key=`, and `ifcopenshell.api.run("pkg.usecase", ...)` as a direct call. |

## Stages

Each module (util) or file (api) moves through these stages. `status.py`
measures the first three; the rest are set in `tracking.yaml` until CI
reports them automatically.


| Stage      | Meaning                                                     | Checked by  |
| ---------- | ----------------------------------------------------------- | ----------- |
| blocked    | Nothing translates; a module-level construct stops the file | `status.py` |
| partial    | Some functions translate, others are throwing stubs         | `status.py` |
| transpiles | Every function translates                                   | `status.py` |
| typecheck  | Generated code passes `tsc --noEmit` inside the package     | CI, L2      |
| parity     | Parity tests pass against Python                            | CI, L3/L4   |
| shipped    | Exported from the npm package and documented                | release     |




## Tiers

Assigned in `tracking.yaml`, shown in `TRACKING.md`.


| Tier         | Contents                                                                                                                                          | Approach                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1            | Pure IFC graph logic: `element`, `unit`, `pset`, `attribute`, `resource`, `classification`, `system`, `constraint`, `type`, `file`, `schema`, ... | Transpiler                                                   |
| 2            | Dates and scheduling: `date`, `sequence`                                                                                                          | Transpiler + date runtime                                    |
| 3            | Math: `placement`, `representation`, `geolocation`, `shape_builder`, `data`                                                                       | Transpiler + matrix runtime                                  |
| 4            | Grammars: `selector`, `cost`, `mvd_info`                                                                                                          | Lark grammars ported by hand to a JS parser; rest transpiled |
| 5            | Geometry kernel: `util.shape`, api files using `ifcopenshell.geom`                                                                                | Hand-written on top of `ifcopenshell/geom`                   |
| api-core     | `root`, `attribute`, `pset`, `owner`, `unit`, `aggregate`, `spatial`, `type`                                                                      | Transpiler, first api packages                               |
| api          | Remaining packages                                                                                                                                | Transpiler                                                   |
| api-geometry | `geometry`, `alignment`, `cogo`                                                                                                                   | Last; depends on tier 3                                      |
| skip         | `doc`, `ifc4x3dev_scrape_data_for_docs`, `generate_pset_templates`, `profiler`                                                                    | Not ported                                                   |




## Testing

Five layers, cheapest first. All run in CI on every change to
`src/ifcopenshell-python/ifcopenshell/{util,api}` or `src/transpiler`.

### L0: Coverage (exists)

`python src/transpiler/status.py` transpiles everything and regenerates
`TRACKING.md`. CI fails if any module's translated count drops (regression gate).

### L1: Freshness

`generate.py` writes every util module (except tier `skip`) and every api usecase
into the `src/` of `@ifcopenshell/util` and `@ifcopenshell/api`, plus
`transpile.json` listing each file's stubs or module-level error. A file that
cannot be transpiled becomes a module of throwing functions, so its importers
still load. The output is not committed; CI regenerates it and type-checks and
replays it (L2, L3). To review what a rule change does to the output, CI can upload
the generated `src/` folders as an artifact or post their diff against the base branch.

### L2: Type check (exists)

`npm run build` in `src/ts/ifcopenshell-util`, then `npm run typecheck` in
`src/ts/ifcopenshell-api`, type-check both packages. Current result: 8 errors in util and 32 in api,
mostly namedtuple types, unresolved `ifcopenshell.api.*` calls and core API
signature differences. Each error is fixed in the bindings, the rules or the
Python annotations, never by hand-editing output.

### L3: Parity against Python (exists)

Rather than writing test cases by hand, the existing Python tests are the
cases. `parity/record.py` runs the pytest suites of the recorded modules and
captures every call the tests make into them:

```
src/transpiler/parity/
  record.py               # runs the Python tests, writes golden/<module>.json
  golden/<module>.json    # input file snapshots, arguments, results, file changes
src/ts/ifcopenshell-util/tests/
  runtime.test.ts         # the hand-written runtime against values computed with Python
  parity.test.ts          # replays the recorded util.* calls
  parity/replay.ts        # the replay, shared with the api package
  parity/values.ts        # JSON encoding and comparison shared with record.py
src/ts/ifcopenshell-api/tests/
  parity.test.ts          # replays the recorded api.* calls
```

How recording works:

- The modules being recorded are loaded from this checkout's source; the
wrapper and the APIs that build fixtures come from the installed
`ifcopenshell` package. This is the version being transpiled.
- Only calls made directly by test code are recorded (nested calls into other
recorded modules are not), so each call is one unit to replay.
- Before each call the IFC file is snapshotted as SPF (deduplicated by hash),
along with Python-only file state such as the `units` cache.
- Arguments are bound to the Python signature and stored positionally, with
defaults filled in; keyword-only parameters go into a trailing options object.
- After the call the return value, or the exception type, is stored. If the file
changed, every entity's flat `get_info()` is stored too.
- Each test's outcome is stored. TS skips calls from Python tests that failed.

How replay works: for each recorded call, `parity.test.ts` opens the snapshot,
restores the file state, decodes the arguments, calls the generated function and
compares the return value, file state and file contents. A call is skipped,
with the reason in the test name, if its function is a stub, its file did not
transpile, or its arguments could not be recorded.

Comparison rules:

- Entities compare by id and class; inline typed values by class and value.
- Floats use a relative tolerance of 1e-9.
- Dict and set order is ignored; Python int dict keys equal their JS string form.
- `GlobalId`, `CreationDate` and `LastModifiedDate` are masked. Entity ids must
match, so TS must create entities in the same order as Python.

Golden data is recorded with `npm run record` (in either package) and is
not committed: recording needs pytest and an installed ifcopenshell close to this checkout.
Once recorded, the TS tests need no Python.

Current results, recorded against ifcopenshell 0.9.0.post1 with every util module and
api package loaded from this checkout. Replay runs with `npm test` in each package
(the earlier milestone's totals were 6287 passed and 75 failed):

| Module | Passed | Failed | Skipped |
|---|---|---|---|
| `util.type` | 2499 | 1 | 0 |
| `api.root` | 1764 | 5 | 9 |
| `api.type` | 482 | 0 | 2 |
| `api.sequence` | 477 | 9 | 0 |
| `util.element` | 404 | 1 | 7 |
| `api.owner` | 327 | 0 | 0 |
| `api.pset` | 284 | 13 | 0 |
| `api.project` | 276 | 131 | 0 |
| `api.unit` | 260 | 0 | 2 |
| `util.unit` | 150 | 0 | 27 |
| `api.cost` | 118 | 0 | 0 |
| `api.spatial` | 99 | 2 | 0 |
| `util.geolocation` | 79 | 49 | 6 |
| `api.georeference` | 72 | 11 | 0 |
| `api.aggregate` | 68 | 2 | 0 |
| `api.profile` | 66 | 0 | 0 |
| `util.system` | 36 | 0 | 0 |
| `api.library` | 32 | 0 | 0 |
| `api.control` | 26 | 0 | 0 |
| `util.cost` | 24 | 0 | 18 |
| `util.alignment` | 17 | 0 | 0 |
| `api.grid` | 16 | 0 | 0 |
| `util.pset` | 10 | 0 | 0 |
| `util.date` | 8 | 0 | 0 |
| `util.placement` | 7 | 2 | 11 |
| `util.classification` | 5 | 0 | 0 |
| `util.brick` | 4 | 0 | 0 |
| `util.attribute` | 0 | 0 | 10548 |
| Total | 7610 | 226 | 10630 |

`tests/runtime.test.ts` checks the hand-written runtimes (numpy, datetime, isodate,
dateutil, `str.format`) against values computed with Python; all pass.

`util.constraint`, `util.file`, `util.fm`, `util.resource`, `util.schema` and
`api.attribute` have no Python tests that call them directly, so no calls are
recorded for them yet.

What the skips are:

- **`util.attribute`:** its arguments are schema attribute objects, which cannot be
  recorded, and most of its calls come from the failing `util.schema` migrator tests.
- **`util.unit`:** `format_length` uses `fractions.Fraction`.
- **`util.cost`:** arguments the recorder cannot encode (formula parse trees).

The remaining failures, all in code that was a throwing stub before this milestone
except the last two:

- **`ifcopenshell.geom` (55: `util.geolocation`, `util.placement`, `api.aggregate`,
  `api.spatial`, `api.root`):** `util.placement.get_placement` builds the matrix with
  the geometry kernel (tier 5).
- **`type(x)` introspection (114, `api.project`):** `append_asset` uses `type()` as a
  value in a nested helper.
- **Schemas (17, `api.project`):** IFC4X1 and IFC4X2 have no schema plugin in the JS build.
- **ShapeBuilder (14, `api.georeference`, `api.root`):** one method calls
  `__builtins__["print"](*args, **kwargs)`.
- **networkx (9, `api.sequence`):** `recalculate_schedule` (manual port).
- **Numbers (13, `api.pset`):** JS has one number type, so a whole-number float
  becomes `IfcInteger`/`IfcQuantityCount` where Python picks `IfcReal`/`IfcQuantityLength`.
- **Values across files (`api.pset`) and `util.type` / `util.element` (1 each)**, as before.

Resolved in this pass:

- **Pset templates:** `@ifcopenshell/util` ships `src/schema/Pset_*.ifc`, copied by
  `generate.py`. Generated code opens them with the new core `openPath(path)`,
  which reads from Node's file system or from bytes given to `registerResource()`
  (needed in browsers).
- **`get_primitive_type`:** schema objects from the core now have Python's `str()`
  form (`<type IfcLabel: <string>>`), so the Python function transpiles unchanged.
  Aggregate bounds print as `?`, because the WASM API does not expose them.
- **Classes and data types:** `__init__` becomes a constructor, `Cls(args)` becomes
  `new Cls(...)`, `create_entity(..., id=...)` keeps the id, `re` and `pathlib`
  use the runtime, `isinstance(x, ifcopenshell_wrapper.<class>)` checks against
  `ifcopenshell.wrapper`, and builtins used as values (`list`, `str`) are mapped.

How recording works with 0.9:

- **Source loading:** all util modules and api packages are loaded from this
  checkout. Only `util.schema` (missing data files), `util.ifc4x3dev_scrape_data_for_docs`
  and `api.style` (Python 3.13 TypedDict) fall back to the installed copies.
- **File state:** each call stores the id counter (`get_max_id()`) and which owner
  settings the test left active, since neither is in the STEP snapshot.
- **Golden size:** about 5.5 MB for 22 modules, because file snapshots are
  deduplicated per STEP line and only changed entities are stored after a call.

Core fixes, in the `ifcopenshell` package (45 tests pass):

- **Schema reflection:** `schemaByName` and `entity.declaration()` return
  declarations downcast like Python, including `supertype()`/`subtypes()`
  returning named declarations. This works around a WASM binding gap: entity
  declarations from those methods have no `name()`.
- **Native helpers:** `file.isReferencedOnlyIn` and `file.idsReferencedOnlyWithin`,
  matching the 0.9 helpers that `util.element.remove_deep2` uses.
- **Files and schema:** `openPath`, `registerResource`, `file.create(cls, attrs, id)`,
  `entity.isEntity()`, Python `str()` of schema objects, `declarationByName` throwing
  for unknown names, and `ifcopenshell.wrapper` (the native classes).

Known limitations:

- **Version mismatch:** recording needs an installed `ifcopenshell` close to this
checkout (0.9.0 now). With 0.8.5, 67 Python tests failed on missing native methods.
- **Recorded calls only:** only calls made directly from test code are replayed;
modules without their own tests are covered only through other modules.
- **Python-only state:** a call whose result depends on state beyond the IFC data,
`FILE_STATE` (`units`), the id counter and the owner settings is not replayed faithfully.
- **Unchanged files:** when the file is not expected to change, that is not
checked yet.



### L4: Transpiled Python tests

L3 already replays every call the Python tests make, but not their `assert`
statements on derived values. When that gap matters, a second rule set
(`pytest.yaml`) can translate the pytest files themselves into Vitest. This is
optional and comes after api-core.

### Exit criteria per module

A module is done when it transpiles with no stubs (or its stubs are listed as
intentionally unsupported in `tracking.yaml`), type-checks, and every recorded
call from a passing Python test replays successfully.

## Path to full parity

Status: util 91% and api 95% of functions/classes translate (see `TRACKING.md`);
7610 recorded calls match Python, 226 fail, 10630 are skipped. `tsc` reports 84
errors in util and 137 in api (273 before this milestone, with far less code).

What remains, largest first:

1. **numpy and dates (tiers 2 and 3): done** in `_numpy.ts`, `_datetime.ts`,
   `_isodate.ts` and `_dateutil.ts`; see "Decisions (milestone 6)". Left: `util.placement.get_placement`
   on `ifcopenshell/geom` (tier 5), and `fractions.Fraction` / `decimal.Decimal`
   (`util.unit.format_length`, `util.geolocation.dd2dms`).
2. **Cyclic packages.** `util.alignment` and `util.unit` import `ifcopenshell.api`
   inside functions, as Python does. The generated `@ifcopenshell/util` therefore
   imports `@ifcopenshell/api`, which `tsc` cannot resolve inside the util package.
   Either the two packages become one, or those functions move to the api package.
3. **Grammars (tier 4).** `util.selector`, `util.mvd_info` and cost formulas use
   Lark grammars. They need a hand-written parser, or a Lark-compatible JS one.
4. **Geometry kernel (tier 5).** `util.shape` and api files using `ifcopenshell.geom`
   map onto `ifcopenshell/geom` by hand.
5. **Smaller transpiler gaps:** `type()` as a value, `try`/`except`/`else`,
   `ifcopenshell.util.schema.Migrator` (needs the generated `class_*_to_*.json` data),
   `ast` and `csv` (one file each), and Python annotations narrower than the code's
   actual use (for example `util.date.datetime2ifc` rebinds a `date | str` parameter
   to a `time`), which `tsc` reports.
6. **Recording coverage.** Modules without their own Python tests (`util.constraint`,
   `util.file`, `util.fm`, `util.resource`, `api.attribute`, and most api packages
   beyond api-core) are only exercised indirectly. Add them to
   `DEFAULT_MODULES` tier by tier; `util.attribute` calls take schema objects and
   need a schema-object encoding in the recorder (10548 skipped calls).
7. **Language differences to document, not fix:**
   - JS has one number type, so a whole-number Python float such as `30.0` behaves
     as an int (`IfcInteger`, `IfcQuantityCount`) where Python picks `IfcReal` or
     `IfcQuantityLength` (11 failing calls).
   - An entity from another file assigned to an attribute: Python keeps a reference
     to the foreign entity; JS rejects it. Typed values from another file are recreated,
     which matches Python's observable behaviour.

Added to the `ifcopenshell` core (JS) for parity so far: canonical entity wrappers,
`entity.file()`, iteration and indexing of entities, `entity.walk`, `entity.isEntity()`,
`file.create(cls, attrs | positional, id)`, `openPath`/`registerResource`,
`file.isReferencedOnlyIn`/`idsReferencedOnlyWithin`, `guid`, `version`, `File.units`,
downcast schema declarations with Python `str()`, `declarationByName` raising,
`ifcopenshell.wrapper`, and typed values recreated across files. Still needed in the
native bindings: `name()` on entity declarations from `subtypes()`/`supertype()`
(worked around in JS) and aggregate bounds on aggregation types.

## Milestones


| #   | Milestone               | Done when                                                                                                                            |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| M0  | Tracking                | `status.py`, `tracking.yaml`, `TRACKING.md`, this plan (done)                                                                        |
| M1 | Multi-module transpiler | Done: decisions above implemented, both packages generated |
| M2 | Test harness | L0, L2 and L3 run locally (done); still to do: CI, recording against a build of this checkout, L2 at zero errors |
| M3 | Pilot: `util.element` | In progress: 51/56 functions translate, 339/348 replayable calls pass. Nearly all rules added were general, not element-specific |
| M4  | Tier 1 util             | All tier 1 modules at parity                                                                                                         |
| M5  | api-core + L4           | api-core packages at parity; pytest-to-Vitest translation running for them                                                           |
| M6  | Runtime tiers           | In progress: runtimes for numpy, datetime, isodate, dateutil, os and itertools; `util.date` and `util.alignment` at parity; `util.placement` and `util.geolocation` wait on `get_placement` (geom) |
| M7  | Remaining api           | All `api` tier packages at parity                                                                                                    |
| M8  | Manual tiers            | Tier 4 grammars and tier 5 geometry ported by hand; api-geometry at parity                                                           |


Each milestone ends with the numbers in this plan updated from `status.py` and the parity run.

## Current blockers

From the first `status.py` run, the most frequent first failures are imports
of other ifcopenshell modules (`ifcopenshell.api.owner`, `ifcopenshell.util.element`,
...), then `setattr`, `file.create_entity`, `import numpy`, `import math` and
`datetime`. Cross-module imports and `setattr`/`create_entity` are therefore
the first rules to add in M1. See the top blockers in `TRACKING.md` for the current list.

## Workflow for a module

1. Run `status.py`; pick the next module in tier order with the most unblocked dependents.
2. Add rules for its blockers; re-run `status.py` and check no other module regressed.
3. Add the module to `DEFAULT_MODULES` in `parity/record.py`, run `npm run generate`, `npm run record` and `npm test` in its package (see "Running the tests" in [README.md](README.md)).
4. Fix type errors in the bindings, rules or annotations.
5. Set `stage` in `tracking.yaml` if CI does not report it yet; commit the rules, runtime and `tracking.yaml`.

