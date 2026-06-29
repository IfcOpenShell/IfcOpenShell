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
    for (auto& sp : sub_pools_) {
        if (sp.buffer) wgpuBufferRelease(sp.buffer);
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

    // 64 MB floor: smaller sub-buffers aren't worth the per-allocation
    // bookkeeping cost (one bind group per chunk, free-list overhead).
    // If the driver won't grant even 64 MB the pool is genuinely at
    // its ceiling; growth_disabled_ latches and future grow attempts
    // skip the doomed retry.
    constexpr uint64_t MIN_SUB_BUFFER_BYTES = 64ull * 1024 * 1024;
    uint64_t try_size = last_growth_size_ > 0
                      ? last_growth_size_
                      : per_sub_buffer_capacity_;
    if (try_size < MIN_SUB_BUFFER_BYTES) try_size = MIN_SUB_BUFFER_BYTES;

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

    wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);
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

    WGPUPopErrorScopeCallbackInfo pcb = {};
    pcb.mode = WGPUCallbackMode_AllowSpontaneous;
    pcb.callback = [](WGPUPopErrorScopeStatus, WGPUErrorType type,
                      WGPUStringView, void* ud1, void* /*ud2*/) {
        static_cast<BufferPool*>(ud1)->resolveProvisionalGrowth(
            type != WGPUErrorType_NoError);
    };
    pcb.userdata1 = this;
    wgpuDevicePopErrorScope(device_, pcb);

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

        // wgpu-native classifies "Not enough memory left" as Validation,
        // not OutOfMemory. Nested scopes: OOM inner, Validation outer.
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_Validation);
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);

        WGPUBuffer buf = wgpuDeviceCreateBuffer(device_, &desc);

        struct PopResult { bool done = false; bool error = false; };
        auto pop = [&](PopResult& pr) {
            WGPUPopErrorScopeCallbackInfo pcb = {};
            pcb.mode = WGPUCallbackMode_AllowProcessEvents;
            pcb.callback = [](WGPUPopErrorScopeStatus, WGPUErrorType type,
                              WGPUStringView, void* ud1, void* /*ud2*/) {
                auto* p = static_cast<PopResult*>(ud1);
                p->done  = true;
                p->error = (type != WGPUErrorType_NoError);
            };
            pcb.userdata1 = &pr;
            wgpuDevicePopErrorScope(device_, pcb);
            while (!pr.done) wgpuInstanceProcessEvents(instance_);
        };
        PopResult oom_pop, validation_pop;
        pop(oom_pop);
        pop(validation_pop);
        const bool ok = buf && !oom_pop.error && !validation_pop.error;

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
            sub_pools_[i].provisional = false;
            std::fprintf(stderr,
                "[wgpu pool] added sub-buffer %zu (%llu MB); pool total now %llu MB\n",
                i,
                (unsigned long long)(sub_pools_[i].capacity / (1024 * 1024)),
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
            SubPool& sp = sub_pools_[sp_idx];
            // Web: never allocate out of a sub-buffer still awaiting OOM
            // validation — its handle may be a Dawn error buffer.
            if (sp.provisional) continue;
            for (size_t i = 0; i < sp.free_ranges.size(); ++i) {
                const FreeRange& r = sp.free_ranges[i];
                const uint64_t aligned = (r.offset + (align - 1)) & ~(align - 1);
                const uint64_t pad     = aligned - r.offset;
                if (pad >= r.size)           continue;
                if (size > r.size - pad)     continue;

                const uint64_t post_off  = aligned + size;
                const uint64_t post_size = (r.offset + r.size) - post_off;

                if (pad == 0 && post_size == 0) {
                    sp.free_ranges.erase(sp.free_ranges.begin() + i);
                } else if (pad == 0) {
                    sp.free_ranges[i] = {post_off, post_size};
                } else if (post_size == 0) {
                    sp.free_ranges[i] = {r.offset, pad};
                } else {
                    sp.free_ranges[i] = {r.offset, pad};
                    sp.free_ranges.insert(sp.free_ranges.begin() + i + 1,
                                          {post_off, post_size});
                }

                sp.used += size;
                out.buffer  = sp.buffer;
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
    SubPool& sp = sub_pools_[size_t(s.sub_idx)];
    assert(s.offset + s.size <= sp.capacity);

    size_t i = 0;
    while (i < sp.free_ranges.size() && sp.free_ranges[i].offset < s.offset) ++i;
    sp.free_ranges.insert(sp.free_ranges.begin() + i, {s.offset, s.size});
    sp.used -= s.size;

    if (i + 1 < sp.free_ranges.size()
        && sp.free_ranges[i].offset + sp.free_ranges[i].size == sp.free_ranges[i + 1].offset) {
        sp.free_ranges[i].size += sp.free_ranges[i + 1].size;
        sp.free_ranges.erase(sp.free_ranges.begin() + i + 1);
    }
    if (i > 0
        && sp.free_ranges[i - 1].offset + sp.free_ranges[i - 1].size == sp.free_ranges[i].offset) {
        sp.free_ranges[i - 1].size += sp.free_ranges[i].size;
        sp.free_ranges.erase(sp.free_ranges.begin() + i);
    }
}

uint64_t BufferPool::total_capacity_bytes() const {
    uint64_t s = 0;
    // Skip provisional sub-pools (web, awaiting OOM validation) — their
    // capacity isn't usable yet, so counting it would mislead the
    // evictor's "is there room?" heuristics.
    for (const auto& sp : sub_pools_) if (!sp.provisional) s += sp.capacity;
    return s;
}

uint64_t BufferPool::total_used_bytes() const {
    uint64_t s = 0;
    for (const auto& sp : sub_pools_) if (!sp.provisional) s += sp.used;
    return s;
}

uint64_t BufferPool::largest_free_run_bytes() const {
    uint64_t m = 0;
    for (const auto& sp : sub_pools_) {
        if (sp.provisional) continue;
        for (const auto& r : sp.free_ranges) {
            if (r.size > m) m = r.size;
        }
    }
    return m;
}

void BufferPool::addSubBufferForTesting(WGPUBuffer fake_buffer, uint64_t capacity) {
    SubPool sp;
    sp.buffer   = fake_buffer;
    sp.capacity = capacity;
    sp.used     = 0;
    sp.free_ranges.push_back({0, capacity});
    sub_pools_.push_back(std::move(sp));
}

void BufferPool::clearSubPoolsForTesting() {
    // Skip wgpuBufferRelease — handles are fakes that would crash on deref.
    sub_pools_.clear();
}
