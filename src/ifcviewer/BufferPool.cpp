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

#include "BufferPool.h"
#include "GpuAllocScope.h"

#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstring>

BufferPool::~BufferPool() {
    destroy();
}

void BufferPool::configure(WGPUInstance instance, WGPUDevice device,
                               WGPUBufferUsage usage,
                               uint64_t per_sub_buffer_capacity,
                               const char* label_prefix) {
    destroy();
    instance_                = instance;
    device_                  = device;
    usage_                   = usage;
    per_sub_buffer_capacity_ = per_sub_buffer_capacity;
    last_growth_size_        = per_sub_buffer_capacity;
    label_prefix_            = label_prefix ? label_prefix : "";
}

void BufferPool::destroy() {
    for (auto& sub_pool : sub_pools_) {
        if (sub_pool.buffer) wgpuBufferRelease(sub_pool.buffer);
    }
    sub_pools_.clear();
    device_                  = nullptr;
    instance_                = nullptr;
    usage_                   = 0;
    per_sub_buffer_capacity_ = 0;
    last_growth_size_        = 0;
    growth_disabled_         = false;
    growth_pending_          = false;
    label_prefix_.clear();
}

bool BufferPool::addSubBuffer() {
    if (!device_ || per_sub_buffer_capacity_ == 0) return false;
    if (growth_disabled_) return false;

    uint64_t try_size = last_growth_size_ > 0
                      ? last_growth_size_
                      : per_sub_buffer_capacity_;
    if (try_size < MIN_SUB_BUFFER_BYTES) try_size = MIN_SUB_BUFFER_BYTES;

    // Never overshoot the budget: the cache's whole job is to stop short
    // of what the required tier needs, and a sub-buffer that straddles
    // the line would take exactly the bytes it was told to leave. A
    // budget refusal is not a driver refusal, so growth_disabled_ is not
    // latched — the budget is the (already lower) ceiling.
    if (max_total_capacity_bytes_ > 0) {
        const uint64_t total = total_capacity_bytes();
        if (total + MIN_SUB_BUFFER_BYTES > max_total_capacity_bytes_) return false;
        try_size = std::min(try_size, max_total_capacity_bytes_ - total);
    }

#if defined(__EMSCRIPTEN__)
    // Web can't synchronously learn whether createBuffer OOM'd: the
    // desktop spin-wait that drains PopErrorScope would block the JS
    // event loop so the resolving microtask never runs (page hangs), and
    // Dawn returns a NON-NULL error buffer on OOM — so a plain
    // `buf != nullptr` check silently accepts an invalid buffer, and
    // every bind group built against it then fails ("BindGroup is
    // invalid" spam). Instead add the sub-buffer as *provisional* (alloc
    // skips it), then validate it through a non-blocking async error
    // scope. resolveProvisionalGrowth() clears the flag once it's known
    // good, or drops it and latches growth_disabled_ on a real OOM. Only
    // one provisional grow is ever in flight (growth_pending_), so a hung
    // validation can't spawn a pile of sub-buffers.
    if (growth_pending_) return false;

    char label[128];
    std::snprintf(label, sizeof(label), "%s.sub%zu",
                  label_prefix_.c_str(), sub_pools_.size());
    WGPUBufferDescriptor desc = {};
    desc.usage        = usage_;
    desc.size         = try_size;
    desc.label.data   = label;
    desc.label.length = std::strlen(label);

    GpuAllocScope scope(instance_, device_);
    WGPUBuffer buf = wgpuDeviceCreateBuffer(device_, &desc);

    SubPool sp;
    sp.buffer      = buf;
    sp.capacity    = try_size;
    sp.used        = 0;
    sp.provisional = true;
    sp.free_ranges.push_back({0, try_size});
    sub_pools_.push_back(std::move(sp));
    last_growth_size_ = try_size;
    growth_pending_   = true;

    scope.end([this](bool ok) { resolveProvisionalGrowth(!ok); });

    // No usable space yet: the provisional sub-buffer isn't handed out
    // until validated. alloc fails this frame and retries on a later one.
    return false;
#else
    while (try_size >= MIN_SUB_BUFFER_BYTES) {
        char label[128];
        std::snprintf(label, sizeof(label), "%s.sub%zu",
                      label_prefix_.c_str(), sub_pools_.size());

        WGPUBufferDescriptor desc = {};
        desc.usage        = usage_;
        desc.size         = try_size;
        desc.label.data   = label;
        desc.label.length = std::strlen(label);

        GpuAllocScope scope(instance_, device_);
        WGPUBuffer buf = wgpuDeviceCreateBuffer(device_, &desc);
        bool ok = false;
        scope.end([&](bool result) { ok = result && buf; });

        if (ok) {
            SubPool sp;
            sp.buffer   = buf;
            sp.capacity = try_size;
            sp.used     = 0;
            sp.free_ranges.push_back({0, try_size});
            sub_pools_.push_back(std::move(sp));
            last_growth_size_ = try_size;
            std::fprintf(stderr,
                "[wgpu pool] added sub-buffer %zu (%llu MB); pool total now %llu MB\n",
                sub_pools_.size() - 1,
                (unsigned long long)(try_size / (1024 * 1024)),
                (unsigned long long)(total_capacity_bytes() / (1024 * 1024)));
            return true;
        }
        if (buf) wgpuBufferRelease(buf);
        try_size /= 2;
    }

    std::fprintf(stderr,
        "[wgpu pool] driver refused growth even at %llu MB; "
        "pool capped at %llu MB across %zu sub-buffer(s) — growth disabled\n",
        (unsigned long long)(MIN_SUB_BUFFER_BYTES / (1024 * 1024)),
        (unsigned long long)(total_capacity_bytes() / (1024 * 1024)),
        sub_pools_.size());
    growth_disabled_ = true;
    return false;
#endif  // __EMSCRIPTEN__
}

