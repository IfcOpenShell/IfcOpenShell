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
#include <Geom_BSplineSurface.hxx>
#include <Geom_CylindricalSurface.hxx>
#include <Geom_SphericalSurface.hxx>
#include <Geom_ToroidalSurface.hxx>
#include <BRepAdaptor_CompCurve.hxx>
#include <Approx_Curve3d.hxx>
#include <Standard_Version.hxx>
#include <Geom_SurfaceOfLinearExtrusion.hxx>
#include <Geom_SurfaceOfRevolution.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>

#if OCC_VERSION_HEX < 0x70600
#include <BRepAdaptor_HCompCurve.hxx>
#endif

#include "OpenCascadeKernel.h"
#include "face_definition.h"
#include "wire_utils.h"
#include "base_utils.h"

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;


namespace {
	struct surface_creation_visitor {
		OpenCascadeKernel* kernel;
		Handle(Geom_Surface) result;

		Handle(Geom_Surface) operator()(const taxonomy::bspline_surface::ptr& bs) {
			auto& cps = bs->control_points;
			if (!cps.size() || !cps[0].size()) {
				throw std::runtime_error("Empty control point array");
			}

			auto& uknots = bs->knots[0];
			auto& vknots = bs->knots[1];
			auto& umults = bs->multiplicities[0];
			auto& vmults = bs->multiplicities[1];

			TColgp_Array2OfPnt Poles(0, (int)cps.size() - 1, 0, (int)cps[0].size() - 1);
			TColStd_Array1OfReal UKnots(0, (int)uknots.size() - 1);
			TColStd_Array1OfReal VKnots(0, (int)vknots.size() - 1);
			TColStd_Array1OfInteger UMults(0, (int)umults.size() - 1);
			TColStd_Array1OfInteger VMults(0, (int)vmults.size() - 1);
			Standard_Integer UDegree = bs->degree[0];
			Standard_Integer VDegree = bs->degree[1];

			int i = 0, j;
			for (auto it = cps.begin(); it != cps.end(); ++it, ++i) {
				j = 0;
				for (auto jt = (*it).begin(); jt != (*it).end(); ++jt, ++j) {
					Poles(i, j) = kernel->convert_xyz<gp_Pnt>(**jt);
				}
			}
			i = 0;
			for (std::vector<double>::const_iterator it = uknots.begin(); it != uknots.end(); ++it, ++i) {
				UKnots(i) = *it;
			}
			i = 0;
			for (std::vector<double>::const_iterator it = vknots.begin(); it != vknots.end(); ++it, ++i) {
				VKnots(i) = *it;
			}
			i = 0;
			for (std::vector<int>::const_iterator it = umults.begin(); it != umults.end(); ++it, ++i) {
				UMults(i) = *it;
			}
			i = 0;
			for (std::vector<int>::const_iterator it = vmults.begin(); it != vmults.end(); ++it, ++i) {
				VMults(i) = *it;
			}
			return result = Handle(Geom_Surface)(new Geom_BSplineSurface(Poles, UKnots, VKnots, UMults, VMults, UDegree, VDegree));
		}

		Handle(Geom_Surface) operator()(const taxonomy::plane::ptr& p) {
			const auto& m = p->matrix->ccomponents();
			return result = Handle(Geom_Surface)(new Geom_Plane(
				OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2))));
		}

		Handle(Geom_Surface) operator()(const taxonomy::cylinder::ptr& c) {
			const auto& m = c->matrix->ccomponents();
			return result = Handle(Geom_Surface)(new Geom_CylindricalSurface(gp_Ax3(
				OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(0))
			), c->radius));
		}

		Handle(Geom_Surface) operator()(const taxonomy::sphere::ptr& s) {
			const auto& m = s->matrix->ccomponents();
			return result = Handle(Geom_Surface)(new Geom_SphericalSurface(gp_Ax3(
				OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(0))
			), s->radius));
		}

		Handle(Geom_Surface) operator()(const taxonomy::torus::ptr& t) {
			const auto& m = t->matrix->ccomponents();
			return result = Handle(Geom_Surface)(new Geom_ToroidalSurface(gp_Ax3(
				OpenCascadeKernel::convert_xyz2<gp_Pnt>(m.col(3)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(2)),
				OpenCascadeKernel::convert_xyz2<gp_Dir>(m.col(0))
			), t->radius1, t->radius2));
		}

		TopoDS_Wire get_edges_as_wire(const taxonomy::item::ptr& i) {
			// It's a bit more convenient to use high level BRepPrimAPI calls that operate on
			// topology. On a single edge that will create a Geom_TrimmedCurve for us.
			auto crv_or_wire = kernel->convert_curve(i);
			if (crv_or_wire.which() == 1) {
				const auto& w = boost::get<TopoDS_Wire>(crv_or_wire);
				return w;
			} else {
				throw std::runtime_error("Unexpected curve evaluation");
			}
		}

		Handle(Geom_Curve) get_curve(const taxonomy::item::ptr& i) {
			// @todo unify with trimmed curve handling
			auto crv_or_wire = kernel->convert_curve(i);
			if (crv_or_wire.which() == 0) {
				return boost::get<Handle(Geom_Curve)>(crv_or_wire);
			} else {
				// @todo
				const double precision_ = 1.e-5;
				Logger::Warning("Approximating BasisCurve due to possible discontinuities", i->instance);
				const auto& w = boost::get<TopoDS_Wire>(crv_or_wire);
#if OCC_VERSION_HEX < 0x70600
				BRepAdaptor_CompCurve cc(w, true);
				Handle(Adaptor3d_HCurve) hcc = Handle(Adaptor3d_HCurve)(new BRepAdaptor_HCompCurve(cc));
#else
				auto hcc = new BRepAdaptor_CompCurve(w, true);
#endif
				// @todo, arbitrary numbers here, note they cannot be too high as contiguous memory is allocated based on them.
				Approx_Curve3d approx(hcc, precision_, GeomAbs_C0, 10, 10);
				return approx.Curve();
			}
		}

		Handle(Geom_Surface) operator()(const taxonomy::extrusion::ptr& e) {
			auto crv = get_curve(e->basis);
			return result = Handle(Geom_Surface)(new Geom_SurfaceOfLinearExtrusion(
				crv,
				OpenCascadeKernel::convert_xyz<gp_Dir>(*e->direction)
			));
		}

		Handle(Geom_Surface) operator()(const taxonomy::revolve::ptr& e) {
			gp_Ax1 ax(
				OpenCascadeKernel::convert_xyz<gp_Pnt>(*e->axis_origin),
				OpenCascadeKernel::convert_xyz<gp_Dir>(*e->direction));

			if (e->basis && (e->basis->kind() == taxonomy::EDGE || (e->basis->kind() == taxonomy::LOOP && taxonomy::cast<taxonomy::loop>(e->basis)->children.size() == 1))) {
				auto e_basis = e->basis;
				if ((e->basis->kind() == taxonomy::LOOP)) {
					e_basis = taxonomy::cast<taxonomy::loop>(e->basis)->children[0];
				}
				auto w = get_edges_as_wire(e_basis);
				TopoDS_Shape shp = BRepPrimAPI_MakeRevol(w, ax);
				TopExp_Explorer exp(shp, TopAbs_FACE);
				if (exp.More()) {
					Handle(Geom_Surface) surf = BRep_Tool::Surface(TopoDS::Face(exp.Current()));
					exp.Next();
					if (!exp.More()) {
						return result = surf;
					}
				}
				// fall back to approach below
			}

			auto crv = get_curve(e->basis);
			return result = Handle(Geom_Surface)(new Geom_SurfaceOfRevolution(
				crv, ax	
			));
		}
	};
}

