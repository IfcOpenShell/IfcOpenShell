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

set GENERATOR=%1

:: TODO IDEA: Take more user-friendly VS generators and convert them to the CMake ones?
:: F.ex. "vs2013-32" and/or "vc14-64"

:: TODO Print CMake and VS versions. Maybe in build-deps.cmd would be better than here.

:: Supported Visual Studio versions:
set GENERATORS[0]="Visual Studio 14 2015"
set GENERATORS[1]="Visual Studio 14 2015 Win64"
:: TODO Check CMake version and convert possible new format (>= 3.0) generator names 
:: to the old versions if using older CMake for VS <= 2013,
:: see http://www.cmake.org/cmake/help/v3.0/release/3.0.0.html#other-changes
set GENERATORS[2]="Visual Studio 12 2013"
set GENERATORS[3]="Visual Studio 12 2013 Win64"
set GENERATORS[4]="Visual Studio 11 2012"
set GENERATORS[5]="Visual Studio 11 2012 Win64"
set GENERATORS[6]="Visual Studio 10 2010"
set GENERATORS[7]="Visual Studio 10 2010 Win64"
set GENERATORS[8]="Visual Studio 9 2008"
set GENERATORS[9]="Visual Studio 9 2008 Win64"
set GENERATOR_DEFAULT=%GENERATORS[1]%

IF "!GENERATOR!"=="" (
    set GENERATOR=%GENERATOR_DEFAULT%
    call utils\cecho.cmd 0 14 "%~nx0: Warning: Generator not passed - using the default '`"%GENERATOR_DEFAULT%`'`t
)

FOR /l %%i in (0,1,9) DO (
    IF !GENERATOR!==!GENERATORS[%%i]! GOTO :GeneratorValid
)
call utils\cecho.cmd 0 12 "%~nx0: Invalid or unsupported CMake generator string passed: '`"!GENERATOR!`'". Cannot proceed, aborting!"
exit /b 1

:GeneratorValid
:: Figure out the build configuration from the CMake generator string.
:: Are we building 32-bit or 64-bit version.
set ARCH_BITS=32
set TARGET_ARCH=x86
:: Visual Studio platform name, Win32 (i.e. x86) or x64.
set VS_PLATFORM=Win32

:: Find out VS version, VC versions and are we doing 64-bit or not.
:: VS_VER and VC_VER are convenience variables used f.ex. for filenames.
set GENERATOR_NO_DOUBLEQUOTES=%GENERATOR:"=%
set GENERATOR_SPLIT=%GENERATOR_NO_DOUBLEQUOTES: =,%
FOR %%i IN (%GENERATOR_SPLIT%) DO (
    call :StrLength LEN %%i
    IF !LEN!==1 set VC_VER=%%i
    IF !LEN!==2 set VC_VER=%%i
    IF !LEN!==4 set VS_VER=%%i
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
    call utils\cecho.cmd 0 14 "%~nx0: Warning: BUILD_CFG not specified - using the default %BUILD_CFG_DEFAULT%"
)
IF NOT !BUILD_CFG!==%BUILD_CFG_MINSIZEREL% IF NOT !BUILD_CFG!==%BUILD_CFG_RELEASE% (
IF NOT !BUILD_CFG!==%BUILD_CFG_RELWITHDEBINFO% IF NOT !BUILD_CFG!==%BUILD_CFG_DEBUG% (
    call utils\cecho.cmd 0 12 "%~nx0: Invalid or unsupported CMake build configuration type passed: !BUILD_CFG!. Cannot proceed, aborting!"
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

:: Add utils to PATH
set ORIGINAL_PATH=%PATH%
set PATH=%PATH%;%~dp0\utils

:: Fetch and build the dependencies to a dedicated directory depending on the used VS version and target architecture.
:: NOTE For IfcOpenShell we can build all of our deps both x86 and x64 using different VS versions in the same directories
:: so no need for -%VS_VER%-%TARGET_ARCH% postfix.
:: set DEPS_DIR=%CD%\deps-%VS_VER%-%TARGET_ARCH%
pushd ..
set DEPS_DIR=%CD%\deps
set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-installed
REM set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-%DEBUG_OR_RELEASE_LOWERCASE%-installed
popd

GOTO :EOF
:: http://geekswithblogs.net/SoftwareDoneRight/archive/2010/01/30/useful-dos-batch-functions-substring-and-length.aspx
:StrLength
set #=%2%
set length=0
:stringLengthLoop
if defined # (set #=%#:~1%&set /A length += 1&goto stringLengthLoop)
::echo the string is %length% characters long!
set "%~1=%length%"
GOTO :EOF