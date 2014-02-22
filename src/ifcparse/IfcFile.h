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

/********************************************************************************
 *                                                                              *
 * This file provides functions for loading an IFC file into memory and access  *
 * its entities either by ID, by an IfcSchema::Type or by reference             * 
 *                                                                              *
 ********************************************************************************/

#ifndef IFCFILE_H
#define IFCFILE_H

#include "../ifcparse/IfcParse.h"

namespace IfcParse {

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IfcFile {
private:
	MapEntityById byid;
	MapEntitiesByType bytype;
	MapEntitiesByRef byref;
	MapEntityByGuid byguid;
	MapOffsetById offsets;
	unsigned int lastId;
	unsigned int MaxId;
	std::string _filename;
	std::string _timestamp;
	std::string _author;
	std::string _author_email;
	std::string _author_organisation;
	void initTimestamp();
public:
	typedef MapEntityById::const_iterator const_iterator;
	IfcFile();
	~IfcFile();
	/// Returns the first entity in the file, this probably is the entity with the lowest id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator begin() const;
	/// Returns the last entity in the file, this probably is the entity with the highes id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator end() const;
	IfcParse::IfcSpfStream* file;
	IfcParse::Tokens* tokens;
	/// Returns all entities in the file that match the template argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	template <class T>
	typename T::list EntitiesByType() {
		IfcEntities e = EntitiesByType(T::Class());
		typename T::list l ( new IfcTemplatedEntityList<T>() );
		if ( e && e->Size() )
			for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {
				l->push(reinterpret_pointer_cast<IfcUtil::IfcBaseClass,T>(*it));
			}
			return l;
	}
	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntities EntitiesByType(IfcSchema::Type::Enum t);
	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntities EntitiesByType(const std::string& t);
	/// Returns all entities in the file that reference the id
	IfcEntities EntitiesByReference(int id);
	/// Returns the entity with the specified id
	IfcEntity EntityById(int id);
	/// Returns the entity with the specified GlobalId
	IfcSchema::IfcRoot::ptr EntityByGuid(const std::string& guid);
	bool Init(const std::string& fn);
	bool Init(std::istream& fn, int len);
	bool Init(void* data, int len);
	bool Init(IfcParse::IfcSpfStream* f);
	unsigned int FreshId() { MaxId ++; return MaxId; }
	void AddEntity(IfcUtil::IfcSchemaEntity e);
	void AddEntities(IfcEntities es);

	void filename(const std::string& s);
	std::string filename() const;
	void timestamp(const std::string& s);
	std::string timestamp() const;
	void author(const std::string& name, const std::string& email, const std::string& organisation);
	std::string authorName() const;
	std::string authorEmail() const;
	std::string authorOrganisation() const;
};

}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);

#endif
