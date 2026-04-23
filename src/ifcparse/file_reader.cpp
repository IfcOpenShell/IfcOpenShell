#include "file_reader.h"

#include <algorithm>
#include <cstring>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <stdexcept>

#ifdef USE_MMAP
#include <boost/filesystem/path.hpp>
#endif

#include "utils.h"

namespace {

#if defined(_WIN32)
inline void file_seek_abs(FILE* f, std::uint64_t off) {
    if (_fseeki64(f, static_cast<long long>(off), SEEK_SET) != 0) {
        throw std::runtime_error("fseek failed");
    }
}
#else
inline void file_seek_abs(FILE* f, std::uint64_t off) {
    if (fseeko(f, static_cast<off_t>(off), SEEK_SET) != 0) {
        throw std::runtime_error("fseeko failed");
    }
}
#endif

} // namespace

using namespace ifcopenshell;

namespace {

template <typename T, typename Fn>
T gather_value(Fn&& fn) {
    char bytes[sizeof(T)];
    for (size_t i = 0; i < sizeof(bytes); ++i) {
        bytes[i] = fn(i);
    }
    T value;
    std::memcpy(&value, bytes, sizeof(value));
    return value;
}

} // namespace

full_buffer_impl::full_buffer_impl(const std::string& fn) {
#ifdef _MSC_VER
    std::wstring fn_ws = ifcopenshell::path::from_utf8(fn);
    const wchar_t* fn_wide = fn_ws.c_str();
    auto stream = _wfopen(fn_wide, L"rb");
#else
    auto stream = fopen(fn.c_str(), "rb");
#endif
    if (!stream) {
        throw std::runtime_error("Failed to open file");
    }
    fseek(stream, 0, SEEK_END);
    size_ = (size_t)ftell(stream);
    buf_.resize(size_);
    rewind(stream);
    buf_.resize((size_t)fread(buf_.data(), 1, buf_.capacity(), stream));
    fclose(stream);
}

full_buffer_impl::full_buffer_impl(const caller_fed_tag&) {
}

full_buffer_impl::full_buffer_impl(const std::string& content, const caller_fed_tag&)
    : buf_(content.begin(), content.end())
    , size_(content.size()) {
}

size_t full_buffer_impl::size() const { return size_; }

char full_buffer_impl::get(size_t pos) const {
    if (pos >= buf_.size()) {
        throw std::out_of_range("get out of range");
    }
    return buf_[pos];
}

uint64_t full_buffer_impl::get_u64(size_t pos) const {
    if (pos + sizeof(uint64_t) > buf_.size()) {
        throw std::out_of_range("get_u64 out of range");
    }
    uint64_t value;
    std::memcpy(&value, buf_.data() + pos, sizeof(value));
    return value;
}

uint32_t full_buffer_impl::get_u32(size_t pos) const {
    if (pos + sizeof(uint32_t) > buf_.size()) {
        throw std::out_of_range("get_u32 out of range");
    }
    uint32_t value;
    std::memcpy(&value, buf_.data() + pos, sizeof(value));
    return value;
}

void full_buffer_impl::push_next_page(const std::string& data) {
    buf_.insert(buf_.end(), data.begin(), data.end());
    size_ = buf_.size();
}

void full_buffer_impl::drop_pages(size_t) {
}

paged_file_impl::paged_file_impl(const std::string& fn, size_t page_size, size_t cap)
    : fn_(fn)
    , page_size_(std::max<size_t>(512, page_size))
    , capacity_(std::max<size_t>(2, cap)) {
#ifdef _MSC_VER
    std::wstring fn_ws = ifcopenshell::path::from_utf8(fn);
    const wchar_t* fn_wide = fn_ws.c_str();
    fp_ = _wfopen(fn_wide, L"rb");
#else
    fp_ = fopen(fn.c_str(), "rb");
#endif
    if (!fp_) {
        throw std::runtime_error("Failed to open file");
    }
    fseek(fp_, 0, SEEK_END);
    file_size_ = (size_t)ftell(fp_);
    rewind(fp_);
}

paged_file_impl::~paged_file_impl() {
    if (fp_) {
        std::fclose(fp_);
    }
    fp_ = nullptr;
}

size_t paged_file_impl::size() const { return file_size_; }

char paged_file_impl::get(size_t pos) const {
    if (pos >= file_size_) {
        throw std::out_of_range("get out of range");
    }
    const size_t pidx = pos / page_size_;
    const file_reader_page& p = fetchPage_(pidx);
    const size_t off = pos % page_size_;
    if (off >= p.data.size()) {
        throw std::out_of_range("offset beyond valid page bytes");
    }
    return p.data[off];
}

uint64_t paged_file_impl::get_u64(size_t pos) const {
    if (pos + sizeof(uint64_t) > file_size_) {
        throw std::out_of_range("get_u64 out of range");
    }

    const size_t pidx = pos / page_size_;
    const file_reader_page& p = fetchPage_(pidx);
    const size_t off = pos % page_size_;
    if (off + sizeof(uint64_t) <= p.data.size()) {
        uint64_t value;
        std::memcpy(&value, p.data.data() + off, sizeof(value));
        return value;
    }

    return gather_value<uint64_t>([&](size_t i) { return get(pos + i); });
}

uint32_t paged_file_impl::get_u32(size_t pos) const {
    if (pos + sizeof(uint32_t) > file_size_) {
        throw std::out_of_range("get_u32 out of range");
    }

    const size_t pidx = pos / page_size_;
    const file_reader_page& p = fetchPage_(pidx);
    const size_t off = pos % page_size_;
    if (off + sizeof(uint32_t) <= p.data.size()) {
        uint32_t value;
        std::memcpy(&value, p.data.data() + off, sizeof(value));
        return value;
    }

    return gather_value<uint32_t>([&](size_t i) { return get(pos + i); });
}

