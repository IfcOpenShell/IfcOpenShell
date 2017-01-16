#include "CgalEntityMappingUndefine.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) { \
		try { \
			return convert((T*)l,r); \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l->entity); \
		} \
		return false; \
	}
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"
