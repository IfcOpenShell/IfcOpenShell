#include "EntityMappingUndefine.h"
#define WIRE(T) \
	if ( l->is(T::Class()) ) return convert((T*)l,r);
#include "EntityMappingDefine.h"

#include "EntityMapping.h"
