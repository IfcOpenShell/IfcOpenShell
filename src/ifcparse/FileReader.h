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
#include <memory>
#include <optional>
#include <string>
#include <variant>
#include <stdexcept>
#include <vector>

namespace IfcParse {

/// \brief Read-only file accessor that supports four backends:
///  - full-buffer in RAM
///  - paged (LRU-cached with capacity)
///  - memory-mapped via boost::iostreams
///  - user-pushed sequential pages (caller feeds pages intended for streaming reads in WASM)
class IFC_PARSE_API FileReader {
public:
    struct Page { std::vector<char> data; };

    /// \brief Tag to choose memory-mapped backend via boost::iostreams::mapped_file_source.
    struct mmap_tag {};
    /// \brief Tag to choose user-pushed sequential pages.
    struct caller_fed_tag {};

    /// \brief Construct a FileReader.
    /// \param fn File path.
    /// \param maybe_mmaped_or_chunked
    ///        - std::nullopt: full-buffer mode (entire file loaded into memory)
    ///        - size_t: paged mode with this page size in bytes (e.g., 4096)
    ///        - mmap_tag: memory-mapped mode using boost::iostreams::mapped_file_source
    /// \param page_cache_capacity Number of pages to keep in the LRU when in paged mode.
    FileReader(const std::string& fn);

    FileReader(const std::string& fn, const mmap_tag&);

    FileReader(const caller_fed_tag&);
    FileReader(const std::string& content, const caller_fed_tag&);

    FileReader(const std::string& fn, size_t page_size, size_t page_capacity);

    /// \brief Copy-construct a new reader sharing the underlying storage but with its own cursor.
    FileReader clone() const;

    /// \brief Seek to an absolute byte position.
    /// \throws std::out_of_range if pos > size().
    void seek(size_t pos) {
        if (pos > size()) throw std::out_of_range("seek out of range");
        cursor_ = pos;
    }

    /// \brief Return the current cursor position.
    size_t tell() const { return cursor_; }

    /// \brief Total file size in bytes.
    size_t size() const { return contiguous_ ? contiguous_size_ : impl_->size(); }

    /// \brief Peek the byte at the current cursor.
    /// \throws std::out_of_range at EOF.
    char peek() const {
        if (contiguous_) {
            if (cursor_ >= contiguous_size_) throw std::out_of_range("peek at EOF");
            return contiguous_[cursor_];
        }
        return peek_paged_();
    }

    /// \brief Advance the cursor by n bytes (default 1).
    /// \throws std::out_of_range if advancing crosses EOF.
    void increment(size_t n = 1) {
        if (cursor_ + n > size()) throw std::out_of_range("increment past EOF");
        cursor_ += n;
    }

    /// \brief Push the next sequential page (pushed backend only).
	/// \param data Contents of the page.
    /// \throws std::logic_error if the current backend is not in pushed mode
    void pushNextPage(const std::string& data);

    /// \brief Drops pages up to cursor position or provided offset. Does nothing when current backend is not in pushed mode
    /// \param up_to_pos Pages with an end offset before up_to_pos are dropped from memory
    void dropPages();
    void dropPages(size_t up_to_pos);

    /// \brief Returns true if the cursor is at or beyond the end of available data.
    /// For the pushed backend, EOF means all pushed bytes have been consumed.
    bool eof() const { return cursor_ >= size(); }

    /// \brief Equivalent of peek() followed by increment(1)
    char read() {
        auto c = peek();
        increment(1);
        return c;
    }

    /// \brief Equivalent of peek() followed by increment(1)
    char get(size_t offset) const {
        if (contiguous_) {
            if (offset >= contiguous_size_) throw std::out_of_range("get out of range");
            return contiguous_[offset];
        }
        return impl_->get(offset);
    }

    /// \brief Entire backing buffer, indexed by absolute file offset, when the backend
    /// is stable contiguous memory (full-buffer or mmap); nullptr otherwise.
    const char* contiguous_buffer() const { return contiguous_; }

    struct Impl {
        virtual ~Impl() = default;
        virtual size_t size() const = 0;
        virtual char get(size_t pos) const = 0;
        /// \brief Backends with a stable in-memory buffer return it here so that the
        /// per-character accessors can bypass virtual dispatch; default nullptr.
        virtual const char* contiguous_data() const { return nullptr; }
        /// \brief Backend may support pushing pages; default throws.
        virtual void pushNextPage(const std::string&) {
            throw std::logic_error("push_next_page: backend does not support pushed mode");
        }
        virtual void dropPages(size_t) {
            // empty on purpose
        }
    };

private:
    std::shared_ptr<Impl> impl_;
    size_t cursor_ = 0;
    const char* contiguous_ = nullptr;
    size_t contiguous_size_ = 0;

    void init_contiguous_();
    char peek_paged_() const;
};

} // namespace IfcParse

#endif
