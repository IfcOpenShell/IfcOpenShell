<!-- This file was generated with the assistance of an AI coding tool. -->

# Framing system (branch `framing-system`)

Tracking issue: #10044, with the roadmap.

Status: written, with tests:
- the layout solver `ifcopenshell.util.framing` (`test/util/test_framing.py`);
- the 3D geometry and IFC writer
  `ifcopenshell.api.geometry.add_framing_representation`
  (`test/api/geometry/test_add_framing_representation.py`).

- Bonsai: `bim/module/model/framing.py`, the Framing panel, type-to-occurrence
  regeneration, constituent sync, and profile write-back. Being tested in Blender 5.1.

Base: `v0.9.0`.

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

- **Framing is open to any element class** (decided 2026-10-23), not a list of hosts.
  Any IfcElement or IfcElementType can be framed. Feature and virtual elements are
  excluded by class. `framing_refusal()` refuses, with a reason shown in the panel, where
  something else already owns the body:
  - another parametric tool (door, window, stair, old railing, roof, array, or array
    copies);
  - a layered or profiled material usage, on the element or its type;
  - a type with representation maps;
  - distribution ports;
  - an assembly that already has parts.

  The Type Manager offers the Framing (Railing) and Framing (Storefront) templates for
  every framing class, after the class's own templates.
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
  - `FIXED`: exact spacing. `align` sets where it is measured from in each range:
    `START`, `CENTER` (the default: the remainder is split between both ends) or `END`.
    For a repeating horizontal, start is the bottom and end the top.
  - `MAX`: equal bays, no wider than the value.
  - `COUNT`: a fixed number per segment.
- `at_ends` / `at_corners`.
- `within`: spaces this array inside the bays of another vertical array. Examples are
  balusters between posts, and intermediate mullions between primary ones.
- `bottom` / `top` bound: `BASE` (v = 0), `TOP` (occurrence height), an absolute `v`, or
  `{"member": name}`.
- Square or raked cut at sloped bounds.
- `breaks_at: [horizontal names]` cuts the member into pieces at the faces of those
  rows that cross it: every row of a repeating horizontal, and only where the row runs
  at that u. Pieces are `VerticalMember.piece` 0, 1, … upward. Two entries cannot break
  at each other: each would cut the other and leave a hole, so it is an error that asks
  which one is continuous.

### Horizontal member (rails, cables, transoms, plates)

- At `v`, or repeating upward between two bounds (`COUNT` / `FIXED`).
- `continuous`, or `breaks_at: [vertical names]`. Each end of a broken member is
  shortened by half the depth of the profile it stops at.
- `extend_start` / `extend_end`: how far each run carries on past its start and end, in
  plan along the path, added after the outer-face overhang. Negative pulls it back.
  Breaks within a run are not affected, so a rail broken at posts and extended past
  the end posts gets stubs beyond them. Past the path's ends it follows the end
  segment's direction and slope.
- **Run ends reach outer faces:** where a run ends at a vertical that meets the member
  (passing through it, or stopping just under or over it), the run carries on to that
  vertical's outer face. So a top rail covers its end posts, and a rail limited to some
  bays covers the posts at its bay ends. With `breaks_at` set, the cut still trims it to
  the inner faces. A rail all the way round a closed path has no ends. On an open path
  the first and last segments carry on past the path's ends for this.

### Infill (glass, spandrel, plate, mesh)

- A cell between left and right bounds (the bays of a vertical array, or the path ends)
  and bottom and top bounds (a member, `BASE`, `TOP` or `v`).
- `thickness`, an `offset` out of the guide plane, and a `gap` to each bound (one value,
  or one per side).
- `max_width` with `joint`: splits a wide bay into equal panels. With no posts, this is
  today's `FRAMELESS_PANEL`.
- Glass, mesh and plate differ only by material; the geometry is one thin solid per
  panel.

### Picking bays and rows (added after first testing)

- **Bays** always count along the path and **Rows** always count upward. Both are 1-based
  lists, with negatives counting from the end (`[1, -1]` is first and last). Empty means
  all. In the UI they are text fields such as `2, 4`.
