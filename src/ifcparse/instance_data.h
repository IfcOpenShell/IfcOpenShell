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

#ifndef InstanceData_H
#define InstanceData_H

#include "express.h"
#include "argument_type.h"
#include "variant_array.h"
#include "schema.h"
#include "storage.h"

#ifdef IFOPSH_WITH_ROCKSDB

#pragma push_macro("Handle")
#undef Handle

#include <rocksdb/db.h>

#pragma pop_macro("Handle")

#endif

#include <cstdint>
#include <cstring>

#include <boost/optional.hpp>
#include <memory>
#include <boost/logic/tribool.hpp>
#include <boost/dynamic_bitset.hpp>

namespace ifcopenshell {

class IFC_PARSE_API enumeration_reference {
private:
    const ifcopenshell::enumeration_type* enumeration_;
    size_t index_;
public:

    enumeration_reference(const ifcopenshell::enumeration_type* enumeration = nullptr, size_t index = 0)
        : enumeration_(enumeration)
        , index_(index)
    {}

    const char* value() const {
        return enumeration_->lookup_enum_value(index_);
    }

    size_t index() const {
        return index_;
    }

    const ifcopenshell::enumeration_type* enumeration() const {
        return enumeration_;
    }
};
class IFC_PARSE_API blank {};
class IFC_PARSE_API derived {};
class IFC_PARSE_API empty_aggregate {};
class IFC_PARSE_API empty_aggregate_of_aggregate {};

} // namespace ifcopenshell

namespace impl {
    template <>
    struct variant_type_name<ifcopenshell::blank> {
        static std::string get() { return "null"; }
    };

    template <>
    struct variant_type_name<ifcopenshell::derived> {
        static std::string get() { return "derived"; }
    };

    template <>
    struct variant_type_name<int> {
        static std::string get() { return "int"; }
    };

    template <>
    struct variant_type_name<int64_t> {
        static std::string get() { return "int"; }
    };

    template <>
    struct variant_type_name<bool> {
        static std::string get() { return "bool"; }
    };

    template <>
    struct variant_type_name<boost::logic::tribool> {
        static std::string get() { return "logical"; }
    };

    template <>
    struct variant_type_name<double> {
        static std::string get() { return "real"; }
    };

    template <>
    struct variant_type_name<std::string> {
        static std::string get() { return "string"; }
    };

    template <>
    struct variant_type_name<boost::dynamic_bitset<>> {
        static std::string get() { return "binary"; }
    };

    template <>
    struct variant_type_name<ifcopenshell::enumeration_reference> {
        static std::string get() { return "enumeration"; }
    };

    template <>
    struct variant_type_name<express::base> {
        static std::string get() { return "instance"; }
    };

    template <>
    struct variant_type_name<ifcopenshell::empty_aggregate> {
        static std::string get() { return "aggregate"; }
    };

    template <typename T, typename Allocator>
    struct variant_type_name<std::vector<T, Allocator>> {
        static std::string get() { return "aggregate of " + variant_type_name<T>::get(); }
    };

    template <>
    struct variant_type_name<ifcopenshell::empty_aggregate_of_aggregate> {
        static std::string get() { return "aggregate of aggregate"; }
    };
}

namespace ifcopenshell {

template<typename... Args>
struct parameter_pack {
    static constexpr size_t size = sizeof...(Args);
};

typedef parameter_pack <
    // A null argument, it will always serialize to $
    blank,
    // @todo derived is not really necessary anymore, just serialize correctly based on schema
    // A derived argument, it will always serialize to *
    derived,
    // An integer argument, e.g. 123

    // SCALARS:
    // Stored as int64_t so integer attributes (IfcInteger, IfcTimeStamp)
    // can hold values outside the signed 32-bit range.
    int64_t,
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
    enumeration_reference,
    // An entity instance argument. It will either serialize to
    // e.g. #123 or datatype identifier for simple types, e.g.
    // IFCREAL(12.3)
    express::base,

    // AGGREGATES:
    empty_aggregate,
    // An aggregate of integers, e.g. (1,2,3). Stored as int64_t for the
    // same reason as the scalar int64_t above.
    std::vector<int64_t>,
    // An aggregate of floats, e.g. (12.3,4.)
    std::vector<double>,
    // An aggregate of strings, e.g. ('Ifc','Open','Shell')
    std::vector<std::string>,
    // An aggregate of binaries, e.g. ("23B", "092A") -> (111011, 100100101010)
    std::vector<boost::dynamic_bitset<>>,
    // An aggregate of entity instances. It will either serialize to
    // e.g. (#1,#2,#3) or datatype identifier for simple types,
    // e.g. (IFCREAL(1.2),IFCINTEGER(3.))
    std::vector<express::base>,

