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

#ifndef IFCGEOMSMLIBREPRESENTATION_H
#define IFCGEOMSMLIBREPRESENTATION_H

#include "../../../ifcgeom/conversion_result.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

class SmBrep;

namespace ifcopenshell {
namespace geom {

/// Axis aligned box used by `bounding_box(void*&)` and `set_box(void*)`.
struct IFC_GEOMLIBRARY_API smlib_box {
	double min[3] = { 0., 0., 0. };
	double max[3] = { 0., 0., 0. };
	bool valid = false;
};

/// A geometry object produced by the SMLib kernel.
///
/// SMLib models exact boundary representations; triangles are only produced for
/// the parts of the pipeline that need them.
class IFC_GEOMLIBRARY_API smlib_shape : public ifcopenshell::geom::conversion_result_shape {
public:
	smlib_shape() = default;
	explicit smlib_shape(SmBrep* brep);
	smlib_shape(const smlib_shape& other);
	smlib_shape& operator=(const smlib_shape& other);
	~smlib_shape() override;

	/// The exact boundary representation, if the shape still carries one.
	SmBrep* brep() const { return brep_; }

	/// Whether the shape represents a closed volume.
	bool is_solid() const { return solid_; }
	void set_solid(bool solid) { solid_ = solid; }

	virtual std::string_view backend_id() const { return "smlib"; }

	virtual void triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, ifcopenshell::geom::triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
	virtual void serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const;

	virtual int surface_genus() const;
	virtual bool is_manifold() const;

	virtual int num_vertices() const;
	virtual int num_edges() const;
	virtual int num_faces() const;

	virtual double bounding_box(void*&) const;
	virtual std::pair<ifcopenshell::geom::opaque_coordinate<3>, ifcopenshell::geom::opaque_coordinate<3>> bounding_box() const;
	virtual void set_box(void* b);

	virtual ifcopenshell::geom::opaque_number length();
	virtual ifcopenshell::geom::opaque_number area();
	virtual ifcopenshell::geom::opaque_number volume();

	virtual ifcopenshell::geom::opaque_coordinate<3> position();
	virtual ifcopenshell::geom::opaque_coordinate<3> axis();
	virtual ifcopenshell::geom::opaque_coordinate<4> plane_equation();

	virtual std::vector<ifcopenshell::geom::conversion_result_shape*> convex_decomposition();
	virtual ifcopenshell::geom::conversion_result_shape* halfspaces();
	virtual ifcopenshell::geom::conversion_result_shape* box();
	virtual ifcopenshell::geom::conversion_result_shape* solid();
	virtual ifcopenshell::geom::conversion_result_shape* wrap_in_compound();

	virtual std::vector<ifcopenshell::geom::conversion_result_shape*> vertices();
	virtual std::vector<ifcopenshell::geom::conversion_result_shape*> edges();
	virtual std::vector<ifcopenshell::geom::conversion_result_shape*> facets();

	virtual ifcopenshell::geom::conversion_result_shape* add(ifcopenshell::geom::conversion_result_shape*);
	virtual ifcopenshell::geom::conversion_result_shape* subtract(ifcopenshell::geom::conversion_result_shape*);
	virtual ifcopenshell::geom::conversion_result_shape* intersect(ifcopenshell::geom::conversion_result_shape*);
	virtual ifcopenshell::geom::conversion_result_shape* concat(ifcopenshell::geom::conversion_result_shape*);

	virtual std::size_t map(ifcopenshell::geom::opaque_coordinate<4>& from, ifcopenshell::geom::opaque_coordinate<4>& to);
	virtual std::size_t map(const std::vector<ifcopenshell::geom::opaque_coordinate<4>>& from, const std::vector<ifcopenshell::geom::opaque_coordinate<4>>& to);
	virtual ifcopenshell::geom::conversion_result_shape* moved(ifcopenshell::geom::taxonomy::matrix4::ptr) const;

	virtual bool surface_area_along_direction(double tol, const ifcopenshell::geom::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const;

private:
	SmBrep* brep_ = nullptr;
	bool solid_ = false;
};

} // namespace geom
} // namespace ifcopenshell

#endif
