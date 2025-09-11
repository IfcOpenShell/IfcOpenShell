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

#include <map>
#include <variant>
#include <tuple>
#include <utility>
#include <cstddef>
#include <string>
#include <iostream>

// VariantMap: A map interface that delegates to one of several map types.
// The underlying maps are referenced by pointers (not moved into the variant).
// All map types must share the same key_type, mapped_type, and value_type.
template <typename... Maps>
class VariantMap {
public:
    // The variant holds a pointer to the map
    using variant_type = std::variant<std::monostate, Maps*...>;
    variant_type map_;

    // Deduce common types from the first map type.
    // @todo these are not common types, but just the 1st
    using key_type = typename std::tuple_element<0, std::tuple<Maps...>>::type::key_type;
    using mapped_type = typename std::tuple_element<0, std::tuple<Maps...>>::type::mapped_type;
    using value_type = typename std::tuple_element<0, std::tuple<Maps...>>::type::value_type;

    using underlying_iterator_variant = std::variant<typename Maps::iterator...>;

    class iterator {
    public:
        using value_type = VariantMap::value_type;
        using difference_type = std::ptrdiff_t;
        using pointer = value_type*;
        using reference = value_type;
        using iterator_category = std::forward_iterator_tag;

        underlying_iterator_variant it_var;

        // mutable cache to support operator-> (so that it->second works)
        mutable std::unique_ptr<value_type> cached_value_ptr_;

        iterator() = default;

        explicit iterator(underlying_iterator_variant v)
            : it_var(std::move(v)) {}

        iterator(const iterator& other)
            : it_var(other.it_var), cached_value_ptr_(nullptr) {}

        iterator& operator=(const iterator& other) {
            if (this != &other) {
                it_var = other.it_var;
                cached_value_ptr_.reset(); // clear the cache
            }
            return *this;
        }

        value_type operator*() const {
            return std::visit([](auto& it) -> value_type { return *it; }, it_var);
        }

        value_type* operator->() const {
            // @todo we need to make a copy here (stored in unique_ptr) because the
            // value_type appears to be pair<const K, V> instead of <K, V> or something
            // related...
            cached_value_ptr_ = std::make_unique<value_type>(**this);
            return cached_value_ptr_.get();
        }

        iterator& operator++() {
            std::visit([](auto& it) { ++it; }, it_var);
            return *this;
        }

        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        bool operator==(const iterator& other) const {
            return it_var == other.it_var;
        }

        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    VariantMap() {}

    template <typename MapT>
    VariantMap(MapT* m) : map_(m) {}

    iterator begin() const{
        return std::visit([](auto m) -> iterator {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return iterator{};
            } else {
                return iterator(m->begin());
            }
        }, map_);
    }

    iterator end() const {
        return std::visit([](auto m) -> iterator {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return iterator{};
            } else {
                return iterator(m->end());
            }
        }, map_);
    }

    iterator find(const key_type& key) const {
        return std::visit([&key](auto m) -> iterator {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return iterator{};
            } else {
                return iterator(m->find(key));
            }
        }, map_);
    }

    size_t erase(const key_type& key) {
        return std::visit([&key](auto m) -> size_t {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return size_t(0);
            } else {
                return m->erase(key);
            }
        }, map_);
    }

    size_t erase(const iterator& it) {
        return std::visit([&it](auto m) -> size_t {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return size_t(0);
            } else {
                // @todo erasing by iterator would be more efficient
                return m->erase(it->first);
            }
        }, map_);
    }

    std::pair<iterator, bool> insert(const value_type& val) {
        return std::visit([this, &val](auto m) -> std::pair<iterator, bool> {
            // @todo is monostate still necessary here?
            if constexpr (!std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                auto result = m->insert(val);
                return { iterator(result.first), result.second };
            } else {
                return { end(), false };
            }
        }, map_);
    }
};
