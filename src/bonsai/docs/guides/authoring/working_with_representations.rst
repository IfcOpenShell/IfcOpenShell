Working with Representations
----------------------------

Bonsai provides tools to view, edit, and manage representations of IFC elements directly within Blender's interface.
This section covers how to work with these representations effectively.

Viewing Representations
^^^^^^^^^^^^^^^^^^^^^^^

To view the representations of an IFC element:

1. Select the element in the 3D viewport.
2. Navigate to Scene > Geometry and Materials > Representations in the Properties panel.
3. You'll see a list of all representations associated with the element, including their context and type.

Editing Representations
^^^^^^^^^^^^^^^^^^^^^^^

To edit an existing representation:

1. In the Representations panel, click on the representation you want to edit to make it active.
2. Switch to Edit Mode in the 3D viewport.
3. Make your desired changes to the geometry.
4. Once finished, click "Manually Save Representation" in the Representation Utilities section.

.. note::
   Not all representation types can be directly edited. For example, SweptSolid representations cannot be modified in this way.

Adding Representations
^^^^^^^^^^^^^^^^^^^^^^

To add a new representation to an element:

1. Select the element in the 3D viewport.
2. In the Representations panel, use the dropdown menu at the top to select the desired context (e.g., Model, Plan).
3. Click the "+" button next to the dropdown.
4. In the dialog that appears, choose the method for creating the representation (e.g., Trace Outline, Bounding Box).
5. Follow any additional prompts to complete the creation of the new representation.

Common Representation Types in Bonsai
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Bonsai supports several representation types, each suitable for different purposes:

1. SweptSolid
   - RepresentationIdentifier: 'Body'
   - RepresentationType: 'SweptSolid'
   - Description: Used for 3D shapes created by extruded area solids or revolved area solids.
   - Typical use: Walls, columns, beams with simple profiles.

2. Tessellation
   - RepresentationIdentifier: 'Body'
   - RepresentationType: 'Tessellation'
   - Description: Represents 3D shapes using tessellated surface models.
   - Typical use: Complex geometries, imported meshes.

3. Clipping
   - RepresentationIdentifier: 'Body'
   - RepresentationType: 'Clipping'
   - Description: 3D shapes created using Boolean operations with half-spaces.
   - Typical use: Complex shapes with cutouts or intersections.

4. Curve2D
   - RepresentationIdentifier: 'Axis'
   - RepresentationType: 'Curve2D'
   - Description: 2D curves, often used for wall axes or material layer alignments.
   - Typical use: Defining the centerline of walls.

5. Curve3D
   - RepresentationIdentifier: 'Axis'
   - RepresentationType: 'Curve3D'
   - Description: 3D curves, used for axes of longitudinal elements.
   - Typical use: Defining the profile of walls, openings.


Converting Representations
^^^^^^^^^^^^^^^^^^^^^^^^^^

Bonsai offers tools to convert between different representation types:

1. Select the representation you want to convert.
2. In the Representation Utilities section, you'll find options like:
   - Convert To Tessellation
   - Convert To Rectangle Extrusion
   - Convert To Circle Extrusion
   - Convert To Arbitrary Extrusion

.. warning::
   Converting representations may result in loss of parametric information. Use these tools with caution.

Best Practices
^^^^^^^^^^^^^^

- Always use the appropriate representation type for the element you're modeling.
- Be cautious when editing representations directly, as this may affect the element's relationship with its type or other elements.
- When possible, use parametric definitions (like Material Layers for walls) instead of direct mesh editing.
- Regularly check the IFC validity of your model after making significant changes to representations.

Future Developments
^^^^^^^^^^^^^^^^^^^

The Bonsai team is continually working on improving the representation editing experience. Future updates may include:

- More intuitive interfaces for non-mesh modeling.
- Enhanced tools for working with parametric representations.
- Improved validation and error checking when editing representations.

For the latest updates and feature requests, refer to the Bonsai GitHub repository.
