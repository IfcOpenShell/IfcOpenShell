mkdir build && cd build

cmake \
 -DCMAKE_INSTALL_PREFIX=$PREFIX \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH=$PREFIX \
 -DCMAKE_SYSTEM_PREFIX_PATH=$PREFIX \
 -DOCC_INCLUDE_DIR=$PREFIX/include/oce \
 -DOCC_LIBRARY_DIR=$PREFIX/lib \
 -DCOLLADA_SUPPORT=Off \
 ../cmake

make -j$CPU_COUNT _ifcopenshell_wrapper
cd ifcwrap
make install/local
