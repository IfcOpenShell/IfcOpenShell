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

// Tier-1 coverage of BufferPool's sub-allocator. The pool's free-list +
// coalescing logic is pure CPU bookkeeping; wgpu calls only happen inside
// addSubBuffer() during growth. We pre-seed sub-pools via the test-only
// addSubBufferForTesting() seam so the tests don't need a real device,
// then exercise alloc / free / alignment / coalescing / multi-sub-pool
// behaviour against the public API.
//
// The fake handles below are never dereferenced — BufferPool treats
// WGPUBuffer as an opaque token it just hands back inside Slice. Using
// `reinterpret_cast<WGPUBuffer>(0x100)` etc. gives us stable identities
// for cross-pool sub_idx assertions.

#include "BufferPool.h"

#include <catch2/catch_all.hpp>

#include <cstdint>
#include <vector>

namespace {

WGPUBuffer fake_handle(uintptr_t id) {
    // Any non-null pointer works; the value is only used for == comparisons
    // and never dereferenced. Adding an offset by id keeps multiple fakes
    // visibly distinct in failure messages.
    return reinterpret_cast<WGPUBuffer>(static_cast<uintptr_t>(0x1000) + id);
}

// RAII guard so the pool's destructor doesn't try to wgpuBufferRelease()
// our fake handles. Drops the sub-pools via the test seam first.
struct FakePoolGuard {
    BufferPool& p;
    ~FakePoolGuard() { p.clearSubPoolsForTesting(); }
};

} // namespace

TEST_CASE("empty pool reports zero capacity and refuses allocs", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};

    REQUIRE(pool.sub_buffer_count() == 0);
    REQUIRE(pool.total_capacity_bytes() == 0);
    REQUIRE(pool.total_used_bytes() == 0);
    REQUIRE(pool.total_free_bytes() == 0);
    REQUIRE(pool.largest_free_run_bytes() == 0);

    // No sub-pool exists yet; without a configured device addSubBuffer
    // can't grow, so alloc returns an invalid Slice rather than UB.
    auto s = pool.alloc(64, 16);
    REQUIRE_FALSE(s.valid());
    REQUIRE(s.size == 0);
}

TEST_CASE("single alloc returns a valid aligned slice", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 1024);

    REQUIRE(pool.sub_buffer_count() == 1);
    REQUIRE(pool.total_capacity_bytes() == 1024);
    REQUIRE(pool.total_used_bytes() == 0);
    REQUIRE(pool.largest_free_run_bytes() == 1024);

    auto s = pool.alloc(/*size=*/100, /*align=*/256);
    REQUIRE(s.valid());
    REQUIRE(s.buffer == fake_handle(1));
    REQUIRE(s.size == 100);
    REQUIRE((s.offset % 256) == 0);
    REQUIRE(s.sub_idx == 0);

    // `used` tracks alloc sizes (excludes pad). Free space drops by both.
    REQUIRE(pool.total_used_bytes() == 100);
    REQUIRE(pool.total_free_bytes() == 1024 - 100);
}

TEST_CASE("alloc-then-free round-trip returns the slot to the pool", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 1024);

    auto s = pool.alloc(256, 1);
    REQUIRE(s.valid());
    REQUIRE(pool.total_used_bytes() == 256);

    pool.free(s);
    REQUIRE(pool.total_used_bytes() == 0);
    REQUIRE(pool.largest_free_run_bytes() == 1024);

    // After the free-with-coalesce the pool is byte-identical to its
    // initial state, so an alloc of the original size can reuse the
    // same offset.
    auto s2 = pool.alloc(256, 1);
    REQUIRE(s2.valid());
    REQUIRE(s2.offset == s.offset);
}

TEST_CASE("alignment padding is reclaimable by smaller allocs", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 1024);

    // First alloc requests 256-byte alignment; offset 0 already satisfies
    // it, so no pad. Second alloc of size 100 follows at offset 256.
    auto a = pool.alloc(100, 256);
    auto b = pool.alloc(100, 256);
    REQUIRE(a.offset == 0);
    REQUIRE(b.offset == 256);
    REQUIRE(b.offset >= a.offset + a.size);

    // Used = sum of allocation sizes only. The 156 bytes of pad inside the
    // first 256-byte slot remain in free_ranges and are reclaimable by an
    // alloc small enough to fit them.
    REQUIRE(pool.total_used_bytes() == 200);
    auto c = pool.alloc(50, 1);
    REQUIRE(c.valid());
    REQUIRE(c.offset >= 100);   // lands in the leading pad of slot 0
    REQUIRE(c.offset < 256);
}

