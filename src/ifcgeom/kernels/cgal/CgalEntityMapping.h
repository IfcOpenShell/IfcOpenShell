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
 * entities. For entities of type CLASS an std::map is also created to cache    *
 * the output of the conversion functions                                       *
 *                                                                              *
 ********************************************************************************/

#include "../../../ifcparse/IfcUtil.h"
#include "../../../ifcparse/IfcParse.h"

SHAPES(IfcShellBasedSurfaceModel);
SHAPES(IfcFaceBasedSurfaceModel);
SHAPES(IfcRepresentation);
SHAPES(IfcMappedItem);
// IfcFacetedBrep included
// IfcAdvancedBrep included
// IfcFacetedBrepWithVoids included
// IfcAdvancedBrepWithVoids included
SHAPES(IfcManifoldSolidBrep);
SHAPES(IfcGeometricSet);

#ifdef USE_IFC4
//SHAPE(IfcCylindricalSurface);
//SHAPE(IfcAdvancedBrep);
//SHAPE(IfcBSplineSurfaceWithKnots);
SHAPE(IfcTriangulatedFaceSet);
SHAPE(IfcExtrudedAreaSolidTapered);
#endif
//SHAPE(IfcPlane);
SHAPE(IfcExtrudedAreaSolid);
//SHAPE(IfcRevolvedAreaSolid);
SHAPE(IfcConnectedFaceSet);
SHAPE(IfcBooleanResult);
//SHAPE(IfcPolygonalBoundedHalfSpace);
SHAPE(IfcHalfSpaceSolid);
//SHAPE(IfcSurfaceOfLinearExtrusion);
//SHAPE(IfcSurfaceOfRevolution);
SHAPE(IfcBlock);
SHAPE(IfcRectangularPyramid);
SHAPE(IfcRightCircularCylinder);
SHAPE(IfcRightCircularCone);
SHAPE(IfcSphere);
SHAPE(IfcCsgSolid);
//SHAPE(IfcCurveBoundedPlane);
//SHAPE(IfcRectangularTrimmedSurface);
//SHAPE(IfcSurfaceCurveSweptAreaSolid);
//SHAPE(IfcSweptDiskSolid);

FACE(IfcArbitraryProfileDefWithVoids);
FACE(IfcArbitraryClosedProfileDef);
FACE(IfcRoundedRectangleProfileDef);
FACE(IfcRectangleHollowProfileDef);
FACE(IfcRectangleProfileDef);
FACE(IfcTrapeziumProfileDef)
FACE(IfcCShapeProfileDef);
// IfcAsymmetricIShapeProfileDef included
FACE(IfcIShapeProfileDef);
FACE(IfcLShapeProfileDef);
FACE(IfcTShapeProfileDef);
FACE(IfcUShapeProfileDef);
FACE(IfcZShapeProfileDef);
FACE(IfcCircleHollowProfileDef);
FACE(IfcCircleProfileDef);
FACE(IfcEllipseProfileDef);
//FACE(IfcCenterLineProfileDef);
//FACE(IfcCompositeProfileDef);
FACE(IfcDerivedProfileDef);
// IfcFaceSurface included
// IfcAdvancedFace included in case of IFC4
FACE(IfcFace);

//WIRE(IfcEdgeCurve);
//WIRE(IfcSubedge);
WIRE(IfcOrientedEdge);
WIRE(IfcEdge);
WIRE(IfcEdgeLoop);
WIRE(IfcPolyline);
WIRE(IfcPolyLoop);
WIRE(IfcCompositeCurve);
WIRE(IfcTrimmedCurve);
//WIRE(IfcArbitraryOpenProfileDef);

CURVE(IfcCircle);
CURVE(IfcEllipse);
CURVE(IfcLine);
#ifdef USE_IFC4
// IfcRationalBSplineCurveWithKnots included
//CURVE(IfcBSplineCurveWithKnots);
#endif

CLASS(IfcCartesianPoint,cgal_point_t);
CLASS(IfcDirection,cgal_direction_t);
CLASS(IfcAxis2Placement2D,cgal_placement_t);
CLASS(IfcAxis2Placement3D,cgal_placement_t);
CLASS(IfcAxis1Placement,cgal_placement_t);
CLASS(IfcCartesianTransformationOperator2DnonUniform,cgal_placement_t);
CLASS(IfcCartesianTransformationOperator3DnonUniform,cgal_placement_t);
CLASS(IfcCartesianTransformationOperator2D,cgal_placement_t);
CLASS(IfcCartesianTransformationOperator3D,cgal_placement_t);
CLASS(IfcObjectPlacement,cgal_placement_t);
CLASS(IfcVector,cgal_vector_t);
CLASS(IfcPlane,cgal_plane_t);
