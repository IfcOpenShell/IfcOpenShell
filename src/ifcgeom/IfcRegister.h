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

#include <TopoDS_Shape.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <gp_Pnt.hxx>
#include <gp_Pln.hxx>
#include <gp_Dir.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcParse.h"

SHAPES(IfcShellBasedSurfaceModel);
SHAPES(IfcFaceBasedSurfaceModel);
SHAPES(IfcRepresentation);
SHAPES(IfcMappedItem);
SHAPES(IfcFacetedBrep);
SHAPES(IfcGeometricSet);

#ifdef USE_IFC4
SHAPE(IfcCylindricalSurface);
SHAPE(IfcAdvancedBrep);
// FIXME: Surfaces should have a shape type of their own
SHAPE(IfcBSplineSurfaceWithKnots);
SHAPE(IfcPlane);
SHAPE(IfcTriangulatedFaceSet);
#endif
SHAPE(IfcExtrudedAreaSolid);
SHAPE(IfcRevolvedAreaSolid);
SHAPE(IfcConnectedFaceSet);
SHAPE(IfcBooleanResult);
SHAPE(IfcPolygonalBoundedHalfSpace);
SHAPE(IfcHalfSpaceSolid);
// FIXME: Surfaces should have a shape type of their own
SHAPE(IfcSurfaceOfLinearExtrusion);
SHAPE(IfcSurfaceOfRevolution);
SHAPE(IfcBlock);
SHAPE(IfcRectangularPyramid);
SHAPE(IfcRightCircularCylinder);
SHAPE(IfcRightCircularCone);
SHAPE(IfcSphere);
SHAPE(IfcCsgSolid);
SHAPE(IfcCurveBoundedPlane);
SHAPE(IfcRectangularTrimmedSurface);
SHAPE(IfcSurfaceCurveSweptAreaSolid);
SHAPE(IfcSweptDiskSolid);

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
FACE(IfcCenterLineProfileDef);
FACE(IfcCompositeProfileDef);
FACE(IfcDerivedProfileDef);
// IfcFaceSurface included
// IfcAdvancedFace included in case of IFC4
FACE(IfcFace);

WIRE(IfcEdgeCurve);
WIRE(IfcSubedge);
WIRE(IfcOrientedEdge);
WIRE(IfcEdge);
WIRE(IfcEdgeLoop);
WIRE(IfcPolyline);
WIRE(IfcPolyLoop);
WIRE(IfcCompositeCurve);
WIRE(IfcTrimmedCurve);
WIRE(IfcArbitraryOpenProfileDef);

CURVE(IfcCircle);
CURVE(IfcEllipse);
CURVE(IfcLine);
#ifdef USE_IFC4
CURVE(IfcBSplineCurveWithKnots);
#endif

CLASS(IfcCartesianPoint,gp_Pnt);
CLASS(IfcDirection,gp_Dir);
CLASS(IfcAxis2Placement2D,gp_Trsf2d);
CLASS(IfcAxis2Placement3D,gp_Trsf);
CLASS(IfcAxis1Placement,gp_Ax1);
CLASS(IfcCartesianTransformationOperator2DnonUniform,gp_GTrsf2d);
CLASS(IfcCartesianTransformationOperator3DnonUniform,gp_GTrsf);
CLASS(IfcCartesianTransformationOperator2D,gp_Trsf2d);
CLASS(IfcCartesianTransformationOperator3D,gp_Trsf);
CLASS(IfcObjectPlacement,gp_Trsf);
CLASS(IfcVector,gp_Vec);
CLASS(IfcPlane,gp_Pln);