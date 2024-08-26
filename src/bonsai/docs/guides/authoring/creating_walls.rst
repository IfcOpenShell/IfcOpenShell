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

