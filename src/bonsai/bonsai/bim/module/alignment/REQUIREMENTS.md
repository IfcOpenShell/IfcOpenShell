# Alignment Authoring — Requirements

Working requirements doc for the Bonsai alignment authoring UI (Alignment BIM tab). 
Captures planned work, not yet implemented unless noted. Update in place as
scope is refined or decisions are made; keep open questions marked as such rather than silently
resolving them.

## Status and work plan (resume here)

*Last updated 2026-09-25.* Branch `rab_infrastructure` (F:\ifcopenshell), 17 commits ahead of
`origin/rab_infrastructure` before this push (all pushed 2026-09-25). Commits this round, oldest first:
`5123046cf` typed 180 degree polyline angle fix (also its own branch/PR
`rab_polyline_tool_180_fix` -- **PR already open**), `97e04ca7e` cherry-pick of #9505 (IFC4x3 Road
and Bridge templates), `483a4c9a5` interactive PI editing, `2aee75b33` bearings/deflections in the
Angle field, `5b909888d` distinct vertical names + renaming, `53bacc069` grid-north bearings,
`53bb23aae` stationing referents on polyline curves (library), `1772f309e` polyline alignments (§5.1),
`ef30e9235` extending alignments + length matching (§9), `3507bd7e4` offset curve alignments (§5.2),
`fecdc1919` `update_layout_segments` (library), `a5a42c77b` keeping segment GlobalIds through
edits + Insert/Delete PI + PI click-pick (§11), `6ea213041` cant follows horizontal edits (§11),
`92039c2ea` exact values through the staged tables (§12).

**Work plan, in order:**

1. **§10 Manual referent definitions -- needs discussion with the user first.** Open questions:
   - Placement: by station + lateral offset (+ elevation?) along an alignment; picked in the viewport,
     typed, or both?
   - Which kinds: mileposts/reference markers, or general IfcReferent PredefinedTypes?
   - Behaviour on alignment edits: segment GlobalIds are now kept (§11), so should a referent
     attached to a segment move with it, or stay at its station? What happens when its segment is
     deleted (today `update_layout_segments` removes referents positioned on removed segments)?
   - Management UI: a list to view/edit/delete; how they relate to stationing (§4) and key-point
     (§8) referents; polyline alignments (§5.1) rely on these instead of key points.
2. **Offset alignment follow-ups (§5.2):** stationing referents on an offset alignment (the library's
   `add_stationing_referent` only handles composite and polyline curves), and a profile view for a
   3D offset curve.
3. **Bottom of the list -- the C++ pass (see the note at the end of §1):** moving the Python-side
   alignment geometry (PI solver, spiral integrands, join-radius root finding) to C++; the
   degenerate spiral crash (equal start/end radius spiral, equal-gradient vertical arc); the
   LINEARTRANSITION divide-by-zero in `_map_linear_transition` (constant cant across a transition,
   hit when a spiral-less curve sits next to a spiralled one); and
   [IfcOpenShell#5360](https://github.com/IfcOpenShell/IfcOpenShell/issues/5360) (sample straight
   regions by their end points only).
4. **Before the PR for the final work is posted: delete `dev_tests/`** (see Testing below).

**Smaller open items noted along the way:**
- Typed/dragged values are still limited to float32 resolution (~3 cm at 500 km coordinates) -- a
  string-backed field would be needed (§12).
- The cant layout's mirroring when a curve's turn direction flips is implemented but not directly
  tested (§11).
- An inserted PI is placed on the straight leg (zero deflection); applying without moving it gives
  two collinear tangents, which Edit PIs then can't reconstruct.
- `_cant_lookup_for_pi_markers` (VIENNESEBEND cant per PI) is positional, so it defaults after a PI
  insert/delete until the cant layout is regenerated.
- Upstream candidates, if wanted: `fecdc1919` (`update_layout_segments`) and `53bb23aae` (polyline
  stationing referents) as their own PRs.

**Testing:** headless Blender scripts (`blender --background --python-exit-code 1 --python X.py`,
Blender 5.1) and a UI-mode harness (`ui_invoke.py`, `ui_pick.py` with `--enable-event-simulate`)
are in `dev_tests/` next to this file (see its README). Library tests:
`src/ifcopenshell-python/test/api/alignment` (`python -m pytest -q test/api/alignment` from
`src/ifcopenshell-python`).

**Before posting the PR for the final alignment work: remove `dev_tests/`** (temporary development
scripts, committed only so work can resume on another computer).

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

**~~Known, deliberate gap carried over from §4's existing note below:~~ Apply is a full rebuild, not
a partial/in-place regenerate — every segment in that layout gets a fresh GUID each time.**
Fixed (2026-09-25) — see §11: every row loaded from an existing segment keeps it (and its GlobalId).

**Known, deliberate non-validation (per the user, 2026-09-14):** a spiral-family row with equal
start/end radius, or a vertical CIRCULARARC row with equal start/end gradient, is degenerate input
that reliably crashes the geometry kernel (divides by a curvature-change factor that's exactly
zero) rather than erroring gracefully. This is intentionally left unguarded in
`tool.Alignment.validate_horizontal_segment_rows`/`validate_vertical_segment_rows` — the crash is
meant to stay visible as a reminder that the kernel itself needs the fix, not papered over with a
UI-side check. Offer to user that this needs to be handled - offer to explore graceful handling
in the ifcopenshell geometry kernel, if not practical/possible there, then error guard in the UI.

