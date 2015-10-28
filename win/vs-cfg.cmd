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

:: This script initializes various Visual Studio -related environment variables needed for building
:: This batch file expects CMake generator as %1 and build configuration type as %2.
:: NOTE: The delayed environment variable expansion needs to be enabled before calling this.

@echo off

:: TOOLS is the path where the Windows build scripts reside.
set TOOLS=%CD%

set GENERATOR=%1

:: TODO IDEA: Take more user-friendly VS generators and convert them to the CMake ones?
:: F.ex. "vs2013-32" and/or "vc14-64"

:: TODO Print CMake and VS versions. Maybe in build-deps.cmd would be better than here.
:: Make CMake missing a fatal error and abort the script.

:: Supported Visual Studio versions:
set GENERATOR_VS2015_32="Visual Studio 14 2015"
set GENERATOR_VS2015_64="Visual Studio 14 2015 Win64"
:: TODO Check CMake version and convert possible new format (>= 3.0) generator names 
:: to the old versions if using older CMake for VS <= 2013,
:: see http://www.cmake.org/cmake/help/v3.0/release/3.0.0.html#other-changes
set GENERATOR_VS2013_32="Visual Studio 12"
set GENERATOR_VS2013_64="Visual Studio 12 Win64"
set GENERATOR_VS2012_32="Visual Studio 11"
set GENERATOR_VS2012_64="Visual Studio 11 Win64"
set GENERATOR_VS2010_32="Visual Studio 10"
set GENERATOR_VS2010_64="Visual Studio 10 Win64"
set GENERATOR_VS2008_32="Visual Studio 9 2008"
set GENERATOR_VS2008_64="Visual Studio 9 2008 Win64"
set GENERATOR_DEFAULT=%GENERATOR_VS2015_64%

IF "!GENERATOR!"=="" (
    set GENERATOR=%GENERATOR_DEFAULT%
    utils\cecho {0E}vs-cfg.cmd: Warning: Generator not passed - using the default %GENERATOR_DEFAULT%.{# #}{\n}
)

IF NOT !GENERATOR!==%GENERATOR_VS2008_32% IF NOT !GENERATOR!==%GENERATOR_VS2008_64% (
IF NOT !GENERATOR!==%GENERATOR_VS2010_32% IF NOT !GENERATOR!==%GENERATOR_VS2010_64% (
IF NOT !GENERATOR!==%GENERATOR_VS2012_32% IF NOT !GENERATOR!==%GENERATOR_VS2012_64% (
IF NOT !GENERATOR!==%GENERATOR_VS2013_32% IF NOT !GENERATOR!==%GENERATOR_VS2013_64% (
IF NOT !GENERATOR!==%GENERATOR_VS2015_32% IF NOT !GENERATOR!==%GENERATOR_VS2015_64% (
    utils\cecho {0C}vs-cfg.cmd: Invalid or unsupported CMake generator string passed: !GENERATOR!. Cannot proceed, aborting!{# #}{\n}
    GOTO :EOF
)))))

:: Figure out the build configuration from the CMake generator string.
:: Are we building 32-bit or 64-bit version.
set ARCH_BITS=32
set TARGET_ARCH=x86
:: Visual Studio platform name, Win32 (i.e. x86) or x64.
set VS_PLATFORM=Win32

:: Split the string for closer inspection.
:: VS_VER and VC_VER are convenience variables used f.ex. for filenames.
set GENERATOR_NO_DOUBLEQUOTES=%GENERATOR:"=%
set GENERATOR_SPLIT=%GENERATOR_NO_DOUBLEQUOTES: =,%
FOR %%i IN (%GENERATOR_SPLIT%) DO (
    IF %%i==14 (
        set VS_VER=2015
        set VC_VER=14
    )
    IF %%i==12 (
        set VS_VER=2013
        set VC_VER=12
    )
    IF %%i==11 (
        set VS_VER=2012
        set VC_VER=11
    )
    IF %%i==10 (
        set VS_VER=2010
        set VC_VER=10
    )
    IF %%i==2008 (
        set VS_VER=2008
        set VC_VER=9
    )
    REM Are going to perform a 64-bit build?
    IF %%i==Win64 (
        set ARCH_BITS=64
        set TARGET_ARCH=x64
        set VS_PLATFORM=x64
    )
)

:: VS project file extension is different on older VS versions
set VCPROJ_FILE_EXT=vcxproj
IF %VS_VER%==2008 set VCPROJ_FILE_EXT=vcproj

:: Set up variables depending on the used build configuration type.
set BUILD_CFG=%2

:: The default build types provided by CMake
set BUILD_CFG_MINSIZEREL=MinSizeRel
set BUILD_CFG_RELEASE=Release
set BUILD_CFG_RELWITHDEBINFO=RelWithDebInfo
set BUILD_CFG_DEBUG=Debug
set BUILD_CFG_DEFAULT=%BUILD_CFG_RELWITHDEBINFO%

IF "!BUILD_CFG!"=="" (
    set BUILD_CFG=%BUILD_CFG_DEFAULT%
    utils\cecho {0E}vs-cfg.cmd: Warning: BUILD_CFG not specified - using the default %BUILD_CFG_DEFAULT%{# #}{\n}
)
IF NOT !BUILD_CFG!==%BUILD_CFG_MINSIZEREL% IF NOT !BUILD_CFG!==%BUILD_CFG_RELEASE% (
IF NOT !BUILD_CFG!==%BUILD_CFG_RELWITHDEBINFO% IF NOT !BUILD_CFG!==%BUILD_CFG_DEBUG% (
    utils\cecho {0C}vs-cfg.cmd: Invalid or unsupported CMake build configuration type passed: !BUILD_CFG!. Cannot proceed, aborting!{# #}{\n}
    exit /b 1
))

:: DEBUG_OR_RELEASE and DEBUG_OR_RELEASE_LOWERCASE are "Debug" and "debug" for Debug build and "Release" and
:: "release" for all of the Release variants.
:: POSTFIX_D, POSTFIX_UNDERSCORE_D and POSTFIX_UNDERSCORE_DEBUG are helpers for performing file copies and
:: checking for existence of files. In release build these variables are empty.
set DEBUG_OR_RELEASE=Release
set DEBUG_OR_RELEASE_LOWERCASE=release
set POSTFIX_D=
set POSTFIX_UNDERSCORE_D=
set POSTFIX_UNDERSCORE_DEBUG=
IF %BUILD_CFG%==Debug (
    set DEBUG_OR_RELEASE=Debug
    set DEBUG_OR_RELEASE_LOWERCASE=debug
    set POSTFIX_D=d
    set POSTFIX_UNDERSCORE_D=_d
    set POSTFIX_UNDERSCORE_DEBUG=_debug
)

:: Populate path variables
cd ..\
set ORIGINAL_PATH=%PATH%
set PATH=%PATH%;"%CD%\win\utils"

:: Fetch and build the dependencies to a dedicated directory depending on the used VS version and target architecture.
:: NOTE For IfcOpenShell we can build all of our deps both x86 and x64 using different VS versions in the same directories
:: so no need for -%VS_VER%-%TARGET_ARCH% postfix.
:: set DEPS_DIR=%CD%\deps-%VS_VER%-%TARGET_ARCH%
set DEPS_DIR=%CD%\deps
set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-installed
REM set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-%DEBUG_OR_RELEASE_LOWERCASE%-installed
cd %TOOLS%
