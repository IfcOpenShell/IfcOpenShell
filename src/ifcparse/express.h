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

#ifndef IFCBASECLASS_H
#define IFCBASECLASS_H

#include "argument.h"
#include "ifc_parse_api.h"
#include "schema.h"
#include "utils.h"

#include <atomic>
#include <memory>

class aggregate_of_instance;

namespace ifcopenshell {

#ifdef IFOPSH_SAFE_INSTANCE
using pointer_type = std::weak_ptr<instance_data>;
using shared_pointer_type = shared_pointer_type;
template <typename T, typename... Args>
shared_pointer_type make_pointer_type(Args&&... args) {
    return std::make_shared<T>(std::forward<Args>(args)...);
}
#else
using pointer_type = instance_data*;
using shared_pointer_type = instance_data*;
template <typename T, typename... Args>
shared_pointer_type make_pointer_type(Args&&... args) {
    return new T(std::forward<Args>(args)...);
}
#endif

class file;
namespace impl {
struct in_memory_file_storage;
}
} // namespace ifcopenshell

namespace ifcopenshell {
class instance_data;
class attribute_value;
}

namespace express {

class base;
class select;
class entity;
class declared_type;

class IFC_PARSE_API base {
  protected:
    ifcopenshell::pointer_type data_;
    const ifcopenshell::instance_data* data() const;
    ifcopenshell::instance_data* data();
  public:
    operator bool() const {
#ifdef IFOPSH_SAFE_INSTANCE
        return !data_.expired();
#else
        return data_ != nullptr;
#endif
    }

    bool operator<(const base& other) const {
        return data() < other.data();
    }

    bool operator==(const base& other) const {
        return data() == other.data();
    }

    bool operator!=(const base& other) const {
        return !(*this == other);
    }

    base() {
#ifndef IFOPSH_SAFE_INSTANCE
        data_ = nullptr;
#endif
    };
    base(std::nullopt_t) noexcept : base() {}
    base(const ifcopenshell::pointer_type& data) : data_(data) {}

    // @todo try and make this private over time too
    const ifcopenshell::pointer_type& data_weak() const { return data_; }

    const ifcopenshell::declaration& declaration() const;

    template <typename T>
    typename std::enable_if<
        (!std::is_base_of_v<express::base, T> || std::is_same_v<express::base, T>),
        void>::type
    set_attribute_value(size_t attribute_index, const T& value);

    template <typename T>
    typename std::enable_if<
        (!std::is_base_of_v<express::base, T> || std::is_same_v<express::base, T>),
        void>::type
    set_attribute_value(const std::string& attribute_name, const T& value);

    void set_attribute_value(size_t attribute_index, const express::base& value);
    void set_attribute_value(const std::string& attribute_name, const express::base& value);

    void unset_attribute_value(size_t attribute_index);

    ifcopenshell::attribute_value get_attribute_value(size_t attribute_index) const;

    uint32_t identity() const;

    uint32_t id() const;

    void to_string(std::ostream& stream, bool uppercase = false) const;

    template <class T>
    T as() const {
        if constexpr (std::is_same_v<entity, T>) {
            if (declaration().as_entity() != nullptr) {
                return T(data_weak());
            } else {
                return T{};
            }
        } else if constexpr (std::is_same_v<declared_type, T>) {
            if (declaration().as_entity() == nullptr) {
                return T(data_weak());
            } else {
                return T{};
            }
        } else if constexpr (std::is_same_v<select, T>) {
            static_assert(std::is_same_v<select, T>, "select is abstract");
        } else {
            if (declaration().is(T::Class())) {
                return T(data_weak());
            } else {
                return T{};
            }
        }
    }

    ifcopenshell::file* file() const;
};

class IFC_PARSE_API entity : public base {
  public:
    using base::base;

    ifcopenshell::attribute_value get(const std::string& attribute_name) const;

    template <typename T>
    T get_value(const std::string& attribute_name) const;

    template <typename T>
    T get_value(const std::string& attribute_name, const T& default_value) const;

    std::vector<express::entity> get_inverse(const std::string& attribute_name) const;
};

class IFC_PARSE_API select : public base {
  public:
    select() {}
    select(std::nullopt_t) noexcept : base() {}
    select(const ifcopenshell::pointer_type& data) : base(data) {}
    select(const base& value) : base(value.data_weak()) {}

    base concrete() const {
        return base(data_weak());
    }
};

// @todo Investigate whether these should be template classes instead
// @todo currently this class doesn't do much, decide whether to keep
//       it or move certain functionality from base downwards to
//       entity and declared_type
class IFC_PARSE_API declared_type : public base {
  public:
    using base::base;
};

} // namespace express

namespace std {

template <>
struct hash<express::base> {
    std::size_t operator()(const express::base& value) const noexcept {
        return std::hash<uint32_t>{}(value.identity());
    }
};

template <>
struct hash<express::entity> {
    std::size_t operator()(const express::entity& value) const noexcept {
        return std::hash<uint32_t>{}(value.identity());
    }
};

} // namespace std

namespace boost {

template <>
struct hash<express::base> {
    std::size_t operator()(const express::base& value) const noexcept {
        return std::hash<uint32_t>{}(value.identity());
    }
};

template <>
struct hash<express::entity> {
    std::size_t operator()(const express::entity& value) const noexcept {
        return std::hash<uint32_t>{}(value.identity());
    }
};

} // namespace boost

namespace {
template <typename>
struct is_std_vector : std::false_type {};

template <typename X, typename A>
struct is_std_vector<std::vector<X, A>> : std::true_type {};

template <typename T>
constexpr bool is_std_vector_v = is_std_vector<T>::value;

template <typename T>
struct is_std_vector_vector : std::false_type {};

template <typename T, typename Alloc, typename Alloc2>
struct is_std_vector_vector<std::vector<std::vector<T, Alloc>, Alloc2>> : std::true_type {};

template <typename T>
constexpr bool is_std_vector_vector_v = is_std_vector_vector<T>::value;
}

template <typename T, typename U>
typename std::conditional_t<
    is_std_vector<U>::value,
    std::vector<std::vector<T>>,
    std::vector<T>>
cast_vector(const std::vector<U>& values) {
    if constexpr (is_std_vector<U>::value) {
        std::vector<std::vector<T>> result;
        result.reserve(values.size());
        for (const auto& value : values) {
            result.push_back(cast_vector<T>(value));
        }
        return result;
    } else {
        std::vector<T> result;
        for (const auto& value : values) {
            if constexpr (std::is_base_of_v<T, U>) {
                // For a base or identity transform we can just rely on static cast
                result.push_back(value);
            } else if constexpr (std::is_base_of_v<express::select, U> && std::is_same_v<T, express::base>) {
                // From a select to concrete we simply call the appropriate method
                result.push_back(value.concrete());
            } else {
                if (auto cast_value = value.template as<T>()) {
                    result.push_back(cast_value);
                }
            }
        }
        return result;
    }
}

#endif
