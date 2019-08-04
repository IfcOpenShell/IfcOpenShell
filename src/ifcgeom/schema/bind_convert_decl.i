#ifdef BIND
#undef BIND
#endif

#define BIND(T) ifcopenshell::geometry::taxonomy::item* convert(const IfcSchema::T*);

#include "mapping.i"
