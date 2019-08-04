#include "../ifcparse/IfcBaseClass.h"
#include "../ifcgeom/taxonomy.h"

namespace ifcopenshell {

namespace geometry {
    
    class abstract_mapping {
	public:
		virtual ifcopenshell::geometry::taxonomy::item* map(const IfcUtil::IfcBaseClass*) = 0;
    };
    
}

}