#ifndef ABSTRACT_MAPPING_H
#define ABSTRACT_MAPPING_H

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcEntityList.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/settings.h"

#include <boost/function.hpp>

#include <map>
#include <string>

namespace ifcopenshell {

namespace geometry {

	struct geometry_conversion_task {
		int index;
		IfcUtil::IfcBaseEntity* representation;
		IfcEntityList::ptr products;
	};

	typedef boost::function<bool(IfcUtil::IfcBaseEntity*)> filter_t;
    
    class abstract_mapping {
	protected:
		settings settings_;
	public:
		abstract_mapping(settings& s) : settings_(s) {}

		virtual ifcopenshell::geometry::taxonomy::item* map(const IfcUtil::IfcBaseClass*) = 0;
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters, settings& s) = 0;
		virtual IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity* product, bool include_openings = true) = 0;
		virtual std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*) = 0;
    };

	namespace impl {
		typedef boost::function2<abstract_mapping*, IfcParse::IfcFile*, settings&> mapping_fn;

		class MappingFactoryImplementation : public std::map<std::string, mapping_fn> {
		public:
			MappingFactoryImplementation();
			void bind(const std::string& schema_name, mapping_fn);
			abstract_mapping* construct(IfcParse::IfcFile*, settings&);
		};

		MappingFactoryImplementation& mapping_implementations();
	}
    
}

}

#endif
