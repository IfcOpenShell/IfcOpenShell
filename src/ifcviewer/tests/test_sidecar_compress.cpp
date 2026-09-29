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

#include "SidecarCompress.h"

#include <catch2/catch_test_macros.hpp>

#include <cstdint>
#include <vector>

TEST_CASE("zstd round-trips arbitrary bytes", "[compress]") {
    // Structured data like the sidecar carries (repeated matrices, patterned
    // indices) — should both round-trip AND actually shrink.
    std::vector<std::uint8_t> raw;
    for (int i = 0; i < 20000; ++i) {
        raw.push_back(std::uint8_t(i & 0xFF));
        raw.push_back(std::uint8_t((i >> 8) & 0x07));  // low-entropy high byte
        raw.push_back(0);
        raw.push_back(0xAA);
    }

    auto packed = SidecarCompress::compress(raw.data(), raw.size(), 19);
    REQUIRE_FALSE(packed.empty());
    REQUIRE(packed.size() < raw.size());  // it compressed

    std::vector<std::uint8_t> out(raw.size());
    REQUIRE(SidecarCompress::decompress(packed.data(), packed.size(),
                                        out.data(), out.size()));
    REQUIRE(out == raw);
}

TEST_CASE("decompress rejects a wrong raw size / garbage", "[compress]") {
    std::vector<std::uint8_t> raw(1024, 0x42);
    auto packed = SidecarCompress::compress(raw.data(), raw.size(), 3);
    REQUIRE_FALSE(packed.empty());

    // Wrong declared raw size must fail, not silently truncate.
    std::vector<std::uint8_t> too_small(512);
    REQUIRE_FALSE(SidecarCompress::decompress(packed.data(), packed.size(),
                                              too_small.data(), too_small.size()));

    // Garbage input fails cleanly.
    std::vector<std::uint8_t> junk = { 1, 2, 3, 4, 5, 6, 7, 8 };
    std::vector<std::uint8_t> dst(1024);
    REQUIRE_FALSE(SidecarCompress::decompress(junk.data(), junk.size(),
                                              dst.data(), dst.size()));
}

TEST_CASE("empty round-trips to empty", "[compress]") {
    std::vector<std::uint8_t> dst;
    REQUIRE(SidecarCompress::decompress(nullptr, 0, dst.data(), 0));
}
