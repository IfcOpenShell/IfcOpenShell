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

#pragma push_macro("Handle")
#undef Handle

#include <rocksdb/db.h>

#pragma pop_macro("Handle")

#include <boost/optional.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/logic/tribool.hpp>
#include <boost/dynamic_bitset.hpp>

class EnumerationReference {
private:
    const IfcParse::enumeration_type* enumeration_;
    size_t index_;
public:

    EnumerationReference(const IfcParse::enumeration_type* enumeration = nullptr, size_t index = 0)
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

template<typename... Args>
struct parameter_pack {
    static constexpr size_t size = sizeof...(Args);
};

typedef parameter_pack <
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
> type_variant_parameter_pack;

template<typename Pack>
struct pack_to_variant_array;

template<typename... Args>
struct pack_to_variant_array<parameter_pack<Args...>> {
    using type = VariantArray<Args...>;
};

using in_memory_attribute_storage = pack_to_variant_array<type_variant_parameter_pack>::type;

template <typename Pack>
struct TypeEncoder_t;

template <typename... Types>
struct TypeEncoder_t<parameter_pack<Types...>> {
    template <typename U>
    static char encode_type() {
        return 'A' + ::impl::TypeIndex_v<U, Types...>;
    }
};

using TypeEncoder = TypeEncoder_t<type_variant_parameter_pack>;

struct MutableAttributeValue {
    int name_;
    uint8_t index_;
};

namespace IfcParse {
    namespace impl {
        class rocks_db_file_storage;
    }
}


namespace impl {

    // Trait to detect contiguous containers (vector / string)
    template <typename T>
    struct is_contiguous_container : std::false_type {};
    template <typename T, typename Alloc>
    struct is_contiguous_container<std::vector<T, Alloc>> : std::true_type {};
    template <typename CharT, typename Traits, typename Alloc>
    struct is_contiguous_container<std::basic_string<CharT, Traits, Alloc>> : std::true_type {};

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        return false;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && !is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        auto s = sizeof(typename T::value_type) * t.size();
        val.resize(s + 1);
        val[0] = TypeEncoder::encode_type<T>();
        memcpy(val.data() + 1, t.data(), s);
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        val.resize(sizeof(T) + 1);
        val[0] = TypeEncoder::encode_type<T>();
        memcpy(val.data() + 1, &t, sizeof(T));
        return true;
    }

    bool serialize(std::string& val, const Blank& t);

    bool serialize(std::string& val, const Derived& t);
    bool serialize(std::string& val, const empty_aggregate_t& t);
    bool serialize(std::string& val, const empty_aggregate_of_aggregate_t& t);

    bool serialize(std::string& val, const boost::logic::tribool& t);

    bool serialize(std::string& val, const boost::dynamic_bitset<>& t);
    
    bool serialize(std::string& val, const IfcUtil::IfcBaseClass* t);

    bool serialize(std::string& val, const EnumerationReference& v);

    bool serialize(std::string& val, const aggregate_of_instance::ptr& t);

