# From https://github.com/tpaviot/pythonocc-core/blob/master/ci/conda/build.sh
if [ "$PY3K" == "1" ]; then
    MY_PY_VER="${PY_VER}m"
else
    MY_PY_VER="${PY_VER}"
fi

if [ `uname` == Darwin ]; then
    PY_LIB="libpython${MY_PY_VER}.dylib"
else
    PY_LIB="libpython${MY_PY_VER}.so"
fi

mkdir build && cd build

cmake \
 -DCMAKE_INSTALL_PREFIX=$PREFIX \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH=$PREFIX \
 -DCMAKE_SYSTEM_PREFIX_PATH=$PREFIX \
 -DOCC_INCLUDE_DIR=$PREFIX/include/oce \
 -DOCC_LIBRARY_DIR=$PREFIX/lib \
 -DPYTHON_EXECUTABLE:FILEPATH=$PYTHON \
 -DPYTHON_INCLUDE_DIR:PATH=$PREFIX/include/python$MY_PY_VER \
 -DPYTHON_LIBRARY:FILEPATH=$PREFIX/lib/${PY_LIB} \
 -DCOLLADA_SUPPORT=Off \
 ../cmake

make -j$CPU_COUNT _ifcopenshell_wrapper
cd ifcwrap
make install/local
