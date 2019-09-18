#include "../abstract_mapping.h"
#include "../../ifcparse/macros.h"
#include "../../ifcparse/IfcFile.h"

#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA
#define INCLUDE_SCHEMA(x) STRINGIFY(../../ifcparse/x-definitions.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

namespace ifcopenshell {

namespace geometry {
    
    class POSTFIX_SCHEMA(mapping) : public abstract_mapping {
	private:
		IfcParse::IfcFile* file_;
		double length_unit_, angle_unit_;
		std::string length_unit_name_;
		const IfcParse::declaration* placement_rel_to_;

		void initialize_units_();
	public:
		POSTFIX_SCHEMA(mapping)(IfcParse::IfcFile* file) : file_(file), placement_rel_to_(0) {
			initialize_units_();
		}
		virtual ifcopenshell::geometry::taxonomy::item* map(const IfcUtil::IfcBaseClass*);
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters, settings& s);
		virtual std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);
		
		const IfcSchema::IfcMaterial* get_single_material_association(const IfcSchema::IfcProduct* product);
		IfcSchema::IfcRepresentation* representation_mapped_to(const IfcSchema::IfcRepresentation* representation);
		IfcSchema::IfcProduct::list::ptr products_represented_by(const IfcSchema::IfcRepresentation* representation);
		bool reuse_ok_(settings& s, const IfcSchema::IfcProduct::list::ptr& products);
		IfcEntityList::ptr find_openings(const IfcSchema::IfcProduct* product);
		IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity* product, bool include_openings);

#include "bind_convert_decl.i"
    };
    
}

}