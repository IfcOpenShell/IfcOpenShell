#include "CgalEntityMappingUndefine.h"
#define SHAPES(T) \
	if (l->declaration().is(IfcSchema::T::Class())) { \
		try { \
			return convert((IfcSchema::T*)l,r); \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l); \
		} \
		return false; \
	}
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"
