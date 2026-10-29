<!-- This file was generated with the assistance of an AI coding tool. -->

# Porting `ifcopenshell.util` and `ifcopenshell.api` to TypeScript

## Goal

Ship `ifcopenshell.util` and `ifcopenshell.api` in the `ifcopenshell` npm package
(`src/ts/ifcopenshell-js`), generated from the Python sources by `transpile.py`.
Python stays the source of truth: the TypeScript is regenerated on every change,
never edited by hand. Modules that cannot be expressed as reusable rules are
ported by hand.

The api calls util heavily (`util.element`, `util.unit`, `util.date`,
`util.representation`) and itself, so porting goes bottom-up.

## Principles

1. **Rules over modules.** A new construct gets a general rule in `ts.yaml`.
   If a module mostly needs rules nothing else uses, port it by hand instead.
2. **No silent gaps.** Unsupported functions stay throwing stubs with a reason;
   unsupported module-level code fails the file. `transpile.json` lists both.
3. **Fix the bindings, not the transpiler.** Missing JS API (schema reflection,
   `entity.file`, `get_total_inverses`, ...) is added to the WASM bindings or
   `src/ts/ifcopenshell-js`, not faked in generated code.
4. **Every stage is tested automatically** (see Testing).

## Layout and decisions

| Topic | Decision |
|---|---|
| Output | `generate.py` writes `src/ts/ifcopenshell-js/src/python/util/<module>.ts` and `src/python/api/<package>/<usecase>.ts` (plus an `index.ts` per api package), and `src/python/transpile.json` with each file's stubs or module-level error. They are build output and not committed. A file that cannot be transpiled becomes a module of throwing functions, so its importers still load. |
| Imports | `ifcopenshell/util/unit` and `ifcopenshell/api/root`, through the package's `./util/*` and `./api/*` exports. Generated modules import the core and each other by relative path. |
| Build | `npm run build` compiles the core strictly, then `src/python` with `tsconfig.python.json` (`strict: false`, as Python does not track None), and copies the data files (`Pset_*.ifc`, JSON tables) next to the generated modules. |
| Inputs | The Python source, `ts.yaml`, the hand-written runtime `src/python/_*.ts`, and `precomputed.json` (results of the functions listed under `precomputed` in `ts.yaml`, refreshed with `generate.py --precompute`). `generate.py` needs only `requirements.txt`. |
| Types | Annotations become TS types where TypeScript can check them as Python uses them. String `Literal` parameters accept `string` and `set` parameters any `Iterable`, as callers pass `file.schema()` and lists. A parameter the function rebinds to another kind of value, or narrows with `isinstance`/`hasattr` when it is a union, is `any`; so are the return types of `@overload` implementations and of nested functions returning unions, and names the module does not declare (`TYPE_CHECKING` imports such as `mathutils.Vector`). |
| Naming | camelCase functions and module data (`getProjectUnit`); CONSTANT_CASE and `_private` names are kept. Locals keep their Python names; JS reserved words get a trailing `_`. |
| Arguments | Required parameters stay positional; parameters with defaults and keyword-only parameters go into a trailing options object with camelCase keys, as in the core (`getInfo({ recursive })`). `f(a, *rest)` fills optional parameters at runtime. |
| Calls | A project-wide index of util and api functions and classes resolves `ifcopenshell.util.x.f(...)`, `from ... import f`, local and nested calls, and binds their arguments with Python semantics. `ifcopenshell.api.run("pkg.usecase", ...)` becomes a direct call. |
| Classes | Classes (the `Usecase` pattern), dataclasses (`fromKwargs` for `Cls(**kwargs)`), classmethods (static, `cls` bound to the class), context managers (`__enter__`/`__exit__` in try/finally) and TypedDicts (object types). |
| Runtime modules | `runtime_modules` in `ts.yaml` maps `numpy`, `datetime`, `isodate`, `dateutil`, `os` and `itertools` onto `src/python/_numpy.ts`, `_datetime.ts`, ... Members are camelCase (`np.zeros_like` is `np.zerosLike`). `math` maps onto `Math`. `_py.ts` holds Python semantics used where a value's type is not known: truthiness, `len`, `in`, operators, indexing, `str.format`, `re`. |
| Python data model | Arrays and dates overload operators, so `+ - * / // % ** @`, unary `-`, `==` and subscripts dispatch at runtime (`py.add`, `py.getitem`, ...) to `__add__`/`__radd__`, `__getitem__` and so on, for values inferred as arrays or dates and for values of unknown type in modules importing numpy or datetime. |
| numpy | `NDArray` has shape, strides and offset, so slices and rows are views, as in numpy. Broadcasting, integer and boolean array indices and `np.newaxis` are supported, with the functions the generated code calls. Functions returning a numpy scalar return a JS number. |
| Dates | `date`, `datetime`, `time`, `timedelta` and fixed-offset `timezone` follow Python's arithmetic, comparison, `str()`, `isoformat()` and `strftime()`; naive datetimes are local time. `isodate` durations and `dateutil.parser` follow the installed versions. |
| Data files | `json.load(open(path))`, `with open(path) as f`, `os.path` and `ifcopenshell.open(path)` read through the core's `readResource`, which uses Node's file system or bytes given to `registerResource()` (browsers). |
| Overridable modules | `ifcopenshell.api.owner.settings` gets an `overrides` object, since Python users assign to its functions. |
| Core fixes | In `ifcopenshell`: one canonical wrapper per entity (so `===`, `Set` and `Map` follow Python entity equality), `entity.file()`, iterating and indexing entities and files, `entity.walk`, `file.create(cls, attrs, id)`, `File.fromString`, `file.stepHeader`, `guid`, `version`, `File.units`, downcast schema declarations with Python `str()`, `openPath`/`readResource`/`registerResource`. |

