#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) return true;
#include "IfcRegisterDef.h"

#include "IfcRegister.h"