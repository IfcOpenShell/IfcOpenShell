#include "../../ifcparse/IfcBaseClass.h"

#include "../../ifcgeom/ifc_geom_api.h"

#include <TopoDS_Shape.hxx>

#include <string>

namespace IfcGeom {
	IFC_GEOM_API IfcUtil::IfcBaseClass* tesselate(const std::string& schema_name, const TopoDS_Shape& shape, double deflection);
	IFC_GEOM_API IfcUtil::IfcBaseClass* serialise(const std::string& schema_name, const TopoDS_Shape& shape, bool advanced);
}
