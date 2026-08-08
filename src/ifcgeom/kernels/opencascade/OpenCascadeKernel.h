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

#ifndef IFCGEOM_H
#define IFCGEOM_H

#include <cmath>
#include <array>

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Quaternion.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>
#include <BOPAlgo_Operation.hxx>
#include <BRep_Builder.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>

#include "../../../ifcgeom/AbstractKernel.h" 

#include "../../../ifcgeom/IfcGeomElement.h" 
#include "../../../ifcgeom/IfcGeomRepresentation.h" 
#include "../../../ifcgeom/ConversionResult.h"

#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

#include "../../../ifcgeom/taxonomy.h"
#include "../../../ifcgeom/ConversionSettings.h"

namespace {
template <typename Fn>
bool handle_occt_exception(Fn&& fn) {
    try {
        return std::forward<Fn>(fn)();
    } catch (const Standard_Failure& e) {
        if (e.GetMessageString() && strlen(e.GetMessageString())) {
            throw std::runtime_error(e.GetMessageString());
		} else {
            throw std::runtime_error("Unknown error creating geometry");
		}
    }
}
}

namespace ifcopenshell::geom {

class IFC_GEOMLIBRARY_API open_cascade_kernel : public ifcopenshell::geom::kernels::abstract_kernel {
private:

	/*
	faceset_helper traverses the forward instance references of IfcConnectedFaceSet and then provides a mapping
	M of (IfcCartesianPoint, IfcCartesianPoint) -> TopoDS_Edge, where M(a, b) is a partner of M(b, a), ie share
	the same underlying edge but with orientation reversed. This then later speeds op the process of creating a
	manifold Shell / Solid from this set of faces. Only IfcPolyLoop instances are used. Points within the tolerance
	threshiold are merged, so consider points a, b, c, distance(a, b) < eps then M(a, b) = Null, M(a, b) = M(a, c).
	*/

	class faceset_helper {
	private:
		open_cascade_kernel* kernel_;
		std::set<int> duplicates_;
		std::map<int, int> vertex_mapping_;
		std::map<std::pair<int, int>, TopoDS_Edge> edges_;
		double eps_;
		bool non_manifold_;
		
		void loop_(const ifcopenshell::geom::taxonomy::loop::ptr ps, const std::function<void(int, int, bool)>& callback);
	public:
		faceset_helper(open_cascade_kernel* kernel, const ifcopenshell::geom::taxonomy::shell::ptr l);
		~faceset_helper();

		bool non_manifold() const { return non_manifold_; }
		bool& non_manifold() { return non_manifold_; }
		double epsilon() const { return eps_; }
		
		bool edge(int A, int B, TopoDS_Edge& e);

		bool wire(const ifcopenshell::geom::taxonomy::loop::ptr loop, TopoDS_Wire& wire);
		bool wires(const ifcopenshell::geom::taxonomy::loop::ptr loop, NCollection_List<TopoDS_Shape>& wires);
	};

	faceset_helper* faceset_helper_;

	double precision_;
public:
	open_cascade_kernel(const ifcopenshell::geom::settings& settings, ::logger& logger = ::logger::root())
		: abstract_kernel("opencascade", settings, logger)
		, faceset_helper_(nullptr)
		, precision_(settings.get<ifcopenshell::geom::settings::Precision>().get())
	{}

	virtual abstract_kernel* clone(::logger& logger) const {
		return new open_cascade_kernel(settings(), logger);
	}

	virtual bool supports_boolean_operations() const { return true; }

	bool convert(const ifcopenshell::geom::taxonomy::extrusion::ptr, TopoDS_Shape&);
	bool convert(const ifcopenshell::geom::taxonomy::face::ptr, TopoDS_Shape&, bool reversed_surface = false);
	bool convert(const ifcopenshell::geom::taxonomy::loop::ptr, TopoDS_Wire&);
	bool convert(const ifcopenshell::geom::taxonomy::matrix4::ptr, gp_GTrsf&);
	bool convert(const ifcopenshell::geom::taxonomy::shell::ptr, TopoDS_Shape&);
	bool convert(const ifcopenshell::geom::taxonomy::solid::ptr, TopoDS_Shape&);
	bool convert(const ifcopenshell::geom::taxonomy::loft::ptr, TopoDS_Shape&);
	bool convert(const ifcopenshell::geom::taxonomy::bspline_surface::ptr bs, Handle(Geom_Surface) surf);
	bool convert(const ifcopenshell::geom::taxonomy::sweep_along_curve::ptr, TopoDS_Shape&);

	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::edge::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::loop::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::face::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::solid::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::shell::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::extrusion::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::revolve::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::boolean_result::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::loft::ptr, ifcopenshell::geom::conversion_results&);
	virtual bool convert_impl(const ifcopenshell::geom::taxonomy::sweep_along_curve::ptr, ifcopenshell::geom::conversion_results&);

	virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<ifcopenshell::geom::taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
		const ifcopenshell::geom::conversion_results& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, ifcopenshell::geom::conversion_results& cut_shapes);
	virtual bool unify_shapes(const ifcopenshell::geom::conversion_results& input, ifcopenshell::geom::conversion_results& output);

	typedef std::variant<boost::blank, Handle(Geom_Curve), TopoDS_Wire> curve_creation_visitor_result_type;
	curve_creation_visitor_result_type convert_curve(const ifcopenshell::geom::taxonomy::ptr);
	Handle(Geom_Surface) convert_surface(const ifcopenshell::geom::taxonomy::ptr);

	template <typename T, typename U>
	static T convert_xyz(const U& u) {
		const auto& vs = u.ccomponents();
		return T(vs(0), vs(1), vs(2));
	}

	// @todo eliminate
	template <typename T, typename U>
	static T convert_xyz2(const U& vs) {
		return T(vs(0), vs(1), vs(2));
	}
};

express::base POSTFIX_SCHEMA(tesselate_)(const TopoDS_Shape& shape, double deflection);
express::base POSTFIX_SCHEMA(serialise_)(const TopoDS_Shape& shape, bool advanced);

}
#endif
