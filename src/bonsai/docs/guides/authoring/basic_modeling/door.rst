Door
====

A door is a wall opening that allows passage between spaces, controlling access for people and goods.

In IFC, it is represented by the ``IfcDoor`` entity, which is a subtype of ``IfcBuildingElement``. A door always requires a host wall and a corresponding ``IfcOpeningElement`` cut into that wall.

.. note::
   This guide applies equally to **Windows** (``IfcWindow``), as they share the exact same opening mechanics.

User Guide – Adding and Modifying Doors
---------------------------------------

This section focuses on *what* you need to do, hiding unnecessary IFC internals.

Adding a Door
~~~~~~~~~~~~~

1. **Select the wall** where you want to place the door.
2. (Optional) Set the 3D cursor on the wall at the desired position.
3. Click the **"Create Door"** tool in the Bonsai toolbar.
4. In the top bar, edit the type name (e.g., change ``[TYPEX]`` to ``DOOR001``) and click **"+ Add IfcDoorType"**.
5. Click **"Add"** (or press :kbd:`Shift+A`) to create the door.
6. Adjust the door's **width** and **height** using the parameters in the top bar.

.. tip::
   If you forgot to select the wall first, the relationship to the wall will be missing.
   In that case, **select both the wall and the door** and click **"Apply Void"** (:kbd:`Shift+O`) to create the opening.

Creating Multiple Doors
~~~~~~~~~~~~~~~~~~~~~~~

Once you have created a door type, you can add multiple doors of the same type:

1. Select the desired door type from the dropdown menu in the top bar.
2. Set the 3D cursor on a wall where you want to place a new door.
3. Select the wall.
4. Click **"Add"** (or press :kbd:`Shift+A`) for each new door you want to create.
5. Adjust the 3D cursor, position, and parameters for each new door as needed.

Modifying a Door – Which Button Do I Press?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Mnemonic:** *Regen = Reposition, Apply Void = Alter shape*

The rule depends on *what* you changed about the door:

.. list-table:: Decision Matrix for Modifying Doors
   :header-rows: 1
   :widths: 25 30 25 20

   * - What you did to the Door
     - What changed in IFC
     - Action to Update the Wall
     - Select this
   * - **Moved** it (translated/rotated)
     - Door's Placement (Matrix)
     - Press **Regen** (:kbd:`Shift+G`)
     - **Door** only
   * - **Flipped** the swing (:kbd:`Shift+F`) or changed "Operation Type"
     - Door's Local Shape / Profile
     - Press **Apply Void** (:kbd:`Shift+O`)
     - **Wall + Door**
   * - **Resized** Width/Height (parametric)
     - Door's Dimensions
     - Usually handled automatically. If the wall cutout looks out of sync, press Apply Void.
     - **Wall + Door** if needed
   * - Changed material or thickness
     - Door's Visual representation
     - No action needed for the wall opening.

.. important::
   - **Regen**, when the **door** is selected (:kbd:`Shift+G`), updates the **opening's placement** to match the door and then refreshes the wall. It does **not** change the opening's shape.
   - **Regen**, when the **wall** is selected, only refreshes the wall's own geometry — it leaves existing opening placements untouched.
   - **Apply Void** (:kbd:`Shift+O`) recreates the opening's **shape** from scratch based on the door's current geometry. It safely removes any existing opening first, so it's safe to use multiple times.
   - If you flip a door and press **Regen**, the opening will be repositioned correctly, but its shape will still reflect the old swing direction. You must use **Apply Void** after flipping.

Step-by-Step: Moving a Door
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Select the door and use Blender's move tools to reposition it. This updates the door's own IFC placement immediately.
2. **With the door still selected**, press :kbd:`Shift+G` (Regen).
3. This copies the door's new placement onto its opening, then regenerates the wall so the hole moves to match.

.. note::
   Selecting the **wall** instead and pressing :kbd:`Shift+G` will **not** move the opening — it only refreshes the wall mesh using the opening's existing (now stale) position. **Always select the door after moving it.**

Step-by-Step: Flipping a Door (Changing Swing)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Select only the door.
2. Press :kbd:`Shift+F` to flip the door by 180°.
3. (Optional) In the **Properties panel** (typically on the right side of Blender), under the **Scene Properties** tab, find the **Geometry and Materials** section. Locate the **"Door"** subsection and change the **"Operation Type"** (e.g., to ``SINGLE_SWING_RIGHT``).
4. **Select both the wall and the door**.
5. Press :kbd:`Shift+O` (Apply Void) to recreate the opening shape to match the new swing.
6. The wall geometry updates with the correct cutout.

Deleting a Door and Removing the Opening
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deleting the door object **does not** automatically delete the hole in the wall — the opening is a separate entity.

**Primary method (recommended):**

1. Delete the door object (e.g., press :kbd:`X`).
2. Select the wall that contained the door.
3. Open the **Voids** panel (in the Geometric Relationships tab).
4. Click **"Remove Opening"** next to the orphaned opening.
5. The wall geometry regenerates automatically without the hole.

**Manual method (fallback – advanced users only):**

If the Voids panel doesn't show the opening (e.g., due to a UI bug), you can clean up manually. This is **hacky** and not recommended for everyday use; it's intended for troubleshooting only.

