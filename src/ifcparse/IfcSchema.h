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
 * This file provides a (quite ugly) partial reproduction of the entities       *
 * defined in IFC2X3.exp. Macro's are used to expand the definitions into C++   * 
 * code in various contexts, several enumerations, class defenitions and        *
 * conversion functions.                                                        *
 *                                                                              *
 * IFC_SHAPE_CLASS   A class that will be mapped directly to a TopoDS_Shape     *
 * IFC_FACE_CLASS    A class that will be mapped directly to a TopoDS_Face      *
 * IFC_WIRE_CLASS    A class that will be mapped directly to a TopoDS_Wire      *
 *                       These functions are automatically injected in          *
 *                       IfcGeom::convert_shape and IfcGeom::convert_wire       *
 *                       respectively and their function is called when the     *
 *                       corresponding datatype is encountered.                 *
 * IFC_CLASS         A class that will be mapped to another class aiding        *
 *                       generation of shapes or wires.                         *
 * IFC_HELPER_CLASS  A class that is not mapped to a geometrical representation *
 *                       but is included in IfcSchema::Enum and has a class def *
 * IFC_SKIP_CLASS    This datatype will not be stored when encountered, use to  *                     
 *                   save memory. Enumeration type: IfcDontCare.                *
 *                                                                              *
 *                   Other datatypes will be assigned IfcUnknown, but their     *
 *                   datatypes can still be checked using string comparisons    *
 *                                                                              *
 ********************************************************************************/

#include "../ifcparse/IfcMacro.h"

IFC_SHAPE_CLASS(ExtrudedAreaSolid)
IFC_REF(ExtrudedAreaSolid,Profile,0)
IFC_REF(ExtrudedAreaSolid,Placement,1)
IFC_REF(ExtrudedAreaSolid,Dir,2)
IFC_FLT(ExtrudedAreaSolid,Height,3)
IFC_END_CLASS

IFC_SHAPE_CLASS(FacetedBrep)
IFC_REF(FacetedBrep,Shell,0)
IFC_END_CLASS

IFC_SHAPE_CLASS(ClosedShell)
IFC_REFS(ClosedShell,Faces,0)
IFC_END_CLASS

IFC_SHAPE_CLASS(OpenShell)
IFC_REFS(OpenShell,Faces,0)
IFC_END_CLASS

IFC_SHAPE_CLASS(ShellBasedSurfaceModel)
IFC_REFS(ShellBasedSurfaceModel,Shells,0)
IFC_END_CLASS

IFC_SHAPE_CLASS(FaceBasedSurfaceModel)
IFC_REFS(FaceBasedSurfaceModel,FaceSets,0)
IFC_END_CLASS

IFC_SHAPE_CLASS(ConnectedFaceSet)
IFC_END_CLASS

IFC_SHAPE_CLASS(HalfSpaceSolid)
IFC_REF(HalfSpaceSolid,Surface,0)
IFC_BOOL(HalfSpaceSolid,Flag,1)
IFC_END_CLASS

IFC_SHAPE_CLASS(PolygonalBoundedHalfSpace)
IFC_REF(PolygonalBoundedHalfSpace,Surface,0)
IFC_BOOL(PolygonalBoundedHalfSpace,Flag,1)
IFC_REF(PolygonalBoundedHalfSpace,Placement,2)
IFC_REF(PolygonalBoundedHalfSpace,Boundary,3)
IFC_END_CLASS

IFC_SHAPE_CLASS(BooleanClippingResult)
IFC_REF(BooleanClippingResult,First,1)
IFC_REF(BooleanClippingResult,Second,2)
IFC_END_CLASS

IFC_FACE_CLASS(Face)
IFC_REFS(Face,Bounds,0)
IFC_END_CLASS

IFC_HELPER_CLASS(FaceBound)
IFC_REF(FaceBound,Loop,0)
IFC_BOOL(FaceBound,Flag,1)
IFC_END_CLASS

IFC_CLASS(Plane,gp_Pln)
IFC_REF(Plane,Placement,0)
IFC_END_CLASS

IFC_WIRE_CLASS(ArbitraryClosedProfileDef)
IFC_REF(ArbitraryClosedProfileDef,Polyline,2)
IFC_END_CLASS

IFC_FACE_CLASS(ArbitraryProfileDefWithVoids)
IFC_REF(ArbitraryProfileDefWithVoids,Polyline,2)
IFC_REFS(ArbitraryProfileDefWithVoids,Voids,3)
IFC_END_CLASS

IFC_FACE_CLASS(RectangleProfileDef)
IFC_REF(RectangleProfileDef,Placement,2)
IFC_FLT(RectangleProfileDef,Width,3)
IFC_FLT(RectangleProfileDef,Height,4)
IFC_END_CLASS

IFC_WIRE_CLASS(CircleProfileDef)
IFC_REF(CircleProfileDef,Placement,2)
IFC_FLT(CircleProfileDef,Radius,3)
IFC_END_CLASS

