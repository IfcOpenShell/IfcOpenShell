#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			return convert((T*)l,r); \
		} catch (...) { } \
		Logger::Message(Logger::LOG_ERROR,"Failed to convert:",l->entity); \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"