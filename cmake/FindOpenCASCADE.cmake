#
# Input variables:
# - `OCC_INCLUDE_DIR`
# - `OCC_LIBRARY_DIR`
# If input variables are not specified, try to find OpenCASCADE config.
# Input variables could also be provided as environment variables.
#
# Output variables:
# - `OCC_INCLUDE_DIR`
# - `OCC_LIBRARY_DIR`
# - `OpenCASCADE_LIBRARIES`
#

UNIFY_ENVVARS_AND_CACHE(OCC_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OCC_LIBRARY_DIR)

if(OCC_INCLUDE_DIR)
    set(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
    message(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
endif()

if(OCC_LIBRARY_DIR)
    set(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
    message(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
endif()

# No specific paths specified, try to find package.
if(OCC_INCLUDE_DIR AND OCC_LIBRARY_DIR)
    message(
        STATUS
        "Using provided OCC_INCLUDE_DIR ('${OCC_INCLUDE_DIR}') "
        "and OCC_LIBRARY_DIR ('${OCC_LIBRARY_DIR}')."
    )
    # Parse OCC_VERSION_STRING.
    file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAJOR
        REGEX "#define OCC_VERSION_MAJOR.*"
    )
    string(REGEX MATCH "[0-9]+" OCC_MAJOR ${OCC_MAJOR})
    file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MINOR
        REGEX "#define OCC_VERSION_MINOR.*"
    )
    string(REGEX MATCH "[0-9]+" OCC_MINOR ${OCC_MINOR})
    file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAINT
        REGEX "#define OCC_VERSION_MAINTENANCE.*"
    )
    string(REGEX MATCH "[0-9]+" OCC_MAINT ${OCC_MAINT})
    set(OCC_VERSION_STRING "${OCC_MAJOR}.${OCC_MINOR}.${OCC_MAINT}")
elseif(NOT OCC_INCLUDE_DIR AND NOT OCC_LIBRARY_DIR)
    # OCE is not supported for find_package, because it's using a different name (`oce`)
    # and also has an odd directory structure (install/lib/oce-0.18/*.cmake).
    find_package(OpenCASCADE CONFIG REQUIRED)
    set(OCC_INCLUDE_DIR ${OpenCASCADE_INCLUDE_DIR})
    # Do not use OpenCASCADE_LIBRARY_DIR for OCC_LIBRARY_DIR - check target property explicitly.
    # On Windows there is a case with OpenCASCADE_LIBRARY_DIR points to `lib` folder,
    # while TKernel is actually in `libi`.
    get_target_property(TKERNEL_LIB_PATH TKernel LOCATION)
    get_filename_component(OCC_LIBRARY_DIR "${TKERNEL_LIB_PATH}" DIRECTORY)
    set(OCC_VERSION_STRING ${OpenCASCADE_VERSION})
    message(
        STATUS
        "Found Open CASCADE package at '${OpenCASCADE_DIR}', "
        "deducing from it OCC_INCLUDE_DIR: '${OCC_INCLUDE_DIR}' "
        "and OCC_LIBRARY_DIR: '${OCC_LIBRARY_DIR}'."
    )
else()
    message(
        FATAL_ERROR
        "Couldn't find Open CASCADE installation. "
        "Either both OCC_INCLUDE_DIR ('${OCC_INCLUDE_DIR}') and OCC_LIBRARY_DIR ('${OCC_LIBRARY_DIR}') "
        "must be specified or OpenCASCADE package should be discoverable. "
        "If you're using OCE, then providing a package is not available "
        "and you need to provide OCE_INCLUDE_DIR and OCE_LIBRARY_DIR directly."
    )
endif()

set(
    OpenCASCADE_LIBRARIES
    TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
    TKFillet TKXSBase TKOffset TKHLR

    # @todo investigate the exact conditions when this is necessary
    TKBin
)

if(OCC_VERSION_STRING VERSION_LESS 7.8.0)
    list(APPEND OpenCASCADE_LIBRARIES  TKIGES TKSTEPBase TKSTEPAttr TKSTEP209 TKSTEP)
else(OCC_VERSION_STRING VERSION_LESS 7.8.0)
    list(APPEND OpenCASCADE_LIBRARIES TKDESTEP TKDEIGES)
endif(OCC_VERSION_STRING VERSION_LESS 7.8.0)

clear_wasm_sysroot()
find_library(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} NO_DEFAULT_PATH)
restore_wasm_sysroot()

if(libTKernel)
    message(STATUS "Required Open Cascade Library files found")
else()
    message(
        FATAL_ERROR
        "Unable to find Open Cascade library files in OCC_LIBRARY_DIR ('${OCC_LIBRARY_DIR}'), aborting"
    )
endif()

# Use the found libTKernel as a template for all other OCC libraries
# TODO Extract this into macro/function
foreach(lib ${OpenCASCADE_LIBRARIES})
    # Make sure we'll handle the Windows/MSVC debug postfix convention too.
    string(REPLACE TKerneld "${lib}" lib_path "${libTKernel}")
    string(REPLACE TKernel "${lib}" lib_path "${lib_path}")
    list(APPEND OpenCASCADE_LIBRARIES "${lib_path}")
endforeach()

if(MSVC)
    add_definitions(-DHAVE_NO_DLL)
    add_debug_variants(OpenCASCADE_LIBRARIES "${OpenCASCADE_LIBRARIES}" d)
endif()

if(WIN32)
    # OCC might require linking to Winsock depending on the version and build configuration
    list(APPEND OpenCASCADE_LIBRARIES ws2_32.lib)
endif()

# Make sure cross-referenced symbols between static OCC libraries get
# resolved. Also add thread and rt libraries.
get_filename_component(libTKernelExt ${libTKernel} EXT)
if("${libTKernelExt}" STREQUAL ".a")
    set(OCCT_STATIC ON)
endif()

if(OCCT_STATIC)
    find_package(Threads)

    if(WASM_BUILD)
        set(OpenCASCADE_LIBRARIES ${OpenCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
    else()
        # OpenCASCADE_LIBRARIES repeated N times below in order to fix cyclic dependencies
        # tfk: --start-group ... --end-group didn't work on the apple linker when last tested
        if(APPLE)
            set(OpenCASCADE_LIBRARIES ${OpenCASCADE_LIBRARIES} ${OpenCASCADE_LIBRARIES} ${OpenCASCADE_LIBRARIES} ${OpenCASCADE_LIBRARIES} ${OpenCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
        else()
            set(OpenCASCADE_LIBRARIES -Wl,--start-group ${OpenCASCADE_LIBRARIES} -Wl,--end-group ${CMAKE_THREAD_LIBS_INIT})
        endif()
    endif()

    if(NOT APPLE AND NOT WIN32)
        set(OpenCASCADE_LIBRARIES ${OpenCASCADE_LIBRARIES} "rt")
    endif()
    if(NOT WIN32)
        set(OpenCASCADE_LIBRARIES ${OpenCASCADE_LIBRARIES} "dl")
    endif()
endif()
