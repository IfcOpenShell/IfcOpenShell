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
::::::::::::::::::::::::::::::::::::::::::::::::::::::: ::::::::::::::::::::::::::

:: This script initializes various Visual Studio related environment variables needed for building.
:: the dependencies. This batch file expects a CMake generator as %1. If %1 is not provided, it is
:: deduced from the VisualStudioVersion environment variable and from the location of cl.exe.
:: User-friendly VS generators are allowed (e.g. "vs2013-x86") and converted to the appropriate CMake ones.

:: NOTE This batch file expects the generator string to be CMake 3.0.0 and newer format, i.e.
:: "Visual Studio 10 2010" instead of "Visual Studio 10". However, one can use this batch file
:: also with CMake 2 as the generator will be converted into the older format if necessary.

:: NOTE: The delayed environment variable expansion needs to be enabled before calling this.

@echo off

set GENERATOR=%1

:: Supported Visual Studio versions:
set GENERATORS[0]="Visual Studio 9 2008 Win64"
set GENERATORS[1]="Visual Studio 9 2008"
set GENERATORS[2]="Visual Studio 10 2010 Win64"
set GENERATORS[3]="Visual Studio 10 2010"
set GENERATORS[4]="Visual Studio 11 2012 Win64"
set GENERATORS[5]="Visual Studio 11 2012"
set GENERATORS[6]="Visual Studio 12 2013 Win64"
set GENERATORS[7]="Visual Studio 12 2013"
set GENERATORS[8]="Visual Studio 14 2015 Win64"
set GENERATORS[9]="Visual Studio 14 2015"
:: NOTE VC version for VS 2017 is not 15 but 14.1: have to wait and see
:: if CMake generator string is updated to reflect this.
set GENERATORS[10]="Visual Studio 15 2017 Win64"
set GENERATORS[11]="Visual Studio 15 2017"
set LAST_GENERATOR_IDX=11

set STEP=2
:: Is generator shorthand used?
set GEN_SHORTHAND=!GENERATOR:vs=!
if not "!GEN_SHORTHAND!"=="" if !GEN_SHORTHAND!==!GENERATOR! goto :GeneratorShorthandCheckDone
set START=%LAST_GENERATOR_IDX%
:: "echo if" trick from http://stackoverflow.com/a/8758579
echo(!GEN_SHORTHAND! | findstr /c:"-x86" >nul && ( set START=1 )
echo(!GEN_SHORTHAND! | findstr /c:"-x64" >nul && ( set START=0 )
set VS_VER=!GEN_SHORTHAND:-x86=!
set VS_VER=!VS_VER:-x64=!
echo(!GENERATOR! | findstr /c:"vs20" >nul && (
    for /l %%i in (!START!,!STEP!,%LAST_GENERATOR_IDX%) do (
        echo(!GENERATORS[%%i]! | findstr /c:"!VS_VER!" >nul && (
            set GENERATOR=!GENERATORS[%%i]!
            goto :GeneratorShorthandCheckDone
        )
    )
)
:GeneratorShorthandCheckDone

:: Deduce desired architecture from the location of cl.exe
:: TODO harmless "INFO: Could not find files for the given pattern(s)." spam if cl.exe not in path
:: Look for path with either "amd64" or "x64" (VS 2017 and newer)
where cl.exe | findstr "amd64 x64" >nul
set START=%ERRORLEVEL%

IF "!GENERATOR!"=="" IF NOT "%VisualStudioVersion%"=="" (
    set VC_VER=%VisualStudioVersion:.0=%
    FOR /l %%i in (%START%,%STEP%,%LAST_GENERATOR_IDX%) DO (
        REM NOTE add space before VC_VER so that e.g. "12" doesn't match with "2012"
        echo(!GENERATORS[%%i]! | findstr /c:" !VC_VER!" >nul && (
            set GENERATOR=!GENERATORS[%%i]!
            call utils\cecho.cmd black cyan "Generator not passed, but VisualStudioVersion=%VisualStudioVersion% environment variable detected:"
            call utils\cecho.cmd black cyan "using '`"!GENERATOR!`'" as the generator."
            GOTO :GeneratorValid
        )
    )
)
:: Check that the used CMake version supports the chosen generator
set GENERATOR_CHECK=%GENERATOR: Win64=%
cmake --help | findstr /c:%GENERATOR_CHECK% >nul
if not %ERRORLEVEL%==0 (
call utils\cecho.cmd 0 12 "%~nx0: The used CMake version does not support '`"!GENERATOR!`'"- cannot proceed."
exit /b 1
)

FOR /l %%i in (0,1,%LAST_GENERATOR_IDX%) DO (
    IF !GENERATOR!==!GENERATORS[%%i]! GOTO :GeneratorValid
)
call utils\cecho.cmd 0 12 "%~nx0: Invalid or unsupported CMake generator string passed: '`"!GENERATOR!`'"- cannot proceed."
echo Supported CMake generator strings:
FOR /l %%i in (0,1,%LAST_GENERATOR_IDX%) DO (
    echo !GENERATORS[%%i]!
)
exit /b 1

:GeneratorValid
:: Figure out the build configuration from the CMake generator string.
:: Are we building 32-bit or 64-bit version.
set ARCH_BITS=32
set TARGET_ARCH=x86
:: Visual Studio platform name, Win32 (i.e. x86) or x64.
set VS_PLATFORM=Win32

:: Find out VS (e.g. 2015) and VC (e.g. 14) versions and are we targeting x64 or not (x86).
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

:: Check CMake version and convert possible new format (>= 3.0) generator names to the old versions if using older CMake for VS <= 2013,
:: see http://www.cmake.org/cmake/help/v3.0/release/3.0.0.html#other-changes
FOR /f "delims=" %%i in ('where cmake') DO set CMAKE_PATH=%%i
IF NOT "%CMAKE_PATH%"=="" (
    FOR /f "delims=" %%i in ('cmake --version ^| findstr /C:"cmake version 3"') DO GOTO :CMake3AndNewer
)
:: CMake older than 3.0.0: convert new format generators to the old format (simple brute force for simplicity)
set GENERATOR=%GENERATOR: 2013=%
set GENERATOR=%GENERATOR: 2012=%
set GENERATOR=%GENERATOR: 2010=%
:CMake3AndNewer

set GEN_SHORTHAND=vs%VS_VER%-%TARGET_ARCH%
:: VS project file extension is different on older VS versions
set VCPROJ_FILE_EXT=vcxproj
IF %VS_VER%==2008 set VCPROJ_FILE_EXT=vcproj

:: Add utils to PATH
set ORIGINAL_PATH=%PATH%
set PATH=%~dp0utils;%PATH%

:: Fetch and build the dependencies to a dedicated directory depending on the used VS version and target architecture.
:: NOTE For IfcOpenShell we can build all of our deps both x86 and x64 using different VS versions in the same directories
:: so no need for -%VS_VER%-%TARGET_ARCH% postfix.
:: set DEPS_DIR=%CD%\deps-%VS_VER%-%TARGET_ARCH%
pushd ..
set DEPS_DIR=%CD%\deps
set INSTALL_DIR=%CD%\deps-%GEN_SHORTHAND%-installed
REM set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-%DEBUG_OR_RELEASE_LOWERCASE%-installed
:: BUILD_DIR is a relative build directory used for CMake-based projects
set BUILD_DIR=build-%GEN_SHORTHAND%
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
