#ifdef BIND
#undef BIND
#endif

#define BIND(T) ifcopenshell::geometry::taxonomy::item* map_impl(const IfcSchema::T*);

#include "mapping.i"
