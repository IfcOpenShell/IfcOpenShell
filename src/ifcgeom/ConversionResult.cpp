#include "ConversionResult.h"
#include "IfcGeomRepresentation.h"

IfcGeom::Representation::Triangulation * IfcGeom::ConversionResultShape::Triangulate(const ifcopenshell::geometry::Settings& settings) const
{
	auto t = IfcGeom::Representation::Triangulation::empty(settings);
	static ifcopenshell::geometry::taxonomy::matrix4 iden;
	Triangulate(settings, iden, t, -1);
	return t;
}
