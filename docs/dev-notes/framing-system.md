<!-- This file was generated with the assistance of an AI coding tool. -->

# Framing system (branch `framing-system`)

Status: written, with tests:
- the layout solver `ifcopenshell.util.framing` (`test/util/test_framing.py`);
- the 3D geometry and IFC writer
  `ifcopenshell.api.geometry.add_framing_representation`
  (`test/api/geometry/test_add_framing_representation.py`).

Next is Bonsai: the Framing panel, type-to-occurrence regeneration, the constituent set,
and profile write-back. Base: `v0.9.0`.

## Problem

Bonsai's parametric railing has two fixed kinds: `FRAMELESS_PANEL` and
`WALL_MOUNTED_HANDRAIL`. Bonsai has no parametric curtain wall or storefront at all.
These are the same construct: a guide path, profiled members repeating along it and up
it, and infill panels in the cells they make. A railing is a short curtain wall whose
mullions are posts and balusters.

Goal: one generic **framing system** engine. A *type* defines the system (member arrays,
infill, profiles, materials), and each *occurrence* applies it to **its own path and
height**. The first hosts are `IfcRailing` and `IfcCurtainWall` (curtain wall and
storefront). The same model would also cover glass partitions, fences, batten screens and
stud framing (studs, plates and blocking that breaks at studs).

## Decisions so far

- **Generic engine, not railing-specific.** It uses a new `BBIM_Framing` pset,
  independent of `BBIM_Railing`. The legacy railing kinds stay as they are, and
  `tool.Parametric.is_railing` (keyed on `BBIM_Railing`) is unaffected.
- **Repetition resets per path segment** by default; an option spreads it across the
  whole path.
- **One element per host for now, railings and curtain walls alike.** Members are shape
  items of the host's own Body (`BODY` output), which keeps Blender fast. `PARTS` output
  (aggregates) is deferred.
- **Height is a typed-in occurrence value**, the way wall height works now: a default
  comes from the tool settings at creation, and it can be edited per occurrence. It is not
  derived from storeys or the path.
- **The existing railing system is not touched.** `FRAMELESS_PANEL`,
  `WALL_MOUNTED_HANDRAIL` and `BBIM_Railing` stay as they are. Framing is a separate tool
  that can also be used on an IfcRailing. No migration and no replacement for now.

## The (u, v) domain

Everything is defined in a 2D domain laid onto the guide:

- `u` is the distance along the guide path. Repetition resets at each path vertex
  unless whole-path mode is on.
- `v` is the height above the path at `u`. On a stair, the path rises and `v` rides on
  it. On a curtain wall, the path is level.
- Members are lines of constant `u` (verticals) or constant `v` (horizontals). Infill
  fills the cells between them.

The solver works purely in (u, v) and returns members and cells. A separate *guide
mapping* turns (u, v) into 3D. Phase 1 uses a vertical ruled surface over a polyline,
which covers railings, curtain walls and storefront. Sloped glazing and skylights only
need a second mapping, with `v` running up a tilted plane; the solver is unchanged.

## System model (type-level JSON)

The type holds an ordered list. Each entry is an array of one of three kinds.

### Vertical member (posts, balusters, mullions, studs)

- Spacing modes:
  - `FIXED`: the remainder is centred.
  - `MAX`: equal bays, no wider than the value.
  - `COUNT`: a fixed number per segment.
- `at_ends` / `at_corners`.
- `within`: spaces this array inside the bays of another vertical array. Examples are
  balusters between posts, and intermediate mullions between primary ones.
- `bottom` / `top` bound: `BASE` (v = 0), `TOP` (occurrence height), an absolute `v`, or
  `{"member": name}`.
- Square or raked cut at sloped bounds.

### Horizontal member (rails, cables, transoms, plates)

- At `v`, or repeating upward between two bounds (`COUNT` / `FIXED`).
- `continuous`, or `breaks_at: [vertical names]`. Each end of a broken member is
  shortened by half the depth of the profile it stops at.

### Infill (glass, spandrel, plate, mesh)

