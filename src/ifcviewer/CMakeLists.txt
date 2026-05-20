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
# IfcViewerLib always needs OpenGL in addition to Core/Gui/Widgets. We don't
# use the CACHE'd QT_COMPONENTS here because it may have been set by another
# target (e.g. qtviewer) without the OpenGL component.
find_package(Qt${QT_VERSION} COMPONENTS Core Gui Widgets OpenGL REQUIRED PATHS ${QT_DIR})

find_package(OpenGL REQUIRED)

file(GLOB IFCVIEWER_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)
file(GLOB IFCVIEWER_H_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
set(IFCVIEWER_FILES ${IFCVIEWER_CPP_FILES} ${IFCVIEWER_H_FILES})

add_library(IfcViewer STATIC ${IFCVIEWER_FILES})

set_target_properties(IfcViewer PROPERTIES
    AUTOMOC ON
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}"
)

if (WITH_MESH_OPTIMIZER)
find_package(meshoptimizer REQUIRED)
set(MESH_OPTIMIZER_LIB meshoptimizer::meshoptimizer)
target_compile_definitions(IfcViewer PUBLIC -DWITH_MESH_OPTIMIZER)
endif()

# Consumers include headers as `#include "ViewportWindow.h"`, so expose this
# directory on the public interface.
target_include_directories(IfcViewer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_dependencies(IfcViewer ${kernel_libraries} ${mapping_libraries})

target_link_libraries(IfcViewer PUBLIC
    IfcGeom
    IfcParse
    ${OpenCASCADE_LIBRARIES}
    ${Boost_LIBRARIES}
    ${CGAL_LIBRARIES}
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui
    Qt${QT_VERSION}::Widgets
    Qt${QT_VERSION}::OpenGL
    OpenGL::GL
    ${MESH_OPTIMIZER_LIB}
)

if(UNIX AND NOT APPLE)
    find_package(Threads REQUIRED)
    target_link_libraries(IfcViewer PUBLIC Threads::Threads)
endif()

install(TARGETS IfcViewer EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})

install(FILES ${IFCVIEWER_H_FILES}
    DESTINATION ${INCLUDEDIR}/ifcviewer
)

if(BUILD_BONSAIVIEWER_TESTS)
    add_subdirectory(tests)
endif()
