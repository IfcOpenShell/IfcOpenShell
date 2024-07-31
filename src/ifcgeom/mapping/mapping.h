#ifndef MAPPING_H
#define MAPPING_H

#include "../abstract_mapping.h"
#include "../../ifcparse/macros.h"
#include "../../ifcparse/IfcFile.h"
#include "../../ifcparse/IfcLogger.h"

#include <mutex>

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

		std::map<uint32_t, ifcopenshell::geometry::taxonomy::ptr> cache_;
      std::mutex cache_guard_; // provides mutually exclusive access to cache_

		const IfcParse::declaration* placement_rel_to_type_;
		const IfcUtil::IfcBaseEntity* placement_rel_to_instance_;
		
		void initialize_units_();
		void addRepresentationsFromContextIds(IfcSchema::IfcRepresentation::list::ptr&);
		void addRepresentationsFromDefaultContexts(IfcSchema::IfcRepresentation::list::ptr&);

		// Set of instances to mark failures that are intended, such as representations not
		// resulting in any items due to dimensionality filters.
		std::set<const IfcUtil::IfcBaseInterface*> failed_on_purpose_;

		template <typename T>
		void process_mapping(bool& matched, taxonomy::ptr& item, IfcUtil::IfcBaseInterface const * inst) {
			if (!item && inst->as<T>()) {
				matched = true;
				try {
					item = map_impl(inst->as<T>());
					if (item != nullptr) {
						if (item->instance == nullptr) {
							item->instance = inst;
						}
						try {
							if (inst->as<IfcSchema::IfcRepresentationItem>() && !inst->as<IfcSchema::IfcStyledItem>() &&
								/* @todo */
								(item->kind() == taxonomy::SOLID || item->kind() == taxonomy::SHELL || item->kind() == taxonomy::COLLECTION || item->kind() == taxonomy::EXTRUSION || item->kind() == taxonomy::LOFT || item->kind() == taxonomy::BOOLEAN_RESULT || item->kind() == taxonomy::REVOLVE || item->kind() == taxonomy::SWEEP_ALONG_CURVE)
								) {
								auto style = find_style(inst->as<IfcSchema::IfcRepresentationItem>());
								if (style) {
									auto mstyle = map(style);
									if (mstyle) {
										taxonomy::cast<taxonomy::geom_item>(item)->surface_style = taxonomy::cast<taxonomy::style>(mstyle);
									}
								}
							}
						} catch (const std::exception& e) {
							Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", inst);
						}
					} else if (failed_on_purpose_.find(inst) == failed_on_purpose_.end()) {
						Logger::Message(Logger::LOG_ERROR, "Failed to convert:", inst);
					}
				} catch (const std::exception& e) {
					Logger::Message(Logger::LOG_ERROR, std::string(e.what()) + "\nFailed to convert:", inst);
				}
			}
		}
		const IfcSchema::IfcStyledItem* find_style(const IfcSchema::IfcRepresentationItem*);
	public:
		POSTFIX_SCHEMA(mapping)(IfcParse::IfcFile* file, Settings& settings) : abstract_mapping(settings), file_(file), placement_rel_to_type_(0), placement_rel_to_instance_(0) {
			initialize_units_();
		}
		virtual ifcopenshell::geometry::taxonomy::ptr map(const IfcUtil::IfcBaseInterface*);
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters);
		virtual std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);
		virtual void initialize_settings();
		virtual double get_length_unit() const { return length_unit_; }
		virtual aggregate_of_instance::ptr find_openings(const IfcUtil::IfcBaseEntity*);
		virtual IfcUtil::IfcBaseEntity* representation_of(const IfcUtil::IfcBaseEntity* product);

		virtual const IfcUtil::IfcBaseEntity* get_product_type(const IfcUtil::IfcBaseEntity* product_);
		virtual const IfcUtil::IfcBaseEntity* get_single_material_association(const IfcUtil::IfcBaseEntity* product);
		IfcSchema::IfcRepresentation* representation_mapped_to(const IfcSchema::IfcRepresentation* representation);
		IfcSchema::IfcProduct::list::ptr products_represented_by(const IfcSchema::IfcRepresentation* representation, bool only_direct=false);
		bool reuse_ok_(const IfcSchema::IfcProduct::list::ptr& products);
		IfcUtil::IfcBaseEntity* get_decomposing_entity(const IfcUtil::IfcBaseEntity* product, bool include_openings);

		bool get_layerset_information(const IfcUtil::IfcBaseInterface*, layerset_information&, int&);
		bool get_wall_neighbours(const IfcUtil::IfcBaseInterface*, std::vector<endpoint_connection>&);
		IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct*, const std::string&);

#include "bind_convert_decl.i"
    };

	template <typename U>
	struct element_type {
		typedef taxonomy::item type;
	};
	template <>
	struct element_type<taxonomy::boolean_result> {
		typedef taxonomy::geom_item type;
	};
	template <>
	struct element_type<taxonomy::collection> {
		typedef taxonomy::geom_item type;
	};
	template <>
	struct element_type<taxonomy::shell> {
		typedef taxonomy::face type;
	};
	template <>
	struct element_type<taxonomy::loop> {
		typedef taxonomy::edge type;
	};
	template <>
	struct element_type<taxonomy::solid> {
		typedef taxonomy::shell type;
	};	

	template <typename U = taxonomy::collection, typename T>
	typename U::ptr map_to_collection(POSTFIX_SCHEMA(mapping)* m, const T& ts) {
		auto c = taxonomy::make<U>();
		if (ts->size()) {
			for (auto it = ts->begin(); it != ts->end(); ++it) {
				if (auto r = m->map(*it)) {
					c->children.push_back(taxonomy::cast<typename element_type<U>::type>(r));
				}
			}
		}
		if (c->children.empty()) {
#ifdef TAXONOMY_USE_NAKED_PTR
			delete c;
#endif
			return nullptr;
		}
		return c;
	}

}

}

#endif