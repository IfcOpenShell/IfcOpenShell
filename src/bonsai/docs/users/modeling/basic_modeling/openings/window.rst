Window
======

A window is an opening that allows light and air to enter a building, providing ventilation and views to the outside.

In IFC, it's represented by the IfcWindow entity, which is a subtype of IfcBuildingElement.
Windows play a crucial role in building design, affecting natural lighting, ventilation, energy efficiency, and aesthetics.

This section covers how to add and customize windows in your BIM model using Bonsai.

Adding a Window
---------------

1. Select the wall where you want to place the window.
2. Set the 3D cursor on the wall at the desired window location.
3. Click on the "Create Window" tool in the Bonsai toolbar.
4. In the top bar, you'll see "[No IfcWindowType Found] | Name [TYPEX] | + Add IfcWindowType".
5. Edit [TYPEX] to use a window type name of your choice (e.g., WINDOW001).
6. Click "+ Add IfcWindowType". The top bar will update with additional options.
7. Click "Add" (or press SHIFT+A) to create a window with its own type.
8. Adjust the window's width and height using the parameters in the top bar.

Placing a Window and Changing its Configuration
-----------------------------------------------

1. Select the wall:
   - (Optional) Use the "Create Wall" tool to add a wall in your scene.
   - Select the wall where you want to place the window.

   Selecting the wall is crucial as it ensures that the void relation between the window and the wall is automatically created.

2. Add a Window:
   - Use the "Create Window" tool from the toolbar.
   - Press SHIFT+A or click "Add" to place the window on the selected wall.

**Applying Void**

If you forgot to select the wall before placing the window, you'll need to manually create the void relation:

   - Select both the wall and the window.
   - Click "Apply Void" (Shift+O) button.

.. important::
   If you need to use "Apply Void", do this before making any modifications to the window,
   as there are limitations with this function that may affect window orientation.

   Usually, the Regen function will recalculate all the openings with existing void relationships.

3. Adjust Window Position (if needed):
   - With the window selected, use Blender's move tools to adjust its position along the wall.

4. Regenerate the Wall Geometry:
   - Select the wall.
   - Press Shift+G to regenerate the wall geometry, incorporating the window opening.

   .. note::
      This step ensures the wall geometry is updated to include the window opening.

      Moving the Window using Blender tools doesn't actually change the IFC model.
      Future versions need to improve UX in that regard.
      Synchronisation between the Blender scene and IFC model is an issue that has the highest priority.

5. Change Window Configuration:
   - Select only the window.
   - Locate the "Parametric Geometry" panel in the `Scene Properties > Geometry and Materials` subtab.
   - Find the "Window" section within this panel.
   - Change the "Operation Type" to the desired configuration (e.g., "DOUBLE_PANEL").

6. Final Wall Geometry Regeneration:
   - Select the wall again.
   - Press Shift+G one more time to ensure all changes are properly applied.

Modifying Windows
-----------------

.. note::
   Some functionality is not implemented.

You can modify windows using various tools:

- Resize: Adjust the width and height parameters in the top bar.
- Move: Use Blender's standard move tools to reposition the window.
- Flip: Change the opening direction using the flip tool (if available).

.. note::
   After moving a window, you need to recalculate the void in the wall. To do this:

- Select the wall containing the moved window.
- Click on the "Regen" (:kbd:`Shift` + :kbd:`G`) button in the top bar or use the appropriate shortcut.
- This ensures that the opening in the wall is correctly positioned after moving the window.

If Regen operation doesn't achieve the required result, use Apply Void function:

- Click on the "Apply Void" (:kbd:`Shift` + :kbd:`O`) button in the top bar or use the appropriate shortcut.
- This ensures that the opening is linked to the wall.

Window Properties
^^^^^^^^^^^^^^^^^

.. note::
   This functionality is not implemented.

After adding a window, you can customize its properties:

1. Select the window in the 3D viewport.
2. Go to the ... panel.
3. Find the ... section.
4. Here you can set various properties such as thermal transmittance (U-value), solar heat gain coefficient, or any custom properties required for your project.

.. note::
   This functionality is not implemented.

Customize window properties such as:

- Dimensions
- Window type (e.g. fixed, casement, sliding)
- Glazing options
- Frame material

Creating Multiple Windows
-------------------------

To create multiple windows of the same type:

1. Select the desired window type from the dropdown menu in the top bar.
2. Set the 3D cursor on a wall where you want to place the new window.
3. Select the wall
4. Click "Add" (or press SHIFT+A) for each new window you want to create.
5. Adjust the 3D cursor, position and parameters for each new window as needed.

Calculating Quantities
----------------------

After creating windows, you can calculate quantities:

1. Select the window(s) you want to measure.
2. Press Q or click "Calculate All Quantities" in the top bar.

This will update the quantity information for the selected elements.

See Also
--------

- :doc:`../creating_walls`
- :doc:`../../advanced_modeling/material_assignment`