TEST_CASE("free coalesces adjacent ranges in the same sub-pool", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 1024);

    auto a = pool.alloc(256, 1);
    auto b = pool.alloc(256, 1);
    auto c = pool.alloc(256, 1);
    REQUIRE(a.offset + a.size == b.offset);
    REQUIRE(b.offset + b.size == c.offset);

    // Free in non-adjacent order: a, then c, leaves a hole around b.
    pool.free(a);
    pool.free(c);
    // largest_free_run can be a (256), b (still alloc'd, no), c+tail
    // (256 + remaining = at least 256). It's not 768 because b is in
    // the middle.
    REQUIRE(pool.largest_free_run_bytes() < 768);

    pool.free(b);
    // Now all three runs collapse into one contiguous free block, plus
    // the tail. largest_free_run is the entire sub-pool again.
    REQUIRE(pool.largest_free_run_bytes() == 1024);
    REQUIRE(pool.total_used_bytes() == 0);
}

TEST_CASE("alloc fails gracefully when no sub-pool can fit", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 512);

    auto big = pool.alloc(512, 1);
    REQUIRE(big.valid());
    REQUIRE(pool.total_used_bytes() == 512);

    // Pool is now full and can_grow() is false (we never configure'd
    // a device, so per_sub_buffer_capacity_ is 0). alloc returns
    // an invalid Slice rather than asserting or growing into garbage.
    REQUIRE_FALSE(pool.can_grow());
    auto fail = pool.alloc(1, 1);
    REQUIRE_FALSE(fail.valid());
}

TEST_CASE("multi sub-pool alloc spans pools and reports correct sub_idx", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 256);
    pool.addSubBufferForTesting(fake_handle(2), 256);

    REQUIRE(pool.sub_buffer_count() == 2);
    REQUIRE(pool.total_capacity_bytes() == 512);

    // First alloc fits in sub-pool 0.
    auto a = pool.alloc(256, 1);
    REQUIRE(a.valid());
    REQUIRE(a.buffer == fake_handle(1));
    REQUIRE(a.sub_idx == 0);

    // Second alloc can't fit in sub-pool 0 (full); first-fit moves to
    // sub-pool 1.
    auto b = pool.alloc(256, 1);
    REQUIRE(b.valid());
    REQUIRE(b.buffer == fake_handle(2));
    REQUIRE(b.sub_idx == 1);

    REQUIRE(pool.total_used_bytes() == 512);
    REQUIRE(pool.total_free_bytes() == 0);
}

TEST_CASE("free routes by sub_idx — no cross-pool coalescing", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 256);
    pool.addSubBufferForTesting(fake_handle(2), 256);

    auto a = pool.alloc(256, 1);   // sub 0
    auto b = pool.alloc(256, 1);   // sub 1
    REQUIRE(a.sub_idx == 0);
    REQUIRE(b.sub_idx == 1);

    pool.free(a);
    pool.free(b);

    // Both sub-pools are individually empty, but they are distinct
    // buffers — largest_free_run is per-sub-buffer, not summed across.
    REQUIRE(pool.total_used_bytes() == 0);
    REQUIRE(pool.largest_free_run_bytes() == 256);
}

TEST_CASE("free with invalid slice is a no-op", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 512);

    auto a = pool.alloc(128, 1);
    REQUIRE(a.valid());
    const uint64_t used_before = pool.total_used_bytes();

    // Default-constructed Slice has size=0 + null buffer + sub_idx=-1.
    // free() should silently ignore it (this is the path real callers
    // hit when an alloc failed earlier and they unconditionally free).
    BufferPool::Slice junk;
    REQUIRE_FALSE(junk.valid());
    pool.free(junk);
    REQUIRE(pool.total_used_bytes() == used_before);

    // Sub-index out of range is also ignored.
    BufferPool::Slice bad_idx = a;
    bad_idx.sub_idx = 99;
    pool.free(bad_idx);
    REQUIRE(pool.total_used_bytes() == used_before);

    // Real free still works after these no-ops.
    pool.free(a);
    REQUIRE(pool.total_used_bytes() == 0);
}

// ---- Budget ceiling + shrink (the cache yielding to the required tier) ----

