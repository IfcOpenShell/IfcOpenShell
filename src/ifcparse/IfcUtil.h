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

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

class Argument;
class IfcEntityList;
class IfcEntityListList;
class IfcAbstractEntity;

namespace IfcUtil {
    enum ArgumentType {
        Argument_INT, Argument_BOOL, Argument_DOUBLE, Argument_STRING, Argument_VECTOR_INT, Argument_VECTOR_DOUBLE, Argument_VECTOR_STRING, Argument_ENTITY, Argument_ENTITY_LIST, Argument_ENTITY_LIST_LIST, Argument_ENUMERATION, Argument_UNKNOWN
    };

	class IfcBaseClass {
	public:
		IfcAbstractEntity* entity;
		virtual bool is(IfcSchema::Type::Enum v) const = 0;
		virtual IfcSchema::Type::Enum type() const = 0;
	};

	class IfcBaseEntity : public IfcBaseClass {
	public:
		virtual unsigned int getArgumentCount() const = 0;
		virtual ArgumentType getArgumentType(unsigned int i) const = 0;
		virtual Argument* getArgument(unsigned int i) const = 0;
		virtual const char* getArgumentName(unsigned int i) const = 0;
	};
}

template <class T>
class IfcTemplatedEntityList;

class IfcEntityList {
	std::vector<IfcUtil::IfcBaseClass*> ls;
public:
	typedef SHARED_PTR<IfcEntityList> ptr;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator it;
	ptr getInverse(IfcSchema::Type::Enum c = IfcSchema::Type::ALL);
	ptr getInverse(IfcSchema::Type::Enum c, int i, const std::string& a);
	void push(IfcUtil::IfcBaseClass* l);
	void push(const ptr& l);
	it begin();
	it end();
	IfcUtil::IfcBaseClass* operator[] (int i);
	int Size() const;
	template <class U>
	typename U::list::ptr as() {
		typename U::list::ptr r(new typename U::list);
		for ( it i = begin(); i != end(); ++ i ) if ((*i)->is(U::Class())) r->push((U*)*i);
		return r;
	}
};

template <class T>
class IfcTemplatedEntityList {
	std::vector<T*> ls;
public:
	typedef SHARED_PTR< IfcTemplatedEntityList<T> > ptr;
	typedef typename std::vector<T*>::const_iterator it;
	inline void push(T* t) {if (t) ls.push_back(t);}
	inline void push(ptr t) { for ( typename T::list::it it = t->begin(); it != t->end(); ++it ) push(*it); }
	inline it begin() { return ls.begin(); }
	inline it end() { return ls.end(); }
	inline unsigned int Size() const { return (unsigned int) ls.size(); }
	IfcEntityList::ptr generalize() {
		IfcEntityList::ptr r (new IfcEntityList());
		for ( it i = begin(); i != end(); ++ i ) r->push(*i);
		return r;
	}
	template <class U> 
	typename U::list::ptr as() {
		typename U::list::ptr r(new typename U::list);
		for ( it i = begin(); i != end(); ++ i ) if ((*i)->is(U::Class())) r->push(*i);
		return r;
	}
};

template <class T>
class IfcTemplatedEntityListList;

class IfcEntityListList {
	std::vector< std::vector<IfcUtil::IfcBaseClass*> > ls;
public:
	typedef SHARED_PTR< IfcEntityListList > ptr;
	typedef std::vector< std::vector<IfcUtil::IfcBaseClass*> >::const_iterator outer_it;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator inner_it;
	void push(const std::vector<IfcUtil::IfcBaseClass*>& l) { 
		ls.push_back(l); 
	}
	void push(const IfcEntityList::ptr& l) { 
		std::vector<IfcUtil::IfcBaseClass*> li;
		for (std::vector<IfcUtil::IfcBaseClass*>::const_iterator jt = l->begin(); jt != l->end(); ++jt) {
			li.push_back(*jt); 
		} 
		push(li); 
	}
	outer_it begin() { return ls.begin(); }
	outer_it end()  { return ls.end(); }
	int Size() const  { return ls.size(); }
	template <class U> 
	typename IfcTemplatedEntityListList<U>::ptr as() {
		typename IfcTemplatedEntityListList<U>::ptr r(new IfcTemplatedEntityListList<U>);
		const bool all = U::Class() == IfcSchema::Type::ALL;
		for (outer_it outer = begin(); outer != end(); ++ outer) {
			const std::vector<IfcUtil::IfcBaseClass*>& from = *outer;
			typename std::vector<U*> to;
			for (inner_it inner = from.begin(); inner != from.end(); ++ inner) {
				if (all || (*inner)->is(U::Class())) to.push_back((U*)*inner);
			}
			r->push(to);
		}
		return r;
	}
};

