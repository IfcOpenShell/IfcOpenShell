/********************************************************************************
*                                                                              *
* This file is part of IfcOpenShell.                                           *
*                                                                              *
* IfcOpenShell is free software: you can redistribute it and/or modify         *
* it under the terms of the Lesser GNU General Public License as published by  *
* the Free Software Foundation, either version 3.0 of the License, or          *
* (at your option) any later version.                                          *
*                                                                              *
* IfcOpenShell is distributed in the hope that it will be useful,              *
* but WITHOUT ANY WARRANTY; without even the implied warranty of               *
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
* Lesser GNU General Public License for more details.                          *
*                                                                              *
* You should have received a copy of the Lesser GNU General Public License     *
* along with this program. If not, see <http://www.gnu.org/licenses/>.         *
*                                                                              *
********************************************************************************/

/********************************************************************************
 *                                                                              *
 * This file registers function prototypes for all supported IFC geometrical    *
 * entities.																	*
 *                                                                              *
 ********************************************************************************/

// @todo bring back return value for reduced casting, casting of vector is expensive?

BIND(IfcProduct);

BIND(IfcShellBasedSurfaceModel); // -> collection
BIND(IfcFaceBasedSurfaceModel); // -> collection
BIND(IfcRepresentation); // -> collection
BIND(IfcMappedItem); // -> collection
// IfcFacetedBrep included
// IfcAdvancedBrep included
// IfcFacetedBrepWithVoids included
// IfcAdvancedBrepWithVoids included
BIND(IfcManifoldSolidBrep); // -> shell
BIND(IfcGeometricSet); // -> collection

#ifdef SCHEMA_HAS_IfcCylindricalSurface
// BIND(IfcCylindricalSurface);
#endif
#ifdef SCHEMA_HAS_IfcAdvancedBrep
// BIND(IfcAdvancedBrep);
#endif
// FIXME: Surfaces should have a shape type of their own
#ifdef SCHEMA_HAS_IfcBSplineSurfaceWithKnots
// BIND(IfcBSplineSurfaceWithKnots);
#endif
#ifdef SCHEMA_HAS_IfcTriangulatedFaceSet
// BIND(IfcTriangulatedFaceSet);
#endif
#ifdef SCHEMA_HAS_IfcExtrudedAreaSolidTapered
// BIND(IfcExtrudedAreaSolidTapered);
#endif
BIND(IfcExtrudedAreaSolid); // -> extrusion
// BIND(IfcRevolvedAreaSolid);
BIND(IfcConnectedFaceSet); // -> shell
BIND(IfcBooleanResult); // -> boolean_result
BIND(IfcPolygonalBoundedHalfSpace); // -> face
BIND(IfcHalfSpaceSolid); // -> face
// BIND(IfcSurfaceOfLinearExtrusion);
// BIND(IfcSurfaceOfRevolution);
// BIND(IfcBlock);
// BIND(IfcRectangularPyramid);
// BIND(IfcRightCircularCylinder);
// BIND(IfcRightCircularCone);
// BIND(IfcSphere);
// BIND(IfcCsgSolid);
// BIND(IfcCurveBoundedPlane);
// BIND(IfcRectangularTrimmedSurface);
// BIND(IfcSurfaceCurveSweptAreaSolid);
// BIND(IfcSweptDiskSolid);

// IfcArbitraryProfileDefWithVoids included
BIND(IfcArbitraryClosedProfileDef); // -> face
BIND(IfcRectangleHollowProfileDef); // -> face
// IfcRoundedRectangleProfileDef included
BIND(IfcRectangleProfileDef); // -> face
// BIND(IfcTrapeziumProfileDef)
// BIND(IfcCShapeProfileDef);
// IfcAsymmetricIShapeProfileDef included
BIND(IfcIShapeProfileDef); // -> face
// BIND(IfcLShapeProfileDef);
// BIND(IfcTShapeProfileDef);
// BIND(IfcUShapeProfileDef);
// BIND(IfcZShapeProfileDef);
// IfcCircleHollowProfileDef included
BIND(IfcCircleProfileDef); // -> face
// BIND(IfcEllipseProfileDef);
// BIND(IfcCenterLineProfileDef);
// BIND(IfcCompositeProfileDef);
// BIND(IfcDerivedProfileDef);
// IfcFaceSurface included
// IfcAdvancedFace included in case of IFC4
BIND(IfcFace); // -> face

// BIND(IfcEdgeCurve);
// BIND(IfcSubedge);
// BIND(IfcOrientedEdge);
// BIND(IfcEdge);
// BIND(IfcEdgeLoop);
BIND(IfcPolyline); // -> loop
BIND(IfcPolyLoop); // -> loop
BIND(IfcCompositeCurve); // -> loop
BIND(IfcTrimmedCurve); // -> edge
// BIND(IfcArbitraryOpenProfileDef);
#ifdef SCHEMA_HAS_IfcIndexedPolyCurve
// BIND(IfcIndexedPolyCurve)
#endif

BIND(IfcCircle); // -> circle
// BIND(IfcEllipse);
// BIND(IfcLine);
#ifdef SCHEMA_HAS_IfcBSplineCurveWithKnots
// IfcRationalBSplineCurveWithKnots included
// BIND(IfcBSplineCurveWithKnots);
#endif

BIND(IfcCartesianPoint); // -> point3
BIND(IfcDirection); // -> direction3
BIND(IfcAxis2Placement2D); // -> matrix4
BIND(IfcAxis2Placement3D); // -> matrix4
// BIND(IfcAxis1Placement);
// IfcCartesianTransformationOperator2DnonUniform included
BIND(IfcCartesianTransformationOperator2D); // -> matrix4
// IfcCartesianTransformationOperator3DnonUniform included
BIND(IfcCartesianTransformationOperator3D); // -> matrix4
BIND(IfcLocalPlacement); // -> matrix4
// BIND(IfcVector);
// BIND(IfcPlane);

// BIND(IfcColourRgb);
BIND(IfcMaterial); // -> style
BIND(IfcStyledItem); // -> style
