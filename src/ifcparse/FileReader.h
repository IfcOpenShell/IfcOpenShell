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

namespace IfcParse {

struct FileReaderPage {
    std::vector<char> data;
};

struct caller_fed_tag {};

template <typename>
inline constexpr bool file_reader_dependent_false_v = false;

class IFC_PARSE_API FullBufferImpl;
class IFC_PARSE_API PagedFileImpl;
#ifdef USE_MMAP
class IFC_PARSE_API MMapImpl;
#endif
class IFC_PARSE_API PushedSequentialImpl;

template <typename Impl>
class FileReader {
public:
    using impl_type = Impl;
    using Page = FileReaderPage;

    FileReader() = default;

    explicit FileReader(const std::string& fn)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, FullBufferImpl>
#ifdef USE_MMAP
            || std::is_same_v<Impl, MMapImpl>
#endif
        ) {
            impl_ = std::make_shared<Impl>(fn);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This FileReader constructor is not supported for the selected backend");
        }
    }

    explicit FileReader(const caller_fed_tag&)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, PushedSequentialImpl>) {
            impl_ = std::make_shared<Impl>();
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This FileReader constructor is not supported for the selected backend");
        }
    }

    FileReader(const std::string& content, const caller_fed_tag&)
        : FileReader(caller_fed_tag{}) {
        if constexpr (std::is_same_v<Impl, PushedSequentialImpl>) {
            impl_->pushNextPage(content);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This FileReader constructor is not supported for the selected backend");
        }
    }

    FileReader(const std::string& fn, size_t page_size, size_t page_capacity)
        : cursor_(0) {
        if constexpr (std::is_same_v<Impl, PagedFileImpl>) {
            impl_ = std::make_shared<Impl>(fn, page_size, page_capacity);
        } else {
            static_assert(file_reader_dependent_false_v<Impl>, "This FileReader constructor is not supported for the selected backend");
        }
    }

    FileReader clone() const {
        FileReader c(*this);
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

    void pushNextPage(const std::string& data) {
        impl_->pushNextPage(data);
    }

    void dropPages() {
        impl_->dropPages(0);
    }

    void dropPages(size_t up_to_pos) {
        impl_->dropPages(up_to_pos);
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

class IFC_PARSE_API FullBufferImpl {
public:
    explicit FullBufferImpl(const std::string& fn);

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void pushNextPage(const std::string& data);
    void dropPages(size_t pos);

private:
    std::vector<char> buf_;
    size_t size_;
};

class IFC_PARSE_API PagedFileImpl {
public:
    struct Entry {
        FileReaderPage page;
        std::list<size_t>::iterator it;
    };

    PagedFileImpl(const std::string& fn, size_t page_size, size_t cap);
    ~PagedFileImpl();

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void pushNextPage(const std::string& data);
    void dropPages(size_t pos);

private:
    const FileReaderPage& fetchPage_(size_t idx) const;
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
class IFC_PARSE_API MMapImpl {
public:
    explicit MMapImpl(const std::string& fn);

    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void pushNextPage(const std::string& data);
    void dropPages(size_t pos);

private:
    boost::iostreams::mapped_file_source map_;
    size_t size_ = 0;
};
#endif

class IFC_PARSE_API PushedSequentialImpl {
public:
    size_t size() const;
    char get(size_t pos) const;
    uint32_t get_u32(size_t pos) const;
    uint64_t get_u64(size_t pos) const;
    void pushNextPage(const std::string& data);
    void dropPages(size_t pos);

private:
    std::deque<FileReaderPage> pages_;
    size_t discarded_page_bytes_ = 0;
};

} // namespace IfcParse

#endif
