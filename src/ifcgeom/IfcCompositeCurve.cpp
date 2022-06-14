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

#include <cmath>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt2d.hxx>
#include <gp_Vec2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax3.hxx>
#include <gp_Ax2d.hxx>
#include <gp_Pln.hxx>
#include <gp_Circ.hxx>
#include <GC_MakeCircle.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <Geom_Line.hxx>
#include <Geom_Circle.hxx>
#include <Geom_Ellipse.hxx>
#include <Geom_TrimmedCurve.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakeShell.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp.hxx>
#include <TopExp_Explorer.hxx>
#include <TopLoc_Location.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepOffsetAPI_Sewing.hxx>
#include <BRepPrimAPI_MakePrism.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>
#include <BRep_Tool.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <ShapeFix_Solid.hxx>
#include <Geom_BSplineCurve.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <ShapeBuild_ReShape.hxx>
#include <TopTools_ListOfShape.hxx>
#include <TopTools_ListIteratorOfListOfShape.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <Standard_Version.hxx>
#include <BRepAdaptor_HCompCurve.hxx>
#include <Approx_Curve3d.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <Extrema_ExtPC.hxx>

#include "../ifcgeom_schema_agnostic/wire_builder.h"

#define _USE_MATH_DEFINES
#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCompositeCurve* l, TopoDS_Wire& wire) {
	if ( getValue(GV_PLANEANGLE_UNIT)<0 ) {
		Logger::Message(Logger::LOG_WARNING,"Creating a composite curve without unit information:",l);

		// Temporarily pretend we do have unit information
		setValue(GV_PLANEANGLE_UNIT,1.0);
		
		bool succes_radians = false;
        bool succes_degrees = false;
        bool use_radians = false;
        bool use_degrees = false;

		// First try radians
		TopoDS_Wire wire_radians, wire_degrees;
        try {
		    succes_radians = IfcGeom::Kernel::convert(l,wire_radians);
        } catch (const std::exception& e) {
			Logger::Notice(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Notice(e.GetMessageString());
			} else {
				Logger::Notice("Unknown error using radians");
			}
		} catch (...) {
			Logger::Notice("Unknown error using radians");
		}

		// Now try degrees
		setValue(GV_PLANEANGLE_UNIT,0.0174532925199433);
        try {
		    succes_degrees = IfcGeom::Kernel::convert(l,wire_degrees);
        } catch (const std::exception& e) {
			Logger::Notice(e);
		} catch (const Standard_Failure& e) {
			if (e.GetMessageString() && strlen(e.GetMessageString())) {
				Logger::Notice(e.GetMessageString());
			} else {
				Logger::Notice("Unknown error using degrees");
			}
		} catch (...) {
			Logger::Notice("Unknown error using degrees");
		}

		// Restore to unknown unit state
		setValue(GV_PLANEANGLE_UNIT,-1.0);

		if ( succes_degrees && ! succes_radians ) {
			use_degrees = true;
		} else if ( succes_radians && ! succes_degrees ) {
			use_radians = true;
		} else if ( succes_radians && succes_degrees ) {
			if ( wire_degrees.Closed() && ! wire_radians.Closed() ) {
				use_degrees = true;
			} else if ( wire_radians.Closed() && ! wire_degrees.Closed() ) {
				use_radians = true;
			} else {
				// No heuristic left to prefer the one over the other,
				// apparently both variants are equally successful.
				// The curve might be composed of only straight segments.
				// Let's go with the wire created using radians as that
				// at least is a SI unit.
				use_radians = true;
			}
		}

		if ( use_radians ) {
			Logger::Message(Logger::LOG_NOTICE,"Used radians to create composite curve");
            wire = wire_radians;
		} else if ( use_degrees ) {
			Logger::Message(Logger::LOG_NOTICE,"Used degrees to create composite curve");
            wire = wire_degrees;
		}

		return use_radians || use_degrees;
	}

#ifdef SCHEMA_HAS_IfcSegment
	// 4x3
	IfcSchema::IfcSegment::list::ptr segments = l->Segments();
#else
	IfcSchema::IfcCompositeCurveSegment::list::ptr segments = l->Segments();
#endif

	TopTools_ListOfShape converted_segments;
	
	for (auto it = segments->begin(); it != segments->end(); ++it) {

		if (!(*it)->declaration().is(IfcSchema::IfcCompositeCurveSegment::Class())) {
			Logger::Error("Not implemented", *it);
			return false;
		}

		IfcSchema::IfcCurve* curve = ((IfcSchema::IfcCompositeCurveSegment*)(*it))->ParentCurve();

		// The type of ParentCurve is IfcCurve, but the documentation says:
		// ParentCurve: The *bounded curve* which defines the geometry of the segment. 
		// At least let's exclude IfcLine as an infinite linear segment
		// definitely does not make any sense.
		TopoDS_Wire segment;

		if (curve->as<IfcSchema::IfcLine>()) {
			Logger::Notice("Infinite IfcLine used as ParentCurve of segment, treating as a segment", *it);
			Handle_Geom_Curve handle;
			convert_curve(curve, handle);
			double u0 = 0.0;
			double u1 = curve->as<IfcSchema::IfcLine>()->Dir()->Magnitude() * getValue(GV_LENGTH_UNIT);
			if (u1 < getValue(GV_PRECISION)) {
				Logger::Warning("Segment length below tolerance", *it);
			}
			BRepBuilderAPI_MakeEdge me(handle, u0, u1);
			if (me.IsDone()) {
				BRep_Builder B;
				B.MakeWire(segment);
				B.Add(segment, me.Edge());
			}
		} else if (!convert_wire(curve, segment)) {
			const bool failed_on_purpose = curve->as<IfcSchema::IfcPolyline>() && !segment.IsNull();
			Logger::Message(failed_on_purpose ? Logger::LOG_WARNING : Logger::LOG_ERROR, "Failed to convert curve:", curve);
			continue;
		}

		if (!((IfcSchema::IfcCompositeCurveSegment*)(*it))->SameSense()) {
			segment.Reverse();
		}

		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(segment, getValue(GV_PRECISION), TopAbs_WIRE);

		converted_segments.Append(segment);

	}

	if (converted_segments.Extent() == 0) {
		Logger::Message(Logger::LOG_ERROR, "No segment succesfully converted:", l);
		return false;
	}

	BRepBuilderAPI_MakeWire w;
	TopoDS_Vertex wire_first_vertex, wire_last_vertex, edge_first_vertex, edge_last_vertex;

	TopTools_ListIteratorOfListOfShape it(converted_segments);

	aggregate_of_instance::ptr profile = l->data().getInverse(&IfcSchema::IfcProfileDef::Class(), -1);
	const bool force_close = profile && profile->size() > 0;

	util::wire_builder bld(getValue(GV_PRECISION), l);
	util::shape_pair_enumerate(it, bld, force_close);
	wire = bld.wire();

	return true;
}
