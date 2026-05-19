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
    # Mimic Eigen3Config.cmake target.
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    target_include_directories(Eigen3::Eigen INTERFACE "${EIGEN_DIR}")
else()
    find_package(Eigen3 CONFIG)
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