- A cell between left and right bounds (the bays of a vertical array, or the path ends)
  and bottom and top bounds (a member, `BASE`, `TOP` or `v`).
- `thickness`, an `offset` out of the guide plane, and a `gap` to each bound (one value,
  or one per side).
- `max_width` with `joint`: splits a wide bay into equal panels. With no posts, this is
  today's `FRAMELESS_PANEL`.
- Glass, mesh and plate differ only by material; the geometry is one thin solid per
  panel.

### Shared per entry

- `name`: unique, and the reference target.
- `profile`: `{"id": <step id>, "name": <ProfileName>}`; see "Profile and material
  references". Infill has no profile.
- `rotation`, `cardinal_point`, `offset` out of the plane. Curtain wall mullions are
  deep, asymmetric profiles set back from the glass, so these matter.
- No `material` key: an entry's material is the IfcMaterialConstituent named after the
  entry (see below).

## Profile and material references

Decision: keep both rooted in the .ifc, so the JSON holds only layout.

- **Materials:** the type has an `IfcMaterialConstituentSet` with **one constituent per
  entry**. The constituent's Name is the entry name, and its Material is any
  IfcMaterial. Entries that share a material point to the same IfcMaterial. The shape
  aspect for an entry's items has the same name. Changing a material is ordinary Bonsai
  material editing, with no JSON involved. Renaming an entry renames its constituent.
- **Profiles:** IFC4 has no relationship tying a profile to a type
  (`IfcRelAssociatesProfileDef` exists only in IFC4X3, and IFC2X3 has a different one).
  So the JSON stores `{"id", "name"}`:
  - Resolve by step id first, which is stable in NativeIFC. Accept the id only if it is
    still an IfcProfileDef.
  - Otherwise fall back to the name: after append-asset or a copy into another file, ids
    change. When the name resolves, rewrite the id.
  - If neither resolves, report the entry and skip it; do not guess.
- **Purge hazard:** `bonsai.core.profile.purge_unused_profiles` sees only IFC inverses.
  Occurrence bodies use the profiles, but a type with no occurrences references them only
  from JSON, so purging would delete them. Options: teach the purge about
  `BBIM_Framing`, or, in IFC4X3 projects, also write `IfcRelAssociatesProfileDef` from the
  type. To decide when the writer exists.
- **Append-asset of a type** must bring its framing profiles along. Check what
  `api/project/append_asset.py` copies for a type with no representation maps.

## Solver (`ifcopenshell.util.framing`)

- `parse_system(data) -> list[Entry]` validates names, kinds, bounds, references, and
  loops (`within` chains and horizontal-to-horizontal bounds; nothing else can loop).
- `solve(entries, segment_lengths, height, closed, scope, extents) -> FramingLayout`
  works only in (u, v). Profiles enter as `extents[name] = (lo, hi)`, the profile's size
  across the member axis (along u for a vertical, along v for a horizontal). The caller
  takes these from the resolved profile, so the solver never reads IFC.
- Solve order: horizontal levels, then verticals (bounds need levels), then horizontal
  intervals (breaks need verticals), then infill.
- A horizontal is broken only by verticals that actually pass through its extent. A top
  rail sitting on posts that stop at its underside therefore stays continuous, even with
  `breaks_at` set.
- Spacing positions are always interior: `FIXED` does not put members on range ends; use
  `at_ends` / `at_corners` for those. Spacing is centre to centre. A `CLEAR` measure for
  balusters (a 100 mm sphere rule) may be wanted later.
- Bounds that reference a repeating horizontal are rejected in phase 1.
- Running the tests without Blender: a checkout needs a compiled 0.9 wrapper. On Ryan's
  machine that is the git-ignored cp313 wrapper in `C:\IfcOpenShell`, so the tests run
  with Blender 5.1's bundled `python.exe` (3.13; it does not start Blender). Put
  `src/ifcopenshell-python` first on `sys.path` and append Blender 5.1's extension
  site-packages for pytest and shapely. Run pytest with `-o addopts= --noconftest`.
  Mixing a 0.8.5 system install with 0.9 sources does not work.

### Examples

