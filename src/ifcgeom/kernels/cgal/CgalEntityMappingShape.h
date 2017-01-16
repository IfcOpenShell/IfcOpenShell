#include "CgalEntityMappingUndefine.h"
#define SHAPE(T) \
	if ( !processed && l->is(T::Class()) ) { \
		processed = true; \
		try { \
			if ( convert((T*)l,r) ) { \
				success = true; \
			} \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l->entity); \
			return false; \
		} \
		if (!success) { \
			Logger::Message(Logger::LOG_ERROR,"Failed to convert:",l->entity); \
			return false; \
		} \
	}
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"