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
#include <TColgp_SequenceOfPnt.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BOPAlgo_Operation.hxx>
#include <BRep_Builder.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>

#include "../../../ifcgeom/AbstractKernel.h" 

#include "../../../ifcgeom/IfcGeomElement.h" 
#include "../../../ifcgeom/IfcGeomRepresentation.h" 
#include "../../../ifcgeom/ConversionResult.h"

#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include "../../../ifcgeom/ifc_geom_api.h"

#include "../../../ifcgeom/taxonomy.h"
#include "../../../ifcgeom/ConversionSettings.h"

// @todo remove once merged to same ns.
using namespace ifcopenshell::geometry;

namespace IfcGeom {

class IFC_GEOM_API OpenCascadeKernel : public kernels::AbstractKernel {
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
		OpenCascadeKernel* kernel_;
		std::set<int> duplicates_;
		std::map<int, int> vertex_mapping_;
		std::map<std::pair<int, int>, TopoDS_Edge> edges_;
		double eps_;
		bool non_manifold_;
		
		void loop_(const taxonomy::loop::ptr ps, const std::function<void(int, int, bool)>& callback);

		/*
		bool construct(const IfcSchema::IfcCartesianPoint* cp, gp_Pnt* l);
		bool construct(const std::vector<double>& cp, gp_Pnt* l);

		const void* get_idx(const IfcSchema::IfcCartesianPoint* cp) {
			return cp;
		}

		const void* get_idx(const std::vector<double>& cp) {
			return &cp;
		}

		std::vector<const void*> get_idxs(const IfcSchema::IfcPolyLoop* lp);
		std::vector<const void*> get_idxs(const std::vector<int>& it);
		*/
	public:
		faceset_helper(OpenCascadeKernel* kernel, const taxonomy::shell::ptr l);
		~faceset_helper();

		bool non_manifold() const { return non_manifold_; }
		bool& non_manifold() { return non_manifold_; }
		double epsilon() const { return eps_; }
		
		bool edge(int A, int B, TopoDS_Edge& e);

		bool wire(const taxonomy::loop::ptr loop, TopoDS_Wire& wire);
		bool wires(const taxonomy::loop::ptr loop, TopTools_ListOfShape& wires);
	};

	faceset_helper* faceset_helper_;

	// @todo these should be moved to the mapping
	/*
	gp_Vec offset = gp_Vec{0.0, 0.0, 0.0};
	gp_Quaternion rotation = gp_Quaternion{};
	gp_Trsf offset_and_rotation = gp_Trsf();
	*/

	double precision_;

public:
	OpenCascadeKernel(const ConversionSettings& settings)
		: AbstractKernel("opencascade", settings)
		, faceset_helper_(nullptr)
		, precision_(settings.getValue(ConversionSettings::GV_PRECISION))
	{}

	bool convert(const taxonomy::extrusion::ptr, TopoDS_Shape&);
	bool convert(const taxonomy::face::ptr, TopoDS_Shape&);
	bool convert(const taxonomy::loop::ptr, TopoDS_Wire&);
	bool convert(const taxonomy::matrix4::ptr, gp_GTrsf&);
	bool convert(const taxonomy::shell::ptr, TopoDS_Shape&);
	bool convert(const taxonomy::solid::ptr, TopoDS_Shape&);
	bool convert(const taxonomy::bspline_surface::ptr bs, Handle(Geom_Surface) surf);

	virtual bool convert_impl(const taxonomy::face::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::solid::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::shell::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::extrusion::ptr, IfcGeom::ConversionResults&);
	virtual bool convert_impl(const taxonomy::boolean_result::ptr, IfcGeom::ConversionResults&);

	virtual bool convert_openings(const IfcUtil::IfcBaseEntity* entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
		const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes);

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

IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(tesselate_)(const TopoDS_Shape& shape, double deflection);
IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(serialise_)(const TopoDS_Shape& shape, bool advanced);

}
#endif
