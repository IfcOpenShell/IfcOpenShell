Material Assignment
===================

This section covers how to assign and customize materials in your BIM model using the Bonsai.

Types of Material Definitions
-----------------------------

In BIM, materials can be defined in several ways:

1. Single Material: The simplest approach, where an object has one material.
2. Material Constituent Set: For objects with multiple materials (e.g., a window with an aluminum frame and glass glazing).
3. Material Layer Set: Used for objects like walls or slabs, defining layers of different materials and thicknesses.
4. Material Profile Set: Typically used for structural elements, defining materials in relation to a specific profile shape.

Basic Material Assignment
-------------------------

To assign a material to an object:

1. Select the object in the 3D viewport.
2. Go to the Material Properties panel.
3. Click "New" to create a new material.
4. Give the material a name.
5. Set the material type (single, constituent set, layer set, or profile set).

Material Categories
-------------------

Materials should be categorized for easy identification and scheduling:

- In IFC4 models, materials are automatically grouped into categories (e.g., concrete, steel, wood).
- For IFC2x3 models, materials may appear uncategorized.

To view all materials in your project:

1. Go to the Materials schedule in the Bonsai panels.
2. You'll see a list of all materials used in the model.

Best Practices for Material Naming
----------------------------------

- Use standardized naming conventions for materials.
- Names should match how materials are tagged in drawings, schedules, and specifications.
- Avoid using color codes as material names.

Material Properties
-------------------

In IFC4 models, materials can have associated properties:

1. Select a material in the Materials panel.
2. Look for the "Common Properties" section.
3. Set relevant properties for the material (e.g., density, thermal properties).

Note: IFC2x3 models have limited support for material properties.

Profiles for Structural Elements
--------------------------------

For structural models, especially steel structures:

1. Use Material Profile Sets for elements like beams and columns.
2. Name profiles according to standardized codes in your region.
3. In IFC4 models, profiles can have associated structural properties.

To view profiles:

1. Look for the Profiles schedule in Bonsai panels.
2. You should see a list of all profiles used in the project.

Color vs. Material
------------------

It's important to distinguish between an object's color and its material:

- Color is a visual property for rendering and display.
- Material defines the physical properties and composition of the object.

Avoid merging these concepts; an object can have a material without a specific color, and vice versa.

Saving and Exporting
--------------------

Remember that Bonsai .ifc files cannot currently save textures from image files. To preserve both BIM data and detailed materials:

1. Save your project as a .blend file to retain all material and texture information for rendering.
2. Also save as an .ifc file to store BIM data.

Always maintain both .blend and .ifc versions of your project to ensure all information is preserved.

IFC Version Considerations
--------------------------

- IFC4 provides better support for material properties, categories, and profiles compared to IFC2x3.
- Consider migrating to IFC4 for more comprehensive material information and structural analysis capabilities.

See Also
--------

- :doc:`../../structural_analysis/index`
- :doc:`../../costing_and_scheduling/index`