Railing:

```json
{"members": [
  {"name": "Post",    "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_corners": true, "at_ends": true,
   "bottom": "BASE", "top": {"member": "TopRail"}, "profile": {"id": 0, "name": "SHS 50"}},
  {"name": "TopRail", "kind": "H", "v": 1.07, "continuous": true, "profile": {"id": 0, "name": "Cap 60x20"}},
  {"name": "BotRail", "kind": "H", "v": 0.10, "breaks_at": ["Post"], "profile": {"id": 0, "name": "RHS 40x20"}},
  {"name": "Glass",   "kind": "INFILL", "between": "Post", "bottom": {"member": "BotRail"},
   "top": {"member": "TopRail"}, "thickness": 0.012, "gap": 0.02}
]}
```

Storefront (the occurrence height sets `TOP`):

```json
{"members": [
  {"name": "Mullion", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": true, "at_corners": true,
   "bottom": "BASE", "top": "TOP", "profile": {"id": 0, "name": "SF 45x115"}},
  {"name": "Sill",    "kind": "H", "v": 0.0,  "breaks_at": ["Mullion"], "profile": {"id": 0, "name": "SF 45x115"}},
  {"name": "Transom", "kind": "H", "v": 2.4,  "breaks_at": ["Mullion"], "profile": {"id": 0, "name": "SF 45x115"}},
  {"name": "Head",    "kind": "H", "v": "TOP", "breaks_at": ["Mullion"], "profile": {"id": 0, "name": "SF 45x115"}},
  {"name": "Vision",  "kind": "INFILL", "between": "Mullion", "bottom": {"member": "Sill"},
   "top": {"member": "Transom"}, "thickness": 0.025, "gap": 0.006},
  {"name": "Clerestory", "kind": "INFILL", "between": "Mullion", "bottom": {"member": "Transom"},
   "top": {"member": "Head"}, "thickness": 0.025, "gap": 0.006}
]}
```

In the examples `"id": 0` stands for the profile's real step id. Materials come from
the constituents named after each entry, so they are not in the JSON.

The solver builds a dependency graph from `within`, `between`, `bottom`, `top` and
`breaks_at`, and rejects cycles.

## Type applies the system to each occurrence's guide

| Where | What |
|---|---|
| Type | `BBIM_Framing.Data`: the system. `IfcMaterialConstituentSet`. **No Body representation map.** |
| Occurrence | `BBIM_Framing.Guide`: path plus the typed-in height. `BBIM_Framing.Overrides` (see below). Its own Body. |

`ifcopenshell.util.element.get_pset` merges type and occurrence properties **per
property**, so an occurrence reads `Data` from its type and `Guide` from itself. This is
the same pattern as layered walls (layer set on the type, Body per occurrence).

- Editing the type regenerates every occurrence.
- Assign type, duplicate and copy-class must regenerate instead of mapping the type's
  representation. This is the main Bonsai touch point.
- Untyped elements keep all properties on the occurrence.
- An occurrence-level `Data` replaces the type's whole system: all or nothing, no merge.

## Occurrence overrides (curtain walls need these, railings rarely do)

Rules make the regular grid; real façades break it. Overrides are stored on the
occurrence and keyed by stable grid addresses: `(entry name, segment index, bay index,
row index)`.

- Remove a member instance (for example, drop one mullion to merge two cells).
- Change one cell's infill entry, for example from vision glass to spandrel.
- Replace a cell's infill with a door or window type. This is essential for storefront,
  and requires the aggregate output.

Grid addresses shift when the guide or the spacing changes. Overrides that no longer
resolve should be reported, not silently dropped. Phase 2 or later; the first version
has no overrides.

## IFC output

Decision: `BODY` only, for every host, in phase 1.

Roadmap: a **host-level toggle** between `BODY` (single element) and `PARTS` (composed
of separate elements). Flipping it regenerates the host in the other form, so a façade
can stay light while designing and be exploded into parts when it needs scheduling or
doors. Phase 1 must not rule this out:

- The solver output carries each member's identity: entry name, plus its grid address
  `(segment, bay, row)`. The same solve can then be written either way.
