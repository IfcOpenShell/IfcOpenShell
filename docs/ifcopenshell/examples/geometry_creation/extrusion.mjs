// This file was generated with the assistance of an AI coding tool.
//
// Geometry creation (JavaScript): an extruded rectangular profile.

import * as ifcopenshell from 'ifcopenshell';

const runtime = await ifcopenshell.init();
await runtime.loadPlugin('schema', 'ifc4');

// tag::example
const model = new ifcopenshell.File('IFC4');
try {
  const origin = model.create('IfcCartesianPoint', {
    Coordinates: [0, 0, 0],
  });
  const axes = model.create('IfcAxis2Placement3D', { Location: origin });

  // A 1 by 1 metre rectangle, centred at the origin, extruded 1 metre up.
  const profile = model.create('IfcRectangleProfileDef', {
    ProfileType: 'AREA',
    XDim: 1,
    YDim: 1,
  });
  const up = model.create('IfcDirection', { DirectionRatios: [0, 0, 1] });
  const solid = model.create('IfcExtrudedAreaSolid', {
    SweptArea: profile,
    Position: axes,
    ExtrudedDirection: up,
    Depth: 1,
  });

  // The solid is the Body of the wall, in a 3D model context.
  const context = model.create('IfcGeometricRepresentationContext', {
    ContextType: 'Model',
    CoordinateSpaceDimension: 3,
    Precision: 1e-5,
    WorldCoordinateSystem: axes,
  });
  const body = model.create('IfcShapeRepresentation', {
    ContextOfItems: context,
    RepresentationIdentifier: 'Body',
    RepresentationType: 'SweptSolid',
    Items: [solid],
  });
  const definition = model.create('IfcProductDefinitionShape', {
    Representations: [body],
  });

  const placement = model.create('IfcLocalPlacement', {
    RelativePlacement: axes,
  });
  const wall = model.create('IfcWall', {
    GlobalId: '0YvctVUKr0kugbFTf53O9L',
    Name: 'Box wall',
    ObjectPlacement: placement,
    Representation: definition,
  });
  console.log(wall.id(), wall.Name);
} finally {
  model.dispose();
}
// end::example
