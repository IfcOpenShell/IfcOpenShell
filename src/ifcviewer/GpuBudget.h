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
// The budget's *source* differs per platform, the mechanism does not:
//   - desktop: derived from the driver's free-memory report minus a reserve
//     for the attachments (GpuMemory.h);
//   - web: no memory query exists, so a fixed ceiling (the wasm heap) and
//     pressure feedback alone;
//   - either: when a required allocation still fails, onPressure() lowers
//     the budget so the pool releases enough for that allocation to succeed
//     on retry. Over a session the budget converges on what the device
//     actually allows, which is the only information WebGPU ever gives.
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
    // Headroom added on top of the failed allocation when lowering the
    // budget, so the very next small required allocation does not fail
    // again and trigger another shrink cycle.
    static constexpr std::uint64_t kPressureSlackBytes   = 32ull * 1024 * 1024;

    // `device_free_bytes` 0 = unknown (web, or an unsupported driver).
    // `reserve_bytes` is what the required tier is expected to need at its
    // largest (attachments at the biggest plausible surface, plus margin).
    // `hard_cap_bytes` 0 = none; otherwise an absolute ceiling regardless
    // of device memory (the wasm heap on web).
    void configure(std::uint64_t device_free_bytes,
                   std::uint64_t reserve_bytes,
                   std::uint64_t hard_cap_bytes);

    // False when nothing bounds the cache yet (no device information, no
    // cap, no pressure so far). The pool then grows until the driver
    // refuses, exactly as before; the first pressure event bounds it.
    bool          bounded()            const { return bounded_; }
    // Meaningful only when bounded().
    std::uint64_t cache_budget_bytes() const { return budget_; }

    // A required allocation of `bytes_needed` failed while the cache held
    // `cache_capacity_bytes`. Lowers the budget so that shrinking the cache
    // to it frees bytes_needed + slack. Returns false when the budget could
    // not be lowered any further (already at the floor): the device is
    // exhausted and the caller must degrade rather than retry.
    bool onPressure(std::uint64_t cache_capacity_bytes,
                    std::uint64_t bytes_needed);

    std::uint32_t pressure_events() const { return pressure_events_; }

private:
    bool          bounded_         = false;
    std::uint64_t budget_          = 0;
    std::uint32_t pressure_events_ = 0;
};

#endif  // IFCVIEWER_GPUBUDGET_H
