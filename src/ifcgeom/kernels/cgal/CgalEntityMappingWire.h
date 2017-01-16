#include "CgalEntityMappingUndefine.h"
#define WIRE(T) \
	if ( l->is(T::Class()) ) return convert((T*)l,r);
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"
