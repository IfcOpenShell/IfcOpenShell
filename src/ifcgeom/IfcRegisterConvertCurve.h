#include "IfcRegisterUndef.h"
#define CURVE(T) \
	if ( l->declaration().is(T::Class()) ) return convert(l->as<T>(), r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"