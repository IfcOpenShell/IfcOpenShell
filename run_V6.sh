#!/bin/sh

cmake \
     -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
     -DCMAKE_C_COMPILER_LAUNCHER=ccache \
     -DCMAKE_CXX_FLAGS="-fdata-sections -ffunction-sections -fvisibility=hidden -fvisibility-inlines-hidden -mmacosx-version-min=11.1"\
     -DCMAKE_C_FLAGS="-fdata-sections -ffunction-sections -fvisibility=hidden -mmacosx-version-min=11.1"\
     -DCMAKE_LD_FLAGS="-Wl,--gc-sections -mmacosx-version-min=11.1"\
     -DCMAKE_INSTALL_PREFIX=$PWD/install/ \
     -DCMAKE_BUILD_TYPE=Release \
     -DCMAKE_PREFIX_PATH=/usr \
     -DCMAKE_SYSTEM_PREFIX_PATH=/usr \
     -DBUILD_PACKAGE=On \
     -DOCC_INCLUDE_DIR=/usr/local/include/opencascade \
     -DOCC_LIBRARY_DIR=/usr/local/lib \
÷     -DPYTHON_EXECUTABLE:FILEPATH="/usr/local/opt/python@3.7/bin/python3.7" \
     -DPYTHON_INCLUDE_DIR:PATH="/usr/local/Cellar/python@3.7/3.7.11/Frameworks/Python.framework/Versions/3.7/include/python3.7m" \
     -DPYTHON_LIBRARY:FILEPATH="/usr/local/Cellar/python@3.7/3.7.11/Frameworks/Python.framework/Versions/3.7/lib/libpython3.7m.dylib" \
     -DCOLLADA_SUPPORT=On \
     "-DLIBXML2_INCLUDE_DIR=/usr/local/Cellar/libxml2/2.9.12/include" \
     "-DLIBXML2_LIBRARIES=/usr/local/Cellar/libxml2/2.9.12/lib/libxml2.dylib"\
     -DGLTF_SUPPORT=On\
     -Djson_hpp="/usr/local/Cellar/nlohmann-json/3.9.1_1/include/nlohmann/json.hpp"\
      "-DSCHEMA_VERSIONS=2x3;4"\
     -DJSON_INCLUDE_DIR=/usr/include \
     "-DHDF5_INCLUDE_DIR=/usr/local/Cellar/hdf5/1.12.1/include" \
     -DRapidJSON_INCLUDE_DIRS=/usr/local/Cellar/rapidjson/1.1.0/include  -DRapidJSON_LIBRARY_DIRS=/usr/local/Cellar/rapidjson/1.1.0/lib \
     -DOPENCOLLADA_INCLUDE_DIR="/usr/local/opencollada/include/opencollada/" \
     -DBoost_INCLUDE_DIR="/usr/local/Cellar/boost/1.76.0/include" \
     -DBoost_DIR="/usr/local/lib/cmake/Boost-1.76.0/" \
     -DOPENCOLLADA_LIBRARY_DIR="/usr/local/opencollada/lib/opencollada/" ../cmake
