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

#ifndef GUID_MAP_H
#define GUID_MAP_H

#include <array>
#include <cstdint>
#include <cstring>
#include <functional>
#include <iterator>
#include <string>
#include <string_view>
#include <unordered_map>
#include <tuple>
#include <utility>

namespace ifcopenshell {

// A map from GlobalId to a value, keyed by std::string but stored as an
// unordered_map with std::array<char, 22> keys, so a GlobalId costs no heap
// allocation. Only keys of exactly 22 characters, the length of a GlobalId,
// can be stored or found: anything else is not found and is not inserted.
// Exposes the subset of the std::map interface the file storage uses;
// iteration order is unspecified.
template <typename V>
class guid_map {
  public:
    typedef std::string key_type;
    typedef V mapped_type;
    typedef std::pair<const std::string, V> value_type;

  private:
    typedef std::array<char, 22> guid_key;
    struct guid_key_hash {
        size_t operator()(const guid_key& key) const {
            return std::hash<std::string_view>()(std::string_view(key.data(), key.size()));
        }
    };
    static bool is_guid_sized(const std::string& s) {
        return s.size() == std::tuple_size<guid_key>::value;
    }
    static guid_key to_key(const std::string& s) {
        guid_key key;
        std::memcpy(key.data(), s.data(), key.size());
        return key;
    }
    typedef std::unordered_map<guid_key, V, guid_key_hash> map_type;
    map_type map_;

  public:
    class iterator {
        friend class guid_map;
        typename map_type::iterator it_;
        mutable std::pair<std::string, V> cached_;
        explicit iterator(typename map_type::iterator it)
            : it_(it) {}

      public:
        typedef std::forward_iterator_tag iterator_category;
        typedef std::pair<std::string, V> value_type;
        typedef std::ptrdiff_t difference_type;
        typedef value_type* pointer;
        typedef value_type reference;

        iterator() = default;
        value_type operator*() const {
            return {std::string(it_->first.data(), it_->first.size()), it_->second};
        }
        value_type* operator->() const {
            cached_ = **this;
            return &cached_;
        }
        iterator& operator++() {
            ++it_;
            return *this;
        }
        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }
        bool operator==(const iterator& other) const {
            return it_ == other.it_;
        }
        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    void reserve(size_t count) {
        map_.reserve(count);
    }
    size_t size() const {
        return map_.size();
    }
    bool empty() const {
        return map_.empty();
    }
    void clear() {
        map_.clear();
    }
    iterator begin() {
        return iterator(map_.begin());
    }
    iterator end() {
        return iterator(map_.end());
    }
    iterator find(const std::string& key) {
        return is_guid_sized(key) ? iterator(map_.find(to_key(key))) : end();
    }
    size_t count(const std::string& key) const {
        return is_guid_sized(key) ? map_.count(to_key(key)) : 0;
    }
    // Stores the value under the key, replacing any previous one; false if
    // the key is not GlobalId sized and nothing was stored.
    bool insert_or_assign(const std::string& key, const V& value) {
        if (!is_guid_sized(key)) {
            return false;
        }
        map_[to_key(key)] = value;
        return true;
    }
    std::pair<iterator, bool> insert(const std::pair<const std::string, V>& value) {
        if (!is_guid_sized(value.first)) {
            return {end(), false};
        }
        auto result = map_.insert({to_key(value.first), value.second});
        return {iterator(result.first), result.second};
    }
    size_t erase(const std::string& key) {
        return is_guid_sized(key) ? map_.erase(to_key(key)) : 0;
    }
};

} // namespace ifcopenshell

#endif
