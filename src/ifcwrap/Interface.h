#define IFCUNTYPEDENTITY_H

#include <map>
#include <fstream>

namespace IfcParse { class IfcUntypedEntity; }

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/Ifc2x3.h"

#include "../ifcgeom/IfcGeom.h"


namespace IfcParse {
	class IfcUntypedEntity : public IfcUtil::IfcBaseEntity {
	private:
		IfcSchema::Type::Enum _type;
	public:
		IfcUntypedEntity(const std::string& s);
		bool is(IfcSchema::Type::Enum v) const;
		IfcSchema::Type::Enum type() const;	
		bool is_a(const std::string& s) const;
		std::string is_a() const;
		unsigned int getArgumentCount() const;
		IfcUtil::ArgumentType getArgumentType(unsigned int i) const;
		ArgumentPtr getArgument(unsigned int i) const;
		ArgumentPtr getArgument(const std::string& a) const;
		const char* getArgumentName(unsigned int i) const;
		unsigned getArgumentIndex(const std::string& a) const;
		
		IfcEntities get_inverse(const std::string& a);

		void setArgument(unsigned int i);
		void setArgument(unsigned int i, int v);
		void setArgument(unsigned int i, bool v);
		void setArgument(unsigned int i, double v);
		void setArgument(unsigned int i, const std::string& v);
		void setArgument(unsigned int i, const std::vector<int>& v);
		void setArgument(unsigned int i, const std::vector<double>& v);
		void setArgument(unsigned int i, const std::vector<std::string>& v);
		void setArgument(unsigned int i, IfcUntypedEntity* v);
		void setArgument(unsigned int i, IfcEntities v);

		std::string toString();
		
		std::pair<IfcUtil::ArgumentType,ArgumentPtr> get_argument(unsigned i);
		std::pair<IfcUtil::ArgumentType,ArgumentPtr> get_argument(const std::string& a);

		bool is_valid();
	};
}

typedef IfcUtil::IfcSchemaEntity IfcEntity;
typedef std::map<IfcSchema::Type::Enum,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<std::string,IfcSchema::IfcRoot::ptr> MapEntityByGuid;
typedef std::map<unsigned int,IfcEntities> MapEntitiesByRef;
typedef std::map<unsigned int,unsigned int> MapOffsetById;

namespace IfcParse {
	class IfcSpfStream;
	class Tokens;

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
	public:
		IfcParse::IfcSpfStream* stream;
		IfcParse::Tokens* tokens;
		bool Init(const std::string& fn);
		IfcEntities EntitiesByType(const std::string& t);
		IfcEntity EntityById(int id);
		IfcSchema::IfcRoot::ptr EntityByGuid(const std::string& guid);
		void AddEntity(IfcUtil::IfcSchemaEntity e);
		IfcFile();
		~IfcFile();

		std::vector<int> entity_names() const {
			std::vector<int> keys;
			keys.reserve(byid.size());
			for (MapEntityById::const_iterator it = byid.begin(); it != byid.end(); ++ it) {
				keys.push_back(it->first);
			}
			return keys;	
		}
	};

	IfcParse::IfcFile* open(const std::string& s) {
		IfcParse::IfcFile* f = new IfcParse::IfcFile();
		f->Init(s);
		IfcEntities projects = f->EntitiesByType("IfcProject");
		if (projects->Size() == 1) {
			double unit_magnitude;
			std::string unit_name;
			IfcGeom::initialize_units_and_precision((IfcSchema::IfcProject*)*projects->begin(), unit_magnitude, unit_name);
		}
		return f;
	}

	std::string create_shape(IfcParse::IfcUntypedEntity* e, unsigned int settings = 0) {
		if (!e->is(IfcSchema::Type::IfcProduct)) throw IfcException("Entity is not an IfcProduct");
		IfcSchema::IfcProduct* ifc_product = (IfcSchema::IfcProduct*) e;
		return IfcGeom::create_brep_data(ifc_product, settings);
	}

	void clean() { 
		IfcGeom::Cache::Purge(); 
	}

	const int DISABLE_OPENING_SUBTRACTIONS = 1 << 0;
	const int DISABLE_OBJECT_PLACEMENT     = 1 << 1;
	const int SEW_SHELLS                   = 1 << 2;
	const int CONVERT_TO_METERS            = 1 << 3;
}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);