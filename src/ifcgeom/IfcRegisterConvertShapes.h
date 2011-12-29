#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			return IfcGeom::convert((T*)l,r); \
		} catch (...) { } \
		Ifc::LogMessage("Error","Failed to convert:",l->entity); \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"