## Tiers

| Tier | Contents | Approach |
|---|---|---|
| 1 | IFC graph logic: `element`, `unit`, `pset`, `attribute`, `resource`, `classification`, `system`, `type`, `schema`, ... | Transpiler |
| 2 | Dates and scheduling: `date`, `sequence` | Transpiler + date runtime |
| 3 | Math: `placement`, `representation`, `geolocation`, `shape_builder`, `data` | Transpiler + numpy runtime |
| 4 | Grammars: `selector`, `cost`, `mvd_info` | Lark grammars ported by hand; rest transpiled |
| 5 | Geometry kernel: `util.shape`, api files using `ifcopenshell.geom` | By hand on top of `ifcopenshell/geom` |
| api | All api packages; `geometry`, `alignment` and `cogo` last, as they depend on tier 3 | Transpiler |
| skip | `doc`, `ifc4x3dev_scrape_data_for_docs`, `generate_pset_templates`, `profiler` | Not ported (`SKIP` in `generate.py`) |

## Testing

How to run the tests is described in "Running the tests" in [README.md](README.md).

- **Coverage:** `generate.py --report` prints translated functions per module and the
  most frequent unsupported constructs. A module's translated count must not drop.
- **Type check:** `npm run build` in `src/ts/ifcopenshell-js` type-checks the generated
  code. Errors are fixed in the bindings, the rules or the Python annotations, never by
  editing output.
- **Runtime:** `tests/python/runtime.test.ts` checks the hand-written runtime against
  values computed with Python, numpy, isodate and dateutil.
- **Parity:** the Python tests are the test cases. `parity/record.py` runs the pytest
  suites of the modules in its `DEFAULT_MODULES` and records every call the tests make
  into them in `golden/<module>.json` (not committed); `tests/python/parity.test.ts`
  replays each call against the built package.

Recording:

- The recorded modules, and every other util module and api package, are loaded from
  this checkout's source; the wrapper comes from the installed `ifcopenshell`, which must
  be close to this checkout (0.9).
- Only calls made directly by test code are recorded, so each call is one unit to replay.
- Before each call the IFC file is snapshotted as STEP (deduplicated per line), with the
  id counter, the owner settings the test left active and Python-only state (`units`).
- Arguments are bound to the Python signature and stored positionally; optional and
  keyword-only parameters go into a trailing options object. Dates, durations and numpy
  arrays have their own encodings.
- The return value, or the exception type, is stored, and the entities the call changed.
  TS skips calls from Python tests that failed.

Comparison:

- Entities compare by id and class; inline typed values by class and value. Entity ids
  must match, so TS must create entities in the same order as Python.
- Floats use a relative tolerance of 1e-9; dict and set order is ignored.
- `GlobalId`, timestamps and values set from the current time are masked.

## Status

util 336/383 (88%) and api 506/531 (95%) functions and classes translate. 7610 recorded calls match
Python, 226 fail and 10630 are skipped (recorded against ifcopenshell 0.9.0.post1).
The generated code type-checks.

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

## What remains

Largest first:

1. **Failing calls.** `ifcopenshell.geom` (55: `util.placement.get_placement` builds the
   matrix with the geometry kernel, tier 5); `type()` as a value (114, `api.project`);
   IFC4X1/IFC4X2 have no schema plugin in the JS build (17); a call with both `**kwargs`
   and keywords in one ShapeBuilder method (14); networkx in `recalculate_schedule` (9, by hand).
2. **Dates set from the current day.** IFC2X3 cost and sequence usecases write today's
   date as an `IfcCalendarDate`; its components are not masked yet, so 14 recorded calls
   fail when replayed on another day than they were recorded.
3. **Grammars (tier 4).** `util.selector`, `util.mvd_info` and cost formulas use Lark grammars.
4. **Smaller gaps:** `fractions.Fraction`, `decimal.Decimal`, `try`/`except`/`else`,
   `ifcopenshell.util.schema.Migrator` (needs generated `class_*_to_*.json` data), `ast`, `csv`.
5. **Recording coverage.** `util.constraint`, `util.file`, `util.fm`, `util.resource`,
   `api.attribute` and most api packages have no recorded calls yet; `util.attribute`
   calls take schema objects, which the recorder cannot encode (10548 skipped calls).
6. **Language differences to document, not fix:** JS has one number type, so a
   whole-number float such as `30.0` becomes `IfcInteger`/`IfcQuantityCount` where Python
   picks `IfcReal`/`IfcQuantityLength` (13 failing calls in `api.pset`); an entity from
   another file cannot be assigned to an attribute.

Still needed in the native bindings: `name()` on entity declarations from
`subtypes()`/`supertype()` (worked around in JS) and aggregate bounds on aggregation types.

## Workflow for a module

1. Run `generate.py --report`; pick the next module in tier order.
2. Add rules for its blockers; check no other module's count dropped.
3. Add the module to `DEFAULT_MODULES` in `parity/record.py`, then `npm run generate`,
   `npm run build`, `npm run record` and `npm test` in `src/ts/ifcopenshell-js`.
4. Fix type errors in the bindings, rules or annotations.
