#ifndef ABSTRACT_MAPPING_H
#define ABSTRACT_MAPPING_H

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/aggregate_of_instance.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/IteratorSettings.h"
#include "../ifcgeom/ConversionSettings.h"

#include <boost/function.hpp>

#include <map>
#include <string>
#include <tuple>

namespace ifcopenshell {

namespace geometry {

	struct geometry_conversion_task {
		int index;
		IfcUtil::IfcBaseEntity* representation;
		aggregate_of_instance::ptr products;
	};

	typedef boost::function<bool(IfcUtil::IfcBaseEntity*)> filter_t;
    
    class abstract_mapping {
	protected:
		Settings settings_;

		bool use_caching_ = true;

	public:
		abstract_mapping(Settings& s) : settings_(s) {}
		virtual ~abstract_mapping() {}

		virtual ifcopenshell::geometry::taxonomy::ptr map(const IfcUtil::IfcBaseInterface*) = 0;
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters) = 0;
		virtual IfcUtil::IfcBaseEntity* get_decomposing_entity(const IfcUtil::IfcBaseEntity* product, bool include_openings = true) = 0;
		virtual std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*) = 0;
		virtual aggregate_of_instance::ptr find_openings(const IfcUtil::IfcBaseEntity*) = 0;
		virtual void initialize_settings() = 0;
		virtual bool get_layerset_information(const IfcUtil::IfcBaseInterface*, layerset_information&, int&) = 0;
		virtual bool get_wall_neighbours(const IfcUtil::IfcBaseInterface*, std::vector<endpoint_connection>&) = 0;
		virtual const IfcUtil::IfcBaseEntity* get_product_type(const IfcUtil::IfcBaseEntity*) = 0;
		virtual const IfcUtil::IfcBaseEntity* get_single_material_association(const IfcUtil::IfcBaseEntity*) = 0;
		virtual double get_length_unit() const = 0;
		virtual IfcUtil::IfcBaseEntity* representation_of(const IfcUtil::IfcBaseEntity* product) = 0;

		const Settings& settings() const { return settings_; }
		Settings& settings() { return settings_; }

		bool use_caching() const { return use_caching_; }
		bool& use_caching() { return use_caching_; }
    };

	namespace impl {
		typedef boost::function2<abstract_mapping*, IfcParse::IfcFile*, Settings&> mapping_fn;

		class MappingFactoryImplementation : public std::map<std::string, mapping_fn> {
		public:
			MappingFactoryImplementation();
			void bind(const std::string& schema_name, mapping_fn);
			abstract_mapping* construct(IfcParse::IfcFile*, Settings&);
		};

		MappingFactoryImplementation& mapping_implementations();
	}
    
}

}

#endif
