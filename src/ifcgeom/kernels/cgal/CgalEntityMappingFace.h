#include "CgalEntityMappingUndefine.h"
#define FACE(T) \
	if (l->declaration().is(IfcSchema::T::Class())) return convert((IfcSchema::T*)l,r);
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"