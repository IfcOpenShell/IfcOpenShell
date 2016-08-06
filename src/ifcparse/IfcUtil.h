﻿/********************************************************************************
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

#include <set>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

#include "ifc_parse_api.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

#include <boost/shared_ptr.hpp>
#include <boost/dynamic_bitset.hpp>
#include <boost/foreach.hpp>

#define foreach BOOST_FOREACH
#define rforeach BOOST_REVERSE_FOREACH

class Argument;
class IfcEntityList;
class IfcEntityListList;
class IfcAbstractEntity;
namespace IfcWrite {
	class IfcWritableEntity;
}

namespace IfcUtil {
	enum ArgumentType {
		Argument_NULL,
		Argument_DERIVED,
		Argument_INT,
		Argument_BOOL,
		Argument_DOUBLE,
		Argument_STRING,
		Argument_BINARY,
		Argument_ENUMERATION, 
		Argument_ENTITY_INSTANCE,

		Argument_AGGREGATE_OF_INT, 
		Argument_AGGREGATE_OF_DOUBLE, 
		Argument_AGGREGATE_OF_STRING,
		Argument_AGGREGATE_OF_BINARY, 
		Argument_AGGREGATE_OF_ENTITY_INSTANCE,
	
		Argument_AGGREGATE_OF_AGGREGATE_OF_INT,
		Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE,
		Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE, 

		Argument_UNKNOWN
	};

    IFC_PARSE_API const char* ArgumentTypeToString(ArgumentType argument_type);

	class IFC_PARSE_API IfcBaseClass {
	public:
        virtual ~IfcBaseClass() {}
		IfcAbstractEntity* entity;
		virtual bool is(IfcSchema::Type::Enum v) const = 0;
		virtual IfcSchema::Type::Enum type() const = 0;

		virtual unsigned int getArgumentCount() const = 0;
		virtual ArgumentType getArgumentType(unsigned int i) const = 0;
		virtual IfcSchema::Type::Enum getArgumentEntity(unsigned int i) const = 0;
		virtual Argument* getArgument(unsigned int i) const = 0;
		virtual const char* getArgumentName(unsigned int i) const = 0;

		template <class T>
		T* as() {
			return is(T::Class()) 
				? static_cast<T*>(this) 
				: static_cast<T*>(0);
		}

		template <class T>
		const T* as() const {
			return is(T::Class()) 
				? static_cast<const T*>(this) 
				: static_cast<const T*>(0);
		}
	};

	class IFC_PARSE_API IfcBaseEntity : public IfcBaseClass {
	};

	// TODO: Investigate whether these should be template classes instead
	class IFC_PARSE_API IfcBaseType : public IfcBaseEntity {
	public:
		unsigned int getArgumentCount() const;
		Argument* getArgument(unsigned int i) const;
		const char* getArgumentName(unsigned int i) const;
		IfcSchema::Type::Enum getArgumentEntity(unsigned int /*i*/) const { return IfcSchema::Type::UNDEFINED; }
	};

	IFC_PARSE_API bool valid_binary_string(const std::string& s);
    /// Replaces spaces and potentially other problem causing characters with underscores.
    IFC_PARSE_API void sanitate_material_name(std::string &str);
    IFC_PARSE_API void escape_xml(std::string &str);
    IFC_PARSE_API void unescape_xml(std::string &str);
}

template <class T>
class IfcTemplatedEntityList;

class IFC_PARSE_API IfcEntityList {
	std::vector<IfcUtil::IfcBaseClass*> ls;
public:
	typedef boost::shared_ptr<IfcEntityList> ptr;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator it;
	void push(IfcUtil::IfcBaseClass* l);
	void push(const ptr& l);
	it begin();
	it end();
	IfcUtil::IfcBaseClass* operator[] (int i);
	unsigned int size() const;
	bool contains(IfcUtil::IfcBaseClass*) const;
	template <class U>
	typename U::list::ptr as() {
		typename U::list::ptr r(new typename U::list);
		const bool all = U::Class() == IfcSchema::Type::UNDEFINED;
		for ( it i = begin(); i != end(); ++ i ) if (all || (*i)->is(U::Class())) r->push((U*)*i);
		return r;
	}
	void remove(IfcUtil::IfcBaseClass*);
	IfcEntityList::ptr filtered(const std::set<IfcSchema::Type::Enum>& entities);
};

template <class T>
class IfcTemplatedEntityList {
	std::vector<T*> ls;
public:
	typedef boost::shared_ptr< IfcTemplatedEntityList<T> > ptr;
	typedef typename std::vector<T*>::const_iterator it;
	void push(T* t) { if (t) { ls.push_back(t); } }
	void push(ptr t) { if (t) { for ( typename T::list::it it = t->begin(); it != t->end(); ++it ) push(*it); } }
	it begin() { return ls.begin(); }
	it end() { return ls.end(); }
	unsigned int size() const { return (unsigned int) ls.size(); }
	IfcEntityList::ptr generalize() {
		IfcEntityList::ptr r (new IfcEntityList());
		for ( it i = begin(); i != end(); ++ i ) r->push(*i);
		return r;
	}
	bool contains(T* t) const { return std::find(ls.begin(), ls.end(), t) != ls.end(); }
	template <class U> 
	typename U::list::ptr as() {
		typename U::list::ptr r(new typename U::list);
		const bool all = U::Class() == IfcSchema::Type::UNDEFINED;
		for ( it i = begin(); i != end(); ++ i ) if (all || (*i)->is(U::Class())) r->push((U*)*i);
		return r;
	}
	void remove(T* t) {
		typename std::vector<T*>::iterator it;
		while ((it = std::find(ls.begin(), ls.end(), t)) != ls.end()) {
			ls.erase(it);
		}
	}
};

