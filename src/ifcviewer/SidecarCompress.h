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

#ifndef SIDECARCOMPRESS_H
#define SIDECARCOMPRESS_H

// zstd wrappers for the .ifcview format (v16+). Geometry chunks and metadata
// blocks are stored zstd-compressed so the network pulls far fewer bytes while
// keeping HTTP Range streaming intact (unlike server Content-Encoding, which
// can't be byte-ranged). The baker compresses (desktop only); every loader —
// desktop and web — decompresses. The web build links the vendored single-file
// zstd DECODER (third_party/zstddeclib.c); desktop links the full libzstd.

#include <cstddef>
#include <cstdint>
#include <vector>

namespace SidecarCompress {

// Decompress a zstd frame in [src, src+src_size) into dst, which must have room
// for exactly raw_size bytes. Returns false on any zstd error or if the frame
// doesn't expand to exactly raw_size. Available on all platforms.
bool decompress(const std::uint8_t* src, std::size_t src_size,
                std::uint8_t* dst, std::size_t raw_size);

#if !defined(__EMSCRIPTEN__)
// Compress [src, src+n) with zstd at `level`. Returns the compressed frame, or
// an empty vector on error. Bake/desktop only — the web build never compresses.
std::vector<std::uint8_t> compress(const std::uint8_t* src, std::size_t n,
                                   int level);
#endif

}  // namespace SidecarCompress

#endif  // SIDECARCOMPRESS_H
