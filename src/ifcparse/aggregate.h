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

#ifndef IFCAGGREGATE_H
#define IFCAGGREGATE_H

#include "exception.h"
#include "express.h"
#include "file.h"
#include "instance_data.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <iterator>
#include <type_traits>
#include <vector>

namespace express {

template <typename T>
class aggregate;

namespace detail {

// What the attribute storage holds for an element of type T: a handle for an
// instance type, the value for a simple type, a vector for a nested aggregate.
template <typename T>
struct stored {
    using type = std::conditional_t<std::is_base_of_v<base, T>, base, T>;
};
template <typename T>
struct stored<aggregate<T>> {
    using type = std::vector<typename stored<T>::type>;
};
template <typename T>
using stored_t = typename stored<T>::type;

template <typename T>
struct is_aggregate : std::false_type {};
template <typename T>
struct is_aggregate<aggregate<T>> : std::true_type {};

// An aggregate edited on a copy writes the copy back; a nested aggregate
// does so through the aggregate that holds the copy.
struct committer {
    virtual ~committer() = default;
    virtual void commit() = 0;
};

} // namespace detail

// An aggregate attribute as it is stored: read and edited in place, without
// copying the list out or rewriting it whole for a change. Editing an
// aggregate of instances keeps the file's inverse index current.
//
// Obtained with instance.get<express::aggregate<T>>(attribute_index), where
// T is express::base or a generated class (elements are cast as they are
// read), a simple element type (int64_t, double, std::string,
// boost::dynamic_bitset<>), or express::aggregate<U> for a nested aggregate.
//
// The view points into the instance's storage and is valid until that
// attribute is set anew or the instance is removed. An attribute not held in
// memory as such a vector (unset, an empty aggregate, or RocksDB-backed) is
// edited on a copy that every edit writes back through set_attribute_value().
template <typename T>
class aggregate : private detail::committer {
  public:
    using stored_type = detail::stored_t<T>;
    using vector_type = std::vector<stored_type>;
    static constexpr bool nested = detail::is_aggregate<T>::value;
    static constexpr bool of_instances = std::is_base_of_v<base, T>;

    // The elements: handles and nested views by value, simple values by reference.
    using reference = std::conditional_t<of_instances || nested, T, const T&>;

    aggregate(const base& owner, size_t attribute_index, ifcopenshell::instance_data* data)
        : owner_(owner), index_(attribute_index) {
        if (auto* stored = data->in_memory_aggregate<vector_type>(attribute_index)) {
            list_ = stored;
            in_place_ = true;
        } else {
            copy_ = current_value_(owner, attribute_index);
            list_ = &copy_;
            in_place_ = false;
        }
    }

    aggregate(const aggregate& other) { *this = other; }
    aggregate& operator=(const aggregate& other) {
        owner_ = other.owner_;
        index_ = other.index_;
        in_place_ = other.in_place_;
        parent_ = other.parent_;
        copy_ = other.copy_;
        list_ = other.list_ == &other.copy_ ? &copy_ : other.list_;
        return *this;
    }

    size_t size() const { return list_->size(); }
    bool empty() const { return list_->empty(); }

    reference operator[](size_t i) { return element_((*list_)[i]); }

    class iterator {
      public:
        using iterator_category = std::input_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        using pointer = void;
        using reference = typename aggregate::reference;

        iterator(aggregate* owner, size_t position) : owner_(owner), position_(position) {}
        reference operator*() const { return (*owner_)[position_]; }
        iterator& operator++() {
            ++position_;
            return *this;
        }
        iterator operator++(int) {
            auto before = *this;
            ++position_;
            return before;
        }
        bool operator==(const iterator& other) const { return position_ == other.position_; }
        bool operator!=(const iterator& other) const { return position_ != other.position_; }

      private:
        aggregate* owner_;
        size_t position_;
    };

    iterator begin() { return iterator(this, 0); }
    iterator end() { return iterator(this, size()); }

