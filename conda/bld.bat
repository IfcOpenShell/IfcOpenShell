mkdir build && cd build

REM Remove dot from PY_VER for use in library name
REM From https://github.com/tpaviot/pythonocc-core/blob/master/ci/conda/bld.bat
set MY_PY_VER=%PY_VER:.=%

cmake -G "NMake Makefiles" ^
 -DCMAKE_INSTALL_PREFIX="%LIBRARY_PREFIX%" ^
 -DCMAKE_BUILD_TYPE=Release ^
 -DCMAKE_PREFIX_PATH="%LIBRARY_PREFIX%" ^
 -DCMAKE_SYSTEM_PREFIX_PATH="%LIBRARY_PREFIX%" ^
 -DPYTHON_EXECUTABLE="%PYTHON%" ^
 -DPYTHON_INCLUDE_DIR="%PREFIX%"/include ^
 -DPYTHON_LIBRARY="%PREFIX%"/libs/python%MY_PY_VER%.lib ^
 -DBOOST_LIBRARYDIR="%LIBRARY_PREFIX%\lib" ^
 -DBOOST_INCLUDEDIR="%LIBRARY_PREFIX%\include" ^
 -DOCC_INCLUDE_DIR="%LIBRARY_PREFIX%\include\oce" ^
 -DOCC_LIBRARY_DIR="%LIBRARY_PREFIX%\lib" ^
 -DCOLLADA_SUPPORT=Off ^
 -DBUILD_EXAMPLES=Off ^
 -DBUILD_GEOMSERVER=Off ^
 -DBUILD_CONVERT=Off ^
 ../cmake
 
if errorlevel 1 exit 1

cmake --build . --target INSTALL --config Release

if errorlevel 1 exit 1
