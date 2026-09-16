# Alignment Authoring — Requirements

Working requirements doc for the Bonsai alignment authoring UI (Civil Infrastructure tab and the
Alignment BIM tab). Captures planned work, not yet implemented unless noted. Update in place as
scope is refined or decisions are made; keep open questions marked as such rather than silently
resolving them.

## 1. Table-based editing

**Implemented.** The Alignment tab's segment tables (`ALIGN_PT_alignment_segments`) now support
edit/add/delete/reorder, one section (horizontal, a given vertical layout, or cant) at a time via a
pencil icon that swaps the read-only rows for an editable `UIList`
(`ALIGN_UL_h_segments`/`_v_segments`/`_cant_segments`, staged in `HorizontalSegmentRow`/
`VerticalSegmentRow`/`CantSegmentRow` on `CivilAlignmentProperties`). Interaction model is
"stage edits, then Apply" — add/remove/reorder rows and edit values freely with nothing touching
IFC until Apply, mirroring the existing `VerticalPIMarker` + `ALIGN_OT_apply_vertical_pi_curve`
precedent rather than writing per-cell. Apply (`ALIGN_OT_apply_h_segments`/`_v_segments`/
`_cant_segments`) rebuilds the whole layout in one pass (`ifcopenshell.api.alignment.
clear_layout_segments` + a `create_layout_segment` loop over the staged rows), then refreshes the
`IfcAlignment` representation, the 3D viewport mesh (`refresh_alignment_representation_object`),
and the vertical/cant profile view (`_refresh_vertical_profile_view`) — all three refresh targets
from the original ask are covered. Cancel discards the staged rows without touching IFC.

Segment type coverage: horizontal supports LINE, CIRCULARARC, and the full spiral-transition family
(CLOTHOID, CUBIC, HELMERTCURVE, BLOSSCURVE, COSINECURVE, SINECURVE); vertical supports
CONSTANTGRADIENT, PARABOLICARC, and CIRCULARARC. Excluded, each for a specific documented reason
(see `prop.py`'s `HorizontalSegmentRow`/`VerticalSegmentRow` docstrings): horizontal VIENNESEBEND
(its geometry also depends on the CANT segment at the same station — rail cant angle, gravity
centerline height — which this table has no place for) and vertical CLOTHOID (`ifcopenshell`'s own
mapper raises `NotImplementedError` for it). A row whose real IFC type is something else entirely
(e.g. a file authored outside Bonsai) shows as "Unsupported" and blocks Apply rather than silently
mis-editing it.

**Known, deliberate gap carried over from §4's existing note below:** Apply is a full rebuild, not
a partial/in-place regenerate — every segment in that layout gets a fresh GUID each time, same
limitation §4 already documents for the interactive draw tools. Not fixed here; a future "regenerate
only the affected subset" pass would benefit both this and §4 together.

**Known, deliberate non-validation (per the user, 2026-09-14):** a spiral-family row with equal
start/end radius, or a vertical CIRCULARARC row with equal start/end gradient, is degenerate input
that reliably crashes the geometry kernel (divides by a curvature-change factor that's exactly
zero) rather than erroring gracefully. This is intentionally left unguarded in
`tool.Alignment.validate_horizontal_segment_rows`/`validate_vertical_segment_rows` — the crash is
meant to stay visible as a reminder that the kernel itself needs the fix, not papered over with a
UI-side check.

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

Segments do **not** need to be represented as individual objects in the Scene Collection
(decided — the existing panel-list + on-the-fly viewport decorator approach is sufficient;
see `AlignmentSegmentDecorator`, which already covers the three items below):

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

**Implemented (2026-09-15):** horizontal PIs now also have a table-editing path
(`ALIGN_UL_horizontal_pi_markers`, staged in `HorizontalPIMarker`, loaded by
`ALIGN_OT_load_horizontal_pi_table` and applied by `ALIGN_OT_apply_horizontal_pi_table`), added
alongside the existing draggable-Empty workflow rather than replacing it — mirrors
`VerticalPIMarker`'s "PI list as a plain table" pattern exactly, reusing the same
`_reconstruct_horizontal_pis` classification the Empty-based `align.edit_horizontal_pis` already
used. Decided not to converge the two alignments onto one single editing model: a horizontal PI has
a real (X, Y) position in the actual 3D scene, so viewport dragging (with native snapping/numeric
entry) is a natural, already-working fit with no equivalent for vertical PIs, which only have
meaning in the profile view's synthetic (distance-along, elevation) space. The table is offered as
an additional, keyboard-precise path for horizontal rather than swapping out what already works.
