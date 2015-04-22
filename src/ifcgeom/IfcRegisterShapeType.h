#include "IfcRegisterUndef.h"
#define SHAPES(T) \
	if ( l->is(T::Class()) ) return ST_SHAPELIST;
#define SHAPE(T) \
	if ( l->is(T::Class()) ) return ST_SHAPE;
#define WIRE(T) \
	if ( l->is(T::Class()) ) return ST_WIRE;
#define FACE(T) \
	if ( l->is(T::Class()) ) return ST_FACE;
#define CURVE(T) \
	if ( l->is(T::Class()) ) return ST_CURVE;
#include "IfcRegisterDef.h"

#include "IfcRegister.h"