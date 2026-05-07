# This file was generated with the assistance of an AI coding tool.
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

message("Running CMakeLists.txt in /src/interface")

set(QT_VERSION 6 CACHE STRING "Qt version")
find_package(Qt${QT_VERSION} COMPONENTS Core Gui Widgets Svg REQUIRED PATHS ${QT_DIR})

set(INTERFACE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/ElementRegistry.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/ElementRegistry.h
    ${CMAKE_CURRENT_SOURCE_DIR}/MainWindow.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/MainWindow.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/SvgIcon.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/SvgIcon.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Style.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Style.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Dialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Dialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Tabs.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Tabs.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/KeyValueTable.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/KeyValueTable.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Buttons.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Buttons.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Section.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Section.h
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/components/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/add_model/Dialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/add_model/Dialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/models/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/models/Widget.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/models/Widget.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/models/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/models/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/todo/Widget.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/todo/Widget.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/properties/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/properties/Widget.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/properties/Widget.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/properties/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/properties/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/settings/Dialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/settings/Dialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/spatial_hierarchy/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/spatial_hierarchy/Widget.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/spatial_hierarchy/Widget.h
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/spatial_hierarchy/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/panels/spatial_hierarchy/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/interface_resources.qrc
)

add_executable(IfcInterfaceMockup ${INTERFACE_FILES})

set_target_properties(IfcInterfaceMockup PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(IfcInterfaceMockup PRIVATE
    IfcViewer
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::Gui
    Qt${QT_VERSION}::Svg
    Qt${QT_VERSION}::Widgets
)

install(TARGETS IfcInterfaceMockup EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
