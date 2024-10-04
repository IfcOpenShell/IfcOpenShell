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

FIND_PACKAGE(SWIG)
IF(NOT SWIG_FOUND)
	MESSAGE(FATAL_ERROR "BUILD_IFCPYTHON enabled, but unable to find SWIG. Disable BUILD_IFCPYTHON or fix SWIG paths to proceed.")
ENDIF()
include(GNUInstallDirs)
INCLUDE(${SWIG_USE_FILE})

IF(NOT "$ENV{PYTHON_INCLUDE_DIR}" STREQUAL "")
	SET(PYTHON_INCLUDE_DIR $ENV{PYTHON_INCLUDE_DIR} CACHE FILEPATH "Python header files")
	MESSAGE(STATUS "Looking for Python header files in: ${PYTHON_INCLUDE_DIR}")
ENDIF()
IF(NOT "$ENV{PYTHON_LIBRARY}" STREQUAL "")
	SET(PYTHON_LIBRARY $ENV{PYTHON_LIBRARY} CACHE FILEPATH "Python library file")
	MESSAGE(STATUS "Looking for Python library file in: ${PYTHON_LIBRARY}")
ENDIF()

# NOTE PYTHONLIBS_FOUND and PYTHONINTERP_FOUND cannot seem to be trusted so
# we need further checks to see whether the packages were actually found or not.
FIND_PACKAGE(PythonLibs)
IF(NOT PYTHONLIBS_FOUND OR "$PYTHON_INCLUDE_DIRS}" STREQUAL "")
	MESSAGE(FATAL_ERROR "BUILD_IFCPYTHON enabled, but unable to find Python lib or header. Disable BUILD_IFCPYTHON or fix Python paths to proceed.")
ENDIF()

INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_DIRS})
INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS ${SWIG_DEFINES})
# NOTE Workaround for most likely missing debug Python libraries on Windows (requires Python built from the source).
# Python 3.5 intaller and onwards will have an option to install the debug libraries too.
# NOTE PYTHON_DEBUG_LIBRARIES appears to be a deprecated variable
IF (WIN32 AND NOT PYTHON_DEBUG_LIBRARIES)
	MESSAGE(STATUS "PYTHON_DEBUG_LIBRARIES not found, defining SWIG_PYTHON_INTERPRETER_NO_DEBUG workaround for IfcWrap.")
	ADD_DEFINITIONS(-DSWIG_PYTHON_INTERPRETER_NO_DEBUG)
ENDIF()

if (WITH_CGAL)
    set(LIBSVGFILL libsvgfill)
endif()

SET_SOURCE_FILES_PROPERTIES(IfcPython.i PROPERTIES CPLUSPLUS ON)
# Rebuild on changes in other .i files.
SET_PROPERTY(
	SOURCE IfcPython.i
	PROPERTY DEPENDS
		IfcGeomWrapper.i
		IfcParseWrapper.i
		utils/type_conversion.i
		utils/typemaps_in.i
		utils/typemaps_out.i
)
swig_add_library(ifcopenshell_wrapper LANGUAGE python SOURCES IfcPython.i)
SET_PROPERTY(TARGET ${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME} PROPERTY SWIG_DEPENDS ${IFCOPENSHELL_LIBRARIES})
if("$ENV{LDFLAGS}" MATCHES ".undefined.suppress")
# On osx there is some state in the python dylib. With `-Wl,undefined,suppress` we can ignore the missing symbols at compile time.
SWIG_LINK_LIBRARIES(ifcopenshell_wrapper ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES} ${LIBSVGFILL})
else()
SWIG_LINK_LIBRARIES(ifcopenshell_wrapper ${IFCOPENSHELL_LIBRARIES} ${PYTHON_LIBRARIES} ${LIBSVGFILL})
endif()
if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    SET_INSTALL_RPATHS(${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME} "${IFCDIRS};${OCC_LIBRARY_DIR}")
endif()

# Try to find the Python interpreter to get the site-packages
# directory in which the wrapper can be installed.
FIND_PACKAGE(PythonInterp)
IF((PYTHONINTERP_FOUND AND NOT "${PYTHON_EXECUTABLE}" STREQUAL "") OR PYTHON_MODULE_INSTALL_DIR)
    # Find Python interpreter and get its version
    EXECUTE_PROCESS(
        COMMAND ${PYTHON_EXECUTABLE} -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
        OUTPUT_VARIABLE PYTHON_EXTENSION_SUFFIX
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    SET_TARGET_PROPERTIES(${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME} PROPERTIES SUFFIX ${PYTHON_EXTENSION_SUFFIX})
    if (PYTHON_MODULE_INSTALL_DIR)
	set(python_package_dir "${PYTHON_MODULE_INSTALL_DIR}")
    else()
        IF (USERSPACE_PYTHON_PREFIX)
            EXECUTE_PROCESS(
                COMMAND ${PYTHON_EXECUTABLE} -c "import sys; import site; sys.stdout.write(site.USER_SITE)"
                OUTPUT_VARIABLE python_package_dir
            )
        ELSE ()
            EXECUTE_PROCESS(
                COMMAND ${PYTHON_EXECUTABLE} -c "import sys; import sysconfig; sys.stdout.write(sysconfig.get_path('platlib'))"
                OUTPUT_VARIABLE python_package_dir
            )
        ENDIF()
        if (BUILD_PACKAGE)
            set(python_package_dir ${CMAKE_INSTALL_LIBDIR}/python${PYTHON_VERSION_MAJOR}/dist-packages/)
        endif()
    endif()
    IF("${python_package_dir}" STREQUAL "")
        MESSAGE(WARNING "Unable to locate Python site-package directory, unable to install the Python wrapper")
    ELSE()
        FILE(GLOB_RECURSE sourcefiles 
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/*"
        )
        FOREACH(file ${sourcefiles})
            FILE(RELATIVE_PATH relative "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/" "${file}")
            GET_FILENAME_COMPONENT(dir "${relative}" DIRECTORY)
            if(NOT IS_DIRECTORY "${file}")
			    INSTALL(FILES "${file}"
                        DESTINATION "${python_package_dir}/ifcopenshell/${dir}")
            endif()
        ENDFOREACH()
        INSTALL(FILES "${CMAKE_BINARY_DIR}/ifcwrap/ifcopenshell_wrapper.py"
                DESTINATION "${python_package_dir}/ifcopenshell")
        INSTALL(TARGETS ${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME}
                DESTINATION "${python_package_dir}/ifcopenshell")
	if (MSVC)
	    INSTALL(FILES $<TARGET_PDB_FILE:${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME}> DESTINATION bin OPTIONAL)
	endif()
    ENDIF()
ELSE()
    MESSAGE(WARNING "No Python interpreter found, unable to install the Python wrapper")
ENDIF()
