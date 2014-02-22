#include "IfcRegisterUndef.h"
#define SHAPE(T) \
	if ( !processed && l->is(T::Class()) ) { \
		processed = true; \
		try { \
			if ( convert((T*)l,r) ) { \
				success = true; \
			} \
		} catch(...) {  } \
		if ( !success) { \
			Logger::Message(Logger::LOG_ERROR,"Failed to convert:",l->entity); \
			return false; \
		} \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"