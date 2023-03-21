#ifndef MAPPING_H
#define MAPPING_H

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

		const IfcParse::declaration* placement_rel_to_type_;
		const IfcUtil::IfcBaseEntity* placement_rel_to_instance_;
		
		void initialize_units_();
		void addRepresentationsFromContextIds(IfcSchema::IfcRepresentation::list::ptr&);
		void addRepresentationsFromDefaultContexts(IfcSchema::IfcRepresentation::list::ptr&);
	public:
		POSTFIX_SCHEMA(mapping)(IfcParse::IfcFile* file, IfcGeom::IteratorSettings& settings) : abstract_mapping(settings), file_(file), placement_rel_to_type_(0), placement_rel_to_instance_(0) {
			initialize_units_();
			apply_settings();
		}
		virtual ifcopenshell::geometry::taxonomy::item* map(const IfcUtil::IfcBaseInterface*);
		virtual void get_representations(std::vector<geometry_conversion_task>& tasks, std::vector<filter_t>& filters);
		virtual std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);
		virtual void initialize_settings();
		virtual double get_length_unit() const { return length_unit_; }
		virtual aggregate_of_instance::ptr find_openings(const IfcUtil::IfcBaseEntity*);
		virtual IfcUtil::IfcBaseEntity* representation_of(const const IfcUtil::IfcBaseEntity* product);

		void apply_settings();
		
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


	// Hacks around not wanting to use if constexpr
	template <typename T>
	class loop_to_face_upgrade {
	public:
		loop_to_face_upgrade(taxonomy::item*) {}

		operator bool() const {
			return false;
		}

		operator taxonomy::face() const {
			throw taxonomy::topology_error();
		}

		operator T() const {
			throw taxonomy::topology_error();
		}
	};

	template <>
	class loop_to_face_upgrade<taxonomy::face> {
	private:
		boost::optional<taxonomy::face> face_;
	public:
		loop_to_face_upgrade(taxonomy::item* item) {
			taxonomy::loop* loop = dynamic_cast<taxonomy::loop*>(item);
			if (loop) {
				loop->external = true;

				face_.emplace();
				face_->instance = loop->instance;
				face_->matrix = loop->matrix;
				face_->children = { loop->clone() };
			}
		}

		operator bool() const {
			return face_.is_initialized();
		}

		operator taxonomy::face() const {
			return *face_;
		}
	};

	// A RAII-based mechanism to cast the conversion results
	// from map() into the right type expected by the higher
	// level typology items. An exception is thrown if the
	// types do not match or the result was nullptr. A copy
	// will be assigned to the higher level topology member
	// and the original pointer will be deleted.

	// This class is also able to uplift some topology items
	// to higher level types, such as a loop to a face, which
	// is why the cast operator does not return a reference.
	template <typename T>
	class as {
	private:
		taxonomy::item* item_;

	public:
		as(taxonomy::item* item) : item_(item) {}
		operator T() const {
			if (!item_) {
				throw taxonomy::topology_error("item was nullptr");
			}
			T* t = dynamic_cast<T*>(item_);
			if (t) {
				return T(*t);
			} else {
				{
					loop_to_face_upgrade<T> upgrade(item_);
					if (upgrade) {
						return upgrade;
					}
				}
				throw taxonomy::topology_error("item does not match type");
			}
		}
		~as() {
			delete item_;
		}
	};

	template <typename U = taxonomy::collection, typename T>
	U* map_to_collection(POSTFIX_SCHEMA(mapping)* m, const T& ts) {
		auto c = new U;
		if (ts->size()) {
			for (auto it = ts->begin(); it != ts->end(); ++it) {
				if (auto r = m->map(*it)) {
					c->children.push_back(r);
				}
			}
		}
		if (c->children.empty()) {
			delete c;
			return nullptr;
		}
		return c;
	}

}

}

#endif