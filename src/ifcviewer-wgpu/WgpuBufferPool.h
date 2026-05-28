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

#ifndef WGPUBUFFERPOOL_H
#define WGPUBUFFERPOOL_H

#include <webgpu/webgpu.h>

#include <cstdint>
#include <vector>

// Single-buffer sub-allocator. Owns one WGPUBuffer of fixed capacity and
// hands out byte ranges within it. Replaces the per-chunk
// wgpuDeviceCreateBuffer/Release pattern, which on wgpu-native triggers
// gpu-alloc-rs fragmentation (one VkDeviceMemory per buffer with
// rounding overhead) and OOMs the device well below physical VRAM.
//
// Lifetime model: alloc/free are immediate. WebGPU guarantees that
// queue.writeBuffer to a just-freed range is correctly serialised against
// any prior submitted GPU reads — we never need to fence frees ourselves.
//
// Allocator: sorted free list with adjacent-range coalescing, first-fit.
// Adequate for the chunk workload (a few hundred allocations of broadly
// similar size); revisit if a workload demonstrates worst-case behaviour.
class WgpuBufferPool {
public:
    WgpuBufferPool() = default;
    ~WgpuBufferPool();

    WgpuBufferPool(const WgpuBufferPool&)            = delete;
    WgpuBufferPool& operator=(const WgpuBufferPool&) = delete;

    // Allocate the underlying buffer at the given capacity. `usage` must
    // include CopyDst (alloc'd ranges are populated via queueWriteBuffer).
    // Returns false if creation failed (caller can retry at smaller size).
    bool init(WGPUDevice device, uint64_t capacity_bytes,
              WGPUBufferUsage usage, const char* label);
    void destroy();

    // Sub-allocate a range of `size` bytes, aligned to `align` (must be
    // a power of two; typical: 256 for storage-buffer binding offsets).
    // On success returns true and writes the byte offset to *out_offset.
    // On failure (no free range fits) returns false; *out_offset is
    // unchanged.
    bool alloc(uint64_t size, uint64_t align, uint64_t* out_offset);
    // Free a previously-allocated range. (offset, size) must exactly
    // match a prior alloc(); freeing a partial range is unsupported.
    void free(uint64_t offset, uint64_t size);

    WGPUBuffer buffer()         const { return buffer_; }
    uint64_t   capacity_bytes() const { return capacity_; }
    uint64_t   used_bytes()     const { return used_; }
    uint64_t   free_bytes()     const { return capacity_ - used_; }
    // Largest contiguous free run. Useful for evictor heuristics ("can
    // this allocation even fit, ever, without eviction?").
    uint64_t   largest_free_run_bytes() const;

private:
    struct FreeRange { uint64_t offset; uint64_t size; };

    // Sorted by offset, non-overlapping, non-adjacent (coalesced on
    // every free). Empty when the pool is fully allocated.
    std::vector<FreeRange> free_ranges_;

    WGPUBuffer buffer_   = nullptr;
    uint64_t   capacity_ = 0;
    uint64_t   used_     = 0;
};

#endif  // WGPUBUFFERPOOL_H
