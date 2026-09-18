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
    file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_world_line REGEX "^#define EIGEN_WORLD_VERSION")
    file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_major_line REGEX "^#define EIGEN_MAJOR_VERSION")
    file(STRINGS "${EIGEN_DIR}/Eigen/src/Core/util/Macros.h" eigen_version_minor_line REGEX "^#define EIGEN_MINOR_VERSION")
    string(REGEX REPLACE "^#define EIGEN_WORLD_VERSION ([0-9]+)$" "\\1" eigen_version_world "${eigen_version_world_line}")
    string(REGEX REPLACE "^#define EIGEN_MAJOR_VERSION ([0-9]+)$" "\\1" eigen_version_major "${eigen_version_major_line}")
    string(REGEX REPLACE "^#define EIGEN_MINOR_VERSION ([0-9]+)$" "\\1" eigen_version_minor "${eigen_version_minor_line}")
    set(Eigen3_VERSION "${eigen_version_world}.${eigen_version_major}.${eigen_version_minor}")

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(Eigen3
        REQUIRED_VARS EIGEN_DIR
        VERSION_VAR Eigen3_VERSION
    )

    # Mimic Eigen3Config.cmake target.
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    target_include_directories(Eigen3::Eigen INTERFACE "${EIGEN_DIR}")
else()
    find_package(Eigen3 ${Eigen3_FIND_VERSION} CONFIG)
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
