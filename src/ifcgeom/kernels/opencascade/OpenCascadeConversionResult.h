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

#ifndef IFCGEOMOPENCASCADEREPRESENTATION_H
#define IFCGEOMOPENCASCADEREPRESENTATION_H

#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepGProp_Face.hxx>

#include <Poly_Triangulation.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepTools.hxx>

#include <gp_GTrsf.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <GCPnts_QuasiUniformDeflection.hxx>

#include "../../../ifcgeom/ConversionResult.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

namespace ifcopenshell {
	namespace geom {

		using ifcopenshell::geom::opaque_coordinate;
		using ifcopenshell::geom::opaque_number;

		class IFC_GEOMLIBRARY_API open_cascade_shape : public ifcopenshell::geom::conversion_result_shape {
		public:
			open_cascade_shape(const TopoDS_Shape& shape);
			open_cascade_shape(TopoDS_Shape&& shape);

			const TopoDS_Shape& shape() const;
			operator const TopoDS_Shape& ();
			virtual std::string_view backend_id() const;

			virtual void Triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, ifcopenshell::geom::Representation::triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
			virtual void Serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const;

			virtual ifcopenshell::geom::conversion_result_shape* clone() const;

			virtual double bounding_box(void*&) const {
				throw std::runtime_error("Not implemented");
			}

			virtual void set_box(void*) {
				throw std::runtime_error("Not implemented");
			}

			virtual int surface_genus() const;
			virtual bool is_manifold() const;

			virtual int num_vertices() const;
			virtual int num_edges() const;
			virtual int num_faces() const;

			// @todo this must be something with a virtual dtor so that we can delete it.
			virtual std::pair<opaque_coordinate<3>, opaque_coordinate<3>> bounding_box() const;

			virtual opaque_number length();
			virtual opaque_number area();
			virtual opaque_number volume();

			virtual opaque_coordinate<3> position();
			virtual opaque_coordinate<3> axis();
			virtual opaque_coordinate<4> plane_equation();

			virtual std::vector<conversion_result_shape*> convex_decomposition();
			virtual conversion_result_shape* halfspaces();
			virtual conversion_result_shape* solid();
			virtual conversion_result_shape* box();
			virtual conversion_result_shape* wrap_in_compound();

			virtual std::vector<conversion_result_shape*> vertices();
			virtual std::vector<conversion_result_shape*> edges();
			virtual std::vector<conversion_result_shape*> facets();

			virtual conversion_result_shape* add(conversion_result_shape*);
			virtual conversion_result_shape* subtract(conversion_result_shape*);
			virtual conversion_result_shape* intersect(conversion_result_shape*);
			virtual conversion_result_shape* concat(conversion_result_shape*);

			virtual std::size_t map(opaque_coordinate<4>& from, opaque_coordinate<4>& to);
			virtual std::size_t map(const std::vector<opaque_coordinate<4>>& from, const std::vector<opaque_coordinate<4>>& to);
			virtual conversion_result_shape* moved(ifcopenshell::geom::taxonomy::matrix4::ptr) const;

			virtual bool surface_area_along_direction(double tol, const ifcopenshell::geom::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const;
		private:
			TopoDS_Shape shape_;
		};

	}
}

#endif
