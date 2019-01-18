#include "IfcGeomIteratorImplementation.h"
#include "../../../ifcgeom/schema_agnostic/IteratorImplementation.h"

namespace IfcGeom {
	template class MAKE_TYPE_NAME(IteratorImplementation_)<float, float>;
	template class MAKE_TYPE_NAME(IteratorImplementation_)<float, double>;
	template class MAKE_TYPE_NAME(IteratorImplementation_)<double, double>;
}

#define MAKE_INIT_FN__(a, b) init_ ## a ## b
#define MAKE_INIT_FN_(a, b) MAKE_INIT_FN__(a, b)
#define MAKE_INIT_FN(t) MAKE_INIT_FN_(t, IfcSchema)

namespace {
	template <typename P, typename PP>
	struct MAKE_TYPE_NAME(factory_t) {
		IfcGeom::IteratorImplementation<P, PP>* operator()(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters) const {
			return new IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<P, PP>(settings, file, filters);
		}
	};
}

template <typename P, typename PP>
void MAKE_INIT_FN(IteratorImplementation_)(IteratorFactoryImplementation<P, PP>* mapping) {
	static const std::string schema_name = STRINGIFY(IfcSchema);
	MAKE_TYPE_NAME(factory_t)<P, PP> factory;
	mapping->bind(schema_name, factory);
}

template void MAKE_INIT_FN(IteratorImplementation_)<float, float>(IteratorFactoryImplementation<float, float>*);
template void MAKE_INIT_FN(IteratorImplementation_)<float, double>(IteratorFactoryImplementation<float, double>*);
template void MAKE_INIT_FN(IteratorImplementation_)<double, double>(IteratorFactoryImplementation<double, double>*);
