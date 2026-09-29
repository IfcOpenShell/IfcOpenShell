#ifdef BIND
#undef BIND
#endif

#define BIND(T) ifcopenshell::geom::taxonomy::ptr map_impl(const IfcSchema::T&);

#include "mapping.i"
