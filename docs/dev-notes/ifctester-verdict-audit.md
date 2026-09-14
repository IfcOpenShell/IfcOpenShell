# ifctester wrong-verdict audit

Scope: `src/ifctester/ifctester/facet.py`, `reporter.py`, `ids.py`. Goal: find
defects that make an IDS check report the wrong pass/fail verdict, on top of
the four already fixed this week in #9187, #9188, #9189, #9190.

## Existing-work check

Before starting, all open PRs and `bimvoice` branches touching `ifctester` or
`ids` were enumerated (805 open PRs total; the first `--limit 400` search
missed older PRs, corrected with `--limit 900`, zero skipped after that).
Confirmed already fixed or already in flight, and therefore out of scope:

- #9190 (`optional` masking failures, reporter forced-fail pass count,
  console prohibited success count, `Txt.print` operator precedence)
- #9189 (prohibited specification requirement status)
- #9188 (property table `dataType` silent fail)
- #9187 (crash on unset layer material)
- #9142 (`totalDigits`/`fractionDigits` restriction)
- #9059 (Classification `SYSTEM` false fail when no system specified;
  IFC2X3 predefined property sets)
- #9058 (unrecognised boolean spellings matching `True`)
- #8407 (scalar IDS values not normalised to their XML string form)
- #8292 (Entity restriction crash on IFC2X3 fail path)
- #8253 (Entity `predefinedType` restriction including `USERDEFINED`)
- #8161 (`IFCLOGICAL` `UNKNOWN` value wrongly treated as absent)

None of these touch `PartOf`.

## Branch enumeration

`__call__` branch count per facet type, `Restriction.__eq__` constraint
count, and reporter verdict-affecting computations:

| Facet | `__call__` branches |
|---|---|
| `Entity` | 4 (exact match, IFC2X3 type inference, `predefinedType` literal, `predefinedType` USERDEFINED) |
| `Attribute` | ~10 (single/restriction name resolution, LOGICAL UNKNOWN emptiness, value type dispatch x5, prohibited flip) |
| `Classification` | 5 (no-reference, value match, system match, prohibited flip, optional short-circuit) |
| `Property` | 7 property-entity classes x (existence, dataType, unit-convert) + value-dispatch x5 + prohibited flip |
| `Material` | 5 material classes x value-set-build + prohibited flip |
| `PartOf` | 6 relation branches (none / `IFCRELAGGREGATES` / `IFCRELASSIGNSTOGROUP` / `IFCRELCONTAINEDINSPATIALSTRUCTURE` / `IFCRELNESTS` / `IFCRELVOIDSELEMENT IFCRELFILLSELEMENT`), each with entity-name and `predefinedType` sub-checks, x prohibited flip |
| `Restriction.__eq__` | 9 constraints (enumeration, pattern, length, minLength, maxLength, maxExclusive, maxInclusive, minExclusive, minInclusive) |

Total facet-level decision points examined: 6 facet types, 6 `PartOf`
relation branches, 9 restriction constraints, plus 3 reporter aggregation
sites (`Console`, `Json`, `Txt`) already covered by #9190.

## FALSE PASS found: `PartOf` never recognises `predefinedType="USERDEFINED"`

**Every `PartOf` relation branch, plus the ancestor-walk (no-`relation`) and
`IFCRELAGGREGATES` branches, silently mismatch `predefinedType="USERDEFINED"`,
producing a false PASS on a `prohibited` requirement and a false FAIL on a
`required` one.**

### Root cause

`ifcopenshell.util.element.get_predefined_type()` never returns the literal
string `"USERDEFINED"`. Its own docstring:

> "If the predefined type is user defined, the custom type (such as object
> type, element type, or process type depending on the class) is returned
> instead."

`Entity.__call__` (facet.py:249) already special-cases this:

```python
if self.predefinedType == "USERDEFINED":
    is_pass = ifcopenshell.util.element.is_userdefined_type(inst)
```

`PartOf.__call__` had no such special case in any of its six sites
(facet.py:516, 538, 562, 576, 592, 618, pre-fix), each comparing
`get_predefined_type(x) != self.predefinedType` directly. Since the custom
text (e.g. `"CustomSpace"`) never equals the literal `"USERDEFINED"`, a
`predefinedType="USERDEFINED"` requirement can never be satisfied through
this comparison, in either direction.

### Reproduction (before fix)

```python
ifc = ifcopenshell.file(schema='IFC4')
ifc.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name='P')
space = ifcopenshell.api.root.create_entity(ifc, ifc_class='IfcSpace', name='Room1')
space.PredefinedType = 'USERDEFINED'
space.ObjectType = 'CustomSpace'
wall = ifcopenshell.api.root.create_entity(ifc, ifc_class='IfcWall', name='Wall1')
ifcopenshell.api.spatial.assign_container(ifc, relating_structure=space, products=[wall])

facet = PartOf(name='IFCSPACE', predefinedType='USERDEFINED',
               relation='IFCRELCONTAINEDINSPATIALSTRUCTURE', cardinality='prohibited')
result = facet(wall)
```

IDS requirement: "An element must not be contained in a user-defined-type
`IfcSpace`." The wall genuinely is contained in a userdefined-type space.

- **Verdict obtained (before fix): `PASS`** — `is_pass=True`,
  `reason={'type': 'PROHIBITED'}`
- **Correct verdict: `FAIL`** — the prohibited relationship exists.

The mirror `cardinality='required'` case gives the opposite wrong answer:

- **Verdict obtained (before fix): `FAIL`** — `is_pass=False`,
  `reason={'type': 'PREDEFINEDTYPE', 'actual': 'CustomSpace'}`
- **Correct verdict: `PASS`** — the required relationship exists.