- Overrides are keyed by grid address, never by element GUID, so they survive the
  toggle.
- The toggle is one value on the occurrence (`BBIM_Framing.Output`), not per entry. A
  per-entry mix, for example mullions in the body and panels as parts, is a possible
  later refinement.

| Mode | Result | Status |
|---|---|---|
| `BODY` | Shape items in the host's own Body, grouped by `IfcShapeAspect` named after the constituent | Phase 1, all hosts |
| `PARTS` | Host aggregates generated elements: IfcMember (`MULLION` / `POST` / `BALUSTER` / `STUD`…) and IfcPlate (`CURTAIN_PANEL`), or IfcDoor / IfcWindow in an overridden cell | Deferred |

IFC convention for curtain walls is decomposition into members and plates, so `PARTS`
will matter eventually: it makes glass sizes schedulable and lets a cell hold a door.
The cost is many Blender objects. Ideas to soften it, if it comes back:

- Generated parts are managed by the host: locked, regenerated wholesale, and not
  hand-edited.
- One IfcMemberType / IfcPlateType per entry, with an `IfcMappedItem` wherever lengths
  match, so there are few distinct meshes.
- A host-level "collapse to BODY" switch for large façades during design.

Mixed mode, for example mullions in `BODY` and panels in `PARTS`, is allowed but not a
priority.

## Geometry

Profile convention, for users drawing profiles:
- Vertical members: profile X along the path, profile Y out of the plane (to the path's
  left).
- Horizontal members: profile X out of the plane (to the left), profile Y up.
- `rotation` turns the profile in its own plane, counter-clockwise from X toward Y.
- `offset` moves the member out of the plane, to the left.

- **Horizontals:** one `IfcExtrudedAreaSolid` per straight piece, with local Z along the
  piece, X out of plane and Y up, so the library profile is used directly. Where a member
  continues around a corner:
  - Each piece is lengthened just enough for its whole section to reach the bisector
    plane, then clipped by an `IfcHalfSpaceSolid` on that plane.
  - The clipped piece is wrapped as `IfcCsgSolid(IfcBooleanClippingResult)`, so every
    item is an IfcSolidModel. The representation is `SolidModel` when there are mitres,
    otherwise `SweptSolid`.
  - The mitre plane goes through the corner on the path, so offset rails still meet.
  - A whole-loop member on a closed path is mitred at the start vertex too, with no gap.
- **Why not `IfcFixedReferenceSweptAreaSolid`:** the first design swept along the path
  with FixedReference = +Z. That sweep puts profile X up and profile Y to the path's
  right, so it needs an `IfcDerivedProfileDef` to turn the profile 90°. **The kernel
  applies a derived profile's operator rotation twice**: 45° comes out as 90°, ±90° as
  180°. This happens in plain extrusions too, in both 0.8.5 and 0.9, and is likely in
  `src/ifcgeom/mapping/IfcDerivedProfileDef.cpp` or in the 2D operator's mapping. Reported
  upstream as #10043. Per-piece extrusions avoid it entirely.
  Minimal repro: a point at (1, 0), rotated 45°, lands on (0, 1).

  ```python
  f = ifcopenshell.file(schema="IFC4")
  sq = f.createIfcRectangleProfileDef("AREA", None, f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((1.0, 0.0))), 0.01, 0.01)
  c = 0.5 ** 0.5
  op = f.createIfcCartesianTransformationOperator2D(f.createIfcDirection((c, c)), None, f.createIfcCartesianPoint((0.0, 0.0)), 1.0)
  solid = f.createIfcExtrudedAreaSolid(f.createIfcDerivedProfileDef("AREA", None, sq, op, None), None, f.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
  v = ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), solid))
  print(v.min(0), v.max(0))  # expected about (0.707, 0.707); prints about (0, 1)
  ```
- **Verticals:** `IfcExtrudedAreaSolid` along Z (along `v` in a tilted mapping), with
  the length solved from the bounds. A corner member takes the direction of the segment
  it starts.
