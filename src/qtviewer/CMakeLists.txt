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

cmake_minimum_required(VERSION 3.1.3)

message("Running CMakeLists.txt in /src/qtviewer")

# Specify the Qt version and components to use
set(QT_VERSION 6 CACHE STRING "Qt version")
set(QT_COMPONENTS Core Gui OpenGL OpenGLWidgets Widgets CACHE STRING "Qt components")

find_package(Qt${QT_VERSION} COMPONENTS ${QT_COMPONENTS} REQUIRED PATHS ${QT_DIR})

if(Qt${QT_VERSION}_FOUND)
    message(STATUS "Found Qt Version: ${Qt${QT_VERSION}_VERSION}")
endif()

set(targetName "QtViewer")

add_executable(${targetName}
    IfcViewerWidget.h
    IfcViewerWidget.cpp
    ParseIfcFile.h
    ParseIfcFile.cpp
    MainWindow.h
    MainWindow.cpp
    main.cpp
)

set_target_properties(${targetName} PROPERTIES
    AUTOMOC On
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(${targetName}
    ${IFCOPENSHELL_LIBRARIES}
    Qt${QT_VERSION}::Core 
    Qt${QT_VERSION}::Gui 
    Qt${QT_VERSION}::OpenGL 
    Qt${QT_VERSION}::OpenGLWidgets 
    Qt${QT_VERSION}::Widgets
    ${OPENCASCADE_LIBRARIES}
)

target_include_directories(${targetName} PUBLIC 
    ${QT_DIR}/include
)

get_target_property(targetIncludeDirs ${targetName} INCLUDE_DIRECTORIES)
message(STATUS "target_include_directories: ${targetIncludeDirs}")