#ifdef BIND
#undef BIND
#endif

#define BIND(T) ifcopenshell::geometry::taxonomy::item* map(const IfcSchema::T*);

#include "mapping.i"
