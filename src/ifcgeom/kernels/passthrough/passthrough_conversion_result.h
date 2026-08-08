#ifndef IFCGEOMPASSTHROUGHREPRESENTATION_H
#define IFCGEOMPASSTHROUGHREPRESENTATION_H

#include "../../../ifcgeom/conversion_result.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

namespace ifcopenshell {
namespace geom {

struct IFC_GEOMLIBRARY_API passthrough_part {
	taxonomy::shell::ptr shell;
	taxonomy::matrix4::ptr matrix;
	bool manifold;
};

class IFC_GEOMLIBRARY_API passthrough_shape : public ifcopenshell::geom::conversion_result_shape {
public:
	passthrough_shape() = default;
	explicit passthrough_shape(const passthrough_part& part);
	explicit passthrough_shape(passthrough_part&& part);
	explicit passthrough_shape(const std::vector<passthrough_part>& parts);
	explicit passthrough_shape(std::vector<passthrough_part>&& parts);

	const std::vector<passthrough_part>& parts() const { return parts_; }
	virtual std::string_view backend_id() const { return "passthrough"; }

	virtual void Triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, ifcopenshell::geom::Representation::triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
	virtual void Serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const;

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
	std::vector<passthrough_part> parts_;
};

}
}

#endif
