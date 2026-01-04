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
		const express::Base placement_rel_to_instance_;

		Eigen::Matrix4d offset_and_rotation_ = Eigen::Matrix4d::Identity();
		
		void initialize_units_();
		void addRepresentationsFromContextIds(std::vector<IfcSchema::IfcRepresentation>&);
		void addRepresentationsFromDefaultContexts(std::vector<IfcSchema::IfcRepresentation>&);

		// Set of instances to mark failures that are intended, such as representations not
		// resulting in any items due to dimensionality filters.
		std::set<express::Base> failed_on_purpose_;
		std::set<IfcSchema::IfcRepresentationMap> not_reusable_maps_;

		template <typename T>
		void process_mapping(bool& matched, taxonomy::ptr& item, const express::Base& inst) {
			if (!item && inst.as<T>()) {
				matched = true;
				try {
					item = map_impl(inst.as<T>());
					if (item != nullptr) {
						if (!item->instance) {
							item->instance = inst;
						}
						try {
							if (inst.as<IfcSchema::IfcRepresentationItem>() && !inst.as<IfcSchema::IfcStyledItem>() &&
								/* @todo */
								(item->kind() == taxonomy::SOLID || item->kind() == taxonomy::SHELL || item->kind() == taxonomy::COLLECTION || item->kind() == taxonomy::EXTRUSION || item->kind() == taxonomy::LOFT || item->kind() == taxonomy::BOOLEAN_RESULT || item->kind() == taxonomy::REVOLVE || item->kind() == taxonomy::SWEEP_ALONG_CURVE || item->kind() == taxonomy::FACE)
								) {
								auto style = find_style(inst.as<IfcSchema::IfcRepresentationItem>());
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
		IfcSchema::IfcStyledItem find_style(const IfcSchema::IfcRepresentationItem&);
	public:
		POSTFIX_SCHEMA(mapping)(IfcParse::IfcFile* file, Settings& settings) : abstract_mapping(settings), file_(file), placement_rel_to_type_(nullptr) {
			initialize_units_();
		}
		virtual ifcopenshell::geometry::taxonomy::ptr map(const express::Base&);
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters);
        virtual std::map<std::string, express::Base> get_layers(const express::Base&);
		virtual void initialize_settings();
		virtual double get_length_unit() const { return length_unit_; }
		virtual const std::string& get_length_unit_name() const { return length_unit_name_; }
		virtual std::vector<express::Base> find_openings(const express::Base&);
		virtual express::Base representation_of(const express::Base& product);

		virtual const express::Base get_product_type(const express::Base& product_);
        virtual const express::Base get_single_material_association(const express::Base& product);
        IfcSchema::IfcRepresentation representation_mapped_to(const IfcSchema::IfcRepresentation& representation);
        std::vector<IfcSchema::IfcProduct> products_represented_by(const IfcSchema::IfcRepresentation& representation, IfcSchema::IfcRepresentationMap& rmap, bool only_direct = false);
		bool reuse_ok_(const std::vector<IfcSchema::IfcProduct>& products);
		express::Base get_decomposing_entity(const express::Base& product, bool include_openings);

		bool get_layerset_information(const express::Base&, layerset_information&, int&);
        bool get_wall_neighbours(const express::Base&, std::vector<endpoint_connection>&);
		IfcSchema::IfcRepresentation find_representation(const IfcSchema::IfcProduct&, const std::string&);

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
		if (ts.size()) {
			for (auto& t : ts) {
				if (auto r = m->map(t)) {
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