IFC_FACE_CLASS(CircleHollowProfileDef)
IFC_REF(CircleHollowProfileDef,Placement,2)
IFC_FLT(CircleHollowProfileDef,Radius,3)
IFC_FLT(CircleHollowProfileDef,WallThickness,4)
IFC_END_CLASS

IFC_FACE_CLASS(IShapeProfileDef)
IFC_REF(IShapeProfileDef,Placement,2)
IFC_FLT(IShapeProfileDef,Width,3)
IFC_FLT(IShapeProfileDef,Depth,4)
IFC_FLT(IShapeProfileDef,WebThickness,5)
IFC_FLT(IShapeProfileDef,FlangeThickness,6)
IFC_FLT(IShapeProfileDef,FilletRadius,7)
IFC_END_CLASS

IFC_FACE_CLASS(CShapeProfileDef)
IFC_REF(CShapeProfileDef,Placement,2)
IFC_FLT(CShapeProfileDef,Width,3)
IFC_FLT(CShapeProfileDef,Depth,4)
IFC_FLT(CShapeProfileDef,WallThickness,5)
IFC_FLT(CShapeProfileDef,Girth,6)
IFC_FLT(CShapeProfileDef,InternalFilletRadius,7)
IFC_END_CLASS

IFC_FACE_CLASS(LShapeProfileDef)
IFC_REF(LShapeProfileDef,Placement,2)
IFC_FLT(LShapeProfileDef,Depth,3)
IFC_FLT(LShapeProfileDef,Width,4)
IFC_FLT(LShapeProfileDef,Thickness,5)
IFC_FLT(LShapeProfileDef,FilletRadius,6)
IFC_FLT(LShapeProfileDef,EdgeRadius,7)
IFC_FLT(LShapeProfileDef,LegSlope,8)
IFC_END_CLASS

IFC_CURVE_CLASS(Circle)
IFC_REF(Circle,Placement,0)
IFC_FLT(Circle,Radius,1)
IFC_END_CLASS

IFC_CURVE_CLASS(Line)
IFC_REF(Line,Pnt,0)
IFC_REF(Line,Dir,1)
IFC_END_CLASS

IFC_CURVE_CLASS(Ellipse)
IFC_REF(Ellipse,Placement,0)
IFC_FLT(Ellipse,Axis1,1)
IFC_FLT(Ellipse,Axis2,2)
IFC_END_CLASS

IFC_CLASS(CartesianPoint,gp_Pnt)
IFC_FLT_SUB(CartesianPoint,X,0,0)
IFC_FLT_SUB(CartesianPoint,Y,0,1)
IFC_FLT_SUB(CartesianPoint,Z,0,2)
IFC_END_CLASS

IFC_CLASS(Direction,gp_Dir)
IFC_FLT_SUB(Direction,X,0,0)
IFC_FLT_SUB(Direction,Y,0,1)
IFC_FLT_SUB(Direction,Z,0,2)
IFC_END_CLASS

IFC_CLASS(Vector,gp_Vec)
IFC_REF(Vector,Orientation,0)
IFC_FLT(Vector,Magnitude,1)
IFC_END_CLASS

IFC_CLASS(Axis2Placement3D,gp_Trsf)
IFC_REF(Axis2Placement3D,Origin,0)
IFC_REF(Axis2Placement3D,Axis,1)
IFC_REF(Axis2Placement3D,RefDirection,2)
IFC_END_CLASS

IFC_CLASS(Axis2Placement2D,gp_Trsf2d)
IFC_REF(Axis2Placement2D,Origin,0)
IFC_REF(Axis2Placement2D,Axis,1)
IFC_END_CLASS

IFC_CLASS(LocalPlacement,gp_Trsf)
IFC_REF(LocalPlacement,Parent,0)
IFC_REF(LocalPlacement,Placement,1)
IFC_END_CLASS

IFC_WIRE_CLASS(Polyline)
IFC_REFS(Polyline,Points,0)
IFC_END_CLASS

IFC_WIRE_CLASS(CompositeCurve)
IFC_REFS(CompositeCurve,Segments,0)
IFC_BOOL(CompositeCurve,SelfIntersects,1)
IFC_END_CLASS

IFC_WIRE_CLASS(Polyloop)
IFC_REFS(Polyloop,Points,0)
IFC_END_CLASS

IFC_WIRE_CLASS(TrimmedCurve)
IFC_REF(TrimmedCurve,BasisCurve,0)
IFC_REFS(TrimmedCurve,Trim1,1)
IFC_REFS(TrimmedCurve,Trim2,2)
IFC_BOOL(TrimmedCurve,SenseAgreement,3)
IFC_STR(TrimmedCurve,MasterRepresentation,4)
IFC_END_CLASS

IFC_HELPER_CLASS(BuildingElement)
IFC_STR(BuildingElement,Guid,0)
IFC_REF(BuildingElement,Owner,1)
IFC_STR(BuildingElement,Name,2)
IFC_REF(BuildingElement,Placement,5)
IFC_REF(BuildingElement,Shape,6)
IFC_END_CLASS

