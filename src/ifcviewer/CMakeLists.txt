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

message("Running CMakeLists.txt in /src/ifcviewer")

set(QT_VERSION 6 CACHE STRING "Qt version")
# IfcViewer always needs OpenGL in addition to Core/Gui/Widgets. We don't use
# the CACHE'd QT_COMPONENTS here because it may have been set by another target
# (e.g. qtviewer) without the OpenGL component.
find_package(Qt${QT_VERSION} COMPONENTS Core Gui Widgets OpenGL REQUIRED PATHS ${QT_DIR})

find_package(OpenGL REQUIRED)

file(GLOB IFCVIEWER_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB IFCVIEWER_H_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
set(IFCVIEWER_FILES ${IFCVIEWER_CPP_FILES} ${IFCVIEWER_H_FILES})

add_executable(IfcViewer ${IFCVIEWER_FILES})

set_target_properties(IfcViewer PROPERTIES
    AUTOMOC ON
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(IfcViewer PRIVATE
    IfcGeom
    IfcParse
    ${kernel_libraries}
    ${OpenCASCADE_LIBRARIES}
    ${Boost_LIBRARIES}
    ${CGAL_LIBRARIES}
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui
    Qt${QT_VERSION}::Widgets
    Qt${QT_VERSION}::OpenGL
    OpenGL::GL
)

if(UNIX AND NOT APPLE)
    find_package(Threads REQUIRED)
    target_link_libraries(IfcViewer PRIVATE Threads::Threads)
endif()

install(TARGETS IfcViewer EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
