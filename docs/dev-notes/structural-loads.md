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
  boundary conditions → supports, actions → loads, results → `IfcStructuralResultGroup`.
  Chosen over anaStruct, which is 2D only.
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
