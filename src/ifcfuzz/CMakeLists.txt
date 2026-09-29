################################################################################
#                                                                              #
# This file is part of IfcOpenShell.                                           #
#                                                                              #
# IfcOpenShell is free software: you can redistribute it and/or modify         #
# it under the terms of the Lesser GNU General Public License as published by  #
# the Free Software Foundation, either version 3.0 of the License, or          #
# (at your option) any later version.                                          #
#                                                                              #
# IfcOpenShell is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 #
# Lesser GNU General Public License for more details.                          #
#                                                                              #
# You should have received a copy of the Lesser GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.         #
#                                                                              #
################################################################################

# libFuzzer harness(es) for IfcOpenShell. Only built when BUILD_FUZZERS is ON,
# which is expected to be paired with a Clang toolchain configured with
# -fsanitize=fuzzer (and typically also address,undefined) in
# CMAKE_CXX_FLAGS - this target does not add sanitizer flags itself.

include_directories("${CMAKE_SOURCE_DIR}/../src")

add_executable(ifcparse_fuzzer ifcparse_fuzzer.cpp)
target_include_directories(ifcparse_fuzzer PRIVATE "${CMAKE_SOURCE_DIR}/../src")
target_link_libraries(ifcparse_fuzzer PRIVATE IfcParse)

# -fsanitize=fuzzer supplies its own main() and libFuzzer's driver, so it
# must stay scoped to this one executable rather than going in the global
# CMAKE_CXX_FLAGS - every other target (including CMake's own compiler
# checks) would otherwise fail to link. ASan/UBSan, by contrast, are applied
# globally via CMAKE_CXX_FLAGS so that IfcParse itself is instrumented.
target_compile_options(ifcparse_fuzzer PRIVATE -fsanitize=fuzzer)
target_link_options(ifcparse_fuzzer PRIVATE -fsanitize=fuzzer)
