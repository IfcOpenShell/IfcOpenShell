<!-- This file was generated with the assistance of an AI coding tool. -->

# Opening template on type — preserving custom openings across duplicate_type / append

> **Living dev note** for the `opening-template-on-type` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention.

## Problem

`bpy.ops.bim.duplicate_type` and `bpy.ops.bim.append_library_element` lose a custom
`IfcOpeningElement` body (e.g. an `IfcPolygonalFaceSet`/tessellation) and replace it
with a generated extrusion. Root cause: the only mechanism that preserved a custom
opening was "copy it from a sibling occurrence of the same type"
(`get_existing_opening_occurrence_if_any`), which returns nothing for a brand-new
type. `generate_opening_from_filling` then always builds an extrusion (profile or
bbox), discarding the custom geometry.

## Key facts established

- IFC-level `root.copy_class` already `copy_deep`s opening representations; the loss
  happens on the Bonsai side (the `regenerate_from_type` listener on
  `type.assign_type`, and placement-time generation).
- Opening occurrences of one type already **share** a single `IfcRepresentationMap`
  via mapped representations — that is why editing one void edits them all
  (see `tool.Model.unshare_opening_representation` docstring). Bonsai shares, it does
  not copy. The shared map just has no durable home (it is hosted implicitly by
  whichever occurrence exists), so it does not survive to a new type.
- IFC4 ADD2 TC1 `IfcShapeRepresentation`: identifier **`Reference`** = "3D
  representation that is **not part of the Body representation** ... used, e.g., for
  opening geometries ... excluded from an implicit Boolean operation." Schema-valid;
  `IfcTypeProduct` has no uniqueness rule on `RepresentationMaps` (only
  `ApplicableOccurrence`). So a `Reference` map can sit beside the `Body` map.
- The geometry kernel selects an opening's geometry **by context, not by
  `RepresentationIdentifier`** (`mapping::representation_of`, `ifcgeom/mapping/mapping.cpp`).
  So a `Reference`-identified opening in the Body context still booleans correctly.
  Nothing in Bonsai reads `"Reference"` to *skip* applying an opening.
- Caveat: IFC has no type-level void (`IfcRelVoidsElement` is occurrence-only). The
  "opening template on type" is therefore a Bonsai convention using a spec-valid
  identifier; other tools see a harmless extra `Reference` rep they ignore. The
  regeneration smarts are Bonsai-only by necessity.

## Design

Store the shared opening body on the **type** as a `Reference` representation map.
Because `bim.duplicate_type` (`tool.Root.copy_representation`) and
`append_type_product` both copy a type's `RepresentationMaps`, the template survives
both. Occurrence openings map over the same map, so editing a void rewrites the
shared map = updates the type template in one stroke (no separate write-back needed).

`map_type_representations` must skip `Reference` maps so the window/door occurrence
does not receive the opening shape as its own Body (the kernel would otherwise pick
arbitrarily between the real Body and the opening rep). The skip is both required and
spec-endorsed ("not part of the Body representation").

### Body-context coexistence (Option A)

The template lives in the **Body** subcontext (required: the instance opening that maps
over it must resolve in Body context for the geometry kernel to subtract it). So the
type holds two reps in one context: the `Body` window body and the `Reference` opening
template. Per IFC, `Reference` is a *RepresentationIdentifier value used within the Body
context*, not a separate context - so we keep it there and disambiguate elsewhere:

- The representations panel now shows `RepresentationIdentifier` as its own column
  (`geometry/data.py`, `geometry/ui.py`) so the two Body-context reps are
  distinguishable (`Model | Body | MODEL_VIEW | Reference | Tessellation`). The panel
  column previously read "Body" because it shows `ContextOfItems.ContextIdentifier`,
  not the representation's identifier.
- `Geometry.reimport_element_representations` type branch now renders the requested
  `base_representation` instead of `get_representation(element, context)`, which matched
  only by context and returned the window body when switching to the `Reference` rep.
  This is what makes "switch to the Reference row" actually show the void on the type.

### Precedence in `generate_opening_from_filling`
type `Reference` template → (existing sibling occurrence, checked by callers) →
type `Profile` extrusion → bbox extrusion.

### Type switching (assign_type)

On `type.assign_type` the opening is rebuilt to reflect the **assigned** type's void.
Two listeners in `model/handler.py`:

- **pre** `Bonsai.Opening.PreserveOnTypeChange` → `preserve_opening_on_type_change`:
  before the filling moves to the new type, `promote_opening_to_type(old_type)` anchors
  the old type's custom void as a template, so it isn't lost when (possibly the last)
  occurrence is regenerated. Idempotent; custom voids only.
- **post** `Bonsai.Opening.RegenerateFromType` → `regenerate_from_type` →
  `_regenerate_from_type`: rebuilds from the new type's template / sibling / extrusion.
  The old PR1 "preserve custom" guard was **removed** here — it kept the previous type's
  void on a switch (wrong), and the template now makes preservation unnecessary.

