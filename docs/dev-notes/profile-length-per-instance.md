<!-- This file was generated with the assistance of an AI coding tool. -->

# Profile length per-instance — typed vs per-instance length for profile types

> **Living dev note** for the `profile-length-per-instance` branch/PR. Read before working
> on the feature; append decisions and findings as the PR is refined. This is *not* user
> documentation — at merge it is removed or its durable parts promoted to code comments.
> See [README.md](README.md) for the convention.
>
> Tracks feature **#8657**; depends on bug fixes **#8655** (`change_data` None) and
> **#8656** (mapped-profile assign cascade).

## Problem

Revit-exported profile members (e.g. curtain-wall mullions) come in **typed-length**:
the extrusion — including its **length** — lives on the `IfcMemberType` as an
`IfcRepresentationMap`, and every occurrence shares it via an `IfcMappedItem`. Bonsai's
profile tools assume each occurrence owns an editable extrusion (`IfcMemberStandardCase`
style), so on these mapped occurrences the length UI never appears, editing/joining
crashes, changing the type-material bleeds across all instances, and `extend_profile`
flips the origin.

Goal: make **Length** a typed-vs-per-instance property of a profile type, toggle-able in
both directions, without corrupting the shared geometry.

- **Typed length** = geometry (incl. length) on the type's `RepresentationMap`;
  occurrences `IfcMappedItem` it. One length for all instances.
- **Per-instance length** = occurrence has its **own** `SweptSolid` body + its **own**
  `IfcMaterialProfileSetUsage`. Each instance edits its own length (`IfcMemberStandardCase`).

## Key facts established

- **`tool.Model.get_usage_type(el)` returns `"PROFILE"` iff `el` carries an
  `IfcMaterialProfileSet(Usage)`** (checked with `should_inherit=False`). Bonsai gates the
  per-instance profile UI (Length control) on this. A mapped occurrence that only
  *inherits* the type's profile set reports `None` → no Length UI. This is why un-mapping
  must also give the occurrence its **own** `IfcMaterialProfileSetUsage`.
- **The mapped representation is shared.** `bonsai.core.geometry.remove_representation`,
  when handed a mapped rep, resolves it and loops `get_elements_of_type` →
  `switch_from_representation`, i.e. it **cascades to every sibling instance of the type**,
  leaving them empty. Any code that removes an occurrence's mapped body triggers this. This
  is the single biggest hazard and the root of most crashes we saw.
- **Typed length is spec-valid.** A plain `IfcMember` with a mapped body + a profile-set
  usage is valid IFC (just not the `IfcMemberStandardCase` subtype). `IfcMaterialProfileSet`
  has **no length**; length is always in the geometry. So offering typed length is a
  legitimate mode, not a workaround (verified against local IFC4 ADD2 TC1).
- **Two origins, on opposite ends.** Revit places the object's `ObjectPlacement` origin at
  one end of the mullion and the extrusion's own `Position` origin at the other, with the
  object's local **+Z pointing away** from the sweep (local Z runs `-depth → 0`).
  `get_profile_axis` (object bound-box local-Z range) + `DumbProfileJoiner.recreate_profile`
  (which plants the new origin at `body[0]` = min-local-Z) then relocate the origin to the
  far end on extend/join — the "flip". Natively-authored profiles run local Z `0 → depth`,
  so `body[0]` is already the origin and nothing moves.
- **`create_profile` double-bodies mapped types.** `assign_type` (default
  `should_map_representations=True`) maps the type's shared body onto a new occurrence, then
  `DumbProfileGenerator.create_profile` adds a per-instance extrusion on top → two Body reps
  / typed-by-default.
- The wrapper/core were **not** the cause of the crashes we chased for a while — a
  `git reset --hard v0.8.0` reproduced clean, our applied changes reproduced the crash. The
  installed environment is now matched (repo source + release wrapper `3e7b739`, via
  `dev_environment.py`).

## Design

Two explicit operators + a Type-panel toggle, plus defaults/guards so the mapped hazard is
never hit implicitly.

