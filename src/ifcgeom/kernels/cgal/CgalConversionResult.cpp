#include "CgalKernel.h"
#include "CgalConversionResult.h"

template <typename Precision>
void triangulate_helper(const cgal_shape_t, const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<Precision>* t, int surface_style_id) {
	throw std::runtime_error("Not implemented Triangulate()");
}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<float>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}

void IfcGeom::CgalShape::Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const {
	triangulate_helper(shape_, settings, place, t, surface_style_id);
}
