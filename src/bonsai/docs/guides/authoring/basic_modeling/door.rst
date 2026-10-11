Door
====

A door is a wall opening that allows passage between spaces, controlled access for people and goods.

In IFC, it's represented by the IfcDoor entity, which is a subtype of IfcBuildingElement.
Doors play a crucial role in building design, affecting circulation, accessibility, and space functionality.

This section covers how to add and customize doors in your BIM model using Bonsai.

Adding a Door
-------------

1. Select the wall where you want to place the door.
2. Set the 3D cursor on the wall at the desired door location.
3. Click on the "Create Door" tool in the Bonsai toolbar.
4. In the top bar, you'll see "[No IfcDoorType Found] | Name [TYPEX] | + Add IfcDoorType".
5. Edit [TYPEX] to use a door type name of your choice (e.g., DOOR001).
6. Click "+ Add IfcDoorType". The top bar will update with additional options.
7. Click "Add" (or press SHIFT+A) to create a door with its own type.
8. Adjust the door's width and height using the parameters in the top bar.

Placing a Door and Changing its Swing Direction
-----------------------------------------------

1. Select the wall:
   - (Optional) Use the "Create Wall" tool to add a wall in your scene.
   - Select the wall where you want to place the door.

   Selecting the wall is crucial as it ensures that the void relation between the door and the wall is automatically created.

2. Add a Door:
   - Use the "Create Door" tool from the toolbar.
   - Press SHIFT+A or click "Add" to place the door on the selected wall.

**Applying Void**

If you forgot to select the wall before placing the door, you'll need to manually create the void relation:

   - Select both the wall and the door.
   - Click "Apply Void" (Shift+O) button.

.. important::
   If you need to use "Apply Void", do this before making any modifications to the door,
   as there are limitations with this function that may affect door orientation.

   Usually, the Regen function will recalculate all the openings with existing void relationships.

3. Adjust Door Position (if needed):
   - With the door selected, use Blender's move tools to adjust its position along the wall.

4. Regenerate the Wall Geometry:
   - Select the wall.
   - Press Shift+G to regenerate the wall geometry, incorporating the door opening.

   .. note::
      This step ensures the wall geometry is updated to include the door opening.

      Moving the Door using Blender tools doesn't actually change the IFC model.
      Future versions need to improve UX in that regard.
      Synchronisation between the Blender scene and IFC model is an issue that has the highest priority.

5. Change Door Swing Direction:
   - Select only the door and enter door edit mode (the pen icon, or :kbd:`Tab`).
   - Two swing arcs appear in the viewport: the highlighted arc is the current swing,
     the dimmed arc is the alternative on the other side of the wall.
   - Click the highlighted arc to move the hinge to the opposite jamb.
     The door stays on the same face of the wall and keeps its opening direction,
     only the hand mirrors (for example SINGLE_SWING_LEFT becomes SINGLE_SWING_RIGHT).
   - Click the dimmed arc to swing the door from the opposite side of the wall instead.
     :kbd:`Shift` + click mirrors the door geometry without changing the recorded swing.
   - Alternatively, pick any Operation Type directly from the drop-down next to the gizmo.

   .. note::
      External doors (Pset_DoorCommon.IsExternal) ask for confirmation before a flip,
      because a factory-handed door leaf cannot swap its hinge side on site:
      the flipped door is a different product.

      If the door shares its type with other doors, entering edit mode warns you
      that the change applies to every door of that type.

6. Final Wall Geometry Regeneration:
   - Select the wall again.
   - Press Shift+G one more time to ensure all changes are properly applied.

Additional Notes
----------------

- Shift+F (the Flip button in the Door tool interface) moves the door to the other
  face of the wall. To change only the hinge side, use the swing arcs in door edit
  mode as described above.
- Always use Shift+G (Regenerate) after making changes
  to ensure the wall and door geometries are correctly updated.
- Avoid using Shift+O (Apply Void) as it may cause issues
  with the door's orientation.


Modifying Doors
---------------

.. note::
   Some functionality is not implemented.

You can modify doors using various tools:

- Resize: Adjust the width and height parameters in the top bar.
- Move: Use Blender's standard move tools to reposition the door.
- Flip: Move the door to the other face of the wall using the flip tool (Shift+F),
  or change the hinge side with the swing arcs in door edit mode.

.. note::
   After moving a door, you need to recalculate the void in the wall. To do this:

- Select the wall containing the moved door.
- Click on the "Regen" (:kbd:`Shift` + :kbd:`G`) button in the top bar or use the appropriate shortcut.
- This ensures that the opening in the wall is correctly positioned after moving the door.

If Regen operation doesn't achive the required result, use Apply Void function:

- Click on the "Apply Void" (:kbd:`Shift` + :kbd:`O`) button in the top bar or use the appropriate shortcut.
- This ensures that the opening is linked to the wall.


Door Properties
^^^^^^^^^^^^^^^

.. note::
   This functionality is not implemented.

After adding a door, you can customize its properties:

1. Select the door in the 3D viewport.
2. Go to the ... panel.
3. Find the ... section.
4. Here you can set various properties such as fire rating, u-value, or any custom properties required for your project.

.. note::
   This functionality is not implemented.

You can customize various properties of the door:

- Dimensions (width, height, thickness)
- Opening direction 
- Door type (e.g. single swing, double swing, sliding)
- Material


Creating Multiple Doors
-----------------------

To create multiple doors of the same type:

1. Select the desired door type from the dropdown menu in the top bar.
2. Set the 3D cursor on a wall where you want to place a new door.
3. Select the wall
4. Click "Add" (or press SHIFT+A) for each new door you want to create.
5. Adjust the 3D cursor, position and parameters for each new door as needed.

See Also
--------

- :doc:`creating_walls`
- :doc:`../advanced_modeling/material_assignment`
