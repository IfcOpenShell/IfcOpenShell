#include "IfcRegisterUndef.h"
#define CLASS(T,V) \
	std::map<int,V> T;
#include "IfcRegisterDef.h"

#include "IfcRegister.h"