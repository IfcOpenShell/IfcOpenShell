#include "CgalEntityMappingUndefine.h"
#define SHAPE(T) \
	if ( !processed && l->declaration().is(IfcSchema::T::Class()) ) { \
		processed = true; \
		try { \
			if (convert((IfcSchema::T*)l, r) ) { \
				success = true; \
			} \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l); \
			return false; \
		} \
		if (!success) { \
			Logger::Message(Logger::LOG_ERROR,"Failed to convert:", l); \
			return false; \
		} \
	}
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"