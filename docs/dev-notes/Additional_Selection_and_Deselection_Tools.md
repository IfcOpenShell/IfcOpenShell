<!-- This file was generated with the assistance of an AI coding tool. -->

# Additional selection and deselection tools — uniform modifier scheme for select operators

> **Living dev note** for the `Additional_Selection_and_Deselection_Tools` branch/PR.
> Read before working on the feature; append decisions and findings as the PR is
> refined. This is *not* user documentation — at merge it is removed or its durable
> parts promoted to code comments. See [README.md](README.md) for the convention.

## Problem

Bonsai's many "select …" buttons (by class, by type, by material, by container, by
group, by aggregate, by similar value) could only **add** to the selection. There was
no way to subtract matches from a large selection, or to narrow a selection down to
just the matches. `bim.select_similar` had grown a SHIFT+Click
`remove_from_selection`, but nothing else had it, and each operator had accumulated
its own ad-hoc modifier bindings.

## Design

One modifier scheme, applied uniformly across nine operators:

| Modifier | Action |
|---|---|
| Click | select matches (additive) |
| SHIFT+Click | **remove** matches from the selection set |
| CTRL+Click | **filter** the selection to matches only (selects nothing new) |
| CTRL+SHIFT+Click | legacy plain-CTRL function, where one existed |
| ALT+Click | also unhide matches (viewport + local hide) — from the base branch |
| CTRL+ALT+Click | `select_similar`, `select_similar_type`, `select_by_material`, `select_group_elements`, `select_aggregate`: regex-search dialog (see below) |

Operators covered: `bim.select_similar`, `bim.select_ifc_class`,
`bim.select_similar_type`, `bim.select_by_material`, `bim.select_similar_container`,
`bim.select_decomposed_elements`, `bim.select_group_elements`,
`bim.select_aggregate`, `bim.select_linked_aggregates`.

### Key decisions and the why

- **Remove/filter criteria come from the active object only** (not all selected
  objects), following `SelectSimilar._get_reference_values`. If criteria came from
  every selected object, a SHIFT/CTRL click would typically match — and wipe or keep —
  the entire selection, which is useless. Plain Click keeps the old behavior
  (criteria from all selected objects). Operators whose criteria come from the
  clicked UI item (material, group, container row) are unaffected by this rule.
- **Filter mode selects nothing new.** It computes the matched set and deselects
  already-selected objects outside it. Implemented centrally in
  `Spatial.select_products(products, unhide=..., remove=..., filter_selection=...)`
  (`tool/spatial.py`) for the UI-item operators, and as small per-operator branches
  where selection is done with bespoke loops (`select_similar`, `select_ifc_class`,
  `select_similar_type`, the two aggregate operators).
- **CTRL = filter, CTRL+SHIFT = legacy CTRL function.** Originally implemented the
  other way around; swapped after review because the two selection-set operations
  (subtract, intersect) belong on the simple modifiers. The demoted plain-CTRL
  functions are: one-level-deep (`select_aggregate`, `select_similar_container`,
  `select_decomposed_elements`), exclude-children (`select_group_elements`), and
  calculate-sum (`select_similar`). Existing muscle memory for those will now hit
  the filter instead — deliberate trade-off.
- **Modifiers resolve exclusively** in every `invoke`: SHIFT means remove only when
  CTRL is up, CTRL means filter only when SHIFT is up, so combos are unambiguous.
- **Aggregate operators keep the current selection in remove/filter mode.** Their
  normal flow deselects the seed selection before selecting targets; doing that in
  remove/filter mode would destroy the very selection being edited
  (`keep_current_selection` in `aggregate/operator.py`).
- **`select_ifc_class` filter matches subtypes** (`element.is_a(cls)`), consistent
  with normal select mode which uses `file.by_type(cls)` (also subtype-inclusive).

### Regex-search dialog on `select_similar`, `select_similar_type`, `select_by_material`, `select_group_elements`, `select_aggregate` (CTRL+ALT+Click)

