#include "FileReader.h"

#include <algorithm>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <list>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>
#include <deque>

#ifdef USE_MMAP
#include <boost/iostreams/device/mapped_file.hpp>
#include <boost/filesystem/path.hpp>
#endif

#include "utils.h"

namespace {

#if defined(_WIN32)
    inline void file_seek_abs(FILE* f, std::uint64_t off) {
        if (_fseeki64(f, static_cast<long long>(off), SEEK_SET) != 0)
            throw std::runtime_error("fseek failed");
    }
#else
    inline void file_seek_abs(FILE* f, std::uint64_t off) {
        if (fseeko(f, static_cast<off_t>(off), SEEK_SET) != 0)
            throw std::runtime_error("fseeko failed");
    }
#endif

} // namespace

using namespace IfcParse;

struct FullBufferImpl final : FileReader::Impl {
    std::vector<char> buf_;
    explicit FullBufferImpl(const std::string& fn) {
#ifdef _MSC_VER
        std::wstring fn_ws = IfcUtil::path::from_utf8(fn);
        const wchar_t* fn_wide = fn_ws.c_str();
        auto stream = _wfopen(fn_wide, L"rb");
#else
        auto stream = fopen(fn.c_str(), "rb");
#endif
        fseek(stream, 0, SEEK_END);
        buf_.resize((size_t)ftell(stream));
        rewind(stream);
        buf_.resize((size_t) fread(buf_.data(), 1, buf_.capacity(), stream));
        fclose(stream);
    }
    size_t size() const override { return buf_.size(); }
    char get(size_t pos) const override {
        if (pos >= buf_.size()) throw std::out_of_range("get out of range");
        return buf_[pos];
    }
    const char* contiguous_data() const override { return buf_.data(); }
};

struct PagedFileImpl final : FileReader::Impl {
    std::string fn_;
    FILE* fp_ = nullptr;
    size_t file_size_ = 0;
    size_t page_size_ = 4096;

    // LRU cache
    size_t capacity_ = 8;
    mutable std::list<size_t> lru_;
    struct Entry {
        FileReader::Page page;
        std::list<size_t>::iterator it;
    };
    mutable std::unordered_map<size_t, Entry> map_;

    PagedFileImpl(const std::string& fn, size_t page_size, size_t cap)
        : fn_(fn), page_size_(std::max<size_t>(512, page_size)), capacity_(std::max<size_t>(2, cap))
    {
#ifdef _MSC_VER
        std::wstring fn_ws = IfcUtil::path::from_utf8(fn);
        const wchar_t* fn_wide = fn_ws.c_str();
        fp_ = _wfopen(fn_wide, L"rb");
#else
        fp_ = fopen(fn.c_str(), "rb");
#endif
        fseek(fp_, 0, SEEK_END);
        file_size_ = (size_t)ftell(fp_);
        rewind(fp_);
    }

    ~PagedFileImpl() override {
        if (fp_) std::fclose(fp_);
        fp_ = nullptr;
    }

    size_t size() const override { return file_size_; }

    char get(size_t pos) const override {
        if (pos >= file_size_) throw std::out_of_range("get out of range");
        const size_t pidx = pos / page_size_;
        const FileReader::Page& p = fetchPage_(pidx);
        const size_t off = pos % page_size_;
        if (off >= p.data.size()) throw std::out_of_range("offset beyond valid page bytes");
        return p.data[off];
    }

private:
    const FileReader::Page& fetchPage_(size_t idx) const {
        auto it = map_.find(idx);
        if (it != map_.end()) {
            touch_(it);
            return it->second.page;
        }
        // Load page from disk using persistent FILE*
        FileReader::Page pg;
        pg.data.resize(page_size_);
        const size_t begin = idx * page_size_;
        const size_t avail = std::min(page_size_, file_size_ - begin);

        file_seek_abs(fp_, begin);
        if (avail > 0) {
            const size_t nread = std::fread(pg.data.data(), 1, avail, fp_);
            if (nread != avail) throw std::runtime_error("Short fread on page");
        }
        // trim to actual size
		pg.data.resize(avail);

        // Insert into LRU
        if (map_.size() >= capacity_) evict_();
        lru_.push_front(idx);
        auto lit = lru_.begin();
        auto [emplaced_it, ok] = map_.emplace(idx, Entry{ std::move(pg), lit });
        (void)ok;
        return emplaced_it->second.page;
    }

    void touch_(typename std::unordered_map<size_t, Entry>::iterator it) const {
        lru_.erase(it->second.it);
        lru_.push_front(it->first);
        it->second.it = lru_.begin();
    }

    void evict_() const {
        if (lru_.empty()) return;
        const size_t victim = lru_.back();
        lru_.pop_back();
        map_.erase(victim);
    }
};

#ifdef USE_MMAP
struct MMapImpl final : FileReader::Impl {
    boost::iostreams::mapped_file_source map_;
    size_t size_ = 0;

