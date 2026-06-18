set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(svgfill)

if(POLICY CMP0144) # 3.27
    cmake_policy(SET CMP0144 NEW) # find_package() uses upper-case <PACKAGENAME>_ROOT variables.
endif()
if(POLICY CMP0167) # 3.30 find_package(Boost) to use BoostConfig instead of FindBoost.
    cmake_policy(SET CMP0167 OLD)
endif()

if(WIN32 AND NOT DEFINED ENV{CONDA_BUILD})
    set(Boost_USE_STATIC_LIBS ON)
    set(Boost_USE_MULTITHREADED ON)
    if(USE_STATIC_MSVC_RUNTIME)
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

if(MSVC)
    add_definitions(-bigobj)
endif()

find_package(Boost)
message(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
find_package(LibXml2 REQUIRED)
find_package(CGAL REQUIRED)

set(SVGPP_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/svgpp/include")
if(NOT EXISTS ${SVGPP_INCLUDE})
    message(
        FATAL_ERROR
        "Missing svgpp include path, probably you forgot to initialize submodules in git repo. Missing path - '${SVGPP_INCLUDE}'."
    )
endif()
include_directories(${Boost_INCLUDE_DIRS} ${SVGPP_INCLUDE})

file(GLOB LIB_H_FILES src/*.h)
file(GLOB LIB_CPP_FILES src/svgfill.cpp src/arrange_polygons.cpp)
set(LIB_SRC_FILES ${LIB_H_FILES} ${LIB_CPP_FILES})
add_library(svgfill ${LIB_SRC_FILES})
target_link_libraries(svgfill ${Boost_LIBRARIES} ${BCRYPT_LIBRARIES} LibXml2::LibXml2 IFCOPENSHELL_CGAL IfcParse)
set_target_properties(svgfill PROPERTIES PUBLIC_HEADER "${LIB_H_FILES}")

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

install(
    TARGETS svgfill_exe svgfill
    EXPORT ${IFCOPENSHELL_EXPORT_TARGETS}
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/svgfill"
)
