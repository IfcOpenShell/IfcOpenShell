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

INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS} ${ICU_INCLUDE_DIR}
    ${Boost_INCLUDE_DIRS} ${THREEDS_MAX_SDK_HOME}/include
)

# All recent versions of 3ds Max (2014 and newer) are 64-bit only so assume lib/x64 directory
LINK_DIRECTORIES(${LINK_DIRECTORIES} ${IfcOpenShell_BINARY_DIR} ${OCC_LIBRARY_DIR} ${OPENCOLLADA_LIBRARY_DIR}
    ${ICU_LIBRARY_DIR} ${Boost_LIBRARY_DIRS} ${THREEDS_MAX_SDK_HOME}/lib/x64/Release
)

ADD_LIBRARY(IfcMax SHARED IfcMax.h IfcMax.cpp)

# TODO: find the minimal subset of 3dsmax libraries to reference
TARGET_LINK_LIBRARIES(IfcMax ${IFCOPENSHELL_LIBRARIES} Comctl32.lib zlibdll.lib bmm.lib core.lib CustDlg.lib edmodel.lib expr.lib
    flt.lib geom.lib gfx.lib gup.lib imageViewers.lib ManipSys.lib maxnet.lib Maxscrpt.lib
    maxutil.lib MenuMan.lib menus.lib mesh.lib MNMath.lib Paramblk2.lib particle.lib Poly.lib RenderUtil.lib
    tessint.lib viewfile.lib ${OPENCASCADE_LIBRARIES}
)

SET_TARGET_PROPERTIES(IfcMax PROPERTIES SUFFIX ".dli")

INSTALL(TARGETS IfcMax RUNTIME DESTINATION ${BINDIR})
