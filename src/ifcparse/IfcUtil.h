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

#ifndef IFCUTIL_H
#define IFCUTIL_H

#include <string>
#include <vector>
#include <sstream>

#include "../ifcparse/SharedPointer.h"
#include "../ifcparse/Ifc2x3enum.h"

class IfcAbstractEntity;
//typedef SHARED_PTR<IfcAbstractEntity> IfcAbstractEntityPtr;
typedef IfcAbstractEntity* IfcAbstractEntityPtr;

class IfcEntityList;
typedef SHARED_PTR<IfcEntityList> IfcEntities;

class Argument;
//typedef SHARED_PTR<Argument> ArgumentPtr;
typedef Argument* ArgumentPtr;


template <class F, class T>
inline T* reinterpret_pointer_cast(F* from) {
	return (T*)from;
	//SHARED_PTR<void> v = std::tr1::static_pointer_cast<void,F>(from);
	//return std::tr1::static_pointer_cast<T,void>(v);
}

namespace IfcUtil {
    enum ArgumentType {
        Argument_INT, Argument_BOOL, Argument_DOUBLE, Argument_STRING, Argument_VECTOR_INT, Argument_VECTOR_DOUBLE, Argument_VECTOR_STRING, Argument_ENTITY, Argument_ENTITY_LIST, Argument_ENUMERATION, Argument_UNKNOWN
    };
}

namespace IfcUtil {

class IfcBaseClass {
public:
    IfcAbstractEntityPtr entity;
    virtual bool is(Ifc2x3::Type::Enum v) const = 0;
    virtual Ifc2x3::Type::Enum type() const = 0;
};

class IfcBaseEntity : public IfcBaseClass {
public:
    virtual unsigned int getArgumentCount() const = 0;
    virtual ArgumentType getArgumentType(unsigned int i) const = 0;
    virtual ArgumentPtr getArgument(unsigned int i) const = 0;
    virtual const char* getArgumentName(unsigned int i) const = 0;
};

//typedef SHARED_PTR<IfcBaseClass> IfcSchemaEntity;
typedef IfcBaseClass* IfcSchemaEntity;

}

class IfcEntityList {
	std::vector<IfcUtil::IfcSchemaEntity> ls;
public:
	typedef std::vector<IfcUtil::IfcSchemaEntity>::const_iterator it;
	IfcEntities getInverse(Ifc2x3::Type::Enum c = Ifc2x3::Type::ALL);
	IfcEntities getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a);
	void push(IfcUtil::IfcSchemaEntity l);
	void push(IfcEntities l);
	it begin();
	it end();
	IfcUtil::IfcSchemaEntity operator[] (int i);
	int Size() const;
};

template <class T>
class IfcTemplatedEntityList {
	std::vector<T*> ls;
public:
	typedef typename std::vector<T*>::const_iterator it;
	inline void push(T* t) {if (t) ls.push_back(t);}
	inline void push(SHARED_PTR< IfcTemplatedEntityList<T> > t) { for ( typename T::it it = t->begin(); it != t->end(); ++it ) push(*it); }
	inline it begin() { return ls.begin(); }
	inline it end() { return ls.end(); }
	inline T operator[] (int i) { return ls[i]; }
	inline unsigned int Size() const { return (unsigned int) ls.size(); }
	IfcEntities generalize() {
		IfcEntities r (new IfcEntityList());
		for ( it i = begin(); i != end(); ++ i ) r->push(*i);
		return r;
	}
};

namespace IfcUtil {
	class IfcAbstractSelect : public IfcBaseClass {
	public:
		typedef SHARED_PTR< IfcTemplatedEntityList<IfcAbstractSelect> > list;
		typedef IfcTemplatedEntityList<IfcAbstractSelect>::it it;
		typedef IfcAbstractSelect* ptr;
		virtual bool isSimpleType() = 0;
	};
	class IfcEntitySelect : public IfcAbstractSelect {
	public:
		typedef IfcEntitySelect* ptr;
		IfcEntitySelect(IfcSchemaEntity b);
		IfcEntitySelect(IfcAbstractEntityPtr e);
		~IfcEntitySelect();
		bool is(Ifc2x3::Type::Enum v) const;
		Ifc2x3::Type::Enum type() const;
		bool isSimpleType();
	};
	class IfcArgumentSelect : public IfcAbstractSelect {
		Ifc2x3::Type::Enum _type;
		ArgumentPtr arg;
	public:
		typedef IfcArgumentSelect* ptr;
		IfcArgumentSelect(Ifc2x3::Type::Enum t, ArgumentPtr a);
		~IfcArgumentSelect();
		ArgumentPtr wrappedValue();
		bool is(Ifc2x3::Type::Enum v) const;
		Ifc2x3::Type::Enum type() const;
		bool isSimpleType();
	};
}

namespace IfcParse {
	class IfcFile;
}

class Argument {
public:
	//void* file;
//public:
	virtual operator int() const = 0;
	virtual operator bool() const = 0;
	virtual operator double() const = 0;
	virtual operator std::string() const = 0;
	virtual operator std::vector<double>() const = 0;
	virtual operator std::vector<int>() const = 0;
	virtual operator std::vector<std::string>() const = 0;
	virtual operator IfcUtil::IfcSchemaEntity() const = 0;
	//virtual operator IfcUtil::IfcAbstractSelect::ptr() const = 0;
	virtual operator IfcEntities() const = 0;
	virtual unsigned int Size() const = 0;
	virtual ArgumentPtr operator [] (unsigned int i) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
	virtual bool isNull() const = 0;
	virtual ~Argument() {};
};

class IfcAbstractEntity {
public:
	IfcParse::IfcFile* file;
	virtual IfcEntities getInverse(Ifc2x3::Type::Enum c = Ifc2x3::Type::ALL) = 0;
	virtual IfcEntities getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a) = 0;
	virtual std::string datatype() = 0;
	virtual ArgumentPtr getArgument (unsigned int i) = 0;
	virtual unsigned int getArgumentCount() = 0;
	virtual ~IfcAbstractEntity() {};
	virtual Ifc2x3::Type::Enum type() const = 0;
	virtual bool is(Ifc2x3::Type::Enum v) const = 0;
	virtual std::string toString(bool upper=false) = 0;
	virtual unsigned int id() = 0;
	virtual bool isWritable() = 0;
};

class Logger {
public:
	typedef enum { LOG_NOTICE, LOG_WARNING, LOG_ERROR } Severity;
private:
	static std::ostream* log1;
	static std::ostream* log2;
	static std::stringstream log_stream;
	static Severity verbosity;
	static char* severity_strings[];
public:
	/// Determines to what stream respectively progress and errors are logged
	static void SetOutput(std::ostream* l1, std::ostream* l2);
	/// Determines the types of log messages to get logged
	static void Verbosity(Severity v);
	static Severity Verbosity();
	/// Log a message to the output stream
	static void Message(Severity type, const std::string& message, const IfcAbstractEntityPtr entity=0);
	static void Status(const std::string& message, bool new_line=true);
	static std::string Logger::GetLog();
};

#endif
