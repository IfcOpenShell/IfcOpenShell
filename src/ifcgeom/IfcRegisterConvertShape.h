#include "IfcRegisterUndef.h"
#define SHAPE(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			if ( convert((T*)l,r) ) { \
				Cache::Shape[id] = r; \
				return &(Cache::Shape[id]); \
			} \
		} catch(...) {  } \
		Logger::Message(Logger::LOG_ERROR,"Failed to convert:",l->entity); \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"