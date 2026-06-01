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

# Tier-1 unit tests for the wgpu backend's pure-CPU state machines (selection,
# visibility). Header-only subjects — the test binaries compile against the
# class definitions directly, no link to IfcViewerWgpu needed and no
# wgpu-native runtime involvement.

set(IFCVIEWER_WGPU_SRC ${CMAKE_CURRENT_SOURCE_DIR}/..)

function(add_ifcviewer_wgpu_unit_test name)
    add_executable(${name} ${name}.cpp)
    target_include_directories(${name} PRIVATE ${IFCVIEWER_WGPU_SRC})
    target_link_libraries(${name} PRIVATE Catch2::Catch2WithMain)
    catch_discover_tests(${name})
endfunction()

add_ifcviewer_wgpu_unit_test(test_wgpu_selection)
add_ifcviewer_wgpu_unit_test(test_wgpu_visibility)
