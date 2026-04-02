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

:: This batch file expects CMake generator as %1 and build configuration type as %2. If not provided,
:: a deduced generator will be used for %1 and BUILD_CFG_DEFAULT for %2 (both set in vs-cfg.cmd)
:: Optionally a build type (Build/Rebuild/Clean) can be passed as %3.
::
:: Example usage (all arguments are optional):
:: build-deps.cmd vs2022-x64 RelWithDebInfo Build

@if not defined ECHO_ON ( echo off )
echo.

for %%Q in ("%~dp0\.") DO set "batpath=%%~fQ"

if NOT "%CD%" == "%batpath%" (
    GOTO :ErrorAndPrintUsage
)


set PROJECT_NAME=IfcOpenShell
call utils\cecho.cmd 0 15 "This script fetches and builds all %PROJECT_NAME% dependencies"
echo.

:: Enable the delayed environment variable expansion needed in vs-cfg.cmd.
setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0

:: Make sure vcvarsall.bat is called and dev env set is up.
IF "%VSINSTALLDIR%"=="" (
   call utils\cecho.cmd 0 12 "Visual Studio environment variables not set- cannot proceed."
   GOTO :ErrorAndPrintUsage
)

:: Check for cl.exe - at least the "Typical" Visual Studio 2015 installation does not include the C++ toolset by default,
:: http://blogs.msdn.com/b/vcblog/archive/2015/07/24/setup-changes-in-visual-studio-2015-affecting-c-developers.aspx
where cl.exe 2>&1>NUL
if not %ERRORLEVEL%==0 (
    call utils\cecho.cmd 0 12 "%~nx0: cl.exe not in PATH. Make sure to select the C++ toolset when installing Visual Studio- cannot proceed."
    GOTO :ErrorAndPrintUsage
)

:: Set up variables depending on the used Visual Studio version
call vs-cfg.cmd %1
IF NOT %ERRORLEVEL%==0 GOTO :Error

:: Set up the BuildDepsCache.txt filename
IF DEFINED VS_TOOLSET (
    set BUILD_DEPS_CACHE_PATH=BuildDepsCache-%VS_PLATFORM%-%VS_TOOLSET%.txt
) ELSE (
    set BUILD_DEPS_CACHE_PATH=BuildDepsCache-%VS_PLATFORM%.txt
)

:: fix for Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
:: see https://tracker.dev.opencascade.org/view.php?id=31628
SET COMPILE_WITH_WPO=FALSE

call build-type-cfg.cmd %2
IF NOT %ERRORLEVEL%==0 GOTO :Error

set BUILD_TYPE=%3
IF "%BUILD_TYPE%"=="" set BUILD_TYPE=Build

IF NOT "!BUILD_TYPE!"=="Build" IF NOT "!BUILD_TYPE!"=="Rebuild" IF NOT "!BUILD_TYPE!"=="Clean" (
    call utils\cecho.cmd 0 12 "Invalid build type passed: !BUILD_TYPE!. Cannot proceed, aborting!"
    GOTO :Error
)

:: Make sure deps and install folders exists.
IF NOT EXIST "%DEPS_DIR%". mkdir "%DEPS_DIR%"
IF NOT EXIST "%INSTALL_DIR%". mkdir "%INSTALL_DIR%"

:: If we use VS2008, framework path (for MSBuild) may not be correctly set. Manually attempt to add in that case
IF %VS_VER%==2008 set PATH=C:\Windows\Microsoft.NET\Framework\v3.5;%PATH%

:: User-configurable build options
IF NOT DEFINED IFCOS_INSTALL_PYTHON set IFCOS_INSTALL_PYTHON=TRUE

IF NOT DEFINED IFCOS_NUM_BUILD_PROCS set IFCOS_NUM_BUILD_PROCS=%NUMBER_OF_PROCESSORS%

:: For subroutines
REM /clp:ErrorsOnly;WarningsOnly
:: Note BUILD_TYPE not passed, Clean e.g. wouldn't delete the installed files.
set MSBUILD_MULTIPROC=/m /p:CL_MPCount=%IFCOS_NUM_BUILD_PROCS% /p:UseMultiToolTask=true /p:EnforceProcessCountAcrossBuilds=true
set MSBUILD_CMD=MSBuild.exe /nologo %MSBUILD_MULTIPROC%

echo.

:: Check that required tools are in PATH
FOR %%i IN (powershell git cmake) DO (
    where.exe %%i 1> NUL 2> NUL || call cecho.cmd 0 12 "Required tool `'%%i`' not installed or not added to PATH" && goto :ErrorAndPrintUsage
)

:: Check powershell version
powershell -c "exit $PSVersionTable.PSVersion.Major -lt 5"
IF NOT %ERRORLEVEL%==0 call cecho.cmd 0 12 "Powershell version 5 or higher required" && goto :ErrorAndPrintUsage
set PWSH_TOOLS=powershell -NonInteractive -File %SCRIPT_DIR%\utils\tools.ps1

cmake --version | findstr version > temp.txt
set /p CMAKE_VERSION=<temp.txt
del temp.txt
if "%CMAKE_VERSION%" LSS "cmake version 3.11.4" (
    echo "CMake v3.11.4 or higher is required"
    goto :ErrorAndPrintUsage
)

:: NOTE Boost < 1.64 doesn't work without tricks if the user has only VS 2017 installed and no earlier versions.
set BOOST_VERSION=1.86.0
:: Version string with underscores instead of dots.
set BOOST_VER=%BOOST_VERSION:.=_%

:: Print build configuration information

