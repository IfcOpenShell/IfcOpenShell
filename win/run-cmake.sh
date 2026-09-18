###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

set -e

export PATH=/mingw64/bin/:$PATH

BUILD_DIR=../build-msys
[ -d $BUILD_DIR ] || mkdir -p $BUILD_DIR

CMAKE_INSTALL_PREFIX=../installed-msys

# Keep this in sync with build-deps.sh: when COLLADA_SUPPORT=0 OpenCOLLADA is not
# built, so configure IfcOpenShell without it (IfcConvert still supports glTF).
COLLADA_SUPPORT="${COLLADA_SUPPORT:-1}"
COLLADA_CMAKE_ARGS=""
if [ "$COLLADA_SUPPORT" = "0" ] || [ "$COLLADA_SUPPORT" = "OFF" ] || [ "$COLLADA_SUPPORT" = "off" ]; then
    COLLADA_CMAKE_ARGS="-DCOLLADA_SUPPORT=OFF"
fi

pushd $BUILD_DIR

# PYTHON_INCLUDE_DIR=/mingw64/include/python2.7 \
# PYTHON_LIBRARY=/mingw64/lib/python2.7/config/libpython2.7.a \
OCC_INCLUDE_DIR=`pwd`/../deps-msys-installed/oce/include/oce/ \
OCC_LIBRARY_DIR=`pwd`/../deps-msys-installed/oce/Win64/lib/ \
OPENCOLLADA_INCLUDE_DIR=`pwd`/../deps-msys-installed/OpenCOLLADA/include/opencollada/ \
OPENCOLLADA_LIBRARY_DIR=`pwd`/../deps-msys-installed/OpenCOLLADA/lib/opencollada/ \
cmake -G "MSYS Makefiles" ../cmake -DSWIG_DIR=/usr/bin -DCMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX \
    -DCMAKE_MAKE_PROGRAM=/mingw64/bin/mingw32-make.exe $COLLADA_CMAKE_ARGS $@

popd
