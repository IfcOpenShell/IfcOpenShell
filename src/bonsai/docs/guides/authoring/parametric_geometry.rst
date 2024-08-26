Parametric Geometry
===================

Bonsai provides tools for creating and editing parametric geometry for IFC elements.
Parametric geometry allows you to define building elements using parameters that can be easily adjusted, rather than modeling fixed geometry.

Key features of the parametric geometry system include:

- Predefined parametric types for common building elements like walls, windows, doors, slabs, etc.
- Custom parametric types that can be created and saved
- Parameters for dimensions, materials, profiles, and other properties
- Automatic updating of geometry when parameters are changed
- IFC-compliant parametric definitions that can be exchanged with other applications

To work with parametric geometry:

1. Select an IFC element in the 3D viewport
2. Open the Geometric Relationships panel in the Scene Properties
3. Expand the Parametric Geometry section
4. Choose a parametric type from the dropdown or create a custom type
5. Adjust the available parameters to define the element's geometry

Parameters may include options like:

- Overall dimensions (width, height, length)
- Material layers and thicknesses  
- Profiles for extrusions
- Opening sizes and positions
- Component offsets and angles

The geometry will update in real-time as parameters are adjusted.
The parametric definition is stored in the IFC data and can be exchanged with other applications that support parametric IFC.

Some elements like windows and doors have additional specialized parametric options in their respective tools.

Parametric geometry allows for efficient modeling and updating of BIM elements while maintaining IFC compatibility.
Experiment with the available options to find parametric workflows that suit your modeling needs.
