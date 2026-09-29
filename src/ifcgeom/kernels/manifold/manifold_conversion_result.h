#ifndef IFCGEOMMANIFOLDREPRESENTATION_H
#define IFCGEOMMANIFOLDREPRESENTATION_H

#include <manifold/manifold.h>

#include "../../../ifcgeom/conversion_result.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

#include <optional>

namespace ifcopenshell {
namespace geom {

struct IFC_GEOMLIBRARY_API manifold_part {
	manifold::MeshGL64 mesh;
	std::optional<manifold::Manifold> solid;

	manifold_part(const manifold::Manifold& s) {
        auto copy = s;
        copy.CalculateNormals(3);
        mesh = copy.GetMeshGL64();
        solid = s;
	}

	manifold_part(const manifold::MeshGL64& s) : mesh(s) {}

	manifold_part(const manifold::MeshGL64& s, const manifold::Manifold& m) : mesh(s), solid(m) {}
};

class IFC_GEOMLIBRARY_API manifold_shape : public ifcopenshell::geom::conversion_result_shape {
public:
	manifold_shape() = default;
    explicit manifold_shape(const manifold::Manifold& part);
    explicit manifold_shape(const manifold_part& part);
	explicit manifold_shape(manifold_part&& part);
	explicit manifold_shape(const std::vector<manifold_part>& parts);
	explicit manifold_shape(std::vector<manifold_part>&& parts);

	const std::vector<manifold_part>& parts() const { return parts_; }
	std::optional<manifold::Manifold> as_manifold() const;
	virtual std::string_view backend_id() const { return "manifold"; }

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
	std::vector<manifold_part> parts_;
};

}
}

#endif
