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

#include "ifc_parse_api.h"

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcSpfHeader.h"
#include "../ifcparse/IfcSchema.h"

namespace IfcParse {

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IFC_PARSE_API IfcFile {
public:
	typedef std::map<const IfcParse::declaration*, IfcEntityList::ptr> entities_by_type_t;
	typedef boost::unordered_map<unsigned int, IfcUtil::IfcBaseClass*> entity_by_id_t;
	typedef std::map<std::string, IfcUtil::IfcBaseClass*> entity_by_guid_t;
	typedef std::map<unsigned int, std::vector<unsigned int> > entities_by_ref_t;
	typedef std::map<unsigned int, IfcEntityList::ptr> ref_map_t;
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

private:
	typedef std::map<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*> entity_entity_map_t;

	bool parsing_complete_, good_;

	const IfcParse::schema_definition* schema_;
	const IfcParse::declaration* ifcroot_type_;

	entity_by_id_t byid;
	entities_by_type_t bytype;
	entities_by_type_t bytype_excl;
	entities_by_ref_t byref;
	ref_map_t by_ref_cached_;
	entity_by_guid_t byguid;
	entity_entity_map_t entity_file_map;

	unsigned int MaxId;

	IfcSpfHeader _header;

	void setDefaultHeaderValues();

	void initialize_(IfcParse::IfcSpfStream* f);

	void build_inverses_(IfcUtil::IfcBaseClass*);
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

	virtual ~IfcFile();

	bool good() const { return good_; }
	
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
		IfcEntityList::ptr untyped_list = instances_by_type(&T::Class());
		if (untyped_list) {
			return untyped_list->as<T>();
		} else {
			return typename T::list::ptr(new typename T::list);
		}
	}

	template <class T>
	typename T::list::ptr instances_by_type_excl_subtypes() {
		IfcEntityList::ptr untyped_list = instances_by_type_excl_subtypes(&T::Class());
		if (untyped_list) {
			return untyped_list->as<T>();
		} else {
			return typename T::list::ptr(new typename T::list);
		}
	}

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr instances_by_type(const IfcParse::declaration*);

	/// Returns all entities in the file that match the positional argument.
	IfcEntityList::ptr instances_by_type_excl_subtypes(const IfcParse::declaration*);

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr instances_by_type(const std::string& t);

	/// Returns all entities in the file that reference the id
	IfcEntityList::ptr instances_by_reference(int id);

	/// Returns the entity with the specified id
	IfcUtil::IfcBaseClass* instance_by_id(int id);

	/// Returns the entity with the specified GlobalId
	IfcUtil::IfcBaseClass* instance_by_guid(const std::string& guid);

	/// Performs a depth-first traversal, returning all entity instance
	/// attributes as a flat list. NB: includes the root instance specified
	/// in the first function argument.
	IfcEntityList::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level=-1);

	IfcEntityList::ptr getInverse(int instance_id, const IfcParse::declaration* type, int attribute_index);

	/// Marks entity as modified so that potential cache for it is invalidated.
	/// @todo Currently the whole cache is invalidated. Implement more fine-grained invalidation.
	void mark_entity_as_modified(int id);

	unsigned int FreshId() { return ++MaxId; }

	IfcUtil::IfcBaseClass* addEntity(IfcUtil::IfcBaseClass* entity);
	void addEntities(IfcEntityList::ptr es);

	void removeEntity(IfcUtil::IfcBaseClass* entity);

	const IfcSpfHeader& header() const { return _header; }
	IfcSpfHeader& header() { return _header; }

	std::string createTimestamp() const;

	void load(const IfcEntityInstanceData&);
	size_t load(unsigned entity_instance_name, Argument**& attributes, size_t num_attributes);

	void register_inverse(unsigned, Token);
	void register_inverse(unsigned, IfcUtil::IfcBaseClass*);
	void unregister_inverse(unsigned, IfcUtil::IfcBaseClass*);
    
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
