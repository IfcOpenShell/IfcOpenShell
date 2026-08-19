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

#ifndef CGAL_KERNEL_H
#define CGAL_KERNEL_H

#include "../../../ifcparse/logger.h"

/*
#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->entity->id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->entity->id()] = e;

#endif
*/

#ifdef IFOPSH_SIMPLE_KERNEL
#define cgal_kernel SimpleCgalKernel
#define create_cube create_cube_simple
#define create_polyhedron create_polyhedron_simple
#endif

#include "../../../ifcparse/macros.h"

#include "../../../ifcgeom/abstract_kernel.h"

#include "../../../ifcgeom/element.h"
#include "../../../ifcgeom/kernels/cgal/cgal_conversion_result.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

#include <CGAL/Polygon_2.h>

#include <cmath>

namespace ifcopenshell {
	namespace geom {
		namespace utils {
			IFC_GEOMLIBRARY_API CGAL::Polyhedron_3<kernel_> create_cube(double d);
			IFC_GEOMLIBRARY_API CGAL::Polyhedron_3<kernel_> create_cube(const kernel_::Point_3& lower, const kernel_::Point_3& upper);
			IFC_GEOMLIBRARY_API CGAL::Polyhedron_3<kernel_> create_polyhedron(std::list<cgal_face> &face_list, bool stitch_borders = false, logger& logger = ifcopenshell::logger::root());

#ifndef IFOPSH_SIMPLE_KERNEL
			IFC_GEOMLIBRARY_API CGAL::Polyhedron_3<kernel_> create_polyhedron(const CGAL::Nef_polyhedron_3<kernel_> &nef_polyhedron, logger& logger = ifcopenshell::logger::root());
			IFC_GEOMLIBRARY_API CGAL::Nef_polyhedron_3<kernel_> create_nef_polyhedron(std::list<cgal_face> &face_list, logger& logger = ifcopenshell::logger::root());
			IFC_GEOMLIBRARY_API CGAL::Nef_polyhedron_3<kernel_> create_nef_polyhedron(CGAL::Polyhedron_3<kernel_> &polyhedron, logger& logger = ifcopenshell::logger::root());
#endif
		}

		namespace kernels {

			class IFC_GEOMLIBRARY_API cgal_kernel : public abstract_kernel {
			private:
#ifndef IFOPSH_SIMPLE_KERNEL
				enum boolean_operand_preprocess {
					PP_MINKOWSKY_DILATE,
					PP_SNAP_POINTS_TO_FIRST_OPERAND,
					PP_SNAP_PLANES_TO_FIRST_OPERAND,
					PP_UNIFY_PLANES_INTERNALLY,
					PP_NONE
				};

				bool preprocess_boolean_operand(const express::base& log_reference, const std::list<cgal_polyhedron>& first_operands, const std::list<CGAL::Nef_polyhedron_3<kernel_>>& first_operands_nef, const std::list<kernel_::Plane_3>& all_operand_planes, const cgal_polyhedron& shape_const, CGAL::Nef_polyhedron_3<kernel_>& result, boolean_operand_preprocess proc);

				bool thin_solid(const CGAL::Nef_polyhedron_3<kernel_>& a, CGAL::Nef_polyhedron_3<kernel_>& result);

				CGAL::Nef_polyhedron_3<kernel_> create_precision_cube_() const {
					auto cc = utils::create_cube(settings_.get<settings::Precision>().get());
					return CGAL::Nef_polyhedron_3<kernel_>(cc);
				}
#endif
			public:

				cgal_kernel(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root())
					: abstract_kernel("cgal", settings, logger)
				{}

				virtual abstract_kernel* clone(ifcopenshell::logger& logger) const {
					return new cgal_kernel(settings(), logger);
				}

				virtual bool supports_boolean_operations() const {
#ifndef IFOPSH_SIMPLE_KERNEL
					return true;
#else
					return false;
#endif
				}

				bool convert(const taxonomy::extrusion::ptr, cgal_polyhedron&);
				bool convert(const taxonomy::face::ptr, std::list<cgal_face>&);
				bool convert(const taxonomy::loop::ptr, cgal_wire&);
				// bool convert(const taxonomy::matrix4::ptr, cgal_placement&);
				bool convert(const taxonomy::shell::ptr, cgal_polyhedron&);

				bool process_extrusion(const cgal_face& bottom_face, taxonomy::direction3::ptr direction, double height, cgal_polyhedron& shape);
				bool process_as_2d_polygon(const taxonomy::boolean_result::ptr br, std::list<CGAL::Polygon_2<kernel_>>& loops, double& z0, double& z1);
                bool process_as_2d_polygon(const std::list<std::list<std::pair<express::base, cgal_polyhedron>>>& operands, std::list<CGAL::Polygon_2<kernel_>>& loops, double& z0, double& z1);

				virtual bool convert_impl(const taxonomy::shell::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
				virtual bool convert_impl(const taxonomy::extrusion::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
				virtual bool convert_impl(const taxonomy::boolean_result::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
				virtual bool convert_impl(const taxonomy::solid::ptr, std::vector<ifcopenshell::geom::conversion_result>&);

				virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
					const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes);

#ifndef IFOPSH_SIMPLE_KERNEL
				CGAL::Nef_polyhedron_3<kernel_> precision_cube() const { return create_precision_cube_(); }
#endif
			};

		}
	}
}
#endif
