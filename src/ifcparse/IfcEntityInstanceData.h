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

#ifndef IFCENTITYINSTANCEDATA_H
#define IFCENTITYINSTANCEDATA_H

#include "ArgumentType.h"
#include "variantarray.h"
#include "aggregate_of_instance.h"
#include "IfcSchema.h"

#include <boost/optional.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/logic/tribool.hpp>
#include <boost/dynamic_bitset.hpp>

class EnumerationReference {
private:
    const IfcParse::enumeration_type* enumeration_;
    size_t index_;
public:

    EnumerationReference(const IfcParse::enumeration_type* enumeration, size_t index)
        : enumeration_(enumeration)
        , index_(index)
    {}

    const char* value() const {
        return enumeration_->lookup_enum_value(index_);
    }

    size_t index() const {
        return index_;
    }

    const IfcParse::enumeration_type* enumeration() const {
        return enumeration_;
    }
};
class Blank {};
class Derived {};
class empty_aggregate_t {};
class empty_aggregate_of_aggregate_t {};

typedef VariantArray <
    // A null argument, it will always serialize to $
    Blank,
    // @todo Derived is not really necessary anymore, just serialize correctly based on schema
    // A derived argument, it will always serialize to *
    Derived,
    // An integer argument, e.g. 123

    // SCALARS:
    int,
    // A boolean argument, it will serialize to either .T. or .F.
    bool,
    // A logical argument, it will serialize to either .T. or .F. or .U.
    boost::logic::tribool,
    // A floating point argument, e.g. 12.3
    double,
    // A character string argument, e.g. 'IfcOpenShell'
    std::string,
    // A binary argument, e.g. "092A" -> 100100101010
    boost::dynamic_bitset<>,
    // An enumeration argument, e.g. .USERDEFINED.
    // To initialize the argument a string representation
    // has to be explicitly passed of the enumeration value
    // which is stored internally as an integer. The argument
    // itself does not keep track of what schema enumeration
    // type is represented.
    EnumerationReference,
    // An entity instance argument. It will either serialize to
    // e.g. #123 or datatype identifier for simple types, e.g.
    // IFCREAL(12.3)
    IfcUtil::IfcBaseClass*,

    // AGGREGATES:
    empty_aggregate_t,
    // An aggregate of integers, e.g. (1,2,3)
    std::vector<int>,
    // An aggregate of floats, e.g. (12.3,4.)
    std::vector<double>,
    // An aggregate of strings, e.g. ('Ifc','Open','Shell')
    std::vector<std::string>,
    // An aggregate of binaries, e.g. ("23B", "092A") -> (111011, 100100101010)
    std::vector<boost::dynamic_bitset<>>,
    // An aggregate of entity instances. It will either serialize to
    // e.g. (#1,#2,#3) or datatype identifier for simple types,
    // e.g. (IFCREAL(1.2),IFCINTEGER(3.))
    aggregate_of_instance::ptr,

    // AGGREGATES OF AGGREGATES:
    empty_aggregate_of_aggregate_t,
    // An aggregate of an aggregate of ints. E.g. ((1, 2), (3))
    std::vector<std::vector<int>>,
    // An aggregate of an aggregate of floats. E.g. ((1., 2.3), (4.))
    std::vector<std::vector<double>>,
    // An aggregate of an aggregate of entities. E.g. ((#1, #2), (#3))
    aggregate_of_aggregate_of_instance::ptr
> storage_t;

struct MutableAttributeValue {
    int name_;
    uint8_t index_;
};

// short lived
struct AttributeValue {
    const storage_t* array_;
    uint8_t index_;

    AttributeValue()
        : array_(nullptr)
        , index_(0)
    {}

    AttributeValue(const storage_t* arr, uint8_t index)
        : array_(arr)
        , index_(index)
    {}

    operator int() const;
    operator bool() const;
    operator boost::logic::tribool() const;
    operator double() const;
    operator std::string() const;
    operator boost::dynamic_bitset<>() const;
    operator IfcUtil::IfcBaseClass* () const;

    operator std::vector<int>() const;
    operator std::vector<double>() const;
    operator std::vector<std::string>() const;
    operator std::vector<boost::dynamic_bitset<>>() const;
    operator boost::shared_ptr<aggregate_of_instance>() const;

    operator std::vector<std::vector<int>>() const;
    operator std::vector<std::vector<double>>() const;
    operator boost::shared_ptr<aggregate_of_aggregate_of_instance>() const;

    bool isNull() const;
    unsigned int size() const;

    IfcUtil::ArgumentType type() const;
};

class IFC_PARSE_API IfcEntityInstanceData {
  public:
      storage_t storage_;

      IfcEntityInstanceData(storage_t&& storage)
          : storage_(std::move(storage))
      {}

      IfcEntityInstanceData(IfcEntityInstanceData&& other) noexcept
          : storage_(std::move(other.storage_))
      {}

      IfcEntityInstanceData(const IfcEntityInstanceData& data);

      IfcEntityInstanceData& operator=(IfcEntityInstanceData&& other) {
          if (this != &other) {
              storage_ = std::move(other.storage_);
          }
          return *this;
      }

    AttributeValue get_attribute_value(size_t index) const;

    /*
    template <typename T>
    void set_attribute_value(size_t index, const T& t);

    void set_attribute_value(size_t index, AttributeValue&, IfcUtil::ArgumentType attr_type = IfcUtil::Argument_UNKNOWN);
    */

    size_t size() const {
        return storage_.size();
    }

    void toString(std::ostream&, bool upper = false, const IfcParse::entity* ent = nullptr) const;
};

#endif
