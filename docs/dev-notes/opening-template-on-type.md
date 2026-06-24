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
template via `update_type_template_from_opening` (creates the template if absent;
re-points the shared map so siblings follow). Hooked at both commit paths:
`UpdateRepresentation._execute` (the `edited_objs` path) and
`OverrideModeSetObject` after `edit_representation_item` (the in-place item edit). The
older `edit_openings`/`is_edited` path also calls it. `set_type_opening_representation`
has replace semantics (one `Reference` map per type).

## Status — implemented (manually verified in Blender)

- core `map_type_representations.py`: skip `Reference` maps.
- `model/opening.py`: `get_/set_type_opening_representation`, `promote_opening_to_type`,
  `update_type_template_from_opening`, `preserve_opening_on_type_change`;
  `generate_opening_from_filling` consults the template; PR1 guard removed from
  `_regenerate_from_type`.
- `model/handler.py`: pre + post assign_type listeners.
- `type/operator.py` `DuplicateType`: promote before copy.
- `project/operator.py` `AppendLibraryElement`: `harvest_opening_template`.
- `geometry/operator.py`: write-back hooks in `UpdateRepresentation` and
  `OverrideModeSetObject`; `reimport_element_representations` renders the requested rep.
- `geometry/data.py` + `geometry/ui.py`: `RepresentationIdentifier` column + headers.

Committed as a single commit on branch `opening-template-on-type` (10 files).

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
- Edit a void → type's `Reference` row updates; siblings follow; survives duplicate.
- Three write-back hooks are intentional (different commit paths) — candidate for
  consolidation in review.
- Re-test against upstream's new `assign_type` (see NOTE under "Type switching").
