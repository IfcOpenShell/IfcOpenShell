#include "IfcRegisterUndef.h"
#define SHAPE(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			if ( convert((T*)l,r) ) { \
				Cache::Shape[l->entity->id()] = r; \
				return true; \
			} \
		} catch(...) {  } \
		Ifc::LogMessage("Error","Failed to convert:",l->entity); \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"