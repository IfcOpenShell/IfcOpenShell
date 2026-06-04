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
#include <string>
#include <vector>

// Multi-sub-buffer sub-allocator. Owns one or more fixed-size WGPUBuffers
// and hands out byte ranges within them.
//
// Why multiple sub-buffers: WebGPU caps any single buffer at
// `limits.maxBufferSize`, which on wgpu-native + Vulkan tops out
// around 2 GB regardless of how much GPU memory exists. The GL backend
// reaches 4+ GB by letting the driver sub-allocate across many
// VkDeviceMemory blocks behind one logical GL buffer; here we do the
// same explicitly — `per_sub_buffer_capacity` (set from a probe) is the
// largest single buffer that allocates cleanly, and the pool grows
// lazily by adding more sub-buffers of that size when alloc demand
// exceeds what existing sub-buffers can fit.
//
// Lifetime model: alloc/free are immediate. WebGPU guarantees that
// queue.writeBuffer to a just-freed range is correctly serialised against
// any prior submitted GPU reads — we never need to fence frees ourselves.
//
// Allocator: per-sub-buffer sorted free list with adjacent-range
// coalescing, first-fit across sub-buffers. Adequate for the chunk
// workload (a few hundred allocations of broadly similar size).
class BufferPool {
public:
    // A handle to a previously-allocated range. Includes the underlying
    // sub-buffer so callers (bind-group builders, queueWriteBuffer) can
    // address the correct buffer; includes sub_idx so free() knows which
    // sub-pool's bookkeeping to update.
    struct Slice {
        WGPUBuffer buffer = nullptr;
        uint64_t   offset = 0;
        uint64_t   size   = 0;
        int        sub_idx = -1;
        bool valid() const { return size > 0 && buffer != nullptr; }
    };

    BufferPool() = default;
    ~BufferPool();

    BufferPool(const BufferPool&)            = delete;
    BufferPool& operator=(const BufferPool&) = delete;

    // Record the device + usage + sub-buffer size. Does NOT allocate any
    // sub-buffer here — that happens lazily on first alloc(). `instance`
    // is needed so the pool can drain async PopErrorScope events when
    // probing whether a new sub-buffer can be created.
    void configure(WGPUInstance instance, WGPUDevice device,
                   WGPUBufferUsage usage,
                   uint64_t per_sub_buffer_capacity,
                   const char* label_prefix);
    void destroy();

    // Sub-allocate a range of `size` bytes, aligned to `align` (must be
    // a power of two; typical: 256 for storage-buffer binding offsets).
    // Tries every existing sub-buffer; if none can fit, attempts to add
    // a new sub-buffer at per_sub_buffer_capacity. Returns an invalid
    // Slice (size == 0) if no sub-buffer fits and growth fails.
    Slice alloc(uint64_t size, uint64_t align);
    // Return a slice to the free list. Coalesces with adjacent free
    // ranges in the same sub-buffer.
    void  free(const Slice& s);

    // Tally summed across every sub-buffer.
    uint64_t total_capacity_bytes() const;
    uint64_t total_used_bytes()     const;
    uint64_t total_free_bytes()     const { return total_capacity_bytes() - total_used_bytes(); }
    // Largest contiguous free run across all sub-buffers. Useful for
    // evictor heuristics ("can this allocation even fit, ever, without
    // eviction or growth?").
    uint64_t largest_free_run_bytes() const;
    // Per-sub-buffer count, for diagnostics / logging.
    size_t   sub_buffer_count() const { return sub_pools_.size(); }
    uint64_t per_sub_buffer_capacity_bytes() const { return per_sub_buffer_capacity_; }
    // Best estimate of the size a *future* sub-buffer would land at:
    // last_growth_size_ if we've ever grown (or just been configured),
    // else the configured per_sub_buffer_capacity. After the driver
    // refuses a size, halve-on-failure in addSubBuffer pushes this down
    // so callers' "can this chunk fit via growth?" check stays honest.
    uint64_t next_growth_size_bytes() const {
        return last_growth_size_ > 0 ? last_growth_size_ : per_sub_buffer_capacity_;
    }
    // Whether the pool can still attempt to add a sub-buffer. Flips to
    // false the first time addSubBuffer is refused even at the floor
    // size — eviction callers need this to know whether a future alloc
    // could rescue them, or whether eviction is the only path.
    bool     can_grow() const { return !growth_disabled_ && per_sub_buffer_capacity_ > 0; }

private:
    struct FreeRange { uint64_t offset; uint64_t size; };
    struct SubPool {
        WGPUBuffer             buffer = nullptr;
        uint64_t               capacity = 0;
        uint64_t               used = 0;
        std::vector<FreeRange> free_ranges;
    };

    // Append a new sub-buffer to the pool. Starts at last_growth_size_
    // (initially per_sub_buffer_capacity_) and halves on driver refusal
    // before giving up — many Vulkan drivers cap single VkDeviceMemory
    // allocations at a couple GB (e.g. NVIDIA: maxStorageBufferBindingSize
    // is exactly 2 GB on consumer GeForce cards) or refuse big contiguous
    // allocations once heap is fragmented, but happily grant smaller ones.
    // Halving turns "stop at first refused 2 GB" into "2 GB + 1 GB + …",
    // which on a 4 GB card lets us reach 3 GB total instead of 2 GB.
    // Wrapped in OOM/Validation error scopes so failed attempts don't
    // take the device down. Returns true on success at some size
    // ≥ MIN_SUB_BUFFER_BYTES; false only when even the minimum size is
    // refused, at which point growth_disabled_ latches.
    bool addSubBuffer();

    std::vector<SubPool> sub_pools_;

    WGPUInstance     instance_                 = nullptr;
    WGPUDevice       device_                   = nullptr;
    WGPUBufferUsage  usage_                    = 0;
    uint64_t         per_sub_buffer_capacity_  = 0;
    // The largest size addSubBuffer last *succeeded* at, in bytes.
    // Starts at per_sub_buffer_capacity_ (the probe's discovered max)
    // and decays as the driver refuses larger allocations. Future grow
    // attempts start from here rather than re-trying the max every
    // time — once the driver has refused 2 GB, retrying 2 GB on every
    // subsequent grow is wasted work.
    uint64_t         last_growth_size_         = 0;
    bool             growth_disabled_          = false;
    std::string      label_prefix_;
};

#endif  // WGPUBUFFERPOOL_H
