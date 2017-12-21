#include "IfcGeomIteratorImplementation.h"
#include "../ifcgeom_schema_agnostic/IteratorImplementation.h"

namespace IfcGeom {
	template class MAKE_TYPE_NAME(IteratorImplementation_)<float>;
	template class MAKE_TYPE_NAME(IteratorImplementation_)<double>;
}

#define MAKE_INIT_FN__(a, b) init_ ## a ## b
#define MAKE_INIT_FN_(a, b) MAKE_INIT_FN__(a, b)
#define MAKE_INIT_FN(t) MAKE_INIT_FN_(t, IfcSchema)

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

template <typename P>
void MAKE_INIT_FN(IteratorImplementation_)(IteratorFactoryImplementation<P>* mapping) {
	static const std::string schema_name = TOSTRING(IfcSchema);
	
	struct {
		IfcGeom::IteratorImplementation<P>* operator()(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file) const {
			return new IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<P>(settings, file);
		}
	} factory;

	mapping->bind(schema_name, factory);
}

template void MAKE_INIT_FN(IteratorImplementation_)<float>(IteratorFactoryImplementation<float>*);
template void MAKE_INIT_FN(IteratorImplementation_)<double>(IteratorFactoryImplementation<double>*);