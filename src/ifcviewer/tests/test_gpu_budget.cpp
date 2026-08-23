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

// GpuBudget decides how much device memory the streamed-geometry cache may
// hold. It is pure policy: a live number derived from what the platform
// can tell us (desktop: the driver's free-memory report; web: nothing but
// a heap ceiling), lowered by pressure events when a required allocation
// fails anyway, and learning from those how much reported-free memory the
// driver will not actually grant. These pin down the arithmetic, the floor
// and the learning.

#include "GpuBudget.h"

#include <catch2/catch_all.hpp>

namespace {
constexpr std::uint64_t MB = 1024ull * 1024;
}

TEST_CASE("nothing known leaves the cache unbounded", "[gpu_budget]") {
    GpuBudget b;
    REQUIRE_FALSE(b.bounded());
    b.update(0, 512 * MB);  // query could not answer: still unbounded
    REQUIRE_FALSE(b.bounded());
}

TEST_CASE("a device report bounds the cache at held + free - margin", "[gpu_budget]") {
    GpuBudget b;
    b.update(2800 * MB, 0);
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes() == 2800 * MB - GpuBudget::kFixedMarginBytes);

    // The pool now holds 1000 MB and the driver reports 1800 MB free: the
    // cache's own bytes count as available to it.
    b.update(1800 * MB, 1000 * MB);
    REQUIRE(b.cache_budget_bytes() == 2800 * MB - GpuBudget::kFixedMarginBytes);

    // Another process took 1000 MB: the budget follows the device down.
    b.update(800 * MB, 1000 * MB);
    REQUIRE(b.cache_budget_bytes() == 1800 * MB - GpuBudget::kFixedMarginBytes);
    // ...and back up when it is released.
    b.update(1800 * MB, 1000 * MB);
    REQUIRE(b.cache_budget_bytes() == 2800 * MB - GpuBudget::kFixedMarginBytes);
}

TEST_CASE("less than the margin available floors the budget, not zero", "[gpu_budget]") {
    GpuBudget b;
    b.update(100 * MB, 0);
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes() == GpuBudget::kMinCacheBudgetBytes);
}

TEST_CASE("a hard cap bounds the cache on its own (web) and clamps a device-derived budget", "[gpu_budget]") {
    GpuBudget web;
    web.setHardCap(3072 * MB);
    REQUIRE(web.bounded());
    REQUIRE(web.cache_budget_bytes() == 3072 * MB);

    GpuBudget both;
    both.setHardCap(3072 * MB);
    both.update(8000 * MB, 0);
    REQUIRE(both.cache_budget_bytes() == 3072 * MB);

    GpuBudget small_device;
    small_device.setHardCap(3072 * MB);
    small_device.update(2800 * MB, 0);
    REQUIRE(small_device.cache_budget_bytes() == 2800 * MB - GpuBudget::kFixedMarginBytes);
}

TEST_CASE("pressure lowers the budget below what the cache currently holds", "[gpu_budget]") {
    GpuBudget b;
    REQUIRE_FALSE(b.bounded());

    // The pool grew to 2048 MB unbounded; a 120 MB attachment set then failed.
    REQUIRE(b.onPressure(2048 * MB, 120 * MB, 0));
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes()
            == 2048 * MB - 120 * MB - GpuBudget::kPressureSlackBytes);
    REQUIRE(b.pressure_events() == 1);
}

TEST_CASE("pressure is measured against actual capacity, not the previous budget", "[gpu_budget]") {
    // Budget said ~2500 MB but the driver only ever granted 1024 MB; a
    // failure must carve out of the 1024, else nothing would be released.
    GpuBudget b;
    b.update(2800 * MB, 0);
    REQUIRE(b.onPressure(1024 * MB, 100 * MB, 0));
    REQUIRE(b.cache_budget_bytes()
            == 1024 * MB - 100 * MB - GpuBudget::kPressureSlackBytes);
}

TEST_CASE("pressure never raises the budget", "[gpu_budget]") {
    GpuBudget b;
    b.setHardCap(500 * MB);
    REQUIRE(b.onPressure(256 * MB, 0, 0));
    REQUIRE(b.cache_budget_bytes() == 256 * MB - GpuBudget::kPressureSlackBytes);
    // A later event whose arithmetic lands above the current budget is a no-op.
    REQUIRE_FALSE(b.onPressure(4096 * MB, 0, 0));
    REQUIRE(b.cache_budget_bytes() == 256 * MB - GpuBudget::kPressureSlackBytes);
}

TEST_CASE("pressure bottoms out at the floor and then reports exhaustion", "[gpu_budget]") {
    GpuBudget b;
    REQUIRE(b.onPressure(100 * MB, 90 * MB, 0));
    REQUIRE(b.cache_budget_bytes() == GpuBudget::kMinCacheBudgetBytes);
    // Already at the floor: nothing more to give.
    REQUIRE_FALSE(b.onPressure(64 * MB, 90 * MB, 0));
    REQUIRE(b.pressure_events() == 2);
}

TEST_CASE("a refusal with memory still reported free teaches the margin", "[gpu_budget]") {
    GpuBudget b;
    b.update(2800 * MB, 0);
    REQUIRE(b.margin_bytes() == GpuBudget::kFixedMarginBytes);

    // 59 MB refused with 221 MB "free" (the measured crash): at least
    // 162 MB of what the driver reports is not usable.
    REQUIRE(b.onPressure(2048 * MB, 59 * MB, 221 * MB));
    REQUIRE(b.margin_bytes()
            == GpuBudget::kFixedMarginBytes + 162 * MB + GpuBudget::kPressureSlackBytes);

    // The next live report stops short by the learned amount, so the pool
    // does not grow straight back into the same refusal.
    b.update(221 * MB, 2048 * MB);
    REQUIRE(b.cache_budget_bytes() == 2048 * MB + 221 * MB - b.margin_bytes());

    // Learning only ever grows; a later refusal with less phantom free
    // memory does not shrink it.
    b.onPressure(1500 * MB, 59 * MB, 100 * MB);
    REQUIRE(b.margin_bytes()
            == GpuBudget::kFixedMarginBytes + 162 * MB + GpuBudget::kPressureSlackBytes);
    // A refusal that needed more than was reported free teaches nothing.
    b.onPressure(1500 * MB, 500 * MB, 100 * MB);
    REQUIRE(b.margin_bytes()
            == GpuBudget::kFixedMarginBytes + 162 * MB + GpuBudget::kPressureSlackBytes);
}
