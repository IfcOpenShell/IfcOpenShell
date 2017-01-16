#include "CgalEntityMappingUndefine.h"
#define CLASS(T,V) \
	std::map<int,V> T;
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"
