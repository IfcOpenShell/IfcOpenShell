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

#include <iterator>
#include <type_traits>
#include <utility>
#include <functional>

// map_transformer: wraps a map-like construct so that its iterator returns
// a value_type where the mapped element is transformed via a function.
template <typename BaseMap, typename Transform, typename TransformBack>
class map_transformer {
public:
    using key_type = typename BaseMap::key_type;
    using base_mapped_type = typename BaseMap::mapped_type;
    using transformed_mapped_type = std::invoke_result_t<Transform, base_mapped_type>;
    using value_type = std::pair<key_type, transformed_mapped_type>;
    using mapped_type = transformed_mapped_type;

private:
    BaseMap* base_map_;
    Transform transform_;

    TransformBack transform_back_;

public:
    map_transformer(BaseMap* map, Transform transform, TransformBack transform_back)
        : base_map_(map), transform_(transform), transform_back_(transform_back){}

    class iterator {
    public:
        using base_iterator = typename BaseMap::iterator;
        using iterator_category = std::forward_iterator_tag;
        using difference_type = typename std::iterator_traits<base_iterator>::difference_type;
        using key_type = typename BaseMap::key_type;
        using transformed_mapped_type = std::invoke_result_t<Transform, typename BaseMap::mapped_type>;
        using value_type = std::pair<key_type, transformed_mapped_type>;

    private:
        base_iterator base_it_;
        Transform* transform_ptr_;

        mutable value_type cached_value_;

    public:
        iterator() : base_it_(), transform_ptr_(nullptr) {}
        iterator(base_iterator base_it, Transform* transform_ptr)
            : base_it_(base_it), transform_ptr_(transform_ptr) {}

        // On dereference, return a pair where the key is unchanged and the mapped value
        // is the result of applying the transform to the underlying mapped value.
        // @todo should these also all be const references so that key/value can be non-copyable (i.e unique_ptr)
        value_type operator*() const {
            auto base_val = *base_it_;
            return { base_val.first, (*transform_ptr_)(base_val.second) };
        }

        // operator-> uses a mutable cache to return a pointer to the current value.
        value_type* operator->() const {
            cached_value_ = **this;
            return &cached_value_;
        }

        iterator& operator++() {
            ++base_it_;
            return *this;
        }

        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        bool operator==(const iterator& other) const {
            return base_it_ == other.base_it_;
        }

        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    iterator begin() {
        return iterator(base_map_->begin(), &transform_);
    }

    iterator end() {
        return iterator(base_map_->end(), &transform_);
    }

    iterator find(const key_type& k) {
        return iterator(base_map_->find(k), &transform_);
    }

    // @todo still not sure if this is a good idea, do we want to insert into the transformed map?
    std::pair<iterator, bool> insert(const value_type& val) {
        auto p = base_map_->insert({ val.first, transform_back_(val.second) });
        return { iterator(p.first, &transform_), p.second };
    }

    size_t erase(const key_type& key) {
        return base_map_->erase(key);
    }
};