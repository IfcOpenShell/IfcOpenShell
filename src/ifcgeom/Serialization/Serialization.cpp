#include "Serialization.h"

#include <boost/algorithm/string/case_conv.hpp>

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/algorithm/string/case_conv.hpp>

#define EXTERNAL_DEFS_1(r, data, elem) \
	IfcUtil::IfcBaseClass* BOOST_PP_CAT(tesselate_Ifc, elem)(const TopoDS_Shape& shape, double deflection);

#define EXTERNAL_DEFS_2(r, data, elem) \
	IfcUtil::IfcBaseClass* BOOST_PP_CAT(serialise_Ifc, elem)(const TopoDS_Shape& shape, bool advanced);

#define CONDITIONAL_CALL(r, data, elem) \
	if (schema_name_lower == BOOST_PP_STRINGIZE(BOOST_PP_CAT(elem,))) { \
		return BOOST_PP_CAT(METHOD_NAME, elem)(shape, arg_2); \
	}

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS_1, , SCHEMA_SEQ);
BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS_2, , SCHEMA_SEQ);

#define METHOD_NAME tesselate_Ifc

IfcUtil::IfcBaseClass* IfcGeom::tesselate(const std::string& schema_name, const TopoDS_Shape& shape, double arg_2) {
	// @todo an ugly hack to guarantee schemas are initialised.
	try {
		IfcParse::schema_by_name("IFC2X3");
	} catch (IfcParse::IfcException&) {}

	const std::string schema_name_lower = boost::to_lower_copy(schema_name.substr(3));

	BOOST_PP_SEQ_FOR_EACH(CONDITIONAL_CALL, , SCHEMA_SEQ);

	throw IfcParse::IfcException("No geometry serialization available for " + schema_name);
}

#undef METHOD_NAME
#define METHOD_NAME serialise_Ifc

IfcUtil::IfcBaseClass* IfcGeom::serialise(const std::string& schema_name, const TopoDS_Shape& shape, bool arg_2) {
	// @todo an ugly hack to guarantee schemas are initialised.
	try {
		IfcParse::schema_by_name("IFC2X3");
	} catch (IfcParse::IfcException&) {}

	const std::string schema_name_lower = boost::to_lower_copy(schema_name.substr(3));

	BOOST_PP_SEQ_FOR_EACH(CONDITIONAL_CALL, , SCHEMA_SEQ);

	throw IfcParse::IfcException("No geometry serialization available for " + schema_name);
}