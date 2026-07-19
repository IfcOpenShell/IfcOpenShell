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

// libFuzzer entry point for IfcParse::IfcFile. Parses the input entirely
// in-memory (no subprocess, no temp files) so a coverage-guided fuzzer can
// reach the tokenizer and argument parser directly instead of only ever
// observing IfcConvert's exit code.

#include "ifcparse/IfcFile.h"

#include <cstddef>
#include <cstdint>
#include <limits>
#include <sstream>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    if (size == 0 || size > static_cast<size_t>(std::numeric_limits<int>::max())) {
        return 0;
    }

    try {
        IfcParse::IfcFile file(const_cast<void*>(static_cast<const void*>(data)), static_cast<int>(size));

        if (file.good()) {
            // Constructing IfcFile already tokenizes and type-checks every
            // attribute of every instance (and resolves references), so
            // most tokenizer/argument bugs are reachable without going any
            // further. toString() is still exercised here since
            // reserialization walks a different code path and may surface
            // additional faults.
            std::ostringstream discard;
            for (const auto& entity : file) {
                try {
                    entity.second->toString(discard);
                } catch (const std::exception&) {
                    // Malformed attributes are expected on fuzzed input.
                }
            }
        }
    } catch (const std::exception&) {
        // IfcException (and friends) is expected control flow for malformed
        // input, not a bug. Only crashes caught by ASan/UBSan/libFuzzer
        // itself - which bypass try/catch - are findings.
    }

    return 0;
}
