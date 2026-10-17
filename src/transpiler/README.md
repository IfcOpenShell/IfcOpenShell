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