    // The elements as stored: handles for instance types, values otherwise.
    const vector_type& stored() const { return *list_; }

    // The elements copied out and cast to T.
    template <typename U = T, typename = std::enable_if_t<!detail::is_aggregate<U>::value>>
    operator std::vector<U>() {
        std::vector<U> values;
        values.reserve(size());
        for (size_t i = 0; i < size(); ++i) {
            values.push_back((*this)[i]);
        }
        return values;
    }

    // Appends an element. An instance's inverse record is added.
    void push_back(const T& value) {
        static_assert(!nested, "a nested aggregate is edited through its inner aggregates");
        if constexpr (std::is_same_v<T, double>) {
            if (!std::isfinite(value)) {
                throw ifcopenshell::exception("Only finite values are allowed");
            }
        }
        list_->push_back(value);
        if (in_place_) {
            if constexpr (of_instances) {
                register_inverse_(value);
            }
        } else {
            commit();
        }
    }

    // Erases every occurrence of an element and returns how many there were.
    // An instance's inverse records go with them.
    size_t erase(const T& value) {
        static_assert(!nested, "a nested aggregate is edited through its inner aggregates");
        const auto end = std::remove(list_->begin(), list_->end(), stored_type(value));
        const size_t erased = (size_t)(list_->end() - end);
        if (erased == 0) {
            return 0;
        }
        list_->erase(end, list_->end());
        if (in_place_) {
            if constexpr (of_instances) {
                for (size_t n = 0; n < erased; ++n) {
                    unregister_inverse_(value);
                }
            }
        } else {
            commit();
        }
        return erased;
    }

  private:
    // A nested aggregate: a view on one of the vectors held by its owner.
    aggregate(const base& owner, size_t attribute_index, vector_type* list, bool in_place, detail::committer* parent)
        : owner_(owner), index_(attribute_index), list_(list), in_place_(in_place), parent_(parent) {}

    template <typename U>
    friend class aggregate;

    static vector_type current_value_(const base& owner, size_t attribute_index) {
        auto value = owner.get_attribute_value(attribute_index);
        if (value.isNull() || value.type() == ifcopenshell::Argument_EMPTY_AGGREGATE || value.type() == ifcopenshell::Argument_AGGREGATE_OF_EMPTY_AGGREGATE) {
            return {};
        }
        return (vector_type)value;
    }

    reference element_(stored_type& stored) {
        if constexpr (nested) {
            return T(owner_, index_, &stored, in_place_, in_place_ ? nullptr : static_cast<detail::committer*>(this));
        } else if constexpr (std::is_same_v<T, base>) {
            return stored;
        } else if constexpr (of_instances) {
            return stored.template as<T>();
        } else {
            return stored;
        }
    }

    void commit() override {
        if (parent_ != nullptr) {
            parent_->commit();
        } else {
            owner_.set_attribute_value(index_, copy_);
        }
    }

    void register_inverse_(const base& instance) {
        owner_.file()->register_inverse(owner_.id(), owner_.declaration().as_entity(), (int)instance.id(), (int)index_);
    }

    void unregister_inverse_(const base& instance) {
        owner_.file()->unregister_inverse(owner_.id(), owner_.declaration().as_entity(), instance, (int)index_);
    }

    base owner_;
    size_t index_ = 0;
    // The vector read and edited: the instance's own, or a copy.
    vector_type* list_ = nullptr;
    bool in_place_ = false;
    // The copy, when the attribute is not held in memory as vector_type.
    vector_type copy_;
    // The enclosing aggregate whose copy holds list_, for a nested view.
    detail::committer* parent_ = nullptr;
};

template <typename A>
A base::get(size_t attribute_index) {
    static_assert(detail::is_aggregate<A>::value, "get<T>() reads an express::aggregate<...>");
    return A(*this, attribute_index, data());
}

} // namespace express

#endif
