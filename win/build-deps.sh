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

###############################################################################
#                                                                             #
# This script installs and builds IfcOpenShell's dependencies using MSYS2     #
#                                                                             #
# Note that this script is currently a very bare-bones implementation         #
#                                                                             #
###############################################################################

set -e

# Set defaults for missing empty environment variables

if [ -z "$IFCOS_NUM_BUILD_PROCS" ]; then
IFCOS_NUM_BUILD_PROCS=$(expr $(sysctl -n hw.ncpu 2> /dev/null || cat /proc/cpuinfo | grep processor | wc -l) + 1)
fi

BUILD_DIR=build-msys
SCRIPT_DIR=`pwd "$0"`

DEPS_DIR="$SCRIPT_DIR/../deps"
[ -d $DEPS_DIR ] || mkdir -p $DEPS_DIR

INSTALL_DIR="$SCRIPT_DIR/../deps-msys-installed"

pacman --noconfirm -S mingw-w64-x86_64-toolchain mingw-w64-x86_64-boost make swig

export PATH=/mingw64/bin/:$PATH

function git_clone_or_pull {
    [ -d $2 ] || git clone $1 $2
    pushd $2
    git pull
    popd
}

function git_clone_and_checkout_revision {
    [ -d $2 ] || git clone $1 $2
    pushd $2
    git checkout $3
    popd
}

# Use a fixed revision in order to prevent introducing breaking changes
git_clone_and_checkout_revision https://github.com/KhronosGroup/OpenCOLLADA.git "$DEPS_DIR/OpenCOLLADA" \
    064a60b65c2c31b94f013820856bc84fb1937cc6
pushd "$DEPS_DIR/OpenCOLLADA"
[ -d $BUILD_DIR ] || mkdir -p $BUILD_DIR
pushd $BUILD_DIR
cmake .. -G "MSYS Makefiles" -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR/OpenCOLLADA"
make -j$IFCOS_NUM_BUILD_PROCS
make install
popd 

git_clone_or_pull https://github.com/tpaviot/oce.git "$DEPS_DIR/oce"
git_clone_or_pull https://github.com/QbProg/oce-win-bundle.git "$DEPS_DIR/oce/oce-win-bundle"
pushd "$DEPS_DIR/oce"
[ -d $BUILD_DIR ] || mkdir -p $BUILD_DIR
pushd $BUILD_DIR
# -DOCE_BUILD_SHARED_LIB=0 
cmake .. -G "MSYS Makefiles" -DOCE_INSTALL_PREFIX="$INSTALL_DIR/oce" -DOCE_TESTING=0
make -j$IFCOS_NUM_BUILD_PROCS
make install
popd 

popd

echo IfcOpenShell dependencies installed and built
