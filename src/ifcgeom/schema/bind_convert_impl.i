#ifdef BIND
#undef BIND
#endif

#define BIND(T) \
	if (l->declaration().is(IfcSchema::T::Class())) { \
		try { \
			return map((IfcSchema::T*)l); \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l); \
		} \
		return false; \
	}

#include "mapping.i"