call cecho.cmd 0 10 "Script configuration:"
call cecho.cmd 0 13 "* CMake Generator`t= '`"%GENERATOR%`'`t
echo   - Passed to CMake -G option.
call cecho.cmd 0 13 "* Target Architecture`t= %TARGET_ARCH%"
echo   - Whether were doing 32-bit (x86) or 64-bit (x64, arm64) build.
call cecho.cmd 0 13 "* Target Platform`t= %VS_PLATFORM%"
echo   - Passed to CMake -A option.
call cecho.cmd 0 13 "* Target Toolset`t= %VS_TOOLSET%"
echo   - Passed to CMake -T option.
call cecho.cmd 0 13 "* Dependency Directory`t= %DEPS_DIR%"
echo   - The directory where %PROJECT_NAME% dependencies are fetched and built.
call cecho.cmd 0 13 "* Installation Directory = %INSTALL_DIR%"
echo   - The directory where %PROJECT_NAME% dependencies are installed.
call cecho.cmd 0 13 "* Build Config Type`t= %BUILD_CFG%"
echo   - The used build configuration type for the dependencies.
echo     Defaults to RelWithDebInfo if not specified.
IF %BUILD_CFG%==MinSizeRel call cecho.cmd 0 14 "     WARNING: MinSizeRel build can suffer from a significant performance loss."
call cecho.cmd 0 13 "* Build Type`t`t= %BUILD_TYPE%"
echo   - The used build type for the dependencies (Build, Rebuild, Clean).
echo     Defaults to Build if not specified.
call cecho.cmd 0 13 "* IFCOS_INSTALL_PYTHON`t= %IFCOS_INSTALL_PYTHON%"
echo   - Download and install Python.
echo     Set to something other than TRUE if you wish to use an already installed version of Python.
echo     But then you'll need to set PYTHONHOME env variable to your Python installation before running run-cmake.bat
echo     to your Python installation path.
call cecho.cmd 0 13 "* IFCOS_NUM_BUILD_PROCS`t= %IFCOS_NUM_BUILD_PROCS%"
echo   - How many MSBuild.exe processes may be run in parallel.
echo     Defaults to NUMBER_OF_PROCESSORS. Used also by other IfcOpenShell build scripts.
echo.

call :PrintUsage

call cecho.cmd 0 14 "Warning: You will need roughly 8 GB of disk space to proceed."
echo.

call cecho.cmd black cyan "If you are not ready with the above: type `'n`' in the prompt below. Build proceeds on all other inputs!"

set /p do_continue="> "
if "%do_continue%"=="n" goto :Finish

echo.
set START_TIME=%TIME%
echo Build started at %START_TIME%.
set BUILD_STARTED=TRUE
echo.

cd "%DEPS_DIR%"

:: VERSIONS
:: Don't use HDF5 1.13.0, because it has a broken cmake package path.
set HDF5_VERSION=1_13_1
set OCCT_VERSION=7.8.1
IF DEFINED PYTHON_VERSION (
    echo Using overridden PYTHON_VERSION: '%PYTHON_VERSION%'
) else (
    set PYTHON_VERSION=3.11.7
)

:: VERSION DERIVATIONS
for /f "tokens=1,2,3 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PY_VER_MAJOR_MINOR=%%a%%b
)
IF "%IFCOS_INSTALL_PYTHON%"=="TRUE" (
    IF /I "%TARGET_ARCH%"=="arm64" (
        set PYTHONHOME=%DEPS_DIR%\pythonarm64.%PYTHON_VERSION%\tools
    ) ELSE (
        set PYTHONHOME=%DEPS_DIR%\python.%PYTHON_VERSION%\tools
    )
)

:: Cache last used CMake generator and configurable dependency dirs for other scripts to use
:: This is consolidated at the beginning of the script so that the script can be partially
:: executed by jumping (using goto) to different labels.
if defined GEN_SHORTHAND echo GEN_SHORTHAND=%GEN_SHORTHAND%>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
echo HDF5_VERSION=%HDF5_VERSION%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
IF "%IFCOS_INSTALL_PYTHON%"=="TRUE" (
    echo PYTHONHOME=%PYTHONHOME%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
)


:nuget
set DEPENDENCY_NAME=nuget
set NUGET_VERSION=6.14.0
set NUGET_INSTALL_DIR=%DEPS_DIR%\nuget-%NUGET_VERSION%
set NUGET_EXE=%NUGET_INSTALL_DIR%\nuget.exe

where nuget >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Found existing nuget in PATH. Skipping.
    for /f "delims=" %%i in ('where nuget') do set "NUGET_EXE=%%i"
    goto :ccache
)

IF EXIST "%NUGET_EXE%" (
    echo Found existing "%DEPS_DIR%\nuget.exe", skipping
    goto :ccache
)

cd %DEPS_DIR%
call :DownloadFile ^
    https://dist.nuget.org/win-x86-commandline/v%NUGET_VERSION%/nuget.exe ^
    "%NUGET_INSTALL_DIR%" nuget.exe
IF NOT %ERRORLEVEL%==0 GOTO :Error


:ccache
set DEPENDENCY_NAME=ccache
set CCACHE_VERSION=4.12.1
set CCACHE_INSTALL_DIR=%DEPS_DIR%\%DEPENDENCY_NAME%.%CCACHE_VERSION%\tools
set DEPENDENCY_DIR=%CCACHE_INSTALL_DIR%

where ccache >nul 2>&1
IF %ERRORLEVEL%==0 (
    echo Found existing ccache in PATH. Skipping.
    goto :proj
)

echo CCACHE_INSTALL_DIR=%CCACHE_INSTALL_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
IF EXIST "%DEPENDENCY_DIR%" (
    echo Found existing "%DEPENDENCY_DIR%", skipping
    goto :proj
)

"%NUGET_EXE%" install ccache -Version %CCACHE_VERSION% -OutputDirectory "%DEPS_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error

:proj

set PROJ_VERSION=9.4.1
IF EXIST "%INSTALL_DIR%\proj-%PROJ_VERSION%" (
    echo Found existing "%INSTALL_DIR%\proj-%PROJ_VERSION%", skipping
    goto :mpir
)

set DEPENDENCY_NAME=sqlite3
md %INSTALL_DIR%\sqlite3\lib %INSTALL_DIR%\sqlite3\bin %INSTALL_DIR%\sqlite3\include
call :DownloadFile https://www.sqlite.org/2023/sqlite-amalgamation-3430100.zip "%DEPS_DIR%" sqlite-amalgamation-3430100.zip
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive sqlite-amalgamation-3430100.zip "%DEPS_DIR%" "%DEPS_DIR%\sqlite-amalgamation-3430100"
IF NOT %ERRORLEVEL%==0 GOTO :Error
pushd "%DEPS_DIR%\sqlite-amalgamation-3430100"
cl /c sqlite3.c
lib /OUT:%INSTALL_DIR%\sqlite3\lib\sqlite3.lib sqlite3.obj
cl sqlite3.c shell.c /link /out:%INSTALL_DIR%\sqlite3\bin\sqlite3.exe
set PATH=%PATH%;%INSTALL_DIR%\sqlite3\bin
copy sqlite3.h %INSTALL_DIR%\sqlite3\include
popd