uint64_t BufferPool::releaseNewestSubBuffer(
        const std::function<void(int sub_idx)>& evict_sub_buffer) {
    if (sub_pools_.empty()) return 0;
    const int idx = int(sub_pools_.size()) - 1;
    if (sub_pools_[size_t(idx)].provisional) return 0;
    evict_sub_buffer(idx);
    SubPool& sub_pool = sub_pools_[size_t(idx)];
    assert(sub_pool.used == 0 && "owner must free every slice before a sub-buffer is released");
    if (sub_pool.buffer && sub_pool.owns_handle) {
        // Destroy, not just release: the handle may still be
        // referenced by in-flight work, and destroy tells the
        // backend to reclaim the memory as soon as that completes
        // instead of when the last reference goes away.
        wgpuBufferDestroy(sub_pool.buffer);
        wgpuBufferRelease(sub_pool.buffer);
    }
    const uint64_t released = sub_pool.capacity;
    sub_pools_.pop_back();
    return released;
}

namespace {
void logRelease(uint64_t released, uint64_t total, size_t count, uint64_t budget) {
    if (released == 0) return;
    std::fprintf(stderr,
        "[wgpu pool] released %llu MB under memory pressure; pool now %llu MB "
        "across %zu sub-buffer(s), budget %llu MB\n",
        (unsigned long long)(released / (1024 * 1024)),
        (unsigned long long)(total / (1024 * 1024)),
        count,
        (unsigned long long)(budget / (1024 * 1024)));
}
}  // namespace

uint64_t BufferPool::shrinkToCapacity(
        uint64_t target_bytes,
        const std::function<void(int sub_idx)>& evict_sub_buffer) {
    uint64_t released = 0;
    while (!sub_pools_.empty()) {
        const SubPool& newest = sub_pools_.back();
        if (newest.provisional) break;
        const uint64_t capacity = total_capacity_bytes();
        if (capacity < target_bytes + newest.capacity) break;  // would undershoot
        released += releaseNewestSubBuffer(evict_sub_buffer);
    }
    logRelease(released, total_capacity_bytes(), sub_pools_.size(), max_total_capacity_bytes_);
    return released;
}

uint64_t BufferPool::releaseAtLeast(
        uint64_t bytes,
        const std::function<void(int sub_idx)>& evict_sub_buffer) {
    uint64_t released = 0;
    while (released < bytes) {
        const uint64_t got = releaseNewestSubBuffer(evict_sub_buffer);
        if (got == 0) break;
        released += got;
    }
    logRelease(released, total_capacity_bytes(), sub_pools_.size(), max_total_capacity_bytes_);
    return released;
}

#if defined(__EMSCRIPTEN__)
void BufferPool::resolveProvisionalGrowth(bool failed) {
    growth_pending_ = false;
    // The provisional sub-pool is the most recently added; locate it from
    // the back (growth_pending_ guaranteed no others were appended).
    for (size_t i = sub_pools_.size(); i-- > 0; ) {
        if (!sub_pools_[i].provisional) continue;
        if (failed) {
            if (sub_pools_[i].buffer) wgpuBufferRelease(sub_pools_[i].buffer);
            sub_pools_.erase(sub_pools_.begin() + i);
            growth_disabled_ = true;
            std::fprintf(stderr,
                "[wgpu pool] sub-buffer grow OOM'd; pool capped at %llu MB "
                "across %zu sub-buffer(s) — growth disabled\n",
                (unsigned long long)(total_capacity_bytes() / (1024 * 1024)),
                sub_pools_.size());
        } else {
            SubPool& sub_pool = sub_pools_[i];
            sub_pool.provisional = false;
            std::fprintf(stderr,
                "[wgpu pool] added sub-buffer %zu (%llu MB); pool total now %llu MB\n",
                i,
                (unsigned long long)(sub_pool.capacity / (1024 * 1024)),
                (unsigned long long)(total_capacity_bytes() / (1024 * 1024)));
        }
        return;
    }
}
#endif  // __EMSCRIPTEN__

