# Alignment Authoring — Requirements

Working requirements doc for the Bonsai alignment authoring UI (Civil Infrastructure tab and the
Alignment BIM tab). Captures planned work, not yet implemented unless noted. Update in place as
scope is refined or decisions are made; keep open questions marked as such rather than silently
resolving them.

## 1. Table-based editing

The Alignment tab's UI lists the horizontal, vertical, and cant layouts. These listings need to
become editable:

- Edit existing segments
- Add new segments
- Delete segments

When editing finishes, the `IfcAlignment` model and its representations must be updated, and the
updated representations must automatically refresh in:

- the 3D viewport
- the vertical/cant profile view

## 2. Interactive creation of a horizontal alignment

Mimic the existing draw/edit tangent-line workflow from the Civil Infrastructure tab, with these
improvements:

1. Alongside Angle, also show the line's **Bearing** (e.g. `N 30 15 24 E`) — how civil engineers
   think about direction.
2. Allow manual input of Distance and one of Bearing, Angle, or Deflection Angle — likely via a
   pop-up input box.
3. Interactively define the smoothing curves *before* the command ends, rather than as a separate
   pass afterward.

### Proposed interaction sequence

1. Press the eyedropper (or similar) to begin the command.
2. Automatically rotate the 3D viewport to the XY plane (Z-up).
3. Draw tangent lines with the mouse, or use the manual text input from item 2 above.
4. Repeat step 3 until all tangents are drawn.
5. Right-click (or whatever is the standard convention) to move on to the second phase of the
   command.
6. Click each PI (or only the PIs of interest) and input the smoothing type and its parameters.
   Smoothing types include: Circular, Spiral-Circular, Circular-Spiral, Spiral-Circular-Spiral.
   **Implemented** (`ALIGN_OT_apply_pi_curve`, `PICurveMarkerProperties.curve_type` in the
   Alignments tab panel) for the clothoid spiral family, via the PI method: each PI marker still
   stands for one combined "curve" in the UI, but resolves to a run of independent
   `IfcAlignmentSegment`s underneath (tangent run / entry spiral / arc / exit spiral / tangent
   run), placed by `ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method` and
   written via `layout_horizontal_alignment_by_pi_method`.
7. In a pop-up (or other appropriate UI element), input the parameters:
   - **Circular curve**: radius only.
   - **Spiral curve**: spiral length(s) (entry, exit, or both). **Implemented for the clothoid
     family only** — this assumes all spirals have infinite start/end radius and share the
     circular arc's radius. Other spiral families (Bloss, Cosine, Sine, Cubic, Helmert) are not
     yet supported by the PI-method solver; each would need its own curvature-vs-length
     integrand substituted into `solve_horizontal_alignment_by_pi_method`'s displacement
     composition (the tangent-distance projection itself is spiral-family agnostic).

   **Confirmed future requirement**: compound curves (PCC, point of compound curvature — two
   arcs curving the same direction) and reverse curves (PRC, point of reverse curvature — two
   arcs curving opposite directions), joined directly with no tangent run between them, optionally
   with a spiral on the outer/non-joined side of either curve (e.g.
   Spiral-Circular-Spiral-Circular-Spiral). A PCC/PRC-capable solver variant (`join_next` on a PI's
   radii entry, closure-validated so the two curves' tangent lengths exactly span the PI-to-PI
   distance) exists as prior art on another branch, ported from upstream PR #8833, but was not
   brought in with the clothoid spiral-circular-spiral pass.

   **Open question**: the UI for this — since a compound/reverse curve junction spans two PIs, it
   may need selecting 2 PIs and defining both curves' parameters together, rather than the
   single-PI marker interaction used for §2 steps 6-7 today.
8. Right-click (or whatever is standard) to end the command. Generate the alignment automatically.

## 3. Interrogating an alignment

Replace the PI-grid display with basic information about the alignment layout — PI points
themselves are no longer needed in that grid.

With each alignment segment represented in the Scene Collection:

- Selecting a segment highlights it.
- Display segment information in the 3D viewport: Start Point, End Point, Length, Radius, PI,
  Center of Circle, Spiral Type (as applicable to the segment type).
- Draw tangent and radial lines for the segment.

## 4. Interactively editing an alignment

Two editing scenarios:

1. **Moving a point.** Select the alignment's Start Point, End Point, or a PI point and drag it
   (or key in a new position) to relocate it.
2. **Changing smoothing curve parameters.** Select a smoothing curve to get the same UI element
   used to define it during creation (see §2, steps 6-7), and edit its parameters there.

For now, edits trigger a full wipe-out-and-regenerate of the alignment. A future iteration should
regenerate only the affected subset instead of the whole alignment.
