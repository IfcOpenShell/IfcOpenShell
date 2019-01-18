#include "IfcRegisterUndef.h"
#define WIRE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return convert((IfcSchema::T*)l,r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"