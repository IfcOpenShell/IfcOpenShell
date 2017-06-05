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

#include <vector>
#include <algorithm>

#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <boost/version.hpp>
#include <boost/lexical_cast.hpp>

#include "../ifcparse/IfcGlobalId.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcLogger.h"

static const char* chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$";

// Converts an unsigned integer into a base64 string of length l
std::string base64(unsigned v, int l) {
	std::string r;
	r.reserve(l);
	while ( v ) {
		r.push_back(chars[v%64]);
		v /= 64;
	}
	while ( (int)r.size() != l ) r.push_back('0');
	std::reverse(r.begin(),r.end());
	return r;
}

// Converts a base64 string into an unsigned integer
unsigned from_base64(const std::string& s) {
	std::string::size_type zeros = s.find_first_not_of('0');
	unsigned r = 0;
	if ( zeros != std::string::npos )
		for ( std::string::const_iterator i = s.begin()+zeros; i != s.end(); ++ i ) {
			r *= 64;
			const char* c = strchr(chars,*i);
			if ( !c ) throw IfcParse::IfcException("Failed to decode GlobalId");
			r += (unsigned)(c-chars);
		}
	return r;
}

// Compresses the UUID byte array into a base64 representation
std::string compress(unsigned char* v) {
	std::string r;
	r.reserve(22);
	r += base64(v[0],2);
	for ( unsigned i = 1; i < 16; i += 3 ) {
		r += base64((v[i]<<16) + (v[i+1]<<8) + v[i+2],4);
	}
	return r;
}

// Expands the base64 representation into a UUID byte array
void expand(const std::string& s, std::vector<unsigned char>& v) {
	v.push_back((unsigned char)from_base64(s.substr(0,2)));
	for( unsigned i = 0; i < 5; ++i ) {
		unsigned d = from_base64(s.substr(2+4*i,4));
		for ( unsigned j = 0; j < 3; ++ j ) {
			v.push_back((d>>(8*(2-j))) % 256);
		}
	}
}

// A random number generator for the UUID
static boost::uuids::basic_random_generator<boost::mt19937> gen;

IfcParse::IfcGlobalId::IfcGlobalId() {
	uuid_data = gen();
	std::vector<unsigned char> v(uuid_data.size());
	std::copy(uuid_data.begin(), uuid_data.end(), v.begin());
	string_data = compress(&v[0]);
#if BOOST_VERSION < 104400
	formatted_string = boost::lexical_cast<std::string>(uuid_data);
#else
	formatted_string = boost::uuids::to_string(uuid_data);
#endif

#ifndef NDEBUG
	std::vector<unsigned char> test_vector;
	expand(string_data, test_vector);
	boost::uuids::uuid test_uuid;
	std::copy(test_vector.begin(), test_vector.end(), test_uuid.begin());
	if (uuid_data != test_uuid) {
		Logger::Message(Logger::LOG_ERROR, "Internal error generating GlobalId");
	}
#endif
}

IfcParse::IfcGlobalId::IfcGlobalId(const std::string& s)
	: string_data(s)
{
	std::vector<unsigned char> v;
	expand(string_data, v);
	std::copy(v.begin(), v.end(), uuid_data.begin());
#if BOOST_VERSION < 104400
	formatted_string = boost::lexical_cast<std::string>(uuid_data);
#else
	formatted_string = boost::uuids::to_string(uuid_data);
#endif

#ifndef NDEBUG
	const std::string test_string = compress(&uuid_data.data[0]);
	if (string_data != test_string) {
		Logger::Message(Logger::LOG_ERROR, "Internal error generating GlobalId");
	}
#endif
}

IfcParse::IfcGlobalId::operator const std::string&() const {
	return string_data;
}

IfcParse::IfcGlobalId::operator const boost::uuids::uuid&() const {
	return uuid_data;
}

const std::string& IfcParse::IfcGlobalId::formatted() const {
	return formatted_string;
}