set DEPENDENCY_NAME=proj
set DEPENDENCY_DIR=%DEPS_DIR%\proj-%PROJ_VERSION%
call :DownloadFile https://download.osgeo.org/proj/proj-%PROJ_VERSION%.zip "%DEPS_DIR%" proj-%PROJ_VERSION%.zip
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive proj-%PROJ_VERSION%.zip "%DEPS_DIR%" "%DEPS_DIR%\proj-%PROJ_VERSION%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
pushd "%DEPENDENCY_DIR%"
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\proj-%PROJ_VERSION%" ^
    -DSQLITE3_INCLUDE_DIR=%INSTALL_DIR%\sqlite3\include ^
    -DSQLITE3_LIBRARY=%INSTALL_DIR%\sqlite3\lib\sqlite3.lib ^
    -DENABLE_TIFF=Off -DENABLE_CURL=Off -DBUILD_PROJSYNC=Off ^
    -DBUILD_SHARED_LIBS=Off ^
    -DBUILD_TESTING=Off
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
popd


:mpir

IF EXIST "%INSTALL_DIR%\mpir" (
    echo Found existing "%INSTALL_DIR%\mpir", skipping
    goto :mpfr
)

set DEPENDENCY_NAME=mpir
:: `mpfr` depends on relative path `..\mpir\config.h`, so dependency name should match exactly.
set DEPENDENCY_DIR=%DEPS_DIR%\mpir
call :GitCloneAndCheckoutRevision https://github.com/Andrej730/mpir-vs2026.git "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
pushd "%DEPENDENCY_DIR%"
git reset --hard
git clean -fdx
REM There probably need to be quotes here around the filename
powershell -c "get-content %~dp0patches\mpir.patch | %%{$_ -replace \"sdk\",\"%UCRTVersion%\"} | %%{$_ -replace \"fn\",\"lib_mpir_cxx\"}" | git apply --unidiff-zero --ignore-whitespace
IF NOT %ERRORLEVEL%==0 GOTO :Error
powershell -c "get-content %~dp0patches\mpir.patch | %%{$_ -replace \"sdk\",\"%UCRTVersion%\"} | %%{$_ -replace \"fn\",\"lib_mpir_gc\"}" | git apply --unidiff-zero --ignore-whitespace
IF NOT %ERRORLEVEL%==0 GOTO :Error
if NOT "%USE_STATIC_RUNTIME%"=="FALSE" git apply "%~dp0patches\mpir_runtime.patch" --unidiff-zero --ignore-whitespace
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF /I "%VS_PLATFORM%"=="ARM64" (
    echo "Applying ARM64 Patches for Mpir"
    git apply "%~dp0patches\mpir-arm64-changes.patch" --unidiff-zero --ignore-whitespace
)
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd msvc
cd vs%VS_VER:~2,2%
call .\msbuild.bat gc LIB %VS_PLATFORM% %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF NOT EXIST "%INSTALL_DIR%\mpir". mkdir "%INSTALL_DIR%\mpir"
copy ..\..\lib\%VS_PLATFORM%\%DEBUG_OR_RELEASE%\* "%INSTALL_DIR%\mpir"
IF NOT %ERRORLEVEL%==0 GOTO :Error
popd

:mpfr

IF EXIST "%INSTALL_DIR%\mpfr" (
    echo Found existing "%INSTALL_DIR%\mpfr", skipping
    goto :HDF5
)

set DEPENDENCY_NAME=mpfr
set DEPENDENCY_DIR=%DEPS_DIR%\mpfr
call :GitCloneAndCheckoutRevision https://github.com/aothms/mpfr.git "%DEPENDENCY_DIR%" 2ebbe10fd029a480cf6e8a64c493afa9f3654251
IF NOT %ERRORLEVEL%==0 GOTO :Error
pushd "%DEPENDENCY_DIR%"
git reset --hard
powershell -c "get-content %~dp0patches\mpfr.patch | %%{$_ -replace \"sdk\",\"%UCRTVersion%\"} | %%{$_ -replace \"fn\",\"lib_mpfr\"}" | git apply --unidiff-zero --ignore-whitespace
IF NOT %ERRORLEVEL%==0 GOTO :Error
if NOT "%USE_STATIC_RUNTIME%"=="FALSE" git apply "%~dp0patches\mpfr_runtime.patch" --unidiff-zero --ignore-whitespace
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF /I "%VS_PLATFORM%"=="ARM64" (
    echo "Applying ARM64 Patches for Mpfr"
    git apply "%~dp0patches\mpfr-arm64-changes.patch" --unidiff-zero --ignore-whitespace
)
if "%VS_VER%"=="2017" (
  set mpfr_sln=build.vc15
  set orig_platform_toolset=v141
) else (
  set mpfr_sln=build.vs19
  set orig_platform_toolset=v142
)
powershell -c "get-childitem %DEPENDENCY_DIR%\%mpfr_sln% -recurse -include *.vcxproj | select -expand fullname | foreach { (Get-Content $_) -replace '%orig_platform_toolset%', 'v%VC_VER:.=%' | Set-Content $_ }"
call :BuildSolution "%DEPENDENCY_DIR%\%mpfr_sln%\lib_mpfr.sln" %DEBUG_OR_RELEASE% lib_mpfr
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM This command fails because not all msvc projects are patched with the right sdk version
IF NOT EXIST lib\%VS_PLATFORM%\%DEBUG_OR_RELEASE%\mpfr.lib GOTO :Error
IF NOT EXIST "%INSTALL_DIR%\mpfr". mkdir "%INSTALL_DIR%\mpfr"
copy lib\%VS_PLATFORM%\%DEBUG_OR_RELEASE%\* "%INSTALL_DIR%\mpfr"
IF NOT %ERRORLEVEL%==0 GOTO :Error
popd

:HDF5

