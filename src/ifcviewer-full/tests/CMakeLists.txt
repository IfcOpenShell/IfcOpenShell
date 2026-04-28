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

# Tier-1 tests for ifcviewer-full. Federation is QObject-derived but only
# uses Qt6::Core (no event loop, no GL), so tests can construct it directly.

set(IFCVIEWER_FULL_SRC ${CMAKE_CURRENT_SOURCE_DIR}/..)

# Federation::HomeView holds a QVector3D (defined in QtGui), and QSignalSpy
# / QTest live in Qt6::Test.
find_package(Qt${QT_VERSION} COMPONENTS Core Gui Test REQUIRED PATHS ${QT_DIR})

add_executable(test_federation
    test_federation.cpp
    ${IFCVIEWER_FULL_SRC}/Federation.cpp
)
set_target_properties(test_federation PROPERTIES AUTOMOC ON)
target_include_directories(test_federation PRIVATE ${IFCVIEWER_FULL_SRC})
target_link_libraries(test_federation PRIVATE
    Catch2::Catch2WithMain
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui    # Federation::HomeView uses QVector3D from QtGui
    Qt${QT_VERSION}::Test   # QSignalSpy
)
catch_discover_tests(test_federation)
