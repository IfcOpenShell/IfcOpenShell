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

#ifndef ROCKSDB_SET_VIEW_H
#define ROCKSDB_SET_VIEW_H

#ifdef IFOPSH_WITH_ROCKSDB
#include <rocksdb/db.h>
#include <rocksdb/options.h>
#endif

#include <memory>
#include <string>
#include <iterator>
#include <cstddef>
#include <cstring>
#include <stdexcept>


template <typename KeyT>
class rocksdb_set_view {
public:
    using key_type = KeyT;
    using value_type = key_type;

private:
    rocksdb::DB* db_;
    std::string prefix_;

public:
    // Constructor: provide a pointer to an open RocksDB instance and the key-space prefix,
    // e.g. "i|"
    rocksdb_set_view(rocksdb::DB* db, const std::string& prefix)
        : db_(db), prefix_(prefix) {}

    // --- Iterator ---
    class iterator {
    public:
        using value_type = key_type;
        using difference_type = std::ptrdiff_t;
        using iterator_category = std::forward_iterator_tag;
        using pointer = const value_type*;
        using reference = const value_type&;

    private:
        rocksdb::DB* db_;
        std::string prefix_;
        std::unique_ptr<rocksdb::Iterator> it_;
        mutable value_type cached_value_;

        // Helper: extract the key (i.e. the value) from the current RocksDB key.
        value_type extract_current_value() const {
#ifdef IFOPSH_WITH_ROCKSDB
            std::string full_key = it_->key().ToString();
            std::string remainder = full_key.substr(prefix_.size());
            size_t pos = remainder.find('|');
            std::string key_str = (pos != std::string::npos) ? remainder.substr(0, pos) : remainder;
            return key_from_string<key_type>(key_str);
#else
            return cached_value_;
#endif
        }

        // Validates the current iterator state.
        void check_valid() {
#ifdef IFOPSH_WITH_ROCKSDB
            if (!it_ || !it_->Valid() || !it_->key().starts_with(prefix_))
                it_.reset();
#endif
        }

    public:
        iterator() : db_(nullptr), prefix_(), it_(nullptr) {}

        iterator(rocksdb::DB* db, const std::string& prefix,
            std::unique_ptr<rocksdb::Iterator> iter)
            : db_(db), prefix_(prefix), it_(std::move(iter))
        {
            check_valid();
        }

        iterator(const iterator& other)
            : db_(other.db_), prefix_(other.prefix_)
        {
#ifdef IFOPSH_WITH_ROCKSDB
            if (other.it_) {
                std::string curr = other.it_->key().ToString();
                it_.reset(db_->NewIterator(rocksdb::ReadOptions{}));
                it_->Seek(curr);
                if (!it_->Valid() || it_->key().ToString() != curr)
                    it_.reset();
            }
#endif
        }

        iterator& operator=(const iterator& other) {
#ifdef IFOPSH_WITH_ROCKSDB
            if (this != &other) {
                db_ = other.db_;
                prefix_ = other.prefix_;
                if (other.it_) {
                    std::string curr = other.it_->key().ToString();
                    it_.reset(db_->NewIterator(rocksdb::ReadOptions{}));
                    it_->Seek(curr);
                    if (!it_->Valid() || it_->key().ToString() != curr)
                        it_.reset();
                } else {
                    it_.reset();
                }
            }
#endif
            return *this;
        }

        // Dereference: extract the key part from the RocksDB key.
        value_type operator*() const {
            return extract_current_value();
        }

        // Pointer access (via a cached value)
        const value_type* operator->() const {
            cached_value_ = **this;
            return &cached_value_;
        }

        // Pre-increment: advance the iterator and skip over any duplicate keys.
        iterator& operator++() {
#ifdef IFOPSH_WITH_ROCKSDB
            if (it_) {
                // Record the current key value.
                value_type curr = extract_current_value();
                do {
                    it_->Next();
                } while (it_ && it_->Valid() && it_->key().starts_with(prefix_) &&
                    (extract_current_value() == curr));
                if (!it_ || !it_->Valid() || !it_->key().starts_with(prefix_))
                    it_.reset();
            }
#endif
            return *this;
        }

        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        bool operator==(const iterator& other) const {
#ifdef IFOPSH_WITH_ROCKSDB
            if (!it_ && !other.it_)
                return true;
            if (it_ && other.it_)
                return it_->key().ToString() == other.it_->key().ToString();
#endif
            return false;
        }

        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    // Returns an iterator to the first element in the key-space (or end() if none exist).
    iterator begin() const {
#ifdef IFOPSH_WITH_ROCKSDB
        auto iter = std::unique_ptr<rocksdb::Iterator>(db_->NewIterator(rocksdb::ReadOptions{}));
        iter->Seek(prefix_);
        if (iter->Valid() && iter->key().starts_with(prefix_))
            return iterator(db_, prefix_, std::move(iter));
#endif
        return end();
    }

    // Returns an iterator representing the end of the key-space.
    iterator end() const {
        return iterator();
    }

    // Read-only find: returns an iterator to the element with the given key if it exists.
    iterator find(const key_type& key) const {
#ifdef IFOPSH_WITH_ROCKSDB
        std::string key_str = key_to_string(key);
        // Construct the search key: prefix + key_str + separator.
        std::string start_key = prefix_ + key_str + "|";
        auto iter = std::unique_ptr<rocksdb::Iterator>(db_->NewIterator(rocksdb::ReadOptions{}));
        iter->Seek(start_key);
        if (iter->Valid() && iter->key().starts_with(prefix_)) {
            std::string full_key = iter->key().ToString();
            std::string remainder = full_key.substr(prefix_.size());
            size_t pos = remainder.find('|');
            std::string found_key_str = (pos != std::string::npos) ? remainder.substr(0, pos) : remainder;
            if (key_from_string<key_type>(found_key_str) == key)
                return iterator(db_, prefix_, std::move(iter));
        }
#endif
        return end();
    }

    size_t erase(const key_type& key) {
        // @todo
        return 0;
    }
};

#endif