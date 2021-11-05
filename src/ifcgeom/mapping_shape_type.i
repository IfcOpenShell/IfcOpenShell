#include "mapping_undefine.i"
#define SHAPES(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return ST_SHAPELIST;
#define SHAPE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return ST_SHAPE;
#define WIRE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return ST_WIRE;
#define FACE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return ST_FACE;
#define CURVE(T) \
	if ( l->declaration().is(IfcSchema::T::Class()) ) return ST_CURVE;
#include "mapping_define_missing.i"

#include "mapping.i"