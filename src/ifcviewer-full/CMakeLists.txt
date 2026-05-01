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

message("Running CMakeLists.txt in /src/ifcviewer-full")

file(GLOB IFCVIEWER_FULL_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB IFCVIEWER_FULL_H_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
set(IFCVIEWER_FULL_FILES ${IFCVIEWER_FULL_CPP_FILES} ${IFCVIEWER_FULL_H_FILES})

add_executable(IfcViewerFull ${IFCVIEWER_FULL_FILES})

set_target_properties(IfcViewerFull PROPERTIES
    AUTOMOC ON
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(IfcViewerFull PRIVATE IfcViewer)

install(TARGETS IfcViewerFull EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
