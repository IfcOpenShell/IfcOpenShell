#define IFCUNTYPEDENTITY_H

#include <map>
#include <fstream>

namespace Ifc { class IfcUntypedEntity; }

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/Ifc2x3.h"

#include "../ifcgeom/IfcGeom.h"


namespace Ifc {
	class IfcUntypedEntity : public IfcUtil::IfcBaseEntity {
	private:
		Ifc2x3::Type::Enum _type;
	public:
		IfcUntypedEntity(const std::string& s);
		bool is(Ifc2x3::Type::Enum v) const;
		Ifc2x3::Type::Enum type() const;	
		bool is_a(const std::string& s) const;
		std::string is_a() const;
		unsigned int getArgumentCount() const;
		IfcUtil::ArgumentType getArgumentType(unsigned int i) const;
		ArgumentPtr getArgument(unsigned int i) const;
		ArgumentPtr getArgument(const std::string& a) const;
		const char* getArgumentName(unsigned int i) const;
		unsigned getArgumentIndex(const std::string& a) const;

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
typedef std::map<Ifc2x3::Type::Enum,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<std::string,Ifc2x3::IfcRoot::ptr> MapEntityByGuid;
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
		IfcParse::IfcSpfStream* file;
		IfcParse::Tokens* tokens;
	public:
		bool Init(const std::string& fn);
		IfcEntities EntitiesByType(const std::string& t);
		IfcEntity EntityById(int id);
		Ifc2x3::IfcRoot::ptr EntityByGuid(const std::string& guid);
		void AddEntity(IfcUtil::IfcSchemaEntity e);
		IfcFile();
		~IfcFile();
	};

	IfcParse::IfcFile* open(const std::string& s) {
		IfcParse::IfcFile* f = new IfcParse::IfcFile();
		f->Init(s);
		return f;
	}

	std::string create_shape(Ifc::IfcUntypedEntity* e) {
		if (!e->is(Ifc2x3::Type::IfcProduct)) throw IfcException("Entity is not an IfcProduct");
		Ifc2x3::IfcProduct* ifc_product = (Ifc2x3::IfcProduct*) e;
		return IfcGeom::create_brep_data(ifc_product);
	}
}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);