- **Verticals:** `bays` picks which ranges spacing fills: the bays of `within`, or the
  path segments.
- **Horizontals:**
  - `within` on a repeating horizontal fills each gap between the rows of another
    horizontal, which may itself repeat. The gaps lie within the horizontal's own
    bottom and top bounds.
  - `rows` picks those gaps.
  - `between` + `bays` makes a rail run only in some bays along the path, centre to
    centre between the members of `between`. `breaks_at` still trims to faces.
    Adjacent picked bays merge into one piece.
- **Infill:**
  - `within` stacks panels between the rows of a horizontal; `between` + `within` makes
    a grid.
  - `bays` picks columns and `rows` picks rows. Addresses are now
    `(segment, bay, row, panel)`.
  - `breaks_at` cuts panels at the faces of other verticals, as for rails, but only
    where those members pass through the panel's height. It is needed when the panels
    are `between` members that skip some verticals, e.g. pickets placed `within` posts.
- **Following members:**
  - A panel appears only where each horizontal it is bounded by runs along at least half
    the bay. The same goes for the rows it stacks between.
  - A vertical bounded by a member stands only where that member runs. This is checked
    against the member's runs before breaks, so balusters on a rail limited to bay 2 are
    only in bay 2.

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
- **Bounds may reference a repeating horizontal**, resolved to the nearest row:
  - a repeating top bound is its lowest row above the bottom;
  - a repeating bottom bound is its highest row below the top;
  - with both repeating, the bottom is the first row and the top the next one up.

  So a storefront with repeating transoms keeps Vision (Sill → Transom) and Clerestory
  (Transom → Head), and the gaps in between are filled with `within`. A repeating
  member is still rejected as a horizontal's own level `v`.
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
- **Sloped guides** (stairs, ramps), added after testing on an L path with a 29° leg:
  - **u is measured in plan.** Spacing, bay widths and member extents are horizontal,
    as baluster spacing rules are. Members stay plumb, and v is plumb above the path.
  - **Rails are oblique extrusions with a plumb section.** The profile sits in a plumb
    plane facing along the path in plan, and the extrusion direction follows the slope.
    So the rail keeps its vertical height and thickness, its ends are plumb (flush with
    post faces), and a change of slope joins with no clip. Plan corners still get a plumb
    bisector mitre.
  - **Verticals are raked by default:** both ends are clipped to planes that follow the
    path's slope at that point. A member standing on a change of slope is clipped under
    both slopes, which never penetrates and leaves at most a small gap. `square_cut`
    (the Square Cut toggle) opts out.
  - **Panels on a slope are parallelograms** (`IfcArbitraryClosedProfileDef`): plumb
    sides, with the bottom and top following the slope.
  - **ShapeBuilder.plane degenerates for a downward normal**, so `_clip` builds its own
    plane placements.
  - **Offset rails ease round climbing corners** (`_ease_corners`). Offset to one side,
    the two legs reach the rail's own corner at different heights. So one leg's slope
    carries on around the corner until the other leg's line meets it:
    - On the outside of a rising turn, a short level return along the outgoing leg.
    - On the inside, the climb starts a little before the corner, on the incoming leg.

    The plan corner is then a mitre between pieces of the same slope, and the slope
    change is a plumb joint. This only applies at plan corners where the slope changes;
    centred rails are unchanged.
  - **Run ends only reach over verticals the rail overlaps out of plane.** `solve()`
    takes `lateral` (profile plus offset across the guide plane), so an offset handrail
    is not stretched over end posts it misses.
  - **Clipped pieces need a kernel with booleans.** Mitred rails and raked verticals are
    `IfcCsgSolid(IfcBooleanClippingResult)`. Bonsai's "CGAL Simple" geometry library
    ("CGAL without booleans") drops them, while OpenCASCADE, CGAL and the default Hybrid
    build them. Decision (Ryan, 2026-10-23): keep clipping, the standard IFC pattern, as
    for walls clipped under roofs. An option to write those pieces as exact faceted
    solids instead was considered and parked.

