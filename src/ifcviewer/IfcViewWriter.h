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

#ifndef IFCVIEWWRITER_H
#define IFCVIEWWRITER_H

// Baking a .ifcview (format in IfcViewFormat.h).  Desktop only: the web build
// never writes a .ifcview and links a decompress-only zstd, so this file is not
// compiled under Emscripten.

#include "IfcViewFormat.h"

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

// Compress [src, src+n) as one zstd frame at `level`. Returns the frame, or an
// empty vector on error.
std::vector<std::uint8_t> compressIfcViewFrame(const std::uint8_t* src, std::size_t n,
                                               int level);

// Write `data` to the .ifcview path for `ifc_path` (see ifcViewPathFor),
// compressing every chunk's geometry in parallel.
bool writeIfcView(const std::string& ifc_path, const IfcViewData& data);

#endif // IFCVIEWWRITER_H
