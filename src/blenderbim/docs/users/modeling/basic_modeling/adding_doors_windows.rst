Adding Doors and Windows
========================

This section covers how to add and customize doors and windows in your BIM model using the BlenderBIM Add-on.

Adding a Door
-------------

1. Select the wall where you want to place the door.
2. Set the 3D cursor on the wall at the desired door location.
3. Click on the "Create Door" tool in the BlenderBIM toolbar.
4. In the top bar, you'll see "[No IfcDoorType Found] | Name [TYPEX] | + Add IfcDoorType".
5. Edit [TYPEX] to use a door type name of your choice (e.g., DOOR001).
6. Click "+ Add IfcDoorType". The top bar will update with additional options.
7. Click "Add" (or press SHIFT+A) to create a door with its own type.
8. Adjust the door's width and height using the parameters in the top bar.

Adding a Window
---------------

1. Select the wall where you want to place the window.
2. Set the 3D cursor on the wall at the desired window location.
3. Click on the "Create Window" tool in the BlenderBIM toolbar.
4. In the top bar, you'll see "[No IfcWindowType Found] | Name [TYPEX] | + Add IfcWindowType".
5. Edit [TYPEX] to use a window type name of your choice (e.g., WINDOW001).
6. Click "+ Add IfcWindowType". The top bar will update with additional options.
7. Click "Add" (or press SHIFT+A) to create a window with its own type.
8. Adjust the window's width and height using the parameters in the top bar.

Modifying Doors and Windows
---------------------------

.. note::
   Some functionality is not implemented.

You can modify doors and windows using various tools:

- Resize: Adjust the width and height parameters in the top bar.
- Move: Use Blender's standard move tools to reposition the door or window.
- Flip: Change the opening direction using the flip tool (if available).

.. note::
   After moving a door or window, you need to recalculate the void in the wall. To do this:

- Select the wall containing the moved door or window and the door/window.
- Click on the "Apply Void" (:kbd:`Shift` + :kbd:`O`) button in the top bar or use the appropriate shortcut.
- This ensures that the opening in the wall is correctly positioned after moving the door or window.


Door and Window Properties
--------------------------

.. note::
   This functionality is not implemented.

After adding a door or window, you can customize its properties:

1. Select the door or window in the 3D viewport.
2. Go to the ... panel.
3. Find the ... section.
4. Here you can set various properties such as fire rating, u-value, or any custom properties required for your project.

Customizing Door Properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
   This functionality is not implemented.

You can customize various properties of the door:

- Dimensions (width, height, thickness)
- Opening direction 
- Door type (e.g. single swing, double swing, sliding)
- Material

Window Customization
^^^^^^^^^^^^^^^^^^^^

.. note::
   This functionality is not implemented.

Customize window properties such as:

- Dimensions
- Window type (e.g. fixed, casement, sliding)
- Glazing options
- Frame material

Creating Multiple Doors or Windows
----------------------------------

To create multiple doors or windows of the same type:

1. Select the desired door or window type from the dropdown menu in the top bar.
2. Set the 3D cursor on a wall where you want to place the new door or window.
3. Click "Add" (or press SHIFT+A) for each new door or window you want to create.
4. Adjust the position and parameters for each new element as needed.

Calculating Quantities
----------------------

After creating doors and windows, you can calculate quantities:

1. Select the door(s) or window(s) you want to measure.
2. Press Q or click "Calculate All Quantities" in the top bar.

This will update the quantity information for the selected elements.

See Also
--------

- :doc:`creating_walls`
- :doc:`../advanced_modeling/material_assignment`
