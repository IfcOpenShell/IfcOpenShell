#ifndef IFCGEOMMANIFOLDREPRESENTATION_H
#define IFCGEOMMANIFOLDREPRESENTATION_H

#include <manifold/manifold.h>

#include "../../../ifcgeom/ConversionResult.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

#include <optional>

namespace ifcopenshell {
namespace geometry {

struct IFC_GEOMLIBRARY_API ManifoldPart {
	manifold::MeshGL64 mesh;
	std::optional<manifold::Manifold> solid;

	ManifoldPart(const manifold::Manifold& s) {
        auto copy = s;
        copy.CalculateNormals(3);
        mesh = copy.GetMeshGL64();
        solid = s;	
	}

	ManifoldPart(const manifold::MeshGL64& s) : mesh(s) {}

	ManifoldPart(const manifold::MeshGL64& s, const manifold::Manifold& m) : mesh(s), solid(m) {}
};

class IFC_GEOMLIBRARY_API ManifoldShape : public IfcGeom::ConversionResultShape {
public:
	ManifoldShape() = default;
    explicit ManifoldShape(const manifold::Manifold& part);
    explicit ManifoldShape(const ManifoldPart& part);
	explicit ManifoldShape(ManifoldPart&& part);
	explicit ManifoldShape(const std::vector<ManifoldPart>& parts);
	explicit ManifoldShape(std::vector<ManifoldPart>&& parts);

	const std::vector<ManifoldPart>& parts() const { return parts_; }
	std::optional<manifold::Manifold> as_manifold() const;
	virtual std::string_view backend_id() const { return "manifold"; }

	virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const;
	virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const;

	virtual int surface_genus() const;
	virtual bool is_manifold() const;

	virtual int num_vertices() const;
	virtual int num_edges() const;
	virtual int num_faces() const;

	virtual double bounding_box(void*&) const;
	virtual std::pair<IfcGeom::OpaqueCoordinate<3>, IfcGeom::OpaqueCoordinate<3>> bounding_box() const;
	virtual void set_box(void* b);

	virtual IfcGeom::OpaqueNumber* length();
	virtual IfcGeom::OpaqueNumber* area();
	virtual IfcGeom::OpaqueNumber* volume();

	virtual IfcGeom::OpaqueCoordinate<3> position();
	virtual IfcGeom::OpaqueCoordinate<3> axis();
	virtual IfcGeom::OpaqueCoordinate<4> plane_equation();

	virtual std::vector<IfcGeom::ConversionResultShape*> convex_decomposition();
	virtual IfcGeom::ConversionResultShape* halfspaces();
	virtual IfcGeom::ConversionResultShape* box();
	virtual IfcGeom::ConversionResultShape* solid();
	virtual IfcGeom::ConversionResultShape* wrap_in_compound();

	virtual std::vector<IfcGeom::ConversionResultShape*> vertices();
	virtual std::vector<IfcGeom::ConversionResultShape*> edges();
	virtual std::vector<IfcGeom::ConversionResultShape*> facets();

	virtual IfcGeom::ConversionResultShape* add(IfcGeom::ConversionResultShape*);
	virtual IfcGeom::ConversionResultShape* subtract(IfcGeom::ConversionResultShape*);
	virtual IfcGeom::ConversionResultShape* intersect(IfcGeom::ConversionResultShape*);
	virtual IfcGeom::ConversionResultShape* concat(IfcGeom::ConversionResultShape*);

	virtual void map(IfcGeom::OpaqueCoordinate<4>& from, IfcGeom::OpaqueCoordinate<4>& to);
	virtual void map(const std::vector<IfcGeom::OpaqueCoordinate<4>>& from, const std::vector<IfcGeom::OpaqueCoordinate<4>>& to);
	virtual IfcGeom::ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const;

	virtual bool surface_area_along_direction(double tol, const ifcopenshell::geometry::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const;

private:
	std::vector<ManifoldPart> parts_;
};

}
}

#endif
