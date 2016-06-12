#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			return convert((T*)l,r); \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l->entity); \
		} catch (const Standard_Failure& f) { \
			if (f.GetMessageString()) \
				Logger::Message(Logger::LOG_ERROR, std::string("Error in: ") + f.GetMessageString() + "\nFailed to convert:", l->entity); \
			else \
				Logger::Message(Logger::LOG_ERROR, "Failed to convert:", l->entity); \
		} \
		return false; \
	}
#include "IfcRegisterDef.h"

#include "IfcRegister.h"