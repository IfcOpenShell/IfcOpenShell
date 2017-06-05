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

#include <iomanip>
#include <locale>
#include <limits>

#include <boost/algorithm/string.hpp>

#include "../ifcparse/IfcParse.h" 
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcFile.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4-latebound.h"
#else
#include "../ifcparse/Ifc2x3-latebound.h"
#endif

using namespace IfcWrite;

class SizeVisitor : public boost::static_visitor<int> {
public:
	int operator()(const boost::blank& /*i*/) const { return -1; }
	int operator()(const IfcWriteArgument::Derived& /*i*/) const { return -1; }
	int operator()(const int& /*i*/) const { return -1; }
	int operator()(const bool& /*i*/) const { return -1; }
	int operator()(const double& /*i*/) const { return -1; }
	int operator()(const std::string& /*i*/) const { return -1; }
	int operator()(const boost::dynamic_bitset<>& /*i*/) const { return -1; }
	int operator()(const IfcWriteArgument::empty_aggregate_t&) const { return 0; }
	int operator()(const IfcWriteArgument::empty_aggregate_of_aggregate_t&) const { return 0; }
	int operator()(const std::vector<int>& i) const { return (int)i.size(); }
	int operator()(const std::vector<double>& i) const { return (int)i.size(); }
	int operator()(const std::vector< std::vector<int> >& i) const { return (int)i.size(); }
	int operator()(const std::vector< std::vector<double> >& i) const { return (int)i.size(); }
	int operator()(const std::vector<std::string>& i) const { return (int)i.size(); }
	int operator()(const std::vector< boost::dynamic_bitset<> >& i) const { return (int)i.size(); }
	int operator()(const IfcWriteArgument::EnumerationReference& /*i*/) const { return -1; }
	int operator()(const IfcUtil::IfcBaseClass* const& /*i*/) const { return -1; }
	int operator()(const IfcEntityList::ptr& i) const { return i->size(); }
	int operator()(const IfcEntityListList::ptr& i) const { return i->size(); }
};

class StringBuilderVisitor : public boost::static_visitor<void> {
private:
	StringBuilderVisitor(const StringBuilderVisitor&); //N/A
	StringBuilderVisitor& operator =(const StringBuilderVisitor&); //N/A

	std::ostringstream& data;
	template <typename T> void serialize(const std::vector<T>& i) {
		data << "(";
		for (typename std::vector<T>::const_iterator it = i.begin(); it != i.end(); ++it) {
			if (it != i.begin()) data << ",";
			data << *it;
		}
		data << ")";
	}
	// The REAL token definition from the IFC SPF standard does not necessarily match
	// the output of the C++ ostream formatting operation.
	// REAL = [ SIGN ] DIGIT { DIGIT } "." { DIGIT } [ "E" [ SIGN ] DIGIT { DIGIT } ] .
	std::string format_double(const double& d) {
		std::ostringstream oss;
		oss.imbue(std::locale::classic());
		oss << std::setprecision(std::numeric_limits<double>::digits10) << d;
		const std::string str = oss.str();
		oss.str("");
		std::string::size_type e = str.find('e');
		if (e == std::string::npos) {
			e = str.find('E');
		}
		const std::string mantissa = str.substr(0,e);
		oss << mantissa;
		if (mantissa.find('.') == std::string::npos) {
			oss << ".";
		}
		if (e != std::string::npos) {
			oss << "E";
			oss << str.substr(e+1);
		}
		return oss.str();
	}

	std::string format_binary(const boost::dynamic_bitset<>& b) {
		std::ostringstream oss;
		oss.imbue(std::locale::classic());
		oss.put('"');
		oss << std::hex << std::setw(1);
		unsigned c = (unsigned)b.size();
		unsigned n = (4 - (c % 4)) & 3;
		oss << n;
		for (unsigned i = 0; i < c + n;) {
			unsigned accum = 0;
			for (int j = 0; j < 4; ++j, ++i) {
				unsigned bit = i < n ? 0 : b.test(c - i + n - 1) ? 1 : 0;
				accum |= bit << (3-j);
			}
			oss << accum;
		}
		oss.put('"');
		return oss.str();
	}

	bool upper;
public:
	StringBuilderVisitor(std::ostringstream& stream, bool upper = false) 
		: data(stream), upper(upper) {}
	void operator()(const boost::blank& /*i*/) { data << "$"; }
	void operator()(const IfcWriteArgument::Derived& /*i*/) { data << "*"; }
	void operator()(const int& i) { data << i; }
	void operator()(const bool& i) { data << (i ? ".T." : ".F."); }
	void operator()(const double& i) { data << format_double(i); }
	void operator()(const boost::dynamic_bitset<>& i) { data << format_binary(i); }
	void operator()(const std::string& i) { 
		std::string s = i;
		if (upper) {
			data << static_cast<std::string>(IfcCharacterEncoder(s));
		} else {
			data << '\'' << s << '\'';
		}
	}
	void operator()(const std::vector<int>& i);
	void operator()(const std::vector<double>& i);
	void operator()(const std::vector<std::string>& i);
	void operator()(const std::vector< boost::dynamic_bitset<> >& i);
	void operator()(const IfcWriteArgument::EnumerationReference& i) {
		data << "." << i.enumeration_value << ".";
	}
	void operator()(const IfcUtil::IfcBaseClass* const& i) { 
		IfcEntityInstanceData* e = i->entity;
		if ( IfcSchema::Type::IsSimple(e->type()) ) {
			data << e->toString(upper);
		} else {
			data << "#" << e->id();
		}
	}
	void operator()(const IfcEntityList::ptr& i) { 
		data << "(";
		for (IfcEntityList::it it = i->begin(); it != i->end(); ++it) {
			if (it != i->begin()) data << ",";
			(*this)(*it);
		}
		data << ")";
	}
	void operator()(const std::vector< std::vector<int> >& i);
	void operator()(const std::vector< std::vector<double> >& i);
	void operator()(const IfcEntityListList::ptr& i) { 
		data << "(";
		for (IfcEntityListList::outer_it outer_it = i->begin(); outer_it != i->end(); ++outer_it) {
			if (outer_it != i->begin()) data << ",";
			data << "(";
			for (IfcEntityListList::inner_it inner_it = outer_it->begin(); inner_it != outer_it->end(); ++inner_it) {
				if (inner_it != outer_it->begin()) data << ",";
				(*this)(*inner_it);
			}
			data << ")";
		}
		data << ")";
	}
	void operator()(const IfcWriteArgument::empty_aggregate_t&) const { data << "()"; }
	void operator()(const IfcWriteArgument::empty_aggregate_of_aggregate_t&) const { data << "()"; }
	operator std::string() { return data.str(); }
};

