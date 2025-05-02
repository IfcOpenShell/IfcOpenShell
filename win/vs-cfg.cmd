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

:: This script initializes various Visual Studio related environment variables.
::
:: It expects a CMake generator as %1. If %1 is not provided, it is deduced from
:: the VisualStudioVersion environment variable and from the location of cl.exe.
::
:: The generator string must be in the CMake 3.0 and newer format, i.e.
:: "Visual Studio 12 2013" instead of "Visual Studio 12"
::
:: User-friendly VS generators are preferred, since they permit a more accurate
:: platform and toolset configuration. Some examples:
::
::   "vs2013"             => cmake -G "Visual Studio 12 2013" -A Win32
::   "vs2013-x86"         => cmake -G "Visual Studio 12 2013" -A Win32
::   "vs2015-x64"         => cmake -G "Visual Studio 14 2015" -A x64
::   "vs2017-ARM64"       => cmake -G "Visual Studio 15 2017" -A ARM64
::   "vs2019-x86-v141_xp" => cmake -G "Visual Studio 16 2019" -A Win32 -T v141_xp
::
:: NOTE: The delayed environment variable expansion needs to be enabled before calling this.

@echo off

set GENERATOR=%1

:: Supported Visual Studio versions:
set GENERATORS[1]="Visual Studio 12 2013"
set GENERATORS[2]="Visual Studio 14 2015"
set GENERATORS[3]="Visual Studio 15 2017"
set GENERATORS[4]="Visual Studio 16 2019"
set GENERATORS[5]="Visual Studio 17 2022"
set LAST_GENERATOR_IDX=5

:: Is generator shorthand used?
set GEN_SHORTHAND=!GENERATOR:vs=!

if not "!GEN_SHORTHAND!"=="" if !GEN_SHORTHAND!==!GENERATOR! goto :GeneratorShorthandCheckDone

set "VS_PLATFORM=Win32"
:: use the command prompt target platform, at least initially
if "%VSCMD_ARG_TGT_ARCH%"=="x86" set "VS_PLATFORM=Win32"
if "%VSCMD_ARG_TGT_ARCH%"=="x64" set "VS_PLATFORM=x64"
if "%VSCMD_ARG_TGT_ARCH%"=="arm" set "VS_PLATFORM=ARM"
if "%VSCMD_ARG_TGT_ARCH%"=="arm64" set "VS_PLATFORM=ARM64"

