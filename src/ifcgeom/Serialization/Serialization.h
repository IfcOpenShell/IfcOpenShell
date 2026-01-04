#include "../../ifcparse/express.h"

#include "ifc_geomserialization_api.h"

#include <TopoDS_Shape.hxx>

#include <string>

namespace IfcGeom {
IFC_GEOMSERIALIZATION_API express::Base tesselate(IfcParse::IfcFile& f, const TopoDS_Shape& shape, double deflection);
IFC_GEOMSERIALIZATION_API express::Base serialise(IfcParse::IfcFile& f, const TopoDS_Shape& shape, bool advanced);
} // namespace IfcGeom
