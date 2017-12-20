#include "IfcGeomIteratorImplementation.h"
#include "../iterator/IteratorImplementation.h"

namespace IfcGeom {
	template class MAKE_TYPE_NAME(IteratorImplementation_)<float>;
	template class MAKE_TYPE_NAME(IteratorImplementation_)<double>;
}

#define MAKE_INIT_FN__(a, b) init_ ## a ## b
#define MAKE_INIT_FN_(a, b) MAKE_INIT_FN__(a, b)
#define MAKE_INIT_FN(t) MAKE_INIT_FN_(t, IfcSchema)

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

void MAKE_INIT_FN(IteratorImplementation_)() {
	static const std::string schema_name = TOSTRING(IfcSchema);
	
	struct {
		IfcGeom::IteratorImplementation<float>* operator()(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file) const {
			return new IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<float>(settings, file);
		}
	} factory_float;

	struct {
		IfcGeom::IteratorImplementation<double>* operator()(const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file) const {
			return new IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<double>(settings, file);
		}
	} factory_double;

	static Registrar< IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<float> > float_registration(schema_name, factory_float);
	static Registrar< IfcGeom::MAKE_TYPE_NAME(IteratorImplementation_)<double> > double_registration(schema_name, factory_double);
}