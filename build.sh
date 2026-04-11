#!/bin/sh
set -e

mkdir -p build && cd build

cmake ../cmake \
  -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DPython_EXECUTABLE=/home/dion/Projects/env/bin/python3.11 \
  -DPython_INCLUDE_DIR=/usr/include/python3.11 \
  -DBUILD_IFCPYTHON=ON \
  -DBUILD_IFCGEOM=ON \
  -DBUILD_CONVERT=ON \
  -DBUILD_GEOMSERVER=OFF \
  -DBUILD_EXAMPLES=OFF \
  -DWITH_OPENCASCADE=ON \
  -DWITH_CGAL=ON \
  -DWITH_MANIFOLD=ON \
  -DHDF5_SUPPORT=OFF \
  -DGLTF_SUPPORT=ON \
  -DIFCXML_SUPPORT=OFF \
  -DCOLLADA_SUPPORT=OFF \
  -DSCHEMA_VERSIONS="2x3;4;4x3_add2" \
  -DOCC_INCLUDE_DIR=/usr/include/opencascade \
  -DOCC_LIBRARY_DIR=/usr/lib64/opencascade

ninja

cp ifcwrap/_ifcopenshell_wrapper*.so ifcwrap/ifcopenshell_wrapper.py \
   ../src/ifcopenshell-python/ifcopenshell/
