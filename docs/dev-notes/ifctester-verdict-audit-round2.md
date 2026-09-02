# ifctester wrong-verdict audit, round 2

Scope: `src/ifctester/ifctester/facet.py`, `ids.py`. Goal: find defects that
make an IDS check report the wrong pass/fail verdict, on top of round 1
(`PartOf` `predefinedType="USERDEFINED"`, #9203) and the four fixes in
#9190, plus #9187, #9188, #9189, #9058, #9059, #9142, #8407, #8292, #8253,
#8161.

## Existing-work check

```
git fetch origin --quiet && git fetch bimvoice --quiet
gh pr list --repo IfcOpenShell/IfcOpenShell --state open --limit 900 \
  --json number,title --jq '.[] | select(.title|test("ifctester|ids";"i"))'
git for-each-ref --format='%(refname:short)' refs/remotes/bimvoice/ | grep -iE 'ifctester|ids'
```

805 open PRs total (`--limit 900` used, none skipped by the limit). 22
ifctester/ids-related PRs found; all 11 named in the task brief confirmed
still open and unmerged. `bimvoice` branches enumerated; the round-1 branch
`fix/ifctester-partof-userdefined` was found and read in full (its own
`docs/dev-notes/ifctester-verdict-audit.md`) to avoid re-treading its
branches: `PartOf` (all 6 relation branches x `USERDEFINED`),
`Specification.minOccurs`/`maxOccurs` (considered, correctly not pursued),
and a full re-read of `reporter.py` (nothing beyond #9190).

Each of the 11 named PRs was read via `gh pr diff` (not just titles) to
pin down the exact lines already fixed elsewhere, so this round does not
duplicate:

- #9190: `Txt.print` operator precedence, `Console` prohibited success
  count, `Json` forced-fail pass count, `Property` optional masking other
  matching psets.
- #9189: `Specification.validate` prohibited-with-requirements status.
- #9188: `Property` `IfcPropertyTableValue` dataType-unset silent fail
  (confirmed by reading the diff: `if self.dataType and ...` with no
  `else` branch meant `values` stayed empty and the property fails when no
  `dataType` constraint is given at all).
- #9187: crash on unset layer material.
- #9142: `totalDigits`/`fractionDigits` restriction.
- #9059: `Classification.__call__`'s `if is_pass:` before the system check
  should be `if is_pass and self.system:` (false FAIL when no system is
  specified); IFC2X3 `IfcPreDefinedPropertySet` fallback.
- #9058: `cast_to_value`'s bare `elif target_type == "bool":` falls
  through to `bool(from_value)` for any unrecognised spelling, which is
  `True` for any non-empty string. Fixed at the shared helper, so it
  already covers both `Attribute` and `Property` callers.
- #8407: scalar IDS value XML-string normalisation.
- #8292: `Entity` restriction crash on IFC2X3 fail path.
- #8253: `Entity` `predefinedType` restriction including `USERDEFINED`.
- #8161: `Property.__call__`'s `IFCLOGICAL` `UNKNOWN` handling: the
  pre-fix code did `pass` (discarding the property as if it didn't exist)
  instead of recording the `UNKNOWN` value. This is the fix whose
  *sibling* defect this round found (see below).

## Branch enumeration

| Area | Branches examined |
|---|---|
| `Entity.__call__` | 4 (exact match, IFC2X3 type inference, literal `predefinedType`, `USERDEFINED` literal via #8253's scope) |
| `Attribute.__call__` | 11: single-name resolution, multi-name (Restriction) resolution, optional-on-name-not-found short-circuit, optional-on-value-empty (**new**, not previously short-circuited), LOGICAL UNKNOWN emptiness (**new defect**), value-type dispatch x5, prohibited flip |
| `Classification.__call__` | 5 (no-reference optional short-circuit, value match, system match [#9059], prohibited flip, optional-with-wrong-value fall-through, verified correct) |
| `Property.__call__` | 7 property-entity classes x (existence, dataType, unit-convert), value-dispatch x5, prohibited flip, IfcPropertyTableValue dataType-unset [#9188], IFCLOGICAL UNKNOWN [#8161] |
| `Material.__call__` | 5 material classes x value-set-build, prohibited flip, optional short-circuit |
| `PartOf.__call__` | 6 relation branches, out of scope (round 1 / #9203) |
| `Restriction.__eq__` | 9 constraints (enumeration, pattern, length, minLength, maxLength, maxExclusive, maxInclusive, minExclusive, minInclusive), all re-verified inclusive/exclusive bounds by direct reading; no defect found |
| `cast_to_value` | shared helper, boolean-spelling defect already fixed at #9058 (covers all callers) |
| `Specification.validate` | prohibited-specification requirement status [#9189]; broadphase filter chaining re-read for double-application correctness, no defect found (idempotent) |

Total: 6 facet `__call__` methods (minus `PartOf`, out of scope),
9 `Restriction` constraints, `cast_to_value`, and `Specification.validate`'s
cardinality branches examined. 2 confirmed new defects, both in
`Attribute.__call__`.

## Defect 1 (FALSE PASS + FALSE FAIL): `Attribute` never recognises `IFCLOGICAL` `UNKNOWN` as a real value

Same shape as #8161, in the sibling facet #8161 did not touch.

### Root cause

`Attribute.__call__` (pre-fix, `facet.py:349`):

```python
try:
    attribute_type = inst.attribute_type(argument_index)
    if attribute_type == "LOGICAL" and value == "UNKNOWN":
        is_empty = True
except:
    ...
```

`IFCLOGICAL` is a tri-state type (`TRUE`/`FALSE`/`UNKNOWN`); `UNKNOWN` is a
legitimate, present value, not an absent one. Marking it `is_empty = True`
here removes it from `non_empty_values`, so an attribute that is genuinely
set to `UNKNOWN` is treated identically to an attribute that was never set
at all.

### Reproduction (before fix)

```python
ifc = ifcopenshell.file(schema='IFC4')
layer = ifc.create_entity('IfcPresentationLayerWithStyle', Name='L1',
                           AssignedItems=[], LayerOn='UNKNOWN')
facet.Attribute(name='LayerOn', cardinality='required')(layer)
facet.Attribute(name='LayerOn', cardinality='prohibited')(layer)
```

IDS requirement A: "The `LayerOn` attribute shall be provided." The
attribute genuinely is provided (value `UNKNOWN`).
- Verdict obtained (before fix): **FAIL**, `reason={'type': 'FALSEY', 'actual': 'UNKNOWN'}`
- Correct verdict: **PASS**

IDS requirement B (the severe one): "The `LayerOn` attribute shall not be
provided." The attribute genuinely is provided.
- Verdict obtained (before fix): **PASS**, `reason={'type': 'PROHIBITED'}`
- Correct verdict: **FAIL**

Contrast with the same attribute set to a normal boolean value (`True`),
which already behaves correctly both ways (required PASS, prohibited FAIL),
and with the attribute genuinely absent (required FAIL, prohibited PASS) —
`UNKNOWN` was the only present value silently mistreated as absent.

### Fix

`src/ifctester/ifctester/facet.py`: removed the `LOGICAL`/`UNKNOWN`
special case; the `attribute_type()` call is kept only for its original
purpose (detecting inverse attributes that raise on `attribute_type()`).

`src/ifctester/test/test_facet.py`: the existing test at this exact case
asserted the *wrong* behaviour (`"Attributes with a logical unknown always
fail"`, `expected=False`); corrected to `expected=True`, plus a new
`prohibited`-cardinality case added to cover the false-PASS side.

## Defect 2 (FALSE FAIL): `Attribute` `optional` cardinality never short-circuits on a merely-unset (but valid) attribute

### Root cause

`Attribute.__call__` (`facet.py:308-333`, forward-attribute path):

```python
if attribute_type == 1:  # Forward attribute
    values = [getattr(inst, self.name, None)]
...
is_pass = bool(values)
if not is_pass:
    if self.cardinality == "optional":
        return AttributeResult(True)
    reason = {"type": "NOVALUE"}
```

For a valid forward attribute, `values` is always a one-element Python
list, even when the attribute itself is unset (`values = [None]`).
`bool([None])` is `True` because the *list* is non-empty, not because the
*value* is non-empty. The `optional` short-circuit above therefore only
ever fires when the attribute **name** does not resolve at all (the
inverse-attribute path, where `values = []`); it never fires for the far
more common case of a real, valid, currently-unset attribute. The
falsy-value filtering that follows (lines 335-360) correctly detects the
unset value and sets `reason={"type": "FALSEY"}`, but by then the
`optional` check has already been skipped, so `optional` behaves exactly
like `required` for this case: it fails.

### Reproduction (before fix)

```python
ifc = ifcopenshell.file(schema='IFC4')
wall = ifc.create_entity('IfcWall', GlobalId=ifcopenshell.guid.new(), Name='Wall1')
# wall.Description is None (never set)
facet.Attribute(name='Description', cardinality='optional')(wall)
```

IDS requirement: "If `Description` is provided, it should [restriction];
if not provided, that's fine" — the entire point of `optional`.
- Verdict obtained (before fix): **FAIL**, `reason={'type': 'FALSEY', 'actual': None}`
- Correct verdict: **PASS** (nothing to check, attribute is absent)

Same wrong result for an explicit empty string (`Description=""`).
Contrast: `Attribute(name="Rabbit", cardinality="optional")` (an
attribute name that does not exist on the class at all) already correctly
passes — this is the pre-existing test at `test_facet.py:339` — showing
the two "absent" cases were handled inconsistently depending on which code
path produced the empty `values`.

This is a **false FAIL**, not a false PASS, but it is a very commonly hit
one: any IDS spec using `cardinality="optional"` on an `Attribute`
requirement against a genuinely unset attribute reported non-compliance
that does not exist.

### Fix

`src/ifctester/ifctester/facet.py`: added the same `optional`
short-circuit at the point where `non_empty_values` turns out empty
(mirrors the existing short-circuit for the name-not-found case).

`src/ifctester/test/test_facet.py`: two new assertions next to the
existing `optional` coverage, for an unset attribute and an empty-string
attribute.

## Considered and not pursued

- **`Restriction.__eq__` bounds**: `maxExclusive`/`maxInclusive`/
  `minExclusive`/`minInclusive` re-derived by hand against their names;
  all four correctly implement inclusive-vs-exclusive with no off-by-one.
  `length`/`minLength`/`maxLength` use `len(str(other))`, which is correct
  for the string base type these are documented against; no fixture or
  code path applies `length` to a non-string base, so not chased further
  (same "spec being odd, not code being wrong" restraint as round 1).
- **`Classification`/`Material` "least attention" facets**: read and
  exercised (including on IFC2X3, `IfcClassificationReference` via
  `ItemReference` and `IfcMaterial`/`IfcMaterialLayerSet` value sets) with
  no new defect; the one real defect in this area (`Classification`
  system false FAIL) is #9059's, out of scope.
- **IFC2X3 vs IFC4 divergence**: `Property.filter()`'s schema-conditional
  candidate set (`IfcObjectDefinition` only on IFC2X3, plus
  `IfcMaterialDefinition`/`IfcProfileDef` on IFC4) is a real difference but
  is a narrowing-only broadphase filter, not a silent no-op; per-element
  checks still run correctly on whatever `filter()` returns, verified by
  running `Material` and `Classification` facets against IFC2X3-created
  entities directly (see above). `Attribute.filter()` and `__call__` are
  schema-driven via `ifcopenshell.ifcopenshell_wrapper.schema_by_name`, no
  hardcoded IFC4-only lookup found.
- **`get_container`/`get_aggregate`/`get_nest`/`get_type`/`get_material`
  docstrings vs callers**: read in full; each caller in `facet.py` (mostly
  `PartOf`, out of scope this round) matches the documented contract. No
  second `get_predefined_type()`-shaped mismatch found among these.
- **`Specification.validate`'s broadphase filter chaining**: every
  applicability facet after the first is applied twice (once during
  `filter()` narrowing, once again per-element in the `is_applicable`
  loop, except `Entity` which is explicitly skipped in the loop). Read
  through; this is redundant work, not a correctness bug, since
  `facet(element)` is a pure, idempotent function of the element and
  model state.

## Measured ratio

2 confirmed wrong-verdict defects (both in `Attribute.__call__`: an
`IFCLOGICAL` `UNKNOWN` false PASS/false FAIL pair, and an `optional`
cardinality false FAIL) out of the systematic re-check of 6 facet
`__call__` methods (`PartOf` excluded, already round 1's), 9 `Restriction`
constraints, the shared `cast_to_value` helper, and `Specification`'s
cardinality handling, all cross-checked against the 11 already-fixed PRs
named in the task brief plus round 1's own findings.

## Verification

- Environment: python3.13.6 scratch copy at `/tmp/ifctester-audit2-env`
  (full copy of `build/Darwin/arm64/10.15/install/python-3.13.6`, then
  `.py`-only rsync of `ifcopenshell-python/ifcopenshell` and
  `ifctester/ifctester` over it, run with `PYTHONNOUSERSITE=1`).
  `ifcopenshell.__file__`/`ifctester.__file__` confirmed resolving into
  the scratch copy. All 35 `ifcopenshell.api.*` submodules confirmed
  importing, plus `isodate`, `python-dateutil`, `networkx`,
  `typing_extensions`, `numpy`, `shapely`, `lark`, `xmlschema` (needed by
  `ids.py` itself, not on the task's stated dependency list but required
  for `ifctester` to import at all).
- Baseline (before any change, this worktree's `src/ifctester`, which does
  not yet include round 1's or any of the 11 named PRs' fixes):
  `pytest -p no:pytest-blender test/` — 37 passed.
- After both fixes plus new test assertions: 37 passed (test count
  unchanged; assertions added inside existing test methods).
- `black`/`ruff` clean on `facet.py` and `test_facet.py`.

## Branch

`fix/ifctester-verdict-audit-round2`, pushed to `bimvoice`. No PR opened
per instructions.