- **Pure solver** (no IFC, no Blender) returning dataclasses, shared by the viewport
  preview and the IFC writer. Suggested homes: the solver in
  `ifcopenshell.util.framing`, the IFC writer in
  `ifcopenshell.api.geometry.add_framing_representation` (and a parts generator for
  `PARTS`), and Bonsai in `bim/module/model/framing.py`.

## Materials

- `IfcMaterialConstituentSet` on the type, one constituent per entry (see above).
- `BODY`: shape aspects named after the constituents. **The geometry kernel does not
  resolve constituents through shape aspects.** `mapping.cpp` uses a constituent set's
  material only when it has exactly one constituent, so every entry rendered in one
  colour. So `add_framing_representation(constituent_set=...)` also gives each item an
  `IfcStyledItem` with its constituent material's surface style (Body context, or its
  parent). Verified on the 0.9 kernel: per-entry materials come out.
- Only entries with a material get a constituent. Removing an entry or clearing its
  material removes its constituent.
- `PARTS`: each generated element gets the constituent's material directly.

## UI

Decision: a **Framing** panel (`BIM_PT_framing`) under `BIM_PT_tab_parametric_geometry`,
like `BIM_PT_railing` and `BIM_PT_stair`. It shows on any IfcRailing / IfcCurtainWall
occurrence or type. Its states follow the railing panel: "Add Framing" when the element
has no `BBIM_Framing`, then an edit / finish / cancel flow for the system and a separate
flow for editing the path. One generator per element: on an element that has
`BBIM_Railing`, "Add Framing" is disabled with a poll message, and the reverse also
applies.

As built (phase 1):
- **Editing from an occurrence edits the system where it lives.** If the system comes
  from the type, the panel says so ("System from type: X (N occurrences)"), and Finish
  rebuilds every occurrence that has its own path. Height and path are always the
  occurrence's own. This replaces the earlier "read-only on occurrences" idea: Bonsai type
  objects are awkward to select, so editing in place is more practical.
- **On a type, the height field sets `default_height`**, which new occurrences start
  with.
- **Add Framing:**
  - On an untyped element or a type: applies a preset (Railing or Storefront), which
    creates its profiles and materials by name if missing.
  - On an occurrence whose type already has a system: only adds a default path.
  - Refused when the type has representation maps, because rebuilding a mapped Body
    would rewrite the type's shared geometry through `replace_object_ifc_representation`.
- **Create Framing Type** moves an untyped element's system and constituent set onto a
  new `<Class>Type` with no representation (an empty object, like the EMPTY template),
  then assigns it.
- **When a type's system is first added or edited**, occurrences with no path of their
  own are left alone, so their existing geometry is not replaced.
- **Assign type** (`core.type.assign_type`, new `model.is_framing` branch) and **Add
  Occurrence** (a new branch that skips the representation-template dialog) build the
  occurrence's body, along a default 3 m path if it has none.
- **Framing is registered in `tool.Parametric.EDIT_TYPES`** (`is_framing`,
  `BIMFramingProperties`, `bim.{enable,finish,cancel}_editing_framing`), so a pending edit
  is committed on save like the other parametric types.
- **Entry references** (`within`, bounds, `between`) are strings picked with
  `prop_search` over the entry list. Blender stores dynamic enums by index, so they would
  break on reorder. Profile and material pickers are dynamic enums keyed by step id.

- A UIList of entries: kind, profile, material and output pickers; add, duplicate,
  reorder.
- A 2D elevation preview of one bay, via a schematic gizmo like `GizmoRailingSchematic`.
- **Space** (`bim.direct_profile_edit`) enters and leaves path editing on a framed
  occurrence, as it does for roof footprints: entering calls
  `bim.enable_editing_framing_path`, which commits a pending system edit first, and leaving
  calls `bim.finish_editing_framing_path`. Types have no path, so Space does nothing
  special on them.
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