    bool serialize(std::string& val, const aggregate_of_aggregate_of_instance::ptr& t);

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value, int>::type = 0>
    bool deserialize(std::string& val, T& t) {
        // @todo vector of vector
        if (val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        auto s = (val.size() - 1) / sizeof(typename T::value_type);
        t.resize(s);
        memcpy(t.data(), val.data() + 1, s * sizeof(typename T::value_type));
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool deserialize(std::string & val, T & t) {
        if (val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        auto s = (val.size() - 1) / sizeof(T);
        memcpy(&t, val.data() + 1, sizeof(T));
        return true;
    }

    bool deserialize(std::string& val, boost::logic::tribool& t);

    bool deserialize(std::string& val, boost::dynamic_bitset<>& t);

    bool deserialize(std::string& val, aggregate_of_instance::ptr& t);

    bool deserialize(std::string& val, aggregate_of_aggregate_of_instance::ptr& t);
}


// short lived
struct AttributeValue {
    uint8_t index_;
    uint8_t storage_model_ = 0;
    size_t instance_name_;
    // @todo couple with db_ptr;
    IfcParse::schema_definition* schema_;
    union pointer_type {
        const in_memory_attribute_storage* storage_ptr;
        IfcParse::impl::rocks_db_file_storage* db_ptr;
        pointer_type(IfcParse::impl::rocks_db_file_storage* db) : db_ptr(db) {}
        pointer_type(const in_memory_attribute_storage* ims) : storage_ptr(ims) {}
    };
    pointer_type array_;
    
    AttributeValue()
        : index_(0)
        , array_((const in_memory_attribute_storage*)nullptr)
        , storage_model_(0)
    {}

    AttributeValue(const in_memory_attribute_storage* arr, uint8_t index)
        : index_(index)
        , array_(arr)
        , storage_model_(0)
    {}

    AttributeValue(IfcParse::schema_definition* schema, IfcParse::impl::rocks_db_file_storage* db, size_t instance_name, uint8_t index)
        : index_(index)
        , array_(db)
        , storage_model_(1)
        , instance_name_(instance_name)
        , schema_(schema)
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

    operator EnumerationReference() const;

    bool isNull() const;
    unsigned int size() const;

    IfcUtil::ArgumentType type() const;
};

struct rocks_db_attribute_storage {
private:
    // @todo not needed as call always passes through EntityInstanceData
    IfcParse::impl::rocks_db_file_storage* fs_;
    // @todo not needed should be passed from call stack
    const char* prefix_;

    template<typename Visitor, std::size_t Index>
    auto apply_visitor_impl(Visitor&& visitor, std::size_t idx, std::integral_constant<std::size_t, Index>) const {
        return apply_visitor_impl(std::forward<Visitor>(visitor), idx, std::integral_constant<std::size_t, Index - 1>{});
    }

    template<typename Visitor>
    void apply_visitor_impl(Visitor&&, std::size_t, std::integral_constant<std::size_t, 0>) const {
        throw std::runtime_error("Invalid variant index");
    }

public:
    rocks_db_attribute_storage(IfcParse::impl::rocks_db_file_storage* fs, const char* const prefix)
        : fs_(fs)
        , prefix_(prefix)
    {}

    rocks_db_attribute_storage(rocks_db_attribute_storage& other)
        : fs_(other.fs_)
        , prefix_(other.prefix_)
    {}

    rocks_db_attribute_storage(rocks_db_attribute_storage&& other)
        : fs_(other.fs_)
        , prefix_(other.prefix_)
    {}

    rocks_db_attribute_storage& operator=(const rocks_db_attribute_storage& other) {
        if (this != &other) {
            fs_ = other.fs_;
            prefix_ = other.prefix_;
        }
        return *this;
    }

    rocks_db_attribute_storage& operator=(const rocks_db_attribute_storage&& other) {
        if (this != &other) {
            fs_ = other.fs_;
            prefix_ = other.prefix_;
        }
        return *this;
    }

    size_t size() const {
        // @todo is this actually needed?
        return 8;
    }

    template<typename T>
    void set(std::size_t index, const T& value);

    template<typename T>
    bool has(std::size_t index) const {
        // @todo
        return false;
    }

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor, std::size_t index) const {
        return apply_visitor_impl(std::forward<Visitor>(visitor), index, std::integral_constant<std::size_t, type_variant_parameter_pack::size>{});
    }
};

class IFC_PARSE_API IfcEntityInstanceData {
  public:
      std::variant<in_memory_attribute_storage, rocks_db_attribute_storage> storage_;

      IfcEntityInstanceData(in_memory_attribute_storage&& storage)
          : storage_(std::move(storage))
      {}

      IfcEntityInstanceData(rocks_db_attribute_storage&& storage)
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

    template<typename T>
    void set_attribute_value(std::size_t index, T&& value) {
        std::visit([&index, &value](auto& x) {
            return x.set(index, value); 
        }, storage_);
    }

    template<typename T>
    bool has_attribute_value(std::size_t index) const {
        return std::visit([&index](const auto& x) {
            return x.has<T>(index);
        }, storage_);
    }

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor, std::size_t index) const {
        return std::visit([&index, &visitor](const auto& x) {
            return x.apply_visitor(std::forward<Visitor>(visitor), index);
        }, storage_);
    }

    size_t size() const {
        return std::visit([](const auto& x) { return x.size(); }, storage_);
    }

    void toString(std::ostream&, bool upper = false, const IfcParse::entity* ent = nullptr) const;
};

#endif