IFC_HELPER_CLASS(ShapeRepresentation)
IFC_REFS(ShapeRepresentation,Shapes,3)
IFC_END_CLASS

IFC_HELPER_CLASS(CompositeCurveSegment)
IFC_STR(CompositeCurveSegment,Transition,0)
IFC_BOOL(CompositeCurveSegment,SameSense,1)
IFC_REF(CompositeCurveSegment,ParentCurve,2)
IFC_END_CLASS

IFC_HELPER_CLASS(SIUnit)
IFC_STR(SIUnit,UnitType,1)
IFC_STR(SIUnit,UnitPrefix,2)
IFC_STR(SIUnit,Name,3)
IFC_END_CLASS
IFC_HELPER_CLASS(ConversionBasedUnit)
IFC_REF(ConversionBasedUnit,Dimensions,0)
IFC_STR(ConversionBasedUnit,UnitType,1)
IFC_STR(ConversionBasedUnit,Name,2)
IFC_REF(ConversionBasedUnit,ConversionFactor,3)
IFC_END_CLASS
IFC_HELPER_CLASS(MeasureWithUnit)
IFC_REF(MeasureWithUnit,Value,0)
IFC_REF(MeasureWithUnit,Unit,1)
IFC_END_CLASS
IFC_HELPER_CLASS(UnitAssignment)
IFC_REFS(UnitAssignment,Units,0)
IFC_END_CLASS

IFC_HELPER_CLASS(ParameterValue)
IFC_FLT(ParameterValue,Value,0)
IFC_END_CLASS
IFC_HELPER_CLASS(RatioMeasure)
IFC_FLT(RatioMeasure,Value,0)
IFC_END_CLASS

IFC_HELPER_CLASS(ProductDefinitionShape)
IFC_REFS(ProductDefinitionShape,ShapeReps,2)
IFC_END_CLASS
IFC_HELPER_CLASS(ProductRepresentation) // 2x2 compatibility
IFC_END_CLASS
IFC_HELPER_CLASS(RepresentationMap)
IFC_END_CLASS
IFC_HELPER_CLASS(MappedItem)
IFC_END_CLASS
IFC_HELPER_CLASS(RelVoidsElement)
IFC_REF(RelVoidsElement,Opening,5)
IFC_END_CLASS
IFC_HELPER_CLASS(OpeningElement)
IFC_END_CLASS


IFC_RENDER_CLASS(BuildingElementProxy)
IFC_END_CLASS
IFC_RENDER_CLASS(Covering)
IFC_END_CLASS
IFC_RENDER_CLASS(Beam)
IFC_END_CLASS
IFC_RENDER_CLASS(Column)
IFC_END_CLASS
IFC_RENDER_CLASS(CurtainWall)
IFC_END_CLASS
IFC_RENDER_CLASS(Door)
IFC_END_CLASS
IFC_RENDER_CLASS(Member)
IFC_END_CLASS
IFC_RENDER_CLASS(Railing)
IFC_END_CLASS
IFC_RENDER_CLASS(Ramp)
IFC_END_CLASS
IFC_RENDER_CLASS(RampFlight)
IFC_END_CLASS
IFC_RENDER_CLASS(Wall)
IFC_END_CLASS
IFC_RENDER_CLASS(WallStandardCase)
IFC_END_CLASS
IFC_RENDER_CLASS(Slab)
IFC_END_CLASS
IFC_RENDER_CLASS(StairFlight)
IFC_END_CLASS
IFC_RENDER_CLASS(Window)
IFC_END_CLASS
IFC_RENDER_CLASS(Stair)
IFC_END_CLASS
IFC_RENDER_CLASS(Roof)
IFC_END_CLASS
IFC_RENDER_CLASS(Pile)
IFC_END_CLASS
IFC_RENDER_CLASS(Footing)
IFC_END_CLASS
IFC_RENDER_CLASS(BuildingElementComponent)
IFC_END_CLASS
IFC_RENDER_CLASS(Plate)
IFC_END_CLASS

IFC_RENDER_CLASS(IfcFlowFitting)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowSegment)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowController)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowTerminal)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowMovingDevice)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcEnergyConversionDevice)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowStorageDevice)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcFlowTreatmentDevice)
IFC_END_CLASS
IFC_RENDER_CLASS(IfcDistributionChamberElement)
IFC_END_CLASS
IFC_RENDER_CLASS(DistributionControlElement)
IFC_END_CLASS

IFC_RENDER_CLASS(Site)
IFC_END_CLASS
IFC_RENDER_CLASS(Space)
IFC_END_CLASS

IFC_RENDER_CLASS(FurnishingElement)
IFC_END_CLASS

IFC_RENDER_CLASS(TransportElement)
IFC_END_CLASS

IFC_RENDER_CLASS(GeographicElement) // 2x4 compatibility
IFC_END_CLASS
