<!-- This file was generated with the assistance of an AI coding tool. -->

# Occurrence representations — copy-drop fix, Type/Occurrence panel split, promote & add-to-occurrence

> **Living dev note** for the `occurrence-representations` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention.

Tracking issue: [#8788](https://github.com/IfcOpenShell/IfcOpenShell/issues/8788) (copy-drop
bug + the four related feature requests). The PR should close it (`Closes #8788`).

Stacked on top of `dev-notes-system` (#8201) → `opening-template-on-type` (#8200) →
`select-by-representation-type` (#7916), because it shares the Representations panel and
`RepresentationsData`. The panel here already carries the stack's header row +
`RepresentationIdentifier` column + `bim.select_by_representation_type` button; this branch
adds the Type/Occurrence split, the promote button, and the add dialog toggle on top.

## Problem

Copying an occurrence that is connected to a type **drops** any occurrence-local
representation whose context the type has no `RepresentationMap` for — e.g. a per-occurrence
`Model/Body/PLAN_VIEW`. Repro: an `IfcFurniture` occurrence with a mapped `Body/MODEL_VIEW`
+ `Box/MODEL_VIEW` from the type **and** its own local `Body/PLAN_VIEW`; Shift+D loses the
PLAN_VIEW.

Root cause: `core.root.copy_class` takes the type branch and calls
`type.map_type_representations`, which **wipes all of the occurrence's representations and
re-maps only the type's** `RepresentationMaps`. Anything the occurrence had that the type
doesn't provide is gone. (The no-type branch, `copy_representation`, copies everything
faithfully — hence the asymmetry.)

## Key facts established

- Schema (IFC4 ADD2 TC1): an occurrence **may** carry representations the type has no map
  for. `IfcProduct.Representation` is its own attribute; the only WHERE rule is
  `PlacementForShapeRepresentation`. Nothing forces occurrence reps to derive from the type —
  the type→occurrence `IfcMappedItem` mapping is *convention*, not a constraint. So a local
  `PLAN_VIEW` on one occurrence is spec-valid, not corruption.
- `root.copy_class` (the IFC API) explicitly `remove_representations` on the copy, so the new
  element starts with **zero** reps; the type branch then re-maps only the type's.
- `geometry.assign_representation` **redirects a non-mapped rep to the type** when the product
  is an occurrence whose type has `RepresentationMaps` (and isn't a profile/layer-set type;
  see #6934). This is a landmine: you cannot "add a rep to an occurrence" through that API in
  the typed case — it silently lands on the type and maps to every occurrence. Bypassed here
  by appending straight to the occurrence's `IfcProductDefinitionShape`.
- The panel's old `*` suffix on `RepresentationType` (data.py) was the *only* signal that a
  rep was mapped/inherited, and nothing parsed it — confirmed (all functional readers use
  `representation.RepresentationType` off the entity, not the panel dict string). Removed in
  favour of the explicit Type/Occurrence split.
- Interaction with #8200: this branch's `map_type_representations.py` already skips `Reference`
  maps. Complementary — my `copy_class` fix re-adds occurrence-only reps *after*
  `map_type_representations` runs; it keys off "context not in the type's `RepresentationMaps`",
  so a type `Reference` map in the same context is *not* re-added as an occurrence rep.

## Design

Four connected pieces, all around occurrence-local vs type-mapped reps.

### 1. Copy-drop fix

`tool.Root.copy_occurrence_only_representations(source, dest, relating_type)` runs in
`copy_class` right after `map_type_representations`. It deep-copies (sharing contexts,
preserving named profiles) each source rep whose `ContextOfItems` is **not** among the type's
`RepresentationMaps` contexts, and **appends directly** to `dest.Representation` — *not* via
`geometry.assign_representation` (which would redirect onto the type; see landmine above).

### 2. Type / Occurrence panel split

`RepresentationsData` (geometry/data.py) gains `is_mapped`
(`resolve_representation(rep) != rep`, i.e. the rep is an `IfcMappedItem` from the type),
`element_is_type`, and `element_has_type`. `BIM_PT_representations` (geometry/ui.py) lists
mapped reps under a **Type** header (`LINKED`) and local reps under an **Occurrence** header
(`OBJECT_DATA`); a type element shows a flat list. Rows are drawn via a shared
`draw_representation_row` helper that also carries the stack's `RepresentationIdentifier`
column + `select_by_representation_type` button.

### 3. Promote to Type

`bim.promote_representation_to_type` (`EXPORT` icon on Occurrence rows, only when
`element_has_type`) → `core.geometry.promote_representation_to_type`. Copies the local rep onto
the type as a new `RepresentationMap` (`tool.Geometry.add_type_representation_map`), then for
each occurrence of the type in the same context:

- **identical** local rep → removed (`core.remove_representation`), occurrence inherits the
  type's mapped rep (`map_representation` + `assign_representation`, which does *not* redirect
  because the rep is now a `MappedRepresentation`);
- **divergent** local rep → left entirely untouched (keeps its override, is not mapped);
- **no** local rep → inherits the mapped rep.

"Identical" = `tool.Geometry.representations_are_identical`: canonical serialization ignoring
STEP ids and the shared context; styles (inverse `IfcStyledItem`) are not compared. Comparison
is against the **type copy**, not the original — the original is removed mid-loop when the
source occurrence is processed. User chose "only identical ones" removed (vs "all in context"
or "only this occurrence"); divergent occurrences stay exactly as they were.

### 4. "Add to Occurrence" toggle

`bim.add_representation` gains `add_to_occurrence` (default **off**, `SKIP_SAVE`), shown in the
add dialog only for an occurrence with a type. `core.geometry.add_representation` gains
`add_to_occurrence=False`; when True (and not a type element) it calls
`tool.Geometry.assign_representation_to_occurrence` (direct shape append) to bypass the
redirect-to-type. **Off preserves existing behaviour exactly** (assign_representation decides,
redirecting to the type only when the type already has maps; an empty type still lands on the
occurrence) so the many internal callers of `add_representation` are unaffected. On = force a
local occurrence override.

## Status — implemented (algorithm verified standalone; not yet driven in live Blender)

- `core/root.py` `copy_class`: calls `copy_occurrence_only_representations`; **diagnostic
  `print("[copy_class] …")` statements + `_ctx_str` helper are still in** (kept intentionally
  for repro — strip before merge).
- `tool/root.py`: `copy_occurrence_only_representations`.
- `tool/geometry.py`: `copy_representation_deep`, `assign_representation_to_occurrence`,
  `add_type_representation_map`, `representations_are_identical`.
- `core/geometry.py`: `promote_representation_to_type`; `add_representation` gains
  `add_to_occurrence`.
- `core/tool.py`: interface decls for the four new `Geometry` methods.
- `bim/module/geometry/operator.py`: `PromoteRepresentationToType`; `AddRepresentation`
  `add_to_occurrence` prop + dialog + pass-through.
- `bim/module/geometry/{data,ui}.py`: `is_mapped` / `element_is_type` / `element_has_type`;
  Type/Occurrence grouping merged with the stack's panel columns; `*` suffix removed.
- `bim/module/geometry/__init__.py`: register `PromoteRepresentationToType`.

Standalone check (installed ifcopenshell 0.8.0; repo src isn't compiled for this Python, and
`api.geometry` won't import standalone due to a broken `mathutils` shim) reproduced source +
identical + divergent occurrences: identical consolidate to mapped, divergent keeps its local
override, type ends with both maps; comparator returns identical-across-separate-graphs = True,
divergent = False, context-ignored = True.

## Things to test / verify

- Shift+D an occurrence with a local `PLAN_VIEW` the type lacks → the copy keeps the PLAN_VIEW
  and it renders in a plan drawing.
- Copy fix vs #8200: an occurrence with a type `Reference` opening template — confirm the copy
  doesn't spuriously re-add a `Reference` occurrence rep, and openings still boolean.
- Promote: identical siblings consolidate and their drawings still show the plan; a **divergent**
  sibling keeps its own geometry and does *not* pick up the type's; the source occurrence ends
  with only the mapped rep. Exercise `remove_representation`'s Blender mesh/data-link side
  effects (the standalone test doesn't cover those).
- `representations_are_identical` on real authored geometry (float exactness): separately
  authored "same" plans may compare unequal → treated as divergent (safe direction, no delete).
- Add-to-Occurrence off → typed occurrence rep lands on the type (existing behaviour); on →
  stays local; toggle hidden for typeless elements and for type elements. Confirm no regression
  in internal `add_representation` callers (wall/opening creation, `assign_class`).
- Panel: Type vs Occurrence grouping correct for occurrence, typed occurrence with no local
  reps (only Type header), typeless element (only Occurrence), and a type element (flat list);
  columns still align with the stack's header row.
- Strip the `copy_class` diagnostic prints before merge.
