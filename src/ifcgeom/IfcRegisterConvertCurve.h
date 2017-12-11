#include "IfcRegisterUndef.h"
#define CURVE(T) \
	if ( l->declaration().is(T::Class()) ) return convert((T*)l,r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"