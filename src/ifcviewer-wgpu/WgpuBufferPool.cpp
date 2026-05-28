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

#include "WgpuBufferPool.h"

#include <cassert>
#include <cstring>

WgpuBufferPool::~WgpuBufferPool() {
    destroy();
}

bool WgpuBufferPool::init(WGPUDevice device, uint64_t capacity_bytes,
                          WGPUBufferUsage usage, const char* label) {
    destroy();
    if (capacity_bytes == 0) return false;

    WGPUBufferDescriptor desc = {};
    desc.usage = usage;
    desc.size  = capacity_bytes;
    if (label) {
        desc.label.data   = label;
        desc.label.length = std::strlen(label);
    }
    buffer_ = wgpuDeviceCreateBuffer(device, &desc);
    if (!buffer_) return false;

    capacity_ = capacity_bytes;
    used_     = 0;
    free_ranges_.clear();
    free_ranges_.push_back({0, capacity_bytes});
    return true;
}

void WgpuBufferPool::destroy() {
    if (buffer_) {
        wgpuBufferRelease(buffer_);
        buffer_ = nullptr;
    }
    capacity_ = 0;
    used_     = 0;
    free_ranges_.clear();
}

bool WgpuBufferPool::alloc(uint64_t size, uint64_t align, uint64_t* out_offset) {
    if (size == 0 || align == 0) return false;
    // First-fit: scan free ranges, pick the first that fits with alignment.
    for (size_t i = 0; i < free_ranges_.size(); ++i) {
        const FreeRange& r = free_ranges_[i];
        const uint64_t aligned = (r.offset + (align - 1)) & ~(align - 1);
        const uint64_t pad     = aligned - r.offset;
        if (pad >= r.size)            continue;          // alignment alone won't fit
        if (size > r.size - pad)      continue;          // payload won't fit

        // Split the range. Three resulting pieces:
        //   [r.offset, aligned)              -> pre-pad, returned to free list
        //   [aligned,  aligned + size)       -> the allocation (claimed)
        //   [aligned + size, r.offset + r.size) -> post-pad, returned to free list
        const uint64_t post_off  = aligned + size;
        const uint64_t post_size = (r.offset + r.size) - post_off;

        // Mutate in place: replace the matched range with the pre-pad
        // (or erase it if there's no pre-pad), then optionally insert
        // the post-pad immediately after.
        if (pad == 0 && post_size == 0) {
            free_ranges_.erase(free_ranges_.begin() + i);
        } else if (pad == 0) {
            free_ranges_[i] = {post_off, post_size};
        } else if (post_size == 0) {
            free_ranges_[i] = {r.offset, pad};
        } else {
            free_ranges_[i] = {r.offset, pad};
            free_ranges_.insert(free_ranges_.begin() + i + 1, {post_off, post_size});
        }

        used_ += size;  // pre-/post-pad remain in free_ranges_, not used_
        *out_offset = aligned;
        return true;
    }
    return false;
}

void WgpuBufferPool::free(uint64_t offset, uint64_t size) {
    if (size == 0) return;
    assert(offset + size <= capacity_);

    // Find insertion point: first range whose offset > released offset.
    size_t i = 0;
    while (i < free_ranges_.size() && free_ranges_[i].offset < offset) ++i;
    free_ranges_.insert(free_ranges_.begin() + i, {offset, size});
    used_ -= size;

    // Coalesce with right neighbour first (so subsequent left-coalesce
    // sees the merged range).
    if (i + 1 < free_ranges_.size()
        && free_ranges_[i].offset + free_ranges_[i].size == free_ranges_[i + 1].offset) {
        free_ranges_[i].size += free_ranges_[i + 1].size;
        free_ranges_.erase(free_ranges_.begin() + i + 1);
    }
    // Coalesce with left neighbour.
    if (i > 0
        && free_ranges_[i - 1].offset + free_ranges_[i - 1].size == free_ranges_[i].offset) {
        free_ranges_[i - 1].size += free_ranges_[i].size;
        free_ranges_.erase(free_ranges_.begin() + i);
    }
}

uint64_t WgpuBufferPool::largest_free_run_bytes() const {
    uint64_t m = 0;
    for (const auto& r : free_ranges_) {
        if (r.size > m) m = r.size;
    }
    return m;
}
