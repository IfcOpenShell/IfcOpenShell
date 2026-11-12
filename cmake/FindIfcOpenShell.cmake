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

include("${CMAKE_CURRENT_LIST_DIR}/utilities.cmake" OPTIONAL)

set(_IfcOpenShell_find_args)
if(IfcOpenShell_FIND_VERSION)
    list(APPEND _IfcOpenShell_find_args "${IfcOpenShell_FIND_VERSION}")
    if(IfcOpenShell_FIND_VERSION_EXACT)
        list(APPEND _IfcOpenShell_find_args EXACT)
    endif()
endif()
list(APPEND _IfcOpenShell_find_args CONFIG QUIET)
if(IfcOpenShell_FIND_COMPONENTS)
    list(APPEND _IfcOpenShell_find_args COMPONENTS ${IfcOpenShell_FIND_COMPONENTS})
endif()

set(_IfcOpenShell_saved_module_path "${CMAKE_MODULE_PATH}")
list(REMOVE_ITEM CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")
find_package(IfcOpenShell ${_IfcOpenShell_find_args})
set(CMAKE_MODULE_PATH "${_IfcOpenShell_saved_module_path}")

if(NOT IfcOpenShell_FOUND)
    set(_IfcOpenShell_error "Could not find an IfcOpenShell CMake config package. Set IfcOpenShell_DIR or CMAKE_PREFIX_PATH.")
    if(IfcOpenShell_FIND_REQUIRED)
        message(FATAL_ERROR "${_IfcOpenShell_error}")
    elseif(NOT IfcOpenShell_FIND_QUIETLY)
        message(STATUS "${_IfcOpenShell_error}")
    endif()
    return()
endif()

set(_IfcOpenShell_required_targets IfcOpenShell::IfcParse IfcOpenShell::IfcGeom)
set(_IfcOpenShell_missing_targets "")
foreach(_IfcOpenShell_target IN LISTS _IfcOpenShell_required_targets)
    if(NOT TARGET ${_IfcOpenShell_target})
        list(APPEND _IfcOpenShell_missing_targets ${_IfcOpenShell_target})
    endif()
endforeach()

if(_IfcOpenShell_missing_targets)
    set(IfcOpenShell_FOUND FALSE)
    string(REPLACE ";" ", " _IfcOpenShell_missing_targets_text "${_IfcOpenShell_missing_targets}")
    set(_IfcOpenShell_error "IfcOpenShell config was found, but required targets are missing: ${_IfcOpenShell_missing_targets_text}.")
    if(IfcOpenShell_FIND_REQUIRED)
        message(FATAL_ERROR "${_IfcOpenShell_error}")
    elseif(NOT IfcOpenShell_FIND_QUIETLY)
        message(STATUS "${_IfcOpenShell_error}")
    endif()
    return()
endif()

if(NOT DEFINED IFCOPENSHELL_WITH_OPENCASCADE)
    set(IFCOPENSHELL_WITH_OPENCASCADE OFF)
    if(TARGET IfcOpenShell::geometry_kernel_opencascade)
        set(IFCOPENSHELL_WITH_OPENCASCADE ON)
    endif()
endif()

if(NOT DEFINED IFCOPENSHELL_WITH_CGAL)
    set(IFCOPENSHELL_WITH_CGAL OFF)
    if(TARGET IfcOpenShell::IFCOPENSHELL_CGAL)
        set(IFCOPENSHELL_WITH_CGAL ON)
    endif()
endif()

if(NOT DEFINED IFCOPENSHELL_IFCXML)
    set(IFCOPENSHELL_IFCXML OFF)
endif()

if(NOT DEFINED IFCOPENSHELL_WITH_ROCKSDB)
    set(IFCOPENSHELL_WITH_ROCKSDB OFF)
endif()

set(IFCOPENSHELL_LIBRARIES IfcOpenShell::IfcParse)
foreach(_IfcOpenShell_target IN ITEMS IfcOpenShell::geometry_serializer IfcOpenShell::Serializers)
    if(TARGET ${_IfcOpenShell_target})
        list(APPEND IFCOPENSHELL_LIBRARIES ${_IfcOpenShell_target})
    endif()
endforeach()

set(IFCOPENSHELL_KERNEL_LIBRARIES "")
foreach(_IfcOpenShell_target IN ITEMS
    IfcOpenShell::geometry_kernel_opencascade
    IfcOpenShell::geometry_kernel_cgal
    IfcOpenShell::geometry_kernel_cgal_simple
)
    if(TARGET ${_IfcOpenShell_target})
        list(APPEND IFCOPENSHELL_KERNEL_LIBRARIES ${_IfcOpenShell_target})
    endif()
endforeach()

set(IFCOPENSHELL_GEOMETRY_LIBRARIES IfcOpenShell::IfcGeom ${IFCOPENSHELL_KERNEL_LIBRARIES})

if(TARGET IfcOpenShell::OpenCASCADE_INTERFACE)
    set(OpenCASCADE_LIBRARIES IfcOpenShell::OpenCASCADE_INTERFACE)
endif()

if(TARGET IfcOpenShell::IFCOPENSHELL_CGAL)
    set(CGAL_LIBRARIES IfcOpenShell::IFCOPENSHELL_CGAL)
endif()

if(TARGET IfcOpenShell::svgfill)
    set(IFCOPENSHELL_SVGFILL_LIBRARY IfcOpenShell::svgfill)
endif()

mark_as_advanced(IfcOpenShell_DIR)

unset(_IfcOpenShell_error)
unset(_IfcOpenShell_find_args)
unset(_IfcOpenShell_missing_targets)
unset(_IfcOpenShell_missing_targets_text)
unset(_IfcOpenShell_required_targets)
unset(_IfcOpenShell_target)
