# Alignment Authoring — Requirements

Working requirements doc for the Bonsai alignment authoring UI (Alignment BIM tab). 
Captures planned work, not yet implemented unless noted. Update in place as
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
UI-side check. Offer to user that this needs to be handled - offer to explore graceful handling
in the ifcopenshell geometry kernel, if not practical/possible there, then error guard in the UI.

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

   2. **Not yet built.** A point on the shared tangent stated -- in practice, a distance along the
      tangent measured from the first PI -- with *both* curves' radii computed. Simpler than mode 1
      in one respect: the split point directly gives both tangent lengths (T1 = the stated
      distance, T2 = PI-to-PI distance minus T1) rather than deriving one from a radius first, so
      each radius is solved independently from its own already-known tangent length using the same
      `solve_join_next_radius` primitive mode 1 already built -- applied twice, no new math, just a
      different, more direct way of arriving at T1/T2. UI-wise, likely a mode selector once
      `join_next` is checked ("Solve using: Radius of first curve | Distance to reverse point"),
      where distance mode replaces the radius field(s) with a single distance field and computes
      both radii, rather than the user needing to already know either radius. Preferred over asking
      for a literal point (which risks not lying exactly on the shared tangent line and needing
      snapping/validation) -- a distance is unambiguous, and a computed point could still be shown
      as a visual crosshair for feedback.

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

**Confirmed future requirement (per the user, 2026-09-16).** Beyond the PI-based tangent+curve
workflow (§2), support defining an alignment's geometry directly from:

1. **3D polyline.** A sequence of 3D points (X, Y, Z) defines both the horizontal alignment and a
   vertical profile in one pass — each point's elevation implies a vertical PI at the corresponding
   distance-along. Presumably straight-tangent segments only at this stage; curve smoothing would
   still be layered on afterward via the existing PI-curve workflow (§2 steps 6-7).
2. **2D polyline.** The same, but points carry only (X, Y) — horizontal geometry only, with no
   vertical profile implied (vertical would need defining separately, e.g. via the existing
   draw-by-PI tool in the profile view).
3. **Offset curve by distance(s).** Define a new alignment as an offset from an existing reference
   alignment, by a given distance (or distances, if the offset varies along the alignment) — e.g. a
   parallel ramp or lane edge defined relative to a mainline alignment rather than drawn from
   scratch.

**Open questions:**
- Input source for the polyline methods — trace an existing Blender curve/mesh-edge object? Import
  points from a table/file? Draw interactively (reusing the existing click-to-place tool, just
  without forcing tangent-only PI-method smoothing)?
- For the offset-curve method: constant offset only, or does the distance vary by station (a table
  of station/offset pairs, similar to how station equations are entered today)? Which side
  (left/right) convention? Does it need its own live preview/decorator, the way the PI-method draw
  tool has one?
- How does an offset curve interact with vertical — does the new alignment inherit the reference
  alignment's vertical profile (shifted), get its own, or default to flat until vertical is added
  separately?

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

2. **Drag-to-edit a PI in the viewport**, as an alternative to the table (horizontal has this as of
   2026-09-16). Vertical's PI editing is table-only today. `REQUIREMENTS.md` §4's original decision
   not to build this ("no equivalent for vertical PIs, which only have meaning in the profile view's
   synthetic (distance-along, elevation) space") is worth revisiting — the profile view is a real
   `SpaceView3D` in ortho mode with an addressable (distance-along, scaled-elevation) coordinate
   space that `VerticalProfileDecorator` already converts to/from for its own drawing, so a
   draggable marker there isn't actually impossible, just not yet built.

**Open questions:**
- For numeric entry: does Tab cycle Elevation → Slope → Distance Along (skipping Distance Along at
  the endpoints), mirroring horizontal's D → A → X → Y cycle?
- For drag-to-edit: would it reuse the same `PICurveMarkerProperties`-style Empty-in-a-3D-view
  pattern horizontal uses, translated into the profile view's (distance-along, scaled-elevation)
  plane, or something bespoke to that view?

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
  layout." `tool.Alignment.sync_cant_segment_types()` matches cant segments to horizontal segments
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
- No UI picker for *which* vertical when generating cant with 2+ verticals present — the operator
  supports it (`layout_id`), but the per-row Generate Cant button in the segments panel is the only UI
  entry point, and multi-vertical generate/delete was only exercised at the Python/operator level in
  this session, not through the actual panel in a running Blender session.
- **Key-point referents** — see §8, a new confirmed future requirement covering generation, deletion,
  and regeneration together (this note used to be the only mention; superseded by §8, which also
  covers the deletion-on-layout-removal gap `tool.Alignment.remove_horizontal_layout`'s docstring
  already flags as a `TODO`).

## 8. Key-point referents

**Confirmed future requirement (per the user, 2026-09-18).** `ifcopenshell.api.alignment.
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

**Open questions, not yet decided:**
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
