.. This file was generated with the assistance of an AI coding tool.

Geometry creation
=================

Authoring IFC representation items
----------------------------------

Create IFC geometry using ``create()`` and ``set()``. The example below
builds an IFC4 wall with a rectangular profile extruded one metre. It assumes
``ifcopenshell`` and ``runtime`` from :doc:`hello_world`, with the IFC4 schema
plugin loaded.

.. code-block:: javascript

   const model = new ifcopenshell.File('IFC4');
   const handles = [];
   function create(type, attributes) {
     const entity = model.create(type);
     handles.push(entity);
     for (const [name, value] of Object.entries(attributes)) entity.set(name, value);
     return entity;
   }
   try {
     const origin = create('IfcCartesianPoint', { Coordinates: [0, 0, 0] });
     const axes = create('IfcAxis2Placement3D', { Location: origin });
     const profile = create('IfcRectangleProfileDef', {
       ProfileType: 'AREA', XDim: 1, YDim: 1,
     });
     const direction = create('IfcDirection', { DirectionRatios: [0, 0, 1] });
     const solid = create('IfcExtrudedAreaSolid', {
       SweptArea: profile, Position: axes, ExtrudedDirection: direction, Depth: 1,
     });
     const context = create('IfcGeometricRepresentationContext', {
       ContextType: 'Model', CoordinateSpaceDimension: 3,
       Precision: 1e-5, WorldCoordinateSystem: axes,
     });
     const representation = create('IfcShapeRepresentation', {
       ContextOfItems: context, RepresentationIdentifier: 'Body',
       RepresentationType: 'SweptSolid', Items: [solid],
     });
     const definition = create('IfcProductDefinitionShape', {
       Representations: [representation],
     });
     const placement = create('IfcLocalPlacement', { RelativePlacement: axes });
     const wall = create('IfcWall', {
       GlobalId: '0YvctVUKr0kugbFTf53O9L', Name: 'Box wall',
       ObjectPlacement: placement, Representation: definition,
     });
     console.log(wall.id(), model.toString());
   } finally {
     model.dispose();
   }

The dimensions in this example assume metres. For a complete exchange model,
also author its project, unit assignment, spatial structure, and relationships.
The profile is centred at the origin, and the wall's placement determines where
the extrusion appears. See :doc:`geometry_processing` to triangulate its
representation.

Authoring a triangulated face set
---------------------------------

For IFC4 mesh geometry, coordinates are arrays of XYZ triples and triangle
indices are **one-based**, unlike the zero-based indices returned by geometry
processing. The following creates a single triangular face in an existing
IFC4 ``model``:

.. code-block:: javascript

   const points = model.create('IfcCartesianPointList3D');
   const mesh = model.create('IfcTriangulatedFaceSet');
   {
     points.set('CoordList', [[0, 0, 0], [1, 0, 0], [0, 1, 0]]);
     mesh.set('Coordinates', points);
     mesh.set('Closed', false);
     mesh.set('CoordIndex', [[1, 2, 3]]);
     console.log(mesh.id());
   }

To display it as part of a product, put the face set in an
``IfcShapeRepresentation`` with ``RepresentationType`` set to
``Tessellation``, and attach that representation through an
``IfcProductDefinitionShape`` as above. Schema constraints determine the
attributes and aggregate structure that each representation item accepts.
