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

#ifndef DENSE_ID_MAP_H
#define DENSE_ID_MAP_H

#include <algorithm>
#include <cstdint>
#include <iterator>
#include <unordered_map>
#include <utility>
#include <vector>

namespace ifcopenshell {

// A map from instance name (#id) to a pointer-like value, with the subset of
// the std::unordered_map interface that the file storage uses.
//
// SPF instance names are small and nearly contiguous, so the primary store is
// a vector indexed by id: one pointer per id, no per-entry node. Ids that
// would leave the vector mostly empty (a name far beyond the populated range)
// go to an overflow hash map instead, so a sparse file degrades to the old
// layout rather than to a huge allocation. Iteration visits the vector's
// occupied slots in id order and then the overflow entries.
template <typename V>
class dense_id_map {
  public:
    typedef uint32_t key_type;
    typedef V mapped_type;
    typedef std::pair<const key_type, mapped_type> value_type;

  private:
    typedef std::unordered_map<key_type, mapped_type> overflow_map;

    // Grow the vector to cover an id only while the vector stays at least
    // this dense relative to the number of entries held so far. A file whose
    // names start high therefore fills the overflow map first and switches to
    // the vector once enough entries justify it.
    static constexpr size_t max_slots_per_entry = 8;
    static constexpr size_t min_slots = 4096;

    std::vector<mapped_type> slots_;
    size_t dense_count_ = 0;
    overflow_map overflow_;

    bool fits_dense(key_type key) const {
        if (key < slots_.size()) {
            return true;
        }
        return (size_t)key < min_slots || (size_t)key <= (size() + 1) * max_slots_per_entry;
    }

  public:
    class iterator {
        friend class dense_id_map;
        dense_id_map* map_ = nullptr;
        size_t index_ = 0;
        typename overflow_map::iterator overflow_it_;
        mutable std::pair<key_type, mapped_type> cached_;

        void skip_empty() {
            while (index_ < map_->slots_.size() && !map_->slots_[index_]) {
                ++index_;
            }
        }
        iterator(dense_id_map* map, size_t index, typename overflow_map::iterator overflow_it)
            : map_(map), index_(index), overflow_it_(overflow_it) {
            if (map_) {
                skip_empty();
            }
        }

      public:
        typedef std::forward_iterator_tag iterator_category;
        typedef std::pair<key_type, mapped_type> value_type;
        typedef std::ptrdiff_t difference_type;
        typedef value_type* pointer;
        typedef value_type reference;

        iterator() = default;

        bool in_overflow() const {
            return index_ >= map_->slots_.size();
        }
        value_type operator*() const {
            if (in_overflow()) {
                return {overflow_it_->first, overflow_it_->second};
            }
            return {(key_type)index_, map_->slots_[index_]};
        }
        value_type* operator->() const {
            cached_ = **this;
            return &cached_;
        }
        iterator& operator++() {
            if (in_overflow()) {
                ++overflow_it_;
            } else {
                ++index_;
                skip_empty();
            }
            return *this;
        }
        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }
        bool operator==(const iterator& other) const {
            return map_ == other.map_ && index_ == other.index_ && (map_ == nullptr || !in_overflow() || overflow_it_ == other.overflow_it_);
        }
        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    void reserve(size_t count) {
        slots_.reserve(count);
    }

    size_t size() const {
        return dense_count_ + overflow_.size();
    }

    bool empty() const {
        return size() == 0;
    }

    void clear() {
        slots_.clear();
        dense_count_ = 0;
        overflow_.clear();
    }

    iterator begin() {
        return iterator(this, 0, overflow_.begin());
    }

    iterator end() {
        return iterator(this, slots_.size(), overflow_.end());
    }

    iterator find(key_type key) {
        if (key < slots_.size()) {
            return slots_[key] ? iterator(this, key, overflow_.begin()) : end();
        }
        auto it = overflow_.find(key);
        return it == overflow_.end() ? end() : iterator(this, slots_.size(), it);
    }

    size_t count(key_type key) const {
        if (key < slots_.size()) {
            return slots_[key] ? 1 : 0;
        }
        return overflow_.count(key);
    }

    // Grows the vector to cover key. Overflow entries whose names now fall
    // inside the vector move into it, otherwise a lookup would stop at the
    // empty slot and never see them. Growing geometrically keeps that
    // migration to O(log n) passes for names arriving in any order.
    void grow_to_(key_type key) {
        const size_t wanted = std::max<size_t>((size_t)key + 1, slots_.size() * 2);
        slots_.resize(wanted, mapped_type{});
        for (auto it = overflow_.begin(); it != overflow_.end();) {
            if (it->first < slots_.size()) {
                slots_[it->first] = it->second;
                ++dense_count_;
                it = overflow_.erase(it);
            } else {
                ++it;
            }
        }
    }

    std::pair<iterator, bool> insert(const std::pair<key_type, mapped_type>& value) {
        const key_type key = value.first;
        if (fits_dense(key)) {
            if (key >= slots_.size()) {
                grow_to_(key);
            }
            if (slots_[key]) {
                return {iterator(this, key, overflow_.begin()), false};
            }
            slots_[key] = value.second;
            ++dense_count_;
            return {iterator(this, key, overflow_.begin()), true};
        }
        auto result = overflow_.insert(value);
        return {iterator(this, slots_.size(), result.first), result.second};
    }

    size_t erase(key_type key) {
        if (key < slots_.size()) {
            if (!slots_[key]) {
                return 0;
            }
            slots_[key] = mapped_type{};
            --dense_count_;
            return 1;
        }
        return overflow_.erase(key);
    }
};

} // namespace ifcopenshell

#endif
