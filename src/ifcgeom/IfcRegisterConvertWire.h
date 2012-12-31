#include "IfcRegisterUndef.h"
#define WIRE(T) \
	if ( l->is(T::Class()) ) return convert((T*)l,r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"