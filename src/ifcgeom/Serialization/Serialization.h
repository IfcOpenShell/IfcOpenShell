#include "../../ifcparse/express.h"

#include "ifc_geomserialization_api.h"

#include <TopoDS_Shape.hxx>

#include <string>

namespace IfcGeom {
IFC_GEOMSERIALIZATION_API express::Base tesselate(ifcopenshell::file& f, const TopoDS_Shape& shape, double deflection);
IFC_GEOMSERIALIZATION_API express::Base serialise(ifcopenshell::file& f, const TopoDS_Shape& shape, bool advanced);
} // namespace IfcGeom
