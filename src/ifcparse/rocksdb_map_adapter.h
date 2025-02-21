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

#include <rocksdb/db.h>
#include <rocksdb/options.h>
#include <memory>
#include <string>
#include <utility>
#include <iterator>
#include <cstddef>

// Serialization and deserialization primitives
template <typename T>
struct DefaultCodec;

// Specialization for size_t.
template <>
struct DefaultCodec<size_t> {
    std::string encode(const size_t& v) const {
        std::string s(sizeof(v), 0);
        size_t temp = v;
        for (size_t i = 0; i < sizeof(v); i++) {
            s[sizeof(v) - i - 1] = static_cast<char>(temp & 0xFF);
            temp >>= 8;
        }
        return s;
    }
    size_t decode(const std::string& s) const {
        size_t v = 0;
        for (size_t i = 0; i < s.size(); i++) {
            v = (v << 8) | static_cast<unsigned char>(s[i]);
        }
        return v;
    }
};

// Specialization for std::string (identity)
template <>
struct DefaultCodec<std::string> {
    std::string encode(const std::string& v) const {
        return v;
    }
    std::string decode(const std::string& s) const {
        return s;
    }
};

template <typename KeyT>
std::string key_to_string(const KeyT& key) {
    if constexpr (std::is_same_v<KeyT, std::string>) {
        return key;
    } else {
        return std::to_string(key);
    }
}

// Convert from a string to a key. For non-string types, we assume numeric keys.
template <typename KeyT>
KeyT key_from_string(const std::string& s) {
    // @todo tuples
    if constexpr (std::is_same_v<KeyT, std::string>) {
        return s;
    } else if constexpr (std::is_integral_v<KeyT>) {
        return static_cast<KeyT>(std::stoll(s));
    } else {
        static_assert(sizeof(KeyT) == 0, "key_from_string not implemented for this type");
    }
}

// rocksdb_map_adapter: a std::map-like interface on a RocksDB keyspace with a given prefix.
// The mapped_type is templated and encoded/decoded via Codec.
template <typename KeyT, typename MappedT, typename Codec = DefaultCodec<MappedT>>
class rocksdb_map_adapter {
public:
    using key_type = KeyT;
    using mapped_type = MappedT;
    using value_type = std::pair<key_type, mapped_type>;

private:
    rocksdb::DB* db_;
    std::string prefix_;
    Codec codec_;

public:
    rocksdb_map_adapter(rocksdb::DB* db, const std::string& prefix)
        : db_(db), prefix_(prefix), codec_(Codec{}) {}

    class iterator {
    public:
        using value_type = std::pair<key_type, mapped_type>;
        using difference_type = std::ptrdiff_t;
        using iterator_category = std::forward_iterator_tag;
        using pointer = value_type*;
        using reference = value_type&;

    private:
        rocksdb::DB* db_;
        std::string prefix_;
        Codec codec_;
        // When it_ is nullptr, this iterator is at end.
        std::unique_ptr<rocksdb::Iterator> it_;
        mutable value_type cached_value_;

        void check_valid() {
            if (!it_ || !it_->Valid() || !it_->key().starts_with(prefix_)) {
                it_.reset();
            }
        }

    public:
        iterator() : db_(nullptr), prefix_(), codec_(Codec{}), it_(nullptr) {}

        iterator(rocksdb::DB* db, const std::string& prefix,
            std::unique_ptr<rocksdb::Iterator> iter, Codec codec = Codec{})
            : db_(db), prefix_(prefix), codec_(codec), it_(std::move(iter))
        {
            check_valid();
        }

        iterator(const iterator& other)
            : db_(other.db_), prefix_(other.prefix_), codec_(other.codec_)
        {
            if (other.it_) {
                std::string curr = other.it_->key().ToString();
                it_.reset(db_->NewIterator(rocksdb::ReadOptions{}));
                it_->Seek(curr);
                if (!it_->Valid() || it_->key().ToString() != curr)
                    it_.reset();
            }
        }

        iterator& operator=(const iterator& other) {
            if (this != &other) {
                db_ = other.db_;
                prefix_ = other.prefix_;
                codec_ = other.codec_;
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
            return *this;
        }

        value_type operator*() const {
            std::string full_key = it_->key().ToString();
            std::string key_without_prefix = full_key.substr(prefix_.size());
            std::string value_str = it_->value().ToString();
            return { key_from_string<key_type>(key_without_prefix), codec_.decode(value_str) };
        }

        // operator-> uses a mutable cache to return a pointer to the current value.
        value_type* operator->() const {
            cached_value_ = **this;
            return &cached_value_;
        }

        iterator& operator++() {
            if (it_) {
                it_->Next();
                check_valid();
            }
            return *this;
        }

        iterator operator++(int) {
            iterator tmp(*this);
            ++(*this);
            return tmp;
        }

        bool operator==(const iterator& other) const {
            if (!it_ && !other.it_) return true;
            if (it_ && other.it_)
                return it_->key().ToString() == other.it_->key().ToString();
            return false;
        }

        bool operator!=(const iterator& other) const {
            return !(*this == other);
        }
    };

    iterator begin() const {
        auto iter = std::unique_ptr<rocksdb::Iterator>(db_->NewIterator(rocksdb::ReadOptions{}));
        iter->Seek(prefix_);
        if (iter->Valid() && iter->key().starts_with(prefix_)) {
            return iterator(db_, prefix_, std::move(iter), codec_);
        }
        return end();
    }

    iterator end() const {
        return iterator();
    }

    iterator find(const key_type& key) const {
        std::string key_str = key_to_string(key);
        std::string full_key = prefix_ + key_str;
        auto iter = std::unique_ptr<rocksdb::Iterator>(db_->NewIterator(rocksdb::ReadOptions{}));
        iter->Seek(full_key);
        if (iter->Valid() && iter->key().ToString() == full_key)
            return iterator(db_, prefix_, std::move(iter), codec_);
        return end();
    }

    size_t erase(const key_type& key) {
        std::string key_str = key_to_string(key);
        std::string full_key = prefix_ + key_str;
        rocksdb::Status s = db_->Delete(rocksdb::WriteOptions{}, full_key);
        return s.ok() ? 1 : 0;
    }

    std::pair<iterator, bool> insert(const value_type& val) {
        std::string key_str = key_to_string(val.first);
        std::string full_key = prefix_ + key_str;
        std::string existing;
        rocksdb::Status s = db_->Get(rocksdb::ReadOptions{}, full_key, &existing);
        if (s.ok()) {
            // Key already exists.
            return { find(val.first), false };
        }
        std::string encoded = codec_.encode(val.second);
        s = db_->Put(rocksdb::WriteOptions{}, full_key, encoded);
        if (!s.ok()) {
            return { end(), false };
        }
        return { find(val.first), true };
    }
};
