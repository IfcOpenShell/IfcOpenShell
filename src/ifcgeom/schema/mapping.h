#include "../abstract_mapping.h"
#include "../../ifcparse/macros.h"

#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA
#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x-definitions.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

namespace ifcopenshell {

namespace geometry {
    
    class POSTFIX_SCHEMA(mapping) : public abstract_mapping {
		virtual ifcopenshell::geometry::taxonomy::item* map(const IfcUtil::IfcBaseClass*);
#include "bind_convert_decl.i"
    };
    
}

}