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

#ifdef IFOPSH_WITH_ROCKSDB

#pragma push_macro("Handle")
#undef Handle

#include <rocksdb/db.h>

#pragma pop_macro("Handle")

#endif

#include <boost/optional.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/logic/tribool.hpp>
#include <boost/dynamic_bitset.hpp>

class IFC_PARSE_API EnumerationReference {
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
class IFC_PARSE_API Blank {};
class IFC_PARSE_API Derived {};
class IFC_PARSE_API empty_aggregate_t {};
class IFC_PARSE_API empty_aggregate_of_aggregate_t {};

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

struct IFC_PARSE_API MutableAttributeValue {
    int name_;
    uint8_t index_;
};

namespace IfcParse {
    namespace impl {
        class IFC_PARSE_API rocks_db_file_storage;
    }
}

#if IFOPSH_WITH_ROCKSDB

namespace impl {

    // Trait to detect contiguous containers (vector / string)
    template <typename T>
    struct is_contiguous_container : std::false_type {};
    template <typename T, typename Alloc>
    struct is_contiguous_container<std::vector<T, Alloc>> : std::true_type {};
    template <typename CharT, typename Traits, typename Alloc>
    struct is_contiguous_container<std::basic_string<CharT, Traits, Alloc>> : std::true_type {};

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && !is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        auto s = sizeof(typename T::value_type) * t.size();
        val.resize(s + 1);
        val[0] = TypeEncoder::encode_type<T>();
        memcpy(val.data() + 1, t.data(), s);
        return true;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value&& is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& val, const T& t) {
        val = std::string(1, TypeEncoder::encode_type<T>());
        for (auto& tt : t) {
            std::string v2;
            serialize(v2, tt);
            std::string len(sizeof(size_t), 0);
            size_t s = v2.size() - 1;
            memcpy(len.data(), &s, sizeof(size_t));
            // @todo horribly inefficient
            // @todo strip off type label?
            val += len + v2.substr(1);
        }
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

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && !is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, T& t, bool prefixed = true) {
        if (prefixed && val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        auto s = (val.size() - (prefixed ? 1 : 0)) / sizeof(typename T::value_type);
        t.resize(s);
        memcpy(t.data(), val.data() + (prefixed ? 1 : 0), s * sizeof(typename T::value_type));
        return true;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool deserialize(IfcParse::impl::rocks_db_file_storage* storage, const std::string& val, T& t) {
        // @todo
        auto ptr = val.data();
        if (*ptr != TypeEncoder::encode_type<T>()) {
            return false;
        }
        ptr++;
        t.clear();
        while (ptr < val.data() + val.size()) {
            size_t s;
            memcpy(&s, ptr, sizeof(size_t));
            // @todo view
            ptr += sizeof(size_t);
            std::string part(ptr, s);
            t.emplace_back();
            deserialize(storage, part, t.back(), false);
            ptr += s;
        }
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, T & t) {
        if (val[0] != TypeEncoder::encode_type<T>()) {
            return false;
        }
        memcpy(&t, val.data() + 1, sizeof(T));
        return true;
    }

    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, boost::logic::tribool& t);

    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, boost::dynamic_bitset<>& t);

    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, aggregate_of_instance::ptr& t);

    bool deserialize(IfcParse::impl::rocks_db_file_storage*, const std::string& val, aggregate_of_aggregate_of_instance::ptr& t);
}

#endif

// short lived
struct IFC_PARSE_API AttributeValue {
    uint8_t index_;
    uint8_t storage_model_ = 0;
    const IfcParse::declaration* entity_or_type_ = 0;
    size_t instance_name_;
    union pointer_type {
        const in_memory_attribute_storage* storage_ptr;
        IfcParse::impl::rocks_db_file_storage* db_ptr;
        pointer_type(IfcParse::impl::rocks_db_file_storage* db) : db_ptr(db) {}
        pointer_type(const in_memory_attribute_storage* ims) : storage_ptr(ims) {}
    };
    pointer_type array_;
    
    AttributeValue()
        : index_(0)
        , storage_model_(0)
        , array_((const in_memory_attribute_storage*)nullptr)
    {}

    AttributeValue(const in_memory_attribute_storage* arr, uint8_t index)
        : index_(index)
        , storage_model_(0)
        , array_(arr)
    {}

