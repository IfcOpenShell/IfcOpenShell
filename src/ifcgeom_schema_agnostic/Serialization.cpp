#include "Serialization.h"

#include <boost/algorithm/string/case_conv.hpp>

namespace IfcGeom {
	extern IfcUtil::IfcBaseClass* tesselate_Ifc2x3(const TopoDS_Shape& shape, double deflection);
	extern IfcUtil::IfcBaseClass* tesselate_Ifc4(const TopoDS_Shape& shape, double deflection);
	extern IfcUtil::IfcBaseClass* serialise_Ifc2x3(const TopoDS_Shape& shape, bool advanced);
	extern IfcUtil::IfcBaseClass* serialise_Ifc4(const TopoDS_Shape& shape, bool advanced);
}

template <typename Fn, typename T>
IfcUtil::IfcBaseClass* execute_based_on_schema(Fn fn1, Fn fn2, const std::string& schema_name, const TopoDS_Shape& shape, T t) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	if (schema_name == "ifc2x3") {
		return fn1(shape, t);
	} else if (schema_name == "ifc4") {
		return fn2(shape, t);
	} else {
		throw IfcParse::IfcException("No geometry serialization available for " + schema_name);
	}
}

IfcUtil::IfcBaseClass* IfcGeom::tesselate(const std::string& schema_name, const TopoDS_Shape& shape, double deflection) {
	return execute_based_on_schema(IfcGeom::tesselate_Ifc2x3, IfcGeom::tesselate_Ifc4, schema_name, shape, deflection);
}

IfcUtil::IfcBaseClass* IfcGeom::serialise(const std::string& schema_name, const TopoDS_Shape& shape, bool advanced) {
	return execute_based_on_schema(IfcGeom::serialise_Ifc2x3, IfcGeom::serialise_Ifc4, schema_name, shape, advanced);
}