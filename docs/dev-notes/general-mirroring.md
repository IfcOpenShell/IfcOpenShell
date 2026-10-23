<!-- This file was generated with the assistance of an AI coding tool. -->

# general-mirroring — working notes (PR #7003)

A living note for this branch: findings that outlive a review comment, so whoever picks
the branch up next does not re-derive them. Not user documentation — drop it or promote
the durable parts when the PR merges.

---

## Open: duplicated mapped types share their body geometry

**Status: known defect, deliberately deferred. Nothing has been changed for it.**

### What happens

`2a9b262fa2` — *"copy_representation: preserve MappedRepresentation structure for
IfcTypeProduct"* — rewrote the `IfcTypeProduct` branch of `tool/root.py`
`Root.copy_representation`. It is on this branch, and `src/bonsai/bonsai/tool/root.py` is
in this PR's diff, so it ships with #7003. It is **not** in `v0.8.0`, so no released Bonsai
is affected — which is why this is a note here rather than a bug report.

The representation map is now copied **shallowly**, and a nested mapped representation is
special-cased:

```python
new_map = ifcopenshell.util.element.copy(tool.Ifc.get(), rep_map)   # shallow
if (source_rep.RepresentationType == 'MappedRepresentation' and
    len(source_rep.Items) == 1 and source_rep.Items[0].is_a("IfcMappedItem")):
    new_rep = ifcopenshell.util.element.copy(tool.Ifc.get(), source_rep)
    new_rep.Items = [ifcopenshell.util.element.copy(tool.Ifc.get(), item) for item in source_rep.Items]
    new_map.MappedRepresentation = new_rep
else:
    new_map.MappedRepresentation = ifcopenshell.util.element.copy_deep(...)
```

The copied `IfcMappedItem` keeps the **original's** `MappingSource`, so everything beneath
it — the inner `IfcRepresentationMap`, its `IfcShapeRepresentation`, the
`IfcExtrudedAreaSolid`, the profile — is shared with the source type. For a type whose
`RepresentationMap.MappedRepresentation` is *itself* a `MappedRepresentation` (Revit-style
nested blocks), `bim.duplicate_type` therefore yields an alias rather than a copy: edit
Type B's geometry and Type A changes with it.

### Measurements

Synthetic `IfcMemberType` with one level of nesting (a single `IfcMappedItem`), duplicated
via `root.copy_class` plus each `copy_representation` strategy:

| strategy | nesting preserved | underlying geometry |
|---|---|---|
| `v0.8.0` (`copy_deep` on the whole map) | yes | **separate** |
| this branch (`2a9b262fa2` mapped branch) | yes | **shared** |

**The commit's stated rationale does not hold on this input.** `copy_deep` was already
preserving the nested `MappedRepresentation` structure, so the special case does not buy
the structural preservation it claims — it only costs geometry independence.

### Ruled out — do not re-chase

The same shallow `copy(rep_map)` also leaves the copy pointing at the original's
`MappingOrigin`, on *every* duplicated type rather than only nested ones. This is harmless.
Nothing in Bonsai or ifcopenshell writes to an existing `MappingOrigin` — it is only ever
created fresh (`api/geometry/assign_representation.py`, `api/geometry/map_representation.py`,
`bim/module/model/profile.py`) and read (`util/placement.py`) — and it is always an identity
placement.

### Why deferred rather than reverted

- The measurement used **one synthetic shape**: a single mapped item, one level of nesting.
  Real Revit output may carry several items per representation, deeper nesting, or shape
  aspects, and `copy_deep` may genuinely misbehave on those — presumably the case that
  motivated the commit in the first place. Reverting on one synthetic input would trade a
  known bug for an unknown one.
- No model on hand is known to contain such a type. The bug report that led here involved
  `IfcFurnitureType` cabinets whose types have **no `RepresentationMaps` at all** (geometry
  lives on the occurrences), so `copy_representation` returns early and this code never runs
  for them.

### What would settle it

1. Scan real Revit imports for types where
   `RepresentationMaps[n].MappedRepresentation.RepresentationType == 'MappedRepresentation'`.
2. **If none exist anywhere** — delete the special case and let `copy_deep` handle every
   map, i.e. revert this part of `2a9b262fa2`.
3. **If some exist** — that is the real input the commit was written for. Test `copy_deep`
   against it first. If it copes, revert as above. If it does not, keep the branch but give
   the copy its own `MappingSource` (deep-copy the inner `IfcRepresentationMap`), which
   preserves the nesting *and* the independence.
4. Either way, the invariant to hold is that a duplicated type must not share its body with
   its source.

### Related

The same failure class — a "copy" that silently keeps pointing at the original — was found
and fixed in `core/type.py` for material usages under PR #8658. Worth keeping in mind when
touching any of the `copy_*` paths.
