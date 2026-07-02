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

#include <zstd.h>

namespace SidecarCompress {

bool decompress(const std::uint8_t* src, std::size_t src_size,
                std::uint8_t* dst, std::size_t raw_size) {
    if (raw_size == 0) return src_size == 0;  // empty in ↔ empty out
    if (!src || !dst || src_size == 0) return false;
    const size_t got = ZSTD_decompress(dst, raw_size, src, src_size);
    return !ZSTD_isError(got) && got == raw_size;
}

#if !defined(__EMSCRIPTEN__)
std::vector<std::uint8_t> compress(const std::uint8_t* src, std::size_t n,
                                   int level) {
    if (n == 0) return {};
    std::vector<std::uint8_t> out(ZSTD_compressBound(n));
    const size_t got = ZSTD_compress(out.data(), out.size(), src, n, level);
    if (ZSTD_isError(got)) return {};
    out.resize(got);
    return out;
}
#endif

}  // namespace SidecarCompress