    // AGGREGATES OF AGGREGATES:
    empty_aggregate_of_aggregate,
    // An aggregate of an aggregate of ints. E.g. ((1, 2), (3))
    std::vector<std::vector<int64_t>>,
    // An aggregate of an aggregate of floats. E.g. ((1., 2.3), (4.))
    std::vector<std::vector<double>>,
    // An aggregate of an aggregate of entities. E.g. ((#1, #2), (#3))
    std::vector<std::vector<express::base>>>
type_variant_parameter_pack;

template<typename Pack>
struct pack_to_variant_array;

template<typename... Args>
struct pack_to_variant_array<parameter_pack<Args...>> {
    using type = variant_array<Args...>;
};

using in_memory_attribute_storage = pack_to_variant_array<type_variant_parameter_pack>::type;

template <typename Pack>
struct type_encoder_impl;

template <typename... Types>
struct type_encoder_impl<parameter_pack<Types...>> {
    template <typename U>
    static char encode_type() {
        return 'A' + ::impl::TypeIndex_v<U, Types...>;
    }
};

using type_encoder = type_encoder_impl<type_variant_parameter_pack>;

class IFC_PARSE_API mutable_attribute_value {
  public:
    uint32_t name_;
    uint8_t index_;
};

} // namespace ifcopenshell

#ifdef IFOPSH_WITH_ROCKSDB

namespace impl {

    // Trait to detect contiguous containers (vector / string)
    template <typename T>
    struct is_contiguous_container : std::false_type {};
    template <typename T, typename Alloc>
    struct is_contiguous_container<std::vector<T, Alloc>> : std::true_type {};
    template <typename CharT, typename Traits, typename Alloc>
    struct is_contiguous_container<std::basic_string<CharT, Traits, Alloc>> : std::true_type {};

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && !is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& buffer, const T& value) {
        auto byte_count = sizeof(typename T::value_type) * value.size();
        buffer.resize(byte_count + 1);
        buffer[0] = ifcopenshell::type_encoder::encode_type<T>();
        memcpy(buffer.data() + 1, value.data(), byte_count);
        return true;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value&& is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool serialize(std::string& buffer, const T& value) {
        buffer = std::string(1, ifcopenshell::type_encoder::encode_type<T>());
        for (auto& nested_value : value) {
            std::string nested_buffer;
            serialize(nested_buffer, nested_value);
            std::string encoded_length(sizeof(size_t), 0);
            size_t payload_size = nested_buffer.size() - 1;
            memcpy(encoded_length.data(), &payload_size, sizeof(size_t));
            // @todo horribly inefficient
            // @todo strip off type label?
            buffer += encoded_length + nested_buffer.substr(1);
        }
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool serialize(std::string& buffer, const T& value) {
        buffer.resize(sizeof(T) + 1);
        buffer[0] = ifcopenshell::type_encoder::encode_type<T>();
        memcpy(buffer.data() + 1, &value, sizeof(T));
        return true;
    }

    bool serialize(std::string& buffer, const ifcopenshell::blank& value);

    bool serialize(std::string& buffer, const ifcopenshell::derived& value);
    bool serialize(std::string& buffer, const ifcopenshell::empty_aggregate& value);
    bool serialize(std::string& buffer, const ifcopenshell::empty_aggregate_of_aggregate& value);

    bool serialize(std::string& buffer, const boost::logic::tribool& value);

    bool serialize(std::string& buffer, const boost::dynamic_bitset<>& value);

    bool serialize(std::string& buffer, const express::base& value);

    bool serialize(std::string& buffer, const ifcopenshell::enumeration_reference& value);

    bool serialize(std::string& buffer, const std::vector<express::base>& value);

    bool serialize(std::string& buffer, const std::vector<std::vector<express::base>>& value);

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && !is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, T& value, bool has_type_prefix = true) {
        static_cast<void>(storage);
        if (has_type_prefix && buffer[0] != ifcopenshell::type_encoder::encode_type<T>()) {
            return false;
        }
        auto element_count = (buffer.size() - (has_type_prefix ? 1 : 0)) / sizeof(typename T::value_type);
        value.resize(element_count);
        memcpy(value.data(), buffer.data() + (has_type_prefix ? 1 : 0), element_count * sizeof(typename T::value_type));
        return true;
    }

    template <typename T, typename std::enable_if<is_contiguous_container<T>::value && is_contiguous_container<typename T::value_type>::value, int>::type = 0>
    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, T& value) {
        // @todo
        auto ptr = buffer.data();
        if (*ptr != ifcopenshell::type_encoder::encode_type<T>()) {
            return false;
        }
        ptr++;
        value.clear();
        while (ptr < buffer.data() + buffer.size()) {
            size_t payload_size;
            memcpy(&payload_size, ptr, sizeof(size_t));
            // @todo view
            ptr += sizeof(size_t);
            std::string part(ptr, payload_size);
            value.emplace_back();
            deserialize(storage, part, value.back(), false);
            ptr += payload_size;
        }
        return true;
    }

    template <typename T, typename std::enable_if<std::is_integral_v<T> || std::is_floating_point_v<T>, int>::type = 0>
    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, T& value) {
        static_cast<void>(storage);
        if (buffer[0] != ifcopenshell::type_encoder::encode_type<T>()) {
            return false;
        }
        memcpy(&value, buffer.data() + 1, sizeof(T));
        return true;
    }

    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, boost::logic::tribool& value);

    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, boost::dynamic_bitset<>& value);

    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, std::vector<express::base>& value);

    bool deserialize(ifcopenshell::impl::rocks_db_file_storage* storage, const std::string& buffer, std::vector<std::vector<express::base>>& value);
    }

