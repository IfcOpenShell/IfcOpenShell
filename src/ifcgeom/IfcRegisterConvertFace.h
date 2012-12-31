#include "IfcRegisterUndef.h"
#define FACE(T) \
	if ( l->is(T::Class()) ) return convert((T*)l,r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"