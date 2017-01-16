#include "CgalEntityMappingUndefine.h"
#define FACE(T) \
	if ( l->is(T::Class()) ) return convert((T*)l,r);
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"