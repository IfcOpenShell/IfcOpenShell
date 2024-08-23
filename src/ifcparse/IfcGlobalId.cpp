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

#include "IfcGlobalId.h"

#include "IfcException.h"
#include "IfcLogger.h"

#include <algorithm>
#include <boost/lexical_cast.hpp>
#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <boost/version.hpp>
#include <vector>

static const char* chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$";

// Converts an unsigned integer into a base64 string of length l
std::string base64(unsigned value, int length) {
    const int BASE64 = 64;
    std::string result;
    result.reserve(length);
    while (value != 0U) {
        result.push_back(chars[value % BASE64]);
        value /= BASE64;
    }
    while ((int)result.size() != length) {
        result.push_back('0');
    }
    std::reverse(result.begin(), result.end());
    return result;
}

// Converts a base64 string into an unsigned integer
unsigned from_base64(const std::string& string) {
    std::string::size_type zeros = string.find_first_not_of('0');
    unsigned result = 0;
    if (zeros != std::string::npos) {
        for (std::string::const_iterator i = string.begin() + zeros; i != string.end(); ++i) {
            result *= 64;
            const char* character = strchr(chars, *i);
            if (character == nullptr) {
                throw IfcParse::IfcException("Failed to decode GlobalId");
            }
            result += (unsigned)(character - chars);
        }
    }
    return result;
}

// Compresses the UUID byte array into a base64 representation
std::string compress(unsigned char* value) {
    std::string result;
    result.reserve(22);
    result += base64(value[0], 2);
    for (unsigned i = 1; i < 16; i += 3) {
        result += base64((value[i] << 16) + (value[i + 1] << 8) + value[i + 2], 4);
    }
    return result;
}

// Expands the base64 representation into a UUID byte array
void expand(const std::string& s, std::vector<unsigned char>& v) {
    v.push_back((unsigned char)from_base64(s.substr(0, 2)));
    for (unsigned i = 0; i < 5; ++i) {
        unsigned d = from_base64(s.substr(2 + 4 * i, 4));
        for (unsigned j = 0; j < 3; ++j) {
            v.push_back((d >> (8 * (2 - j))) % 256);
        }
    }
}

// A random number generator for the UUID
static boost::uuids::basic_random_generator<boost::mt19937> gen;

IfcParse::IfcGlobalId::IfcGlobalId() {
    uuid_data_ = gen();
    std::vector<unsigned char> v(uuid_data_.size());
    std::copy(uuid_data_.begin(), uuid_data_.end(), v.begin());
    string_data_ = compress(v.data());
#if BOOST_VERSION < 104400
    formatted_string = boost::lexical_cast<std::string>(uuid_data);
#else
    formatted_string_ = boost::uuids::to_string(uuid_data_);
#endif

#ifndef NDEBUG
    std::vector<unsigned char> test_vector;
    expand(string_data_, test_vector);
    boost::uuids::uuid test_uuid;
    std::copy(test_vector.begin(), test_vector.end(), test_uuid.begin());
    if (uuid_data_ != test_uuid) {
        Logger::Message(Logger::LOG_ERROR, "Internal error generating GlobalId");
    }
#endif
}

IfcParse::IfcGlobalId::IfcGlobalId(const std::string& string)
    : string_data_(string) {
    std::vector<unsigned char> result;
    expand(string_data_, result);
    std::copy(result.begin(), result.end(), uuid_data_.begin());
#if BOOST_VERSION < 104400
    formatted_string_ = boost::lexical_cast<std::string>(uuid_data_);
#else
    formatted_string_ = boost::uuids::to_string(uuid_data_);
#endif

#ifndef NDEBUG
    const std::string test_string = compress(&uuid_data_.data[0]);
    if (string_data_ != test_string) {
        Logger::Message(Logger::LOG_ERROR, "Internal error generating GlobalId");
    }
#endif
}

IfcParse::IfcGlobalId::operator const std::string&() const {
    return string_data_;
}

IfcParse::IfcGlobalId::operator const boost::uuids::uuid&() const {
    return uuid_data_;
}

const std::string& IfcParse::IfcGlobalId::formatted() const {
    return formatted_string_;
}
