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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcFace* inst) {
	auto face = taxonomy::make<taxonomy::face>();
	auto bounds = inst->Bounds();
	for (auto& bound : *bounds) {
		if (auto r = taxonomy::cast<taxonomy::loop>(map(bound->Bound()))) {
			if (!bound->Orientation()) {
				r->reverse();
			}
			// @todo check why loop sets external to true initially
			r->external = bound->declaration().is(IfcSchema::IfcFaceOuterBound::Class());
			/*
			// Make a copy in case we need immutability later for e.g. caching
			auto s = r->clone();
			((taxonomy::loop*)s)->external = true;
			delete r;
			r = s;
			*/
			face->children.push_back(r);
		}
	}

	auto face_surface = inst->as<IfcSchema::IfcFaceSurface>();

	if (face_surface) {
		face->basis = map(face_surface->FaceSurface());
	}

	if (face->children.empty()) {
#ifdef TAXONOMY_USE_NAKED_PTR
		delete face;
#endif
		return nullptr;
	}
	return face;
}

/*

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
#include "mapping.h"

#include "../ifcgeom_schema_agnostic/face_definition.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#define mapping POSTFIX_SCHEMA(mapping)

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcFace* l, TopoDS_Shape& result) {
	IfcSchema::IfcFaceBound::list::ptr bounds = inst->Bounds();

	util::face_definition fd;

	const bool is_face_surface = inst->declaration().is(IfcSchema::IfcFaceSurface::Class());

	if (is_face_surface) {
		IfcSchema::IfcFaceSurface* fs = (IfcSchema::IfcFaceSurface*) l;
		fs->FaceSurface();
		// FIXME: Surfaces are interpreted as a TopoDS_Shape
		TopoDS_Shape surface_shape;
		if (!convert_shape(fs->FaceSurface(), surface_shape)) return false;

		// FIXME: Assert this obtains the only face
		TopExp_Explorer exp(surface_shape, TopAbs_FACE);
		if (!exp.More()) return false;

		TopoDS_Face surface = TopoDS::Face(exp.Current());
		fd.surface() = BRep_Tool::Surface(surface);
	}
	
	const int num_bounds = bounds->size();
	int num_outer_bounds = 0;

	for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
		IfcSchema::IfcFaceBound* bound = *it;
		if (bound->declaration().is(IfcSchema::IfcFaceOuterBound::Class())) num_outer_bounds ++;
	}

	// The number of outer bounds should be one according to the schema. Also Open Cascade
	// expects this, but it is not strictly checked. Regardless, if the number is greater,
	// the face will still be processed as long as there are no holes. A compound of faces
	// is returned in that case.
	if (num_bounds > 1 && num_outer_bounds > 1 && num_bounds != num_outer_bounds) {
		Logger::Message(Logger::LOG_ERROR, "Invalid configuration of boundaries for:", l);
		return false;
	}

	if (num_outer_bounds > 1) {
		Logger::Message(Logger::LOG_WARNING, "Multiple outer boundaries for:", l);
		fd.all_outer() = true;
	}

	TopTools_DataMapOfShapeInteger wire_senses;
	
	for (int process_interior = 0; process_interior <= 1; ++process_interior) {
		for (IfcSchema::IfcFaceBound::list::it it = bounds->begin(); it != bounds->end(); ++it) {
			IfcSchema::IfcFaceBound* bound = *it;
			IfcSchema::IfcLoop* loop = bound->Bound();

			bool same_sense = bound->Orientation();
			const bool is_interior =
				!bound->declaration().is(IfcSchema::IfcFaceOuterBound::Class()) &&
				(num_bounds > 1) &&
				(num_outer_bounds < num_bounds);

			// The exterior face boundary is processed first
			if (is_interior == !process_interior) continue;

			TopTools_ListOfShape wires;
			TopoDS_Wire wire;
			if (faceset_helper_ && loop->as<IfcSchema::IfcPolyLoop>()) {
				if (!faceset_helper_->wires(loop->as<IfcSchema::IfcPolyLoop>(), wires)) {
					Logger::Message(Logger::LOG_WARNING, "Face boundary loop not included", loop);
					continue;
				}
			} else {
				if (convert_wire(loop, wire)) {
					wires.Append(wire);
				} else {
					Logger::Message(Logger::LOG_ERROR, "Failed to process face boundary loop", loop);
					return false;
				}
			}

			if (wires.Size() > 1) {
				Logger::Message(Logger::LOG_WARNING, "Face loop definition results in " + std::to_string(wires.Size()) + " loops", loop);
				if (!is_interior) {
					fd.all_outer() = true;
				}
			}

			for (auto& w : wires) {
				if (!same_sense) {
					w.Reverse();
				}

				wire_senses.Bind(w.Oriented(TopAbs_FORWARD), same_sense ? TopAbs_FORWARD : TopAbs_REVERSED);

				fd.wires().emplace_back(TopoDS::Wire(w));
			}
		}
	}

	if (fd.wires().empty()) {
		Logger::Warning("Face with no boundaries", l);
		return false;
	}

	if (fd.surface().IsNull()) {
		// Use the first wire to find a plane manually for polygonal wires
		const TopoDS_Wire& wire = fd.wires().front();
		if (util::is_polyhedron(wire)) {
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
				if (util::approximate_plane_through_wire(wire, pln, getValue(GV_PRECISION))) {
					fd.surface() = new Geom_Plane(pln);
				}
			}
		}
	}	

	if (fd.surface().IsNull()) {
		// BRepLib_FindSurface is used in case no surface is found or provided
		
		const TopoDS_Wire& wire = fd.wires().front();

		BRepLib_FindSurface fs(wire, getValue(GV_PRECISION), true, true);
		if (fs.Found()) {
			fd.surface() = fs.Surface();
			ShapeFix_ShapeTolerance ftol;
			ftol.SetTolerance(wire, fs.ToleranceReached(), TopAbs_WIRE);
		}
	}

	TopTools_ListOfShape face_list;

	if (fd.surface().IsNull()) {
		// The set of wires is triangulated in case no surface can be found
		Logger::Message(Logger::LOG_WARNING, "Triangulating face boundaries for face", l);

		if (fd.all_outer()) {
			for (const auto& w : fd.wires()) {
				TopTools_ListOfShape fl;
				auto r = util::triangulate_wire({ w }, fl);
				if (r == util::TRIANGULATE_WIRE_FAIL) {
					continue;
				}
				face_list.Append(fl);
				if (faceset_helper_ && r == util::TRIANGULATE_WIRE_NON_MANIFOLD) {
					faceset_helper_->non_manifold() = true;
				}
			}
		} else {
			auto r = util::triangulate_wire(fd.wires(), face_list);
			if (r != util::TRIANGULATE_WIRE_FAIL) {
				if (faceset_helper_ && r == util::TRIANGULATE_WIRE_NON_MANIFOLD) {
					faceset_helper_->non_manifold() = true;
				}
			}
		}
	} else if (!fd.all_outer()) {
		BRepBuilderAPI_MakeFace mf(fd.surface(), fd.outer_wire());
		TopoDS_Face f = mf.Face();

		if (mf.IsDone()) {
			if (std::distance(fd.inner_wires().first, fd.inner_wires().second)) {
				mf.Init(f);

				for (auto it = fd.inner_wires().first; it != fd.inner_wires().second; ++it) {
					mf.Add(*it);
				}

				face_list.Append(mf.Face());
			} else {
				face_list.Append(f);
			}
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
				ShapeFix_Shape sfs(it.Value());

				Handle(ShapeExtend_MsgRegistrator) msg;
				msg = new ShapeExtend_MsgRegistrator;
				sfs.SetMsgRegistrator(msg);

				sfs.Perform();
				it.Value() = sfs.Shape();
				
				ShapeExtend_DataMapIteratorOfDataMapOfShapeListOfMsg jt(msg->MapShape());
				for (; jt.More(); jt.Next()) {
					Message_ListIteratorOfListOfMsg kt(jt.Value());
					for (; kt.More(); kt.Next()) {
						char* c = new char[kt.Value().Value().LengthOfCString() + 1];
						kt.Value().Value().ToUTF8CString(c);
						Logger::Notice(c, l);
						delete[] c;
					}
				}
			}			
		}

		for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
			const TopoDS_Face& face = TopoDS::Face(it.Value());
			
			ShapeFix_Face sfs(TopoDS::Face(face));
			TopTools_DataMapOfShapeListOfShape wire_map;
			sfs.FixOrientation(wire_map);

			TopoDS_Iterator jt(face, false);
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
			TopoDS_Face& face = TopoDS::Face(it.Value());

			bool all_reversed = true;
			TopoDS_Iterator jt(face, false);
			for (; jt.More(); jt.Next()) {
				const TopoDS_Wire& w = TopoDS::Wire(jt.Value());
				if (!wire_senses.IsBound(w.Oriented(TopAbs_FORWARD)) || (w.Orientation() == wire_senses.Find(w.Oriented(TopAbs_FORWARD)))) {
					all_reversed = false;
				}
			}

			if (all_reversed) {
				face.Reverse();
			}
		}
	}

	if (face_list.Extent() == 0) {
		return false;
	}  else if (face_list.Extent() > 1) {
		TopoDS_Compound compound;
		BRep_Builder builder;
		builder.MakeCompound(compound);
		for (TopTools_ListIteratorOfListOfShape it(face_list); it.More(); it.Next()) {
			TopoDS_Face& face = TopoDS::Face(it.Value());
			builder.Add(compound, face);
		}
		result = compound;
	} else {
		result = face_list.First();
	}

	return true;
}

*/