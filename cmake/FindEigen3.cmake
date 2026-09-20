#
# Input variables:
# - `EIGEN_DIR`
# If input variables are not specified, try to find Eigen3 config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `Eigen3::Eigen`

UNIFY_ENVVARS_AND_CACHE(EIGEN_DIR)

if(EXISTS "${EIGEN_DIR}")
    if(EXISTS "${EIGEN_DIR}/Eigen/Version")
        # Eigen 5 moved the version macros out of Macros.h. The version is now
        # MAJOR.MINOR.PATCH, EIGEN_WORLD_VERSION is left at 3 for compatibility.
        file(STRINGS "${EIGEN_DIR}/Eigen/Version" eigen_version_major_line REGEX "^#define EIGEN_MAJOR_VERSION")
        file(STRINGS "${EIGEN_DIR}/Eigen/Version" eigen_version_minor_line REGEX "^#define EIGEN_MINOR_VERSION")
        file(STRINGS "${EIGEN_DIR}/Eigen/Version" eigen_version_patch_line REGEX "^#define EIGEN_PATCH_VERSION")
        string(REGEX REPLACE "^#define EIGEN_MAJOR_VERSION ([0-9]+)$" "\\1" eigen_version_major "${eigen_version_major_line}")
        string(REGEX REPLACE "^#define EIGEN_MINOR_VERSION ([0-9]+)$" "\\1" eigen_version_minor "${eigen_version_minor_line}")
        string(REGEX REPLACE "^#define EIGEN_PATCH_VERSION ([0-9]+)$" "\\1" eigen_version_patch "${eigen_version_patch_line}")
        set(Eigen3_VERSION "${eigen_version_major}.${eigen_version_minor}.${eigen_version_patch}")
    else()
        file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_world_line REGEX "^#define EIGEN_WORLD_VERSION")
        file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_major_line REGEX "^#define EIGEN_MAJOR_VERSION")
        file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_minor_line REGEX "^#define EIGEN_MINOR_VERSION")
        string(REGEX REPLACE "^#define EIGEN_WORLD_VERSION ([0-9]+)$" "\\1" eigen_version_world "${eigen_version_world_line}")
        string(REGEX REPLACE "^#define EIGEN_MAJOR_VERSION ([0-9]+)$" "\\1" eigen_version_major "${eigen_version_major_line}")
        string(REGEX REPLACE "^#define EIGEN_MINOR_VERSION ([0-9]+)$" "\\1" eigen_version_minor "${eigen_version_minor_line}")
        set(Eigen3_VERSION "${eigen_version_world}.${eigen_version_major}.${eigen_version_minor}")
    endif()

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(Eigen3
        REQUIRED_VARS EIGEN_DIR
        VERSION_VAR Eigen3_VERSION
    )

    # Mimic Eigen3Config.cmake target.
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    target_include_directories(Eigen3::Eigen INTERFACE "${EIGEN_DIR}")
else()
    # Eigen3ConfigVersion.cmake only accepts a request with the same major version as the
    # installed Eigen, and version ranges don't get around that. Eigen went from 3.4 straight
    # to 5.0, so a request for 3.x rejects an installed 5.x. Try the requested version first,
    # then the 5.x series.
    find_package(Eigen3 ${Eigen3_FIND_VERSION} CONFIG QUIET)
    if(NOT Eigen3_DIR AND "${Eigen3_FIND_VERSION}" VERSION_LESS 5.0)
        find_package(Eigen3 5.0 CONFIG QUIET)
    endif()
    if(Eigen3_DIR)
        message(STATUS "Eigen3: found config at '${Eigen3_DIR}'.")
    else()
        message(
            FATAL_ERROR
            "EIGEN_DIR is not provided or provided folder doesn't exist (current value: '${EIGEN_DIR}'). "
            "Also couldn't find Eigen3 as a package."
        )
    endif()
endif()
