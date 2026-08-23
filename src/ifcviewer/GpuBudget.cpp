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

void GpuBudget::bound(std::uint64_t budget) {
    if (hard_cap_ > 0) budget = std::min(budget, hard_cap_);
    bounded_ = true;
    budget_  = std::max(budget, kMinCacheBudgetBytes);
}

void GpuBudget::setHardCap(std::uint64_t hard_cap_bytes) {
    hard_cap_ = hard_cap_bytes;
    if (hard_cap_ > 0) bound(bounded_ ? budget_ : hard_cap_);
}

void GpuBudget::update(std::uint64_t device_free_bytes,
                       std::uint64_t cache_capacity_bytes) {
    if (device_free_bytes == 0) return;
    const std::uint64_t available = cache_capacity_bytes + device_free_bytes;
    const std::uint64_t margin    = margin_bytes();
    bound(available > margin ? available - margin : 0);
}

bool GpuBudget::onPressure(std::uint64_t cache_capacity_bytes,
                           std::uint64_t bytes_needed,
                           std::uint64_t device_free_bytes) {
    ++pressure_events_;
    // The driver refused bytes_needed while reporting device_free_bytes
    // free, so at least (free - needed) of what it reports is not really
    // available. Remember that so update() stops short of it next time.
    if (device_free_bytes > bytes_needed) {
        learned_margin_ = std::max(learned_margin_,
                                   device_free_bytes - bytes_needed + kPressureSlackBytes);
    }
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
    bound(lowered);
    return true;
}
