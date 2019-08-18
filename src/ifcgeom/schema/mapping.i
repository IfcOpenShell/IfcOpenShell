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

// BIND(IfcShellBasedSurfaceModel);
// BIND(IfcFaceBasedSurfaceModel);
// BIND(IfcRepresentation);
// BIND(IfcMappedItem);
// IfcFacetedBrep included
// IfcAdvancedBrep included
// IfcFacetedBrepWithVoids included
// IfcAdvancedBrepWithVoids included
// BIND(IfcManifoldSolidBrep);
// BIND(IfcGeometricSet);

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
BIND(IfcExtrudedAreaSolid);
// BIND(IfcRevolvedAreaSolid);
// BIND(IfcConnectedFaceSet);
// BIND(IfcBooleanResult);
// BIND(IfcPolygonalBoundedHalfSpace);
// BIND(IfcHalfSpaceSolid);
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

// BIND(IfcArbitraryProfileDefWithVoids);
// BIND(IfcArbitraryClosedProfileDef);
// BIND(IfcRoundedRectangleProfileDef);
// BIND(IfcRectangleHollowProfileDef);
// BIND(IfcRectangleProfileDef);
// BIND(IfcTrapeziumProfileDef)
// BIND(IfcCShapeProfileDef);
// IfcAsymmetricIShapeProfileDef included
// BIND(IfcIShapeProfileDef);
// BIND(IfcLShapeProfileDef);
// BIND(IfcTShapeProfileDef);
// BIND(IfcUShapeProfileDef);
// BIND(IfcZShapeProfileDef);
// BIND(IfcCircleHollowProfileDef);
// BIND(IfcCircleProfileDef);
// BIND(IfcEllipseProfileDef);
// BIND(IfcCenterLineProfileDef);
// BIND(IfcCompositeProfileDef);
// BIND(IfcDerivedProfileDef);
// IfcFaceSurface included
// IfcAdvancedFace included in case of IFC4
// BIND(IfcFace);

// BIND(IfcEdgeCurve);
// BIND(IfcSubedge);
// BIND(IfcOrientedEdge);
// BIND(IfcEdge);
// BIND(IfcEdgeLoop);
// BIND(IfcPolyline);
// BIND(IfcPolyLoop);
// BIND(IfcCompositeCurve);
// BIND(IfcTrimmedCurve);
// BIND(IfcArbitraryOpenProfileDef);
#ifdef SCHEMA_HAS_IfcIndexedPolyCurve
// BIND(IfcIndexedPolyCurve)
#endif

// BIND(IfcCircle);
// BIND(IfcEllipse);
// BIND(IfcLine);
#ifdef SCHEMA_HAS_IfcBSplineCurveWithKnots
// IfcRationalBSplineCurveWithKnots included
// BIND(IfcBSplineCurveWithKnots);
#endif

// BIND(IfcCartesianPoint);
// BIND(IfcDirection);
// BIND(IfcAxis2Placement2D);
BIND(IfcAxis2Placement3D);
// BIND(IfcAxis1Placement);
// BIND(IfcCartesianTransformationOperator2DnonUniform);
// BIND(IfcCartesianTransformationOperator3DnonUniform);
// BIND(IfcCartesianTransformationOperator2D);
// BIND(IfcCartesianTransformationOperator3D);
// BIND(IfcObjectPlacement);
// BIND(IfcVector);
// BIND(IfcPlane);

// BIND(IfcColourRgb);
BIND(IfcMaterial);
BIND(IfcStyledItem);
