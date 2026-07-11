Door  
====  
  
A door is a wall opening that allows passage between spaces.  
  
In IFC, it's represented by the ``IfcDoor`` entity. A door always requires a host wall and a corresponding ``IfcOpeningElement`` cut into that wall.  
  
.. note::  
   This guide applies equally to **Windows** (``IfcWindow``).  
  
Adding a Door  
-------------  
  
1. **Select the wall** where you want to place the door.  
2. (Optional) Set the 3D cursor on the wall at the desired position.  
3. Click the **"Create Door"** tool in the Bonsai toolbar.  
4. In the top bar, edit the type name and click **"+ Add IfcDoorType"**.  
5. Click **"Add"** (or press :kbd:`Shift+A`) to create the door.  
6. Adjust the door's **width** and **height** using the parameters in the top bar.  
  
.. tip::  
   If you forgot to select the wall first, **select both the wall and the door** and click **"Apply Void"** (:kbd:`Shift+O`) to create the opening.  
  
Modifying a Door – Quick Reference  
----------------------------------  
  
.. list-table:: When to Press Which Button  
   :header-rows: 1  
   :widths: 30 30 30  
  
   * - What you changed  
     - Press this  
     - Select this  
   * - **Moved** the door (position/rotation)  
     - **Regen** (:kbd:`Shift+G`)  
     - **Door** only  
   * - **Flipped** swing or changed "Operation Type"  
     - **Apply Void** (:kbd:`Shift+O`)  
     - **Wall + Door**  
   * - **Resized** width/height  
     - Usually automatic. If wall cutout looks wrong, press Apply Void.  
     - (Wall + Door if needed)  
  
Step-by-Step: Moving a Door  
~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
1. Select the door and use Blender's move tools to reposition it.  
2. **With the door still selected**, press :kbd:`Shift+G` (Regen).  
3. The wall opening moves to match the door's new position.  
  
.. note::  
   Always select the **door** (not the wall) after moving it. Selecting the wall won't move the opening.  
  
Step-by-Step: Flipping a Door  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
1. Select only the door.  
2. Press :kbd:`Shift+F` to flip the door by 180°.  
3. (Optional) Go to ``Scene Properties > Geometry and Materials`` and change the **"Operation Type"**.  
4. **Select both the wall and the door**.  
5. Press :kbd:`Shift+O` (Apply Void) to recreate the opening shape.  
6. The wall geometry updates with the correct cutout.  
  
Deleting a Door and Removing the Opening  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
Deleting the door object **does not** automatically delete the hole in the wall.  
  
**Recommended method:**  
  
1. Delete the door object (e.g., press :kbd:`X`).  
2. Select the wall that contained the door.  
3. Open the **Voids** panel (in the Geometric Relationships tab).  
4. Click **"Remove Opening"** next to the orphaned opening.  
5. The wall geometry regenerates automatically without the hole.  
  
.. note::  
   If the opening element was manually deleted (so the fill relationship is gone), use **Apply Void** on the wall and door to recreate it.

.. _door_technical_reference:  
  
Technical Reference – Door Openings  
------------------------------------  
  
This section explains the IFC data model and implementation details for advanced users and developers.  
  
IFC Entities and Relationships  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
Three distinct concepts:  
  
- **Filling** (``IfcDoor`` / ``IfcWindow``): the actual door or window object.  
- **Opening** (``IfcOpeningElement``): the feature element representing the hole itself.  
- **Voided Element** (``IfcWall`` / ``IfcSlab``): the building element that gets cut.  
  
Relationships are directional::  
  
    Filling (Door) ── FillsVoids ──> Opening ── VoidsElements ──> Voided Element (Wall)  
  
What "Regen" (Shift+G) Actually Does  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
**When the door is selected:**  
  
The ``RecalculateFill`` operator executes:  
  
1. Retrieves the associated ``IfcOpeningElement`` via the ``FillsVoids`` relationship.  
2. Copies the door's current ``matrix_world`` (placement) onto the opening.  
3. Switches the wall's representation to regenerate its geometry with the new opening position.  
  
This works unconditionally regardless of the door's dirty state.  
  
**When the wall is selected:**  
  
``regenerate_wall_representation`` rebuilds the wall's body geometry from its axis, layers, and connections, but preserves existing opening placements unless the filling is in a moved state.  
  
What "Apply Void" (Shift+O) Actually Does  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
The ``FilledOpeningGenerator.generate()`` method:  
  
1. **Checks if the filling already has an opening** and removes it first via ``remove_feature()``.  
2. Creates a **new** ``IfcOpeningElement`` and places it to match the door.  
3. Adds the opening as a feature to the wall (``VoidsElements``).  
4. Adds the door as a filling to the opening (``FillsVoids``).  
5. Forces the wall to switch to a new representation that includes the newly created void.  
  
**Why Apply Void is safe to use multiple times:**  
  
The implementation explicitly removes any existing opening before creating a new one. The ``remove_feature()`` API properly handles both the void relationship (``IfcRelVoidsElement``) and the filling relationship (``IfcRelFillsElement``) before deleting the opening entity itself.  
  
Removing an Opening Programmatically  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
  
.. code:: python  
  
   # Find the opening related to your door  
   opening = ifcopenshell.util.element.get_filled_void(door)  
   if opening:  
       # This removes BOTH the void relationship (IfcRelVoidsElement)  
       # and the opening entity itself  
       ifcopenshell.api.feature.remove_feature(file, feature=opening)  
  
.. note::  
   If the door/window filling still exists, ``remove_feature`` will also remove its ``IfcRelFillsElement`` relationship, but does **not** delete the filling object itself — that becomes orphaned and must be removed separately.