#endif

namespace ifcopenshell {

// short lived
class IFC_PARSE_API attribute_value {
    uint8_t index_;
    uint8_t storage_model_ = 0;
    const ifcopenshell::declaration* entity_or_type_ = 0;
    size_t instance_name_;

  public:
    union pointer_type {
        const in_memory_attribute_storage* storage_ptr;
        ifcopenshell::impl::rocks_db_file_storage* db_ptr;
        pointer_type(ifcopenshell::impl::rocks_db_file_storage* storage) : db_ptr(storage) {}
        pointer_type(const in_memory_attribute_storage* storage) : storage_ptr(storage) {}
    };

private:
    pointer_type array_;

public:
    attribute_value()
        : index_(0)
        , storage_model_(0)
        , array_((const in_memory_attribute_storage*)nullptr)
    {}

    attribute_value(const in_memory_attribute_storage* storage, uint8_t index)
        : index_(index)
        , storage_model_(0)
        , array_(storage)
    {}

    attribute_value(ifcopenshell::impl::rocks_db_file_storage* storage, size_t instance_name, const ifcopenshell::declaration* entity_or_type, uint8_t index)
        : index_(index)
        , storage_model_(1)
        , entity_or_type_(entity_or_type)
        , instance_name_(instance_name)
        , array_(storage)
    {}

    operator int64_t() const;
    operator bool() const;
    operator boost::logic::tribool() const;
    operator double() const;
    operator std::string() const;
    operator boost::dynamic_bitset<>() const;
    operator express::base() const;

    operator std::vector<int64_t>() const;
    operator std::vector<double>() const;
    operator std::vector<std::string>() const;
    operator std::vector<boost::dynamic_bitset<>>() const;
    operator std::vector<express::base>() const;

    operator std::vector<std::vector<int64_t>>() const;
    operator std::vector<std::vector<double>>() const;
    operator std::vector<std::vector<express::base>>() const;

    operator enumeration_reference() const;

    bool isNull() const;
    unsigned int size() const;