- **`bim.make_profile_length_per_instance`** (un-map; `MakeProfileLengthPerInstance`):
  1. Copy the mapped extrusion items into a new per-instance `SweptSolid` body, **keeping
     the shared `IfcProfileDef`** (`copy_deep(..., exclude=["IfcProfileDef"])`).
  2. **Orphan** the old mapped body (retarget the product shape, do **not** delete it) —
     deleting cascades to siblings, and the raw delete dangles Bonsai's Blender-side links.
  3. Give the occurrence its **own** `IfcMaterialProfileSetUsage` (else no Length UI).
  4. **Normalize placement**: if the object's local +Z points away from the sweep (origin at
     the max-local-Z end), flip 180° about local X and rebuild the extrusion via
     `add_profile_representation` so local Z runs `0 → depth` from the (unchanged) origin.
     This is what stops `extend_profile` flipping the origin.
  - Idempotent / repair-capable: re-running adds a missing usage to an already-un-mapped
    occurrence. Only identity mapping transforms are handled (others are skipped).
- **`bim.make_profile_length_type_driven`** (re-map; `MakeProfileLengthTypeDriven`):
  drop the occurrence's own usage, then `ifcopenshell.api.type.map_type_representations` to
  map the type's shared geometry back on. If the type has **no** `RepresentationMap`
  (Bonsai-authored profile type), first **promote** a copy of the occurrence's body onto the
  type as a `RepresentationMap` (so the first toggled occurrence defines the type's length;
  siblings snap to it).
- **UI toggle** (`type/ui.py` `draw_product_ui`, `type/data.py`, `type/prop.py`): a single
  **Per-instance Length** checkbox. Backed by a `get`/`set` `BoolProperty`
  (`length_per_instance`) — `get` reads the current mode from cached `TypeData` flags
  (`is_typed_length_profile` / `can_make_length_type_driven`), `set` runs the matching
  operator. No stored state to desync.
- **New occurrences default to per-instance** (`DumbProfileGenerator.create_profile`): after
  `assign_type`, drop the inherited mapped reps so only the per-instance extrusion remains.
  No-op for types without a `RepresentationMap`.
- **`recreate_profile` mapped guard** (`DumbProfileJoiner.recreate_profile`): if the body is
  mapped, **skip** the per-instance rebuild (leaving typed geometry alone — a length-driven
  type should stay typed) **but `switch_representation` to reload** so the Blender mesh
  reflects a just-mapped type's geometry. This kills the "assign a length-driven type ⇒
  Failed to set value + sibling turns empty" cascade *and* keeps the typed display fresh.
  Fixes issue **#8656**.
- **`assign_type` preserves per-instance** (`core/type.py`): if the occurrence is already
  per-instance (own non-mapped body + own profile usage), pass
  `should_map_representations=False` so reassigning a type keeps its own geometry/length
  instead of converting it to typed. (Side effect: it also keeps its own profile/material;
  fine when all types share one profile — revisit if reassigning across different profiles.)

## Supporting bug fixes (separate from the feature)

- **`tool/geometry.py` `change_data`** — guard `has_data_users`/`delete_data` against a
  `None` `old_data` (empty→mesh reload path). Real Bonsai bug, exposed by the re-map reload;
  filed as **#8655** — worth its own commit.
- **`ifcopenshell/util/placement.py` `get_axis2placement`** — numpy-2.x `x.resize(3)` fix
  for 2D `RefDirection`. **Duplicate of open PRs #8307 / #8586** — kept locally only so
  profile editing works during testing; **do not commit**, drop when #8307 merges.

## Dead ends (ruled out)

- Auto-un-mapping during `type.assign_type`/`regenerate_profile` → sibling cascade. Un-map
  is an **explicit** action only.
- Deriving depth from `obj.bound_box` for un-map → unreliable when several instances share a
  Blender mesh; use the copied extrusion / native rebuild instead.
- Blaming the compiled wrapper / core (`3e7b739`) for the profile crashes — it was our code.

## Test checklist / what's left before merge

- [ ] **Strip debug prints**: `make_length_per_instance` / `make_length_type_driven`,
      `DumbProfileJoiner.recreate_profile` + `get_profile_axis`, and `core/type.py`
      `assign_type`.
- [ ] Un-map a mullion → own length, Length UI, geometry unchanged, siblings untouched.
- [ ] `extend_profile('T')` on an un-mapped mullion → origin **stays** (no flip).
- [ ] Toggle checkbox both ways → round-trips; typed snaps to type length.
- [ ] New occurrence of a mapped type → defaults to per-instance.
- [ ] Assign a length-driven type to a **typed** occurrence → adopts type length, no cascade.
- [ ] Assign another type to a **per-instance** occurrence → stays per-instance, keeps length.
- [ ] Edge cases untested: non-identity mapping transforms; non-centroid cardinal point vs
      the 180° flip; reassigning across types with **different** profiles.
- [ ] Commit layout: feature on `1c421d0`; separate `change_data` fix; exclude `placement.py`.
