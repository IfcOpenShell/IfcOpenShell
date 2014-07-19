#ifndef IFCUNTYPEDENTITY_H
#define IFCUNTYPEDENTITY_H

#include <string>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"

namespace IfcParse {
	
	class IfcUntypedEntity : public IfcUtil::IfcBaseEntity {
	private:
		IfcSchema::Type::Enum _type;
		IfcWrite::IfcWritableEntity* writable_entity();
		void invalid_argument(unsigned int i, const std::string& t);
	public:
		IfcUntypedEntity(const std::string& s);
		IfcUntypedEntity(IfcAbstractEntity* e);
		
		bool is(IfcSchema::Type::Enum v) const;
		IfcSchema::Type::Enum type() const;	
		bool is_a(const std::string& s) const;
		std::string is_a() const;

		unsigned int id() const;
		unsigned int getArgumentCount() const;
		IfcUtil::ArgumentType getArgumentType(unsigned int i) const;
		ArgumentPtr getArgument(unsigned int i) const;
		const char* getArgumentName(unsigned int i) const;
		unsigned getArgumentIndex(const std::string& a) const;

		IfcEntities get_inverse(const std::string& a);

		void setArgument(unsigned int iz);
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
		
		// TODO: Write as SWIG extension methods
		std::pair<IfcUtil::ArgumentType,ArgumentPtr> get_argument(unsigned i);
		std::pair<IfcUtil::ArgumentType,ArgumentPtr> get_argument(const std::string& a);

		bool is_valid();
	};

}

#endif