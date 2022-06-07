/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCFILE_H
#define IFCFILE_H

#include <map>
#include <set>
#include <iterator>

#include <boost/unordered_map.hpp>
#include <boost/multi_index_container.hpp>
#include <boost/multi_index/sequenced_index.hpp>
#include <boost/multi_index/ordered_index.hpp>
#include <boost/multi_index/random_access_index.hpp>

#include "ifc_parse_api.h"

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcSpfHeader.h"
#include "../ifcparse/IfcSchema.h"

namespace IfcParse {

class IFC_PARSE_API file_open_status {
public:
	enum file_open_enum {
		SUCCESS,
		READ_ERROR,
		NO_HEADER,
		UNSUPPORTED_SCHEMA
	};

private:
	file_open_enum error_;

public:
	file_open_status(file_open_enum error)
		: error_(error)
	{}

	operator file_open_enum() const {
		return error_;
	}

	file_open_enum value() const {
		return error_;
	}

	operator bool() const {
		return error_ == SUCCESS;
	}
};

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IFC_PARSE_API IfcFile {
public:
	typedef std::map<const IfcParse::declaration*, aggregate_of_instance::ptr> entities_by_type_t;
	typedef boost::unordered_map<unsigned int, IfcUtil::IfcBaseClass*> entity_by_id_t;
	typedef std::map<std::string, IfcUtil::IfcBaseClass*> entity_by_guid_t;
	typedef std::tuple<int, int, int> inverse_attr_record;
	enum INVERSE_ATTR { INSTANCE_ID, INSTANCE_TYPE, ATTRIBUTE_INDEX };
	typedef std::map<inverse_attr_record, std::vector<int> > entities_by_ref_t;
	typedef std::map<int, std::vector<int> > entities_by_ref_excl_t;
	typedef std::map<unsigned int, aggregate_of_instance::ptr> ref_map_t;
	typedef entity_by_id_t::const_iterator const_iterator;

	class type_iterator : private entities_by_type_t::const_iterator {
	public:
		type_iterator() : entities_by_type_t::const_iterator() {};

		type_iterator(const entities_by_type_t::const_iterator& it)
			: entities_by_type_t::const_iterator(it)
		{};

		entities_by_type_t::key_type const * operator->() const {
			return &entities_by_type_t::const_iterator::operator->()->first;
		}

		entities_by_type_t::key_type const & operator*() const {
			return entities_by_type_t::const_iterator::operator*().first;
		}

		type_iterator& operator++() { 
			entities_by_type_t::const_iterator::operator++(); return *this; 
		}

		type_iterator operator++(int) { 
			type_iterator tmp(*this); operator++(); return tmp; 
		}

		bool operator!=(const type_iterator& other) const {
			const entities_by_type_t::const_iterator& self_ = *this;
			const entities_by_type_t::const_iterator& other_ = other;
			return self_ != other_;
		}
	};

	static bool lazy_load_;
	static bool lazy_load() { return lazy_load_; }
	static void lazy_load(bool b) { lazy_load_ = b; }

	static bool guid_map_;
	static bool guid_map() { return guid_map_; }
	static void guid_map(bool b) { guid_map_ = b; }

private:
	typedef std::map<uint32_t, IfcUtil::IfcBaseClass*> entity_entity_map_t;

	bool parsing_complete_;
	file_open_status good_ = file_open_status::SUCCESS;

	const IfcParse::schema_definition* schema_;
	const IfcParse::declaration* ifcroot_type_;

	entity_by_id_t byid;
	entities_by_type_t bytype;
	entities_by_type_t bytype_excl;
	entities_by_ref_t byref;
	entities_by_ref_excl_t byref_excl;
	entity_by_guid_t byguid;
	entity_entity_map_t entity_file_map;

	unsigned int MaxId;

	IfcSpfHeader _header;

	void setDefaultHeaderValues();

	void initialize_(IfcParse::IfcSpfStream* f);

	void build_inverses_(IfcUtil::IfcBaseClass*);

	typedef boost::multi_index_container<
		int,
		boost::multi_index::indexed_by<
			boost::multi_index::sequenced<>,
			boost::multi_index::ordered_unique<
				boost::multi_index::identity<int>
			>
		>
	> batch_deletion_ids_t;
	batch_deletion_ids_t batch_deletion_ids_;
	bool batch_mode_ = false;
	void process_deletion_();

public:
	IfcParse::IfcSpfLexer* tokens;
	IfcParse::IfcSpfStream* stream;
	
#ifdef USE_MMAP
	IfcFile(const std::string& fn, bool mmap = false);
#else
	IfcFile(const std::string& fn);
#endif
	IfcFile(std::istream& fn, int len);
	IfcFile(void* data, int len);
	IfcFile(IfcParse::IfcSpfStream* f);
	IfcFile(const IfcParse::schema_definition* schema = IfcParse::schema_by_name("IFC4"));

	/// Deleting the file will also delete all new instances that were added to the file (via memory allocation)
	virtual ~IfcFile();

	file_open_status good() const { return good_; }
	
	/// Returns the first entity in the file, this probably is the entity
	/// with the lowest id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator begin() const;
	/// Returns the last entity in the file, this probably is the entity
	/// with the highest id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator end() const;

	type_iterator types_begin() const;
	type_iterator types_end() const;

	type_iterator types_incl_super_begin() const;
	type_iterator types_incl_super_end() const;

	/// Returns all entities in the file that match the template argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	template <class T>
	typename T::list::ptr instances_by_type() {
		aggregate_of_instance::ptr untyped_list = instances_by_type(&T::Class());
		if (untyped_list) {
			return untyped_list->as<T>();
		} else {
			return typename T::list::ptr(new typename T::list);
		}
	}

	template <class T>
	typename T::list::ptr instances_by_type_excl_subtypes() {
		aggregate_of_instance::ptr untyped_list = instances_by_type_excl_subtypes(&T::Class());
		if (untyped_list) {
			return untyped_list->as<T>();
		} else {
			return typename T::list::ptr(new typename T::list);
		}
	}

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	aggregate_of_instance::ptr instances_by_type(const IfcParse::declaration*);

	/// Returns all entities in the file that match the positional argument.
	aggregate_of_instance::ptr instances_by_type_excl_subtypes(const IfcParse::declaration*);

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	aggregate_of_instance::ptr instances_by_type(const std::string& t);

	/// Returns all entities in the file that match the positional argument.
	aggregate_of_instance::ptr instances_by_type_excl_subtypes(const std::string& t);
	
	/// Returns all entities in the file that reference the id
	aggregate_of_instance::ptr instances_by_reference(int id);

	/// Returns the entity with the specified id
	IfcUtil::IfcBaseClass* instance_by_id(int id);

	/// Returns the entity with the specified GlobalId
	IfcUtil::IfcBaseClass* instance_by_guid(const std::string& guid);

	/// Performs a depth-first traversal, returning all entity instance
	/// attributes as a flat list. NB: includes the root instance specified
	/// in the first function argument.
	aggregate_of_instance::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level=-1);

