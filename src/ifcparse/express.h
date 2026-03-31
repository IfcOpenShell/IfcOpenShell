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
#include <boost/shared_ptr.hpp>

class aggregate_of_instance;

namespace ifcopenshell {
class file;
namespace impl {
struct in_memory_file_storage;
}
} // namespace ifcopenshell

class instance_data;
class attribute_value;

namespace express {

class Base;
class Select;
class Entity;
class DeclaredType;

class IFC_PARSE_API Base {
  protected:
    std::weak_ptr<instance_data> data_;
    const instance_data* data() const;
    instance_data* data();
  public:
    operator bool() const {
        return !data_.expired();
    }

    bool operator<(const Base& other) const {
        return data() < other.data();
    }

    bool operator==(const Base& other) const {
        return data() == other.data();
    }

    bool operator!=(const Base& other) const {
        return !(*this == other);
    }

    Base() {};
    Base(const std::weak_ptr<instance_data>& data) : data_(data) {}

    // @todo try and make this private over time too
    const std::weak_ptr<instance_data>& data_weak() const { return data_; }

    const ifcopenshell::declaration& declaration() const;

    template <typename T>
    typename std::enable_if<
        (!std::is_base_of_v<express::Base, T> || std::is_same_v<express::Base, T>),
        void>::type
    set_attribute_value(size_t i, const T& t);

    template <typename T>
    typename std::enable_if<
        (!std::is_base_of_v<express::Base, T> || std::is_same_v<express::Base, T>),
        void>::type
    set_attribute_value(const std::string& name, const T& t);

    void set_attribute_value(size_t i, const express::Base& p);
    void set_attribute_value(const std::string& name, const express::Base& p);
    
    void unset_attribute_value(size_t i);

    attribute_value get_attribute_value(size_t index) const;

    uint32_t identity() const;

    uint32_t id() const;

    void to_string(std::ostream&, bool upper = false) const;

    template <class T>
    T as() const {
        if constexpr (std::is_same_v<Entity, T>) {
            if (declaration().as_entity() != nullptr) {
                return T(data_weak());
            } else {
                return T{};
            }
        } else if constexpr (std::is_same_v<DeclaredType, T>) {
            if (declaration().as_entity() == nullptr) {
                return T(data_weak());
            } else {
                return T{};
            }
        } else if constexpr (std::is_same_v<Select, T>) {
            static_assert(std::is_same_v<Select, T>, "Select is abstract");
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

class IFC_PARSE_API Entity : public Base {
  public:
    Entity() {}
    Entity(const std::weak_ptr<instance_data>& data) : Base(data) {}

    attribute_value get(const std::string& name) const;

    template <typename T>
    T get_value(const std::string& name) const;

    template <typename T>
    T get_value(const std::string& name, const T& default_value) const;

    std::vector<express::Entity> get_inverse(const std::string& name) const;
};

class IFC_PARSE_API Select : public Base {
  public:
    Select() {}
    // Select are constructed from Base as cast functions, not from data directly
    Select(const Base& base) : Base(base.data_weak()) {}

    Base concrete() const {
        return Base(data_weak());
    }
};

// @todo Investigate whether these should be template classes instead
// @todo currently this class doesn't do much, decide whether to keep
//       it or move certain functionality from Base downwards to
//       Entity and DeclaredType
class IFC_PARSE_API DeclaredType : public Base {
  public:
    DeclaredType() {}
    DeclaredType(const std::weak_ptr<instance_data>& data) : Base(data) {}
};

} // namespace express

namespace std {

template <>
struct hash<express::Base> {
    std::size_t operator()(const express::Base& c) const noexcept {
        return std::hash<uint32_t>{}(c.identity());
    }
};

template <>
struct hash<express::Entity> {
    std::size_t operator()(const express::Entity& c) const noexcept {
        return std::hash<uint32_t>{}(c.identity());
    }
};

} // namespace std

namespace boost {

template <>
struct hash<express::Base> {
    std::size_t operator()(const express::Base& c) const noexcept {
        return std::hash<uint32_t>{}(c.identity());
    }
};

template <>
struct hash<express::Entity> {
    std::size_t operator()(const express::Entity& c) const noexcept {
        return std::hash<uint32_t>{}(c.identity());
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
cast_vector(const std::vector<U>& vs) {
    if constexpr (is_std_vector<U>::value) {
        using V = typename U::value_type;
        std::vector<std::vector<T>> result;
        result.reserve(vs.size());
        for (const auto& v : vs) {
            result.push_back(cast_vector<T>(v));
        }
        return result;
    } else {
        std::vector<T> result;
        for (const auto& v : vs) {
            if constexpr (std::is_base_of_v<T, U>) {
                // For a base or identity transform we can just rely on static cast
                result.push_back(v);
            } else if constexpr (std::is_base_of_v<express::Select, U> && std::is_same_v<T, express::Base>) {
                // From a select to concrete we simply call the appropriate method
                result.push_back(v.concrete());
            } else {
                if (auto u = v.template as<T>()) {
                    result.push_back(u);
                }
            }
        }
        return result;
    }
}

#endif