Handle(Geom_Surface) OpenCascadeKernel::convert_surface(const taxonomy::ptr surface) {
	surface_creation_visitor v{ this };
	if (dispatch_surface_creation<surface_creation_visitor, 0>::dispatch(surface, v)) {
		return v.result;
	} else {
		throw std::runtime_error("No surface created");
	}
}

bool OpenCascadeKernel::convert(const taxonomy::face::ptr face, TopoDS_Shape& result, bool reversed_surface) {
#ifdef IFOPSH_DEBUG
	std::ostringstream oss;
	face->print(oss);
	auto osss = oss.str();
	std::wcout << osss.c_str() << std::endl;
#endif

	face_definition fd;

	if (face->basis) {
		fd.surface() = convert_surface(face->basis);
	}

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
				auto r = triangulate_wire({ w }, fl);
				if (r == util::TRIANGULATE_WIRE_FAIL) {
					continue;
				}
				face_list.Append(fl);
				if (faceset_helper_ && r == util::TRIANGULATE_WIRE_NON_MANIFOLD) {
					faceset_helper_->non_manifold() = true;
				}
			}
		} else {
			auto r = triangulate_wire(fd.wires(), face_list);
			if (r != util::TRIANGULATE_WIRE_FAIL) {
				if (faceset_helper_ && r == util::TRIANGULATE_WIRE_NON_MANIFOLD) {
					faceset_helper_->non_manifold() = true;
				}
			}
		}
	} else if (!fd.all_outer()) {
		auto surf = fd.surface();
		if (reversed_surface) {
			surf = surf->UReversed();
		}
		BRepBuilderAPI_MakeFace mf(surf, fd.outer_wire());

		if (mf.IsDone()) {
			// Is this necessary
			TopoDS_Face f = mf.Face();
			if (std::distance(fd.inner_wires().first, fd.inner_wires().second)) {
				mf.Init(f);

				for (auto it = fd.inner_wires().first; it != fd.inner_wires().second; ++it) {
					mf.Add(*it);
				}

				face_list.Append(mf.Face());
			} else {
				face_list.Append(f);
			}
		} else {
			Logger::Error("Internal error in face creation");
			return false;
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
						char* c = new char[kt.Value().Original().LengthOfCString() + 1];
						kt.Value().Original().ToUTF8CString(c);
						std::string message = c;
						delete[] c;
#if OCC_VERSION_MAJOR==7 && OCC_VERSION_MINOR == 7
						if (!reversed_surface && !fd.surface().IsNull() && fd.surface()->IsUPeriodic() && message == "Unknown message invoked with the keyword FixAdvFace.FixOrientation.MSG0") {
							Logger::Notice("Detected reversed wire, reattempting with reversed basis surface");
							TopoDS_Face reversed_result;
							convert(face, reversed_result, true);
							result = reversed_result;
							return true;
						} else
#endif
							Logger::Warning(message, face->instance);
					}
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

	if (face->matrix) {
		result = apply_transformation(result, *face->matrix);
	}

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::face::ptr face, IfcGeom::ConversionResults& results) {
	TopoDS_Shape shape;
	if (!convert(face, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		face->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		new OpenCascadeShape(shape),
		face->surface_style
	));
	return true;
}
