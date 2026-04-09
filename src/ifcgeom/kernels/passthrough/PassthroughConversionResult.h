#ifndef IFCGEOMPASSTHROUGHREPRESENTATION_H
#define IFCGEOMPASSTHROUGHREPRESENTATION_H

#include "../../../ifcgeom/ConversionResult.h"
#include "../../../ifcgeom/kernels/ifc_geomlibrary_api.h"

namespace ifcopenshell {
namespace geometry {

struct IFC_GEOMLIBRARY_API PassthroughPart {
	taxonomy::shell::ptr shell;
	taxonomy::matrix4::ptr matrix;
	bool manifold;
};

class IFC_GEOMLIBRARY_API PassthroughShape : public IfcGeom::ConversionResultShape {
public:
	PassthroughShape() = default;
	explicit PassthroughShape(const PassthroughPart& part);
	explicit PassthroughShape(PassthroughPart&& part);
	explicit PassthroughShape(const std::vector<PassthroughPart>& parts);
	explicit PassthroughShape(std::vector<PassthroughPart>&& parts);

	const std::vector<PassthroughPart>& parts() const { return parts_; }

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
	std::vector<PassthroughPart> parts_;
};

}
}

#endif
