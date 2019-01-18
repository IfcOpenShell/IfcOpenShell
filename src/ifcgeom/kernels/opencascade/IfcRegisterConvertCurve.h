#include "IfcRegisterUndef.h"
#define CURVE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return convert((IfcSchema::T*)l,r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"