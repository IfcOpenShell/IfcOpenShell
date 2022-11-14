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

#ifndef OPENCASCADEKERNEL_H
#define OPENCASCADEKERNEL_H

#include <cmath>

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
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

#include "../../../ifcgeom/kernel_agnostic/AbstractKernel.h" 

#include "../../../ifcgeom/schema_agnostic/IfcGeomElement.h" 
#include "../../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h" 
#include "../../../ifcgeom/schema_agnostic/ConversionResult.h"

#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include "../../../ifcgeom/schema_agnostic/ifc_geom_api.h"

#include "../../../ifcgeom/taxonomy.h"
#include "../../../ifcgeom/ConversionSettings.h"

// Define this in case you want to conserve memory usage at all cost. This has been
// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
// #define NO_CACHE

#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->data().id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->data().id()] = e;

#endif

namespace ifcopenshell {
namespace geometry {
namespace kernels {

	/*
	class IFC_GEOM_API POSTFIX_SCHEMA(Cache) {
	public:
#include "IfcRegisterCreateCache.h"
		std::map<int, TopoDS_Shape> Shape;
	};
	*/

	
	class IFC_GEOM_API OpenCascadeKernel : public AbstractKernel {
	private:
		// faceset_helper traverses the forward instance references of IfcConnectedFaceSet and then provides a mapping
		// M of (IfcCartesianPoint, IfcCartesianPoint) -> TopoDS_Edge, where M(a, b) is a partner of M(b, a), ie share
		// the same underlying edge but with orientation reversed. This then later speeds op the process of creating a
		// manifold Shell / Solid from this set of faces. Only IfcPolyLoop instances are used. Points within the tolerance
		// threshiold are merged, so consider points a, b, c, distance(a, b) < eps then M(a, b) = Null, M(a, b) = M(a, c).
		class faceset_helper {
		private:
			OpenCascadeKernel* kernel_;
			std::set<int> duplicates_;
			std::map<int, int> vertex_mapping_;
			std::map<std::pair<int, int>, TopoDS_Edge> edges_;
			double eps_;
			bool non_manifold_;

			void loop_(const taxonomy::loop* ps, const std::function<void(int, int, bool)>& callback);
		public:
			faceset_helper(OpenCascadeKernel* kernel, const taxonomy::shell* l);

			~faceset_helper();

			bool non_manifold() const { return non_manifold_; }
			bool& non_manifold() { return non_manifold_; }

			bool edge(int A, int B, TopoDS_Edge& e);

			bool wire(const taxonomy::loop* loop, TopoDS_Wire& wire);

			bool wires(const taxonomy::loop* loop, TopTools_ListOfShape& wires);

			double epsilon() const {
				return eps_;
			}
		};		

/*
#ifndef NO_CACHE
		POSTFIX_SCHEMA(Cache) cache;
#endif
*/

	faceset_helper* faceset_helper_;

	public:
		OpenCascadeKernel(ConversionSettings& settings)
			: AbstractKernel("opencascade", settings)
			, faceset_helper_(nullptr)
		{}		

		OpenCascadeKernel(const OpenCascadeKernel& other)
			: AbstractKernel("opencascade", other.settings_) {
			*this = other;
		}

		static double shape_volume(const TopoDS_Shape&);
		static double face_area(const TopoDS_Face&);
		static int count(const TopoDS_Shape& s, TopAbs_ShapeEnum t, bool unique = false);

		bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& shape);
		bool create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& shape);

		bool convert(const taxonomy::extrusion*, TopoDS_Shape&);
		bool convert(const taxonomy::face*, TopoDS_Shape&);
		bool convert(const taxonomy::loop*, TopoDS_Wire&);
		bool convert(const taxonomy::matrix4*, gp_GTrsf&);
		bool convert(const taxonomy::shell*, TopoDS_Shape&);

		bool boolean_operation(const TopoDS_Shape& a_, const TopTools_ListOfShape& b__, BOPAlgo_Operation op, TopoDS_Shape& result, double fuzziness = -1.);
		const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
		bool flatten_shape_list(const ifcopenshell::geometry::ConversionResults& shapes, TopoDS_Shape& result, bool fuse);
		bool is_compound(const TopoDS_Shape& shape);

		TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const taxonomy::matrix4& t);
		TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t);
		TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t);

		virtual bool convert_impl(const taxonomy::face*, ifcopenshell::geometry::ConversionResults&);
		virtual bool convert_impl(const taxonomy::shell*, ifcopenshell::geometry::ConversionResults&);
		virtual bool convert_impl(const taxonomy::extrusion*, ifcopenshell::geometry::ConversionResults&);
		virtual bool convert_impl(const taxonomy::boolean_result*, ifcopenshell::geometry::ConversionResults&);
	};

	/*
	IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(tesselate_)(const TopoDS_Shape& shape, double deflection);
	IfcUtil::IfcBaseClass* POSTFIX_SCHEMA(serialise_)(const TopoDS_Shape& shape, bool advanced);
	*/

	template <typename T, typename U>
	T convert_xyz(const U& u) {
		const auto& vs = u.ccomponents();
		return T(vs(0), vs(1), vs(2));
	}

	// @todo eliminate
	template <typename T, typename U>
	T convert_xyz2(const U& vs) {
		return T(vs(0), vs(1), vs(2));
	}

}
}
}

#endif