- **Infill:** an `IfcExtrudedAreaSolid` of a rectangle in the segment plane, centred on
  the plane plus `offset`. On a raked cell (phase 2) the outline becomes an
  `IfcArbitraryClosedProfileDef` parallelogram. Curved paths are faceted per segment.
- **Phase 1 limits:**
  - Verticals and infill use the segment's plan direction, and `u` is measured along the
    3D path, so sloped guides (stairs) are not right yet.
  - Rails on a sloped segment are extruded along the slope, with the section
    perpendicular to the rail.
- **Pure solver** (no IFC, no Blender) returning dataclasses, shared by the viewport
  preview and the IFC writer. Suggested homes: the solver in
  `ifcopenshell.util.framing`, the IFC writer in
  `ifcopenshell.api.geometry.add_framing_representation` (and a parts generator for
  `PARTS`), and Bonsai in `bim/module/model/framing.py`.

## Materials

- `IfcMaterialConstituentSet` on the type, one constituent per entry (see above).
- `BODY`: shape aspects named after the constituents. Still to check: Bonsai's viewport
  and drawing support for shape aspects. Fallback: per-item `IfcStyledItem` from the
  constituent's style.
- `PARTS`: each generated element gets the constituent's material directly.

## UI

Decision: a **Framing** panel (`BIM_PT_framing`) under `BIM_PT_tab_parametric_geometry`,
like `BIM_PT_railing` and `BIM_PT_stair`. It shows on any IfcRailing / IfcCurtainWall
occurrence or type. Its states follow the railing panel: "Add Framing" when the element
has no `BBIM_Framing`, then an edit / finish / cancel flow for the system and a separate
flow for editing the path. One generator per element: on an element that has
`BBIM_Railing`, "Add Framing" is disabled with a poll message, and the reverse also
applies. When framing a host type, the panel edits the type's system. On an occurrence
it shows the type's system read-only, with a button to go to the type, plus the
occurrence's own height and path.

- A UIList of entries: kind, profile, material and output pickers; add, duplicate,
  reorder.
- A 2D elevation preview of one bay, via a schematic gizmo like `GizmoRailingSchematic`.
- Presets:
  - Railing: pickets, cables, glass with posts, frameless glass.
  - Storefront: 1 and 2 transoms.
  - Curtain wall: stick system.
  - Stud wall.
- Phase 2: click a cell or member in the viewport to override it.

## Phases

1. Solver plus vertical ruled-surface guide; V, H and infill; spacing, `within` and
   `between`, bounds, breaks; library profiles; constituent materials; `BODY` output;
   type-to-occurrence regeneration; IfcRailing and IfcCurtainWall hosts.
2. Occurrence overrides that stay within `BODY` (remove a member, swap a cell's infill),
   stairs and raked bounds, mapped items.
3. Tilted-plane guide (sloped glazing), fixings.
4. Roadmap: the `BODY` / `PARTS` toggle, and door or window types in a cell (needs
   `PARTS`).

## Open questions

- Purge safety for profiles on types with no occurrences (see above).

## Test checklist

- [x] Solver unit tests (pure Python): spacing modes, `within`, bounds, breaks, infill
      splitting, cycle rejection, per-segment versus whole-path.
- [x] Profile resolves by id, falls back to the name (moved files, renames), and returns
      None when neither resolves. The writer raises, listing the unresolved entries.
- [x] Geometry: post, rail and panel placement; rail profile upright; offset and
      rotation; mitred corners meet exactly (checked by tessellating); closed loops
      mitred all round; shape aspects grouped per entry and replaced on regeneration.
      59 tests pass in total.
- [ ] Bonsai writes the resolved profile id and name back to the JSON.
- [ ] Purging unused profiles keeps the profiles of a framing type with no occurrences.
- [ ] The same system on an IfcRailing and an IfcCurtainWall produces the same members.
- [ ] Two occurrences of one type with different guides produce different geometry.
- [ ] Editing the type regenerates all occurrences.
- [ ] Assign, duplicate and copy-class regenerate instead of mapping.
- [ ] Materials survive append-asset and type duplication.
