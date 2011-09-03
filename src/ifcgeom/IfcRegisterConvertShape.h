#include "IfcRegisterUndef.h"
#define SHAPE(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			bool b = convert((T*)l,r); \
			if ( b ) { \
				Cache::Shape[l->entity->id()] = r; \
				return true; \
			} else { return false; }\
		} catch(...) { Ifc::LogMessage("Error","Failed to convert:",l->entity); } \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"