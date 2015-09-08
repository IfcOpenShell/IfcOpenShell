#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->declaration().is(T::Class()) ) { \
		try { \
			return convert(l->as<T>(), r); \
		} catch (...) { } \
		Logger::Message(Logger::LOG_ERROR, "Failed to convert:", l); \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"