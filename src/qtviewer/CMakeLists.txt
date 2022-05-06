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
message("Provide the path to Qt5 via CMAKE_PREFIX_PATH")

find_package(Qt5 COMPONENTS Core Gui OpenGL Widgets REQUIRED)

add_executable(QtViewer
        ../../src/qtviewer/mainwindow.h
        ../../src/qtviewer/mainwindow.cpp
        ../../src/qtviewer/main.cpp
)

set_target_properties(QtViewer PROPERTIES
	AUTOMOC On
)

target_link_libraries(QtViewer
	${IFCLIBS}
	Qt5::Core Qt5::Gui Qt5::OpenGL Qt5::Widgets
	${OPENCASCADE_LIBRARIES}
)