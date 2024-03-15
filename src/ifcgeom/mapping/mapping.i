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
 * entities.                                                                    *
 *                                                                              *
 ********************************************************************************/

BIND(IfcProduct);

BIND(IfcShellBasedSurfaceModel);
BIND(IfcFaceBasedSurfaceModel);
BIND(IfcRepresentation);
BIND(IfcMappedItem);
// IfcFacetedBrep included
// IfcAdvancedBrep included
// IfcFacetedBrepWithVoids included
// IfcAdvancedBrepWithVoids included
BIND(IfcManifoldSolidBrep);
BIND(IfcGeometricSet);

#ifdef SCHEMA_HAS_IfcCylindricalSurface
BIND(IfcCylindricalSurface);
#endif
#ifdef SCHEMA_HAS_IfcToroidalSurface
BIND(IfcToroidalSurface);
#endif
#ifdef SCHEMA_HAS_IfcSphericalSurface
BIND(IfcSphericalSurface);
#endif
// FIXME: Surfaces should have a shape type of their own
#ifdef SCHEMA_HAS_IfcBSplineSurfaceWithKnots
BIND(IfcBSplineSurfaceWithKnots);
#endif
#ifdef SCHEMA_HAS_IfcTriangulatedFaceSet
BIND(IfcTriangulatedFaceSet);
#endif
#ifdef SCHEMA_HAS_IfcPolygonalFaceSet
BIND(IfcPolygonalFaceSet);
#endif
#ifdef SCHEMA_HAS_IfcExtrudedAreaSolidTapered
BIND(IfcExtrudedAreaSolidTapered);
#endif
BIND(IfcPlane);
BIND(IfcExtrudedAreaSolid);
BIND(IfcRevolvedAreaSolid);
BIND(IfcConnectedFaceSet);
BIND(IfcBooleanResult);
BIND(IfcPolygonalBoundedHalfSpace);
BIND(IfcHalfSpaceSolid);
// FIXME: Surfaces should have a shape type of their own
BIND(IfcSurfaceOfLinearExtrusion);
BIND(IfcSurfaceOfRevolution);
BIND(IfcBlock);
BIND(IfcBoundingBox);
BIND(IfcRectangularPyramid);
BIND(IfcRightCircularCylinder);
BIND(IfcRightCircularCone);
BIND(IfcSphere);
BIND(IfcCsgSolid);
BIND(IfcCurveBoundedPlane);
BIND(IfcRectangularTrimmedSurface);
BIND(IfcSurfaceCurveSweptAreaSolid);
BIND(IfcSweptDiskSolid);

BIND(IfcAnnotationFillArea);
// IfcArbitraryProfileDefWithVoids included
BIND(IfcArbitraryClosedProfileDef);
BIND(IfcRoundedRectangleProfileDef);
BIND(IfcRectangleHollowProfileDef);
BIND(IfcRectangleProfileDef);
BIND(IfcTrapeziumProfileDef);
BIND(IfcCShapeProfileDef);
// IfcAsymmetricIShapeProfileDef included
BIND(IfcIShapeProfileDef);
BIND(IfcLShapeProfileDef);
BIND(IfcTShapeProfileDef);
BIND(IfcUShapeProfileDef);
BIND(IfcZShapeProfileDef);
BIND(IfcCircleProfileDef);
BIND(IfcEllipseProfileDef);
BIND(IfcCenterLineProfileDef);
BIND(IfcCompositeProfileDef);
BIND(IfcDerivedProfileDef);
// IfcFaceSurface included
// IfcAdvancedFace included in case of IFC4
BIND(IfcFace);

#ifdef SCHEMA_HAS_IfcCraneRailAShapeProfileDef
BIND(IfcCraneRailAShapeProfileDef);
#endif

BIND(IfcOrientedEdge);
BIND(IfcEdge);
BIND(IfcEdgeLoop);
BIND(IfcPolyline);
BIND(IfcPolyLoop);
#ifdef SCHEMA_HAS_IfcSegmentedReferenceCurve
BIND(IfcSegmentedReferenceCurve);
#endif
#ifdef SCHEMA_HAS_IfcGradientCurve
BIND(IfcGradientCurve);
#endif
BIND(IfcCompositeCurve);
#ifdef SCHEMA_HAS_IfcOffsetCurveByDistances
BIND(IfcOffsetCurveByDistances)
#endif
BIND(IfcTrimmedCurve);
BIND(IfcArbitraryOpenProfileDef);
#ifdef SCHEMA_HAS_IfcIndexedPolyCurve
BIND(IfcIndexedPolyCurve);
#endif

#ifdef SCHEMA_HAS_IfcFixedReferenceSweptAreaSolid
BIND(IfcFixedReferenceSweptAreaSolid)
#endif
#ifdef SCHEMA_HAS_IfcSectionedSolidHorizontal
BIND(IfcSectionedSolidHorizontal)
#endif

BIND(IfcCircle);
BIND(IfcEllipse);
BIND(IfcLine);
#ifdef SCHEMA_HAS_IfcBSplineCurveWithKnots
// IfcRationalBSplineCurveWithKnots included
BIND(IfcBSplineCurveWithKnots);
#endif
#ifdef SCHEMA_HAS_IfcSurfaceCurve
BIND(IfcSurfaceCurve);
#endif

BIND(IfcCartesianPoint);
#ifdef SCHEMA_HAS_IfcPointByDistanceExpression
BIND(IfcPointByDistanceExpression)
#endif
BIND(IfcDirection);
#ifdef SCHEMA_HAS_IfcAxis2PlacementLinear
BIND(IfcAxis2PlacementLinear)
#endif
BIND(IfcAxis2Placement2D);
BIND(IfcAxis2Placement3D);
BIND(IfcAxis1Placement);
// IfcCartesianTransformationOperator2DnonUniform included
BIND(IfcCartesianTransformationOperator2D);
// IfcCartesianTransformationOperator3DnonUniform included
BIND(IfcCartesianTransformationOperator3D);
BIND(IfcObjectPlacement); // -> matrix4
BIND(IfcVector);

// BIND(IfcColourRgb);
BIND(IfcMaterial); // -> style
BIND(IfcStyledItem); // -> style

#ifdef SCHEMA_HAS_IfcCurveSegment
BIND(IfcCurveSegment);
#endif