template <class T>
class IfcTemplatedEntityListList;

class IFC_PARSE_API IfcEntityListList {
	std::vector< std::vector<IfcUtil::IfcBaseClass*> > ls;
public:
	typedef boost::shared_ptr< IfcEntityListList > ptr;
	typedef std::vector< std::vector<IfcUtil::IfcBaseClass*> >::const_iterator outer_it;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator inner_it;
	void push(const std::vector<IfcUtil::IfcBaseClass*>& l) {
		ls.push_back(l); 
	}
	void push(const IfcEntityList::ptr& l) { 
		if (l) {
			std::vector<IfcUtil::IfcBaseClass*> li;
			for (std::vector<IfcUtil::IfcBaseClass*>::const_iterator jt = l->begin(); jt != l->end(); ++jt) {
				li.push_back(*jt); 
			} 
			push(li); 
		}
	}
	outer_it begin() const { return ls.begin(); }
	outer_it end() const { return ls.end(); }
	int size() const { return (int)ls.size(); }
	int totalSize() const { 
		int accum = 0; 
		for (outer_it it = begin(); it != end(); ++it) { 
			accum += (int)it->size(); 
		} 
		return accum; 
	}
	bool contains(IfcUtil::IfcBaseClass* instance) const {
		for (outer_it it = begin(); it != end(); ++it) {
			const std::vector<IfcUtil::IfcBaseClass*>& inner = *it;
			if (std::find(inner.begin(), inner.end(), instance) != inner.end()) {
				return true;
			}
		}
		return false;
	}
	template <class U> 
	typename IfcTemplatedEntityListList<U>::ptr as() {
		typename IfcTemplatedEntityListList<U>::ptr r(new IfcTemplatedEntityListList<U>);
		const bool all = U::Class() == IfcSchema::Type::UNDEFINED;
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
	typedef typename boost::shared_ptr< IfcTemplatedEntityListList<T> > ptr;
	typedef typename std::vector< std::vector<T*> >::const_iterator outer_it;
	typedef typename std::vector<T*>::const_iterator inner_it;
	void push(const std::vector<T*>& t) {ls.push_back(t);}
	outer_it begin() { return ls.begin(); }
	outer_it end() { return ls.end(); }
	int size() const { return (int)ls.size(); }
	int totalSize() const { 
		int accum = 0; 
		for (outer_it it = begin(); it != end(); ++it) { 
			accum += it->size(); 
		} 
		return accum; 
	}
	bool contains(T* t) const {
		for (outer_it it = begin(); it != end(); ++it) {
			const std::vector<T*>& inner = *it;
			if (std::find(inner.begin(), inner.end(), t) != inner.end()) {
				return true;
			}
		}
		return false;
	}
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

namespace IfcParse {
	class IfcFile;
}

class IFC_PARSE_API Argument {
public:
	virtual operator int() const;
	virtual operator bool() const;
	virtual operator double() const;
	virtual operator std::string() const;
	virtual operator boost::dynamic_bitset<>() const;
	virtual operator IfcUtil::IfcBaseClass*() const;

	virtual operator std::vector<int>() const;
	virtual operator std::vector<double>() const;
	virtual operator std::vector<std::string>() const;
	virtual operator std::vector<boost::dynamic_bitset<> >() const;
	virtual operator IfcEntityList::ptr() const;

	virtual operator std::vector< std::vector<int> >() const;
	virtual operator std::vector< std::vector<double> >() const;
	virtual operator IfcEntityListList::ptr() const;

	virtual bool isNull() const = 0;
	virtual unsigned int size() const = 0;

	virtual IfcUtil::ArgumentType type() const = 0;
	virtual Argument* operator [] (unsigned int i) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
	
	virtual ~Argument() {};
};

class IFC_PARSE_API IfcAbstractEntity {
public:
	IfcParse::IfcFile* file;
	virtual IfcEntityList::ptr getInverse(IfcSchema::Type::Enum type, int attribute_index) = 0;
	virtual std::string datatype() const = 0;
	virtual Argument* getArgument (unsigned int i) = 0;
	virtual unsigned int getArgumentCount() const = 0;
	virtual ~IfcAbstractEntity() {};
	virtual IfcSchema::Type::Enum type() const = 0;
	virtual bool is(IfcSchema::Type::Enum v) const = 0;
	virtual std::string toString(bool upper=false) const = 0;
	virtual unsigned int id() = 0;
	virtual IfcWrite::IfcWritableEntity* isWritable() = 0;
};

#endif
