#include "IfcGeomIteratorImplementation.h"
#include "../ifcgeom_schema_agnostic/IteratorImplementation.h"

#define MAKE_INIT_FN__(a, b) init_ ## a ## b
#define MAKE_INIT_FN_(a, b) MAKE_INIT_FN__(a, b)
#define MAKE_INIT_FN(t) MAKE_INIT_FN_(t, IfcSchema)

namespace {
	struct MAKE_TYPE_NAME(factory_t) {
		IfcGeom::IteratorImplementation* operator()(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads) const {
			return new IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)(settings, file, filters, num_threads);
		}
	};
}

void MAKE_INIT_FN(IteratorImplementation_)(IteratorFactoryImplementation* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	MAKE_TYPE_NAME(factory_t) factory;
	mapping->bind(schema_name, factory);
}