NOTE: upstream `v0.8.0` landed `assign_type` changes + new `test_assign_type_*` tests
(merged under this branch's base). The listeners ride on top of that — re-test the
switch/edit round-trips against the new `assign_type`.

### Write-back on void edit

Editing an occurrence's void writes the new geometry back to the type's `Reference`
template via `update_type_template_from_opening` (creates the template if absent), then
**re-maps every occurrence's opening onto the template** and reloads the affected host walls
(`switch_representation`) so they re-boolean. The re-map (`_remap_opening_to_template`) is the
key part: an earlier version only re-pointed a *pre-existing* shared map, so siblings whose
openings were **independent** (their own `IfcRepresentationMap`, never sharing the template)
didn't follow — the common real-world case. Now they do. Hooked at both commit paths:
`UpdateRepresentation._execute` (the `edited_objs` path) and
`OverrideModeSetObject` after `edit_representation_item` (the in-place item edit). The
older `edit_openings`/`is_edited` path also calls it. `set_type_opening_representation`
has replace semantics (one `Reference` map per type).

### Preserving adjusted extrusions (duplicate_type)

`is_opening_representation_custom` only flags *non-extrusion* geometry (tessellation, brep,
CSG) as worth preserving — a proxy for "not regenerable". That mis-classifies a *manually
adjusted* extrusion, which is still an `IfcExtrudedAreaSolid`, so a hand-tweaked extrusion
opening was reset to the default on `duplicate_type`.

`promote_opening_to_type` now gates on `should_preserve_opening` = custom **or**
`_is_adjusted_extrusion`. The latter generates the default (`generate_opening_from_filling`,
which yields the default since no template exists at promote time) *transiently*, compares the
two bodies' axis-aligned bounding boxes (1 mm tolerance) via the geom engine, then removes the
temporary default. Divergence ⇒ the extrusion was adjusted ⇒ promote it; a plain default
matches ⇒ left regenerable (not frozen — see the "freeze" discussion). Scoped to the duplicate
path so the generate-and-compare stays out of the hot predicate. Limitation: bbox comparison
misses a shape change that preserves the bbox (upgrade to a vertex-set compare if needed).

## Status — implemented (manually verified in Blender)

- core `map_type_representations.py`: skip `Reference` maps.
- `model/opening.py`: `get_/set_type_opening_representation`, `promote_opening_to_type`,
  `update_type_template_from_opening` (+ `_remap_opening_to_template`),
  `preserve_opening_on_type_change`, `should_preserve_opening` (+ `_is_adjusted_extrusion`,
  `_representation_bbox`); `generate_opening_from_filling` consults the template; PR1 guard
  removed from `_regenerate_from_type`.
- `model/handler.py`: pre + post assign_type listeners.
- `type/operator.py` `DuplicateType`: promote before copy.
- `project/operator.py` `AppendLibraryElement`: `harvest_opening_template`.
- `geometry/operator.py`: write-back hooks in `UpdateRepresentation` and
  `OverrideModeSetObject`; `reimport_element_representations` renders the requested rep.
- `geometry/data.py` + `geometry/ui.py`: `RepresentationIdentifier` column + headers.

Branch `opening-template-on-type` (#8200): initial feature commit + the #7916 build-conflict
ancestry-merge + void-propagation-to-all-occurrences + adjusted-extrusion preservation. The
`docs/dev-notes/` convention itself lives on the stacked branch `dev-notes-system` (#8201).

Still **deferred:** explicit "Apply/Reset to type" operators + a "diverges from type"
indicator; import never auto-writes back. `update_simple_openings` still keeps its
`is_opening_representation_custom` guard (array propagation, same type — left as-is).

## Things to test / verify

- Duplicated/appended type's new occurrence gets the faceset void and it **cuts** the
  wall (kernel selects opening geom by context, so a `Reference`-id rep still booleans).
- `harvest_opening_template` cross-file `file.add`: no duplicate
  `IfcGeometricRepresentationContext` left behind; units (kernel doesn't rescale rep
  coords — same assumption as `append_asset`).
- Switch X→Y→X round-trip restores each type's void; switching to a plain (template-less)
  type gives its default extrusion, not the previous faceset.
- Edit a void → type's `Reference` row updates; **all** occurrences follow (including ones
  that had independent openings) and their host walls re-boolean; survives duplicate.
- `duplicate_type` on a type whose extrusion opening was **manually adjusted** → Type B keeps
  the adjusted extrusion; a type with a plain/default extrusion stays regenerable (not frozen).
- Three write-back hooks are intentional (different commit paths) — candidate for
  consolidation in review.
- Re-test against upstream's new `assign_type` (see NOTE under "Type switching").
