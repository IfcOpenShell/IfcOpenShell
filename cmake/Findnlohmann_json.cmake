#
# Input variables:
# - `JSON_INCLUDE_DIR`
# If input variables are not specified, try to find nlohmann_json config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `nlohmann_json::nlohmann_json`

UNIFY_ENVVARS_AND_CACHE(JSON_INCLUDE_DIR)

if(NOT JSON_INCLUDE_DIR)
    find_package(nlohmann_json ${nlohmann_json_FIND_VERSION} CONFIG)
    mark_as_advanced(nlohmann_json)
    if(nlohmann_json_DIR)
        return()
    endif()
endif()

find_path(json_header_path "nlohmann/json.hpp" HINTS "${JSON_INCLUDE_DIR}")
mark_as_advanced(json_header_path)

if(json_header_path)
    # Multiple headers installations (e.g. conda-forge) keep the version macros in a separate header since 3.11.
    set(json_version_header "${json_header_path}/nlohmann/detail/abi_macros.hpp")
    if(NOT EXISTS "${json_version_header}")
        set(json_version_header "${json_header_path}/nlohmann/json.hpp")
    endif()
    foreach(component MAJOR MINOR PATCH)
        file(STRINGS "${json_version_header}" json_version_line REGEX "^#define NLOHMANN_JSON_VERSION_${component} ")
        # Since 3.11 the macros are followed by a NOLINT comment.
        string(REGEX REPLACE "^#define NLOHMANN_JSON_VERSION_${component} ([0-9]+)([ \t]*//.*)?$" "\\1" json_version_${component} "${json_version_line}")
    endforeach()
    set(nlohmann_json_VERSION "${json_version_MAJOR}.${json_version_MINOR}.${json_version_PATCH}")

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(nlohmann_json
        REQUIRED_VARS json_header_path
        VERSION_VAR nlohmann_json_VERSION
    )

    add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED)
    target_include_directories(nlohmann_json::nlohmann_json INTERFACE ${json_header_path})
    return()
endif()

message(FATAL_ERROR "Unable to find JSON for Modern C++ header file / package, aborting")
