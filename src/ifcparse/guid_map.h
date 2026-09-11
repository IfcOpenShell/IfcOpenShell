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
#include <map>
#include <string>
#include <string_view>
#include <unordered_map>
#include <tuple>
#include <utility>

namespace ifcopenshell {

// A map from GlobalId to a value, keyed by std::string but stored as an
// unordered_map with std::array<char, 22> keys, so a valid GlobalId costs
// no heap allocation. Keys of any other length go to an ordinary ordered
// map, so an invalid file still works. Exposes the subset of the std::map
// interface the file storage uses; iteration order is unspecified.
template <typename V>
class guid_map {
  public:
    typedef std::string key_type;
    typedef V mapped_type;
    typedef std::pair<const std::string, V> value_type;

  private:
    // An IFC GlobalId is exactly 22 characters; those keys live inline in
    // the hash node as a std::array. Anything else, which only an invalid
    // file produces, goes to the ordered map.
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
    typedef std::unordered_map<guid_key, V, guid_key_hash> short_map;
    typedef std::map<std::string, V> long_map;

    short_map short_;
    long_map long_;

  public:
    class iterator {
        friend class guid_map;
        guid_map* map_ = nullptr;
        typename short_map::iterator short_it_;
        typename long_map::iterator long_it_;
        mutable std::pair<std::string, V> cached_;

        iterator(guid_map* map, typename short_map::iterator short_it, typename long_map::iterator long_it)
            : map_(map), short_it_(short_it), long_it_(long_it) {}

      public:
        typedef std::forward_iterator_tag iterator_category;
        typedef std::pair<std::string, V> value_type;
        typedef std::ptrdiff_t difference_type;
        typedef value_type* pointer;
        typedef value_type reference;

        iterator() = default;

        bool in_long() const {
            return short_it_ == map_->short_.end();
        }
        value_type operator*() const {
            if (in_long()) {
                return {long_it_->first, long_it_->second};
            }
            return {std::string(short_it_->first.data(), short_it_->first.size()), short_it_->second};
        }
        value_type* operator->() const {
            cached_ = **this;
            return &cached_;
        }
        iterator& operator++() {
            if (in_long()) {
                ++long_it_;
            } else {
                ++short_it_;
            }
            return *this;
        }
        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }
        bool operator==(const iterator& other) const {
            return map_ == other.map_ && short_it_ == other.short_it_ && long_it_ == other.long_it_;
        }
        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    void reserve(size_t count) {
        short_.reserve(count);
    }

    size_t size() const {
        return short_.size() + long_.size();
    }

    bool empty() const {
        return size() == 0;
    }

    void clear() {
        short_.clear();
        long_.clear();
    }

    iterator begin() {
        return iterator(this, short_.begin(), long_.begin());
    }

    iterator end() {
        return iterator(this, short_.end(), long_.end());
    }

    iterator find(const std::string& key) {
        if (is_guid_sized(key)) {
            auto it = short_.find(to_key(key));
            return it == short_.end() ? end() : iterator(this, it, long_.begin());
        }
        auto it = long_.find(key);
        return it == long_.end() ? end() : iterator(this, short_.end(), it);
    }

    size_t count(const std::string& key) const {
        return is_guid_sized(key) ? short_.count(to_key(key)) : long_.count(key);
    }

    V& operator[](const std::string& key) {
        return is_guid_sized(key) ? short_[to_key(key)] : long_[key];
    }

    std::pair<iterator, bool> insert(const std::pair<const std::string, V>& value) {
        if (is_guid_sized(value.first)) {
            auto result = short_.insert({to_key(value.first), value.second});
            return {iterator(this, result.first, long_.begin()), result.second};
        }
        auto result = long_.insert(value);
        return {iterator(this, short_.end(), result.first), result.second};
    }

    size_t erase(const std::string& key) {
        return is_guid_sized(key) ? short_.erase(to_key(key)) : long_.erase(key);
    }
};

} // namespace ifcopenshell

#endif
