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

# check for 3ds Max SDK
set(valid_max_years 2026 2025 2024 2023 2022 2021 2020 2019 2018 2017)

set(max_toolset_versions_143 "2025" "2026" )
set(max_toolset_versions_142 "2022" "2023" "2024" )
set(max_toolset_versions_141 "2020" "2021" )
set(max_toolset_versions_140 "2017" "2018" "2019" ) 
# set(max_toolset_versions_110 "2015" "2016" ) 
# set(max_toolset_versions_100 "2013" "2014" ) 
# set(max_toolset_versions_90  "2010" "2011" "2012" ) 

foreach(max_year ${valid_max_years})
    set(max_sdk "$ENV{ADSK_3DSMAX_SDK_${max_year}}")
    if(NOT "${max_sdk}" STREQUAL "")
        message(STATUS "Autodesk 3ds Max SDK ${max_year} found at ${max_sdk}")
        list(APPEND FOUND_MAX_YEARS ${max_year})
        list(APPEND FOUND_MAX_SDKS ${max_sdk})
        set(HAS_MAX TRUE)
    endif()
endforeach()

message(STATUS)

if(HAS_MAX)
	# set depenency include and link directoris outside of MaxSDK loop
	include_directories(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS} ${ICU_INCLUDE_DIR} ${Boost_INCLUDE_DIRS} )
	link_directories(${LINK_DIRECTORIES} ${IfcOpenShell_BINARY_DIR} ${OCC_LIBRARY_DIR} ${OPENCOLLADA_LIBRARY_DIR} ${ICU_LIBRARY_DIR} ${Boost_LIBRARY_DIRS} )

    # build library for each found 3ds Max SDK
    foreach(max_year max_sdk IN ZIP_LISTS FOUND_MAX_YEARS FOUND_MAX_SDKS)

		# skip 3ds Max versions that do not match the vs toolset
		if( NOT ${max_year} IN_LIST max_toolset_versions_${MSVC_TOOLSET_VERSION} )
			continue()
		endif()

        message(STATUS "Adding build target: IFCMax for 3ds Max SDK ${max_year}")

        add_library(IfcMax_${max_year} SHARED IfcMax.h IfcMax.cpp)

		target_include_directories(IfcMax_${max_year} PRIVATE ${max_sdk}/include)
		
		# All recent versions of 3ds Max (2014 and newer) are 64-bit only so assume lib/x64 directory
		target_link_directories(IfcMax_${max_year} PRIVATE ${max_sdk}/lib/x64/Release)

        # TODO: find the minimal subset of 3dsmax libraries to reference
        target_link_libraries(IfcMax_${max_year} ${IFCOPENSHELL_LIBRARIES}
            bmm.lib
            Comctl32.lib
            core.lib
            CustDlg.lib
            edmodel.lib
            expr.lib
            flt.lib
            geom.lib
            gfx.lib
            gup.lib
            imageViewers.lib
            ManipSys.lib
            maxnet.lib
            Maxscrpt.lib
            maxutil.lib
            mesh.lib
            MNMath.lib
            Paramblk2.lib
            particle.lib
            Poly.lib
            RenderUtil.lib
            tessint.lib
            viewfile.lib
            ${OPENCASCADE_LIBRARIES}
        )	
	
		# Note: libraries build by same major vs toolset versions are binary compatible. so v14x builds can be intermixed
		# Older Max versions using v110 or older require dependencies being build using the according toolset version ( most likely )
		if( ${max_year} IN_LIST max_toolset_versions_143 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v143)		
		elseif( ${max_year} IN_LIST max_toolset_versions_142 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v142)
		elseif( ${max_year} IN_LIST max_toolset_versions_141 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v141)
		elseif( ${max_year} IN_LIST max_toolset_versions_140 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v140)
		elseif( ${max_year} IN_LIST max_toolset_versions_110 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v110)
		elseif( ${max_year} IN_LIST max_toolset_versions_100 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v100)
		elseif( ${max_year} IN_LIST max_toolset_versions_90 )
			set_target_properties( IfcMax_${max_year} PROPERTIES VS_PLATFORM_TOOLSET v90)
		endif()
		
		# fix 3ds Max 2020 SDK's "/permissive-" flag incompatibility / disables C++ language conformance mode
		if( ${max_year} EQUAL 2020 )
			set_source_files_properties( "IfcMax.cpp" PROPERTIES COMPILE_FLAGS "/permissive")
		endif()
		
		# C++17 required for 3ds Max SDK 2025 and higher
		if( ${max_year} GREATER_EQUAL 2025 )
			set_target_properties(IfcMax_${max_year} PROPERTIES CXX_STANDARD 17)
		endif()
		
        set_target_properties(IfcMax_${max_year} PROPERTIES SUFFIX ".dli")
		
		
        install(TARGETS IfcMax_${max_year} RUNTIME DESTINATION ${BINDIR})
		
    endforeach()
	message(STATUS)
else()
    message(STATUS "Autodesk 3ds Max SDK not found, is required to build IFCMax.")
endif()