set DEPENDENCY_NAME=hdf5
set DEPENDENCY_DIR=%DEPS_DIR%\hdf5-%HDF5_VERSION%
set HDF5_CMAKE_ZIP=hdf5-%HDF5_VERSION%.zip
set DEPENDENCY_INSTALL_NAME=HDF5-%HDF5_VERSION%-win%ARCH_BITS%
set HDF5_INSTALL_NAME=%DEPENDENCY_INSTALL_NAME%
set NEXT_DEPENDENCY_LABEL=Boost

call :CheckInstallation
if %ERRORLEVEL%==200 GOTO %NEXT_DEPENDENCY_LABEL%

if "%ARCH_BITS%"=="64" set ARCH_BITS_64=64
call :DownloadFile ^
    https://github.com/HDFGroup/hdf5/archive/refs/tags/hdf5-%HDF5_VERSION%.zip ^
    "%DEPS_DIR%" %HDF5_CMAKE_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %HDF5_CMAKE_ZIP% "%DEPS_DIR%" "%DEPS_DIR%\hdf5-%HDF5_VERSION%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
if exist "%DEPS_DIR%\hdf5-hdf5-%HDF5_VERSION%" ren "%DEPS_DIR%\hdf5-hdf5-%HDF5_VERSION%" "hdf5-%HDF5_VERSION%"
pushd "%DEPENDENCY_DIR%"
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\%HDF5_INSTALL_NAME%" ^
               -DHDF5_ENABLE_Z_LIB_SUPPORT=OFF -DBUILD_TESTING=OFF ^
               -DHDF5_BUILD_TOOLS=OFF -DHDF5_BUILD_EXAMPLES=OFF -DBUILD_SHARED_LIBS=OFF -DHDF5_BUILD_UTILS=OFF ^
               -DHDF5_BUILD_CPP_LIB=ON
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :MarkInstallation
popd

:: Note all of the dependencies have appropriate label so that user can easily skip something if wanted
:: by modifying this file and using goto.
:Boost
:: DEPENDENCY_NAME is used for logging and DEPENDENCY_DIR for saving from some redundant typing
set DEPENDENCY_NAME=Boost %BOOST_VERSION%
set DEPENDENCY_DIR=%DEPS_DIR%\boost_%BOOST_VER%
set DEPENDENCY_INSTALL_DIR=%DEPENDENCY_DIR%\stage\%GEN_SHORTHAND%
echo BOOST_INSTALL_DIR=%DEPENDENCY_INSTALL_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
:: Needed for CGAL build.
set BOOST_ROOT=%DEPENDENCY_DIR%
:: NOTE Also zip download exists, if encountering problems with 7z for some reason.
set ZIP_EXT=7z
set BOOST_ZIP=boost-%BOOST_VERSION%-b2-nodocs.%ZIP_EXT%

cd "%DEPS_DIR%"
call :DownloadFile https://github.com/boostorg/boost/releases/download/boost-%BOOST_VERSION%/%BOOST_ZIP% "%DEPS_DIR%" %BOOST_ZIP%

IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPS_DIR%"
call :ExtractArchive %BOOST_ZIP% "%DEPS_DIR%" %DEPENDENCY_DIR%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:: top-level folder name changed when migrating to github releases
if exist "%DEPS_DIR%\boost-%BOOST_VERSION%". (
    ren %DEPS_DIR%\boost-%BOOST_VERSION% boost_%BOOST_VER%
)

:: As boost 1.90.0 it still includes b2 that doesn't support vc145 (not to mention older boost versions).
:: So to support vc145 we download b2 separately (only if we do use vc145).
call :check_boost_vc145_compatibility "%VC_VER%" "%DEPS_DIR%" "%DEPENDENCY_DIR%"
if NOT %ERRORLEVEL%==0 GOTO :Error

:: Build Boost build script
if not exist "%DEPENDENCY_DIR%\project-config.jam". (
    cd "%DEPS_DIR%"
    IF NOT EXIST "%DEPENDENCY_DIR%\boost.css" GOTO :Error
    cd "%DEPENDENCY_DIR%"
    call cecho.cmd 0 13 "Building Boost build script."
    call bootstrap %BOOST_BOOTSTRAP_VER%
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)

if /I "%TARGET_ARCH%"=="x64" (
    set B2_ARCH_FEATURE=x86
) else if /I "%TARGET_ARCH%"=="arm64" (
    set B2_ARCH_FEATURE=arm
) else (
    echo "Failed to identify architecture"
    GOTO :Error
)
set BOOST_LIBS=--with-system --with-regex --with-thread --with-program_options --with-date_time --with-iostreams --with-filesystem
:: NOTE Boost is fast to build with limited set of libraries so build it always.
cd "%DEPENDENCY_DIR%"
call cecho.cmd 0 13 "Building %DEPENDENCY_NAME% %BOOST_LIBS% Please be patient, this will take a while."
IF EXIST "%DEPENDENCY_DIR%\bin.v2\project-cache.jam" del "%DEPENDENCY_DIR%\bin.v2\project-cache.jam"

call .\b2 toolset=%BOOST_TOOLSET% architecture=%B2_ARCH_FEATURE% runtime-link=shared address-model=%ARCH_BITS% --abbreviate-paths -j%IFCOS_NUM_BUILD_PROCS% ^
    variant=%DEBUG_OR_RELEASE_LOWERCASE% %BOOST_WIN_API% %BOOST_LIBS% stage --stagedir=%DEPENDENCY_INSTALL_DIR%

IF NOT %ERRORLEVEL%==0 GOTO :Error

:JSON
set DEPENDENCY_NAME=JSON for Modern C++ v3.6.1
IF NOT EXIST "%INSTALL_DIR%\json\nlohmann". mkdir "%INSTALL_DIR%\json\nlohmann"
call :DownloadFile https://github.com/nlohmann/json/releases/download/v3.6.1/json.hpp "%INSTALL_DIR%\json\nlohmann" json.hpp

:OpenCOLLADA

:: Note OpenCOLLADA has only Release and Debug builds.
set DEPENDENCY_NAME=OpenCOLLADA
set DEPENDENCY_DIR=%DEPS_DIR%\OpenCOLLADA
set DEPENDENCY_INSTALL_NAME=OpenCOLLADA
set NEXT_DEPENDENCY_LABEL=OCCT
:: Always clone it, even if it's installed, because it contains xml headers we need.
:: Use a fixed revision in order to prevent introducing breaking changes
call :GitCloneAndCheckoutRevision https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPENDENCY_DIR%" 064a60b65c2c31b94f013820856bc84fb1937cc6