    explicit MMapImpl(const std::string& fn) {
        map_.open(boost::filesystem::path(IfcUtil::path::from_utf8(fn)));
        if (!map_.is_open()) throw std::runtime_error("Failed to open mapped_file_source");
        size_ = static_cast<size_t>(map_.size());
    }

    size_t size() const override { return size_; }

    char get(size_t pos) const override {
        if (pos >= size_) throw std::out_of_range("get out of range");
        return map_.data()[pos];
    }

    const char* contiguous_data() const override { return map_.data(); }
};
#endif

/// User-pushed sequential backend with an arbitrary-length queue of future pages.
/// We keep a deque of pages; when reads move forward, we drop fully-consumed
/// pages from the front to release memory.
struct PushedSequentialImpl final : std::enable_shared_from_this<PushedSequentialImpl>, FileReader::Impl {
	// Deque of pages, front is earliest in file.
    std::deque<FileReader::Page> pages_;
    // total bytes in dropped pages
	size_t discarded_page_bytes_ = 0;

    size_t size() const override {
        size_t n = discarded_page_bytes_;
		for (auto& pg : pages_) n += pg.data.size();
		return n;
    }

    // Drop fully-consumed pages so pos is guaranteed to be within the first page
    void dropPages(size_t pos) override {
        while (!pages_.empty()) {
            if (pos - discarded_page_bytes_ >= pages_.front().data.size()) {
				discarded_page_bytes_ += pages_.front().data.size();
                pages_.pop_front();
            } else {
                break;
            }
        }
    }

    char get(size_t pos) const override {
        /*
        auto self = const_cast<PushedSequentialImpl*>(this);
        // We do not do this automatically because all variable width tokens:
        // ENUM/STRING/BINARY/KEYWORD are stored as file offsets until a full
        // entity instance is finalized.
        if (this->shared_from_this().use_count() == 2) {
            // only drop pages when there is only one active client.
            // NB this->shared_from_this() increases count by 1
            self->drop_consumed_up_to(pos);
        }
        */

        const size_t avail_end = size();
        if (pos >= avail_end) throw std::out_of_range("pushed backend: position not committed yet");

		pos -= discarded_page_bytes_;

		size_t page_start = 0;
        for (const auto& pg : pages_) {
            if (pos < page_start + pg.data.size()) {
                const size_t off = pos - page_start;
                return pg.data[off];
            } else {
				page_start += pg.data.size();
            }
        }

        throw std::out_of_range("pushed backend: internal inconsistency");
    }

    void pushNextPage(const std::string& data) override {
        FileReader::Page p; p.data.assign(data.data(), data.data() + data.size());
        pages_.push_back(std::move(p));
    }
};

IfcParse::FileReader::FileReader(const std::string& fn)
    : cursor_(0)
{
	impl_ = std::make_shared<FullBufferImpl>(fn);
	init_contiguous_();
}

IfcParse::FileReader::FileReader(const std::string& fn, const mmap_tag&)
    : cursor_(0)
{
#ifdef USE_MMAP
	impl_ = std::make_shared<MMapImpl>(fn);
	init_contiguous_();
#else
    (void)fn;
    throw std::runtime_error("IfcParse::FileReader: mmap_tag specified but library not compiled with USE_MMAP");
#endif
}

IfcParse::FileReader::FileReader(const caller_fed_tag&)
    : cursor_(0)
{
	impl_ = std::make_shared<PushedSequentialImpl>();
	init_contiguous_();
}

IfcParse::FileReader::FileReader(const std::string& content, const caller_fed_tag&)
{
    impl_ = std::make_shared<PushedSequentialImpl>();
	impl_->pushNextPage(content);
	init_contiguous_();
}

IfcParse::FileReader::FileReader(const std::string& fn, size_t page_size, size_t page_capacity)
    : cursor_(0)
{
	impl_ = std::make_shared<PagedFileImpl>(fn, page_size, page_capacity);
	init_contiguous_();
}

void IfcParse::FileReader::init_contiguous_() {
    contiguous_ = impl_->contiguous_data();
    contiguous_size_ = contiguous_ != nullptr ? impl_->size() : 0;
}

char IfcParse::FileReader::peek_paged_() const {
    if (cursor_ >= impl_->size()) throw std::out_of_range("peek at EOF");
    return impl_->get(cursor_);
}

FileReader FileReader::clone() const {
    FileReader c(*this);
    c.cursor_ = this->cursor_;
    return c;
}

void IfcParse::FileReader::pushNextPage(const std::string& data)
{
    impl_->pushNextPage(data);
}

void IfcParse::FileReader::dropPages()
{
    impl_->dropPages(0);
}

void IfcParse::FileReader::dropPages(size_t up_to_pos)
{
    impl_->dropPages(up_to_pos);
}

