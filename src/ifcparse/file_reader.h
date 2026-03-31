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

/*********************************************************************************
 *                                                                               *
 * Reads a file and provides functions to access its                             *
 * contents randomly and character by character                                  *
 *                                                                               *
 ********************************************************************************/

#ifndef IFCSPFSTREAM_H
#define IFCSPFSTREAM_H

#include "ifc_parse_api.h"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <list>
#include <memory>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <utility>
#include <vector>

#ifdef USE_MMAP
#include <boost/iostreams/device/mapped_file.hpp>
#endif

namespace ifcopenshell {

struct file_reader_page {
    std::vector<char> data;
};

struct caller_fed_tag {};

template <typename>
inline constexpr bool file_reader_dependent_false_v = false;

class IFC_PARSE_API full_buffer_impl;
class IFC_PARSE_API paged_file_impl;
#ifdef USE_MMAP
class IFC_PARSE_API mmap_impl;
#endif
class IFC_PARSE_API pushed_sequential_impl;

template <typename Impl>
class file_reader {
public:
    using impl_type = Impl;
    using Page = file_reader_page;

    file_reader() = default;

    explicit file_reader(const std::string& fn)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, full_buffer_impl>
#ifdef USE_MMAP
            || std::is_same_v<Impl, mmap_impl>
#endif
        ) {
            impl_ = std::make_shared<Impl>(fn);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This file_reader constructor is not supported for the selected backend");
        }
    }

    explicit file_reader(const caller_fed_tag&)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, full_buffer_impl>) {
            impl_ = std::make_shared<Impl>(caller_fed_tag{});
        } else if constexpr (std::is_same_v<Impl, pushed_sequential_impl>) {
            impl_ = std::make_shared<Impl>();
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This file_reader constructor is not supported for the selected backend");
        }
    }

    file_reader(const std::string& content, const caller_fed_tag&)
        : file_reader(caller_fed_tag{}) {
        if constexpr (std::is_same_v<Impl, full_buffer_impl>
            || std::is_same_v<Impl, pushed_sequential_impl>) {
            impl_->push_next_page(content);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This file_reader constructor is not supported for the selected backend");
        }
    }

    file_reader(const std::string& fn, size_t page_size, size_t page_capacity)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, paged_file_impl>) {
            impl_ = std::make_shared<Impl>(fn, page_size, page_capacity);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This file_reader constructor is not supported for the selected backend");
        }
    }

    file_reader clone() const {
        file_reader c(*this);
        c.cursor_ = cursor_;
        return c;
    }

    void seek(size_t pos) {
        if (pos > size()) {
            throw std::out_of_range("seek out of range");
        }
        cursor_ = pos;
    }

    size_t tell() const { return cursor_; }

    size_t size() const { return impl_->size(); }
    size_t remaining() const { return size() - cursor_; }

    char peek() const {
        if (cursor_ >= size()) {
            throw std::out_of_range("peek at EOF");
        }
        return impl_->get(cursor_);
    }

    uint64_t peek_u64() const {
        if (remaining() < sizeof(uint64_t)) {
            throw std::out_of_range("peek_u64 at EOF");
        }
        return impl_->get_u64(cursor_);
    }

    uint32_t peek_u32() const {
        if (remaining() < sizeof(uint32_t)) {
            throw std::out_of_range("peek_u32 at EOF");
        }
        return impl_->get_u32(cursor_);
    }

    void increment(size_t n = 1) {
        if (cursor_ + n > size()) {
            throw std::out_of_range("increment past EOF");
        }
        cursor_ += n;
    }

    void push_next_page(const std::string& data) {
        impl_->push_next_page(data);
    }

    void drop_pages() {
        impl_->drop_pages(0);
    }

    void drop_pages(size_t up_to_pos) {
        impl_->drop_pages(up_to_pos);
    }

    bool eof() const {
        return cursor_ >= size();
    }

    char read() {
        auto c = peek();
        increment(1);
        return c;
    }

    char get(size_t offset) const {
        return impl_->get(offset);
    }

private:
    std::shared_ptr<Impl> impl_;
    size_t cursor_ = 0;
};

class IFC_PARSE_API full_buffer_impl {
public:
    full_buffer_impl() = default;
    explicit full_buffer_impl(const std::string& fn);
    explicit full_buffer_impl(const caller_fed_tag&);
    full_buffer_impl(const std::string& content, const caller_fed_tag&);

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void push_next_page(const std::string& data);
    void drop_pages(size_t pos);

private:
    std::vector<char> buf_;
    size_t size_ = 0;
};

class IFC_PARSE_API paged_file_impl {
public:
    struct Entry {
        file_reader_page page;
        std::list<size_t>::iterator it;
    };

    paged_file_impl(const std::string& fn, size_t page_size, size_t cap);
    ~paged_file_impl();

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void push_next_page(const std::string& data);
    void drop_pages(size_t pos);

private:
    const file_reader_page& fetchPage_(size_t idx) const;
    void touch_(std::unordered_map<size_t, Entry>::iterator it) const;
    void evict_() const;

    std::string fn_;
    FILE* fp_ = nullptr;
    size_t file_size_ = 0;
    size_t page_size_ = 4096;
    size_t capacity_ = 8;
    mutable std::list<size_t> lru_;
    mutable std::unordered_map<size_t, Entry> map_;
};

#ifdef USE_MMAP
class IFC_PARSE_API mmap_impl {
public:
    explicit mmap_impl(const std::string& fn);

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void push_next_page(const std::string& data);
    void drop_pages(size_t pos);

private:
    boost::iostreams::mapped_file_source map_;
    size_t size_ = 0;
};
#endif

class IFC_PARSE_API pushed_sequential_impl {
public:
    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void push_next_page(const std::string& data);
    void drop_pages(size_t pos);

private:
    std::deque<file_reader_page> pages_;
    size_t discarded_page_bytes_ = 0;
};

} // namespace ifcopenshell

#endif
