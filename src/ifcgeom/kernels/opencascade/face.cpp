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

#include <gp_Vec.hxx>
#include <gp_Dir.hxx>
#include <gp_Pln.hxx>
#include <Geom_Line.hxx>
#include <Geom_Plane.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Iterator.hxx>
#include <ShapeFix_Shape.hxx>
#include <ShapeFix_ShapeTolerance.hxx>
#include <BRep_Tool.hxx>
#include <TopTools_DataMapOfShapeInteger.hxx>
#include <BRepLib_FindSurface.hxx>
#include <ShapeExtend_MsgRegistrator.hxx>
#include <Message_Msg.hxx>
#include <ShapeFix_Edge.hxx>
#include <BRepPrimAPI_MakeHalfSpace.hxx>

#include "OpenCascadeKernel.h"
#include "face_definition.h"
#include "wire_utils.h"

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

bool OpenCascadeKernel::convert(const taxonomy::face::ptr face, TopoDS_Shape& result) {
	face_definition fd;

	const bool is_face_surface = false; /* todo */

	/*
	if (is_face_surface) {
		IfcSchema::IfcFaceSurface* fs = (IfcSchema::IfcFaceSurface*) l;
		fs->FaceSurface();
		// FIXME: Surfaces are interpreted as a TopoDS_Shape
		TopoDS_Shape surface_shape;
		if (!convert_shape(fs->FaceSurface(), surface_shape)) return false;

		// FIXME: Assert this obtaines the only face
		TopExp_Explorer exp(surface_shape, TopAbs_FACE);
		if (!exp.More()) return false;

		TopoDS_Face surface = TopoDS::Face(exp.Current());
		fd.surface() = BRep_Tool::Surface(surface);
	}
	*/

	const int num_bounds = face->children.size();
	int num_outer_bounds = 0;

	for (auto& bound : face->children) {
		if (bound->external.get_value_or(false)) {
			num_outer_bounds++;
		}
	}

	// The number of outer bounds should be one according to the schema. Also Open Cascade
	// expects this, but it is not strictly checked. Regardless, if the number is greater,
	// the face will still be processed as long as there are no holes. A compound of faces
	// is returned in that case.
	if (num_bounds > 1 && num_outer_bounds > 1 && num_bounds != num_outer_bounds) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", face->instance);
		return false;
	}

	if (num_outer_bounds > 1) {
		Logger::Message(Logger::LOG_WARNING, "Multiple outer boundaries for:", face->instance);
		fd.all_outer() = true;
	}

	TopTools_DataMapOfShapeInteger wire_senses;

	for (int process_interior = 0; process_interior <= 1; ++process_interior) {
		for (auto& bound : face->children) {
			bool same_sense = true; /* todo bound->Orientation(); */

			const bool is_interior =
				!bound->external.get_value_or(false) &&
				(num_bounds > 1) &&
				(num_outer_bounds < num_bounds);

			// The exterior face boundary is processed first
			if (is_interior == !process_interior) continue;

			TopoDS_Wire wire;
			if (faceset_helper_ && bound->is_polyhedron()) {
				if (!faceset_helper_->wire(bound, wire)) {
					Logger::Message(Logger::LOG_WARNING, "Face boundary loop not included", bound->instance);
					continue;
				}
			} else if (!convert(bound, wire)) {
				Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", bound->instance);
				return false;
			}

			if (!same_sense) {
				wire.Reverse();
			}

			wire_senses.Bind(wire.Oriented(TopAbs_FORWARD), same_sense ? TopAbs_FORWARD : TopAbs_REVERSED);

			fd.wires().emplace_back(wire);
		}
	}

	if (fd.wires().empty()) {
		Logger::Warning("Face with no boundaries", face->instance);
		return false;
	}

	if (fd.surface().IsNull()) {
		// Use the first wire to find a plane manually for polygonal wires
		const TopoDS_Wire& wire = fd.wires().front();
		if (is_polyhedron(wire)) {
			TopExp_Explorer exp(wire, TopAbs_EDGE);
			int count = 0;
			TopoDS_Edge edges[2];
			for (; exp.More(); exp.Next(), count++) {
				if (count < 2) {
					edges[count] = TopoDS::Edge(exp.Current());
				}
			}

			if (count == 3) {
				// Help Open Cascade by finding the plane more efficiently
				double _, __;
				Handle(Geom_Line) c1 = Handle(Geom_Line)::DownCast(BRep_Tool::Curve(edges[0], _, __));
				Handle(Geom_Line) c2 = Handle(Geom_Line)::DownCast(BRep_Tool::Curve(edges[1], _, __));

				const gp_Vec ab = c1->Position().Direction();
				const gp_Vec ac = c2->Position().Direction();
				const gp_Vec cross = ab.Crossed(ac);

				if (cross.SquareMagnitude() > ALMOST_ZERO) {
					const gp_Dir n = cross;
					fd.surface() = new Geom_Plane(c1->Position().Location(), n);
				}
			} else {
				gp_Pln pln;
				if (approximate_plane_through_wire(wire, pln, precision_)) {
					fd.surface() = new Geom_Plane(pln);
				}
			}
		}
	}

	if (fd.surface().IsNull()) {
		// BRepLib_FindSurface is used in case no surface is found or provided

		const TopoDS_Wire& wire = fd.wires().front();

		BRepLib_FindSurface fs(wire, precision_, true, true);
		if (fs.Found()) {
			fd.surface() = fs.Surface();
			ShapeFix_ShapeTolerance ftol;
			ftol.SetTolerance(wire, fs.ToleranceReached(), TopAbs_WIRE);
		}
	}

	TopTools_ListOfShape face_list;

	if (fd.surface().IsNull()) {
		// The set of wires is triangulated in case no surface can be found
		Logger::Message(Logger::LOG_WARNING, "Triangulating face boundaries for face", face->instance);

		if (fd.all_outer()) {
			for (const auto& w : fd.wires()) {
				TopTools_ListOfShape fl;
				triangulate_wire({ w }, fl);
				face_list.Append(fl);
			}
		} else {
			triangulate_wire(fd.wires(), face_list);
		}
	} else if (!fd.all_outer()) {
		BRepBuilderAPI_MakeFace mf(fd.surface(), fd.outer_wire());

		if (mf.IsDone()) {
			// Is this necessary
			TopoDS_Face f = mf.Face();
			mf.Init(f);

			for (auto it = fd.inner_wires().first; it != fd.inner_wires().second; ++it) {
				mf.Add(*it);
			}

			face_list.Append(mf.Face());
		}
	} else {
		for (const auto& w : fd.wires()) {
			BRepBuilderAPI_MakeFace mf(fd.surface(), w);
			if (mf.IsDone()) {
				face_list.Append(mf.Face());
			}
		}
	}

	if (!fd.surface().IsNull()) {
		// Some fixes for orientation and p-curves. If we have no surface, it
		// means the face has been triangulated in which case none of these
		// fixes are necessary.

		if (fd.surface()->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
			// In case of (non-planar) face surface, p-curves need to be computed.
			// For planar faces, Open Cascade generates p-curves on the fly.

			for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
				// Small chance there are multiple faces
				const TopoDS_Face& occ_face = TopoDS::Face(it.Value());
				for (TopExp_Explorer exp2(occ_face, TopAbs_EDGE); exp2.More(); exp2.Next()) {
					const TopoDS_Edge& edge = TopoDS::Edge(exp2.Current());
					ShapeFix_Edge fix_edge;
					fix_edge.FixAddPCurve(edge, occ_face, false, precision_);
				}
			}
		}

		for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
			const TopoDS_Face& occ_face = TopoDS::Face(it.Value());

			ShapeFix_Face sfs(TopoDS::Face(occ_face));
			TopTools_DataMapOfShapeListOfShape wire_map;
			sfs.FixOrientation(wire_map);

			TopoDS_Iterator jt(occ_face, false);
			for (; jt.More(); jt.Next()) {
				const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
				// tfk: @todo if wire_map contains w, I would assume wire_senses also contains w,
				// this is not the case in github issue #405.
				if (wire_map.IsBound(w) && wire_senses.IsBound(w)) {
					const TopTools_ListOfShape& shapes = wire_map.Find(w);
					TopTools_ListIteratorOfListOfShape kt(shapes);
					for (; kt.More(); kt.Next()) {
						// Apparently the wire got reversed, so register it with opposite orientation in the map
						wire_senses.Bind(kt.Value(), wire_senses.Find(w) == TopAbs_FORWARD ? TopAbs_REVERSED : TopAbs_FORWARD);
					}
				}
			}

			it.Value() = sfs.Face();
		}

		for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
			TopoDS_Face& occ_face = TopoDS::Face(it.Value());

			bool all_reversed = true;
			TopoDS_Iterator jt(occ_face, false);
			for (; jt.More(); jt.Next()) {
				const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
				if (!wire_senses.IsBound(w.Oriented(TopAbs_FORWARD)) || (w.Orientation() == wire_senses.Find(w.Oriented(TopAbs_FORWARD)))) {
					all_reversed = false;
				}
			}

			if (all_reversed) {
				occ_face.Reverse();
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	} else if (face_list.Extent() > 1) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
			TopoDS_Face& occ_face = TopoDS::Face(it.Value());
			builder.Add(compound, occ_face);
		}
		result = compound;
	} else {
		result = face_list.First();
	}

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::face::ptr face, IfcGeom::ConversionResults& results) {
	throw std::runtime_error("Root-level face not expected");
	/*

	// Root level faces are only encountered in case of half spaces
	// @todo this is not true, halfspace will be solid>face

	if (face->basis == nullptr) {
		Logger::Error("Half space without underlying surface:", face->instance);
		return false;
	}

	if (face->basis->kind() != taxonomy::PLANE) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported BaseSurface:", face->basis->instance);
		return false;
	}

	// @todo boundary
	const auto& m = ((taxonomy::geom_ptr)face->basis)->matrix.ccomponents();
	gp_Pln pln(convert_xyz2<gp_Pnt>(m.col(3)), convert_xyz2<gp_Dir>(m.col(2)));
	const gp_Pnt pnt = pln.Location().Translated(face->orientation.get_value_or(false) ? -pln.Axis().Direction() : pln.Axis().Direction());
	TopoDS_Shape shape = BRepPrimAPI_MakeHalfSpace(BRepBuilderAPI_MakeFace(pln), pnt).Solid();
	results.emplace_back(ConversionResult(
		face->instance->data().id(),
		new OpenCascadeShape(shape),
		face->surface_style
	));

	return true;
	*/
}
