cmake_minimum_required (VERSION 3.10)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project (svgfill)

cmake_policy(SET CMP0074 NEW) # find_package() uses <PackageName>_ROOT variables.
if (POLICY CMP0144)
cmake_policy(SET CMP0144 NEW) # find_package() uses upper-case <PACKAGENAME>_ROOT variables.
endif()
if(POLICY CMP0167) # 3.30 find_package(Boost) to use BoostConfig instead of FindBoost.
    cmake_policy(SET CMP0167 OLD)
endif()

include(GNUInstallDirs)

# Specify paths to install files
if(NOT BINDIR)
    set(BINDIR bin)
endif()
if(NOT IS_ABSOLUTE ${BINDIR})
    set(BINDIR ${CMAKE_INSTALL_BINDIR})
endif()
message(STATUS "BINDIR: ${BINDIR}")

if(NOT INCLUDEDIR)
    set(INCLUDEDIR include)
endif()
if(NOT IS_ABSOLUTE ${INCLUDEDIR})
    set(INCLUDEDIR ${CMAKE_INSTALL_INCLUDEDIR})
endif()
message(STATUS "INCLUDEDIR: ${INCLUDEDIR}")

if(NOT LIBDIR)
    set(LIBDIR lib)
endif()
if(NOT IS_ABSOLUTE ${LIBDIR})
    set(LIBDIR ${CMAKE_INSTALL_LIBDIR})
endif()
message(STATUS "LIBDIR: ${LIBDIR}")

set(CGAL_LIBRARY_NAMES libCGAL_Core libCGAL_ImageIO libCGAL)

if(NOT CGAL_INCLUDE_DIR)
	find_package(CGAL REQUIRED)
	if(NOT CGAL_DIR)
		message(
			FATAL_ERROR
			"CGAL_SUPPORT enabled, but CGAL_INCLUDE_DIR wasn't provided and CGAL package couldn't be found."
		)
	endif()
	message(STATUS "CGAL: found config at '${CGAL_DIR}'.")
	set(CGAL_LIBRARIES CGAL::CGAL)
else()
	set(CGAL_INCLUDE_DIR ${CGAL_INCLUDE_DIR} CACHE FILEPATH "CGAL header files")
	message(STATUS "Looking for CGAL include files in: ${CGAL_INCLUDE_DIR}")

	if(NOT "${CGAL_LIBRARY_DIR}" STREQUAL "")
		set(CGAL_LIBRARY_DIR ${CGAL_LIBRARY_DIR} CACHE FILEPATH "CGAL library files")
		message(STATUS "Looking for CGAL library files in: ${CGAL_LIBRARY_DIR}")
	endif()

	if(WASM_BUILD)
		set(CMAKE_FIND_ROOT_PATH_BACKUP "${CMAKE_FIND_ROOT_PATH}")
		set(CMAKE_FIND_ROOT_PATH "")
	endif()

	find_library(libCGAL NAMES CGAL PATHS ${CGAL_LIBRARY_DIR} NO_DEFAULT_PATH)

	if(libCGAL)
		message(STATUS "CGAL library files found")
		foreach(lib ${CGAL_LIBRARY_NAMES})
			string(REPLACE libCGAL "${lib}" lib_path "${libCGAL}")
			list(APPEND CGAL_LIBRARIES "${lib_path}")
		endforeach()
	else()
		if(NOT "${CGAL_LIBRARY_DIR}" STREQUAL "")
			file(GLOB CGAL_LIBRARIES ${CGAL_LIBRARY_DIR}/CGAL*.lib)
			list(LENGTH CGAL_LIBRARY_NAMES num_cgal_library_names)
			list(LENGTH CGAL_LIBRARIES num_cgal_libraries)
			link_directories("${CGAL_LIBRARY_DIR}")
			if(NOT "${num_cgal_library_names}" STREQUAL "${num_cgal_libraries}")
				message(FATAL_ERROR "Unable to find CGAL library files, aborting")
			endif()
			message(STATUS "CGAL library files found")
		endif()
	endif()
	find_library(libGMP NAMES gmp mpir PATHS ${GMP_LIBRARY_DIR} NO_DEFAULT_PATH)
	find_library(libMPFR NAMES mpfr PATHS ${MPFR_LIBRARY_DIR} NO_DEFAULT_PATH)
	if(NOT libGMP)
			message(FATAL_ERROR "Unable to find GMP library files, aborting")
	endif()
	if(NOT libMPFR)
			message(FATAL_ERROR "Unable to find MPFR library files, aborting")
	endif()
	
	list(APPEND CGAL_LIBRARIES "${libMPFR}")
	list(APPEND CGAL_LIBRARIES "${libGMP}")
endif(NOT CGAL_INCLUDE_DIR)

if(WIN32 AND ("$ENV{CONDA_BUILD}" STREQUAL ""))
	set(Boost_USE_STATIC_LIBS ON)
	set(Boost_USE_MULTITHREADED ON)
    if (USE_STATIC_MSVC_RUNTIME)
        set(Boost_USE_STATIC_RUNTIME ON)
    endif()
else()
    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and it's going to conflict if there are multiple, as is
    # the case in conda-forge's libboost feedstock.
    add_definitions(-DBOOST_ALL_NO_LIB)
    if(WIN32)
        # Necessary for boost version >= 1.67
        set(BCRYPT_LIBRARIES "bcrypt.lib")
    endif()
endif()

if (MSVC)
	add_definitions(-bigobj)
endif()

find_package(Boost)
message(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
find_package(LibXml2 REQUIRED)

if(WASM_BUILD)
    set(CMAKE_FIND_ROOT_PATH "${CMAKE_FIND_ROOT_PATH_BACKUP}")
endif()



include_directories(${Boost_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR}
	${CGAL_INCLUDE_DIR} ${GMP_INCLUDE_DIR} ${MPFR_INCLUDE_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/svgpp/include
)

file(GLOB LIB_H_FILES src/*.h)
file(GLOB LIB_CPP_FILES src/svgfill.cpp src/arrange_polygons.cpp)
set(LIB_SRC_FILES ${LIB_H_FILES} ${LIB_CPP_FILES})
add_library(svgfill ${LIB_SRC_FILES})
if(LibXml2_DIR)
    find_package(LibXml2 CONFIG REQUIRED)
    target_compile_definitions(svgfill PRIVATE ${LIBXML2_DEFINITIONS})
endif()
target_link_libraries(svgfill ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES} ${LIBXML2_LIBRARIES} ${CGAL_LIBRARIES})

add_executable(svgfill_exe src/main.cpp)
target_link_libraries(svgfill_exe svgfill)
set_property(TARGET svgfill_exe PROPERTY OUTPUT_NAME svgfill)
if(WIN32)
	# both the library and the executable now result in a file with basename svgfill,
	# on linux the the library is prefixed with lib as libsvgfill.a. Windows does not
	# have this mechanism, so on windows the linker would be created an import library
	# for the executable, also named svgfill.lib. This naming conflict results in:
	#     LINK : fatal error LNK1149: output filename matches input filename
	# This flag tells the linker not to generate an import library and therefore no
	# conflict occurs.
    target_link_options(svgfill_exe PRIVATE "/NOIMPLIB")
endif()

install(TARGETS svgfill_exe DESTINATION ${BINDIR})
install(TARGETS svgfill DESTINATION ${LIBDIR})
install(FILES ${LIB_H_FILES} DESTINATION ${INCLUDEDIR})
