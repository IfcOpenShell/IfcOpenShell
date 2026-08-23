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

#include "GpuBudget.h"

#include <algorithm>

void GpuBudget::configure(std::uint64_t device_free_bytes,
                          std::uint64_t reserve_bytes,
                          std::uint64_t hard_cap_bytes) {
    bounded_ = false;
    budget_  = 0;
    if (device_free_bytes > 0) {
        bounded_ = true;
        budget_  = device_free_bytes > reserve_bytes
                 ? device_free_bytes - reserve_bytes
                 : 0;
    }
    if (hard_cap_bytes > 0) {
        budget_  = bounded_ ? std::min(budget_, hard_cap_bytes) : hard_cap_bytes;
        bounded_ = true;
    }
    if (bounded_) budget_ = std::max(budget_, kMinCacheBudgetBytes);
}

bool GpuBudget::onPressure(std::uint64_t cache_capacity_bytes,
                           std::uint64_t bytes_needed) {
    ++pressure_events_;
    // What the cache may keep once the failed allocation and its slack
    // have been carved out of what it holds right now. The pool's actual
    // capacity, not the previous budget, is the honest baseline: the
    // budget may never have been reached (unbounded, or growth refused
    // earlier by the driver), and lowering a number the pool never hit
    // would free nothing.
    const std::uint64_t carve  = bytes_needed + kPressureSlackBytes;
    const std::uint64_t target = cache_capacity_bytes > carve
                               ? cache_capacity_bytes - carve
                               : 0;
    const std::uint64_t lowered = std::max(target, kMinCacheBudgetBytes);
    if (bounded_ && lowered >= budget_) return false;
    bounded_ = true;
    budget_  = lowered;
    return true;
}
