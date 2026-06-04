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

#include <QtDebug>

#include <cassert>
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

    while (try_size >= MIN_SUB_BUFFER_BYTES) {
        // wgpu-native classifies "Not enough memory left" as Validation,
        // not OutOfMemory. Nested scopes: OOM inner, Validation outer.
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_Validation);
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);

        char label[128];
        std::snprintf(label, sizeof(label), "%s.sub%zu",
                      label_prefix_.c_str(), sub_pools_.size());

        WGPUBufferDescriptor desc = {};
        desc.usage        = usage_;
        desc.size         = try_size;
        desc.label.data   = label;
        desc.label.length = std::strlen(label);
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

        if (buf && !oom_pop.error && !validation_pop.error) {
            SubPool sp;
            sp.buffer   = buf;
            sp.capacity = try_size;
            sp.used     = 0;
            sp.free_ranges.push_back({0, try_size});
            sub_pools_.push_back(std::move(sp));
            last_growth_size_ = try_size;
            qInfo().noquote().nospace()
                << "[wgpu pool] added sub-buffer " << (sub_pools_.size() - 1)
                << " (" << (try_size / (1024 * 1024)) << " MB); pool total now "
                << (total_capacity_bytes() / (1024 * 1024)) << " MB";
            return true;
        }
        if (buf) wgpuBufferRelease(buf);
        try_size /= 2;
    }

    qInfo().noquote().nospace()
        << "[wgpu pool] driver refused growth even at "
        << (MIN_SUB_BUFFER_BYTES / (1024 * 1024)) << " MB; pool capped at "
        << (total_capacity_bytes() / (1024 * 1024))
        << " MB across " << sub_pools_.size() << " sub-buffer(s) — growth disabled";
    growth_disabled_ = true;
    return false;
}

BufferPool::Slice BufferPool::alloc(uint64_t size, uint64_t align) {
    Slice out;
    if (size == 0 || align == 0) return out;

    // First-fit across all sub-buffers. When none fits, try to grow by
    // adding another sub-buffer and retry once.
    for (int attempt = 0; attempt < 2; ++attempt) {
        for (size_t sp_idx = 0; sp_idx < sub_pools_.size(); ++sp_idx) {
            SubPool& sp = sub_pools_[sp_idx];
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
    for (const auto& sp : sub_pools_) s += sp.capacity;
    return s;
}

uint64_t BufferPool::total_used_bytes() const {
    uint64_t s = 0;
    for (const auto& sp : sub_pools_) s += sp.used;
    return s;
}

uint64_t BufferPool::largest_free_run_bytes() const {
    uint64_t m = 0;
    for (const auto& sp : sub_pools_) {
        for (const auto& r : sp.free_ranges) {
            if (r.size > m) m = r.size;
        }
    }
    return m;
}
