#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) { \
		return IfcGeom::convert((T*)l,r); \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"