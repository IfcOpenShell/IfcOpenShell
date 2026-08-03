# Design Spec: Space Regeneration with Sloped Roofs, Walls, and Slabs

## Goal

Extend `bonsai.core.spatial.generate_space` so it produces correct `IfcSpace`
geometry for non-rectilinear envelopes:

- sloped roofs,
- sloped slabs,
- sloped walls,
- curved walls.

The existing footprint-based `IfcExtrudedAreaSolid` path is preserved for
ordinary vertical extrusions. A new hybrid path keeps the representation
parametric when possible and falls back to an `IfcFacetedBrep` only when the
boundary cannot be expressed as a clipped extrusion.

## Architecture

```
┌─────────────────────────────────────────┐
│ Existing footprint generation            │
│ (get_space_polygon_from_*_objects)     │
└──────────────┬────────────────────────────┘
               v
┌─────────────────────────────────────────┐
│ Detect extrudability and bounding planes │
│ (pure-Python util, Blender-independent)  │
└──────────────┬────────────────────────────┘
               v
        ┌──────┴──────┐
        v             v
┌───────────────────┐ ┌───────────────────┐
│ Extrusion + clips │ │ B-rep fallback     │
│ IfcExtrudedAreaSolid│ │ IfcFacetedBrep    │
│ + IfcBooleanClippingResult│ │ (or IfcPolygonalFaceSet) │
└───────────────────┘ └───────────────────┘
```

## Detection criteria

Use the parametric `IfcExtrudedAreaSolid` + `IfcBooleanClippingResult` path
when **all** are true:

1. Side walls are vertical extrusions (face normal is horizontal).
   Curved-in-plan walls are allowed; their footprint is polygonized or
   reconstructed as a curved profile.
2. The roof/top boundary is piecewise-planar.
3. The bottom slab/floor boundary is piecewise-planar.
4. The footprint is a single closed outer region, possibly with inner closed
   regions for holes.
5. The resulting half-space intersection is non-empty and produces a single
   solid.

Otherwise use the B-rep fallback.

## Parametric extrusion + clipping algorithm

1. **Build the profile**
   - Outer ring from the footprint polygon → `IfcArbitraryClosedProfileDef`.
   - Inner rings (holes, e.g., around columns) →
     `IfcArbitraryProfileDefWithVoids`.
2. **Extrude**
   - Create `IfcExtrudedAreaSolid` along local +Z, with a height large enough
     to cover all bounding planes.
3. **Find top planes**
   - Cast vertical rays upward from the footprint centroid and sample points
     using `ifcopenshell.geom.tree.select_ray`.
   - Check each hit face for planarity with
     `ifcopenshell.util.shape.dissolve_faces(..., merge_coplanar=True)`.
   - Group coplanar hits into distinct planes.
4. **Find bottom planes**
   - Same as top, but downward.
5. **Clip**
   - For each top plane: create `IfcHalfSpaceSolid` with normal pointing
     upward (removed side), apply via `ifcopenshell.api.geometry.clip_solid`.
   - For each bottom plane: create `IfcHalfSpaceSolid` with normal pointing
     downward, apply via `clip_solid`.
6. **Output**
   - `IfcExtrudedAreaSolid` wrapped in a chain of `IfcBooleanClippingResult`.

## B-rep fallback algorithm

For non-extrudable cases (sloped walls, curved roofs, etc.):

1. **Seed space**
   - Create a temporary rough mesh (e.g., extruded footprint bounding box) as
     a placeholder.
2. **Extract boundary faces**
   - Run `ifcopenshell.util.boundary.auto_generate_boundaries` against the
     seed to identify the faces of bounding elements that touch the space.
   - Convert each boundary polygon from face-local back to 3D world
     coordinates.
3. **Build closed shell**
   - Collect the 3D boundary faces.
   - Add narrow gap-closing faces if `auto_generate_boundaries` leaves
     unmatched edges.
   - Triangulate and produce `IfcClosedShell` → `IfcFacetedBrep` (or
     `IfcPolygonalFaceSet` for IFC4+).
4. **Clean up**
   - Assign the B-rep to the `IfcSpace` and remove the temporary seed
     geometry.

## Files to touch

- `src/ifcopenshell-python/ifcopenshell/util/space.py`
  - New: `detect_space_volume_strategy`
  - New: `build_extruded_clipped_space`
  - New: `build_brep_space`
  - New helpers for ray-cast plane detection and face planarity checks.
- `src/bonsai/bonsai/tool/spatial.py`
  - Extend `set_space_representation_from_polygon` to dispatch to the new
    strategy.
  - Extend footprint/profile creation to support inner rings for holes.
- `src/bonsai/bonsai/core/spatial.py`
  - `generate_space` calls the dispatcher.

## Testing

- Add unit tests in `src/ifcopenshell-python/test/util/test_space.py` for pure
  geometry helpers:
  - simple shed roof,
  - gable roof,
  - sloped slab,
  - L-shaped footprint with sloped roof,
  - curved wall.
- Add Bonsai tests in `src/bonsai/test/tool/test_spatial.py` for end-to-end
  `generate_space` with non-rectilinear geometry.

## Error handling

- If detection fails or half-space clipping produces an invalid result, fall
  back to the B-rep path.
- If the B-rep path also fails, return an error string and leave the existing
  space representation unchanged.
