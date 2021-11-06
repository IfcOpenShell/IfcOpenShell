#include "mapping_undefine.i"
#define SHAPES(T) \
	if (l->as<IfcSchema::T>()) { \
		try { \
			return convert(l->as<IfcSchema::T>(), r); \
		} catch (const std::exception& e) { \
			Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", l); \
		} catch (const Standard_Failure& f) { \
			if (f.GetMessageString()) \
				Logger::Message(Logger::LOG_ERROR, std::string("Error in: ") + f.GetMessageString() + "\nFailed to convert:", l); \
			else \
				Logger::Message(Logger::LOG_ERROR, "Failed to convert:", l); \
		} \
		return false; \
	}
#include "mapping_define_missing.i"

#include "mapping.i"