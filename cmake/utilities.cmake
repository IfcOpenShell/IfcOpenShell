function(get_all_option_flags output_list)
    # Read the contents of the CMakeLists.txt
    file(READ "${CMAKE_SOURCE_DIR}/CMakeLists.txt" cmake_contents)

    # Find all OPTION flags using a regular expression
    string(REGEX MATCHALL "OPTION\\s*\\(\\s*([A-Za-z0-9_]+)" matches "${cmake_contents}")

    # Extract the variable names from the matches
    set(option_flags)
    foreach(match IN LISTS matches)
        string(REGEX REPLACE "OPTION\\s*\\(\\s*([A-Za-z0-9_]+)" "\\1" option_flag "${match}")
        list(APPEND option_flags "${option_flag}")
    endforeach()

    # Return the list of OPTION flags
    set(${output_list} "${option_flags}" PARENT_SCOPE)
endfunction()

function(convert_env_var_to_bool var_name)
    if(DEFINED ENV{${var_name}})
        string(TOUPPER "$ENV{${var_name}}" bool_value)
        if(bool_value STREQUAL "ON" OR bool_value STREQUAL "TRUE" OR bool_value STREQUAL "1")
            set(${var_name} ON CACHE BOOL "${var_name} as boolean" FORCE)
        elseif(bool_value STREQUAL "OFF" OR bool_value STREQUAL "FALSE" OR bool_value STREQUAL "0")
            set(${var_name} OFF CACHE BOOL "${var_name} as boolean" FORCE)
        else()
            # Not a bool, leave it as a string
        endif()
    else()
        # Not defined, leave it as a string
    endif()
endfunction()