TEST_CASE("can_grow respects the total-capacity budget with sub-buffer granularity", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    // No device configured, so can_grow is false regardless; the budget
    // arithmetic is what we check via max_total_capacity_bytes.
    pool.setMaxTotalCapacity(256ull * 1024 * 1024);
    REQUIRE(pool.max_total_capacity_bytes() == 256ull * 1024 * 1024);
    pool.addSubBufferForTesting(fake_handle(1), 200ull * 1024 * 1024);
    // 200 MB held + 64 MB floor > 256 MB budget: a grow could not fit.
    REQUIRE_FALSE(pool.can_grow());
}

TEST_CASE("shrinkToCapacity releases sub-buffers newest-first after the owner empties them", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 1024);
    pool.addSubBufferForTesting(fake_handle(2), 1024);
    pool.addSubBufferForTesting(fake_handle(3), 1024);

    auto a = pool.alloc(256, 16);   // sub 0
    auto b = pool.alloc(1024, 16);  // sub 1 (sub 0 has only 768 left)
    auto c = pool.alloc(512, 16);   // sub 0 again (first fit)
    auto d = pool.alloc(512, 16);   // sub 2
    REQUIRE(a.sub_idx == 0);
    REQUIRE(b.sub_idx == 1);
    REQUIRE(c.sub_idx == 0);
    REQUIRE(d.sub_idx == 2);

    std::vector<int> evicted;
    auto evict = [&](int sub_idx) {
        evicted.push_back(sub_idx);
        if (sub_idx == 2) pool.free(d);
        if (sub_idx == 1) pool.free(b);
        if (sub_idx == 0) { pool.free(a); pool.free(c); }
    };

    // Shrink to 1024: drops sub 2 then sub 1; sub 0 and its slices survive
    // with their sub_idx still valid.
    const uint64_t released = pool.shrinkToCapacity(1024, evict);
    REQUIRE(released == 2048);
    REQUIRE(evicted == std::vector<int>{2, 1});
    REQUIRE(pool.sub_buffer_count() == 1);
    REQUIRE(pool.total_capacity_bytes() == 1024);
    REQUIRE(pool.total_used_bytes() == 256 + 512);
    REQUIRE(pool.largest_free_run_bytes() == 256);

    // Already at or below target: nothing happens, evictor not consulted.
    evicted.clear();
    REQUIRE(pool.shrinkToCapacity(1024, evict) == 0);
    REQUIRE(evicted.empty());

    // Shrinking to zero empties the pool entirely.
    REQUIRE(pool.shrinkToCapacity(0, evict) == 1024);
    REQUIRE(pool.sub_buffer_count() == 0);
    REQUIRE(evicted == std::vector<int>{0});
}

TEST_CASE("shrinkToCapacity never undershoots the target", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 256);
    pool.addSubBufferForTesting(fake_handle(2), 256);
    pool.addSubBufferForTesting(fake_handle(3), 73);
    pool.addSubBufferForTesting(fake_handle(4), 73);
    auto evict = [](int) {};

    // 658 held, target 476: 182 over. The two 73s go (36 still over);
    // the 256 would undershoot, so it stays — the margin absorbs 36.
    REQUIRE(pool.shrinkToCapacity(476, evict) == 146);
    REQUIRE(pool.total_capacity_bytes() == 512);
    // An excess smaller than the newest sub-buffer releases nothing.
    REQUIRE(pool.shrinkToCapacity(500, evict) == 0);
    REQUIRE(pool.total_capacity_bytes() == 512);
}

TEST_CASE("releaseAtLeast frees whole sub-buffers until the requested bytes are gone", "[buffer_pool]") {
    BufferPool pool;
    FakePoolGuard guard{pool};
    pool.addSubBufferForTesting(fake_handle(1), 256);
    pool.addSubBufferForTesting(fake_handle(2), 73);
    pool.addSubBufferForTesting(fake_handle(3), 73);
    std::vector<int> evicted;
    auto evict = [&](int sub_idx) { evicted.push_back(sub_idx); };

    // Needs 100: 73 is not enough, 73+73 is. Overshoot by a sub-buffer is
    // the point — the allocation must fit.
    REQUIRE(pool.releaseAtLeast(100, evict) == 146);
    REQUIRE(evicted == std::vector<int>{2, 1});
    REQUIRE(pool.total_capacity_bytes() == 256);
    // More than the pool holds: everything goes, no crash.
    REQUIRE(pool.releaseAtLeast(1000, evict) == 256);
    REQUIRE(pool.sub_buffer_count() == 0);
    REQUIRE(pool.releaseAtLeast(1, evict) == 0);
}
