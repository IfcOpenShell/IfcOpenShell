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

# Find QT header files
SET(QT_MIN_VERSION "4.5.0")
FIND_PACKAGE(Qt4 REQUIRED)
FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtOpenGL)

INCLUDE(${QT_USE_FILE})
SET(CMAKE_PACKAGE_QTGUI TRUE)

# Find QT header files
IF("$ENV{QT_INCLUDE_DIR}" STREQUAL "") 
        SET(QT_INCLUDE_DIR "/usr/include/QT4/" CACHE FILEPATH "QT4 header files")
        MESSAGE(STATUS "Looking for QT4 include files in: ${QT_INCLUDE_DIR}")
        MESSAGE(STATUS "Use QT_INCLUDE_DIR to specify another directory")
ELSE()
        SET(QT_INCLUDE_DIR $ENV{QT_INCLUDE_DIR} CACHE FILEPATH "QT4 header files")
        MESSAGE(STATUS "Looking for QT4 include files in: ${QT_INCLUDE_DIR}")
ENDIF()


INCLUDE_DIRECTORIES(${QT_INCLUDE_DIR})

SET(QTviewer_SRCS
        ../../src/qtviewer/mainwindow.h
        ../../src/qtviewer/mainwindow.cpp
        ../../src/qtviewer/main.cpp
)
SET(QTviewer_MOC_SRCS 
        ../../src/qtviewer/mainwindow.h
)

QT_WRAP_CPP(QTviewer QTviewer_SRCS ${QTviewer_MOC_SRCS})

ADD_EXECUTABLE(  QTviewer ${QTviewer_SRCS} ${QTviewer_MOC_SRCS})
#http://www.qtcentre.org/wiki/index.php?title=Compiling_Qt4_apps_with_CMake

TARGET_LINK_LIBRARIES (QTviewer ${IFCLIBS} ${QT_LIBRARIES} ${OPENCASCADE_LIBRARIES})
