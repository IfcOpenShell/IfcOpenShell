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

get_property(IFCOPENSHELL_LIBRARIES GLOBAL PROPERTY IFCOPENSHELL_LIBRARIES)
message(STATUS "examples IFCOPENSHELL_LIBRARIES: ${IFCOPENSHELL_LIBRARIES}")

if(SCHEMA_VERSIONS MATCHES "2x3")
    add_executable(IfcParseExamples IfcParseExamples.cpp)
    target_link_libraries(IfcParseExamples IfcParse)
    set_target_properties(IfcParseExamples PROPERTIES FOLDER Examples)
    target_compile_features(IfcParseExamples PUBLIC cxx_std_17)

    if(WITH_OPENCASCADE)
        add_executable(IfcOpenHouse IfcOpenHouse.cpp)
        target_link_libraries(IfcOpenHouse IfcParse ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES})
        set_target_properties(IfcOpenHouse PROPERTIES FOLDER Examples)

        ADD_EXECUTABLE(IfcAdvancedHouse IfcAdvancedHouse.cpp)
        TARGET_LINK_LIBRARIES(IfcAdvancedHouse ${IFCOPENSHELL_LIBRARIES} ${OPENCASCADE_LIBRARIES})
        set_target_properties(IfcAdvancedHouse PROPERTIES FOLDER Examples)

    endif()
endif()

if(SCHEMA_VERSIONS MATCHES "4x3")
    ADD_EXECUTABLE(IfcAlignment IfcAlignment.cpp)
    TARGET_LINK_LIBRARIES(IfcAlignment ${IFCOPENSHELL_LIBRARIES})
    set_target_properties(IfcAlignment PROPERTIES FOLDER Examples)

    ADD_EXECUTABLE(IfcSimplifiedAlignment IfcSimplifiedAlignment.cpp)
    TARGET_LINK_LIBRARIES(IfcSimplifiedAlignment ${IFCOPENSHELL_LIBRARIES})
    set_target_properties(IfcSimplifiedAlignment PROPERTIES FOLDER Examples)
endif()