:: "echo if" trick from http://stackoverflow.com/a/8758579
echo(!GEN_SHORTHAND! | findstr /c:"-x86"     >nul && ( set "VS_PLATFORM=Win32" )
echo(!GEN_SHORTHAND! | findstr /c:"-x64"     >nul && ( set "VS_PLATFORM=x64" )
echo(!GEN_SHORTHAND! | findstr /c:"-ARM"     >nul && ( set "VS_PLATFORM=ARM" )
echo(!GEN_SHORTHAND! | findstr /c:"-ARM64"   >nul && ( set "VS_PLATFORM=ARM64" )

echo(!GEN_SHORTHAND! | findstr /c:"-v120"    >nul && ( set "VS_TOOLSET=v120" )    && ( set "BOOST_TOOLSET=12.0" )
echo(!GEN_SHORTHAND! | findstr /c:"-v120_xp" >nul && ( set "VS_TOOLSET=v120_xp" ) && ( set "BOOST_TOOLSET=12.0" )
echo(!GEN_SHORTHAND! | findstr /c:"-v140"    >nul && ( set "VS_TOOLSET=v140" )    && ( set "BOOST_TOOLSET=14.0" )
echo(!GEN_SHORTHAND! | findstr /c:"-v140_xp" >nul && ( set "VS_TOOLSET=v140_xp" ) && ( set "BOOST_TOOLSET=14.0" )
echo(!GEN_SHORTHAND! | findstr /c:"-v141"    >nul && ( set "VS_TOOLSET=v141" )    && ( set "BOOST_TOOLSET=14.1" )
echo(!GEN_SHORTHAND! | findstr /c:"-v141_xp" >nul && ( set "VS_TOOLSET=v141_xp" ) && ( set "BOOST_TOOLSET=14.1" )
echo(!GEN_SHORTHAND! | findstr /c:"-v142"    >nul && ( set "VS_TOOLSET=v142" )    && ( set "BOOST_TOOLSET=14.2" )

SET VS_VER=%GEN_SHORTHAND:~0,4%

echo(!GENERATOR! | findstr /c:"vs20" >nul && (
    for /L %%i in (0,1,%LAST_GENERATOR_IDX%) do (
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

:: NOTE add space before VC_VER so that e.g. "12" doesn't match with "2012"
IF "!GENERATOR!"=="" IF NOT "%VisualStudioVersion%"=="" (
    set VC_VER=%VisualStudioVersion:.0=%
    FOR /L %%i in (%START%,1,%LAST_GENERATOR_IDX%) DO (
        echo(!GENERATORS[%%i]! | findstr /c:" !VC_VER!" >nul && (
            set GENERATOR=!GENERATORS[%%i]!
            call utils\cecho.cmd black cyan "Generator not passed, but VisualStudioVersion=%VisualStudioVersion% environment variable detected:"
            call utils\cecho.cmd black cyan "using '`"!GENERATOR!`'" as the generator."
			SET VS_VER=!GENERATOR:~-5,4!
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

FOR /L %%i in (0,1,%LAST_GENERATOR_IDX%) DO (
    IF !GENERATOR!==!GENERATORS[%%i]! GOTO :GeneratorValid
)
call utils\cecho.cmd 0 12 "%~nx0: Invalid or unsupported CMake generator string passed: '`"!GENERATOR!`'"- cannot proceed."
echo Supported CMake generator strings:
FOR /L %%i in (0,1,%LAST_GENERATOR_IDX%) DO (
    echo !GENERATORS[%%i]!
)
exit /b 1

:GeneratorValid

IF DEFINED VS_PLATFORM goto :PlatformDefined

:: If we do not have defined a platform yet,
:: figure out the build configuration from the CMake generator string.
:: Are we building 32-bit or 64-bit version.
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
    :: Are going to perform a 64-bit build?
    IF %%i==Win64 (
        set VS_PLATFORM=x64
    )
)

:PlatformDefined

:: determine the Visual C++ default version
IF %VS_VER%==2013 ( set "VC_VER=12.0" )
IF %VS_VER%==2015 ( set "VC_VER=14.0" )
IF %VS_VER%==2017 ( set "VC_VER=14.1" )
IF %VS_VER%==2019 ( set "VC_VER=14.2" )
IF %VS_VER%==2022 ( set "VC_VER=14.3" )

:: determine the argument for Boost bootstrap
set BOOST_BOOTSTRAP_VER=vc%VC_VER%
set BOOST_BOOTSTRAP_VER=%BOOST_BOOTSTRAP_VER:.=%

set VS_TOOLSET_HOST=

:: determine the toolset and winapi for Boost b2
:: optionally use 64bit toolset to work around memory errors when linking
IF DEFINED VS_TOOLSET (
    set BOOST_TOOLSET=msvc-%BOOST_TOOLSET%
    if "!VS_TOOLSET:~-3!"=="_xp" (
        set BOOST_WIN_API=define=BOOST_USE_WINAPI_VERSION=0x0501
    )
    IF NOT "%VS_HOST%"=="" (
        set VS_TOOLSET_HOST=%VS_TOOLSET%,host=%VS_HOST%
    )
) ELSE (
    set BOOST_TOOLSET=msvc-%VC_VER%
    set BOOST_WIN_API=
    IF NOT "%VS_HOST%"=="" (
        set VS_TOOLSET_HOST=host=%VS_HOST%
    )
)

IF %VS_PLATFORM%==Win32 (
    set ARCH_BITS=32
    set TARGET_ARCH=x86
)

IF %VS_PLATFORM%==x64 (
    set ARCH_BITS=64
    set TARGET_ARCH=x64
)

IF %VS_PLATFORM%==ARM (
    set ARCH_BITS=32
    set TARGET_ARCH=ARM
)

IF %VS_PLATFORM%==ARM64 (
    set ARCH_BITS=64
    set TARGET_ARCH=ARM64
)

:: Check CMake version and convert possible new format (>= 3.0) generator names to the old versions if using older CMake for VS <= 2013,
:: see http://www.cmake.org/cmake/help/v3.0/release/3.0.0.html#other-changes
FOR /f "delims=" %%i in ('where cmake') DO set CMAKE_PATH=%%i
IF NOT "%CMAKE_PATH%"=="" (
    FOR /f "delims=" %%i in ('cmake --version ^| findstr /C:"cmake version 3"') DO GOTO :CMake3AndNewer
    FOR /f "delims=" %%i in ('cmake --version ^| findstr /C:"cmake version 4"') DO GOTO :CMake3AndNewer
)

:: reject older CMake, see also build-deps.cmd
echo "CMake v3.11.4 or higher is required"
exit /b 1

:CMake3AndNewer

    :: check variables for debugging
     echo GENERATOR:           [!GENERATOR!]
     echo VS_VER:              [!VS_VER!]
     echo VS_PLATFORM:         [!VS_PLATFORM!]
     echo VS_TOOLSET:          [!VS_TOOLSET!]
     echo VC_VER:              [!VC_VER!]
     echo ARCH_BITS:           [!ARCH_BITS!]
     echo TARGET_ARCH:         [!TARGET_ARCH!]
     echo BOOST_BOOTSTRAP_VER: [!BOOST_BOOTSTRAP_VER!]
     echo BOOST_TOOLSET:       [!BOOST_TOOLSET!]
     echo BOOST_WIN_API:       [!BOOST_WIN_API!]

IF DEFINED VS_TOOLSET (
    set GEN_SHORTHAND=vs%VS_VER%-%VS_PLATFORM%-%VS_TOOLSET%
) ELSE (
    set GEN_SHORTHAND=vs%VS_VER%-%VS_PLATFORM%
)

:: VS project file extension is different on older VS versions
set VCPROJ_FILE_EXT=vcxproj

:: Add utils to PATH
set ORIGINAL_PATH=%PATH%
set PATH=%~dp0utils;%PATH%

:: Fetch and build the dependencies to a dedicated directory depending on the used VS version and target architecture.
:: NOTE For IfcOpenShell we can build all of our deps both x86 and x64 using different VS versions in the same directories
:: so no need for -%VS_VER%-%TARGET_ARCH% postfix.
:: set DEPS_DIR=%CD%\deps-%VS_VER%-%TARGET_ARCH%
pushd ..
set DEPS_DIR=%CD%\_deps
set INSTALL_DIR=%CD%\_deps-%GEN_SHORTHAND%-installed
:: set INSTALL_DIR=%CD%\deps-vs%VS_VER%-%TARGET_ARCH%-%DEBUG_OR_RELEASE_LOWERCASE%-installed
:: BUILD_DIR is a relative build directory used for CMake-based projects
set BUILD_DIR=_build-%GEN_SHORTHAND%
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
