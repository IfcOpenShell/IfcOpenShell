#ifndef IFCFILE_H
#define IFCFILE_H

#include <map>

#include "IfcUtil.h"
#include "IfcParse.h"

namespace IfcParse {

typedef IfcUtil::IfcSchemaEntity IfcEntity;
//typedef IfcEntities IfcEntities;
typedef std::map<Ifc2x3::Type::Enum,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<std::string,Ifc2x3::IfcRoot::ptr> MapEntityByGuid;
typedef std::map<unsigned int,IfcEntities> MapEntitiesByRef;
typedef std::map<unsigned int,unsigned int> MapOffsetById;

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
	IfcEntities EntitiesByType(Ifc2x3::Type::Enum t);
	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntities EntitiesByType(const std::string& t);
	/// Returns all entities in the file that reference the id
	IfcEntities EntitiesByReference(int id);
	/// Returns the entity with the specified id
	IfcEntity EntityById(int id);
	/// Returns the entity with the specified GlobalId
	Ifc2x3::IfcRoot::ptr EntityByGuid(const std::string& guid);
	bool Init(const std::string& fn);
	bool Init(std::istream& fn, int len);
	bool Init(void* data, int len);
	bool Init(IfcParse::IfcSpfStream* f);
	unsigned int FreshId() { MaxId ++; return MaxId; }
	void AddEntity(IfcUtil::IfcSchemaEntity e);
	void AddEntities(IfcEntities es);
};

}

#endif