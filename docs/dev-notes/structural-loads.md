<!-- This file was generated with the assistance of an AI coding tool. -->

# Structural loads in Bonsai — dev note

> Living design note for the `structural-loads/*` stack of pull requests, based on `v0.9.0`.
> Each pull request in the stack adds its section to this note.

## Goal

Bonsai can author an IFC structural analysis model (`ifcopenshell.api.structural`,
`bim/module/structural`), but applying, editing and seeing loads was hard, several basic
operations failed, and nothing solves the model. This stack makes load authoring work and
read well. A following stage connects a solver (PyNite, below) so that results are written
back into the IFC and shown in the viewport.

The pull requests, in stack order:

1. Fixes to load cases, load groups and activities (this section).
2. Applying and editing loads.
3. Readable point force diagrams.
4. Editing loads from the viewport.
5. An item's applied loads.

## Decisions

- **IFC is the data model.** Nodes, members, loads, load cases and, later, results live in the
  `IfcStructuralAnalysisModel`; the UI and the solver read and write it rather than keeping a
  model of their own.
- **Solver: PyNite (`PyNiteFEA`, MIT)**, for the next stage. A 3D frame and plate solver that
  also handles 2D problems, actively maintained, and mapping directly onto the IFC structural
  schema: point connection → node, curve member → frame member, surface member → plate,
  boundary conditions → supports, actions → loads. Chosen over anaStruct, which is 2D only.
