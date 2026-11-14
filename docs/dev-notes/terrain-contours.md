<!-- This file was generated with the assistance of an AI coding tool. -->

# Terrain contours — dev note

> Living design note for the `terrain-contours` branch, checked out in `C:\IfcOpenShell`
> (Blender 5.1's linked tree), based on `v0.9.0`.
> Status: **v1 tested in Blender 5.1; PR open against `v0.9.0`.**

## Implementation status (v1)

| Piece | Where | Verified |
|---|---|---|
| Slice + chain (numpy, pure) | `tool/terrain.py` `slice_triangles`, `chain_segments` | Standalone script: cone → one closed loop at the right radius; slope → one ordered open line; level exactly on vertices → no zero-length steps; two hills → two loops; 80k tris × 48 levels ≈ 1.3 s |
| Top-surface filter (BVH ray up) | `tool/terrain.py` `get_top_surface_triangles` | Blender 5.1, sculpted test terrain (see fix below) |
| Core flow | `core/terrain.py` | `test/core/test_terrain.py`, 5 pass under plain pytest |
| IFC writing (annotation, placement, polylines, psets, assign_product, container) | `tool/terrain.py` `create_contour` | Blender 5.1, IFC4 / feet test project |
| Panel + 3 operators | `bim/module/terrain/` — Object properties → Parametric Geometry → Contours | not yet |
| Drawings include contours | `tool/drawing.py` `get_drawing_elements` (2-line change) | Blender 5.1 plan drawing: each contour drawn once, `IndexContour` styled |
| Geographic Element Tool header button | — | deferred — convenience only, add if the panel proves too far away |

Decisions made while coding:

- Terrain = active mesh object whose element is an `IfcGeographicElement` with predefined
  type **TERRAIN**, **or an `IfcSite`** (many real files keep the terrain as the site's Body).
  Other geographic elements (e.g. VEGETATION trees) are not terrain.
- `root.create_entity(predefined_type="CONTOURLINE")` already does the schema switch:
  IFC4X3 → `PredefinedType`, IFC4 → `ObjectType = "CONTOURLINE"`. Kept upper-case in IFC4
  (Bonsai convention; `get_predefined_type` reads both). `Pset_AnnotationContourLine` is
  attached in both schemas.
- One annotation per elevation, `Model/Annotation/MODEL_VIEW` context (created if
  missing), placement at (terrain x, terrain y, contour z), polylines are
  `IfcIndexedPolyCurve`s from `ShapeBuilder.polyline`.
- Index contours get `EPset_Annotation.Classes = "IndexContour"` → SVG class.
- Levels are multiples of the interval in **datum height** (see "Elevation datum" below),
  so 2 ft contours land on true 2 ft survey heights, under a false origin too.
- Slicing runs before anything is deleted, so a too-small interval (> 2000 levels)
  errors without touching existing contours.
- Contours are contained in the terrain's container (or the site itself) explicitly,
  because `assign_class` skips containment for any annotation while a drawing camera
  is active.

### Fixed: broken / intermittent contours on sculpted terrain (2026-10-07)

Test file: `D:\Dropbox\Gitea_OD\Community_Troubleshooting\Terrain-Contours` (box with a
sculpted top, 1,090 quads). The first version ran the "visible from above" ray test per
**polygon**, from the average of its vertices. On a warped quad that point can sit below the
quad's own surface, so the ray hit the quad itself: 370 of 371 rejected faces were
self-hits, which left holes and split each level into 4–21 fragments. Now the test runs per
**loop triangle** (a triangle's centroid lies on it) and steps past hits on the triangle's
own polygon. Result on the test file: 1–2 polylines per level; the only excluded triangles
are the 4 side faces and the bottom; every open end lies on the terrain boundary.

### Drawing path — checked

`get_drawing_elements` dropped every annotation not in the drawing's group; contours are
now let through. They may then be drawn **twice**: by the C++ SVG serializer (linework,
annotation contexts — but it only emits annotations within the storey Z range in floor
plans) and by `svgwriter.draw_misc_annotation` (annotation layer, which carries the
`IndexContour` class). Checked in a real plan drawing: each contour appears once and
`.PredefinedType-CONTOURLINE.IndexContour` styles the index lines.

## Problem

Drafting a site survey in Bonsai needs topographic contour lines generated from a terrain
mesh: every *N* units (2 ft, 5 ft, 1 m …), with a heavier **index contour** every *k*th
line, regenerated when the terrain changes, and appearing in plan drawings and sheets.

There is nothing in Bonsai today that does this. Third-party Blender options exist
(Parametric Shapes' *Contour Generator*, a Gumroad geometry-nodes tree) but they produce
plain Blender geometry, which Bonsai drawings do not render — drawings only see IFC
elements.

## IFC representation

IFC 4.3 has a dedicated class for this:

- **`IfcAnnotation`, `PredefinedType = CONTOURLINE`** — "annotation used to illustrate
  lines connecting points of equal elevation". IFC4 has no predefined type on
  `IfcAnnotation`; there the type goes in `ObjectType` (see the schema table below).
- **`Pset_AnnotationContourLine.ContourValue`** (`IfcLengthMeasure`) — the elevation of
  the line.

### IFC4 vs IFC4X3 differences (checked against `IFC4.exp` and the repo's pset templates)

| Concept | IFC4 ADD2 TC1 | IFC4X3 |
|---|---|---|
| `IfcAnnotation.PredefinedType` | **does not exist** (entity has no attributes beyond `IfcProduct`) | `CONTOURLINE` |
| `Pset_AnnotationContourLine` | exists, applicable to `IfcAnnotation/ContourLine` (matched on `ObjectType`) | exists, applicable to `IfcAnnotation/CONTOURLINE` |
| `IfcGeographicElementTypeEnum.TERRAIN` | exists | exists |
| `IfcEarthworksCut` / `IfcEarthworksFill` | **do not exist** | exist |

Consequences: in IFC4 set `ObjectType = "ContourLine"` (the spelling the IFC4 pset
applicability uses — Bonsai's own annotation ObjectTypes are upper-case, so check
whether pset-template filtering is case-sensitive before choosing); in IFC4X3 set
`PredefinedType = CONTOURLINE`. Write a small schema switch, as
`bim/module/model/product.py` already does for vegetation (IFC4 `USERDEFINED`/
`VEGETATION` vs IFC4X3 `VEGETATION`).

Decision: each contour elevation is one **model-space** `IfcAnnotation.CONTOURLINE`
(not assigned to a drawing group) whose body is 3D polylines at the true elevation. This
means:

- other IFC tools see real contour objects, not just a Bonsai drawing artefact;
- they read correctly in 3D and in plan;
- index vs. intermediate contours can be styled independently in drawing CSS (class or
  ObjectType distinction — to settle during implementation).

Generation parameters live on the **terrain element** (`IfcGeographicElement`, TERRAIN)
in a `BBIM_Contours` pset, following the `BBIM_Roof` / `BBIM_Stair` parametric pattern:

| Property | Meaning |
|---|---|
| `Interval` | contour spacing, project length units |
| `IndexInterval` | every *k*th contour is an index contour (default 5) |
| `MinElevation` / `MaxElevation` | optional clamp; default = terrain Z range |

The generated annotations need a link back to their terrain so Update can find and
replace them. Candidate: `IfcRelAssignsToProduct` (annotation assigned to the terrain).
To verify against how Bonsai already relates generated annotations before choosing.

Ruled out: adding the contours as a second Plan/Annotation representation on the terrain
itself. Simpler, but invisible to other tools as objects and awkward to style index
contours differently.

## UI placement

1. **Object Properties → "Contours" panel**, polled on a selected terrain element: shows
   the `BBIM_Contours` values, **Generate / Update** and **Remove**. This is where the
   interval is changed later.
2. **Geographic Element Tool header** (`bim.geographic_element_tool`,
   `bim/module/model/workspace.py`) — when a terrain is selected, show the same
   Update button, mirroring how the tool shows wall-specific actions when a wall is
   selected.
3. **Drawings: no new machinery** if contours are annotations — plan drawings include
   them, CSS styles them. Elevation labels on index contours are phase 2 (decorator or
   generated TEXT annotations; label placement/collision is the hard part).

Logic goes in `core/` + `tool/` (Bonsai's usual split) so it does not depend on which
panel calls it.

### Relation to PR #9304 (Saikei Civil CIVIL tab)

PR #9304 adds a **CIVIL** Properties tab for alignment authoring. That tab would be the
natural long-term home for site/terrain tools. Decision: **do not stack on it** — no code
is shared (alignment curve math is unrelated to mesh slicing), its merge path is
uncertain (reviewer is building an alternative alignment UI), and stacking would block a
small PR on a large one. If the CIVIL tab lands, moving the Contours panel there is a
`bl_context` / `bl_parent_id` change.

## Updating

- **Update Contours** re-slices from the current mesh and pset, **reusing the annotation
  already at each elevation** (matched by `ContourValue`, rounded to 1e-6 m): its placement,
  representation (`tool.Model.replace_object_ifc_representation`), ContourValue and the
  `IndexContour` token are updated in place, so its GlobalId — and anything pointing at it,
  e.g. a label — survives. New elevations get new annotations; elevations no longer present
  are removed. Only the `IndexContour` class token is added/removed, so user classes in
  `EPset_Annotation` are kept.
- **Later, opt-in:** regenerate when the terrain representation is saved on leaving Edit
  Mode. Opt-in because terrain meshes are heavy.

## Algorithm sketch

For each elevation `z` in `ceil(zmin/I)*I … zmax` step `I`:

1. `bmesh.ops.bisect_plane` on a **copy** of the terrain mesh with a horizontal plane at
   `z` (transformed into the object's local space — see below), keeping only the cut
   edges (`geom_cut`).
2. Restrict to edges on the **top surface** (see "volume terrain" below).
3. Chain the cut edges into polylines (open where they hit the mesh border, closed
   loops otherwise) and write them as `IfcIndexedPolyCurve` / polyline items.

Alternative to evaluate: Geometry Nodes Mesh Boolean "Intersecting Edges" against a
stack of planes. Rejected for v1 — harder to drive from an IFC operator and to chain into
ordered polylines.

## Related local add-ons (same "site tools" family)

Ryan has two standalone add-ons that may enter the ecosystem later. Both work on terrain
and share hard-won facts this feature needs:

**Mesh Outline Projector**
(`D:\Dropbox\Gitea_OD\Utility_Apps\Blender\addons\Mesh Outline Projector`) — projects
the top-down outline of objects (e.g. building footprints) onto a terrain's top surface,
cuts it with vertical bisect planes and paints the covered faces with the source
material. Directly reusable lessons:

- **`bmesh` / `BVHTree` work in local space**; world-space planes must be transformed by
  `matrix_world.inverted()` (plane from three transformed points, not a transformed
  normal).
- **`bisect_plane` leaves no face straddling the cut** — the same guarantee makes
  contour edges clean.
- **"Top surface" cannot be found from normals** — IFC/imported meshes often have flipped
  winding. Its `make_top_face_predicate` (roughly-horizontal `|n.z|` **and** an upward
  ray-cast against a BVH snapshot hits nothing) is exactly what contours need for
  **volume terrain**: slicing a solid terrain horizontally otherwise also yields loops
  around the sides and bottom. Candidate to promote into a shared `tool.Terrain` helper.

**Excavate** (`D:\Dropbox\Gitea_OD\Utility_Apps\Blender\addons\Excavate`) — turns
selected terrain faces into a flat-bottomed pit (vertical walls, flat floor). In IFC
terms this maps naturally to **`IfcEarthworksCut`** (IFC 4.3 feature subtraction;
`IfcEarthworksFill` is its counterpart), which would keep the terrain unmodified and the
cut as a separate, quantifiable element. **Both are IFC4X3-only**; an IFC4 equivalent
would need an `IfcOpeningElement` (or a direct mesh edit), so this one is schema-gated.

Possible shape of a future Bonsai "Terrain" module: contours, outline projection
(footprints / paving zones onto terrain), earthworks cut/fill. Contours come first
because they are the smallest and need no change to the terrain geometry itself.
Note: projected *materials* in Bonsai would be per-face IFC styles, a harder problem —
out of scope here.

## Elevation datum (2026-10-09)

Contours are cut and labelled in **height above the vertical datum** (e.g. sea level), not
model Z: a contour 1 ft above the project origin on a site whose origin is 435 ft above sea
level is "Contour 436", `ContourValue = 436`. Source, in priority order:

1. `IfcMapConversion.OrthogonalHeight` (IFC2X3: `ePSet_MapConversion`), via
   `ifcopenshell.util.geolocation.auto_z2e`, which also applies the conversion's `Scale` and
   `FactorZ`. Note: in IFC4, `Scale` must be set when map units differ from project units
   (e.g. 0.3048 for a feet project on a metre CRS) — checked: OrthogonalHeight 132.588 m,
   Scale 0.3048 → z = 1 ft gives 436 ft.
2. Otherwise `IfcSite.RefElevation` ("datum elevation relative to sea level") of the
   terrain's site (walk up container/aggregate; fall back to the only site). Not added on top
   of a map conversion — both usually describe the same datum.
3. Otherwise none: model elevation.

`ElevationDatum` (tool/terrain.py) maps Blender Z → height:
`origin_height + slope × (z + blender_offset)`. The Contours panel shows the datum and its
source. Precedent: drawing data's `elevation` key is placement Z + `OrthogonalHeight`.
Changing the datum then pressing Update re-cuts everything (new elevations → new annotations).

## Contour labels (2026-10-09, built; not yet checked in Blender)

**Where:** Annotation Tool (`bim.annotation_tool`) Active Tool panel, in the TEXT block, shown
only when the active object is a terrain or site: **Spacing** + **Label Contours**
(`bim.label_contours`, `core.label_contours`). Greyed out with "Generate contours first" until
the terrain has contours. Needs an active **plan** drawing. The Contours properties panel only
points to it.

**What it makes:** one TEXT `IfcAnnotation` per label in the drawing's group, assigned to its
contour (`drawing.assign_product`), text `` ``round({{Pset_AnnotationContourLine.ContourValue}},
N)`` `` with N from the interval's decimals (checked: 436.0000000247 → "436", 436.5 → "436.5"),
literal `BoxAlignment = center`, Plan/Annotation context. `BBIM_ContourLabel.Placement` stores
the generated world x, y, angle; a label whose placement no longer matches was moved by the user
and is kept on re-label (and new labels avoid it). Removing a contour (incl. via Update)
removes its labels.

**Type:** the Annotation Tool's own type picker (`relating_type_id`, "0" = Untyped). Untyped →
`EPset_Annotation.Classes = "fill-bg ContourLabel"` on each label. Typed → `type.assign_type`;
if the type has a representation it is mapped, so its text is the template for every label;
styling and font size come from the type's classes.

**Spacing:** a model distance along each contour (scene units, `subtype=DISTANCE`, default
15 m) — Ryan's choice over paper distance. Label *size* still follows the drawing scale (font
height from the type's `FONT_SIZES` class, default regular 2.5 mm; width ≈ 0.6 × height per
character + 2 mm).

**Placement** (`tool.Terrain.place_labels`, pure, shapely): contours chained from the contour
objects' mesh edges and projected into camera-local XY; labels spread evenly per polyline; each
slides within ±¼ spacing to the straightest stretch (max deviation from the chord), must lie
fully in the camera frame, not overlap placed labels or kept ones; angle normalised to
(-90°, 90°]. 11 checks outside Blender (straight, reversed, diagonal, vertical, short, frame
edge, kink, close parallels, obstacle, circle).

**Still to verify in Blender:** text direction sign vs. Bonsai's `get_empty_object_angle`;
the `fill-bg` box rotating with the text; moved-label detection; sheet output.

### Decisions behind it

- **Real TEXT annotations in a specific drawing** ("Label Contours in Active Drawing"), not
  computed at drawing time — so they're sized for that drawing's scale, cropped to it, and
  individually movable. Re-labelling leaves hand-moved labels alone.
- **Label text reads `ContourValue`** of the contour it's assigned to (text-literal variable),
  not the line's Z: Blender Z is shifted by a false origin and project Z isn't the survey
  datum. Requires Update to keep contour identity (done, see "Updating").
- **Text type:** the operator takes a TEXT annotation type (`ApplicableOccurrence =
  IfcAnnotation/TEXT`); labels are assigned to it, and styling lives on the type's
  `EPset_Annotation.Classes` (occurrences inherit type psets). Offer a default "Contour
  Label" type with `fill-bg ContourLabel`. Still to check: whether a type's text literal can
  act as the template (e.g. a `'` suffix).
- **Gap under the label: `fill-bg`** — existing class; svgwriter draws a copy of the text
  with the `#fill-background` filter (white flood, `markers.svg`) behind it. Verify the box
  rotates with rotated text.
- **Orientation: readable** — never upside down (not the "uphill" convention).
- **Which contours: every contour** by default; maybe configurable later (index only).
- Placement: every X mm of paper along each line (clipped to the drawing crop), slid to the
  straightest stretch over the label's width, rejecting overlaps with labels already placed
  and spots too near the terrain edge. Pure function, tested outside Blender.

## Open questions

- Existing vs. proposed grade: two terrains with status EXISTING / NEW → dashed vs. solid
  contours. Inherit status onto the generated annotations?
- Clip contours to the site boundary, or the full terrain extent?
- IFC2X3 support — probably not; contours are an IFC4+ feature.

## To test (once implemented)

- [ ] Heightfield terrain, imperial (2 ft / index 10 ft) and metric (1 m / index 5 m).
- [ ] Volume (solid) terrain with flipped normals — only top-surface contours.
- [ ] Rotated / translated terrain object — elevations are world Z.
- [ ] Update after editing the terrain — same GlobalIds kept per elevation, stale ones
  removed, none orphaned.
- [ ] Georeferenced project (map conversion OrthogonalHeight, feet and metre CRS) — panel
  shows the datum, contour names/ContourValue are survey heights on interval multiples.
- [ ] Site RefElevation only — same, source "Site RefElevation".
- [ ] Contours appear in a plan drawing with index/intermediate styling.
- [ ] Interval change 2 ft → 5 ft regenerates correctly.
- [ ] Labels: direction follows the lines, `fill-bg` box rotates with the text, moved labels
  survive re-labelling, Untyped and typed labels render on the sheet.