    ifcopenshell::argument_type type() const;

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor) const {
        switch (type()) {
            case ifcopenshell::Argument_DERIVED:
                return visitor(derived{});
            case ifcopenshell::Argument_INT:
                return visitor((int64_t)*this);
            case ifcopenshell::Argument_BOOL:
                return visitor((bool)*this);
            case ifcopenshell::Argument_LOGICAL: {
                boost::logic::tribool tb = *this;
                return visitor(tb);
            }
            case ifcopenshell::Argument_DOUBLE:
                return visitor((double)*this);
            case ifcopenshell::Argument_STRING:
                return visitor((std::string)*this);
            case ifcopenshell::Argument_BINARY:
                return visitor((boost::dynamic_bitset<>)*this);
            case ifcopenshell::Argument_ENUMERATION:
                return visitor((enumeration_reference)*this);
            case ifcopenshell::Argument_ENTITY_INSTANCE:
                return visitor((express::base) * this);
            case ifcopenshell::Argument_AGGREGATE_OF_INT:
                return visitor((std::vector<int64_t>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_DOUBLE:
                return visitor((std::vector<double>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_STRING:
                return visitor((std::vector<std::string>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_BINARY:
                return visitor((std::vector<boost::dynamic_bitset<>>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_ENTITY_INSTANCE:
                return visitor((std::vector<express::base>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_INT:
                return visitor((std::vector<std::vector<int64_t>>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE:
                return visitor((std::vector<std::vector<double>>)*this);
            case ifcopenshell::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE:
                return visitor((std::vector<std::vector<express::base>>)*this);
            case ifcopenshell::Argument_EMPTY_AGGREGATE:
                return visitor(empty_aggregate{});
            case ifcopenshell::Argument_AGGREGATE_OF_EMPTY_AGGREGATE:
                return visitor(empty_aggregate_of_aggregate{});
            default:
                return visitor(blank{});
        }
    }
};


struct IFC_PARSE_API rocks_db_attribute_storage {
public:
#ifdef IFOPSH_WITH_ROCKSDB
    // @todo void* is obviously very ugly here
    template<typename T>
    IFC_PARSE_API void set(void* storage, const ifcopenshell::declaration* declaration, std::size_t identity, std::size_t index, const T& value);

    template<typename T>
    IFC_PARSE_API bool has(void* storage, const ifcopenshell::declaration* decl, std::size_t identity, std::size_t index) const;
#endif
};

class IFC_PARSE_API instance_data {
 protected:
    static std::atomic_uint32_t counter_;

    ifcopenshell::file* file_;
    // @todo this could also be a 2-byte index, because we can get the schema from the file. But it wouldn't save space due to alignment
    const ifcopenshell::declaration* declaration_;
    uint32_t identity_;
    uint32_t id_;

    template <typename T>
    T* get_storage_of_type() const;

    void populate_derived_();

  public:
      // Since rocks_db_attribute_storage has no members this is not a variant<in_memory, rocks> but in_memory*, where nullptr means a rocks_db_attribute_storage is constructed on the fly given the context from instance data.
      in_memory_attribute_storage* storage_;

      const ifcopenshell::declaration* declaration() const {
          return declaration_;
      }

      ifcopenshell::file* file() const {
          return file_;
      }

      uint32_t identity() const {
          return identity_;
      }

      uint32_t id() const {
          return id_;
      }

      instance_data(ifcopenshell::file* file, const ifcopenshell::declaration* declaration, uint32_t id, in_memory_attribute_storage&& storage)
          : file_(file), declaration_(declaration), identity_(counter_++), id_(id), storage_(new in_memory_attribute_storage(std::move(storage)))
      {
            populate_derived_();
      }

      instance_data(ifcopenshell::file* file, const ifcopenshell::declaration* declaration, uint32_t id, rocks_db_attribute_storage&& storage)
          : file_(file), declaration_(declaration), identity_(counter_++), id_(id), storage_(nullptr)
      {
          static_cast<void>(storage);
          populate_derived_();
      }

      /*
      // now that there are referenced as shared_ptr there is no move constructor anymore
      instance_data(instance_data&& other) noexcept
          : file_(other.file_), id_(other.id_), declaration_(other.declaration_), storage_(std::exchange(other.storage_, nullptr))
      {}
      */

      // No copy-constructor/-assignment anymore because we need the instance for storage model context
      instance_data(const instance_data& other) = delete;
      instance_data& operator=(const instance_data& other) = delete;
      instance_data& operator=(instance_data&& other) = delete;
      instance_data(instance_data&& other) noexcept = delete;

      /*
      // same
      instance_data& operator=(instance_data&& other) noexcept {
          if (this != &other) {
              delete storage_;
              storage_ = std::exchange(other.storage_, nullptr);
          }
          return *this;
      }
      */

      ~instance_data() {
          delete storage_;
      }

    attribute_value get_attribute_value(size_t attribute_index) const;

    template<typename T>
    void set_attribute_value(std::size_t attribute_index, T&& value) {
        if (storage_) {
            storage_->set(attribute_index, value);
            return;
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            rocks_db_attribute_storage{}.set(get_storage_of_type<ifcopenshell::impl::rocks_db_file_storage>(), declaration_, id_ ? id_ : identity_, attribute_index, value);
            return;
        }
#endif
        throw std::logic_error("RocksDB storage is unavailable");
    }

    template<typename T>
    bool has_attribute_value(std::size_t attribute_index) const {
        if (storage_) {
            return storage_->has<T>(attribute_index);
        }
#ifdef IFOPSH_WITH_ROCKSDB
        else {
            return rocks_db_attribute_storage{}.has<T>(get_storage_of_type<ifcopenshell::impl::rocks_db_file_storage>(), declaration_, id_ ? id_ : identity_, attribute_index);
        }
#endif
        throw std::logic_error("RocksDB storage is unavailable");
    }

    void to_string(std::ostream& stream, bool uppercase = false) const;
};

} // namespace ifcopenshell

#endif
