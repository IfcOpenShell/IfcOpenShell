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
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>

#include "../ifcparse/IfcParse.h"

using namespace Ifc2x3;

SHAPE(IfcExtrudedAreaSolid);
SHAPE(IfcClosedShell);
SHAPE(IfcConnectedFaceSet);
SHAPE(IfcFacetedBrep);
SHAPE(IfcShellBasedSurfaceModel);
SHAPE(IfcFaceBasedSurfaceModel);
SHAPE(IfcBooleanClippingResult);
SHAPE(IfcShapeRepresentation);
SHAPE(IfcMappedItem);
SHAPE(IfcPolygonalBoundedHalfSpace);
SHAPE(IfcHalfSpaceSolid);

FACE(IfcArbitraryProfileDefWithVoids);
FACE(IfcArbitraryClosedProfileDef);
FACE(IfcRectangleProfileDef);
FACE(IfcIShapeProfileDef);
FACE(IfcCShapeProfileDef);
FACE(IfcLShapeProfileDef);
FACE(IfcCircleProfileDef);
FACE(IfcFace);
FACE(IfcCircleHollowProfileDef);

WIRE(IfcPolyline);
WIRE(IfcPolyLoop);
WIRE(IfcCompositeCurve);
WIRE(IfcTrimmedCurve);

CURVE(IfcCircle);
CURVE(IfcEllipse);
CURVE(IfcLine);

CLASS(IfcCartesianPoint,gp_Pnt);
CLASS(IfcDirection,gp_Dir);
CLASS(IfcAxis2Placement2D,gp_Trsf2d);
CLASS(IfcAxis2Placement3D,gp_Trsf);
CLASS(IfcCartesianTransformationOperator2D,gp_Trsf2d);
CLASS(IfcCartesianTransformationOperator3D,gp_Trsf);
CLASS(IfcObjectPlacement,gp_Trsf);
CLASS(IfcVector,gp_Vec);
CLASS(IfcPlane,gp_Pln);