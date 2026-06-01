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

message("Running CMakeLists.txt in /src/ifcviewer-wgpu-minimal")

find_package(Qt${QT_VERSION} COMPONENTS Widgets REQUIRED PATHS ${QT_DIR})

file(GLOB IFCVIEWER_WGPU_MIN_CPP_FILES ${CMAKE_CURRENT_SOURCE_DIR}/*.cpp)

add_executable(IfcViewerWgpuMinimal ${IFCVIEWER_WGPU_MIN_CPP_FILES})

set_target_properties(IfcViewerWgpuMinimal PROPERTIES
    AUTOMOC ON
    WIN32_EXECUTABLE ON
    MACOSX_BUNDLE ON
)

target_link_libraries(IfcViewerWgpuMinimal PRIVATE
    IfcViewerWgpu
    Qt${QT_VERSION}::Widgets
)

# Pin the build-tree rpath so the executable finds libwgpu_native.so when
# run directly out of build-viewer-wgpu/. The patched SONAME means DT_NEEDED
# is just the basename, so a single rpath entry suffices.
if(UNIX AND NOT APPLE AND WGPU_NATIVE_LIB_DIR)
    set_target_properties(IfcViewerWgpuMinimal PROPERTIES
        BUILD_RPATH "${WGPU_NATIVE_LIB_DIR}"
    )
endif()

# MACOSX_BUNDLE targets require BUNDLE DESTINATION at install time even
# when nobody is going to run `make install` (CMake validates the rule
# at configure). Provide one alongside the regular bin/ runtime path.
install(TARGETS IfcViewerWgpuMinimal
    EXPORT  ${IFCOPENSHELL_EXPORT_TARGETS}
    RUNTIME DESTINATION bin
    BUNDLE  DESTINATION bin
)
ifcopenshell_deploy_qt_runtime(IfcViewerWgpuMinimal)