On `select_aggregate` the pattern is prefilled with the active object's **aggregate
name** and matched against every `IfcRelAggregates.RelatingObject` that `is_a
IfcElement` (spatial decomposition — project/site/storey — deliberately excluded);
the dialog additionally exposes "Also Select Parts" (+ "One Level Deep") since the
panel's two button variants collapse into one dialog. Union of matched aggregates
(+ parts via `get_parts`/`get_decomposition`) through one `Spatial.select_products`
call; clipboard query `parent = /.*foo.*/`.

On `select_similar_type` the pattern is prefilled with (and matched against) the active
object's **type name**; the clipboard query is `type = /.*foo.*/`. On
`select_by_material` it is the active object's **resolved material name** (via the
#7940 helpers: usage → set, clicked-layer index as hint, `_get_name`), falling back to
the clicked material row's name; clipboard query `material = /.*foo.*/`. On
`select_group_elements` it is the clicked group row's **name**, matched against all
`IfcGroup` names in the file (unnamed groups never match); the union of the matching
groups' elements (recursive by default) goes through a single
`Spatial.select_products` call — union first, so FILTER cannot wrongly intersect
per-group; clipboard query `group = /.*foo.*/`. Otherwise identical to the
`select_similar` behavior below.

Opens a props dialog prefilled with the active object's value for the clicked key; the
(possibly edited) text is compiled as an unanchored Python regex (`re.search`, so
entering `foo` behaves like `.*foo.*`) and applied via an Add / Remove / Filter
dropdown, plus an "Also Unhide Hidden Objects" checkbox (reuses `should_unhide`; in
Add/Remove it sweeps `scene.objects` instead of `visible_objects` and clears both
hide flags on matches; a no-op in Filter since selected objects are visible). CTRL+ALT was free in practice: ALT (unhide) is a no-op in filter mode, which
plain CTRL triggers. Invalid patterns error out and cancel. The equivalent selector
query (`Key = /.*foo.*/`) is copied to the clipboard. Note the prefill is the raw
value — values containing regex metacharacters (e.g. `(`) need escaping before OK.
Overriding `draw()` for the dialog means the F9 redo panel no longer auto-lists the
operator's internal properties for normal runs (it was exposing internals anyway).

### Deliberately overwritten SHIFT bindings (to be reworked later)

Two operators already used SHIFT; the owner chose to overwrite them and revisit with
another approach:

- `bim.select_ifc_class`: SHIFT used to mean "also match Predefined Type". The
  `should_filter_predefined_type` property still exists but has **no key binding**.
- `bim.select_decomposed_elements`: SHIFT used to mean "select all listed elements"
  (itself moved from ALT when ALT became unhide). `should_filter` still exists,
  default True, **no key binding**.

## Status — implemented

Branched from `Unhide_with_alt_click` (ALT+Click unhide across the same operators,
plus container tools in the spatial decomposition panel). Commits so far:

- `3c6d08fabf` SHIFT+Click remove-from-selection (criteria from active object).
- `11be7e2b62` CTRL+Click filter-selection + the CTRL / CTRL+SHIFT swap.

Files: `tool/spatial.py`, `core/tool.py`, `core/material.py`, `core/spatial.py`, and
`bim/module/{search,spatial,type,material,group,aggregate}/operator.py`. All
tooltips document the scheme. Syntax-checked; not yet exercised in Blender.

## Things to test / verify

- Each operator × each modifier, but especially:
  - SHIFT with a large selection: only objects matching the *active* object's
    criteria are removed; the rest of the selection survives.
  - CTRL filter: nothing new gets selected (hidden matches must not appear).
  - CTRL+SHIFT still triggers the legacy behavior (one-level-deep etc.) and does
    **not** also remove/filter.
- `select_ifc_class` remove/filter with a subclass selected (subtype matching).
- Aggregate operators in remove/filter mode: seed selection intact; in normal mode
  behavior unchanged (seeds deselected, aggregates/parts selected).
- `select_decomposed_elements`: the trailing "make active list item the active
  object" block must not re-add it in remove mode nor add it in filter mode.
- `select_similar` calculate-sum on numeric keys now requires CTRL+SHIFT; its
  tooltip line renders only for numeric values.
- Redo-panel (F9) interaction: all new props are `SKIP_SAVE`, so re-running from the
  panel starts clean.
