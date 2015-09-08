#include "IfcRegisterUndef.h"
#define FACE(T) \
	if ( l->declaration().is(T::Class()) ) return convert(l->as<T>(), r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"