void paged_file_impl::push_next_page(const std::string&) {
    throw std::logic_error("push_next_page: backend does not support pushed mode");
}

void paged_file_impl::drop_pages(size_t) {
}

const file_reader_page& paged_file_impl::fetchPage_(size_t idx) const {
    auto it = map_.find(idx);
    if (it != map_.end()) {
        touch_(it);
        return it->second.page;
    }

    file_reader_page pg;
    pg.data.resize(page_size_);
    const size_t begin = idx * page_size_;
    const size_t avail = std::min(page_size_, file_size_ - begin);

    file_seek_abs(fp_, begin);
    if (avail > 0) {
        const size_t nread = std::fread(pg.data.data(), 1, avail, fp_);
        if (nread != avail) {
            throw std::runtime_error("Short fread on page");
        }
    }
    pg.data.resize(avail);

    if (map_.size() >= capacity_) {
        evict_();
    }
    lru_.push_front(idx);
    auto lit = lru_.begin();
    auto [emplaced_it, ok] = map_.emplace(idx, Entry{std::move(pg), lit});
    (void)ok;
    return emplaced_it->second.page;
}

void paged_file_impl::touch_(std::unordered_map<size_t, Entry>::iterator it) const {
    lru_.erase(it->second.it);
    lru_.push_front(it->first);
    it->second.it = lru_.begin();
}

void paged_file_impl::evict_() const {
    if (lru_.empty()) {
        return;
    }
    const size_t victim = lru_.back();
    lru_.pop_back();
    map_.erase(victim);
}

#ifdef USE_MMAP
mmap_impl::mmap_impl(const std::string& fn) {
    map_.open(boost::filesystem::path(ifcopenshell::path::from_utf8(fn)));
    if (!map_.is_open()) {
        throw std::runtime_error("Failed to open mapped_file_source");
    }
    size_ = static_cast<size_t>(map_.size());
}

size_t mmap_impl::size() const { return size_; }

char mmap_impl::get(size_t pos) const {
    if (pos >= size_) {
        throw std::out_of_range("get out of range");
    }
    return map_.data()[pos];
}

uint64_t mmap_impl::get_u64(size_t pos) const {
    if (pos + sizeof(uint64_t) > size_) {
        throw std::out_of_range("get_u64 out of range");
    }
    uint64_t value;
    std::memcpy(&value, map_.data() + pos, sizeof(value));
    return value;
}

uint32_t mmap_impl::get_u32(size_t pos) const {
    if (pos + sizeof(uint32_t) > size_) {
        throw std::out_of_range("get_u32 out of range");
    }
    uint32_t value;
    std::memcpy(&value, map_.data() + pos, sizeof(value));
    return value;
}

void mmap_impl::push_next_page(const std::string&) {
    throw std::logic_error("push_next_page: backend does not support pushed mode");
}

void mmap_impl::drop_pages(size_t) {
}
#endif

size_t pushed_sequential_impl::size() const {
    size_t n = discarded_page_bytes_;
    for (const auto& pg : pages_) {
        n += pg.data.size();
    }
    return n;
}

void pushed_sequential_impl::drop_pages(size_t pos) {
    while (!pages_.empty()) {
        if (pos - discarded_page_bytes_ >= pages_.front().data.size()) {
            discarded_page_bytes_ += pages_.front().data.size();
            pages_.pop_front();
        } else {
            break;
        }
    }
}

char pushed_sequential_impl::get(size_t pos) const {
    const size_t avail_end = size();
    if (pos >= avail_end) {
        throw std::out_of_range("pushed backend: position not committed yet");
    }

    pos -= discarded_page_bytes_;

    size_t page_start = 0;
    for (const auto& pg : pages_) {
        if (pos < page_start + pg.data.size()) {
            const size_t off = pos - page_start;
            return pg.data[off];
        }
        page_start += pg.data.size();
    }

    throw std::out_of_range("pushed backend: internal inconsistency");
}

uint64_t pushed_sequential_impl::get_u64(size_t pos) const {
    if (pos + sizeof(uint64_t) > size()) {
        throw std::out_of_range("get_u64 out of range");
    }

    size_t relative_pos = pos - discarded_page_bytes_;
    size_t page_start = 0;
    for (const auto& pg : pages_) {
        if (relative_pos < page_start + pg.data.size()) {
            const size_t off = relative_pos - page_start;
            if (off + sizeof(uint64_t) <= pg.data.size()) {
                uint64_t value;
                std::memcpy(&value, pg.data.data() + off, sizeof(value));
                return value;
            }
            break;
        }
        page_start += pg.data.size();
    }

    return gather_value<uint64_t>([&](size_t i) { return get(pos + i); });
}

uint32_t pushed_sequential_impl::get_u32(size_t pos) const {
    if (pos + sizeof(uint32_t) > size()) {
        throw std::out_of_range("get_u32 out of range");
    }

    size_t relative_pos = pos - discarded_page_bytes_;
    size_t page_start = 0;
    for (const auto& pg : pages_) {
        if (relative_pos < page_start + pg.data.size()) {
            const size_t off = relative_pos - page_start;
            if (off + sizeof(uint32_t) <= pg.data.size()) {
                uint32_t value;
                std::memcpy(&value, pg.data.data() + off, sizeof(value));
                return value;
            }
            break;
        }
        page_start += pg.data.size();
    }

    return gather_value<uint32_t>([&](size_t i) { return get(pos + i); });
}

void pushed_sequential_impl::push_next_page(const std::string& data) {
    file_reader_page p;
    p.data.assign(data.data(), data.data() + data.size());
    pages_.push_back(std::move(p));
}