This is the severe case: an IDS author writing "no element may sit in a
user-defined space/zone/group/nest/opening host" gets a clean PASS report on
a model that violates the rule.

### All 6 branches verified, before and after the fix

Each branch was independently built and run (IFC4, real API-created models,
type-relationship-driven `PredefinedType="USERDEFINED"`, `predefinedType`
resolved through `get_type()` where the class needs a type object to carry
`PredefinedType`, e.g. `IfcSpaceType`, `IfcWallType`, `IfcTaskType`,
`IfcFurnitureType`, `IfcDoorType`, or through the bare-attribute fallback for
classes with no type object, e.g. `IfcInventory`/`IfcZone`):

| Branch | Before fix (prohibited / required) | After fix (prohibited / required) |
|---|---|---|
| no relation (ancestor walk) | PASS / FAIL (wrong both ways) | FAIL / PASS (correct) |
| `IFCRELAGGREGATES` | PASS / FAIL | FAIL / PASS |
| `IFCRELASSIGNSTOGROUP` | PASS / FAIL | FAIL / PASS |
| `IFCRELCONTAINEDINSPATIALSTRUCTURE` | PASS / FAIL | FAIL / PASS |
| `IFCRELNESTS` | PASS / FAIL | FAIL / PASS |
| `IFCRELVOIDSELEMENT IFCRELFILLSELEMENT` | PASS / FAIL | FAIL / PASS |

### Fix

Added `PartOf.predefined_type_matches()`, mirroring `Entity.__call__`'s
existing literal-`"USERDEFINED"` handling, and used it at all 6 call sites
instead of the direct `==`/`!=` comparison against `get_predefined_type()`.
Scope kept to the literal-string case that `Entity.__call__` already handles
(pre-#8253); the `Restriction`-enumeration-including-`USERDEFINED` case for
`Entity` is #8253's separate, already-open fix and was not duplicated here.

`src/ifctester/ifctester/facet.py`:
- `PartOf.predefined_type_matches()` (new helper)
- 6 call sites updated: the no-relation ancestor walk,
  `IFCRELAGGREGATES`, `IFCRELASSIGNSTOGROUP`,
  `IFCRELCONTAINEDINSPATIALSTRUCTURE`, `IFCRELNESTS`,
  `IFCRELVOIDSELEMENT IFCRELFILLSELEMENT`

`src/ifctester/test/test_facet.py`: added `USERDEFINED`-itself coverage
(required and prohibited) to all 6 branches. Two of the six branches (the
no-`relation` ancestor walk and `IFCRELVOIDSELEMENT IFCRELFILLSELEMENT`) had
**zero** prior test coverage of any kind; basic pass/fail coverage was added
for those alongside the `USERDEFINED` regression tests.

## Considered and not pursued

- **`Specification.minOccurs`/`maxOccurs` as exact numeric bounds** (e.g.
  `minOccurs=2`): `Specification.validate()` only branches on "zero
  applicable entities" for the required/prohibited cases, never on an exact
  count. This looks like it could under-enforce a `minOccurs=2` spec with
  only 1 applicable entity. Not pursued as a bug: the `Cardinality` type
  used throughout the codebase (`facet.py`, `ids.py`) is a strict
  `required`/`optional`/`prohibited` ternary, `get_usage()`/`set_usage()`
  only ever produce `{0,1,unbounded}` combinations, and no test fixture or
  IDS example in the repo uses any other value. Flagging this without
  checking the buildingSMART IDS documentation's stated intent for
  non-`{0,1,unbounded}` `minOccurs`/`maxOccurs` risks the "spec being odd,
  not code being wrong" trap; left as an open question rather than a claimed
  defect.
- **`Attribute`/`Classification`/`Property` case-sensitivity and casting**:
  re-checked every `==`/`!=`/`cast_to_value` site outside the branches
  already fixed by #9058/#9059/#9188. All remaining comparisons are either
  intentionally case-sensitive (matches the IDS spec's literal string
  matching for names/systems/references) or already routed through
  `cast_to_value`/`is_x` with symmetric tolerance handling verified correct
  for both positive and negative bounds.
- **Reporter layer**: read `reporter.py` end to end (`Console`, `Txt`,
  `Json`, `Html`, `Ods`, `OdsSummary`, `Bcf`). The one remaining
  verdict-affecting computation, `Json.report_specification`'s
  `total_fail = len(requirement.failures)`, is exactly the site #9190
  already fixes. No further wrong-verdict computation found; `Ods`/`Html`/
  `Bcf` all consume the already-corrected `Json` results without
  re-deriving pass/fail counts.

## Measured ratio

1 verdict-affecting defect found and fixed (`PartOf` USERDEFINED
`predefinedType`, a false PASS on `prohibited` and a false FAIL on
`required`, across 6 branches) out of the systematic re-check of every
`facet.py` `__call__` branch not already covered by #9187-#9190, #9058,
#9059, #9142, #8407, #8292, #8253, #8161, plus a full re-read of
`reporter.py`. Two previously-untested `PartOf` branches (no-relation
ancestor walk, voids/fills) gained baseline test coverage as a side effect.

## Verification

- Baseline (before any change): `pytest -p no:pytest-blender test/` under
  the scratch python-3.13.6 interpreter (rsynced `.py` sources over the
  built `.so` files, `ifcopenshell.__file__`/`ifctester.__file__` confirmed
  resolving into the scratch copy) — 37 passed.
- After fix + new tests: 37 passed (test count unchanged; new assertions
  were added inside existing test methods, one new import
  `ifcopenshell.api.feature`).
- `black`/`ruff` clean on `facet.py` and `test_facet.py`.

## Branch

`bimvoice/fix/ifctester-partof-userdefined`. No PR opened per instructions.
