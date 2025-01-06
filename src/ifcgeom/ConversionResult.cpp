#include "ConversionResult.h"
#include "IfcGeomRepresentation.h"

#include <iomanip>

IfcGeom::Representation::Triangulation * IfcGeom::ConversionResultShape::Triangulate(const ifcopenshell::geometry::Settings& settings) const
{
	auto t = IfcGeom::Representation::Triangulation::empty(settings);
	static ifcopenshell::geometry::taxonomy::matrix4 iden;
	Triangulate(settings, iden, t, -1, -1);
	return t;
}

using namespace ifcopenshell::geometry::taxonomy;

void IfcGeom::ConversionResult::append(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf) {
	placement_ = make<matrix4>(placement_->ccomponents() * trsf->ccomponents());
}

void IfcGeom::ConversionResult::prepend(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf) {
	placement_ = make<matrix4>(trsf->ccomponents() * placement_->ccomponents());
}

std::string IfcGeom::NumberNativeDouble::to_string() const {
	std::stringstream ss;
	ss << std::setprecision(std::numeric_limits<double>::digits10 + 1) << value_;
	return ss.str();
}