	/// Same as traverse() but maintains topological order by using a
	/// breadth-first search
	aggregate_of_instance::ptr traverse_breadth_first(IfcUtil::IfcBaseClass* instance, int max_level=-1);

	aggregate_of_instance::ptr getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index);
	int getTotalInverses(int instance_id);

	template <class T>
	typename T::list::ptr getInverse(int instance_id, int attribute_index) {
		aggregate_of_instance::ptr return_value(new aggregate_of_instance);
		auto it = byref.find({ instance_id, T::Class().index_in_schema(), attribute_index });
		if (it != byref.end()) {
			for (auto& i : it->second) {
				return_value->push((T*)instance_by_id(i));
			}
		}
		return return_value;
	}

	unsigned int FreshId() { return ++MaxId; }

	unsigned int getMaxId() { return MaxId; }

	void recalculate_id_counter();

	IfcUtil::IfcBaseClass* addEntity(IfcUtil::IfcBaseClass* entity, int id=-1);
	void addEntities(aggregate_of_instance::ptr es);

	void batch() { batch_mode_ = true; }
	void unbatch() { process_deletion_(); batch_mode_ = false; 	}

	/// Removes entity instance from file and unsets references.
	///
	/// Attention when running removeEntity inside a loop over a list of entities to be removed. 
	/// This invalidates the iterator. A workaround is to reverse the loop:
	/// boost::shared_ptr<aggregate_of_instance> entities = ...;
	/// for (auto it = entities->end() - 1; it >= entities->begin(); --it) {
	///    IfcUtil::IfcBaseClass *const inst = *it;
	///    model->removeEntity(inst);
	/// }
	void removeEntity(IfcUtil::IfcBaseClass* entity);

	const IfcSpfHeader& header() const { return _header; }
	IfcSpfHeader& header() { return _header; }

	std::string createTimestamp() const;

	size_t load(unsigned entity_instance_name, const IfcParse::entity* entity, Argument**& attributes, size_t num_attributes, int attribute_index=-1);
	void seek_to(const IfcEntityInstanceData& data);
	void try_read_semicolon();

	void register_inverse(unsigned, const IfcParse::entity* from_entity, Token, int attribute_index);
	void register_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);
	void unregister_inverse(unsigned, const IfcParse::entity* from_entity, IfcUtil::IfcBaseClass*, int attribute_index);
    
	const IfcParse::schema_definition* schema() const { return schema_; }

	std::pair<IfcUtil::IfcBaseClass*, double> getUnit(const std::string& unit_type);

	bool parsing_complete() const { return parsing_complete_; }
	bool& parsing_complete() { return parsing_complete_; }

	void build_inverses();
};

#ifdef WITH_IFCXML
IFC_PARSE_API IfcFile* parse_ifcxml(const std::string& filename);
#endif

}

namespace std {
	template <>
	struct iterator_traits<IfcParse::IfcFile::type_iterator> {
		typedef ptrdiff_t difference_type;
		typedef const IfcParse::declaration* value_type;
		typedef const IfcParse::declaration*& reference;
		typedef const IfcParse::declaration** pointer;
		typedef std::forward_iterator_tag iterator_category;
	};
}

#endif
