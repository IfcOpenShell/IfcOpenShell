#include "IfcRegisterUndef.h"
#define SHAPE(T) \
	if ( !processed && l->declaration().is(T::Class()) ) { \
		processed = true; \
		try { \
			if ( convert(l->as<T>(), r) ) { \
				success = true; \
			} \
		} catch(...) {  } \
		if ( !success) { \
			Logger::Message(Logger::LOG_ERROR, "Failed to convert:", l); \
			return false; \
		} \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"