template <>
void StringBuilderVisitor::serialize(const std::vector<std::string>& i) {
	data << "(";
	for (std::vector<std::string>::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		std::string s = IfcCharacterEncoder(*it);
		data << s;
	}
	data << ")";
}

template <>
void StringBuilderVisitor::serialize(const std::vector<double>& i) {
	data << "(";
	for (std::vector<double>::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		data << format_double(*it);
	}
	data << ")";
}

template <>
void StringBuilderVisitor::serialize(const std::vector< boost::dynamic_bitset<> >& i) {
	data << "(";
	for (std::vector< boost::dynamic_bitset<> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		data << format_binary(*it);
	}
	data << ")";
}

void StringBuilderVisitor::operator()(const std::vector<int>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector<double>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector<std::string>& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector< boost::dynamic_bitset<> >& i) { serialize(i); }
void StringBuilderVisitor::operator()(const std::vector< std::vector<int> >& i) {
	data << "(";
	for (std::vector< std::vector<int> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		serialize(*it);
	}
	data << ")";
}
void StringBuilderVisitor::operator()(const std::vector< std::vector<double> >& i) {
	data << "(";
	for (std::vector< std::vector<double> >::const_iterator it = i.begin(); it != i.end(); ++it) {
		if (it != i.begin()) data << ",";
		serialize(*it);
	}
	data << ")";
}

IfcWriteArgument::operator int() const { return as<int>(); }
IfcWriteArgument::operator bool() const { return as<bool>(); }
IfcWriteArgument::operator double() const { return as<double>(); }
IfcWriteArgument::operator std::string() const { 
	if (type() == IfcUtil::Argument_ENUMERATION) {
		return as<EnumerationReference>().enumeration_value;
	}
	return as<std::string>(); 
}
IfcWriteArgument::operator IfcUtil::IfcBaseClass*() const { return as<IfcUtil::IfcBaseClass*>(); }
IfcWriteArgument::operator boost::dynamic_bitset<>() const { return as< boost::dynamic_bitset<> >(); }
IfcWriteArgument::operator std::vector<double>() const { return as<std::vector<double> >(); }
IfcWriteArgument::operator std::vector<int>() const { return as<std::vector<int> >(); }
IfcWriteArgument::operator std::vector<std::string>() const { return as<std::vector<std::string > >(); }
IfcWriteArgument::operator std::vector< boost::dynamic_bitset<> >() const { return as< std::vector< boost::dynamic_bitset<> > >(); }
IfcWriteArgument::operator IfcEntityList::ptr() const { return as<IfcEntityList::ptr>(); }
IfcWriteArgument::operator std::vector< std::vector<int> >() const { return as<std::vector< std::vector<int> > >(); }
IfcWriteArgument::operator std::vector< std::vector<double> >() const { return as<std::vector< std::vector<double> > >(); }
IfcWriteArgument::operator IfcEntityListList::ptr() const { return as<IfcEntityListList::ptr>(); }
bool IfcWriteArgument::isNull() const { return type() == IfcUtil::Argument_NULL; }
Argument* IfcWriteArgument::operator [] (unsigned int /*i*/) const { throw IfcParse::IfcException("Invalid cast"); }
std::string IfcWriteArgument::toString(bool upper) const {
	std::ostringstream str;
	str.imbue(std::locale::classic());
	StringBuilderVisitor v(str, upper);
	container.apply_visitor(v);
	return v;
}
unsigned int IfcWriteArgument::size() const {
	SizeVisitor v;
	const int size = container.apply_visitor(v);
	if (size == -1) {
		throw IfcParse::IfcException("Invalid cast");
	} else {
		return size;
	}
}

IfcUtil::ArgumentType IfcWriteArgument::type() const {
	return static_cast<IfcUtil::ArgumentType>(container.which());
}

// Overload to detect null values
void IfcWriteArgument::set(const IfcEntityList::ptr& v) {
	if (v) {
		container = v;
	} else {
		container = boost::blank();
	}
}

// Overload to detect null values
void IfcWriteArgument::set(const IfcEntityListList::ptr& v) {
	if (v) {
		container = v;
	} else {
		container = boost::blank();
	}
}

// Overload to detect null values
void IfcWriteArgument::set(IfcUtil::IfcBaseClass*const& v) {
	if (v) {
		container = v;
	} else {
		container = boost::blank();
	}
}