1. Delete the door object.
2. Enable **"Show Voids"** (in the Create Wall tool, or via the Outliner) to reveal the ``IfcOpeningElement``.
3. Select the ``IfcOpeningElement``.
4. In the Python Console, run:

   .. code:: python

      import ifcopenshell.api
      opening = tool.Ifc.get_entity(bpy.context.active_object)
      ifcopenshell.api.feature.remove_feature(tool.Ifc.get(), feature=opening)

   This removes the void relationship **and** deletes the opening entity in one call — no separate delete step needed.
5. Select the wall and press :kbd:`Shift+G` to regenerate it without the hole.

**Important:** This code bypasses the normal UI safeguards. Only use it if you are comfortable with the IFC data model and understand that incorrectly handling relationships can corrupt your model. Prefer the "Remove Opening" button whenever possible.

Under the Hood – Technical Reference
------------------------------------

This section explains the IFC data model behind these operations for advanced users.

IFC Entities and Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Three distinct concepts are often used loosely — here they are precisely:

- **Filling** (``IfcDoor`` / ``IfcWindow``): the actual door or window object.
- **Opening** (``IfcOpeningElement``): the feature element representing the hole itself. This is a real entity in the model, not just a relationship.
- **Voided Element** (``IfcWall`` / ``IfcSlab``): the building element that gets cut.

"Void" is not a separate movable object — it refers to the relationship between the opening and the element it cuts (``IfcRelVoidsElement``). Likewise "filling" refers to the relationship between the opening and the door/window that occupies it (``IfcRelFillsElement``).

The relationships are directional::

    Filling (Door) ── FillsVoids ──> Opening ── VoidsElements ──> Voided Element (Wall)

What "Regen" (Shift+G) Actually Does
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you select the **door** and press :kbd:`Shift+G`, the ``RecalculateFill`` operator executes:

1. Retrieves the associated ``IfcOpeningElement`` via the ``FillsVoids`` relationship.
2. Copies the door's current ``matrix_world`` (placement) onto the opening.
3. Switches the wall's representation to regenerate its geometry with the new opening position.

**Code Reference**: ``src/bonsai/bonsai/bim/module/model/opening.py`` (``RecalculateFill``, lines ~400–450)

If you select the **wall** and press :kbd:`Shift+G`, ``regenerate_wall_representation`` executes instead. It rebuilds the wall's body geometry from its axis, layers, and connections, but it explicitly **preserves the existing placement of any openings** rather than updating them.

What "Apply Void" (Shift+O) Actually Does
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you select the **wall and door** and press :kbd:`Shift+O`, ``FilledOpeningGenerator.generate()`` executes:

1. **Checks if the filling already has an opening** and removes it first via ``remove_feature()``.
2. Creates a **new** ``IfcOpeningElement`` and places it to match the door.
3. Adds the opening as a feature to the wall (``VoidsElements``).
4. Adds the door as a filling to the opening (``FillsVoids``).
5. Forces the wall to switch to a new representation that includes the newly created void.

**Code Reference**: ``src/bonsai/bonsai/bim/module/model/opening.py`` (``FilledOpeningGenerator.generate``, lines ~47–215)

Why Apply Void is Safe to Use Multiple Times
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The implementation explicitly removes any existing opening before creating a new one:

.. code:: python

   if filling.FillsVoids:
       ifcopenshell.api.feature.remove_feature(
           tool.Ifc.get(), feature=filling.FillsVoids[0].RelatingOpeningElement
       )

The ``remove_feature()`` API properly handles both the void relationship (``IfcRelVoidsElement``) and the filling relationship (``IfcRelFillsElement``) before deleting the opening entity itself. This ensures clean removal without orphaned relationships.

**Best Practice**: Apply Void is safe to use multiple times. However, for simple position changes, use Regen (faster). Use Apply Void when you need to change the opening's shape (e.g., after flipping the door swing).

Removing an Opening Programmatically (Advanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To remove an opening cleanly via the API (the same code used by the "Remove Opening" button):

.. code:: python

   # Find the opening related to your door
   opening = ifcopenshell.util.element.get_filled_void(door)
   if opening:
       # This removes BOTH the void relationship (IfcRelVoidsElement)
       # and the opening entity itself — do not call root.remove_product
       # afterwards, or you'll try to delete an already-deleted entity.
       ifcopenshell.api.feature.remove_feature(file, feature=opening)

.. note::
   If the door/window filling still exists at this point, ``remove_feature`` will also remove its ``IfcRelFillsElement`` relationship, but it does **not** delete the filling object itself — that becomes orphaned and must be removed separately with ``ifcopenshell.api.root.remove_product(file, product=filling)``. You should then delete the orphaned door/window object from Blender as well.

Troubleshooting Common Issues
-----------------------------

- **"I moved the door, pressed Regen, but the hole didn't move!"**
  - Ensure the **door** is selected, not the wall — a wall-level Regen leaves opening placements untouched.
  - Check if the door has a ``FillsVoids`` relationship. If not, use Apply Void first.

- **"Regen isn't updating the swing direction!"**
  - Regen only updates the opening's position, not its shape. Use Apply Void to change the hole's shape after a flip.

- **"The wall geometry looks wrong after Apply Void!"**
  - This is rare, but if it occurs, try selecting the wall and pressing Regen to refresh the wall's representation.

See Also
--------

- :doc:`creating_walls`
- :doc:`../advanced_modeling/material_assignment`
