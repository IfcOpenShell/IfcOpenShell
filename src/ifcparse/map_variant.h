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
#include <array>
#include <cstring>
#include <string>
#include <variant>
#include <tuple>
#include <utility>
#include <cstddef>
#include <string>
#include <iostream>

// variant_map: A map interface that delegates to one of several map types.
// The underlying maps are referenced by pointers (not moved into the variant).
// All map types must share the same key_type, mapped_type, and value_type.
template <typename... Maps>
class variant_map {
public:
    // The variant holds a pointer to the map
    using variant_type = std::variant<std::monostate, Maps*...>;
    variant_type map_;

    // Deduce common types from the first map type.
    // @todo these are not common types, but just the 1st
    // A map keyed by a fixed character array (the GlobalId index) is keyed
    // by std::string at this interface; the key is converted on the way in,
    // and a string of the wrong length is simply never found.
    template <typename K>
    struct public_key {
        using type = K;
    };
    template <size_t N>
    struct public_key<std::array<char, N>> {
        using type = std::string;
    };
    using first_map = typename std::tuple_element<0, std::tuple<Maps...>>::type;
    using key_type = typename public_key<typename first_map::key_type>::type;
    using mapped_type = typename first_map::mapped_type;
    using value_type = std::pair<const key_type, mapped_type>;

    template <typename K>
    struct is_char_array : std::false_type {};
    template <size_t N>
    struct is_char_array<std::array<char, N>> : std::true_type {};

    template <typename MapT>
    static bool to_map_key(const key_type& key, typename MapT::key_type& out) {
        if constexpr (is_char_array<typename MapT::key_type>::value) {
            if (key.size() != out.size()) {
                return false;
            }
            std::memcpy(out.data(), key.data(), out.size());
            return true;
        } else {
            out = static_cast<typename MapT::key_type>(key);
            return true;
        }
    }
    template <typename Pair>
    static value_type to_value(const Pair& pair) {
        if constexpr (is_char_array<std::decay_t<decltype(pair.first)>>::value) {
            return value_type(std::string(pair.first.data(), pair.first.size()), pair.second);
        } else {
            return value_type(pair.first, pair.second);
        }
    }

    using underlying_iterator_variant = std::variant<typename Maps::iterator...>;

    class iterator {
    public:
        using value_type = variant_map::value_type;
        using difference_type = std::ptrdiff_t;
        using pointer = value_type*;
        using reference = value_type;
        using iterator_category = std::forward_iterator_tag;

        underlying_iterator_variant it_var;

        // mutable cache to support operator-> (so that it->second works)
        mutable std::unique_ptr<value_type> cached_value_ptr_;

        iterator() = default;

        explicit iterator(underlying_iterator_variant iterator_variant)
            : it_var(std::move(iterator_variant)) {}

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
            return std::visit([](auto& it) -> value_type { return variant_map::to_value(*it); }, it_var);
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

    variant_map() {}

    template <typename MapT>
    variant_map(MapT* map) : map_(map) {}

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
                typename std::decay_t<decltype(*m)>::key_type k{};
                if (!to_map_key<std::decay_t<decltype(*m)>>(key, k)) {
                    return iterator(m->end());
                }
                return iterator(m->find(k));
            }
        }, map_);
    }

    size_t erase(const key_type& key) {
        return std::visit([&key](auto m) -> size_t {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return size_t(0);
            } else {
                typename std::decay_t<decltype(*m)>::key_type k{};
                if (!to_map_key<std::decay_t<decltype(*m)>>(key, k)) {
                    return 0;
                }
                return m->erase(k);
            }
        }, map_);
    }

    size_t erase(const iterator& it) {
        return std::visit([&it](auto m) -> size_t {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                return size_t(0);
            } else {
                // @todo erasing by iterator would be more efficient
                typename std::decay_t<decltype(*m)>::key_type k{};
                if (!to_map_key<std::decay_t<decltype(*m)>>(it->first, k)) {
                    return 0;
                }
                return m->erase(k);
            }
        }, map_);
    }

    std::pair<iterator, bool> insert(const value_type& value) {
        return std::visit([this, &value](auto m) -> std::pair<iterator, bool> {
            // @todo is monostate still necessary here?
            if constexpr (!std::is_same_v<std::decay_t<decltype(m)>, std::monostate>) {
                typename std::decay_t<decltype(*m)>::key_type k{};
                if (!to_map_key<std::decay_t<decltype(*m)>>(value.first, k)) {
                    return { end(), false };
                }
                auto result = m->insert({ k, value.second });
                return { iterator(result.first), result.second };
            } else {
                return { end(), false };
            }
        }, map_);
    }
};