    AttributeValue(IfcParse::impl::rocks_db_file_storage* db, size_t instance_name, const IfcParse::declaration* entity_or_type, uint8_t index)
        : index_(index)
        , storage_model_(1)
        , entity_or_type_(entity_or_type)
        , instance_name_(instance_name)
        , array_(db)
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

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor) const {
        switch (type()) {
            case IfcUtil::Argument_DERIVED:
                return visitor(Derived{});
            case IfcUtil::Argument_INT:
                return visitor((int)*this);
            case IfcUtil::Argument_BOOL:
                return visitor((bool)*this);
            case IfcUtil::Argument_LOGICAL: {
                boost::logic::tribool tb = *this;
                return visitor(tb);
            }
            case IfcUtil::Argument_DOUBLE:
                return visitor((double)*this);
            case IfcUtil::Argument_STRING:
                return visitor((std::string)*this);
            case IfcUtil::Argument_BINARY:
                return visitor((boost::dynamic_bitset<>)*this);
            case IfcUtil::Argument_ENUMERATION:
                return visitor((EnumerationReference)*this);
            case IfcUtil::Argument_ENTITY_INSTANCE:
                return visitor((IfcUtil::IfcBaseClass*)*this);
            case IfcUtil::Argument_AGGREGATE_OF_INT:
                return visitor((std::vector<int>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_DOUBLE:
                return visitor((std::vector<double>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_STRING:
                return visitor((std::vector<std::string>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_BINARY:
                return visitor((std::vector<boost::dynamic_bitset<>>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE:
                return visitor((boost::shared_ptr<aggregate_of_instance>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT:
                return visitor((std::vector<std::vector<int>>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE:
                return visitor((std::vector<std::vector<double>>)*this);
            case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE:
                return visitor((boost::shared_ptr<aggregate_of_aggregate_of_instance>)*this);
            case IfcUtil::Argument_EMPTY_AGGREGATE:
                return visitor(empty_aggregate_t{});
            case IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE:
                return visitor(empty_aggregate_of_aggregate_t{});
            default:
                return visitor(Blank{});
        }
    }
};


struct IFC_PARSE_API rocks_db_attribute_storage {
public:
#ifdef IFOPSH_WITH_ROCKSDB
    // @todo void* is obviously very ugly here
    template<typename T>
    IFC_PARSE_API void set(void* storage, const IfcParse::declaration*, std::size_t identity, std::size_t index, const T& value);

    template<typename T>
    IFC_PARSE_API bool has(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index) const;

    template<typename Visitor>
    auto apply_visitor(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index, Visitor&& visitor) const {
        // @todo do we need visitation on all data/storage/attribute levels?
        AttributeValue((IfcParse::impl::rocks_db_file_storage*)storage, identity, decl, (uint8_t) index).apply_visitor(std::forward<Visitor>(visitor));
    }
#endif
};

class IFC_PARSE_API IfcEntityInstanceData {
  public:
      // Since rocks_db_attribute_storage has no members this is not a variant<in_memory, rocks> but in_memory*, where nullptr means a rocks_db_attribute_storage is constructed on the fly given the context from instance data.
      in_memory_attribute_storage* storage_;

      IfcEntityInstanceData(in_memory_attribute_storage&& storage)
          : storage_(new in_memory_attribute_storage(std::move(storage)))
      {}

      IfcEntityInstanceData(rocks_db_attribute_storage&&)
          : storage_(nullptr)
      {}

      IfcEntityInstanceData(IfcEntityInstanceData&& other) noexcept
          : storage_(std::exchange(other.storage_, nullptr))
      {}

      // No copy-constructor/-assignment anymore because we need the instance for storage model context
      IfcEntityInstanceData(const IfcEntityInstanceData&) = delete;
      IfcEntityInstanceData& operator=(const IfcEntityInstanceData&) = delete;

      IfcEntityInstanceData& operator=(IfcEntityInstanceData&& other) noexcept {
          if (this != &other) {
              delete storage_;
              storage_ = std::exchange(other.storage_, nullptr);
          }
          return *this;
      }

      ~IfcEntityInstanceData() {
          delete storage_;
      }

    AttributeValue get_attribute_value(void* storage, const IfcParse::declaration*, std::size_t identity, size_t index) const;

    template<typename T>
    void set_attribute_value(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index, T&& value) {
        if (storage_) {
            storage_->set(index, value);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            rocks_db_attribute_storage{}.set(storage, decl, identity, index, value);
        }
#endif
    }

    template<typename T>
    bool has_attribute_value(void* storage, const IfcParse::declaration* decl, std::size_t identity, std::size_t index) const {
        if (storage_) {
            return storage_->has<T>(index);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            return rocks_db_attribute_storage{}.has<T>(storage, decl, identity, index);
        }
#endif
    }

    template<typename Visitor>
    auto apply_visitor(void* storage, const IfcParse::declaration* decl, std::size_t identity, Visitor&& visitor, std::size_t index) const {
        if (storage_) {
            return storage_->apply_visitor(std::forward<Visitor>(visitor), index);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            return rocks_db_attribute_storage{}.apply_visitor(storage, decl, identity, index, std::forward<Visitor>(visitor));
        }
#endif
    }

    void toString(void* storage, const IfcParse::declaration*, std::size_t identity, std::ostream&, bool upper = false) const;
};

#endif