call :CheckInstallation
if %ERRORLEVEL%==200 GOTO %NEXT_DEPENDENCY_LABEL%

IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"
:: Debug build of OpenCOLLADAValidator fails (https://github.com/KhronosGroup/OpenCOLLADA/issues/377) so
:: so disable it from the build altogether as we have no use for it
findstr #add_subdirectory(COLLADAValidator) CMakeLists.txt>NUL
IF NOT %ERRORLEVEL%==0 git apply --reject --whitespace=fix "%~dp0patches\OpenCOLLADA_CMakeLists.txt.patch" --ignore-whitespace
:: NOTE OpenCOLLADA has been observed to have problems with switching between debug and release builds so
:: uncomment to following line in order to delete the CMakeCache.txt always if experiencing problems.
REM IF EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt". del "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt"
:: NOTE Enforce that the embedded LibXml2 and PCRE are used as there might be problems with arbitrary versions of the libraries.
:: OpenCOLLADA is ancient at this point and allows cmake 2.6+, which results in error in cmake 4, so we override minimum cmake version.
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%" -DUSE_STATIC_MSVC_RUNTIME=0 -DCMAKE_DEBUG_POSTFIX=d ^
               -DLIBXML2_LIBRARIES="" -DLIBXML2_INCLUDE_DIR="" -DPCRE_INCLUDE_DIR="" -DPCRE_LIBRARIES="" ^
               -DCMAKE_POLICY_VERSION_MINIMUM=3.5
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM IF NOT EXIST "%DEPS_DIR%\OpenCOLLADA\%BUILD_DIR%\lib\%DEBUG_OR_RELEASE%\OpenCOLLADASaxFrameworkLoader.lib".
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :MarkInstallation

:OCCT

SET OCCT_VER=V%OCCT_VERSION:.=_%

set DEPENDENCY_NAME=OpenCASCADE
:: `new-layout` suffix can be removed on the next OCCT version update
:: it's needed to separate legacy layout installation from the new one.
set OCCT_DEPENDENCY_INSTALL_NAME=opencascade-%OCCT_VERSION%-new-layout
set DEPENDENCY_INSTALL_NAME=%OCCT_DEPENDENCY_INSTALL_NAME%
set DEPENDENCY_INSTALL_DIR=%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%
set NEXT_DEPENDENCY_LABEL=Python
echo OCC_INSTALL_DIR=%DEPENDENCY_INSTALL_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

call :CheckInstallation
if %ERRORLEVEL%==200 GOTO %NEXT_DEPENDENCY_LABEL%

set DEPENDENCY_NAME=Open CASCADE %OCCT_VERSION%
set DEPENDENCY_DIR=%DEPS_DIR%\occt_git
set DEPENDENCY_INSTALL_NAME=%OCCT_DEPENDENCY_INSTALL_NAME%
cd "%DEPS_DIR%"
call :GitCloneAndCheckoutRevision https://github.com/Open-Cascade-SAS/OCCT "%DEPENDENCY_DIR%" %OCCT_VER%
if not %ERRORLEVEL%==0 goto :Error

:: Patching always blindly would trigger a rebuild each time
findstr IfcOpenShell "%DEPENDENCY_DIR%\CMakeLists.txt">NUL
if not %ERRORLEVEL%==0 (
    pushd "%DEPENDENCY_DIR%"
    git apply --ignore-whitespace ""%~dp0patches\%OCCT_VER%.patch"
    popd
)
findstr IfcOpenShell "%DEPENDENCY_DIR%\CMakeLists.txt">NUL
if not %ERRORLEVEL%==0 goto :Error

cd "%DEPENDENCY_DIR%"
:: TODO: remove CMAKE_DEBUG_POSTFIX setting later.
:: Temporarily explicitly set `CMAKE_DEBUG_POSTFIX` to empty to override it's perviously being set to `d`.
:: OCCT don't need it, since it's layout is separating debug and release build by different folders.
::
:: OCCT 7.8.1 we're using is becoming old and it was targeting cmake 3.1+.
::To make it buildable on cmake 4, we override policy version, but it may have some quirks in the future and we may consider version bump.
call :RunCMake -DINSTALL_DIR="%DEPENDENCY_INSTALL_DIR%" -DBUILD_LIBRARY_TYPE="Static" -DCMAKE_DEBUG_POSTFIX="" ^
    -DBUILD_MODULE_Draw=0 ^
    -DBUILD_RELEASE_DISABLE_EXCEPTIONS=OFF ^
    -DUSE_XLIB=OFF ^
    -DUSE_FREETYPE=OFF ^
    -DUSE_OPENGL=OFF ^
    -DUSE_GLES2=OFF ^
    -DBUILD_USE_PCH=ON ^
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5
if not %ERRORLEVEL%==0 goto :Error

:: whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
IF %ARCH_BITS%==32 (
	IF %BUILD_CFG%==Release (
		SET COMPILE_WITH_WPO=TRUE
	)
)

call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error

:: If `inc` is present in installation folder, then installation takes much longer
:: See https://github.com/Open-Cascade-SAS/OCCT/issues/901
powershell -c "$path = '%DEPENDENCY_INSTALL_DIR%\inc'; if (Test-Path $path) { Remove-Item -Recurse -Force $path }"
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error

:: Fix upstream bug in cmake config file with unescaped quotes preventing configuration.
:: The issue is fixed in 7.9.0+.
:: See https://github.com/Open-Cascade-SAS/OCCT/pull/373
powershell -c "$path='%DEPENDENCY_INSTALL_DIR%\cmake\OpenCASCADEConfig.cmake'; (Get-Content $path) -replace '/wd\"(\d+)\"','/wd$1' | Set-Content $path"
if not %ERRORLEVEL%==0 goto :Error

call :MarkInstallation

SET COMPILE_WITH_WPO=FALSE

:Python
set DEPENDENCY_NAME=Python %PYTHON_VERSION%
set DEPENDENCY_DIR=N/A
set PYTHON_AMD64_POSTFIX=
IF /I "%TARGET_ARCH%"=="x64"   set "PYTHON_AMD64_POSTFIX=-amd64"
IF /I "%TARGET_ARCH%"=="arm64" set "PYTHON_AMD64_POSTFIX=-arm64"
set "PYTHON_INSTALLER=python-%PYTHON_VERSION%%PYTHON_AMD64_POSTFIX%.exe"

IF NOT "%IFCOS_INSTALL_PYTHON%"=="TRUE" (
    call cecho.cmd 0 13 "IFCOS_INSTALL_PYTHON not 'TRUE', skipping installation of Python."
    goto :SWIG
)

:: nuget doesn't support providing architecture for packages.
IF /I NOT "%TARGET_ARCH%"=="x64" IF /I NOT "%TARGET_ARCH%"=="arm64" (
    call cecho.cmd 0 12 "Automatic insallation of Python for x86 builds is not supported,"
    call cecho.cmd 0 12 "please install Python %PYTHON_VERSION% manually and ensure that it is available in PATH."
    call cecho.cmd 0 12 "https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%"
    goto :Error
)

if EXIST "%PYTHONHOME%" (
    echo Found existing '%PYTHONHOME%', skipping installation.
    goto :SWIG
)

IF /I "%TARGET_ARCH%"=="x64" (
    "%NUGET_EXE%" install Python -Version %PYTHON_VERSION% -OutputDirectory "%DEPS_DIR%"
    IF NOT %ERRORLEVEL%==0 GOTO :Error
) ELSE (
    "%NUGET_EXE%" install pythonarm64 -Version %PYTHON_VERSION% -OutputDirectory "%DEPS_DIR%"
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)

:SWIG
set DEPENDENCY_NAME=SWIG
set SWIG_VERSION=4.2.1
set DEPENDENCY_DIR=%DEPS_DIR%\swig-%SWIG_VERSION%
set DEPENDENCY_INSTALL_DIR=%INSTALL_DIR%\swig-%SWIG_VERSION%
echo SWIG_INSTALL_DIR=%DEPENDENCY_INSTALL_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

IF EXIST "%DEPENDENCY_INSTALL_DIR%" (
    echo Found existing "%DEPENDENCY_INSTALL_DIR%", skipping
    goto :cgal
)

cd "%DEPS_DIR%"

:: Install bison dependency for SWIG.
set SWIG_DEPENDENCY_NAME=%DEPENDENCY_NAME%
set DEPENDENCY_NAME=win_flex_bison
set WIN_FLEX_BISON=win_flex_bison-2.5.25
set WIN_FLEX_BISON_ZIP=%WIN_FLEX_BISON%.zip
call :DownloadFile https://github.com/lexxmark/winflexbison/releases/download/v2.5.25/%WIN_FLEX_BISON_ZIP% "%DEPS_DIR%" %WIN_FLEX_BISON_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
echo test %WIN_FLEX_BISON%
call :ExtractArchive %WIN_FLEX_BISON_ZIP% "%DEPS_DIR%\%WIN_FLEX_BISON%" "%DEPS_DIR%\%WIN_FLEX_BISON%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
set DEPENDENCY_NAME=%SWIG_DEPENDENCY_NAME%

set SWIG_ZIP=swigwin-%SWIG_VERSION%.zip
call :DownloadFile https://github.com/swig/swig/archive/refs/tags/v%SWIG_VERSION%.zip "%DEPS_DIR%" swig-%SWIG_VERSION%.zip
IF NOT %ERRORLEVEL%==0 GOTO :Error

call :ExtractArchive swig-%SWIG_VERSION%.zip "%DEPS_DIR%" "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"

call :RunCMake -DCMAKE_INSTALL_PREFIX="%DEPENDENCY_INSTALL_DIR%" ^
               -DWITH_PCRE=OFF ^
               -DBISON_EXECUTABLE="%DEPS_DIR%\%WIN_FLEX_BISON%\win_bison.exe"
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" Release
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" Release
IF NOT %ERRORLEVEL%==0 GOTO :Error
robocopy "%INSTALL_DIR%\swigwin\bin" "%INSTALL_DIR%\swigwin" /move /e

:cgal

IF EXIST "%INSTALL_DIR%\cgal" (
    echo Found existing "%INSTALL_DIR%\cgal", skipping
    goto :Eigen
)

set DEPENDENCY_NAME=cgal
set DEPENDENCY_DIR=%DEPS_DIR%\cgal
call :GitCloneAndCheckoutRevision https://github.com/CGAL/cgal.git "%DEPENDENCY_DIR%" v5.5.5
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"
git reset --hard
git apply --ignore-whitespace "%~dp0patches\cgal_no_zlib.patch"
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\cgal"    ^
               -DCGAL_HEADER_ONLY=On
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:Eigen
set DEPENDENCY_NAME=Eigen
set DEPENDENCY_DIR=%INSTALL_DIR%\%DEPENDENCY_NAME%

IF EXIST "%INSTALL_DIR%\%DEPENDENCY_NAME%" (
    echo Found existing "%INSTALL_DIR%\%DEPENDENCY_NAME%", skipping
    goto :zstd
)
call :GitCloneAndCheckoutRevision https://gitlab.com/libeigen/eigen.git "%DEPENDENCY_DIR%" 3.3.9

:zstd
set DEPENDENCY_NAME=zstd
set ZSTD_VERSION=1.5.7
set ZSTD_ZIP=zstd-%ZSTD_VERSION%.zip
set DEPENDENCY_DIR=%DEPS_DIR%\%DEPENDENCY_NAME%-%ZSTD_VERSION%

IF EXIST "%INSTALL_DIR%\%DEPENDENCY_NAME%" (
    echo Found existing "%INSTALL_DIR%\%DEPENDENCY_NAME%", skipping
    goto :rocksdb
)

cd %DEPS_DIR%
call :DownloadFile ^
    https://github.com/facebook/zstd/archive/refs/tags/v%ZSTD_VERSION%.zip ^
    "%DEPS_DIR%" %ZSTD_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %ZSTD_ZIP% "%DEPS_DIR%" "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"\build\cmake
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\zstd" -DZSTD_BUILD_STATIC=ON -DZSTD_BUILD_SHARED=OFF
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\build\cmake\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\build\cmake\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:rocksdb
set DEPENDENCY_NAME=rocksdb
set ROCKSDB_VERSION=9.11.2
set ROCKSDB_ZIP=rocksdb-%ROCKSDB_VERSION%.zip
set DEPENDENCY_DIR=%DEPS_DIR%\%DEPENDENCY_NAME%-%ROCKSDB_VERSION%
set DEPENDENCY_INSTALL_NAME=%DEPENDENCY_NAME%
set NEXT_DEPENDENCY_LABEL=Successful

call :CheckInstallation
if %ERRORLEVEL%==200 GOTO %NEXT_DEPENDENCY_LABEL%

cd %DEPS_DIR%
call :DownloadFile ^
    https://github.com/facebook/rocksdb/archive/refs/tags/v%ROCKSDB_VERSION%.zip ^
    "%DEPS_DIR%" %ROCKSDB_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %ROCKSDB_ZIP% "%DEPS_DIR%" "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"
:: see rocksdb\thirdparty.inc
:: providing package is not supported on Windows.
set ZSTD_INCLUDE=%INSTALL_DIR%\zstd\include
set ZSTD_LIB_DEBUG=%INSTALL_DIR%\zstd\lib\zstd_static.lib
set ZSTD_LIB_RELEASE=%INSTALL_DIR%\zstd\lib\zstd_static.lib
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%" ^
               -DROCKSDB_INSTALL_ON_WINDOWS=On ^
               -DFAIL_ON_WARNINGS=Off ^
               -DWITH_TESTS=OFF ^
               -DWITH_TOOLS=OFF ^
               -DWITH_BENCHMARK_TOOLS=OFF ^
               -DWITH_CORE_TOOLS=OFF ^
               -DROCKSDB_BUILD_SHARED=OFF ^
               -DWITH_ZSTD=On ^
               -DZSTD_INCLUDE_DIR="%ZSTD_INCLUDE%" ^
               -DZSTD_LIBRARY_DEBUG="%ZSTD_LIB_DEBUG%" ^
               -DZSTD_LIBRARY_RELEASE="%ZSTD_LIB_RELEASE%" ^
               -DPORTABLE=1 ^
               -DCMAKE_DEBUG_POSTFIX="_d"
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :MarkInstallation

:: :tbb
:: set DEPENDENCY_NAME=tbb
:: set DEPENDENCY_DIR=%DEPS_DIR%\tbb
:: call :GitCloneAndCheckoutRevision https://github.com/wjakob/tbb  "%DEPENDENCY_DIR%" 9e219e24fe223b299783200f217e9d27790a87b0
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: cd "%DEPENDENCY_DIR%"
:: call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\tbb"  ^
::                -DBUILD_SHARED_LIBS=Off
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
::
:: :usd
:: set DEPENDENCY_NAME=usd
:: set DEPENDENCY_DIR=%DEPS_DIR%\usd
:: call :GitCloneAndCheckoutRevision https://github.com/PixarAnimationStudios/OpenUSD "%DEPENDENCY_DIR%" v24.05
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: cd "%DEPENDENCY_DIR%"
:: call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\usd"  ^
::                -DBOOST_ROOT="%DEPS_DIR%\boost_%BOOST_VER%" ^
::                -DOneTBB_CMAKE_ENABLE=On                    ^
::                -DTBB_ROOT_DIR="%INSTALL_DIR%\tbb"          ^
::                -DPXR_ENABLE_PYTHON_SUPPORT=FALSE           ^
::                -DPXR_ENABLE_GL_SUPPORT=FALSE               ^
::                -DPXR_BUILD_IMAGING=FALSE                   ^
::                -DPXR_BUILD_TUTORIALS=FALSE                 ^
::                -DPXR_BUILD_EXAMPLES=FALSE                  ^
::                -DPXR_BUILD_USD_TOOLS=FALSE                 ^
::                -DPXR_BUILD_TESTS=FALSE                     ^
::                -DBUILD_SHARED_LIBS=Off                     ^
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: call :BuildCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
:: IF NOT %ERRORLEVEL%==0 GOTO :Error
:: call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
:: IF NOT %ERRORLEVEL%==0 GOTO :Error

:Successful
echo.
call "%~dp0\utils\cecho.cmd" 0 10 "%PROJECT_NAME% dependencies built."
set IFCOS_SCRIPT_RET=0
goto :Finish

:ErrorAndPrintUsage
echo.
call :PrintUsage
:Error
echo.
call "%~dp0\utils\cecho.cmd" 0 12 "An error occurred! Aborting! Last logged action: %LAST_ACTION%"
set IFCOS_SCRIPT_RET=1
goto :Finish

:Finish
:: Print end time and elapsed time, http://stackoverflow.com/a/9935540
if not defined BUILD_STARTED goto :BuildTimeSkipped
set END_TIME=%TIME%
for /F "tokens=1-4 delims=:.," %%a in ("%START_TIME%") do (
   set /A "start=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*100+1%%d %% 100"
)
for /F "tokens=1-4 delims=:.," %%a in ("%END_TIME%") do (
   set /A "end=(((%%a*60)+1%%b %% 100)*60+1%%c %% 100)*100+1%%d %% 100"
)
set /A elapsed=end-start
set /A hh=elapsed/(60*60*100), rest=elapsed%%(60*60*100), mm=rest/(60*100), rest%%=60*100, ss=rest/100, cc=rest%%100
if %mm% lss 10 set mm=0%mm%
if %ss% lss 10 set ss=0%ss%
if %cc% lss 10 set cc=0%cc%
echo.
echo Build ended at %END_TIME%. Time elapsed %hh%:%mm%:%ss%.%cc%.
:BuildTimeSkipped
set PATH=%ORIGINAL_PATH%
cd "%~dp0"
exit %IFCOS_SCRIPT_RET%

::::::::::::::::::::::::::::::::::::: Subroutines :::::::::::::::::::::::::::::::::::::

:: DownloadFile - Downloads a file using PowerShell
:: Params: %1 url, %2 destinationDir, %3 filename
:: Required vars:
:: - DEPENDENCY_NAME
:DownloadFile
%PWSH_TOOLS% download_file "%DEPENDENCY_NAME%" "%1" "%2" "%3"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: ExtractArchive - Extracts an archive file using 7-zip
:: Params: %1 filename, %2 destinationDir, %3 dirAfterExtraction
:: Required vars:
:: - DEPENDENCY_NAME
:ExtractArchive
%PWSH_TOOLS% extract_file "%DEPENDENCY_NAME%" "%1" "%2" "%3"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: GitCloneAndCheckoutRevision - Clones a Git repository and checks out a specific revision or tag
:: Params: %1 gitUrl, %2 destDir, %3 revision
:: F.ex. call :GitCloneAndCheckoutRevision https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPENDENCY_DIR%" 064a60b65c2c31b94f013820856bc84fb1937cc6
:: Required vars:
:: - DEPENDENCY_NAME
:GitCloneAndCheckoutRevision
%PWSH_TOOLS% git_clone_and_checkout_revision "%DEPENDENCY_NAME%" "%1" "%2" "%3"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: RunCMake - Runs CMake for a CMake-based project
:: Params: %* cmakeOptions
:: NOTE cd to root CMakeLists.txt folder before calling this if the CMakeLists.txt is not in the repo root.
:RunCMake
call cecho.cmd 0 13 "Running CMake for %DEPENDENCY_NAME%."
IF NOT EXIST %BUILD_DIR%. mkdir %BUILD_DIR%
IF NOT %ERRORLEVEL%==0 GOTO :Error
pushd %BUILD_DIR%
:: TODO make deleting cache a parameter for this subroutine? We probably want to delete the
:: cache always e.g. when we've had new changes in the repository.
IF %BUILD_TYPE%==Rebuild IF EXIST CMakeCache.txt. del CMakeCache.txt

set VS_TOOLSET_CMAKE_ARG=
IF NOT "%VS_TOOLSET_HOST%"=="" (
    set VS_TOOLSET_CMAKE_ARG=-T %VS_TOOLSET_HOST%
)
set COMMAND=cmake .. -G %GENERATOR% -A %VS_PLATFORM% %VS_TOOLSET_CMAKE_ARG% %*
echo %COMMAND%
%COMMAND%
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: Params: %1 buildDir, %2 configuration
:: Required vars:
:: - DEPENDENCY_NAME
:BuildCMakeProject
pushd %1
call cecho.cmd 0 13 "Building %DEPENDENCY_NAME%. Please be patient, this will take a while."
set COMPILE_WITH_WPO_SETTING=
IF NOT %COMPILE_WITH_WPO%==FALSE (
    set COMPILE_WITH_WPO_SETTING=;WholeProgramOptimization=TRUE
)
set COMMAND=cmake --build . --config %2 -- %MSBUILD_MULTIPROC%
echo %COMMAND%
%COMMAND%
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: BuildSolution - Builds/Rebuilds/Cleans a solution using MSBuild
:: Params: %1 solutionName, %2 configuration
:BuildSolution
IF [%~3]==[] (
    set TARGET=%BUILD_TYPE%
) ELSE (
    IF /I %BUILD_TYPE%==Build (
        set TARGET="%3"
    ) ELSE (
        set TARGET="%3:%BUILD_TYPE%"
    )
)

call cecho.cmd 0 13 "Building %TARGET% of %DEPENDENCY_NAME%. Please be patient, this will take a while."

:: whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
set COMPILE_WITH_WPO_SETTING=
IF NOT %COMPILE_WITH_WPO%==FALSE (
    set COMPILE_WITH_WPO_SETTING=;WholeProgramOptimization=TRUE
)
%MSBUILD_CMD% %1 /p:configuration=%2;platform=%VS_PLATFORM%%COMPILE_WITH_WPO_SETTING% /t:"%TARGET%"
exit /b %ERRORLEVEL%

:: Params: %1 buildDir, %2 configuration
:: Required vars:
:: - DEPENDENCY_NAME
:InstallCMakeProject
%PWSH_TOOLS% install_cmake_project "%DEPENDENCY_NAME%" "%1" "%2"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: Checks whether a dependency is already installed for the specified config
:: Doesn't work for dependencies, only for those that need separate Debug/Release installs.
:: Required vars:
:: - DEPENDENCY_NAME
:: - DEPENDENCY_INSTALL_NAME
:: - NEXT_DEPENDENCY_LABEL
:: Always intended to be used with the code below
:: (unfortunately we can't move `GOTO` to the this label too,
:: because of how it would interact with `call` and `exit /b`):
:: ```
:: call :CheckInstallation
:: if %ERRORLEVEL%==200 GOTO %NEXT_DEPENDENCY_LABEL%
:: ```
:CheckInstallation
%PWSH_TOOLS% check_installation %DEPENDENCY_NAME% "%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%"
set RET=%ERRORLEVEL%
if %RET%==200 echo Found existing "%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%" for %BUILD_CFG%, skipping && exit /b 200
if %RET% NEQ 404 GOTO :Error
exit /b 0

:: Required vars:
:: - DEPENDENCY_INSTALL_NAME
:MarkInstallation
%PWSH_TOOLS% mark "%INSTALL_DIR%\%DEPENDENCY_INSTALL_NAME%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: Params:
:: - %1 - VC_VER
:: - %2 - DEPS_DIR
:: - %3 - BOOST_ROOT
:check_boost_vc145_compatibility
%PWSH_TOOLS% check_boost_vc145_compatibility "%1" "%2" "%3"
IF NOT %ERRORLEVEL%==0 GOTO :Error
exit /b 0

:: PrintUsage - Prints usage information
:PrintUsage
call "%~dp0\utils\cecho.cmd" 0 10 "Requirements for a successful execution:"
echo  1. Install PowerShell (preinstalled in Windows ^>= 7) version 5 or higher and make sure 'powershell' is accessible from PATH.
echo   - https://support.microsoft.com/en-us/kb/968929
echo  2. Install Git and make sure 'git' is accessible from PATH.
echo   - https://git-for-windows.github.io/
echo  3. Install CMake and make sure 'cmake' is accessible from PATH.
echo   - http://www.cmake.org/
echo  4. Visual Studio 2013 or newer with C++ toolset.
echo   - https://www.visualstudio.com/
echo  5. Run this batch script with Visual Studio environment variables set.
echo   - https://msdn.microsoft.com/en-us/library/ms229859(v=vs.110).aspx
echo.
echo NB: This script needs to be ran from the directory directly containing it.
echo.