template <class T>
class IfcTemplatedEntityListList {
	std::vector< std::vector<T*> > ls;
public:
	typedef typename SHARED_PTR< IfcTemplatedEntityListList<T> > ptr;
	typedef typename std::vector< std::vector<T*> >::const_iterator outer_it;
	typedef typename std::vector<T*>::const_iterator inner_it;
	void push(const std::vector<T*>& t) {ls.push_back(t);}
	outer_it begin() { return ls.begin(); }
	outer_it end() { return ls.end(); }
	unsigned int Size() const { return (unsigned int) ls.size(); }
	IfcEntityListList::ptr generalize() {
		IfcEntityListList::ptr r (new IfcEntityListList());
		for (outer_it outer = begin(); outer != end(); ++ outer) {
			const std::vector<T*>& from = *outer;
			std::vector<IfcUtil::IfcBaseClass*> to;
			for (inner_it inner = from.begin(); inner != from.end(); ++ inner) {
				to.push_back(*inner);
			}
			r->push(to);
		}
		return r;
	}
};

namespace IfcUtil {
	class IfcAbstractSelect : public IfcBaseClass {
	public:
		typedef IfcTemplatedEntityList<IfcAbstractSelect> list;
		virtual bool isSimpleType() = 0;
		static IfcSchema::Type::Enum Class() { return IfcSchema::Type::ALL; }
	};
	class IfcEntitySelect : public IfcAbstractSelect {
	public:
		typedef IfcEntitySelect* ptr;
		IfcEntitySelect(IfcBaseClass* b);
		IfcEntitySelect(IfcAbstractEntity* e);
		~IfcEntitySelect();
		bool is(IfcSchema::Type::Enum v) const;
		IfcSchema::Type::Enum type() const;
		bool isSimpleType();
	};
	class IfcArgumentSelect : public IfcAbstractSelect {
		IfcSchema::Type::Enum _type;
		Argument* arg;
	public:
		typedef IfcArgumentSelect* ptr;
		IfcArgumentSelect(IfcSchema::Type::Enum t, Argument* a);
		~IfcArgumentSelect();
		Argument* wrappedValue();
		bool is(IfcSchema::Type::Enum v) const;
		IfcSchema::Type::Enum type() const;
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
	virtual operator IfcUtil::IfcBaseClass*() const = 0;
	//virtual operator IfcUtil::IfcAbstractSelect::ptr() const = 0;
	virtual operator IfcEntityList::ptr() const = 0;
    virtual operator IfcEntityListList::ptr() const = 0;
	virtual unsigned int Size() const = 0;
	virtual Argument* operator [] (unsigned int i) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
	virtual bool isNull() const = 0;
	virtual ~Argument() {};
};

class IfcAbstractEntity {
public:
	IfcParse::IfcFile* file;
	virtual IfcEntityList::ptr getInverse(IfcSchema::Type::Enum c = IfcSchema::Type::ALL) = 0;
	virtual IfcEntityList::ptr getInverse(IfcSchema::Type::Enum c, int i, const std::string& a) = 0;
	virtual std::string datatype() const = 0;
	virtual Argument* getArgument (unsigned int i) = 0;
	virtual unsigned int getArgumentCount() const = 0;
	virtual ~IfcAbstractEntity() {};
	virtual IfcSchema::Type::Enum type() const = 0;
	virtual bool is(IfcSchema::Type::Enum v) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
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
	static const char* severity_strings[];
public:
	/// Determines to what stream respectively progress and errors are logged
	static void SetOutput(std::ostream* l1, std::ostream* l2);
	/// Determines the types of log messages to get logged
	static void Verbosity(Severity v);
	static Severity Verbosity();
	/// Log a message to the output stream
	static void Message(Severity type, const std::string& message, IfcAbstractEntity* entity=0);
	static void Status(const std::string& message, bool new_line=true);
	static void ProgressBar(int progress);
	static std::string GetLog();
};

#endif