- **Results go to `results.json`, not into the IFC** (after Bruno Postle on #9866). Results are
  generated, orders of magnitude larger than the loads, and replaced on every run, so in a
  Native IFC workflow they do not belong in the design model, and `IfcStructuralResultGroup` is
  not used. Bonsai reads the file, keyed to GlobalIds, as an overlay without modifying the IFC;
  calculation reports take reactions and member forces from it.
- **Analysis through [ifc_structural_mechanics](https://github.com/brunopostle/ifc_structural_mechanics)**
  (GPL-3.0), which already reads the IFC analysis model, runs CalculiX (meshed by Gmsh) and
  writes that `results.json`. PyNite becomes a second backend there rather than a Bonsai-only
  bridge: its layers (`ifc/` → `domain/` → Gmsh → CalculiX → `domain/result` →
  `export/results_exporter`) suggest a PyNite backend takes the `domain` model straight to
  nodes and members, skipping meshing, and hands results back to the same exporter. CalculiX
  stays the default for buildings (plates, buckling); PyNite suits 2D trusses and frames,
  needs nothing beyond Python, and the two cross-check on frames. Test structures come from
  [IfcOpenShell/analysis-models](https://github.com/IfcOpenShell/analysis-models).
- **PyNite runs in a separate process**, started with Blender's own interpreter and a private
  library folder on `PYTHONPATH`, as Bonsai already does for its web UI server
  (`tool/web.py`). PyNite releases since 2.1 declare `numpy>=2.4`, but Blender 5.1 and 5.2
  ship numpy 2.3.4, so installing PyNite into Blender would replace Blender's own numpy.

Feasibility, checked in environments built from Blender 5.1's interpreter without running or
changing Blender: PyNite 3.2.0's own test suite passes on numpy 2.3.4 (136 passed, 1
skipped, as on numpy 2.5; only its VTK display tests were left out), so the numpy pin is not
needed by the solver. A separate-process round trip from Blender's interpreter works in about
1.75 s, mostly imports. Made-up beam and truss models matched hand calculations exactly.
Things the bridge must handle: `import Pynite` imports matplotlib, making the library folder
about 270 MB, so it is probably an opt-in install; `analyze_linear(check_statics=True)` prints
to stdout, so output must be kept apart from results; PyNite reports compression as positive
axial force and a sagging moment as negative; and a node where every member is pinned needs
its rotations restrained, or PyNite reports it unstable.

## 1. Fixes to load cases, load groups and activities

- `structural.remove_structural_load_case` raised a TypeError for any load case without an
  `OwnerHistory`, which includes every one Bonsai authors.
- `IfcStructuralAnalysisModel.LoadedBy`, which lists the load groups and cases a model is
  loaded by, could not be set (also noted in issue #9165). Added
  `structural.assign_structural_load_group` and `unassign_structural_load_group`, and
  toggles in the load case panel. Deleting a load group already unsets an emptied `LoadedBy`
  through `file.remove`, so the removal functions need no change for it.
- There was no way to remove a structural activity. Added
  `structural.remove_structural_activity`, which also removes the
  `IfcRelConnectsStructuralActivity` that `root.remove_product` leaves pointing at nothing,
  and keeps the applied load, which other activities may share.
- `structural.remove_structural_load_group` left the group's own `IfcRelAssignsToGroup` with
  no `RelatingGroup` whenever the group held two or more members. It now removes that
  relationship and the group's activities.
- Show Loads raised an IndexError unless linear force, linear moment and planar force units
  were declared, which no project preset does; it also labelled forces with any force unit in
  the file rather than the assigned one.
- Adding an activity to a load group could not choose a load (changing the load type refreshed
  the list of types, not of loads), and listing a group's activities read
  `AssignedToStructuralItem` as the item instead of the relationship to it.

Library changes come with tests under `test/api/structural`. Bonsai changes were tested by
hand in Blender 5.1.

## 2. Applying and editing loads

Applying one force to one point took about twenty clicks across four panels, and a step left
out, such as assigning the load case or the point to the model, failed silently.

- **Current analysis model.** A model can be made current (radio button in the models list);
  a new model becomes current, and a project's only model is current by default. New
  structural items and load cases are assigned to it. This is separate from the existing
  `active_structural_analysis_model_id`, which means "the model whose attributes are being
  edited". It is a scene property, not saved in the IFC.
- **Activities directly in load cases.** A load case is a load group, so it can hold
  activities itself; the extra load group inside a case is now optional.
- **Apply Load** (`bim.apply_structural_load`; Structural Tool header and Shift+L). One
  dialog applies a force to the selected point connections, curve members or surface members,
  in an existing load case or a new one. Forces are entered as components, or as a magnitude
  with an angle or a slope and a direction (up-right, up-left, down-left, down-right) measured
  from the nearest horizontal, as statics texts give them; the components are shown before
  applying. A project without an analysis model gets one, named after the project. The
  Structural Tool's placeholder Shift+A binding, which hid Blender's Add menu, is removed.
- **Edit Load** (`bim.edit_structural_load_values`). Editing a force opens the same dialog.
  IFC stores only components, so the dialog reopens a force the way it was entered when its
  generated name records it, and otherwise as an angle and slope from the nearest
  horizontal. The name is prefilled and follows the values while it is still a generated
  one. Opened from an applied load, the dialog can move it to another load case; opened from
  the loads list, it moves every use of the load when they share one load case.
- **One edit view per load case.** The pencil shows its attributes (collapsed), a checklist of
  the analysis models it belongs to (a load case may belong to several), its applied loads
  with edit and remove buttons, and its load groups. It replaces three partial views and their
  ghost icons.
- Show Loads lists the load cases of the current model, or every load case when there is no
  model; it previously used the first model in the file.

An operator property's `update` callback receives the operator's properties, not the
operator, so the dialogs' shared input logic is in module-level functions that the callbacks
and the operator methods both call.

## 3. Readable point force diagrams

Show Loads drew each component of the summed force at a point as a fixed-length arrow pointing
at the point, so separate forces and how they combine could not be seen.

- A **Point Forces** setting offers five views. *Components*, *Both* and *Resultant* draw the
  sum of the forces at a point: its components, the components with their resultant, or the
  resultant alone. *Parallelogram* and *Tip-to-Tail* draw each applied force separately and
  build their resultant by the parallelogram law or tip to tail. A single force is shown
  resolved into its components, which are the legs of its parallelogram.
- Forces are drawn from the point outwards to a shared **Force Scale**, a force per unit
  length, or fitted automatically. Arrowheads, shafts and dashes are sized to the longest arrow,
  so the diagram reads the same at any scale. Resultants are white and heavier.
- **Angles** marks each force and resultant lying in the X-Z plane with an arc from a
  horizontal reference axis. By default this is the acute angle from the nearest horizontal,
  as statics texts give it, measured from -X for forces pointing left; *Angle From* can switch
  to counter-clockwise from +X. Reference axes are coloured in bands by the arc that starts in
  each.
- Values are coloured as their arrow, placed beside their line rather than on it (in a
  tip-to-tail chain, at the middle of each arrow outside the force polygon), with settable
  decimals. Forces are chained in the order they were applied.
- Load glyphs no longer write depth, so they do not hide each other or the values, whose
  visibility is tested against depth; later glyphs, such as resultants, draw on top.
- Shown loads redraw after every IFC operation, undo included, when a structural item moves,
  even during a grab, and when a display setting changes, instead of waiting for F5.

Not yet exercised: point loads placed along curve members, which are drawn through the same
code but which nothing creates yet.

## 4. Editing loads from the viewport

- While Show Loads runs, hovering a force arrow that stands for one applied load highlights
  it, and clicking it opens Edit Load for that load. The tail of each arrow is left out, so
  the loaded point can still be selected; arrows that sum several loads are not pickable.
  Light arrows darken when highlighted, others brighten.
- Edit Load **previews** its values in the viewport as they change, until the dialog is
  confirmed or cancelled; `cancel()` restores the saved values, as Bonsai's attribute
  explorer already relies on for dialogs.
- **Edit Resultant** (`bim.edit_structural_resultant`). Clicking a resultant of several
  forces sets a target resultant and solves for the magnitudes of two of the forces, keeping
  their directions; any others are kept, and with three or more forces the two are ticked.
  `tool.Structural.solve_two_force_magnitudes` solves the two-by-two system and returns
  nothing when the two directions are parallel or cannot make the target, as when it is out
  of their plane. The dialog previews the result, warns when a force must reverse (a pull
  becomes a push) or is shared by other applied loads, and reports when there is no
  solution. Only forces in global coordinates are handled.
- Dialogs open at the cursor, so before opening one from a clicked load the cursor is moved
  just clear of the diagram, on the side of the clicked arrow, within the window.

## 5. An item's applied loads

Selecting a structural item gave no way to see what loads it.

- An **Applied Loads** panel, for any structural item, lists its loads by load case, with each
  case's resultant at the item, buttons to edit or remove each load, the current model's load
  cases that do not load it, and Apply Load in its header.
- The structural panels of the Object Information tab (Applied Loads, Structural Connection,
  Structural Member, Structural Boundary Conditions, Connected Structural Members) move out of
  Misc into a **Structural** section above it, shown only for structural items and collapsed
  by default, with Applied Loads open.
- **Load case eyes**, in this panel and on each row of the Structural Load Cases panel, are
  open for the shown load case and closed for the others: a closed eye shows its case, an
  open one stops showing loads. One load case is shown at a time, as in analysis software;
  showing several together is what load combinations are for.

## 6. Entering and displaying loads

- **Directions by eighths.** The Direction input is a pinwheel of eight sections, Q1 to Q8
  counter-clockwise from +X. An angle is measured from the axis its section touches, so it
  runs 0 to 45 degrees, and one typed past that moves to the section it points into. A
  slope's rise is always vertical and its run horizontal, as a roof pitch is, so the two
  sections of a quadrant give a slope the same direction; the pinwheel shows the one it lands
  in. Generated names record the section (`600 lbf at 40 deg Q8`), Edit Load reopens them,
  older up/down-left/right names included, and regenerates them when it opens.
- **Diagrams.** Point forces default to *Parallelogram*. Angles are measured as the inputs
  are, from the axis of each force's section, with the section in the label; *Angle From*
  keeps the nearest horizontal and +X. A **Slopes** toggle draws each force's slope as a rise
  and run triangle beside it. Labels move apart when they would overlap. Forces follow their
  item's visibility, and Apply Load shows the load case it applied to. Forces default to whole
  numbers and angles to a tenth.
- **Tip-to-tail order** is kept per applied load as `BBIM_Structural.DrawOrder`, as IFC leaves
  the loads on an item unordered; move and reverse buttons set it, in the item's Applied
  Loads and in a load case's list, which lists loads by item.
- **A Structural Loads overlay** under Bonsai Decorators, on by default, replaces Show Loads:
  loads show on visible structural items while it is on, including after an IFC loads, and
  clicking one still edits it through an internal operator that runs while they are shown.
- The Structural Loads panel is **Load Definitions**, with an *Unused Only* filter, as
  definitions are what applied loads share. An item's analysis models are set from the item.

## 7. Known and unknown values

Statics problems state which magnitudes and directions are known and which are to be found.

- **Locks.** Apply Load and Edit Load lock an applied load's magnitude and direction as known,
  kept as `BBIM_Structural.MagnitudeLocked` and `DirectionLocked` (unset means known). Edit
  Load opened from a load definition shows them when one applied load uses it, as locks
  belong to applied loads.
- **Edit Resultant** has locks for the resultant too, and finds the two values left unlocked
  with `tool.Structural.solve_unknowns`: two force magnitudes, a force's and the resultant's
  magnitude, a whole force, or just the sum. Finding a direction together with another
  unknown, which can have two answers, is reported as not supported. With too many or too few
  unknowns it names them, `F₁ magnitude, R magnitude`, in the order forces are numbered.
- **A locked resultant is kept.** Edit Resultant stores the resultant's locks and value on
  the structural item, by load case GlobalId, in `BBIM_Structural.Resultants`, as a resultant
  is not an IFC entity. Editing or adding a force there solves the unknowns again to keep it,
  and Edit Load's preview shows them moving.
- Diagram labels of unlocked values carry 🔓.

## 8. Tilted point axes

Statics problems often resolve a force along axes tilted to an incline: parallel and square
to a ceiling or a rafter. A point connection's own axes (`ConditionCoordinateSystem`) can
already express this, but Bonsai's only editor for them turns an empty in 3D by Euler angles.

- **Tilt Axes** on the Structural Connection panel sets them from one angle, x' turning up
  from +X towards +Z, with z' square to it; the panel shows the tilt, or that the axes are
  turned in 3D. `tool.Structural.get_axes_tilt` reads it back.
- Loads draw a point's own axes, x' and z' dashed in the colours of their components, with an
  arc for the tilt from +X. The existing local reference frame then shows components along
  them.
- Section 10 replaces Tilt Axes, and the old 3D editor, with one Edit Axes dialog.

## 9. Calculation reports

- **Export Calculations** writes an analysis model's load cases to a folder as an HTML page,
  with KaTeX bundled so that it reads offline, and a Markdown page for Git forges. For each
  point with forces it gives a diagram, a table of the forces and the steps adding them, as a
  textbook sets them out: components, their sums, the resultant's magnitude and angle.
- **Diagrams are the drawing's own.** Each arrow and line the viewport draws keeps a simple
  primitive beside its shader data, and the report writes those to SVG, so the diagram shows
  what the viewport shows, on white. Forces and components are named as in the steps.
- **Unknowns are found as posed.** Values unlocked and found by Edit Resultant are solved
  first, from the sums along X and Z, then the forces are added as a check; found values are
  in bold. *Detailed Steps* adds the working between steps, in grey.
- **Markdown math** is inline `$\displaystyle …$` paragraphs, as Forgejo centres fenced math
  blocks and reads `$$` lines as text. Symbols take their arrows' colours, left uncoloured
  where the arrow is white, so that they read on dark pages.
- Forces on a point with tilted axes are resolved along x' and z' too.

## 10. Inclines and known components

- **Edit Axes** sets a point's axes as Edit Load sets a force's direction: the same pinwheel,
  x' at an angle or a slope in the X-Z plane, or turned in 3D, with a live preview. A slope
  is kept as `BBIM_Structural.AxesRise` and `AxesRun`, and given back only while it still
  matches the axes. The panel shows the axes in one row, in the terms they were set in
  (`tool.Structural.get_axes_terms`). The direction inputs come from one mixin shared with
  the force dialogs.
- **Along an incline**, the report resolves each force as a textbook does: the smaller angle
  its line makes with the axes, as P sin θ and P cos θ, or the slope's ratios when that angle
  is the slope's own, with signs told in words, up or down the slope, away from or into the
  surface. A second diagram draws each force with its x' and z' components, whatever the
  viewport shows.
- **A slope's triangle.** Forces entered as a slope are resolved by similar triangles, as the
  ratios of the slope's sides. Axes set by a slope show it as a rise and run triangle under
  x', beside the angle, in the viewport and in reports.
- **A push** is drawn arriving at its point rather than leaving it, kept as
  `BBIM_Structural.Push`, as IFC's force vector cannot tell a strut from a cable. Added to
  other forces, it is slid along its line and added as a pull, by transmissibility.
- **A known component.** Apply Load and Edit Load take a force's X or Z component in place of
  its magnitude, as a capacity often is; the magnitude follows from it and the direction, and
  the report finds it from that component. Kept as `BBIM_Structural.KnownComponent`.

## 13. A resultant's angle from any axis

Texts give a resultant's angle from whichever axis suits the problem, often the horizontal
where Bonsai's eighths would measure from the vertical.

- **Edit Resultant** treats an eighth clicked as the axis to measure from, not a new
  direction: the resultant stays where it is, and its angle is re-measured from that eighth's
  axis, turning that eighth's way, up to a full turn (`tool.Structural.get_angle_from_eighth`).
  Typing an angle sets the direction. Apply Load and Edit Load keep their behaviour, where an
  eighth clicked keeps the angle and moves the force; whether they should follow is open.
- **Kept per item and load case** as `BBIM_Structural.ResultantEighths`, apart from
  `Resultants`, which holds only locked resultants. Choosing the resultant's own eighth forgets
  it. The resultant's angle arc and reports measure from it; past 90 degrees the report's angle
  step adds whole quarter turns, then takes the rest from the axis reached.
- **Slope triangles** sit out towards each force's tip, beyond the angle arcs at its tail, and
  on the side away from the axis its angle is measured from while angles are shown, so that
  the angle's label never overlaps them.

## 14. Legible diagrams

- **Global axes.** Each loaded point draws the global X and Z axes, faint and dashed, named +X
  and +Z at their positive ends, so that a diagram reads on its own (Y runs into the view). They
  are part of the drawing data, so the viewport and both report diagrams share them; each way, an
  axis reaches just past what is drawn at the point.
- **Labels keep off lines.** Labels keep off arrows, angle arcs and slope triangles as well as
  each other (`box_crosses_segments`); dashed guides may run under them. A label tries its own
  direction first at each distance, then turns further from it, up to the opposite side, so it
  moves round an arrow beside it rather than across it. The viewport runs this on every redraw,
  so it tests only lines within reach and, after a number of tries, settles for a place clear of
  the other labels only; reports search fully.
- **Larger report diagrams.** Drawn to 600 px rather than 420, with the HTML page widened to
  960 px so that they are not scaled back down; labels keep their size, so they have more room.
- **Slope triangles to one scale.** Every triangle has the same run, the level leg, with its rise
  drawn to scale and capped at 2.5 runs, labelled rise over run as a roof pitch is. A triangle
  keeps off arrows and lines drawn at its point, moving back along its force and then to the
  force's other side to find a clear place. Triangles too flat to read are left out; the angle
  gives the direction.
- **Values at the tips.** In a tip-to-tail chain, values sit at each arrow's tip, leaning outside
  the force polygon, rather than at its middle.
- **Named as in calculations.** The drawing names each label by its symbol (`add_symbols`): a
  force by its number in the tip-to-tail order, a single force's components as its own, several
  forces' as their resultant's. Reports set them with subscripts; the viewport with Unicode ones
  (`get_plain_symbol`), z having none.
- **Viewport labels sized to their diagram**, a share of its longest arrow on screen as in a
  report's diagram, between 8 and 24 px, so that zooming scales them with the arrows.

## 15. Point axes input and editing by click

- **Point Axes.** Apply Load and Edit Load take a direction against a point's tilted axes, x'
  and z', as texts give a force along an incline, when the point's axes are tilted in the X-Z
  plane. Forces are still stored as global components, so solving, reports and Edit Resultant
  are unchanged (`tool.Structural.to_axes`, `from_axes`). The generated name primes the eighth,
  `100 lbf at 30 deg Q6′`, which is how Edit Load reopens against the axes, how diagrams measure
  its angle and slope from them, and how reports describe it; a re-solved load keeps it.
  Switching the toggle keeps the force, measured the other way. A known X or Z component is not
  offered against the axes.
- **Equilibrium.** Forces in equilibrium leave only rounding noise, so no resultant is drawn,
  but an `R = 0` label, which can be clicked like a resultant's value. The Applied Loads panel
  has a pencil beside each case's resultant to open Edit Resultant.
- **Edit by click.** Values, angles, slopes and a point's tilt are clickable as well as arrows,
  opening their dialog with that value ready to type (`activate_init`); the viewport records
  where it drew each label to pick it. Hovered, each part highlights on its own, by colour
  alone, as arrows do. Clicking +X or +Z at a loaded point adds a force there at 45 degrees, the
  average of those beside it, and opens it in Edit Load, which removes it if cancelled.
- **A Blender gotcha fixed on the way.** Edit Load's preview looked up the applied load whose
  locks keep a resultant through an operator method, which update callbacks cannot reach, so
  unknowns only moved on the dialog's first draw. It now works from the properties.

## 16. The +Y axis

- **+Y at loaded points**, beside +X and +Z, as far as the longer of them reaches, and clickable
  to add a load as they are. It is drawn along the view in the drawing data (`along_view`), so
  reports, which look along Y, leave it out.
- **A found resultant in its chosen eighth.** The report's Find line measures a resultant found
  by solving from the eighth chosen for it in Edit Resultant, as the rest of the report does,
  rather than the eighth it falls in.

## 17. Linked magnitudes

- **Magnitude As.** Texts pose some problems with a condition rather than a value, "T₁ = T₂", or
  one force a quarter of another. Edit Load can link a load's magnitude to another point force
  in the chain, times a ratio, stored in BBIM_Structural as `SameMagnitudeAs` (the other load's
  GlobalId) and `MagnitudeRatio` (left out when 1). Links chain: each linked load's magnitude is
  a factor of one its group shares (`tool.Structural.get_magnitude_links`).
- **Solving.** Linked unknown magnitudes count as one unknown: they are solved as one force along
  the sum of their directions, each weighted by its factor, then shared out
  (`solve_linked_unknowns`). A linked magnitude follows a known one in its group. Edit Load's
  preview solves with the link as it stands in the dialog.
- **Reports** state a link first, as texts do, carry the ratio into the sums' terms, and work out
  each linked force from the one found, or from the known one before the sums use it. The forces
  table marks a linked magnitude "magnitude = 0.25 × F₂", so that it does not read as free.

## 18. Padlocks on found values

- **Slopes.** An unknown direction is marked on its slope triangle's rise as well as its angle, so
  that it shows with angles hidden.
- **Resultants.** A resultant of several forces is marked for what Edit Resultant finds of it,
  as the report's table marks it: by how many force values are unknown, two in all, linked
  magnitudes counting once (`tool.Structural.get_resultant_found`, shared by both). A locked
  resultant has none; one summed from known forces is found, so is marked.

## 19. Moments about a point

- **A moment centre per load case.** Show Loads takes moments about the active point connection,
  kept in the load case's BBIM_Structural as `MomentCentre` (its GlobalId), and called A.
- **Counter-clockwise positive**, as the X-Z plane is seen from -Y, as statics texts take it.
  IFC's MomentY, by the right-hand rule about +Y, is the negative of this
  (`tool.Structural.get_moment`).
- **Drawn** for each point force, in its colour, as the right triangle a text draws to find the
  arm: its line of action dashed on to the foot of its moment arm, the arm from A with a square
  corner, labelled `M₁ = … CW, d₁ = …`, r from A to the force's point, and the angle φ between r
  and the line of action; their sum as a curved arrow round A. The viewport's font has no
  turning arrows, so labels say CW and CCW.
- **Forces to scale with the distances.** While moments are taken about a point, point forces are
  drawn to one scale, the largest at 0.4 of the distance to the furthest loaded point, as the
  report draws them, rather than each point's diagram two metres long, which dwarfs a short
  beam. An explicit Force Scale still wins.
- **Reports** add a "Moments about A" section per load case. Its diagram is tagged apart from
  A's own loads, and adds what the viewport shows around it: the members along the points,
  their names, and each force at its point, scaled to the distances. The steps find each arm
  as d = r sin φ, each moment as F·d and again by Varignon's theorem from the force's
  components, then ΣM_A.
- **Report diagrams are cropped** to what is drawn, labels where they were placed. Margins as
  wide as the longest label on every side made a diagram wider than the page, which then scaled
  it, and its labels, down.
- **A Blender gotcha:** shader uniforms take Python floats; single-precision NumPy values, as
  from a mesh's coordinates, raise inside the draw handler and stop the shapes after them.
- **Moments applied as loads are left out** for now: IFC keeps them in the project's torque
  unit, which need not be force times length. Couples come next, with that conversion.

## 20. Editing moments

- **Edit Moment Centre** places A from a loaded point as Edit Load enters a force: Δx and Δz, or
  a distance with a direction as an eighth and an angle or slope, on the same direction inputs
  (`get_direction_input`, `set_in_plane_direction`). A Moment Arm section edits a force's arm d,
  sliding A along it with its foot kept on the line of action, and φ or α, swinging A round the
  force's point with r kept. A moves as values are typed, the moments redrawn; cancelling puts
  it back. The inputs typed in are left as they are while the others follow A, so an angle does
  not jump to the next eighth.
- **Clicked from the drawing:** a force's moment lines and labels are one pickable, picked along
  any of its segments and highlighted whole; each label opens the dialog with its value ready to
  type, as a force's do. The curved arrow at A and its label are another.
- **Applied Loads** lists, for a point that is a moment centre, each load case's ΣM about it
  (`tool.Structural.get_moment_about`), with a pencil to the dialog.
- **The drawing** also shows r's direction from the point, as a force's angle, and its slope
  triangle, as Angles and Slopes are shown, and the triangle's angle α at A, 90 degrees less φ.
  The arm's d sits above its moment. It hides with A, and each force's part with its point.
- **Label Size** in Show Loads scales every label of load diagrams, in the viewport and in
  reports.
- **A Blender gotcha:** an update callback must take exactly two arguments, even with defaults
  for more; otherwise Blender declines to register the property, reported only at startup.

## 21. A resultant moment

- **Edit Resultant Moment**, from the curved arrow at A or Applied Loads, sets ΣM_A and finds the
  one force value unlocked, with the same padlocks as Edit Resultant: a moment is one equation,
  so one value. An unknown magnitude is linear, linked magnitudes following by their ratios; an
  unknown direction has two answers, and the one nearer the force's own is taken
  (`tool.Structural.solve_moment_unknown`). ΣM_A has a padlock too: unlocked, it is found from
  the forces.
- **Kept**, as a locked resultant is: the load case's BBIM_Structural keeps `ResultantMoment`, and
  editing a force or moving A solves the unknown again, in the preview as values are typed and on
  confirming. A kept moment's label at A shows a padlock.
- **Reports** find the unknown after the sum: the moment it must make, then its magnitude from its
  arm, or its direction from where it acts.
- **Components clicked**, their arrows or values, open Edit Load on its Components tab with that
  component ready to type.
- **A force on the boundary of two eighths**, as at 45 degrees, keeps the eighth it was named in
  when its name is generated again.

## Next

Load combinations (a load group of type `LOAD_COMBINATION` holding load cases through
`IfcRelAssignsToGroupByFactor`), then analysis, as in Decisions. Show Loads already reads
the factors, so combinations need a panel to create them, add cases with factors and assign
them to the current model; PyNite takes them as `add_load_combo`. When combinations come, fix
`recursive_subgroups` in `load_decoration_data.py`, which multiplies factors cumulatively
across a group's relationships, so that 1.2 D + 1.6 L would draw the live load at 1.92.

Later, for rigid bodies: **ΣFx, ΣFz and ΣM_A solved together.** Edit Resultant solves the two
force equations for two unknowns, and a resultant moment the moment equation for one. Together
they are the three equations of a rigid body's equilibrium, for three unknowns, as reactions at
supports are found in Chapter 3. Left until the book reaches them.

Later, for load authoring: **directions in the XY and YZ planes.** Angles and slopes are entered
in the X-Z plane only; other planes need components. A Plane choice (XZ, XY, YZ) in the force
dialogs would read the pinwheel, angle and slope against that plane's axes (XY seen from +Z, X
right and Y up; YZ from +X, Y right and Z up), record the plane in generated names as primed
eighths record Point Axes, draw a force's arc and triangle in its plane, and set out its report
steps in it. Forces in different planes at one point make a 3D problem, whose resultant would be
given as components; Edit Resultant would stay with forces sharing a plane.

Revisit with combinations:

- **Applying one load to several load cases at once.** Today a load is applied once per case
  (independent definitions), or shared through the load case panel's + row. A direct way
  would make Apply Load's load case a checklist, one applied load per ticked case sharing one
  definition, with an "Also apply in…" choice in Edit Load. Deferred because most such needs
  are load combinations in disguise.
- **Editing one applied load whose definition is shared** changes every applied load sharing
  it; Edit Load warns "Used by N". Set aside until needed: give the applied load its own copy
  of the definition first, with a "Change all N" option, in Edit Load and Edit Resultant.

### What Bonsai supported before this stack (audit)

| Concept | Status |
|---|---|
| Analysis model (add / edit / assign) | yes |
| Topology: vertex, straight edge, planar face | yes (no curved edges, no faces with holes) |
| Member connections, connection condition and coordinate system, member axis | yes |
| Boundary conditions: node, edge, face | yes (warping: no) |
| Actions: point, linear, planar | yes |
| Loads: single force and displacement, linear and planar force, temperature | yes |
| Load configuration (varying along a member) | display only |
| Load groups and load cases | yes; assigning them to a model (`LoadedBy`) added in section 1 |
| Results and reactions | display only (nothing creates them) |
| Physical ↔ analytical link (`IfcRelAssignsToProduct`) | API only, no UI |
| Varying members, failure and slippage conditions | no |

### Beyond what PyNite solves

PyNite (3.2.0) does linear, tension/compression-only, P-Delta, modal and pushover analysis,
and reports member forces, moments, deflections, reactions and plate stresses. It has no
buckling analysis, response spectrum or time history, member stresses, or design checks. It
gives the forces; most gaps are what those forces mean for a member, which are short,
well-known formulas:

| Topic | Gap | Approach |
|---|---|---|
| Stress, strain, thermal | Member stresses; temperature loads | σ = P/A on PyNite's axial forces. PyNite has no temperature load but IFC does (`IfcStructuralLoadTemperature`): convert to equivalent forces (αΔT·E·A at a restrained member) before solving. |
| Section properties | A, I, c, S, r | Closed-form formulas for IFC's parametric profiles (rectangle, circle, I, channel, tube, angle); the `sectionproperties` library only for arbitrary profiles. |
| Shear and moment | — | PyNite covers it; the work is drawing diagrams in the viewport. |
| Bending and shear stress, deflection | σ = Mc/I, τ = VQ/Ib; capacity checks | Formulas on PyNite's moments and shears with the section properties; deflection from PyNite; LRFD combinations in PyNite, capacity checks ours. |
| Columns | Buckling load | Euler P_cr = π²EI/(KL)² with K from the member's IFC end conditions; AISC column curve and NDS column factor. P-Delta covers second-order frame effects. |
| Connections | Bolts, welds | Hand calculation; perhaps a small calculator much later. |

- **Hand methods** (joints, sections, moment distribution, slope-deflection, virtual work) are
  done by hand and checked against PyNite's member forces. For the method of joints, the
  member forces at a joint drawn tip to tail close the force polygon: the method drawn.
- **Where code lives:** pure calculations in a small Blender-free module (perhaps
  `ifcopenshell.util`), fast to test, with UI in Bonsai. Ask in #9866 whether maintainers want
  design formulas in ifcopenshell before writing them.
- **Design codes stay narrow:** clauses taught in introductory texts, labelled as simplified;
  `structuralcodes` is the option to evaluate if full code checking is ever wanted.
- **Checking:** calculations are checked against worked examples with published answers;
  committed tests use made-up structures only, as worked problems are copyrighted.

### Reports, later

- Reactions and member forces come from `results.json` once analysis runs; shear and moment
  diagrams and stresses after. `handcalcs` (Apache-2.0) is the reference for layout.
- Once the content settles, a *Calculations* document type in Drawings and Documents, as
  Schedules are: an `IfcDocumentInformation` associated with its analysis model, listed,
  rebuilt and placeable on sheets. The Structural tab's button stays as a shortcut.
- Each calculation gets a stable identity (model, load case and item GlobalIds), so that
  review markup can anchor to it and survive a rebuild.
- **LaTeX in diagram labels.** Diagrams are SVGs shown as images, which can run no script and
  load no outside file, so KaTeX cannot render inside them; KaTeX HTML in a `<foreignObject>`
  would need Node at export and embedded fonts, and Inkscape does not draw it. Labels are plain
  text with `<tspan>` subscripts, enough for symbols, values and units. If labels need
  fractions or roots, render them as SVG paths with matplotlib's mathtext, which comes with
  PyNite's library folder.

A gotcha met along the way: an operator property's `update` callback receives the operator's
*properties*, not the operator, so it cannot call the operator's methods.

Known gaps:

- Removing an activity keeps its load, as loads can be shared, so loads made by Apply Load can
  accumulate unused.
- Bonsai's attribute fields are 32-bit floats.
- IFC requires every `IfcStructuralConnection` to connect at least one member, so a force on a
  lone point is not valid IFC until members are attached.
