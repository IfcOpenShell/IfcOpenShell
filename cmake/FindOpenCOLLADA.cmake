
#
# Input variables:
# - `OPENCOLLADA_INCLUDE_DIR`
# - `OPENCOLLADA_LIBRARY_DIR`
# - `PCRE_LIBRARY_DIR`
# If input variables are not specified, try to find OpenCOLLADA config.
# Input variables could also be provided as environment variables.
#
# Output variables:
# - `OPENCOLLADA_INCLUDE_DIR`
# - `OPENCOLLADA_LIBRARY_DIR`
# - `OPENCOLLADA_LIBRARIES`
#

UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_INCLUDE_DIR)
UNIFY_ENVVARS_AND_CACHE(OPENCOLLADA_LIBRARY_DIR)
UNIFY_ENVVARS_AND_CACHE(PCRE_LIBRARY_DIR)

if(NOT OPENCOLLADA_INCLUDE_DIR AND NOT OPENCOLLADA_LIBRARY_DIR)
    # If package is found, automatically sets
    # OPENCOLLADA_INCLUDE_DIRS and OPENCOLLADA_LIBRARIES (list of targets, not paths).
    find_package(OpenCOLLADA CONFIG)
    if(OpenCOLLADA_DIR)
        message(STATUS "Found OpenCOLLADA: '${OpenCOLLADA_DIR}'.")
        set(OPENCOLLADA_FOUND TRUE)
    else()
        message(STATUS "OpenCOLLADA package not found, falling back to manual search.")
    endif()
endif()

if(NOT OpenCOLLADA_DIR)
    # Find OpenCOLLADA
    if("${OPENCOLLADA_INCLUDE_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA include directory specified")
        set(OPENCOLLADA_INCLUDE_DIR "/usr/include/opencollada" CACHE FILEPATH "OpenCOLLADA header files")
    else()
        set(OPENCOLLADA_INCLUDE_DIR "${OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
    endif()

    if("${OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA library directory specified")
        find_library(OPENCOLLADA_FRAMEWORK_LIB NAMES OpenCOLLADAFramework
            PATHS /usr/lib64/opencollada /usr/lib/opencollada /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib)
        get_filename_component(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_FRAMEWORK_LIB} PATH)
    endif()

    find_library(OpenCOLLADAFramework NAMES OpenCOLLADAFramework OpenCOLLADAFrameworkd PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)

    if(OpenCOLLADAFramework)
        message(STATUS "OpenCOLLADA library files found")
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA libraries. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()

    set(OPENCOLLADA_LIBRARY_DIR "${OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")

    set(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

    find_file(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})

    if(COLLADASWStreamWriter_h)
        message(STATUS "OpenCOLLADA header files found")
        set(OPENCOLLADA_FOUND TRUE)

        set(OPENCOLLADA_LIBRARY_NAMES
            GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
            OpenCOLLADAStreamWriter UTF buffer ftoa
        )

        # Use the found OpenCOLLADAFramework as a template for all other OpenCOLLADA libraries
        foreach(lib ${OPENCOLLADA_LIBRARY_NAMES})
            # Make sure we'll handle the Windows/MSVC debug postfix convention too.
            string(REPLACE OpenCOLLADAFrameworkd "${lib}" lib_path "${OpenCOLLADAFramework}")
            string(REPLACE OpenCOLLADAFramework "${lib}" lib_path "${lib_path}")
            list(APPEND OPENCOLLADA_LIBRARIES "${lib_path}")
        endforeach()

        if("${PCRE_LIBRARY_DIR}" STREQUAL "")
            if(WIN32)
                find_library(pcre_library NAMES pcre pcred PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)
            else()
                find_library(pcre_library NAMES pcre PATHS ${OPENCOLLADA_LIBRARY_DIR})
            endif()

            get_filename_component(PCRE_LIBRARY_DIR ${pcre_library} PATH)
        else()
            find_library(pcre_library NAMES pcre pcred PATHS ${PCRE_LIBRARY_DIR} NO_DEFAULT_PATH)
        endif()

        if(pcre_library)
            set(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_LIBRARY_DIR} ${PCRE_LIBRARY_DIR})

            if(MSVC)
                # Add release lib regardless whether release or debug found. Debug version will be appended below.
                list(APPEND OPENCOLLADA_LIBRARIES "${PCRE_LIBRARY_DIR}/pcre.lib")
            else()
                list(APPEND OPENCOLLADA_LIBRARIES "${pcre_library}")
            endif()
        else()
            message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find PCRE. "
                "Disable COLLADA_SUPPORT or fix PCRE_LIBRARY_DIR path to proceed.")
        endif()

        if(MSVC)
            add_debug_variants(OPENCOLLADA_LIBRARIES "${OPENCOLLADA_LIBRARIES}" d)
        endif()
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA headers. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()
endif(NOT OpenCOLLADA_DIR)

if(OPENCOLLADA_FOUND)
    add_definitions(-DWITH_OPENCOLLADA)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_OPENCOLLADA)
endif()
