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

SET(CMAKE_SWIG_FLAGS "")
# NOTE Workaround for most likely missing debug Python libraries on Windows (requires Python built from the source).
# Python 3.5 intaller and onwards will have an option to install the debug libraries too.
# NOTE PYTHON_DEBUG_LIBRARIES appears to be a deprecated variable
IF (WIN32 AND NOT PYTHON_DEBUG_LIBRARIES)
	MESSAGE(STATUS "PYTHON_DEBUG_LIBRARIES not found, defining SWIG_PYTHON_INTERPRETER_NO_DEBUG workaround for IfcWrap.")
	ADD_DEFINITIONS(-DSWIG_PYTHON_INTERPRETER_NO_DEBUG)
ENDIF()

SET_SOURCE_FILES_PROPERTIES(IfcPython.i PROPERTIES CPLUSPLUS ON)
SWIG_ADD_MODULE(ifcopenshell_wrapper python IfcPython.i)
if("$ENV{LDFLAGS}" MATCHES ".undefined.suppress")
# On osx there is some state in the python dylib. With `-Wl,undefined,suppress` we can ignore the missing symbols at compile time.
SWIG_LINK_LIBRARIES(ifcopenshell_wrapper ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES})
else()
SWIG_LINK_LIBRARIES(ifcopenshell_wrapper ${IFCOPENSHELL_LIBRARIES} ${PYTHON_LIBRARIES} ${OPENCASCADE_LIBRARIES} ${Boost_LIBRARIES})
endif()
if ((NOT WIN32) AND BUILD_SHARED_LIBS)
    SET_INSTALL_RPATHS(${SWIG_MODULE_ifcopenshell_wrapper_REAL_NAME} "${IFCDIRS};${OCC_LIBRARY_DIR}")
endif()

# Try to find the Python interpreter to get the site-packages
# directory in which the wrapper can be installed.
FIND_PACKAGE(PythonInterp)
IF(PYTHONINTERP_FOUND AND NOT "${PYTHON_EXECUTABLE}" STREQUAL "")
    IF (USERSPACE_PYTHON_PREFIX)
        EXECUTE_PROCESS(
            COMMAND ${PYTHON_EXECUTABLE} -c "import sys; import site; sys.stdout.write(site.USER_SITE)"
            OUTPUT_VARIABLE python_package_dir
        )
    ELSE ()
        EXECUTE_PROCESS(
            COMMAND ${PYTHON_EXECUTABLE} -c "import sys; from distutils.sysconfig import get_python_lib; sys.stdout.write(get_python_lib(1))"
            OUTPUT_VARIABLE python_package_dir
        )
    ENDIF()
    set(python_package_dir ${CMAKE_INSTALL_LIBDIR}/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages/)
    IF("${python_package_dir}" STREQUAL "")
        MESSAGE(WARNING "Unable to locate Python site-package directory, unals /ble to install the Python wrapper")
    ELSE()
        FILE(GLOB_RECURSE sourcefiles 
            "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/*"
        )
        FOREACH(file ${sourcefiles})
            FILE(RELATIVE_PATH relative "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/" "${file}")
            GET_FILENAME_COMPONENT(dir "${relative}" DIRECTORY)
			INSTALL(FILES "${file}"
                    DESTINATION "${python_package_dir}/ifcopenshell/${dir}")
        ENDFOREACH()
        INSTALL(FILES "${CMAKE_BINARY_DIR}/ifcwrap/ifcopenshell_wrapper.py"
                DESTINATION "${python_package_dir}/ifcopenshell")
        INSTALL(TARGETS _ifcopenshell_wrapper
                DESTINATION "${python_package_dir}/ifcopenshell")
    ENDIF()
ELSE()
    MESSAGE(WARNING "No Python interpreter found, unable to install the Python wrapper")
ENDIF()
