﻿/********************************************************************************
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
 * Implementations of the various conversion functions defined in IfcRegister.h *
 *                                                                              *
 ********************************************************************************/

#define _USE_MATH_DEFINES
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

#include "../ifcgeom/IfcGeom.h"

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCompositeCurve* l, TopoDS_Wire& wire) {
	if ( getValue(GV_PLANEANGLE_UNIT)<0 ) {
		Logger::Message(Logger::LOG_WARNING,"Creating a composite curve without unit information:",l->entity);

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
				// apparently both variants are equally succesful.
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
	IfcSchema::IfcCompositeCurveSegment::list::ptr segments = l->Segments();
	BRepBuilderAPI_MakeWire w;
	//TopoDS_Vertex last_vertex;
	for( IfcSchema::IfcCompositeCurveSegment::list::it it = segments->begin(); it != segments->end(); ++ it ) {
		IfcSchema::IfcCurve* curve = (*it)->ParentCurve();
		TopoDS_Wire wire2;
		if ( !convert_wire(curve,wire2) ) {
			Logger::Message(Logger::LOG_ERROR,"Failed to convert curve:",curve->entity);
			continue;
		}
		if ( ! (*it)->SameSense() ) wire2.Reverse();
		ShapeFix_ShapeTolerance FTol;
		FTol.SetTolerance(wire2, getValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_WIRE);
		/*if ( it != segments->begin() ) {
			TopExp_Explorer exp (wire2,TopAbs_VERTEX);
			const TopoDS_Vertex& first_vertex = TopoDS::Vertex(exp.Current());
			gp_Pnt first = BRep_Tool::Pnt(first_vertex);
			gp_Pnt last = BRep_Tool::Pnt(last_vertex);
			Standard_Real distance = first.Distance(last);
			if ( distance > ALMOST_ZERO ) {
				w.Add( BRepBuilderAPI_MakeEdge( last_vertex, first_vertex ) );
			}
		}*/
		w.Add(wire2);
		//last_vertex = w.Vertex();
		if ( w.Error() != BRepBuilderAPI_WireDone ) {
			Logger::Message(Logger::LOG_ERROR,"Failed to join curve segments:",l->entity);

			TopoDS_Vertex v1, v2, last;
			last = w.Vertex();
				
			if (!last.IsNull()) {
				std::stringstream ss;
				gp_Pnt p = BRep_Tool::Pnt(last);
				ss << std::setprecision(4) << "Last vertex at (" << p.X() << " " << p.Y() << " " << p.Z() << ")";
				Logger::Message(Logger::LOG_NOTICE, ss.str());
			}

			TopExp::Vertices(wire2, v1, v2);
			if (!v1.IsNull()) {
				std::stringstream ss;
				gp_Pnt p = BRep_Tool::Pnt(v1);
				ss << std::setprecision(4) << "Segment starts at (" << p.X() << " " << p.Y() << " " << p.Z() << ") for:";
				Logger::Message(Logger::LOG_NOTICE, ss.str(), (*it)->entity);
			}
			
			return false;
		}
	}
	wire = w.Wire();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcTrimmedCurve* l, TopoDS_Wire& wire) {
	IfcSchema::IfcCurve* basis_curve = l->BasisCurve();
	bool isConic = basis_curve->is(IfcSchema::Type::IfcConic);
	double parameterFactor = isConic ? getValue(GV_PLANEANGLE_UNIT) : getValue(GV_LENGTH_UNIT);
	Handle(Geom_Curve) curve;
	if ( !convert_curve(basis_curve,curve) ) return false;
	bool trim_cartesian = l->MasterRepresentation() != IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER;
	IfcEntityList::ptr trims1 = l->Trim1();
	IfcEntityList::ptr trims2 = l->Trim2();
	unsigned sense_agreement = l->SenseAgreement() ? 0 : 1;
	double flts[2];
	gp_Pnt pnts[2];
	bool has_flts[2] = {false,false};
	bool has_pnts[2] = {false,false};
	BRepBuilderAPI_MakeWire w;
	for ( IfcEntityList::it it = trims1->begin(); it != trims1->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[sense_agreement] );
			has_pnts[sense_agreement] = true;
		} else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[sense_agreement] = value * parameterFactor;
			has_flts[sense_agreement] = true;
		}
	}
	for ( IfcEntityList::it it = trims2->begin(); it != trims2->end(); it ++ ) {
		IfcUtil::IfcBaseClass* i = *it;
		if ( i->is(IfcSchema::Type::IfcCartesianPoint) ) {
			IfcGeom::Kernel::convert((IfcSchema::IfcCartesianPoint*)i, pnts[1-sense_agreement] );
			has_pnts[1-sense_agreement] = true;
		} else if ( i->is(IfcSchema::Type::IfcParameterValue) ) {
			const double value = *((IfcSchema::IfcParameterValue*)i);
			flts[1-sense_agreement] = value * parameterFactor;
			has_flts[1-sense_agreement] = true;
		}
	}
	trim_cartesian &= has_pnts[0] && has_pnts[1];
	bool trim_cartesian_failed = !trim_cartesian;
	if ( trim_cartesian ) {
		if ( pnts[0].Distance(pnts[1]) < getValue(GV_WIRE_CREATION_TOLERANCE) ) {
			Logger::Message(Logger::LOG_WARNING,"Skipping segment with length below tolerance level:",l->entity);
			return false;
		}
		ShapeFix_ShapeTolerance FTol;
		TopoDS_Vertex v1 = BRepBuilderAPI_MakeVertex(pnts[0]);
		TopoDS_Vertex v2 = BRepBuilderAPI_MakeVertex(pnts[1]);
		FTol.SetTolerance(v1, getValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_VERTEX);
		FTol.SetTolerance(v2, getValue(GV_WIRE_CREATION_TOLERANCE), TopAbs_VERTEX);
		BRepBuilderAPI_MakeEdge e (curve,v1,v2);
		if ( ! e.IsDone() ) {
			BRepBuilderAPI_EdgeError err = e.Error();
			if ( err == BRepBuilderAPI_PointProjectionFailed ) {
				Logger::Message(Logger::LOG_WARNING,"Point projection failed for:",l->entity);
				trim_cartesian_failed = true;
			}
		} else {
			w.Add(e.Edge());
		}
	}
	if ( (!trim_cartesian || trim_cartesian_failed) && (has_flts[0] && has_flts[1]) ) {
		// The Geom_Line is constructed from a gp_Pnt and gp_Dir, whereas the IfcLine
		// is defined by an IfcCartesianPoint and an IfcVector with Magnitude. Because
		// the vector is normalised when passed to Geom_Line constructor the magnitude
		// needs to be factored in with the IfcParameterValue here.
		if ( basis_curve->is(IfcSchema::Type::IfcLine) ) {
			IfcSchema::IfcLine* line = static_cast<IfcSchema::IfcLine*>(basis_curve);
			const double magnitude = line->Dir()->Magnitude();
			flts[0] *= magnitude; flts[1] *= magnitude;
		}
		if ( basis_curve->is(IfcSchema::Type::IfcEllipse) ) {
			IfcSchema::IfcEllipse* ellipse = static_cast<IfcSchema::IfcEllipse*>(basis_curve);
			double x = ellipse->SemiAxis1() * getValue(GV_LENGTH_UNIT);
			double y = ellipse->SemiAxis2() * getValue(GV_LENGTH_UNIT);
			const bool rotated = y > x;
			if (rotated) {
				flts[0] -= M_PI / 2.;
				flts[1] -= M_PI / 2.;
			}
		}
		if ( isConic && ALMOST_THE_SAME(fmod(flts[1]-flts[0],M_PI*2.),0.) ) {
			w.Add(BRepBuilderAPI_MakeEdge(curve));
		} else {
			BRepBuilderAPI_MakeEdge e (curve,flts[0],flts[1]);
			w.Add(e.Edge());
		}			
	} else if ( trim_cartesian_failed && (has_pnts[0] && has_pnts[1]) ) {
		w.Add(BRepBuilderAPI_MakeEdge(pnts[0],pnts[1]));
	}
	if ( w.IsDone() ) {
		wire = w.Wire();
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolyline* l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list::ptr points = l->Points();

	// Parse and store the points in a sequence
	TColgp_SequenceOfPnt polygon;
	for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
		gp_Pnt pnt;
		IfcGeom::Kernel::convert(*it, pnt);
		polygon.Append(pnt);
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon, false);
	
	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}

	result = w.Wire();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcPolyLoop* l, TopoDS_Wire& result) {
	IfcSchema::IfcCartesianPoint::list::ptr points = l->Polygon();

	// Parse and store the points in a sequence
	TColgp_SequenceOfPnt polygon;
	for(IfcSchema::IfcCartesianPoint::list::it it = points->begin(); it != points->end(); ++ it) {
		gp_Pnt pnt;
		IfcGeom::Kernel::convert(*it, pnt);
		polygon.Append(pnt);
	}

	// A loop should consist of at least three vertices
	int original_count = polygon.Length();
	if (original_count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
		return false;
	}

	// Remove points that are too close to one another
	remove_duplicate_points_from_loop(polygon, true);

	int count = polygon.Length();
	if (original_count - count != 0) {
		std::stringstream ss; ss << (original_count - count) << " edges removed for:"; 
		Logger::Message(Logger::LOG_WARNING, ss.str(), l->entity);
	}

	if (count < 3) {
		Logger::Message(Logger::LOG_ERROR, "Not enough edges for:", l->entity);
		return false;
	}

	BRepBuilderAPI_MakePolygon w;
	for (int i = 1; i <= polygon.Length(); ++i) {
		w.Add(polygon.Value(i));
	}
	w.Close();

	result = w.Wire();	
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcArbitraryOpenProfileDef* l, TopoDS_Wire& result) {
	return convert_wire(l->Curve(), result);
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdgeCurve* l, TopoDS_Wire& result) {
	IfcSchema::IfcPoint* pnt1 = ((IfcSchema::IfcVertexPoint*) l->EdgeStart())->VertexGeometry();
	IfcSchema::IfcPoint* pnt2 = ((IfcSchema::IfcVertexPoint*) l->EdgeEnd())->VertexGeometry();
	if (!pnt1->is(IfcSchema::Type::IfcCartesianPoint) || !pnt2->is(IfcSchema::Type::IfcCartesianPoint)) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", l->entity);
		return false;
	}
	
	gp_Pnt p1, p2;
	if (!IfcGeom::Kernel::convert(((IfcSchema::IfcCartesianPoint*)pnt1), p1) ||
		!IfcGeom::Kernel::convert(((IfcSchema::IfcCartesianPoint*)pnt2), p2))
	{
		return false;
	}
	
	BRepBuilderAPI_MakeWire mw;
	Handle_Geom_Curve crv;

	// The lack of a clear separation between topological and geometrical entities
	// is starting to get problematic. If the underlying curve is bounded it is
	// assumed that a topological wire can be crafted from it. After which an
	// attempt is made to reconstruct it from the individual curves and the vertices
	// of the IfcEdgeCurve.
	const bool is_bounded = l->EdgeGeometry()->is(IfcSchema::Type::IfcBoundedCurve);

	if (!is_bounded && convert_curve(l->EdgeGeometry(), crv)) {
		mw.Add(BRepBuilderAPI_MakeEdge(crv, p1, p2));
		result = mw;
		return true;
	} else if (is_bounded && convert_wire(l->EdgeGeometry(), result)) {
		if (!l->SameSense()) {
			result.Reverse();
		}
		
		bool first = true;
		TopExp_Explorer exp(result, TopAbs_EDGE);
		
		while (exp.More()) {
			const TopoDS_Edge& ed = TopoDS::Edge(exp.Current());
			Standard_Real u1, u2;
			Handle(Geom_Curve) ecrv = BRep_Tool::Curve(ed, u1, u2);
			exp.Next();
			const bool last = !exp.More();

			gp_Pnt a, b;

			if (first && last) {
				a = p1;
				b = p2;				
			} else if (first) {
				a = p1;
				ecrv->D0(u2, b);
			} else if (last) {
				ecrv->D0(u1, a);
				b = p2;
			} else {
				mw.Add(BRepBuilderAPI_MakeEdge(ecrv, u1, u2));
				first = false;
				continue;
			}

			BRep_Builder builder;
			TopoDS_Vertex v1, v2;
			/// @todo project first and emit warnings accordingly
			builder.MakeVertex(v1, a, getValue(GV_PRECISION));
			builder.MakeVertex(v2, b, getValue(GV_PRECISION));

			mw.Add(BRepBuilderAPI_MakeEdge(ecrv, v1, v2));

			first = false;
		}
		result = mw;
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdgeLoop* l, TopoDS_Wire& result) {
	IfcSchema::IfcOrientedEdge::list::ptr li = l->EdgeList();
	BRepBuilderAPI_MakeWire mw;
	for (IfcSchema::IfcOrientedEdge::list::it it = li->begin(); it != li->end(); ++it) {
		TopoDS_Wire w;
		if (convert_wire(*it, w)) {
			mw.Add(TopoDS::Edge(TopoDS_Iterator(w).Value()));
		}
	}
	result = mw;
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcEdge* l, TopoDS_Wire& result) {
	if (!l->EdgeStart()->is(IfcSchema::Type::IfcVertexPoint) || !l->EdgeEnd()->is(IfcSchema::Type::IfcVertexPoint)) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcVertexPoints are supported for EdgeStart and -End", l->entity);
		return false;
	}

	IfcSchema::IfcPoint* pnt1 = ((IfcSchema::IfcVertexPoint*) l->EdgeStart())->VertexGeometry();
	IfcSchema::IfcPoint* pnt2 = ((IfcSchema::IfcVertexPoint*) l->EdgeEnd())->VertexGeometry();
	if (!pnt1->is(IfcSchema::Type::IfcCartesianPoint) || !pnt2->is(IfcSchema::Type::IfcCartesianPoint)) {
		Logger::Message(Logger::LOG_ERROR, "Only IfcCartesianPoints are supported for VertexGeometry", l->entity);
		return false;
	}
	
	gp_Pnt p1, p2;
	if (!convert(((IfcSchema::IfcCartesianPoint*)pnt1), p1) ||
		!convert(((IfcSchema::IfcCartesianPoint*)pnt2), p2))
	{
		return false;
	}

	BRepBuilderAPI_MakeWire mw;
	mw.Add(BRepBuilderAPI_MakeEdge(p1, p2));

	result = mw.Wire();
	return true;
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcOrientedEdge* l, TopoDS_Wire& result) {
	if (convert_wire(l->EdgeElement(), result)) {
		if (!l->Orientation()) {
			result.Reverse();
		}
		return true;
	} else {
		return false;
	}
}

