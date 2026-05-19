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

message("Running CMakeLists.txt in /src/bonsaiviewer")

set(QT_VERSION 6 CACHE STRING "Qt version")
find_package(Qt${QT_VERSION} COMPONENTS Core CorePrivate Gui Widgets Svg REQUIRED PATHS ${QT_DIR})

set(BONSAIVIEWER_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/ElementRegistry.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/ElementRegistry.h
    ${CMAKE_CURRENT_SOURCE_DIR}/ViewerSettings.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/ViewerSettings.h
    ${CMAKE_CURRENT_SOURCE_DIR}/SessionState.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/SessionState.h
    ${CMAKE_CURRENT_SOURCE_DIR}/MainWindow.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/MainWindow.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Measurement.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Measurement.h
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
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Discovery.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Discovery.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/PickerDialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/PickerDialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Process.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Process.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Registry.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/connectors/Registry.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/AddModelDialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/AddModelDialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/SettingsDialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/SettingsDialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/SettingsView.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/SettingsView.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/Commands.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/Commands.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/FederationItemModel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/FederationItemModel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/models/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/todo/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/todo/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/properties/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/properties/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/properties/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/properties/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/properties/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/Commands.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/Commands.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/SaveProjectDialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/SaveProjectDialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/settings/Dialog.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/settings/Dialog.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/spatial_hierarchy/Types.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/spatial_hierarchy/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/spatial_hierarchy/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/spatial_hierarchy/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/spatial_hierarchy/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/Panel.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/Panel.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/Commands.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/Commands.h
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/View.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/viewport/View.h
    ${CMAKE_CURRENT_SOURCE_DIR}/bonsaiviewer_resources.qrc
)

add_executable(BonsaiViewer ${BONSAIVIEWER_FILES})

set_target_properties(BonsaiViewer PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(BonsaiViewer PRIVATE
    IfcViewer
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::CorePrivate
    Qt${QT_VERSION}::Gui
    Qt${QT_VERSION}::Svg
    Qt${QT_VERSION}::Widgets
)

install(TARGETS BonsaiViewer EXPORT ${IFCOPENSHELL_EXPORT_TARGETS})
ifcopenshell_deploy_qt_runtime(BonsaiViewer)
