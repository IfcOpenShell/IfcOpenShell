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

#include "ifc_parse_api.h"

#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcSpfHeader.h"

namespace IfcParse {

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IFC_PARSE_API IfcFile {
public:
	typedef std::map<IfcSchema::Type::Enum, IfcEntityList::ptr> entities_by_type_t;
	typedef std::map<unsigned int, IfcUtil::IfcBaseClass*> entity_by_id_t;
	typedef std::map<std::string, IfcSchema::IfcRoot*> entity_by_guid_t;
	typedef std::map<unsigned int, std::vector<unsigned int> > entities_by_ref_t;
	typedef entity_by_id_t::const_iterator const_iterator;

	class type_iterator : public entities_by_type_t::const_iterator {
	public:
		type_iterator() : entities_by_type_t::const_iterator() {};

		type_iterator(const entities_by_type_t::const_iterator& it)
			: entities_by_type_t::const_iterator(it)
		{};

		entities_by_type_t::key_type const * operator->() const {
			return &entities_by_type_t::const_iterator::operator->()->first;
		}

		const entities_by_type_t::key_type& operator*() const {
			return entities_by_type_t::const_iterator::operator*().first;
		}

		const std::string& as_string() const {
			return IfcSchema::Type::ToString(**this);
		}
	};

private:
	typedef std::map<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*> entity_entity_map_t;

	bool parsing_complete_;

	entity_by_id_t byid;
	entities_by_type_t bytype;
	entities_by_type_t bytype_excl;
	entities_by_ref_t byref;
	entity_by_guid_t byguid;
	entity_entity_map_t entity_file_map;

	unsigned int MaxId;

	IfcSpfHeader _header;

	void setDefaultHeaderValues();

public:
	IfcParse::IfcSpfLexer* tokens;
	IfcParse::IfcSpfStream* stream;
	
	IfcFile();
	~IfcFile();
	
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
	typename T::list::ptr entitiesByType() {
		IfcEntityList::ptr untyped_list = entitiesByType(T::Class());
		if (untyped_list) {
			return untyped_list->as<T>();
		} else {
			return typename T::list::ptr(new typename T::list);
		}
	}

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr entitiesByType(IfcSchema::Type::Enum t);

	/// Returns all entities in the file that match the positional argument.
	IfcEntityList::ptr entitiesByTypeExclSubtypes(IfcSchema::Type::Enum t);

	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr entitiesByType(const std::string& t);

	/// Returns all entities in the file that reference the id
	IfcEntityList::ptr entitiesByReference(int id);

	/// Returns the entity with the specified id
	IfcUtil::IfcBaseClass* entityById(int id);

	/// Returns the entity with the specified GlobalId
	IfcSchema::IfcRoot* entityByGuid(const std::string& guid);

	/// Performs a depth-first traversal, returning all entity instance
	/// attributes as a flat list. NB: includes the root instance specified
	/// in the first function argument.
	IfcEntityList::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level=-1);

#ifdef USE_MMAP
	bool Init(const std::string& fn, bool mmap=false);
#else
	bool Init(const std::string& fn);
#endif
	bool Init(std::istream& fn, int len);
	bool Init(void* data, int len);
	bool Init(IfcParse::IfcSpfStream* f);

	IfcEntityList::ptr getInverse(int instance_id, IfcSchema::Type::Enum type, int attribute_index);

	unsigned int FreshId() { return ++MaxId; }

	IfcUtil::IfcBaseClass* addEntity(IfcUtil::IfcBaseClass* entity);
	void addEntities(IfcEntityList::ptr es);

	void removeEntity(IfcUtil::IfcBaseClass* entity);

	const IfcSpfHeader& header() const { return _header; }
	IfcSpfHeader& header() { return _header; }

	std::string createTimestamp() const;

	std::pair<IfcSchema::IfcNamedUnit*, double> getUnit(IfcSchema::IfcUnitEnum::IfcUnitEnum);

	void load(const IfcEntityInstanceData&);
	void load(unsigned entity_instance_name, std::vector<Argument*>& attributes);

	void register_inverse(unsigned, Token);
	void register_inverse(unsigned, IfcUtil::IfcBaseClass*);
	void unregister_inverse(unsigned, IfcUtil::IfcBaseClass*);
};

}

#endif