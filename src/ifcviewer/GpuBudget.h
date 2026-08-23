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

#ifndef IFCVIEWER_GPUBUDGET_H
#define IFCVIEWER_GPUBUDGET_H

#include <cstdint>

// How much device memory the elastic geometry cache (BufferPool) may hold.
//
// GPU memory in the viewer falls in two tiers. *Required* allocations --
// render attachments, per-model metadata, readback staging -- are allocated
// eagerly at deterministic moments (surface configure, model load) and the
// frame cannot be drawn without them. The *cache* -- streamed chunk
// geometry -- is elastic: a chunk that does not fit is simply not resident
// this frame. The rule that keeps the two from colliding is that the cache
// never takes the last byte: it grows only up to this budget, and yields
// whenever a required allocation fails.
//
// The budget is *live*, the way D3D12's QueryVideoMemoryInfo and Vulkan's
// memory_budget are meant to be used: on desktop the driver's free-memory
// report (GpuMemory.h) is polled and
//
//     budget = cache capacity + device free - margin
//
// is recomputed each time, so the cache tracks what the device can give as
// other processes come and go. The attachments are eager, so at any poll
// they are already inside "used" at the *actual* surface size; nothing is
// idled for a hypothetical bigger window -- a resize that no longer fits is
// answered by the pressure path instead.
//
// The margin has a fixed part for the required-tier allocations that come
// later (the next model's metadata, staging) and a *learned* part: drivers
// refuse allocations while still reporting memory free (measured here: a
// refusal with 221 MB "free"), and a budget that trusts the report would
// grow straight back into the same refusal after every shrink. A pressure
// event therefore records how much reported-free memory turned out to be
// unusable, and the margin keeps that from then on.
//
// Web has no memory query, so it keeps a fixed ceiling (the wasm heap) and
// pressure feedback alone. The budget's source differs per platform, the
// mechanism does not.
//
// Pure policy, no wgpu: the pool applies the number via
// BufferPool::setMaxTotalCapacity / shrinkToCapacity.
class GpuBudget {
public:
    // Below this the viewer cannot keep even a handful of 4 MB chunks
    // resident, so there is no point lowering further: a required
    // allocation that still fails at the floor is a genuinely exhausted
    // device, and the caller degrades instead.
    static constexpr std::uint64_t kMinCacheBudgetBytes = 64ull * 1024 * 1024;
    // Held back for required allocations made after the cache has grown
    // (a later model's metadata buffers, readback staging, driver
    // bookkeeping).
    static constexpr std::uint64_t kFixedMarginBytes    = 256ull * 1024 * 1024;
    // Headroom added on top of a failed allocation when lowering the
    // budget, so the very next small required allocation does not fail
    // again and trigger another shrink cycle.
    static constexpr std::uint64_t kPressureSlackBytes  = 32ull * 1024 * 1024;

    // Absolute ceiling regardless of device memory (the wasm heap on web).
    // 0 = none.
    void setHardCap(std::uint64_t hard_cap_bytes);

    // Desktop: a fresh driver report. `device_free_bytes` 0 = the query
    // could not answer -- ignored, the budget keeps its last value.
    void update(std::uint64_t device_free_bytes,
                std::uint64_t cache_capacity_bytes);

    // A required allocation of `bytes_needed` failed while the cache held
    // `cache_capacity_bytes` and the driver reported `device_free_bytes`
    // free (0 = unknown). Lowers the budget so that shrinking the cache to
    // it frees bytes_needed + slack, and learns the unusable headroom for
    // future update() calls. Returns false when the budget could not be
    // lowered any further (already at the floor): the device is exhausted
    // and the caller must degrade rather than retry.
    bool onPressure(std::uint64_t cache_capacity_bytes,
                    std::uint64_t bytes_needed,
                    std::uint64_t device_free_bytes);

    // False until something bounds the cache (a device report, a cap, or
    // a pressure event). The pool then grows until the driver refuses,
    // exactly as before; the first of those bounds it.
    bool          bounded()            const { return bounded_; }
    // Meaningful only when bounded().
    std::uint64_t cache_budget_bytes() const { return budget_; }
    // Fixed + learned margin applied by update().
    std::uint64_t margin_bytes()       const { return kFixedMarginBytes + learned_margin_; }
    std::uint32_t pressure_events()    const { return pressure_events_; }

private:
    void bound(std::uint64_t budget);

    bool          bounded_         = false;
    std::uint64_t budget_          = 0;
    std::uint64_t hard_cap_        = 0;
    // Reported-free memory that a refusal proved unusable, plus slack.
    std::uint64_t learned_margin_  = 0;
    std::uint32_t pressure_events_ = 0;
};

#endif  // IFCVIEWER_GPUBUDGET_H
