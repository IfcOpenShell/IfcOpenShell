#include "IfcRegisterUndef.h"
#define WIRE(T) \
	if (l->as<IfcSchema::T>()) return convert(l->as<IfcSchema::T>(), r);
#include "IfcRegisterDef.h"

#include "IfcRegister.h"