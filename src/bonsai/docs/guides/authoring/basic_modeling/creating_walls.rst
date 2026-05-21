Creating Walls
--------------

Walls are fundamental elements in any building design. Bonsai provides powerful tools for creating and manipulating wall elements.
This section will guide you through the process of creating standalone walls, multiple connected walls, and joining walls using various techniques.

By following these steps and utilizing the various tools provided by Bonsai,
you can efficiently create, modify, and join walls to form complex building layouts.
Remember to use snapping and alignment tools to ensure precision in your model.

Creating a Standalone Wall
^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Open an empty model (without predefined types).
2. Click on the wall icon in the toolbar. The top bar will display "[No IfcWallType Found] | Name [TYPEX] | + Add IfcWallType".
3. Edit [TYPEX] to use a wall type name of your choice (e.g., WALL100).
4. Click "+ Add IfcWallType". The top bar will change, providing you with additional options.
5. Click "Add" (or press SHIFT+A) to create a wall with its own type.
6. You can adjust the wall's length and height using the parameters in the top bar.

Creating Multiple Connected Walls
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Activate the wall tool from the toolbar or use the shortcut (SHIFT + SPACEBAR, 6).
2. Select the wall type from the dropdown menu, or create a new wall type if needed.
3. Set the 3D cursor to the desired starting location for the wall by holding SHIFT and left-clicking in the 3D viewport.
4. Add the first wall segment by pressing SHIFT + A.
5. Adjust the length of the wall segment by dragging the "Length" parameter or entering a numeric value.
6. Set the 3D cursor to the location for the next wall segment. Enable snapping to ensure precise connections between segments.
7. Add the next wall segment by pressing SHIFT + A again.
8. If needed, rotate the new wall segment by pressing SHIFT + R and adjusting the angle.
9. Adjust the length of the new segment as required.
10. Repeat steps 6-9 to create additional wall segments, setting the 3D cursor to the desired locations, until you've completed the wall layout.

Modifying and Joining Walls
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Bonsai offers various tools for modifying and joining wall segments:

- **Extend (SHIFT + E)**: Extend an existing wall to intersect with another face.
- **Butt (SHIFT + T)**: Join wall segments end-to-end.
- **Mitre (SHIFT + Y)**: Create a mitre joint between two wall segments.
- **Merge (SHIFT + M)**: Combine two wall segments into a single wall.
- **Flip (SHIFT + F)**: Reverse the direction of a wall segment.
- **Split (SHIFT + K)**: Divide a wall segment into two parts.
- **Rotate 90° (SHIFT + R)**: Rotate the wall by 90 degrees.

To use these tools:

1. Select the wall segment(s) you want to modify.
2. Use the appropriate shortcut or select the tool from the top bar.
3. Follow the on-screen prompts or adjust parameters as needed.

Interactive Parametric Editing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selected walls expose an in-viewport parametric edit mode that mirrors the door /
window / stair pen-icon UI:

1. Select a single wall. A pen (Edit Wall) icon appears next to the wall in the
   3D viewport, and a matching ``Edit Wall`` button is available in the
   ``Parametric Geometry`` tab of the N panel.
2. Click the pen icon (or the panel button) to enter edit mode. Dimension
   gizmos for length, height, slope (x-angle) and the layer offset baseline
   appear around the wall.
3. Drag any handle to update the value. Dragging only modifies the in-progress
   draft — the IFC file is not touched until you commit, so dragging a length
   handle through many intermediate values produces zero extra IFC entities.
4. Click the green ✓ icon to commit; click the red ✗ to discard. Pressing the
   ✓ icon on a wall that hasn't been dragged is a true byte-identical no-op —
   the IFC file is unchanged.

While editing, additional gizmos surface based on context:

- **Cycle Baseline**: cycles the layer offset baseline (Exterior → Centreline →
  Interior). Shift+click cycles in reverse.
- **3D-cursor scissors**: appears when the 3D cursor sits on the wall axis;
  clicking splits the wall at the cursor's projected X.
- **3D-cursor extend (horizontal)**: appears when the 3D cursor sits beyond the
  wall axis; clicking extends the wall to the cursor's projected X.
- **3D-cursor extend (vertical)**: appears when the 3D cursor sits above /
  below the wall; clicking extends the wall's height to the cursor's Z.
- **Rotate 90°**: rotates the wall around its Z axis.
- **Show / hide openings**: toggles opening fill visibility (doors and windows).

When two walls are selected, the gizmo switches to a state-aware icon at their
common point:

- Already joined → an Unjoin icon at the shared corner.
- Collinear (same axis line) → a Merge icon at the boundary midpoint.
- Joinable corner → a Join icon at the floor + an Extend-To-Wall icon at the
  active wall's top.

When a wall and a slab (LAYER3 element) are selected, an Extend-Vertically icon
appears at the wall's origin / slab elevation; clicking dispatches
``bim.extend_walls_to_underside``.

When a wall and a non-wall, non-slab object are selected, an Add-Opening icon
appears above the wall at the other object's projected X.

Auto-commit on save
~~~~~~~~~~~~~~~~~~~

Pressing Ctrl+S (or running ``bim.save_project``) while any wall is mid-edit
flushes every pending parametric draft first — the same Apply-Wall-Edits the ✓
icon performs, scoped per wall. The IFC saved on disk reflects the values the
user dragged, not the snapshot taken when edit mode was entered. Each commit
produces its own undo entry, so Ctrl+Z walks back through commits individually.

Aligning Walls
^^^^^^^^^^^^^^

You can align walls using the following options:

- **Align Exterior (SHIFT + X)**: Align the wall to its exterior face.
- **Align Centerline (SHIFT + C)**: Align the wall to its centerline.
- **Align Interior (SHIFT + V)**: Align the wall to its interior face.

Adding Openings
^^^^^^^^^^^^^^^

To add openings (e.g., for doors or windows) to your walls:

1. Select the wall where you want to add an opening.
2. Click "Add Void" in the top bar or press SHIFT + O.
3. Adjust the opening's size and position as needed.

Calculating Quantities
^^^^^^^^^^^^^^^^^^^^^^

After creating your walls, you can calculate quantities to ensure accurate measurements:

1. Select the wall(s) you want to measure.
2. Press Q or click "Calculate All Quantities" in the top bar.

