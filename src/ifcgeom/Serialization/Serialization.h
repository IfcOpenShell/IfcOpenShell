#include "../../ifcparse/IfcBaseClass.h"

#include "ifc_geomserialization_api.h"

#include <TopoDS_Shape.hxx>

#include <string>

namespace IfcGeom {
	IFC_GEOMSERIALIZATION_API IfcUtil::IfcBaseClass* tesselate(const std::string& schema_name, const TopoDS_Shape& shape, double deflection);
	IFC_GEOMSERIALIZATION_API IfcUtil::IfcBaseClass* serialise(const std::string& schema_name, const TopoDS_Shape& shape, bool advanced);
}