BufferPool::Slice BufferPool::alloc(uint64_t size, uint64_t align) {
    Slice out;
    if (size == 0 || align == 0) return out;

    // First-fit across all sub-buffers. When none fits, try to grow by
    // adding another sub-buffer and retry once.
    for (int attempt = 0; attempt < 2; ++attempt) {
        for (size_t sp_idx = 0; sp_idx < sub_pools_.size(); ++sp_idx) {
            SubPool& sub_pool = sub_pools_[sp_idx];
            // Web: never allocate out of a sub-buffer still awaiting OOM
            // validation — its handle may be a Dawn error buffer.
            if (sub_pool.provisional) continue;
            for (size_t i = 0; i < sub_pool.free_ranges.size(); ++i) {
                const FreeRange& free_range = sub_pool.free_ranges[i];
                const uint64_t aligned = (free_range.offset + (align - 1)) & ~(align - 1);
                const uint64_t alignment_padding = aligned - free_range.offset;
                if (alignment_padding >= free_range.size)           continue;
                if (size > free_range.size - alignment_padding)     continue;

                const uint64_t post_off  = aligned + size;
                const uint64_t post_size = (free_range.offset + free_range.size) - post_off;

                if (alignment_padding == 0 && post_size == 0) {
                    sub_pool.free_ranges.erase(sub_pool.free_ranges.begin() + i);
                } else if (alignment_padding == 0) {
                    sub_pool.free_ranges[i] = {post_off, post_size};
                } else if (post_size == 0) {
                    sub_pool.free_ranges[i] = {free_range.offset, alignment_padding};
                } else {
                    sub_pool.free_ranges[i] = {free_range.offset, alignment_padding};
                    sub_pool.free_ranges.insert(sub_pool.free_ranges.begin() + i + 1,
                                          {post_off, post_size});
                }

                sub_pool.used += size;
                out.buffer  = sub_pool.buffer;
                out.offset  = aligned;
                out.size    = size;
                out.sub_idx = int(sp_idx);
                return out;
            }
        }
        // Existing sub-buffers can't fit. Grow once before giving up.
        if (attempt == 0) {
            if (!addSubBuffer()) break;
        }
    }
    return out;
}

void BufferPool::free(const Slice& s) {
    if (!s.valid())                                       return;
    if (s.sub_idx < 0 || size_t(s.sub_idx) >= sub_pools_.size()) return;
    SubPool& sub_pool = sub_pools_[size_t(s.sub_idx)];
    assert(s.offset + s.size <= sub_pool.capacity);

    size_t i = 0;
    while (i < sub_pool.free_ranges.size() && sub_pool.free_ranges[i].offset < s.offset) ++i;
    sub_pool.free_ranges.insert(sub_pool.free_ranges.begin() + i, {s.offset, s.size});
    sub_pool.used -= s.size;

    if (i + 1 < sub_pool.free_ranges.size()
        && sub_pool.free_ranges[i].offset + sub_pool.free_ranges[i].size
            == sub_pool.free_ranges[i + 1].offset) {
        sub_pool.free_ranges[i].size += sub_pool.free_ranges[i + 1].size;
        sub_pool.free_ranges.erase(sub_pool.free_ranges.begin() + i + 1);
    }
    if (i > 0
        && sub_pool.free_ranges[i - 1].offset + sub_pool.free_ranges[i - 1].size
            == sub_pool.free_ranges[i].offset) {
        sub_pool.free_ranges[i - 1].size += sub_pool.free_ranges[i].size;
        sub_pool.free_ranges.erase(sub_pool.free_ranges.begin() + i);
    }
}

uint64_t BufferPool::total_capacity_bytes() const {
    uint64_t total_capacity = 0;
    // Skip provisional sub-pools (web, awaiting OOM validation) — their
    // capacity isn't usable yet, so counting it would mislead the
    // evictor's "is there room?" heuristics.
    for (const auto& sub_pool : sub_pools_) {
        if (!sub_pool.provisional) total_capacity += sub_pool.capacity;
    }
    return total_capacity;
}

uint64_t BufferPool::total_used_bytes() const {
    uint64_t total_used = 0;
    for (const auto& sub_pool : sub_pools_) {
        if (!sub_pool.provisional) total_used += sub_pool.used;
    }
    return total_used;
}

uint64_t BufferPool::largest_free_run_bytes() const {
    uint64_t largest_free_run = 0;
    for (const auto& sub_pool : sub_pools_) {
        if (sub_pool.provisional) continue;
        for (const auto& free_range : sub_pool.free_ranges) {
            if (free_range.size > largest_free_run) largest_free_run = free_range.size;
        }
    }
    return largest_free_run;
}

void BufferPool::addSubBufferForTesting(WGPUBuffer fake_buffer, uint64_t capacity) {
    SubPool sp;
    sp.buffer      = fake_buffer;
    sp.capacity    = capacity;
    sp.used        = 0;
    sp.owns_handle = false;
    sp.free_ranges.push_back({0, capacity});
    sub_pools_.push_back(std::move(sp));
}

void BufferPool::clearSubPoolsForTesting() {
    // Skip wgpuBufferRelease — handles are fakes that would crash on deref.
    sub_pools_.clear();
}
