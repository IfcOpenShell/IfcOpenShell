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
// hold. It is pure policy: a number derived from what the platform can
// tell us (desktop: driver free-memory report; web: nothing but a heap
// ceiling) and lowered by pressure events when a required allocation fails
// anyway. These pin down the arithmetic and the floor behaviour.

#include "GpuBudget.h"

#include <catch2/catch_all.hpp>

namespace {
constexpr std::uint64_t MB = 1024ull * 1024;
}

TEST_CASE("unknown device memory and no cap leaves the cache unbounded", "[gpu_budget]") {
    GpuBudget b;
    b.configure(0, 512 * MB, 0);
    REQUIRE_FALSE(b.bounded());
}

TEST_CASE("desktop budget is free memory minus the required-tier reserve", "[gpu_budget]") {
    GpuBudget b;
    b.configure(2800 * MB, 800 * MB, 0);
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes() == 2000 * MB);
}

TEST_CASE("a reserve larger than free memory floors the budget, not zero", "[gpu_budget]") {
    GpuBudget b;
    b.configure(300 * MB, 800 * MB, 0);
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes() == GpuBudget::kMinCacheBudgetBytes);
}

TEST_CASE("a hard cap bounds the cache on its own (web) and clamps a device-derived budget", "[gpu_budget]") {
    GpuBudget web;
    web.configure(0, 0, 3072 * MB);
    REQUIRE(web.bounded());
    REQUIRE(web.cache_budget_bytes() == 3072 * MB);

    GpuBudget both;
    both.configure(8000 * MB, 800 * MB, 3072 * MB);
    REQUIRE(both.cache_budget_bytes() == 3072 * MB);

    GpuBudget small_device;
    small_device.configure(2800 * MB, 800 * MB, 3072 * MB);
    REQUIRE(small_device.cache_budget_bytes() == 2000 * MB);
}

TEST_CASE("pressure lowers the budget below what the cache currently holds", "[gpu_budget]") {
    GpuBudget b;
    b.configure(0, 0, 0);
    REQUIRE_FALSE(b.bounded());

    // The pool grew to 2048 MB unbounded; a 120 MB attachment set then failed.
    REQUIRE(b.onPressure(2048 * MB, 120 * MB));
    REQUIRE(b.bounded());
    REQUIRE(b.cache_budget_bytes()
            == 2048 * MB - 120 * MB - GpuBudget::kPressureSlackBytes);
    REQUIRE(b.pressure_events() == 1);
}

TEST_CASE("pressure is measured against actual capacity, not the previous budget", "[gpu_budget]") {
    // Budget said 2000 MB but the driver only ever granted 1024 MB; a
    // failure must carve out of the 1024, else nothing would be released.
    GpuBudget b;
    b.configure(2800 * MB, 800 * MB, 0);
    REQUIRE(b.onPressure(1024 * MB, 100 * MB));
    REQUIRE(b.cache_budget_bytes()
            == 1024 * MB - 100 * MB - GpuBudget::kPressureSlackBytes);
}

TEST_CASE("pressure never raises the budget", "[gpu_budget]") {
    GpuBudget b;
    b.configure(0, 0, 500 * MB);
    // Pool is at 256 MB (below budget) and a tiny allocation fails:
    // capacity - carve is 224 MB-ish, which IS lower, so it lowers.
    REQUIRE(b.onPressure(256 * MB, 0));
    REQUIRE(b.cache_budget_bytes() == 256 * MB - GpuBudget::kPressureSlackBytes);
    // A later event whose arithmetic lands above the current budget is a no-op.
    REQUIRE_FALSE(b.onPressure(4096 * MB, 0));
    REQUIRE(b.cache_budget_bytes() == 256 * MB - GpuBudget::kPressureSlackBytes);
}

TEST_CASE("pressure bottoms out at the floor and then reports exhaustion", "[gpu_budget]") {
    GpuBudget b;
    b.configure(0, 0, 0);
    REQUIRE(b.onPressure(100 * MB, 90 * MB));
    REQUIRE(b.cache_budget_bytes() == GpuBudget::kMinCacheBudgetBytes);
    // Already at the floor: nothing more to give.
    REQUIRE_FALSE(b.onPressure(64 * MB, 90 * MB));
    REQUIRE(b.pressure_events() == 2);
}