**Deferred to the bottom of the list (per the user, 2026-09-24):** "We have added a lot of
calculations on the python side. It may be better (and faster) to have them on the C++ side." Revisit
this crash together with moving the Python-side alignment geometry (the PI-method solver,
`_spiral_curvature`'s integrands, the join-radius root-finding) into C++, rather than as a
stand-alone kernel patch.

The same C++ pass also covers (per the user, 2026-09-25: "If we are going to dig into the C++ side,
this needs to be addressed too"):

- **[IfcOpenShell#5360](https://github.com/IfcOpenShell/IfcOpenShell/issues/5360) -- optimize
  `piecewise_function_evaluator.evaluate` by eliminating unnecessary points in straight regions.**
  `evaluate()` samples the whole domain at a uniform step (default max 0.5), so straight runs get
  as many points as curves, while segment start/end positions -- the points that matter most -- can
  be skipped entirely. The issue's proposal: use Boost's Interval Container Library to find where
  the horizontal, vertical and cant curves are all straight at once, evaluate only the endpoints
  there, and keep the dense sampling for curved regions, always including segment boundaries. On
  the issue's bridge example this cut 24,676 evaluations to 15,159 (~39%) and improved accuracy.
  This is directly relevant here: every Apply regenerates the alignment's evaluated geometry.
- The LINEARTRANSITION divide-by-zero in `_map_linear_transition` (constant cant across a
  transition), found while implementing §11.

## 2. Interactive creation of a horizontal alignment

**Implemented (2026-09-18): Add Alignment dialog — optional stationing, unit-aware format.** Per
the user: "1) Make definition of stationing optional. 2) If the stationing option is enabled (the
default), then present it in station format consistent with the length unit for the project
(0+000 for meter, 0+00 for feet)." `ALIGN_OT_add_alignment` gained a `define_stationing`
`BoolProperty` (default True, matching prior behavior) and a `draw()` method (the dialog previously
had no custom layout, just Blender's default auto-draw of its two properties) that greys out the
Start Station field when unchecked. Unchecked, no stationing referent is created at all --
`tool.Alignment.create_alignment`/`core.create_alignment` both gained a matching
`define_stationing` parameter, skipping `add_stationing_referent` entirely rather than adding one
at station 0 and expecting the user to fix it later; this is a state the codebase already handles
gracefully elsewhere (`ALIGN_OT_set_start_station`'s own "no stationing at all yet" branch already
existed for alignments from before stationing was added, or loaded from a file that never had it),
so a stationing-less alignment isn't a new edge case, just a now-reachable one at creation time
too. For format-consistency: `tool.Alignment.format_station`/`parse_station` already delegated to
`ifcopenshell.util.alignment.station_as_string`/`station_from_string`, which already derive the
digit grouping from the project's `LENGTHUNIT` (metric: `V1+V2` with 3 digits before the decimal,
e.g. `0+000.000`; imperial: 2 digits, e.g. `0+00.00`) -- the dialog just wasn't using them for its
own default, showing a bare `"0"` regardless of project units. Fixed by pre-filling
`start_station` with `format_station(0.0)` in `invoke()` before the dialog opens. Verified via
headless Blender: a metric project's dialog now pre-fills `0+000.000`, an imperial one
`0+00.00`; parsing a typed station in each notation round-trips to the correct project-unit value;
`define_stationing=False` creates the alignment with no stationing referent at all. No regressions
in `test/core/test_alignment.py`/`test/tool/test_alignment.py` (40 passed, same one pre-existing,
unrelated failure noted throughout this doc).

Mimic the existing draw/edit tangent-line workflow from the Civil Infrastructure tab, with these
improvements:

1. Alongside Angle, also show the line's **Bearing** (e.g. `N 30 15 24 E`) — how civil engineers
   think about direction.
2. Allow manual input of Distance and one of Bearing, Angle, or Deflection Angle — likely via a
   pop-up input box.
   **Implemented (2026-09-24), per the user: "angle field accepted by input format".** No new
   field or pop-up: the existing Angle field of the horizontal draw tool and of Move with
   Distance/Angle (§4) also takes a bearing or a deflection, recognised by what's typed:
   - **Quadrant bearing:** `N 30 15 24 E`, `S45W`, or the Bearing readout's own format,
     `N 30°15'24.00" E`. Degrees can be decimal or D M S, separated by spaces, ° ' " or :.
   - **Deflection** from the previous leg's forward direction: `12 30 Rt`, `12.5 L`, `LT 12 30`.
     Right is clockwise.
   - **A plain number** is the polyline tool's own Angle, unchanged.

   Tab/Enter converts a bearing or deflection into that numeric Angle (counter-clockwise from the
   back leg), measured from the same last/second-to-last points the polyline tool uses, before it
   validates. So X/Y, snapping and placement are the tool's own, and the field then shows the
   angle it resolved to, with the Bearing readout confirming the direction.

   Implemented as a mixin, `_CivilAngleInput` (`_parse_civil_angle` is the pure parser), placed
   ahead of `PolylineOperator` in both alignment operators. The shared polyline tool that walls,
   slabs and so on use is untouched. The status bar shows a hint: "Angle also takes N 30 15 E or
   12 30 Rt".

   Direction letters are only taken in the Angle field. D isn't among them, because the polyline
   tool uses D to jump to Distance, so `Due N` must be typed as `N 0 E`. A deflection on a first
   leg is refused, since there's no previous leg to deflect from. Malformed text is refused with a
   specific message: a quadrant angle over 90°, minutes or seconds of 60 or more, or a deflection
   of 180° or more.

   Bearings are relative to Blender's +Y axis: the same north the Bearing readout uses, which
   doesn't account for a georeferenced true-north rotation.

   Verified headless:
   - The parser was checked on every format, on the refusals, and on a round trip of the Bearing
     readout's own output at 52 directions all the way round.
   - The real keyboard path was driven through the move tool's polyline input (typing letters and
     digits into Angle, the polyline tool's recalculation, placement). It covered bearings on a
     first leg and after one, left/right deflections including D M S, `0 R` straight on (which
     relies on the 180° fix), a deflection off a diagonal leg, and a plain angle unchanged. Each
     point landed exactly where expected.

   **Implemented (2026-09-24): bearings are grid bearings.** The Bearing readout, typed bearings,
   and the horizontal segment table's Bearing column previously all took Blender's/the project's
   +Y as north. They now measure from **grid north**: the map grid of the project's
   IfcMapConversion, which is the north a surveyor works to and what
   `ifcopenshell.util.geolocation` itself recommends over the context's TrueNorth for this.
   `_grid_rotation_deg` finds the rotation numerically, by converting a unit +X step through the
   same conversion the alignment code already uses for points: Blender world →
   `tool.Georeference.xyz2enh` for the draw tools, IFC project coordinates → `auto_xyz2enh` for
   the table, whose E/N column already used that frame. That way the conversion's sign conventions
   aren't re-derived. Without georeferencing it's 0, so nothing changes.

   Along the way, the table's own bearing formatter (`ui._rad_to_bearing`) rounded seconds up to
   60 without carrying (`N 59°59'60.0" E`). It now uses the readout's formatter, so text copied from
   the table can also be typed back into the Angle field.

   Verified headless with a 30° map rotation. Both frames report 30°. A leg along world +X reads
   `N 60°00'00.00" E` in the readout and the table alike, and typing `N 60 E` draws exactly along
   world +X.
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
   - **Spiral curve**: spiral length(s) (entry, exit, or both). **Implemented for all seven spiral
     families (2026-09-17)** — CLOTHOID, BLOSSCURVE, COSINECURVE, SINECURVE, HELMERTCURVE, CUBIC,
     VIENNESEBEND — chosen per PI via `PICurveMarkerProperties.spiral_family` /
     `HorizontalPIMarker.spiral_family` (entry and exit spirals at one PI always share the family —
     no UI for choosing them independently). `solve_horizontal_alignment_by_pi_method`'s `radii`
     element gained an optional 4th field, `(R, Lin, Lout, family)`; `compute_spiral_end` dispatches
     each family's own curvature-vs-length integrand, defined once in the new
     `ifcopenshell.api.alignment._spiral_curvature` module and reused by
     `_map_alignment_horizontal_segment` itself (so the solver's assumed endpoint and the geometry
     kernel's rendered endpoint can't drift apart -- they're built from the same coefficient math).
     The circular arc's own deflection (`theta_c`) is now derived from each spiral's *actual*
     accumulated deflection rather than the clothoid-specific `length / (2 * radius)` closed form,
     which happens to also hold exactly for Bloss/Cosine/Sine/Helmert (all normalized to the same
     total deflection as clothoid) but not for CUBIC's Cartesian small-angle approximation -- this
     fix is what makes every family close geometrically exactly, not just clothoid. HELMERTCURVE
     carries one pre-existing, unrelated approximation: its own two-piece representation
     (`_map_helmert_curve`, via `ifcopenshell_wrapper.helmert_curve_point`) has an inherent ~1e-6
     rad residual at the internal split between its two `IfcCurveSegment`s, present for any
     HELMERTCURVE regardless of whether it's authored via the PI method or the raw segment table --
     see the widened tolerance in `test_author_transition_curve_alignment`.

     **VIENNESEBEND (per the user, 2026-09-17): "I would like to see Viennese Bend in the selection
     list, but be disabled if there is not a cant layout. It will only work if there is an existing
     cant layout."** `spiral_family` is now a dynamic `EnumProperty` (`prop._spiral_family_items`)
     that only includes Viennese Bend once `tool.Alignment.has_real_cant_segments(alignment)` is
     true for the marker/row's alignment — unavailable rather than merely greyed out, since a plain
     Blender enum dropdown can't disable one entry. `_generate_alignment_segments` also rejects it
     defensively (same message as the raw table's existing check) in case a marker already held
     "VIENNESEBEND" before its cant layout was deleted.

     **`GravityCenterLineHeight` (per the user, same day, follow-up): "Yes, add the gravity
     centerline height field."** A new `gravity_centerline_height` FloatProperty on both
     `PICurveMarkerProperties`/`HorizontalPIMarker` (shown only when `spiral_family ==
     "VIENNESEBEND"`), defaulting to 0.0 (same degenerate/no-cant-contribution shape as before this
     field existed). Unlike every other per-PI field, it's paired with data the marker/row does
     *not* itself store: the outer rail's cant magnitude and the cant layout's RailHeadDistance, read
     live from the alignment's *current* real cant segment at the arc (`operator.
     _cant_lookup_for_pi_markers`, reusing `_reconstruct_horizontal_pis`'s own positional
     segment-to-cant-segment matching -- the same correspondence `tool.Alignment.
     sync_cant_segment_types` already relies on elsewhere) rather than being entered by hand, since
     the cant magnitude is defined by the separate Generate/Edit Cant Segments workflow, not the
     horizontal PI curve UI. `HorizontalSegmentDefinition` gained a `gravity_centerline_height`
     field so the value survives from `solve_horizontal_alignment_by_pi_method`'s own geometric
     closure (which now derives a per-spiral `cant_factor` from gravity centerline height + cant +
     rail head distance, needed for entry/exit spiral tangent-length fitting to stay exact) through
     to `layout_horizontal_alignment_by_pi_method`, which writes it to
     `IfcAlignmentHorizontalSegment.GravityCenterLineHeight` -- so the solver's assumed shape and
     the geometry kernel's later-rendered shape use the same cant-derived curvature, not just the
     same radius/length. `solve_horizontal_alignment_by_pi_method`'s `radii` element gained an
     optional 5th field, `(R, Lin, Lout, family, cant_params)`, where `cant_params` is `None` for
     every family except VIENNESEBEND. Verified end to end (a real cant layout, non-zero gravity
     centerline height, checked against the geometry kernel) in
     `test_solve_viennese_bend_with_cant_factor`.
     Along the way, fixed a real crash in `ifcopenshell.api.alignment._get_cant_segment`
     (`IndexError` on `alignment.IsDecomposedBy[0]` when an alignment has no cant layout *and* no
     child alignments) and a stale `prop.SUPPORTED_HORIZONTAL_TYPES` that didn't include
     `VIENNESEBEND`, which made an existing Viennese Bend segment show as "Unsupported" when loading
     the raw segment table for editing even though `HorizontalSegmentRow.predefined_type` already
     listed it as choosable.

     **Fixed (2026-09-17): stale read-only segment data after Apply.** Per the user: "When I am
     editing a PI with spiral-curve-spiral and change the spiral type, the start point of the
     spiral, curve, and spiral should update in the tabular data." Root cause: `tool.Blender.
     update_viewport()` (called by every Apply-type operator here) only tags a `VIEW_3D` area for
     redraw, but `ALIGN_PT_alignment_segments` (the read-only Start Point/End Point/Length/Radius
     breakdown, showing live IFC data on every `draw()`) lives in the Properties editor -- a
     different area, never told anything changed, since these operators mutate the IFC file
     directly rather than through Blender's own RNA/depsgraph. New `_tag_all_areas_redraw()` tags
     every area in every window and is now called from `_generate_alignment_segments` (covers
     `ALIGN_OT_apply_pi_curve`, `ALIGN_OT_apply_horizontal_pi_table`, and the initial draw operator)
     and `ALIGN_OT_apply_h_segments`.

     **Verified in a running Blender session (2026-09-17)**, headless via `blender --background`
     against the real registered `bl_ext...bonsai` addon (not just static analysis): built an
     alignment via the PI method, ran the actual `align.generate_cant_layout` /
     `align.edit_horizontal_pis` / `align.apply_pi_curve` operators. Confirmed `spiral_family`'s
     dropdown includes Viennese Bend only once a cant layout exists and correctly excludes it
     otherwise; setting a non-zero `gravity_centerline_height` and applying writes
     `GravityCenterLineHeight` to both spiral segments and produces the expected `LINE`/
     `VIENNESEBEND`/`CIRCULARARC`/`VIENNESEBEND`/`LINE` structure; the cant layout's own segments get
     synced to `VIENNESEBEND` too; and forcing Viennese Bend with no cant layout is rejected
     cleanly (`"Viennese Bend needs a cant layout first..."`) with the horizontal layout left
     untouched. Not individually re-verified live for the other five families (Bloss/Cosine/Sine/
     Helmert/Cubic) beyond Clothoid -- they share the exact same operator code path already
     exercised here, and are separately validated against the geometry kernel by the automated
     `ifcopenshell.api.alignment` test suite.

   **Confirmed future requirement**: compound curves (PCC, point of compound curvature — two
   arcs curving the same direction) and reverse curves (PRC, point of reverse curvature — two
   arcs curving opposite directions), joined directly with no tangent run between them, optionally
   with a spiral on the outer/non-joined side of either curve (e.g.
   Spiral-Circular-Spiral-Circular-Spiral). A PCC/PRC-capable solver variant (`join_next` on a PI's
   radii entry, closure-validated so the two curves' tangent lengths exactly span the PI-to-PI
   distance) exists as prior art on another branch, ported from upstream PR #8833, but was not
   brought in with the clothoid spiral-circular-spiral pass.

   **Open question, resolved: the UI is a per-PI toggle, not a 2-PI-simultaneous selection.**
   Originally worried this would need selecting 2 PIs and defining both curves' parameters
   together. Settled by the prior-art branch's own UI design (a different, older UI on that
   branch, not reused directly, but its approach carries over): `join_next` is a boolean on the
   *first* PI of the pair only ("join this curve directly into the next PI's curve") — the second
   PI's own curve is defined completely normally, with no awareness that it's being joined into.
   No 2-PI selection interaction was needed.

   **Implemented (2026-09-17).** Ported the prior-art `join_next` mechanism (see above) onto the
   current, more advanced solver -- which has diverged substantially past the ported PR #8833 code
   (7 spiral families via `_spiral_curvature`, per-family deflection closure, VIENNESEBEND cant
   params) -- rather than merging the old branch's now-superseded solver wholesale:

   - `solve_horizontal_alignment_by_pi_method`'s `radii` element gained an optional 6th field,
     `join_next` (`(R, Lin, Lout, family, cant_params, join_next)`), tracked across loop iterations
     as `previous_join_next`/`previous_tangent_out`. A new `_check_pi_join_closure` validates that
     the joining curve's tangent claim and the joined-into curve's tangent claim sum to the
     PI-to-PI distance, naming the excess/shortfall and both PIs on failure; the intermediate
     tangent-run LINE segment is suppressed when the previous curve's `join_next` was true, for
     both the plain-circular and spiral-transition branches. Spiral transitions are refused on the
     joined side of either curve (the joining curve's exit spiral, the joined-into curve's entry
     spiral) -- spirals remain fine on the outer, non-joined side, matching the original ask's
     "optionally with a spiral on the outer/non-joined side" and the ported code's own v1
     limitation. `join_next` on the last PI, or on a zero-radius (TANGENT) PI, is refused with a
     clear message. `layout_horizontal_alignment_by_pi_method` needed no functional change (it
     already just writes whatever segments the solver returns, in order) -- only a docstring note.
   - **Tolerance had to be loosened from the ported code's 1e-9 relative to 1e-4.** The reference's
     tests (pure Python/numpy, no Blender) passed cleanly at 1e-9. The Bonsai-level end-to-end test
     below did not: a golden-case PCC built from the exact same hand-derived hpoints failed
     closure by ~9e-8 relative -- because a real PI marker's position round-trips through at least
     one `Object.location`, which is **float32**, not Python's float64. 1e-9 would reject a PI pair
     the user positioned exactly right, purely because a marker got dragged through single
     precision along the way. 1e-4 (0.01%) still catches a genuinely too-tight/too-loose PI pair
     (a real user error, typically off by a meaningful percentage -- verified with a deliberately
     shrunk-by-10% PI pair, which still refuses cleanly) while comfortably absorbing that
     round-trip noise.
   - Bonsai/UI layer: `PICurveMarkerProperties`/`HorizontalPIMarker` (`prop.py`) gained a
     `join_next` `BoolProperty`; `_pi_curve_radii_entry` (`operator.py`) now always builds a
     6-tuple for any non-TANGENT curve (CIRCULAR included, previously a bare float -- needed so a
     plain, un-spiraled joining curve can still carry `join_next`) and passes `marker.join_next`
     through verbatim, trusting the solver to enforce every constraint (no spiral on the joined
     side, not the last PI, tangency closure). `_reconstruct_horizontal_pis` recognizes a PCC/PRC
     junction -- two `CIRCULARARC`s sharing a tangency point with no intervening `LINE`, each with
     at most one outer spiral -- and unlike every other shape it classifies, maps it to *two* PI
     specs rather than one, finding each curve's own PI by intersecting its bounding tangent line
     against the shared tangent line at the junction (reusing `_tangent_line_intersection` with
     the joined curve's own `StartPoint`/`StartDirection` standing in for the missing middle
     `LINE`). **Chains of 3+ directly-joined curves are now also recognized (2026-09-18, see
     below) — this was a documented v1 gap, now closed.** UI: a "Join to Next PI (Compound/Reverse
     Curve)" toggle
     in both the viewport marker panel (`ALIGN_PT_alignment_authoring`) and the horizontal PI
     table (`ALIGN_UL_horizontal_pi_markers`), shown only for `CIRCULAR`/`SPIRAL_CIRCULAR` curve
     types (the ones with no exit spiral, i.e. eligible to join) -- not pre-validated further
     (last-PI, closure) since the solver's own `ValueError` already surfaces cleanly as a
     `WARNING` through the existing `(ok, message)` contract every other validation here uses.
   - **Verified end-to-end in a running headless Blender session**, via the real registered
     operators (`align.edit_horizontal_pis` / `align.apply_pi_curve` / `align.finish_pi_editing`),
     not just static analysis: a golden PCC (two same-direction circular curves, R=600/R=300)
     produces exactly `LINE, CIRCULARARC, CIRCULARARC, LINE` with matching curvature signs, no
     intermediate `LINE`; the actual geometry-kernel tessellation (not just the solver's assumed
     math) renders a continuous 4000+ vertex mesh across the junction; reopening the alignment via
     Edit PIs correctly reconstructs both PIs with `join_next=[True, False]` rather than skipping
     them as unsupported; a PRC with an outer entry spiral on the joining curve produces
     `LINE, CLOTHOID, CIRCULARARC, CIRCULARARC, LINE` with opposite curvature signs; and a
     deliberately too-tight PI pair is refused with a `WARNING` naming both PIs and the shortfall,
     leaving the alignment's segments cleanly cleared rather than partially built or crashed.
     Ported and adapted the prior-art's pure-solver test suite onto the current tuple-based radii
     shape (`test_solve_compound_reverse.py`, `ifcopenshell-python/test/api/alignment/`) -- 9
     tests, plus the full existing `test/api/alignment` suite (128 tests) for regressions, all
     passing. `test/core/test_alignment.py` / `test/tool/test_alignment.py`: 40 passed, same one
     pre-existing, unrelated CSV-import interface-mismatch failure as noted elsewhere in this doc.

   **Fixed (2026-09-18): chains of 3+ directly-joined curves.** Per the user, closing the gap
   `_reconstruct_horizontal_pis` explicitly flagged above. The solver already supported this
   mechanically (`join_next` just chains PI to PI, with no assumption anywhere that a chain is
   exactly two curves long) -- only the *reconstruction* path (reopening a saved alignment via Edit
   PIs) special-cased exactly two adjacent `CIRCULARARC`s. Generalized: `arc_positions` (indices of
   `CIRCULARARC` between the two bounding `LINE`s) is now checked for being *any* contiguous run of
   length >= 2, not just exactly 2, and each curve's own PI is found the same way as before --
   intersecting its incoming tangent line (the previous curve's own `StartDirection` if it has one,
   else the real bounding `LINE`) against its outgoing tangent line (the next curve's own
   `StartDirection` if it has one, else the real bounding `LINE`) -- generalized from the
   hand-written 2-arc version to a loop producing N PI specs for N joined arcs, with `join_next=True`
   on every one but the last. The N==2 case now falls out of the same general code path rather than
   being special-cased, and produces byte-identical results to the version it replaced (verified).
   Spirals remain restricted to the outer, non-joined ends of the *whole* chain (never between two
   joined arcs), matching the solver's own constraint -- a spiral or any other segment type sitting
   between two arc entries breaks their positional contiguity and correctly falls through to
   "unsupported curve family/shape" rather than being misread.

   Verified via headless Blender, through the real operators (draw -> Edit PIs -> Apply, not just
   static analysis): a 3-arc all-left-turn PCC chain (R=600/300/450) reconstructs to exactly 3 specs
   with `join_next=[True, True, False]` and the correct radius/PI position for each, and round-trips
   through Edit PIs -> Apply cleanly, preserving the `LINE, CIRCULARARC, CIRCULARARC, CIRCULARARC,
   LINE` structure; a mixed PCC+PRC 3-arc chain (left/right/left) solves and reconstructs the same
   way. The existing 2-arc PRC case re-verified with no regression. `test/core/test_alignment.py` /
   `test/tool/test_alignment.py`: 40 passed, same one pre-existing, unrelated failure as always.

   **Fixed (2026-09-18): PCC vs. PRC key-point labeling.** Per the user: "there is code that gets a
   label for key points like 'P.T.' Does this handle the PCC and PRC points? It should probably do
   that." It didn't -- `ifcopenshell.api.alignment._get_segment_start_point_label` (used by both
   `update_key_point_referents`, which creates the labeled `IfcReferent`s at every segment
   transition, and `update_alignment_parameter_segment_tags`, which writes the same labels into
   `IfcAlignmentParameterSegment.StartTag`/`EndTag`) has a static lookup table keyed only on the
   pair of segment *types* at a transition -- fine for every other transition (e.g. `LINE ->
   CIRCULARARC` is always "P.C.", unconditionally), but a direct `CIRCULARARC -> CIRCULARARC`
   transition (a join_next junction -- the only way to get one, since spirals are never allowed on
   the joined side) was always labeled "P.C.C.", regardless of whether the two curves actually
   curve the same way (a true compound curve) or opposite ways (a reverse curve, which should be
   "P.R.C."). Fixed by special-casing that one transition ahead of the static table: compares the
   sign of `StartRadiusOfCurvature` (signed +left/-right, per the convention already established
   elsewhere in this codebase, e.g. bonsai's `_pi_curve_radii_entry`) between the two segments --
   same sign is "P.C.C.", opposite is "P.R.C." Removed the now-dead, now-misleading static
   "P.C.C." table entry for that cell (a comment there points to the code above instead). Verified
   with 2 new tests in `test_get_segment_start_point_label.py` (left-left and right-right both
   still "P.C.C."; left-right and right-left both now "P.R.C."), plus the existing tests in that
   file and the full `test/api/alignment` suite for regressions (130 passed, was 128 -- the 2 new
   ones).

   **Fixed (2026-09-17): laying out PI curves now fails gracefully when the curve is too long for
   the space available.** Two distinct gaps existed, both in `solve_horizontal_alignment_by_pi_method`,
   and both are now closed:

   - **Was not validated at all, now is:** `tangent_run` (the straight run left over between the
     previous curve's end and this curve's start) is computed for every PI in both the plain-circular
     branch and the spiral-transition branch, but was only ever checked for being *large enough to
     bother emitting* a `LINE` segment (`1.0e-03 < tangent_run`), never for being negative. When a
     curve's own radius/spiral lengths need more tangent distance than two PIs are actually apart
     (PIs too close together, or the curve too large for the gap), `tangent_run` went negative and
     the solver silently kept going, producing overlapping/self-intersecting geometry with no error
     at all -- this was likely the single biggest practical way a user hit "too long a curve" in
     ordinary use (tightening one PI's radius without checking neighboring PIs). Both branches now
     raise `ValueError(f"PI {n}: ...too large/too long for the distance between PIs...")` the moment
     `tangent_run < -1.0e-03`, naming the specific offending PI (1-based, matching this module's
     "PI n" labels elsewhere) and suggesting the fix (smaller radius/shorter spirals, or move the
     PIs farther apart). Verified this doesn't false-positive on genuinely-tight-but-valid curves
     (`test_solve_errors_when_tangent_run_goes_negative` checks both a failing and a fitting radius,
     and both a failing and a fitting spiral pair, on the same PI) -- the check only ever fires when
     a curve would otherwise have produced backtracking geometry, and it doesn't affect the existing
     `xBT/yBT` chaining that already nets consecutive curves' tangent consumption against each other
     across PIs (verified via the full `test/api/alignment` suite, no regressions).
   - **Was validated, but not gracefully, now is:** the existing `"spiral transition curves are too
     long; their combined deflection exceeds the PI deflection angle"` `ValueError` (entry + exit
     spiral deflection together exceeding the PI's own turn angle) is a real, separate check (still
     present, unchanged) -- but nothing between the solver and the user's screen used to catch it
     specifically, so it propagated uncaught through `_generate_alignment_segments` into
     `tool.Ifc.Operator`'s generic exception handler, surfacing as "Operation partially completed
     (IFC changed, Blender state may be stale). Press Ctrl+Z to restore the previous state."

   Both are now reported the same way validation errors already are elsewhere in this module (e.g.
   `ALIGN_OT_apply_h_segments`'s cant-layout check): `_generate_alignment_segments` catches `ValueError`
   from `tool.Alignment.safe_layout_horizontal_by_pi_method`, clears whatever segments the solver had
   already written for earlier PIs before hitting the failing one (the solver is a streaming generator
   consumed segment-by-segment, so partial writes can happen before the failure), and returns
   `(False, message)` -- the same `(ok, message)` contract every caller here already handles, reporting
   a `WARNING` with the specific message and finishing cleanly (`{"FINISHED"}`, matching the existing
   Viennese-Bend-without-cant precedent) rather than crashing. Both `ValueError` messages now name the
   offending PI number for both of these fixed cases plus the pre-existing "PI deflection angle is
   zero" case, since all three share the same message-formatting change.

   Two ways to specify a PCC/PRC junction, not mutually exclusive -- both reduce to the same
   underlying constraint (the two curves' tangent lengths must sum to the PI-to-PI distance), just
   choosing a different one of the two curves' parameters as the "given" and solving for the rest:

   1. **Implemented (2026-09-18): radius of the first (joining) curve stated, the second
      (joined-into) curve's radius (and curve type) computed automatically.** Per the user: "Working
      with the first PI, set the curve type and radius. Check to Join to Next box and Click Apply
      Curve. This should compute the required radius of the curve at the next PI in order to have
      the join happen. The section curve type should match the first, except Spiral-Circular should
      be Circular-Spiral at the next PI." Previously the joined-into PI's own radius had to already
      be set by hand to a value that happened to satisfy closure, found only by trial and error
      against the `WARNING` naming the shortfall/excess.

      Solver (`solve_horizontal_alignment_by_pi_method.py`): the plain-circular and spiral-transition
      tangent-length math the main loop already computed inline is extracted, unchanged, into a
      shared `_solve_spiral_curve` helper (a small "extract function" refactor, verified
      behavior-preserving by the full existing 130-test suite passing unchanged before adding
      anything new) -- both the main loop and the new solving code below call it, so there is only
      ever one place this math is written, never two independent (and possibly subtly drifting)
      derivations. Two new public functions reuse it: `curve_tangent_out(delta, radius,
      entry_length, exit_length, family, vb_params, pi_number)` (the tangent length a *fully known*
      curve claims on its forward side -- the plain-circular closed form, or `_solve_spiral_curve`'s
      `pi_to_st`) and `solve_join_next_radius(delta, target_tangent_in, exit_length, family,
      vb_params)` (the inverse problem: given the tangent length the joined-into curve's entry side
      must claim, solve for its radius). `_check_pi_join_closure` was split to expose its residual
      as a standalone `_pi_join_closure_excess` so a root-finder can drive it toward zero directly,
      rather than only being able to detect success/failure by parsing exception text.

      For plain `CIRCULAR` this has an exact closed form (`R = target / tan(delta/2)`, the trivial
      algebraic inverse of the one-line formula already in the solver -- not a re-derivation) and is
      solved directly. For `CIRCULAR_SPIRAL` there is no closed form -- an exit spiral, even though
      it sits on the curve's *outer*, non-joined side, still changes how much of the PI's deflection
      is left for the circular arc, which changes the *entry*-side tangent claim as a function of
      radius too -- so this bisects against `_solve_spiral_curve`'s own `ts_to_pi`, guaranteeing
      whatever radius it returns is correct by construction (it's the exact same code path a real
      Apply uses), not by hoping an independent derivation matches. Getting the bracket-search
      direction right took one real bug fix: a fixed-length spiral's own deflection is proportional
      to curvature, i.e. to `1/R` -- so the *invalid* region (exit spiral alone exceeding the PI's
      whole deflection) is at *small* radius, and validity only improves as radius grows, the
      opposite of the first (wrong) assumption the bracket search was written with, which caused it
      to give up immediately on the very case it was meant to solve. Fixed by first finding the
      smallest geometrically-valid radius (growing from a small starting point until
      `_solve_spiral_curve` stops refusing), then bracketing/bisecting upward from there.

      Bonsai layer (`operator.py`): `_apply_join_next_radii(items, hpoints, cant_lookup)` walks a
      PI list left to right (`PICurveMarkerProperties` from viewport markers, or `HorizontalPIMarker`
      table rows -- both expose the same fields `_pi_curve_radii_entry` already relies on, so one
      function serves both), and for any PI with `join_next=True`, computes and *writes back onto
      the next PI's own property* its radius, curve type (`CIRCULAR` -> `CIRCULAR`, `SPIRAL_CIRCULAR`
      -> `CIRCULAR_SPIRAL` exactly as asked), and, for the spiral case, the mirrored exit spiral
      (same family, same length as the joining PI's entry spiral -- a symmetric default, chosen
      since nothing in the request specified an asymmetric one and it's the natural "the join looks
      the same from both sides" reading). Writing back onto the actual property (not just using the
      value internally for this one Apply) means the panel/table shows what was actually used, a
      later Edit PIs reconstruction sees consistent values, and dragging a PI and re-Applying
      recomputes fresh rather than reusing a stale number (verified). Left-to-right order means a
      chain of 3+ joined curves resolves pairwise down the chain automatically -- PI 2's
      auto-computed radius (from closing against PI 1) is what PI 3 closes against next, if PI 2 is
      also `join_next`. Wired into both `ALIGN_OT_apply_pi_curve` and
      `ALIGN_OT_apply_horizontal_pi_table`, *before* `radii` is built and before
      `_generate_alignment_segments` touches anything -- an unsatisfiable geometry (this can
      genuinely happen depending on PI placement, not just user error) is reported as a `WARNING`
      through the same `(ok, message)` contract every other validation here uses, and the existing
      alignment's segments are never touched at all (not even the "solve first, clear second"
      protection from the "3+ chains" fix above is needed here, since this whole computation happens
      before `_generate_alignment_segments` is even called).

      Verified end-to-end in headless Blender via the real registered operators, leaving the
      joined-into PI completely untouched (its stock defaults from marker creation) except for
      enabling `join_next` on the joining PI: a plain `CIRCULAR` join produces a real closing PCC/PRC
      with no intermediate `LINE`; a `SPIRAL_CIRCULAR` join correctly mirrors onto `CIRCULAR_SPIRAL`
      with matching family/length and produces `LINE, <family>, CIRCULARARC, CIRCULARARC, <family>,
      LINE`; dragging the joining PI and re-Applying recomputes a different (correct) radius rather
      than reusing the stale one; and a deliberately unsatisfiable pair (PIs too close for the
      requested radius) reports a clean `WARNING` in under a few milliseconds, with the existing
      segments left exactly as they were. Pure-solver level: 7 new tests
      (`test_solve_join_next_radius.py`) covering the closed-form and bisection cases, a PCC and a
      PRC, a 3-curve chain, and the rejection paths -- each checks the solved radius actually closes
      when fed back through the real solver and produces a genuinely continuous chain (position +
      direction), not just that bisection converged to *something*. Full `test/api/alignment` suite:
      137 passed (was 130, +7 new). `test/core/test_alignment.py` / `test/tool/test_alignment.py`:
      40 passed, same one pre-existing, unrelated CSV-import failure as always.

   2. **Implemented (2026-09-24): distance to the junction stated, *both* curves' radii computed.**
      The split point directly gives both tangent lengths (T1 = the stated distance from the first
      PI, T2 = PI-to-PI distance minus T1), and each radius is solved from its own tangent length.

      One correction to the original plan ("applied twice, no new math"):
      `solve_join_next_radius` only solves the *entry*-side claim (`ts_to_pi`) of a curve with an
      optional exit spiral. The joining curve needs the mirror problem, its *forward*-side claim
      (`pi_to_st`) with an optional *entry* spiral (SPIRAL_CIRCULAR). The bisection core was pulled
      out, unchanged, into a shared `_solve_radius_for_tangent`, and a new public
      `solve_joining_radius(delta, target_tangent_out, entry_length, family, vb_params)` sits
      beside `solve_join_next_radius`, so there is still only one copy of the root-finding and one
      copy of the curve math (`_solve_spiral_curve`). Plain CIRCULAR uses the same closed form as
      before.

      Bonsai layer: `PICurveMarkerProperties`/`HorizontalPIMarker` gained `join_mode`
      (`RADIUS`/`DISTANCE`, shared `prop.JOIN_MODE_ITEMS`) and `join_distance` (LENGTH, local IFC
      units, the same units as `radius`). In `_apply_join_next_radii`, DISTANCE mode checks that
      `0 < join_distance < PI-to-PI distance`, solves and writes back the joining PI's own radius,
      and then carries on exactly like mode 1 for the joined-into PI (radius, curve-type mapping,
      mirrored spiral). RADIUS mode now also writes the resulting junction distance back into
      `join_distance`, so switching modes starts from the current geometry. The new
      `_populate_join_distances` does the same after Edit PIs and Edit PIs (Table) reload a
      saved alignment. It reads the radius and never changes it.

      DISTANCE is refused on a PI that is itself joined into by the previous PI ("PI n's radius
      is already fixed by the join from PI n-1; use Radius mode"), because its radius is already
      fixed by the earlier join. In a chain, distance mode is only available on the first curve.

      UI: once "Join to Next PI" is checked, the marker panel shows an expanded Radius | Distance
      selector, and the PI table shows a compact one. In Distance mode the distance field appears
      and the radius field stays visible but disabled, showing the computed value after Apply.
      `PIMarkerDecorator` draws a yellow crosshair at the junction point on the PI-to-PI leg.
      It updates live as the distance is typed or a marker is dragged, before Apply. After any
      Apply, `ALIGN_OT_apply_pi_curve` now relabels *every* interior marker, not just the active
      one, since a join can change radii on other markers too.

      Verified in headless Blender through the real registered operators
      (`edit_horizontal_pis` → `apply_pi_curve` → `finish_pi_editing` → reload →
      `load_horizontal_pi_table` → `apply_horizontal_pi_table`):
      - A CIRCULAR PCC by distance (T1=300 on a 450 leg) produces `LINE, CIRCULARARC, CIRCULARARC,
        LINE` with the junction within float32 noise of the requested point, and both radii
        match the closed form.
      - The crosshair's world position matches that point.
      - A RADIUS-mode Apply writes the correct `join_distance` back.
      - An out-of-range distance is refused with a WARNING, and the segments are left untouched.
      - A SPIRAL_CIRCULAR/BLOSSCURVE join by distance produces
        `LINE, BLOSSCURVE, CIRCULARARC, CIRCULARARC, BLOSSCURVE, LINE` with the junction on the
        requested point.
      - Reopening via Edit PIs and via the table pre-fills `join_distance`=280.
      - The table path by distance produces the expected PCC.
      - The chain case is refused.

      Pure solver: 9 new tests in `test_solve_join_next_radius.py`, covering closed form,
      bisection, PCC and PRC by distance with a junction-position check, and CLOTHOID/BLOSSCURVE/CUBIC
      outer spirals by distance, plus the rejection paths. Full `test/api/alignment` suite: 146 passed
      (was 137). `test/core/test_alignment.py`/`test/tool/test_alignment.py` could not be run this
      session: the Bonsai test conftest now fails to import the `pytest-blender` plugin in this
      environment.

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

**Fixed (2026-09-24): "current value 'n' matches no enum ... active_alignment_id_str" after
deleting an alignment.** The alignment dropdown (`CivilAlignmentProperties.active_alignment_id_str`)
stores its choice as an index into a list rebuilt from the file each time. Deleting an alignment
shrank that list, leaving the stored index past its end (Blender warned on the next read) or,
worse, silently pointing at a *different* alignment. Delete Alignment now clears the dropdown
first, and `prop._clamp_alignment_enum` resets any out-of-range stored choice before the
selection handler or the panel read it, which also covers undo and loading another file. Verified
headless: deleting the selected alignment, and a stale index, no longer warn. The key-point test,
which deletes an alignment and used to print the warning, is now clean.

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

**Implemented (2026-09-18): dragging the Start Point or End Point.** Was a real, confirmed gap
(only interior PIs ever got a marker/table row — see the "Not yet built" note this replaces).
Mirrors the interior-PI marker pattern exactly: `_create_endpoint_marker` builds the same kind of
draggable, XY-plane-locked `PLAIN_AXES` Empty as `_create_pi_markers`'s interior markers, tagged
with a new `PICurveMarkerProperties.role` field (`"PI"`/`"START"`/`"END"`) instead of the
previously-implicit "every marker is an interior PI" assumption. `_create_pi_markers` now always
creates Start/End markers alongside any interior ones — including when there are zero interior PIs
at all (a dead-straight two-point alignment still gets draggable endpoints) — and
`ALIGN_OT_edit_horizontal_pis` does the same for a previously-drawn/imported alignment.
`ALIGN_OT_apply_pi_curve` (poll broadened to accept any marker, not just an interior one) now reads
the Start/End points from these markers' current `.location` instead of always calling
`tool.Alignment.get_alignment_start_end_points()` — that read is kept only as a defensive fallback
for a marker set predating this feature. `PIMarkerDecorator` and `ALIGN_PT_alignment_authoring`
both got a third, endpoint-specific branch (blue dot/"Start"/"End" label; a minimal panel box with
just Apply/Finish, no curve-type fields, since an endpoint has no curve). Verified end-to-end via
direct script (headless Blender, since `test/bim/` needs `pytest-bdd`, not installed): create
markers → drag Start/End → Apply → new segment start point matches the dragged location exactly;
also verified a straight 2-point alignment gets Start/End markers with no interior PI, and that
endpoint markers never count toward the "N PIs still need a curve" status-bar hint. Regression
tests added in `test_alignment_operators.py` (`TestStartEndPointMarkers`).

**Fixed (2026-09-24), per the user: "If a horizontal alignment is just a straight line, there is
no way to activate the PI editing to drag/drop the end points."** Drawing a straight line already
left Start/End markers. Reopening one via Edit PIs failed, though:
`_reconstruct_horizontal_pis` treated a lone LINE segment as "no bounding tangent" (it looks for
PIs *between* two LINEs), reported it as unclassifiable, and Edit PIs refused to create any markers.
A single LINE is now recognised as a valid alignment with zero interior PIs, so Edit PIs creates
just the Start/End markers. Everything downstream already handled zero interior PIs, the same way
drawing a straight line does. Verified headless: Edit PIs creates Start/End on a straight alignment,
dragging End and applying produces one LINE ending exactly at the dragged point, and Edit PIs
(Table) loads with zero rows instead of erroring.

**Also fixed alongside this (per the user, 2026-09-18): Finish now reselects the alignment.**
`ALIGN_OT_finish_pi_editing` removes the marker Empties, and if the active object was one of them
(the common case — you just dragged and applied it), Blender left nothing selected afterward. It
now explicitly reselects the alignment's own object first, same convention already used by
`ALIGN_OT_add_alignment`/`ALIGN_OT_draw_horizontal_alignment`.

**Confirmed future requirement (per the user, 2026-09-17): typed numeric input while dragging a
PI/Start/End marker, matching the original draw command.** Today, dragging one of these marker
Empties (see the "Implemented (2026-09-18)" note above, and the interior-PI markers from §2 step 6)
is plain Blender object movement — `_lock_pi_marker_transform` only locks Z/rotation/scale, so the
drag itself is Blender's native Move, which does already accept *some* numeric entry (`G` then type
an X value, `Tab`, a Y value, `Enter`; or the N-panel's Location fields) — but that's Blender's
generic transform input, not the civil-engineer-style Distance + Bearing/Angle/Deflection Angle
popup that `ALIGN_OT_draw_horizontal_alignment` already has via the `PolylineOperator` mixin (D/A/X/Y
typed entry, §2 step 2). No marker-drag path reuses that input system. The building blocks already
exist (`PolylineOperator`/`PolylineDecorator`'s D/A/X/Y-with-Tab-cycling UI, and the markers are
already modal-draggable Empties) — this would be extending that proven input overlay to the
marker-drag interaction (or a bespoke modal replacing the plain Move-tool drag) rather than
inventing a new mechanism. Same gap exists for vertical's PI editing per §6 item 2, once that gets
its own drag-to-edit path — one input system, ideally shared by both. Not yet designed or built.

**Implemented (2026-09-24).** Per the user, together with a heads-up display for the vertical drag
("it needs some heads up display information about station, elevation, slope, distance along so
you have some clue about what the drag operation is doing. I guess that is related to 4").

- **Horizontal: `ALIGN_OT_move_pi_marker` ("Move with Distance/Angle").** There's a button in the
  marker's panel box, for an interior PI and for Start/End. This isn't a new input system: the
  operator *is* a `PolylineOperator`, exactly like `ALIGN_OT_draw_horizontal_alignment`. It has
  the same D/A/X/Y fields, snapping, axis locks, status-bar instructions, and the draw tool's own
  Bearing readout (`_draw_bearing_hud`, reused as-is). The trick is seeding the polyline with the
  moved marker's neighbours (`_move_marker_anchors`), so every typed value means what it meant
  when the PI was first drawn:
  - Distance is from the previous point.
  - Angle is measured against the leg before it, using the draw tool's own convention:
    counter-clockwise from the back leg, and a negative value turns the other way. The mouse
    doesn't pick the side.
  - With only one point before it, Angle is measured against +X, like a first drawn leg.
  - The Start marker has no previous point, so it's measured backwards from PI 1 (anchors End/PI 2
    → PI 1).

  A click or Enter places the marker. RMB/Enter with nothing typed, or Esc, leaves it where it
  was. Backspace is swallowed, because it would otherwise delete an anchor point. As with any
  marker move, nothing touches IFC until Apply Curve. Native Blender G-drag still works exactly
  as before.
- **Vertical: typed values and a readout in `ALIGN_OT_drag_vertical_pis`.** See §6 item 2,
  "Implemented (2026-09-24), follow-up". The typed Elevation/Slope/Distance system from vertical
  drawing is now a shared mixin (`_VerticalTypedInput`) used by both the vertical draw and drag
  tools, so it's one input system, as this note asked for. Horizontal and vertical each keep
  their own native one: the polyline tool's D/A/X/Y for plan, E/S/D for profile.

**Fixed (2026-09-24), per the user:** a pre-existing bug in the shared polyline tool
(`tool.Polyline.calculate_x_y_and_z`, used by every Bonsai polyline tool, including the horizontal
alignment draw tool). A typed Angle of exactly ±180° ("straight on") forced the result direction's
X to -1, which is only right when the previous leg runs along +X. With a previous leg at any other
angle, the point landed in the wrong place. For example, a 45° leg with D=500, A=180 put the point
about 610 away in the wrong direction. ±180 now uses the previous leg's own direction, which also
avoids rotating about an undefined axis when the mouse sits on that leg's line. The one-point case,
measured from +X, still goes along -X as the old special case intended. Regression tests were
added in `test/tool/test_polyline.py` (`TestCalculateXYAndZStraightOn`: a 45° leg at +180 and -180,
and the single-point case). They were run directly in headless Blender, since `pytest-blender`
isn't installed here. A real 180° marker move was also added to the move-marker check.

**Fixed (2026-09-17): the start-station "dot" wasn't following the Start Point marker when it
moved, for alignments bootstrapped via Blender's generic Add Element rather than the Alignments
tab's own Add Alignment button.** When an alignment is first created, the start stationing referent
(distance-along 0.0) gets a viewport Empty immediately (`create_object_for_referent`) — visually a
small dot at the alignment's start. Dragging the Start Point marker and clicking Apply Curve is
supposed to keep that dot in sync: `_generate_alignment_segments` calls `tool.Alignment.
sync_stationing_referent_placements()` → `sync_referent_object_placement()` after every rebuild,
re-resolving the referent's `IfcLinearPlacement` (an `IfcPointByDistanceExpression` at
`DistanceAlong=0.0` on the layout's basis curve) and writing the result to the referent's Blender
object.

Set up the dev environment properly to chase this down live rather than by inspection alone: the
`bonsai`/`ifcopenshell` packages Blender's extensions folder actually imports
(`extensions/.local/lib/python3.13/site-packages/{bonsai,ifcopenshell}`) turned out to already be
symlinked straight to this repo (this repo's own `scripts/dev_environment.py` had already been run at
some point) — confirmed by enabling the addon in a `blender --background` session and checking
`bonsai.__file__`. Reproduced the exact reported interaction end to end from there (create alignment
→ draw → Edit PIs → drag Start marker → Apply Curve, via the real, registered operators, no mocking)
in a headless script.

That repro came back clean for the Alignments-tab-button path (`tool.Alignment.create_alignment()` →
`ifcopenshell.api.alignment.create()`): the dot followed the dragged Start point correctly, including
across a second edit/drag/Apply cycle and after Finish. So the sync mechanism itself, and the
IFC-level placement math underneath it, were never the bug.

The same repro against the *other* alignment-creation path — `tool.Alignment.
add_horizontal_layout_to_alignment()`, used to bootstrap an alignment created via Blender's generic
Add Element rather than the Alignments tab's Add Alignment button — reproduced the reported symptom
exactly: the dot stayed pinned at the origin no matter how far or how many times the Start marker was
dragged and applied. Root cause: that function calls `_create_geometric_representation()` (which sets
`alignment.Representation`) and then `add_stationing_referent()` *before* `_add_zero_length_segment()`
— so at the moment the referent is created, the basis curve has zero segments on it yet, and
`add_stationing_referent()`'s own logic (see its docstring) falls back to a plain `IfcLocalPlacement`
at the origin instead of an `IfcLinearPlacement` tracking the curve. Every later real draw/Apply calls
`ifcopenshell.api.alignment.create_representation()`, whose one job is to restate exactly this kind of
origin-placed referent onto the curve once real geometry exists — but it opens with `if alignment.
Representation: return`, and `alignment.Representation` was already set by that earlier
`_create_geometric_representation()` call, so the restate is permanently unreachable. The referent's
placement was never wrong by a little; it just never got upgraded past the origin at all.
`ifcopenshell.api.alignment.create()` (the function the *other*, working creation path calls) avoids
this by adding its zero-length segments before returning — i.e. before any caller can add a stationing
referent — so `add_stationing_referent()` always finds a segment already on the curve.

Fix: reordered `add_horizontal_layout_to_alignment()` to add the zero-length segment before the
stationing referent, mirroring `create()`'s own ordering. Verified with the same headless script:
referent placement is `IfcLinearPlacement` from the moment of bootstrap (rather than
`IfcLocalPlacement`), and the dot now follows the Start marker correctly through drag → Apply, a
second drag/Apply cycle, and Finish — matching the already-working Add Alignment path. Confirmed no
regression via the existing `test/core/test_alignment.py` and `test/tool/test_alignment.py` suites
(40 passed; the one pre-existing failure there, an unrelated CSV-import interface mismatch, reproduces
identically with this fix reverted, so it predates this change). `test/bim/` itself still can't run in
this environment (`pytest-bdd` not installed, same gap already noted elsewhere in this doc).

**Fixed (2026-09-17): the alignment object's own origin (its click-to-select dot) fell behind the
curve's real start point after any PI edit past the first draw.** Per the user, after chasing several
false leads first (see the trail below — kept for the next person hitting the same confusion): "the
dot is annoying and we didn't have it before."

`refresh_alignment_representation_object` special-cases an interactively-drawn alignment so its
Blender object's own origin sits at the curve's start point (rather than at Blender's `(0,0,0)`,
which is what happens by default unless the point is "far away" in `tool.Loader.is_point_far_away`'s
sense — see the code comment there) by baking the mesh's vertices relative to that start point and
carrying it as `matrix_world`'s translation, via a `cartesian_point_offset` mesh property. That
special-casing only ran the *first* time the object was created, though: every later call (from every
Apply, via `_generate_alignment_segments`) took the "already a MESH object" branch, which just called
the generic `tool.Geometry.reload_representation()`. That reload path *reuses the already-stored*
`cartesian_point_offset` rather than recomputing it — correct for rendering the curve itself (mesh
vertices and `matrix_world` still agree with each other, just both anchored to a stale point) but it
meant the object's own origin silently stayed wherever the curve's start was on the very first draw,
never advancing as PIs got edited afterward — while the actual curve, and the separate stationing
referent object, both did keep moving correctly. Three genuinely different things were all named "the
dot" across this investigation, which is what made it confusing to pin down:

1. The stationing referent (`IfcReferent/... 0+000.000`) — always correct; this is the one meant to
   mark the start station and it always tracked the drag correctly, including before this fix.
2. The alignment's own object-origin dot — the one actually broken here, now fixed.
3. Blender's default per-selected-object origin indicator is what dot 2 *is*, which is why comparing
   it to the alignment object's own `.location` reads as "the dot is stuck" rather than "the object's
   origin is stuck" — same underlying fact, just easy to describe either way mid-investigation.

Fix: `refresh_alignment_representation_object` now recomputes `cartesian_point_offset` fresh from the
current geometry and rebuilds the mesh (`create_mesh`) on *every* call, reusing the existing object/mesh
datablock rather than reloading in place or recreating the object — preserves object identity (so
selection/outliner state survives an Apply) while keeping the origin anchored to the curve's *current*
start point. Verified via headless script: object identity is preserved across repeated drag/Apply/
Finish cycles, the origin correctly follows the Start marker each time (not just once), and no orphaned
mesh datablocks accumulate (the previous mesh, now unused, is explicitly removed once `obj.data` moves
to the fresh one). Also verified against the user's own saved file. No regressions in
`test/core/test_alignment.py` / `test/tool/test_alignment.py` (40 passed; same pre-existing, unrelated
CSV-import failure as before).

**The false leads, for the record (all confirmed correct, none needed fixing):**
- The stationing referent itself, first suspected — proven correct via a pure-`ifcopenshell` placement
  resolution test (no Blender objects involved) and later via headless replay of the real operators.
- A second alignment-creation path, `add_horizontal_layout_to_alignment` (used by Blender's generic
  Add Element, as opposed to the Alignments tab's own Add Alignment button) — this one *was* genuinely
  broken (referent permanently stuck at `IfcLocalPlacement`/origin, a real ordering bug, fixed
  separately — see the "Fixed (2026-09-17): the start-station 'dot' wasn't following..." entry above)
  but turned out to be a different bug from the one the user was actually hitting, since they'd used
  the Add Alignment button.
- A theory that `AlignmentSegmentDecorator`'s cached segment highlight goes stale after Apply (it does,
  in principle — its cache tracks a `segment_id` that Apply's full rebuild deletes and replaces with a
  fresh one — but `ALIGN_OT_edit_horizontal_pis` already uninstalls that decorator on entry, so it
  never stays installed across the exact drag/Apply/Finish sequence being debugged).
- A theory that this was a pure viewport-repaint lag rather than a real data problem — ruled out once
  the user reported the *numeric* N-panel Location field itself (not just the on-screen paint) showing
  a stale value, which a render-only lag can't explain.

## 5. Alternative alignment definition methods

**Confirmed future requirement (per the user, 2026-09-16), re-scoped by the user on 2026-09-24.**
Beyond the PI-based tangent+curve workflow (§2), support the other *geometry definitions* IFC 4.3
allows for an IfcAlignment. Per the IfcAlignment documentation ("Supported shape representations"):

* _IfcPolyline_ or _IfcIndexedPolyCurve_ as a 3D alignment by a 3D polyline representation (such as
  coming from a survey).
* _IfcPolyline_ or _IfcIndexedPolyCurve_ as a 2D horizontal alignment by a 2D polyline
  representation (such as in very early planning phases or as a map representation).
* _IfcOffsetCurveByDistances_ as a 2D or 3D curve defined relative to an _IfcCompositeCurve_,
  _IfcGradientCurve_ or another _IfcOffsetCurveByDistances_.

These are geometry definitions *without* the business logic (no IfcAlignmentHorizontal/Vertical/Cant
layouts), which is what distinguishes them from the layout-based alignments everything else in this
document edits. (The original 2026-09-16 wording read "3D/2D polyline" as a way of *generating*
layouts from points -- each vertex a PI. Superseded: per the user, "the idea comes from the supported
shape representations for an IfcAlignment".)

1. **Polyline alignment (2D or 3D)** -- the current focus, see §5.1 below.
2. **Offset curve alignment (IfcOffsetCurveByDistances)** -- see §5.2 below.

### 5.1 Polyline alignment

**Requirement (per the user, 2026-09-24).** Sources of the data:
1. **Coming in from an IFC file** -- an IfcAlignment whose representation is an IfcPolyline or
   IfcIndexedPolyCurve (2D or 3D) must load, display, and be editable.
2. **Drawn by the user in the 3D viewport**, either constrained to Z = 0 (a 2D polyline) or in full
   3D.

Editing:
- **In a table** (the points' coordinates).
- **By drag/drop** of the points in the viewport.

(Resolves this section's old open question about the polyline input source.)

**Decided with the user (2026-09-24):** a polyline alignment is started from **Add Alignment**'s
new *Definition* choice. The **2D/3D choice is made while drawing** (a toggle in the draw tool). New
alignments are written as an **IfcPolyline**. Editing an existing one keeps whichever of
IfcPolyline/IfcIndexedPolyCurve it already uses.

**Implemented (2026-09-24).**
- **What loading already did:** a polyline alignment loaded from a file (IfcPolyline or
  IfcIndexedPolyCurve, Curve2D or Curve3D) already loaded and displayed through the generic
  representation loader. Nothing needed changing there. But the PI-method **Draw** was enabled
  for it and would have layered layouts on top of the polyline, so it's now refused ("This is a
  polyline alignment -- use Draw Polyline").
- **The IFC layer (`tool.Alignment`):**
  - `get_polyline_curve` / `is_polyline_alignment`: an Axis polyline item and no layouts.
  - `is_bare_alignment`: no layouts and no geometry yet, so it could still become either kind.
  - `get_polyline_points` returns local IFC coordinates plus the dimension. It reads an
    IfcIndexedPolyCurve's IfcLineIndex segments in order, and refuses one with IfcArcIndex arcs,
    which can't be edited point by point without losing the arcs.
  - `set_polyline_points` creates the curve through ifcopenshell's own
    `_create_polyline_representation`, or updates the existing curve entity in place. It
    removes orphaned points, updates the RepresentationType (Curve2D/Curve3D), and keeps the
    alignment's own placement 2D/3D in step when an edit changes the dimension.
  - `create_polyline_alignment` makes a bare alignment aggregated to the project.
- **Add Alignment → Definition: Layouts (PI method) | Polyline.** Polyline creates a bare
  alignment. Stationing isn't offered for polyline alignments yet (see below).
- **Draw Polyline** (`align.draw_polyline_alignment`): the main button for a polyline alignment,
  and an extra button for a bare one, which can still become either kind.
  - **2D** (default) is the PI-method draw tool's setup: XY plane, Z = 0, written as Curve2D.
  - **3D** is Bonsai's own Draw Polyline Profile setup: no locked plane, so points snap to scene
    geometry, with a Z field and Shift+X/Y/Z plane locks. It's written as Curve3D.
  - **V** toggles between them while drawing. The status bar shows the current mode. Redrawing
    a 3D polyline starts in 3D.
  - It has the same bearing/deflection Angle input and Bearing readout as the PI-method tool.
  - Finishing replaces the alignment's points.
- **Drag/drop** (`align.edit_polyline_points`): a draggable marker at every point. These are the
  same marker Empties as the PI method's, with a new role, VERTEX, so marker dots,
  **Move with Distance/Angle**, and Finish all work on them unchanged. 2D markers are locked in
  Z; 3D ones move freely. Apply (the same Apply button) writes the markers back.
- **Table** (`align.load_polyline_table`): Easting/Northing, plus Elevation for 3D, with
  add/remove point. Adding inserts a point halfway to the next one, or continues the last leg.
  Staged, then Apply/Finish, like the horizontal PI table.

Verified headless:
- The IFC layer on its own: create, update in place (same curve entity, no orphaned points,
  mesh rebuilt), 3D, IfcIndexedPolyCurve kept through an edit, line-index read, arcs refused.
- The whole flow through the real operators: Add Alignment (Polyline) → bare → draw 2D →
  PI-method Draw refused → markers dragged and applied → table insert/remove/apply → redraw in 3D
  (Curve3D, placement 3D) → 3D marker moved in Z and applied → 3D table → Delete Alignment. The
  draw tool's modal can't run headless, so its 2D/3D setup and its finish step were driven
  directly.
- A **file-loaded IfcIndexedPolyCurve** alignment was edited through the table (type kept),
  saved, reloaded with the edit intact, and opened again as markers at the right 3D positions.

**Scope decided by the user (2026-09-24):**
- **Stationing: yes** -- implemented, see below.
- **Key-point referents: no** for polyline alignments. Referents there are left to *manual referent
  definitions* (§10, a new requirement).
- **Converting a polyline alignment to a layout-based one: not now** ("maybe later").
- **Switching an existing polyline between 2D and 3D: no.** 2D/3D is decided when drawing.
- **Profile view for a 3D polyline: yes, static** -- implemented, see below.

**Implemented (2026-09-24): stationing for polyline alignments.**
- **Library (ifcopenshell-python).** `add_stationing_referent` only put a referent *on* the curve
  (IfcLinearPlacement) when the basis curve was an IfcCompositeCurve with segments. For anything
  else it fell back to an IfcLocalPlacement at the origin. It now does the same for an
  IfcPolyline/IfcIndexedPolyCurve basis curve: `get_basis_curve` already returns that curve for a
  polyline alignment. The geometry kernel resolves distance along both, 2D and 3D, including the
  fallback CartesianPosition. For a 3D polyline, distance along is measured along the 3D curve,
  which is IFC's DistanceAlong. New test:
  `test_polyline_alignment_referent_is_placed_on_the_polyline`, covering an IfcPolyline and a 3D
  IfcIndexedPolyCurve, with positions checked. `test/api/alignment` has 147 passing tests.
- **Bonsai.**
  - Add Alignment → Polyline offers Define Start Station / Start Station again. The start referent
    is created before there's a curve, as for layout alignments, and placed on the curve at
    distance along 0 the first time points are written.
  - After *every* point edit (`tool.Alignment._sync_polyline_stationing`, called by
    `set_polyline_points`), each referent's cached fallback position and its Blender object are
    moved to match the new geometry. The curve entity itself is updated in place, so the
    IfcLinearPlacement stays valid.
  - The Stationing panel (start station, station equations) works on polyline alignments unchanged.
- **Verified headless:** a start station of 1+000 set at creation lands on the first point once
  drawn, object included. A station equation at 150 sits exactly on the sloped 3D second leg and
  reads station 2+000. Editing the points moves both referents, their fallback positions and the
  start referent's object.

**Fixed (2026-09-24), per the user: "When the polyline alignment is selected, its points should be
listed along with an edit button. I don't see how you can look at the profile of a 3D polyline."**
The Alignment Segments panel's polyline section now works like the horizontal section:
- **A header** "Polyline (2D/3D): n points, length L" with a pencil **edit** button. It opens the
  point table *in place* (Easting/Northing/Elevation, add/remove point, Apply/Cancel), and it's
  depressed while the table is open, where clicking it closes the table.
- **A read-only point list** when not editing: #, **Station** (station equations included),
  Easting, Northing, and Elevation for 3D.

The profile toggle had been a bare graph icon on a "Profile (static):" row, easy to miss. It's
now a labelled **Show Profile** / **Hide Profile** button, next to VE. A 2D polyline says why it
has none: "2D polyline: no elevations to profile". A polyline drawn without pressing V is 2D. The
point table no longer also appears in the authoring panel, whose table button still opens it here.
Verified by rendering the panel's own `draw()` headless: the list, the editing state, and the 2D
case.

**Implemented (2026-09-24): static profile for a 3D polyline.** The Alignment Segments panel now
summarises a polyline alignment ("Polyline (3D): n points, length L"). For a 3D one it offers
the profile view toggle, which was previously only shown when there were vertical layouts.
`VerticalProfileDecorator._compute_profile` adds the polyline as one profile line, one straight
grade per leg (labelled Start / Point n / End), against distance along the 3D curve. That axis
matches IFC's DistanceAlong, so the stations shown match the stationing referents, and the grades
shown are rise over that distance. At road grades, that's within a fraction of a percent of rise
over plan distance. It's static: none of the vertical editing tools apply without a vertical
layout. A 2D polyline adds nothing to the profile. Verified headless: legs, 3D lengths,
labels, station labels starting at 1+000, and the panel summary for a 2D and a 3D polyline.

### 5.2 Offset curve alignment

**Requirements (per the user, 2026-09-25):**
1. IfcOffsetCurveByDistances is a representation on IfcAlignment.
2. The IfcAlignment has no nested layout structure.
3. It's **3D** when its OffsetValues use a BasisCurve of type IfcGradientCurve.
4. It's **2D** when its OffsetValues use a BasisCurve of type IfcCompositeCurve.
5. It can be offset from a previously defined IfcOffsetCurveByDistances. Its 2D/3D nature then
   depends on the lowest-level basis curve, per 3 and 4.
6. The minimum number of OffsetValues is 1.
7. The IfcPointByDistanceExpression offsets may be limited to OffsetLateral and OffsetVertical in
   this context. **Not confirmed** -- no such rule was found in the IFC 4.3 documentation or schema
   sources reachable here. So, per the user, **OffsetLongitudinal is omitted as an input for now**
   and can be added later if needed. A value already in a file is carried through an edit
   unchanged, rather than dropped.
8. A table is enough for the UI: select the curve, enter distance along / offset lateral / offset
   vertical, and commit the edits.

**From the spec** (IfcOffsetCurveByDistances): a single offset means a constant offset along the
whole basis curve. Where the offsets don't span the basis curve, the lateral and vertical offsets
implicitly continue with the nearest value. OffsetLateral is positive to the left, facing along the
basis curve.

**Implemented (2026-09-25).**
- **The IFC layer (`tool.Alignment`):**
  - `get_offset_curve` / `is_offset_alignment`.
  - `get_offset_dimension`: walks down the chain of offset curves to the lowest-level basis curve.
    An IfcGradientCurve (or an IfcSegmentedReferenceCurve built on one) is 3D; otherwise 2D.
  - `get_offset_basis_candidates`: every layout alignment's horizontal IfcCompositeCurve (2D),
    each of its verticals' IfcGradientCurve (3D, named with `get_vertical_display_name`), and every
    other offset alignment. It leaves out the alignment's own curves and any offset curve built on
    them, so a circular definition can't be chosen. Polyline alignments aren't offered, since IFC
    doesn't allow them as the basis.
  - `get_offset_values`.
  - `set_offset_values`:
    - It creates the IfcOffsetCurveByDistances and its Axis representation (Curve2D/Curve3D,
      with a matching 2D/3D placement), or updates the existing curve entity in place.
    - It drops OffsetVertical for a 2D curve, and requires at least one offset, with strictly
      increasing distances along.
    - It removes orphaned IfcPointByDistanceExpressions and keeps the representation type and
      placement in step when the dimension changes.
  - `create_polyline_alignment` became `create_bare_alignment`, shared by both kinds.
- **Following the reference alignment.** A reference alignment's curve entities are updated in
  place by every rebuild (segments are cleared and re-added to the same IfcCompositeCurve/
  IfcGradientCurve), so an offset curve stays attached through its reference's edits. Its
  *tessellated* mesh doesn't update by itself, though. `refresh_alignment_representation_object`
  now also rebuilds every offset alignment built on the refreshed one, directly or through other
  offset curves (`refresh_dependent_offset_alignments`). This answers the open question of what
  happens when the reference is fully regenerated.
- **UI:**
  - Add Alignment → *Definition* has a third choice, **Offset Curve**. It makes a bare alignment,
    with stationing as for the other kinds.
  - **Edit Offsets** (`align.load_offset_table`) is the offset alignment's main button in the
    authoring panel, and a bare alignment offers "Define Offset Curve".
  - The Alignment Segments panel lists the offsets ("Offset curve (3D): n offset(s)", the curve
    it's offset from, then Distance Along / Lateral / Vertical). Its pencil opens the table in
    place: the **From** curve dropdown, rows (Vertical only for a 3D curve), add/remove, and
    Apply/Cancel.
  - The PI-method Draw refuses an offset alignment.
- **Verified headless**, through the real operators:
  - Add Alignment (Offset Curve) → bare → Edit Offsets. The candidates are the reference's
    horizontal (2D) and vertical (3D).
  - Applied on the vertical, it gives Curve3D with a 3D placement and no layouts, and the mesh
    starts 3.5 left and 0.2 up of the reference.
  - An offset of that offset works, and is 3D. The first offset isn't offered the second as a basis.
  - Switching the first to the horizontal gives Curve2D with a 2D placement and drops the vertical
    offset. The second then counts as 2D too.
  - Out-of-order distances are refused, with nothing changed.
  - Moving the reference 20 north moves both offset alignments' meshes exactly 20 north, and
    their basis curve entity is unchanged.
  - A longitudinal offset in the file survives an edit.
  - Everything survives save and reload.
  - The panel was rendered in both its states.
- **Kernel check:** IfcOpenShell's geometry kernel was confirmed beforehand to tessellate constant,
  varying and offset-of-offset curves in 2D and 3D.

**Fixed (2026-09-25), per the user, after testing:**
- (1) "after defining a standard alignment, I create an offset alignment but three options are
  enabled, draw horizontal alignment, draw polyline and define offset curve. Only the define offset
  curve should be enabled."
- (2) Creating an offset alignment should not be possible without a basis alignment selected, and
  there was "no way to input offset points for the second offset alignment."
- (3) "Creating an offset alignment is not possible if there aren't any previously defined
  alignments, so it should not be an enabled option."

The root cause of (1) and (2): Add Alignment made an *empty* alignment for both Polyline and
Offset Curve, and an empty alignment offered every kind of tool, since nothing recorded which kind
it was meant to be. Now:
- **An offset curve alignment is created complete, never empty.** Choosing Offset Curve in Add
  Alignment shows **Offset From** (the candidate curves) and the first **Offset Lateral** (plus
  **Offset Vertical** when the chosen curve is 3D). OK creates the IfcOffsetCurveByDistances right
  away, and more offsets are added with Edit Offsets. So an offset alignment can't exist without its
  basis, and its only tool is Edit Offsets. Edit Offsets itself now applies only to offset
  alignments, and "Define Offset Curve" on an empty alignment is gone.
- **Offset Curve isn't offered with nothing to offset from.** Add Alignment's *Definition* is now a
  dynamic list, and Offset Curve only appears once `get_offset_basis_candidates` finds a curve --
  the same "hide it until it can work" approach as Viennese Bend (§2).
- **A polyline alignment that isn't drawn yet remembers it's a polyline.** IFC has nothing to hold
  that intent before there's geometry, so Add Alignment sets a Blender object custom property
  (`tool.Alignment.DEFINITION_PROPERTY`), read by `is_polyline_to_draw`. Such an alignment gets only
  Draw Polyline; the PI-method Draw refuses it. An empty alignment from elsewhere (Add Element, or
  with its horizontal layout deleted) can still be drawn either way.
- **The likely cause of (2)'s missing input: a table left open for another alignment.** Every
  table's poll refuses to open while another table is open, so a table left open for the first
  offset alignment blocked editing the second. The selection-change handler now closes a staged
  offset, polyline or horizontal-PI table left open for a different alignment, discarding unapplied
  edits (`_auto_finish_unrelated_tables`) -- the same "moving on" rule as leftover PI markers.

Verified headless:
- A fresh project doesn't offer Offset Curve; it's offered once there's a standard alignment.
- An offset alignment created from the vertical is complete, and its authoring panel offers only
  Edit Offsets. Both Draw tools are refused.
- An offset of it is created in one step. Selecting it closes the first one's leftover table, and
  its offsets can then be edited.
- A new polyline alignment offers Draw Polyline, with its other tools greyed out, and refuses the
  PI-method Draw.
- A standard alignment still gets only the PI tools.

Also in real UI-mode Blender: the Add Alignment dialog opened with Offset Curve selected, and
Draw Polyline and Draw Horizontal started, all with no errors.

**Not done / noted:**
- **Stationing referents** on an offset alignment are still placed at the origin: the library's
  `add_stationing_referent` only places referents on composite and polyline curves.
- **No profile view** for a 3D offset curve.
- ~~**Single precision:** the table values are Blender float properties (single precision, ~7
  significant digits), so 0.2 is written as 0.20000000298.~~ Fixed 2026-09-25, see §12.

## 6. Vertical draw/edit parity with horizontal

**Confirmed future requirement (per the user, 2026-09-16).** Two modes horizontal's draw/edit tools
have that vertical's don't:

1. **Numeric keyboard entry while drawing.** `ALIGN_OT_draw_horizontal_alignment` inherits
   `PolylineOperator`, giving it typed D/A/X/Y entry (§2's `PolylineDecorator`-driven input).
   `ALIGN_OT_draw_vertical_alignment` is a separate, bespoke modal with no `event.ascii` handling at
   all — mouse-click only (plus Backspace/Enter/Esc), no way to type an exact value while placing a
   vertical PI.

   Inputs for a vertical PI, specifically:
   - **Elevation** — always available, every point.
   - **Slope** (grade, i.e. the incoming/outgoing gradient) — always available, every point.
   - **Distance along** — available for interior PIs only. The first point is pinned to the
     horizontal's start station and the last to its end station (already enforced today — see §2's
     "the first PI is anchored to the start station... moving past the last station locks
     distance-along there too"), so distance-along has nothing to type for those two; only interior
     PIs have a free distance-along value worth entering numerically.

   **Implemented (2026-09-24).** Per the user: "Elevation, Slope, Distance along are not mutually
   exclusive. How to deal with that? The tab order is fine." The three describe a point with only
   two degrees of freedom. The resolution follows horizontal's own precedent (typing X/Y
   recalculates D/A and vice versa), made explicit as locks:

   - **A typed value is locked, and any two locks fix the PI.** The third value is derived and
     shown live. Typing a third value unlocks whichever was locked longest ago, so the two most
     recent entries always win. There's no mode to pick and no dead end.
   - **With one lock, the mouse supplies the rest.** A locked Elevation takes its distance from the
     mouse. A locked Distance takes its elevation from the mouse. A locked Slope slides along that
     grade from the previous PI as the mouse moves. With nothing locked, drawing is purely by mouse,
     as before.
   - **Endpoints.** The first PI only offers Elevation: its distance is pinned to the start station
     and there's no previous PI for a slope. Tab stays on Elevation there, and S/D report why. The
     last PI is placed by typing the end distance, or by the mouse's existing snap to the end.
   - **Typed values that can't be placed are refused, not clamped:** a point at or behind the
     previous PI, one past the end of the alignment, or a 0% slope to a different elevation. They
     are reported as a WARNING and also shown in red in the HUD before Enter. Mouse positions are
     still clamped silently, as before.
   - **Keys:**
     - Typing a number starts in the first field.
     - Tab cycles Elevation → Slope (%) → Distance Along. The order was confirmed by the user.
     - E/S/D jump straight to a field, like horizontal's D.
     - Backspace edits the value, and on an empty field unlocks it. It never removes a PI while
       typing.
     - Enter or RMB (or a click, with the mouse filling in anything unlocked) places the PI.
     - Esc clears the typed values. Enter/RMB/Esc with nothing typed still finish or cancel as
       before. These are handled on key *release*, matching the existing finish/cancel handlers,
       so a key's release half can't also end the command.
   - Slope is in percent, matching the Grade % the HUD already showed.

   Implementation: `_resolve_vertical_pi` (`operator.py`) is a pure function covering every lock
   combination, and the operator keeps `_locks`/`_lock_order`/`_active_field`/`_buffer`.
   `VerticalDrawDecorator.input_lines` holds the Elevation/Slope/Distance fields.

   **Fixed (2026-09-24), per the user:** the readout was drawn pinned to the profile view's top-left
   corner, where the profile's own labels covered it. They also asked "why isn't this exactly the
   same as horizontal, just with different labels?" The fields are now drawn beside the cursor,
   always, typing or not, exactly like `PolylineDecorator.draw_input_ui`: same font size, offset
   and line spacing, the add-on's decoration colour, the highlight colour for the field being
   typed, and the error colour for a value that can't be placed. The old separate
   Dist Along/Elevation/Grade readout is gone. The fields are ordered Elevation → Slope →
   Distance Along to match the Tab order. Locked values carry a "(locked)" suffix, the one thing
   horizontal doesn't need.

   Why the operator itself isn't `PolylineOperator`: that operator is built on real-scene 3D
   picking. It uses raycast snapping against scene geometry, stores points in the scene's
   insertion polyline, and does its D/A/X/Y math in world XY. The profile view is a synthetic
   (distance along, exaggerated elevation) space none of that understands, and its keys differ in
   meaning too (A is an angle *lock* there, not a field). So the input logic stays separate, but
   the display and key conventions match.

   Verified in headless Blender by driving the operator's real `_modal` with keyboard events, then
   building the vertical through its real `_finish`. The run covered:
   - the first PI taking only Elevation;
   - E+S (distance derived), S+D (elevation derived), and a third value unlocking the oldest;
   - Backspace-unlock, and Esc clearing the typed values;
   - the three refusal cases;
   - one lock plus the mouse;
   - typing the last PI at the end station.

   The resulting IfcAlignmentVertical segments match the typed PIs exactly, including the typed
   2% grade. Not tried by hand in the real UI, since the mouse and HUD drawing can't be exercised
   headless.

2. **Drag-to-edit a PI in the viewport**, as an alternative to the table (horizontal has this as of
   2026-09-16). Vertical's PI editing is table-only today. `REQUIREMENTS.md` §4's original decision
   not to build this ("no equivalent for vertical PIs, which only have meaning in the profile view's
   synthetic (distance-along, elevation) space") is worth revisiting — the profile view is a real
   `SpaceView3D` in ortho mode with an addressable (distance-along, scaled-elevation) coordinate
   space that `VerticalProfileDecorator` already converts to/from for its own drawing, so a
   draggable marker there isn't actually impossible, just not yet built.

   **Implemented (2026-09-24).** It works like horizontal's drag-then-Apply, with the look copied
   from horizontal:

   - **The drag session.** `ALIGN_OT_drag_vertical_pis` ("Drag PIs in Profile") is a background
     modal that runs while the vertical PI list is loaded. Edit PIs (`align.load_vertical_pis`)
     starts it automatically, just as horizontal's Edit PIs leaves its markers ready to drag, and
     a button in the Vertical PIs box starts it again.
   - **What you see.** `VerticalPIMarkerDecorator` draws a dot for every staged point, with
     `PIMarkerDecorator`'s own colours, sizes and labels ("Start"/"PI n"/"End"; blue endpoints,
     red-orange sharp PIs, green curved ones). The hovered or dragged dot is enlarged with a ring.
     It also draws the staged grade lines dashed, so a drag shows its effect before Apply.
   - **Dragging.** Press on a dot and drag it. An interior PI moves freely but stays strictly
     between its neighbours. Start/End move up and down only, because their distance-along is the
     horizontal's own start/end. Esc/RMB while dragging puts the PI back. Esc over the profile
     view otherwise stops drag mode. Every other event passes through, so pan, zoom and the panel
     still work.
   - **Staging and Apply.** Edits go into `vertical_pi_markers` (the table updates live, and the
     dragged row becomes the active one). The **Start/End elevations are now staged too**:
     `vertical_start_dist_along`/`_elevation` and `vertical_end_dist_along`/`_elevation`, plus a
     `vertical_endpoints_staged` flag. They are populated by Edit PIs and by the draw tool
     (`_sync_vertical_pi_markers`), shown as editable Start/End Elev fields under the table, and
     used by `ALIGN_OT_apply_vertical_pi_curve`. Before this, Apply always re-read the endpoints
     from IFC. As on horizontal, nothing touches IFC until **Apply Vertical Curves**.
   - **Ending.** The session ends by itself when Finish clears the PI list, or when the profile
     view is closed. A newer invoke takes over from an older one (`_generation`) instead of being
     refused, so a session Blender killed without cleanup (e.g. on loading another file) can't
     leave the button stuck.

   Resolved open question: **bespoke, not Empties.** The profile view is a synthetic space drawn
   by a decorator, and real Empties placed at its coordinates would also appear in every other 3D
   view, near the world origin.

   Verified in headless Blender by driving the modal's real `modal()` with mouse events, using a
   stubbed linear view projection (a background session has no real profile region):
   - hover detection, and a press on empty space passing through;
   - dragging PI 1 to a new spot, with the table row updated and made active;
   - dragging past the next PI being held just short of it;
   - Esc restoring the point;
   - Start/End moving only in elevation;
   - wheel events passing through;
   - Apply writing an IfcAlignmentVertical whose segment starts and end match the dragged points
     exactly, dragged Start/End elevations included;
   - Finish ending the session and removing the decorator.

   Edit PIs' automatic start can't be exercised headless: Blender can't invoke any operator without
   a real event in background mode (confirmed with a bare test operator), so the auto-start is
   skipped there. Nothing that needs real on-screen pixels (dot drawing, hit testing) has been
   tried by hand yet.

   **Implemented (2026-09-24), follow-up: heads-up readout and typed values.** Per the user:
   "it needs some heads up display information about station, elevation, slope, distance along so
   you have some clue about what the drag operation is doing."
   - **Readout.** Beside the cursor, drawn exactly like the draw tools' fields (shared
     `_draw_cursor_fields`), it shows **Station** (project stationing notation, station equations
     included), **Elevation**, **Slope In**, **Distance Along**, and **Slope Out**. It covers the
     hovered PI, the one being dragged (updating live), or the selected one. Vertical drawing's
     readout gained the Station line too.
   - **Selecting.** Clicking a dot without moving selects it: it's ringed, and typing applies to
     it. Clicking empty space deselects.
   - **Typing.** It's the same system as vertical drawing, now the shared `_VerticalTypedInput`
     mixin: Tab/E/S/D, locks, "(locked)" marks, and refusals shown in the error colour.
     - An interior PI takes Elevation, Slope In and Distance Along. The distance must stay between
       its neighbours ("past PI n" / "past the End").
     - Start takes Elevation only. End takes Elevation or Slope In, and its distance stays pinned.
       Each endpoint has one lock, since it has one degree of freedom.
     - While dragging, the mouse fills in whatever isn't typed, and release drops the PI.
     - For a selected PI, whatever isn't typed stays where the PI was, the PI previews live, and
       Enter/RMB applies.
   - **Esc** steps back one level at a time: it puts a dragged or typed-into PI back, then
     deselects, then stops drag mode.
   - **Keyboard scope.** Typing is only taken while the mouse is over the profile view (or a drag
     or typing is under way), so S/E/D in the main 3D view keep working while a vertical PI is
     selected.

   Verified headless by driving the real `modal()`, with the same stubbed projection as before:
   - the hover and drag readouts (exact slope values);
   - typed E+S on a selected PI giving the exact distance;
   - a typed distance past the End being refused with the PI unmoved;
   - Esc;
   - End refusing Distance and taking Slope In;
   - typed Elevation while dragging combining with the mouse's distance;
   - S passing through outside the profile view;
   - the final Apply matching IFC.

   The vertical draw tool's typed-input test still passes after the mixin refactor.

**Open questions:**
- ~~For numeric entry: does Tab cycle Elevation → Slope → Distance Along (skipping Distance Along at
  the endpoints), mirroring horizontal's D → A → X → Y cycle?~~ Resolved (2026-09-24): yes, per
  the user -- see item 1 above.
- ~~For drag-to-edit: would it reuse the same `PICurveMarkerProperties`-style Empty-in-a-3D-view
  pattern horizontal uses, translated into the profile view's (distance-along, scaled-elevation)
  plane, or something bespoke to that view?~~ Resolved (2026-09-24): bespoke -- see item 2 above.

## 7. Cant layout: generate, keep in sync, and delete

**Implemented (2026-09-16).** A cant layout can now be generated from a single cant value rather than
authored segment-by-segment: `ALIGN_OT_generate_cant_layout` walks the horizontal layout's real
segments and builds one matching cant segment per horizontal segment (`tool.Alignment.
build_cant_specs_from_horizontal`) — 0 on tangents, the given value on arcs (raised on whichever rail
is outer to the turn, from the arc's own signed radius), ramping between them on a transition curve
whose *type* mirrors the horizontal one it's paired with wherever the IFC schema has a direct match
(`tool.Alignment.CANT_TYPE_FOR_HORIZONTAL_TYPE`: HELMERTCURVE/BLOSSCURVE/COSINECURVE/SINECURVE/
VIENNESEBEND map to themselves; CLOTHOID/CUBIC, which have no cant-side equivalent, fall back to
LINEARTRANSITION). Individual cant segments can then be hand-tuned via the existing Edit Cant
Segments table.

Three things this required beyond the generator itself:

- **Curve-type sync.** Per the user: "When editing horizontal curve types update the cant layout to
  keep them in sync. Example: change BLOSS to COSINE in horizontal makes the same change in cant
  layout." (Superseded 2026-09-25 by `follow_horizontal_with_cant`, see §11.) `tool.Alignment.sync_cant_segment_types()` matches cant segments to horizontal segments
  positionally and retypes any cant segment whose type has drifted from what
  `CANT_TYPE_FOR_HORIZONTAL_TYPE` now expects, leaving its cant values untouched. Called after every
  horizontal rebuild (`_generate_alignment_segments`, shared by Draw/Apply Curve/Apply Horizontal
  Curves, and `ALIGN_OT_apply_h_segments`'s own raw-table rebuild). A no-op if there's no cant yet, or
  if the segment counts have drifted apart (a stale positional correspondence would silently retype
  the wrong segments).
- **VIENNESEBEND enabled for horizontal, but gated on cant existing.** Per the user: "Vienesse bend is
  not an option for horizontal without cant... so after cant is defined, it should be." Added to
  `HorizontalSegmentRow`'s type list (the raw segment table only — the PI-method marker/table workflow
  never exposed VIENNESEBEND to begin with, since it hardcodes the clothoid family); `ALIGN_OT_apply_h_segments`
  now rejects a VIENNESEBEND row up front if the alignment has no real cant segments yet, matching
  `ifcopenshell.api.alignment.create()`'s own documented constraint ("The horizontal segment geometric
  representation will fail if the cant segment is not defined").
- **Deletion, gated by dependency order.** Per the user: "Cannot delete horizontal if there is a
  vertical. Cannot delete vertical if there is cant. Can delete cant, then vertical, then horizontal
  and have the alignment remain. To delete all, delete the alignment." Three new operators
  (`align.remove_cant_layout`, `align.remove_vertical_layout`, `align.remove_horizontal_layout`), each
  gated on the layer above it being gone first (`tool.Alignment.has_real_vertical_segments`/
  `has_real_cant_segments`), verified end-to-end: generate → delete cant → delete vertical → delete
  horizontal → alignment entity still exists, bare → redraw from scratch succeeds.

**Multiple verticals (IFC CT 4.1.4.4.1.2).** Per the user: "it matters which one the cant uses as its
basis" and "not all child alignments will have vertical + cant, there could be some with vertical only
and some with vertical+cant. There will never be a child alignment with just cant." `generate_cant_layout`
takes an explicit `layout_id` (mirroring `ALIGN_OT_load_vertical_pis`'s own pattern) naming which
vertical to pair with; the cant nests onto *that vertical's own owning alignment* (its child, once a
second+ vertical exists — `ifcopenshell.api.alignment.get_alignment(v_layout)`), not always the
top-level one. `remove_vertical_layout` mirrors this: removing the single/first vertical (still on the
top-level alignment) reverts its representation back to horizontal-only; removing one of several
(each on its own independent child, per `add_vertical_layout`'s own docstring) just removes that whole
child alignment outright.

**Not yet built/verified:**
- ~~No UI picker for *which* vertical when generating cant with 2+ verticals~~ **Resolved
  (2026-09-24).** It turned out the per-vertical **Generate Cant** button on each vertical's row
  (Alignment Segments panel) already *is* the picker: it passes that row's `layout_id`. What was
  missing was verification, plus a way to tell the rows apart:
  - **Verified end to end through the real operators,** with two verticals each given its own cant
    (different values). Each cant nests on its own vertical's child alignment. A horizontal
    rebuild re-syncs *both* cants' curve types (`sync_cant_segment_types`). Key points include both
    cants' transitions. Removing one vertical's cant (its row's delete) leaves the other's intact.
  - **The rows couldn't be told apart.** `add_vertical_layout` names every child alignment
    `Child of <alignment>`, and the panel labelled each vertical row by that name, so two verticals
    showed two identical labels. The new `tool.Alignment.get_vertical_display_name` uses a
    user-given name (the layout's own Name, or its child alignment's, but never the generated
    `Child of ...`) when it's unique among the alignment's verticals, otherwise `Vertical n`. That
    matches the profile view's own `V n` fallback, which uses the same order. A lone vertical keeps
    showing its alignment's name. It's used by the panel row and by the dialog below.
  - **The dialog says which vertical it's for.** With 2+ verticals, Generate Cant Layout's dialog
    shows "For vertical: <name>", and it warns "Replaces this vertical's existing cant layout" when
    there is one.
  - **No silent failure without a target.** Called without a `layout_id` while there are several
    verticals (no UI path does this today), it now refuses with a message pointing at the row
    buttons. It used to report the misleading "That vertical layout has no segments yet".
  - Verified headless (`draw()` rendered into a recording layout for the dialog text).
  - **Renaming a vertical (added the same day, per the user: "renaming would be useful").** Click
    a vertical row's name in the Alignment Segments panel (`align.rename_vertical`, pre-filled with
    its current display name). `tool.Alignment.rename_vertical` does the work:
    - It sets the IfcAlignmentVertical's own Name, which is what the profile view labels it by.
      When the vertical sits on its own child alignment, it also sets that child's Name, e.g.
      "Existing Ground". It never renames the top-level alignment, even for a lone vertical.
    - An empty name puts the defaults back: the layout unnamed and the child "Child of
      <alignment>", so it shows as `Vertical n` again.
    - A name another vertical of the same alignment already shows is refused, since they'd be
      indistinguishable again.
    - The panel, the Generate Cant dialog and an open profile view all update.

    Verified headless through the real operator: rename, duplicate refusal (nothing changed),
    clearing back to `Vertical 1`, and a lone vertical renamed and cleared without touching the
    alignment's name.
- **Key-point referents** — see §8, a new confirmed future requirement covering generation, deletion,
  and regeneration together (this note used to be the only mention; superseded by §8, which also
  covers the deletion-on-layout-removal gap `tool.Alignment.remove_horizontal_layout`'s docstring
  already flags as a `TODO`).

## 8. Key-point referents

**Confirmed future requirement (per the user, 2026-09-18) -- implemented 2026-09-24, see below.** `ifcopenshell.api.alignment.
update_key_point_referents` already exists at the IFC-API level (creates an `IfcReferent` at every
segment transition — P.O.B./P.C./P.T./P.C.C./P.R.C./T.S./S.C./etc., per `_get_segment_start_point_
label`, including the PCC/PRC distinction fixed earlier today) but nothing in the Bonsai Alignments
tab UI ever calls it — a real alignment authored or edited through this module today has no
key-point referents at all, only the single stationing referent(s) `update_key_point_referents`
itself explicitly distinguishes from (see that function's own docstring: key-point referents nest
to a separate `IfcRelNests` from both the segment nest and the stationing nest). Three pieces,
wanted together rather than piecemeal:

1. **A command to add them.** A button (Alignments tab, presumably per-layout like the existing
   Generate Cant Layout button, or per-alignment covering horizontal/vertical/cant together — open
   question, see below) that calls `update_key_point_referents` for the relevant layout(s) and, like
   the stationing referent already does, creates a Blender viewport object for each new
   `IfcReferent` (`tool.Alignment.create_object_for_referent`, already generic over any referent,
   not stationing-specific) so they're visible/selectable, not just IFC-side data.
2. **Automatic deletion when an alignment (or one of its layouts) is deleted.** Already flagged as a
   literal `TODO` in `tool.Alignment.remove_horizontal_layout`'s own docstring — extends to
   `remove_vertical_layout`/`remove_cant_layout`/`ALIGN_OT_remove_alignment` too. Should follow the
   same pattern already used for PI marker cleanup and other per-layout teardown in this module:
   find and remove any key-point referents (and their Blender objects) nested under the
   layout/alignment being removed, not leave them orphaned pointing at deleted segments.
3. **Automatic regeneration whenever the alignment's real geometry changes.** Every Apply-style
   rebuild in this module gives every segment a fresh GUID (`clear_layout_segments` + a
   `create_layout_segment` loop — the same "full wipe-out-and-regenerate, not a partial/in-place
   update" limitation §1 and §4 already document) — so any key-point referents generated before that
   rebuild are now referencing segments that no longer exist. Without automatic regeneration, this
   is exactly the same class of staleness bug already found and fixed twice today for other viewport
   state (the alignment object's own origin point, and — investigated but ruled out as already
   correct — the stationing referent): correct immediately after generation, silently wrong after
   the next edit. Regeneration should hook into the same `_generate_alignment_segments` (horizontal)
   and vertical/cant equivalents that already call `sync_stationing_referent_placements`/
   `sync_cant_segment_types` after every rebuild — calling `update_key_point_referents(..., clear=
   True)` there too, but *only* if key-point referents already exist for that layout (i.e. the user
   has opted in via #1) — don't start generating them unconditionally for alignments that never asked
   for them.

**Implemented (2026-09-24).** Decisions, per the user:

- **One button per alignment, not per layout,** which can also regenerate after the fact:
  **Generate Key Points** / **Regenerate Key Points** (`align.generate_key_points`) in the
  Stationing panel (`ALIGN_PT_alignment_stationing_authoring`). A small **X**
  (`align.remove_key_points`) next to it turns them off again.
  `tool.Alignment.generate_key_point_referents` covers the horizontal, every vertical and every
  cant layout, including verticals and cants on child alignments. It puts all of them in *one*
  IfcRelNests on the top-level alignment, via `update_key_point_referents(...,
  rel_nests=nest)`, so every key point is named after the top-level alignment. It replaces any
  existing key points and creates a Blender object for each one (`create_object_for_referent`).
- **No Blender-side flag. "Turned on" is read from IFC.** The user's point: a flag would be
  missing for a file that already contains key points (authored elsewhere, or saved in an earlier
  session), so automatic updates would silently never start for it.
  `tool.Alignment.get_key_point_nests` instead finds any IfcRelNests on the top-level alignment
  (or a child alignment) whose related objects are *all* `POSITION` IfcReferents that position no
  product. That excludes the stationing nest (`STATION` referents), the layout nest, and
  `add_positioning_referent`'s referents, which link through IfcRelPositions rather than a nest.
  Loaded key points are therefore picked up automatically, and the next edit regenerates them
  into the single top-level nest.
- **No label visibility toggle** for now.

Automatic regeneration (`tool.Alignment.update_key_point_referents_if_present`, which does
nothing if the alignment has no key points) is called after every rebuild or stationing change:
- `_generate_alignment_segments`: draw, Apply Curve and Apply Horizontal Curves. It runs after
  `sync_cant_segment_types`, so cant labels see the synced types.
- `_generate_vertical_alignment_segments`.
- `apply_h_segments`, `apply_v_segments` and `apply_cant_segments`.
- `generate_cant_layout`.
- `remove_cant_layout` and `remove_vertical_layout`, which regenerate without the removed layout.
- `set_start_station`, and add, edit and remove station equation. Station values and names change
  even though the geometry doesn't.

It isn't called when a horizontal rebuild *fails*. The segments have just been cleared at that
point, and regenerating would find no geometry and remove the key points, which would silently
turn them off. Instead the old key points stay until the next successful Apply.

Deletion: `remove_horizontal_layout` removes the key points (this was its old `TODO`). Drawing
again doesn't bring them back, because with nothing left to detect they count as turned off.
`ALIGN_OT_remove_alignment` now removes them from IFC explicitly before `root.remove_product`,
which only drops the IfcRelNests and would otherwise leave the referents orphaned in the file.

Verified in headless Blender through the real operators. Each step checked that the IfcRelNests,
the IfcReferents and their Blender objects agree 1:1, with no orphaned POSITION referents left in
the file:
- Generating creates 10 key points (P.O.B./T.S./S.C./C.S./S.T./P.O.E. plus the vertical ones).
- Regenerating is idempotent.
- A radius edit via Apply Curve moves them.
- Setting the start station to 1000 shifts every station by exactly 1000.
- Generating a cant layout adds the cant key points.
- An alignment that never asked for key points never gets any.
- **Save to .ifc → reload in a fresh session:** the key points are detected with no flag, there is
  no false positive on the other alignment, and the next edit regenerates them.
- Removing the cant layout, then the vertical, drops each layout's key points.
- Removing the horizontal removes all of them.
- The X button removes them.
- Deleting an alignment that has key points leaves no referents or objects behind.

Not added: automated tests under `test/bim/` (they need `pytest-bdd`/`pytest-blender`, which
aren't available in this environment).

**Open questions (resolved above, kept for the record):**
- Per-layout (separate buttons/state for horizontal/vertical/cant) or per-alignment (one button,
  regenerates key points for every layout the alignment has)? The existing Generate Cant Layout
  button is per-row/per-layout; stationing referents are alignment-level (there's only ever one
  stationing system). Key-point referents sit in between — each layout has its own independent set
  (a horizontal P.C. and a vertical P.V.C. are different points, possibly at different stations) —
  leaning per-layout to match Generate Cant Layout's existing precedent, but worth confirming.
- How is "the user has opted in" (needed for #3's "only if they already exist" condition) tracked —
  a scene property flag, or simply "look up whether `get_key_point_referents_nest`-equivalent
  already exists and is non-empty for this layout" (no new state, always re-derivable, matching how
  most of this module already avoids storing UI-only flags where IFC data can answer the same
  question)?
- Toggling visibility/display of key-point referent labels in the viewport, similar to
  `show_h_segment_labels` (used by `AlignmentSegmentDecorator`) — worth its own control, or is having
  the referent objects exist in the scene (selectable, visible in the Outliner) enough on its own?

## 9. Appending to an existing alignment

**Confirmed requirement (per the user, 2026-09-24): "adding to the end of an existing
alignment"** -- to be handled *before* partial regeneration (§1/§4). Extend an existing alignment
past its current end without redrawing it from scratch.

**Decided by the user (2026-09-24):** "IfcGradientCurve (vertical) and IfcSegmentedReferenceCurve
(cant) and their semantic counterparts don't have to be as long as the IfcCompositeCurve
(horizontal). I would let all 3 be edited independently. If vertical or cant is shorter or longer
than horizontal, maybe have a quick fix to extend the last (non zero length) segment so the result
matches the horizontal's length."

**Implemented (2026-09-24).**
- **Extend a horizontal** (`align.extend_horizontal_alignment`, a ▶ button next to Draw). This is
  the horizontal draw tool, seeded with the alignment's last leg, so Distance/Angle/bearing/
  deflection are measured from the current end exactly as if drawing had never stopped.
  - Backspace can't remove the existing points.
  - On finish, the new points are appended to the current PIs, which are rebuilt with
    `_reconstruct_horizontal_pis`. Every existing PI keeps its curve (spirals included), and the old
    end becomes a sharp PI, ready for a curve like any drawn PI. PI markers are left for that.
  - The vertical and cant layouts are left alone.
- **Extend a polyline alignment** (`align.extend_polyline_alignment`, ▶ next to Draw Polyline):
  the same thing, adding points after the last one. It stays 2D or 3D.
- **No 2D/3D switching (per the user):** the polyline draw tool's V toggle now only works for an
  alignment with no polyline yet. Redrawing or extending keeps the existing dimension.
- **Extend a vertical** (`align.extend_vertical_alignment`, ▶ on each vertical's row): the profile-
  view draw tool, seeded with that vertical's current PIs, with typed Elevation/Slope/Distance
  included. Existing PIs keep their parabolic curves, and the old end becomes a sharp PI.
  - The profile view's range now always spans at least the horizontal's length
    (`_compute_profile`). It used to span only the verticals' own extent, so a vertical shorter
    than the horizontal couldn't be drawn or extended past its current end.
- **Cant** has no draw tool; it's extended through its segment table, as before.
- **Length mismatch + quick fix.** Each vertical and cant row shows "Ends X past / short of the
  horizontal" whenever it doesn't end where the horizontal does (`tool.Alignment.
  get_length_mismatch`, 1e-6 relative tolerance). Next to it is a **Match** button
  (`align.match_horizontal_length`), which stretches or shortens the layout's *last* real segment
  so it ends exactly at the horizontal's end. Every other segment is rebuilt unchanged, the same
  clear + recreate a segment-table Apply does. Shortening by more than the last segment's length is
  refused, with nothing changed.
- **Found and fixed along the way:** `_reconstruct_vertical_pis` reported a single-grade vertical
  (one CONSTANTGRADIENT) as "no bounding grade". That blocked extending it, and Edit PIs on it,
  the same flaw §4 fixed for a single-LINE horizontal.
- **Implementation note:** the three draw tools' logic now lives in unregistered base classes
  (`_DrawHorizontalAlignment`, `_DrawPolylineAlignment`, `_DrawVerticalAlignment`), with thin
  registered operators on top, the same shape as `PolylineOperator`. The extend tools subclass the
  bases. An earlier version subclassed the registered draw operators directly, and registering
  those subclasses stripped the parents' own `poll` ("type object has no attribute 'poll'"), which
  broke the original draw buttons. The test suite caught it.

Verified headless (the draw tools' modals can't run headless, so their load/seed/finish steps were
driven directly; the quick fix ran through the real operator):
- A horizontal extended by two points keeps its spiral curve at PI 1, has the old end as a sharp
  PI, and ends at the last new point. Backspace is blocked on the seeded points and allowed on a
  new one.
- The unchanged vertical and cant are then reported 900 short. Match fixes each, changing only the
  last segment.
- An over-trim is refused.
- A vertical extended to a new end keeps its 150-long parabolic curve.
- A 3D polyline extended stays 3D with the new point appended.
- All earlier test scripts pass.

## 10. Manual referent definitions

**New requirement (per the user, 2026-09-24): "manual referent definitions" -- details to be
discussed later.** Placing IfcReferents along an alignment by hand, rather than only the generated
stationing referents (§4) and key-point referents (§8). Polyline alignments (§5.1) get no key-point
referents; any referents they need will come from this.

## 11. Partial regeneration (keeping segment GlobalIds)

**Requirement (per the user, 2026-09-25):** "The types of changes we are talking about are changes in
spiral length, circular curve radii, PI location, vertical curve PI and horizontal length for
parabola or circular curve. [...] for cant the cant values could change. If just these parameter are
modified but the overall layout of the segments is the same, the guids should not change, just the
design parameters. The other form of change that is more complex is deleting a PI or a VPI in the
middle of a layout. There needs to be a re-joining but the guids of the remaining segments is
unchanged. There is also mid-layout insertion of a PI/VPI and resulting horizontal curve and
spirals." Also: "if the last segment changes its properties, then the orientation of the zero
length segment probably needs to be updated so that it is tangent-continuous with the end of the
previous segment."

**Implemented (2026-09-25):**

- **Library: `ifcopenshell.api.alignment.update_layout_segments(file, layout, [(existing | None,
  design_parameters), ...])`.** Replaces a layout's real segments with a new sequence, keeping each
  IfcAlignmentSegment the caller maps a new segment onto (new DesignParameters, same GlobalId),
  creating the unmapped ones and removing the unreferenced ones (with referents positioned on them,
  as `clear_layout_segments` does). IfcCurveSegments have no identity, so the layout's curve is
  rebuilt in place on the same curve entity (offset curves and linear placements stay attached);
  per-segment representations are rebuilt if present. The zero-length terminator is kept and moved
  *and turned* to the new end, tangent-continuous with the last segment (tested). The PI-method
  layout functions' design-parameter builders were split out (`_horizontal_design_parameters`,
  `_vertical_design_parameters`) so callers can build parameters without writing segments. Tests:
  `test/api/alignment/test_update_layout_segments.py`.
- **Segment tables (horizontal/vertical/cant):** Apply maps each row to the segment it was loaded
  from (`row.segment_id`); new rows get new segments, removed rows' segments are removed, reordering
  keeps identities. The chained start of each segment is evaluated before anything is written
  (`tool.Alignment.design_parameters_end`).
- **PI method (markers, horizontal PI table, draw/extend, vertical PI list/drag):**
  `_generate_alignment_segments`/`_generate_vertical_alignment_segments` update in place.
  Ownership: each PI owns its back tangent plus its entry spiral / arc / exit spiral; the end owns
  the final tangent (`tool.Alignment.group_segments_by_pi`). PIs correspond one to one when their
  count is unchanged (moves, radii, spiral lengths, curve lengths); when a PI was inserted or
  deleted, unmoved PIs are matched by position (`tool.Alignment.map_segments_by_pi`), so only that
  PI's own segments are created or removed and its neighbours rejoin. Within a PI, segments keep
  identity by role (e.g. dropping the spirals keeps the tangent and arc). Falls back to the old full
  rebuild only when the layout has no segments yet or its PIs can't be reconstructed.
- **Cant: Generate Cant Layout** keeps every cant segment when the segment count is unchanged
  (one cant segment per horizontal segment).
- **Insert/Delete PI UI:** Insert PI / Delete PI on the selected viewport marker (Insert from the
  Start Point or a PI, halfway to the next point; drag it off the line, give it a curve, Apply), and
  Insert Before / Insert After / Delete on the horizontal PI table and the vertical PI list. Like
  dragging, these are staged until Apply.
- **PI marker picking (per the user, 2026-09-25: "selecting a PI in the 3D viewport for editing the
  horizontal alignment, it is difficult to do that with the mouse. Selection is easier for the
  vertical layout PI"):** the marker empties are tiny crosses, so a click near the dot often picked
  whatever mesh was underneath (e.g. terrain) instead -- which also ended the PI edit.
  `ALIGN_OT_pick_pi_marker` (3D View left-click keymap, shift to extend) now selects the marker
  whose dot is within 12 px of the click, like the vertical profile's PIs; any other click passes
  through to Blender's own select. Verified in UI-mode Blender with simulated clicks over a mesh.

**Known, not addressed:** a spiral-less curve next to a spiralled one gives a LINEARTRANSITION cant
segment with equal start/end cant, which `_map_linear_transition` divides by zero on (pre-existing,
same path with or without this change) -- belongs with the degenerate-spiral/C++ item.

**Implemented (2026-09-25): cant follows horizontal edits.** ~~Cant is not regenerated automatically
when the horizontal's segment structure changes.~~ Every horizontal rebuild (the PI method via
`_generate_alignment_segments`, and the horizontal segment table) now pairs each cant layout with
the horizontal before the edit (`tool.Alignment.pair_cant_with_horizontal`) and rebuilds it after
(`tool.Alignment.follow_horizontal_with_cant`, replacing the type-only `sync_cant_segment_types`):
one cant segment per horizontal segment again, with the new lengths and stations (previously a radius
or spiral-length change left the cant lengths stale) and curve families. A horizontal segment the
edit kept keeps its cant segment's GlobalId; a kept arc keeps its own cant values, hand-tuned ones
included, mirrored only if that curve now turns the other way. A new arc (an inserted PI) gets the
layout's design cant -- the largest cant it had anywhere -- and transitions/tangents are worked out
from the arcs as Generate Cant Layout does. A cant layout whose segment count had already drifted
from the horizontal's (hand-edited rows) is left alone, as before. Tested headless: radius change,
PI delete, PI insert, spiral-family change, and a row added in the horizontal segment table.
Not directly tested: the mirroring when a curve's turn direction flips.

## 12. Exact values through the staged tables (float32 precision)

**Fixed (2026-09-25).** Blender FloatProperties hold only a float32, so every staged table rounded
what it loaded (312.4567891 read back as 312.45670166) and Apply wrote that noise back to IFC even
for values nobody touched; at large local coordinates (e.g. 512345.678) float32 is only good to a few
centimetres, so an untouched PI or polyline point could move. Typed values came back noisy too
(0.2 written as 0.20000000298).

Every staged row -- horizontal/vertical/cant segment tables, the horizontal PI table, the vertical
PI list and its start/end, polyline points, offsets -- and every PI marker now carries a hidden
`exact_values` store. Loaders stage through `tool.Alignment.stage_exact(owner, scale, **values)`,
which remembers the unscaled IFC value; appliers read through `tool.Alignment.exact(owner, name,
scale)`, which returns that exact value while the field is unchanged, else the shortest decimal with
the same float32 as what's shown (`snap_float32`), unscaled. PI markers remember the exact local PI
point they were placed at and Apply uses it while the marker hasn't moved
(`remember_marker_point`/`marker_local_point`). Tested headless with ~512 km local coordinates and
7-decimal radii/lengths: untouched tables write back bit-identical design values; PI-method paths
come back within 1e-6 (the PI points are rebuilt by intersecting tangents, double rounding only);
typed 250.2 / 111.3 are written as exactly that.

**Still float32:** a value *typed or dragged* in is limited to float32 resolution -- at 500 km
coordinates, about 3 cm; that would need a string-backed field.

