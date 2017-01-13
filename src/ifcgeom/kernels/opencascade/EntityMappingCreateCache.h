#include "EntityMappingUndefine.h"
#define CLASS(T,V) \
	std::map<int,V> T;
#include "EntityMappingDefine.h"

#include "EntityMapping.h"
