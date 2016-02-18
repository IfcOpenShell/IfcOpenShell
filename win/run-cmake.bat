:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::                                                                             ::
:: This file is part of IfcOpenShell.                                          ::
::                                                                             ::
:: IfcOpenShell is free software: you can redistribute it and/or modify        ::
:: it under the terms of the Lesser GNU General Public License as published by ::
:: the Free Software Foundation, either version 3.0 of the License, or         ::
:: (at your option) any later version.                                         ::
::                                                                             ::
:: IfcOpenShell is distributed in the hope that it will be useful,             ::
:: but WITHOUT ANY WARRANTY; without even the implied warranty of              ::
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                ::
:: Lesser GNU General Public License for more details.                         ::
::                                                                             ::
:: You should have received a copy of the Lesser GNU General Public License    ::
:: along with this program. If not, see <http://www.gnu.org/licenses/>.        ::
::                                                                             ::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

@echo off
echo.

set PROJECT_NAME=IfcOpenShell

setlocal EnableDelayedExpansion

call vs-cfg.cmd %1
IF NOT %ERRORLEVEL%==0 GOTO :Error
:: As CMake options are typically of format -DSOMETHING:BOOL=ON or -DSOMETHING=1, i.e. they contain an equal sign,
:: they will mess up the batch file argument parsing if the arguments are passed on by splitting them %2 %3 %4 %5
:: %6 %7 %8 %9. Work around that, http://scripts.dragon-it.co.uk/scripts.nsf/docs/batch-search-replace-substitute
if not (%1)==() (
    set ARGUMENTS=%*
    call set ARGUMENTS=%%ARGUMENTS:%1=%%
)

:: Read Python related variables from BuildDepsCache.txt
for /f "delims== tokens=1,2" %%G in (BuildDepsCache-%TARGET_ARCH%.txt) do set %%G=%%H

pushd ..
set CMAKE_INSTALL_PREFIX=%CD%\installed-vs%VS_VER%-%TARGET_ARCH%
popd

IF NOT EXIST ..\%BUILD_DIR%. mkdir ..\%BUILD_DIR%
pushd ..\%BUILD_DIR%

set BOOST_ROOT=%DEPS_DIR%\boost
set BOOST_LIBRARYDIR=%DEPS_DIR%\boost\stage\vs%VS_VER%-%VS_PLATFORM%\lib
set ICU_INCLUDE_DIR=%INSTALL_DIR%\icu\include
set ICU_LIBRARY_DIR=%INSTALL_DIR%\icu\lib
set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce
set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib
set OPENCOLLADA_INCLUDE_DIR=%INSTALL_DIR%\OpenCOLLADA\include\opencollada
set OPENCOLLADA_LIBRARY_DIR=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada
if not defined PY_VER_MAJOR_MINOR set PY_VER_MAJOR_MINOR=34
if not defined PYTHONHOME set PYTHONHOME=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%
set PYTHON_INCLUDE_DIR=%PYTHONHOME%\include
set PYTHON_LIBRARY=%PYTHONHOME%\libs\python%PY_VER_MAJOR_MINOR%.lib
set PYTHON_EXECUTABLE=%PYTHONHOME%\python.exe
set SWIG_DIR=%INSTALL_DIR%\swigwin
set PATH=%PATH%;%SWIG_DIR%;%PYTHONHOME%
:: TODO 3ds Max SDK?

echo.
call cecho.cmd 0 10 "Script configuration:"
echo   Generator = %GENERATOR%
echo   Arguments = %ARGUMENTS%
echo.
call cecho.cmd 0 10 "Dependency Environment Variables for %PROJECT_NAME%:"
echo    BOOST_ROOT              = %BOOST_ROOT%
echo    BOOST_LIBRARYDIR        = %BOOST_LIBRARYDIR%
echo    ICU_INCLUDE_DIR         = %ICU_INCLUDE_DIR%
echo    ICU_LIBRARY_DIR         = %ICU_LIBRARY_DIR%
echo    OCC_INCLUDE_DIR         = %OCC_INCLUDE_DIR%
echo    OCC_LIBRARY_DIR         = %OCC_LIBRARY_DIR%
echo    OPENCOLLADA_INCLUDE_DIR = %OPENCOLLADA_INCLUDE_DIR%
echo    OPENCOLLADA_LIBRARY_DIR = %OPENCOLLADA_LIBRARY_DIR%
echo    PYTHONHOME              = %PYTHONHOME%
echo    PYTHON_INCLUDE_DIR      = %PYTHON_INCLUDE_DIR%
echo    PYTHON_LIBRARY          = %PYTHON_LIBRARY%
echo    PYTHON_EXECUTABLE       = %PYTHON_EXECUTABLE%
echo    SWIG_DIR                = %SWIG_DIR%
echo.
echo    CMAKE_INSTALL_PREFIX    = %CMAKE_INSTALL_PREFIX%
echo.

set CMAKELISTS_DIR=..\cmake
:: For now clear CMakeCache.txt always in order to assure that when changing build options everything goes smoothly.
IF EXIST CMakeCache.txt. del /Q CMakeCache.txt
call cecho.cmd 0 13 "Running CMake for %PROJECT_NAME%."
cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%" %ARGUMENTS%
IF NOT %ERRORLEVEL%==0 GOTO :Error

echo.

set IFCOS_SCRIPT_RET=0
goto :Finish

:Error
echo.
call %~dp0\utils\cecho.cmd 0 12 "An error occurred! Aborting!"
set IFCOS_SCRIPT_RET=1
goto :Finish

:Finish
popd
exit /b %IFCOS_SCRIPT_RET%
