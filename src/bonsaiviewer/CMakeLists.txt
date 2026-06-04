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
# Qt6::CorePrivate is exposed differently across Qt versions: Qt 6.8 ships the
# target inside Qt6Core (no CorePrivate config package), while Qt 6.10 provides
# it only as a separate CorePrivate package. OPTIONAL_COMPONENTS finds that
# package where it exists without failing where it does not; the Qt6::CorePrivate
# target ends up available either way for the link step below.
find_package(Qt${QT_VERSION} REQUIRED
             COMPONENTS Core Gui Widgets Svg
             OPTIONAL_COMPONENTS CorePrivate
             PATHS ${QT_DIR})

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
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/RecentProjects.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/modules/project/RecentProjects.h
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

# macOS bundle runtime layout. BonsaiViewer's exe has
# `LC_LOAD_DYLIB @rpath/libwgpu_native.dylib` (CMake bakes that in from
# the dylib's own install_name). Without an LC_RPATH entry pointing at
# the bundle's Frameworks/ dir, dyld aborts at launch with
# "no LC_RPATH's found". Set the standard macOS app-bundle rpath so
# the load resolves; the wgpu CMakeLists installs the dylib straight
# into BonsaiViewer.app/Contents/Frameworks for us.
if(APPLE)
    set_target_properties(BonsaiViewer PROPERTIES
        INSTALL_RPATH "@executable_path/../Frameworks"
    )
endif()

target_link_libraries(BonsaiViewer PRIVATE
    # IfcViewer is the unified scene + render lib (SceneLoader, Federation,
    # GeometryStreamer, SidecarBuilder, ViewportWindow, OverlayRenderer,
    # BufferPool, …) since the wgpu/ifcviewer merge.
    IfcViewer
    Qt${QT_VERSION}::Core
    Qt${QT_VERSION}::CorePrivate
    Qt${QT_VERSION}::Gui
    Qt${QT_VERSION}::Svg
    Qt${QT_VERSION}::Widgets
)

# BUNDLE DESTINATION must be "." (install-prefix root) on macOS — Qt's
# deploy generator emits `macdeployqt BonsaiViewer.app` (no path
# prefix), which resolves only when the .app sits at the install root.
install(TARGETS BonsaiViewer
    EXPORT  ${IFCOPENSHELL_EXPORT_TARGETS}
    RUNTIME DESTINATION bin
    BUNDLE  DESTINATION .
)
ifcopenshell_deploy_qt_runtime(BonsaiViewer)

# Stage IfcOpenShell dylibs into the .app bundle's Frameworks/ directory.
#
# Two flavours sit alongside each other in <prefix>/lib/ after install:
#
#   1. Linked core libs (lib*.dylib) — IfcParse, IfcGeom (output-named
#      libifcopenshell.geometry.dylib), IfcViewer, plug-in / mapping /
#      kernel shared libs. With --shared these are runtime @rpath deps
#      of BonsaiViewer.exe. macdeployqt is *supposed* to follow them
#      but in practice misses non-Qt @rpath deps when the source lib
#      lives outside the standard system / Qt prefixes, so we stage
#      them explicitly. (In a static build these are absent from lib/
#      and the glob just no-ops, so this rule is safe in both modes.)
#
#   2. Plug-ins (ifcopenshell.*.dylib, no `lib` prefix) — dlopen-only
#      deps the plug-in loader resolves at runtime. macdeployqt has
#      no way to know about these.
#
# Both kinds get a flat copy into Contents/Frameworks/. The plug-in
# loader's primary search path is dirname(libIfcParse) (= Frameworks/
# inside the bundle), so plug-ins and core libs both find each other
# on the first probe.
#
# The geometry-writer filter drops ifcopenshell.geometry.writer.*.dylib
# (the per-schema OBJ / glTF / DAE / STP / IGS / SVG / TTL export
# converters — heavy, viewer-irrelevant). Mirrors the Rocky workflow's
# filter in `stage_runtime_payload` (see 27249770e).
#
# <prefix>/lib/ is IfcOpenShell-exclusive — Qt / boost / eigen live in
# their own brew / build prefixes — so a broad *.dylib glob is safe
# here and automatically picks up any future shared libs without
# needing to maintain an explicit name list.
#
# Subdirectory order in cmake/CMakeLists.txt guarantees that ifcparse/
# / ifcgeom/ / serializers/ are add_subdirectory'd before bonsaiviewer/,
# so by the time this install rule fires the *.dylib files are already
# on disk under <prefix>/lib/.
if(APPLE)
    install(CODE [[
        set(_fw "${CMAKE_INSTALL_PREFIX}/BonsaiViewer.app/Contents/Frameworks")
        file(GLOB _ifc_dylibs "${CMAKE_INSTALL_PREFIX}/lib/*.dylib")
        list(FILTER _ifc_dylibs EXCLUDE REGEX "ifcopenshell\\.geometry\\.writer\\.")
        if(_ifc_dylibs)
            message(STATUS "Staging IfcOpenShell dylibs (linked core + plug-ins) into BonsaiViewer.app/Contents/Frameworks")
            file(COPY ${_ifc_dylibs} DESTINATION "${_fw}")
        else()
            message(WARNING "No IfcOpenShell *.dylib found in lib/ — BonsaiViewer.app will fail to launch (missing @rpath linked deps) or at IFC load time (missing plug-ins)")
        endif()
    ]])
endif()