bool IfcGeom::Kernel::convert(const IfcSchema::IfcSubedge* l, TopoDS_Wire& result) {
	TopoDS_Wire temp;
	if (convert_wire(l->ParentEdge(), result) && convert((IfcSchema::IfcEdge*) l, temp)) {
		TopExp_Explorer exp(result, TopAbs_EDGE);
		TopoDS_Edge edge = TopoDS::Edge(exp.Current());
		Standard_Real u1, u2;
		Handle(Geom_Curve) crv = BRep_Tool::Curve(edge, u1, u2);
		TopoDS_Vertex v1, v2;
		TopExp::Vertices(temp, v1, v2);
		BRepBuilderAPI_MakeWire mw;
		mw.Add(BRepBuilderAPI_MakeEdge(crv, v1, v2));
		result = mw.Wire();
		return true;
	} else {
		return false;
	}
}

#ifdef USE_IFC4

#include <GC_MakeCircle.hxx>

bool IfcGeom::Kernel::convert(const IfcSchema::IfcIndexedPolyCurve* l, TopoDS_Wire& result) {
	
	IfcSchema::IfcCartesianPointList* point_list = l->Points();
	std::vector< std::vector<double> > coordinates;
	if (point_list->as<IfcSchema::IfcCartesianPointList2D>()) {
		coordinates = point_list->as<IfcSchema::IfcCartesianPointList2D>()->CoordList();
	} else if (point_list->as<IfcSchema::IfcCartesianPointList3D>()) {
		coordinates = point_list->as<IfcSchema::IfcCartesianPointList3D>()->CoordList();
	}

	std::vector<gp_Pnt> points;
	points.reserve(coordinates.size());
	for (std::vector< std::vector<double> >::const_iterator it = coordinates.begin(); it != coordinates.end(); ++it) {
		const std::vector<double>& coords = *it;
		points.push_back(gp_Pnt(
			coords.size() < 1 ? 0. : coords[0] * getValue(GV_LENGTH_UNIT),
			coords.size() < 2 ? 0. : coords[1] * getValue(GV_LENGTH_UNIT),
			coords.size() < 3 ? 0. : coords[2] * getValue(GV_LENGTH_UNIT)));
	}

	int max_index = points.size();

	BRepBuilderAPI_MakeWire w;

	IfcEntityList::ptr segments = l->Segments();
	for (IfcEntityList::it it = segments->begin(); it != segments->end(); ++it) {
		IfcUtil::IfcBaseClass* segment = *it;
		if (segment->is(IfcSchema::Type::IfcLineIndex)) {
			IfcSchema::IfcLineIndex* line = (IfcSchema::IfcLineIndex*) segment;
			std::vector<int> indices = *line;
			gp_Pnt previous;
			for (std::vector<int>::const_iterator jt = indices.begin(); jt != indices.end(); ++jt) {
				if (*jt < 1 || *jt > max_index) {
					throw IfcParse::IfcException("IfcIndexedPolyCurve index out of bounds for index " + boost::lexical_cast<std::string>(*jt));
				}
				const gp_Pnt& current = points[*jt - 1];
				if (jt != indices.begin()) {
					w.Add(BRepBuilderAPI_MakeEdge(previous, current));
				}
				previous = current;
			}
		} else if (segment->is(IfcSchema::Type::IfcArcIndex)) {
			IfcSchema::IfcArcIndex* arc = (IfcSchema::IfcArcIndex*) segment;
			std::vector<int> indices = *arc;
			if (indices.size() != 3) {
				throw IfcParse::IfcException("Invalid IfcArcIndex encountered");
			}
			for (int i = 0; i < 3; ++i) {
				const int& idx = indices[i];
				if (idx < 1 || idx > max_index) {
					throw IfcParse::IfcException("IfcIndexedPolyCurve index out of bounds for index " + boost::lexical_cast<std::string>(idx));
				}
			}
			const gp_Pnt& a = points[indices[0] - 1];
			const gp_Pnt& b = points[indices[1] - 1];
			const gp_Pnt& c = points[indices[2] - 1];
			Handle(Geom_Circle) circ = GC_MakeCircle(a, b, c).Value();
			w.Add(BRepBuilderAPI_MakeEdge(circ, a, c));
		} else {
			throw IfcParse::IfcException("Unexpected IfcIndexedPolyCurve segment of type " + IfcSchema::Type::ToString(segment->type()));
		}
	}
		
	result = w.Wire();
	return true;
}

#endif
