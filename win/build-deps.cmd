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

@echo off
echo.

for %%Q in ("%~dp0\.") DO set "batpath=%%~fQ"

if NOT "%CD%" == "%batpath%" (
    GOTO :ErrorAndPrintUsage
)


set PROJECT_NAME=IfcOpenShell
call utils\cecho.cmd 15 0 "This script fetches and builds all %PROJECT_NAME% dependencies"
echo.

:: Enable the delayed environment variable expansion needed in vs-cfg.cmd.
setlocal EnableDelayedExpansion

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
IF NOT DEFINED IFCOS_USE_OCCT set IFCOS_USE_OCCT=TRUE
IF NOT DEFINED IFCOS_INSTALL_PYTHON set IFCOS_INSTALL_PYTHON=TRUE
IF NOT DEFINED IFCOS_USE_PYTHON2 set IFCOS_USE_PYTHON2=FALSE
IF NOT DEFINED IFCOS_NUM_BUILD_PROCS set IFCOS_NUM_BUILD_PROCS=%NUMBER_OF_PROCESSORS%

:: For subroutines
set MSBUILD_CMD=MSBuild.exe /nologo /m:%IFCOS_NUM_BUILD_PROCS% /t:%BUILD_TYPE%
REM /clp:ErrorsOnly;WarningsOnly
:: Note BUILD_TYPE not passed, Clean e.g. wouldn't delete the installed files.
set INSTALL_CMD=MSBuild.exe /nologo /m:%IFCOS_NUM_BUILD_PROCS%

echo.

:: Check that required tools are in PATH
FOR %%i IN (powershell git cmake) DO (
    where.exe %%i 1> NUL 2> NUL || call cecho.cmd 0 12 "Required tool `'%%i`' not installed or not added to PATH" && goto :ErrorAndPrintUsage
)

:: Check powershell version
powershell -c "exit $PSVersionTable.PSVersion.Major -lt 5"
IF NOT %ERRORLEVEL%==0 call cecho.cmd 0 12 "Powershell version 5 or higher required" && goto :ErrorAndPrintUsage

cmake --version | findstr version > temp.txt
set /p CMAKE_VERSION=<temp.txt
del temp.txt
if "%CMAKE_VERSION%" LSS "cmake version 3.11.4" (
    echo "CMake v3.11.4 or higher is required"
    goto :ErrorAndPrintUsage
)

:: Print build configuration information

call cecho.cmd 0 10 "Script configuration:"
call cecho.cmd 0 13 "* CMake Generator`t= '`"%GENERATOR%`'`t
echo   - Passed to CMake -G option.
call cecho.cmd 0 13 "* Target Architecture`t= %TARGET_ARCH%"
echo   - Whether were doing 32-bit (x86) or 64-bit (x64) build.
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
echo     Defaults to Build if not specified. Rebuild/Clean also uninstalls Python (if it was installed by this script).
call cecho.cmd 0 13 "* IFCOS_USE_OCCT`t= %IFCOS_USE_OCCT%"
echo   - Use the official Open CASCADE instead of the community edition.
call cecho.cmd 0 13 "* IFCOS_INSTALL_PYTHON`t= %IFCOS_INSTALL_PYTHON%"
echo   - Download and install Python.
echo     Set to something other than TRUE if you wish to use an already installed version of Python.
call cecho.cmd 0 13 "* IFCOS_USE_PYTHON2`t= %IFCOS_USE_PYTHON2%"
echo   - Use Python 2 instead of 3.
echo     Set to TRUE if you wish to use Python 2 instead of 3. Has no effect if IFCOS_INSTALL_PYTHON is not TRUE.
call cecho.cmd 0 13 "* IFCOS_NUM_BUILD_PROCS`t= %IFCOS_NUM_BUILD_PROCS%"
echo   - How many MSBuild.exe processes may be run in parallel.
echo     Defaults to NUMBER_OF_PROCESSORS. Used also by other IfcOpenShell build scripts.
echo.

call :PrintUsage

call cecho.cmd 0 14 "Warning: You will need roughly 8 GB of disk space to proceed `(VS 2015 x64 RelWithDebInfo`)."
echo.

call cecho.cmd black cyan "If you are not ready with the above: type `'n`' in the prompt below. Build proceeds on all other inputs!"

set /p do_continue="> "
if "%do_continue%"=="n" goto :Finish

:: Cache last used CMake generator for other scripts to use
if defined GEN_SHORTHAND echo GEN_SHORTHAND=%GEN_SHORTHAND%>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

echo.
set START_TIME=%TIME%
echo Build started at %START_TIME%.
set BUILD_STARTED=TRUE
echo.

cd "%DEPS_DIR%"

:: Note all of the dependencies have appropriate label so that user can easily skip something if wanted
:: by modifying this file and using goto.
:Boost
:: NOTE Boost < 1.64 doesn't work without tricks if the user has only VS 2017 installed and no earlier versions.
set BOOST_VERSION=1.74.0
:: Version string with underscores instead of dots.
set BOOST_VER=%BOOST_VERSION:.=_%
:: DEPENDENCY_NAME is used for logging and DEPENDENCY_DIR for saving from some redundant typing
set DEPENDENCY_NAME=Boost %BOOST_VERSION%
set DEPENDENCY_DIR=%DEPS_DIR%\boost_%BOOST_VER%
set BOOST_LIBRARYDIR=%DEPENDENCY_DIR%\stage\%GEN_SHORTHAND%\lib
:: NOTE Also zip download exists, if encountering problems with 7z for some reason.
set ZIP_EXT=7z
set BOOST_ZIP=boost_%BOOST_VER%.%ZIP_EXT%

:: On 2021-05-11 Boost changed download address:
:: Instead of: https://dl.bintray.com/boostorg/release/ you should use https://boostorg.jfrog.io/artifactory/main/release/ to retrieve boost releases.

rem call :DownloadFile https://dl.bintray.com/boostorg/release/%BOOST_VERSION%/source/%BOOST_ZIP% "%DEPS_DIR%" %BOOST_ZIP%
call :DownloadFile https://boostorg.jfrog.io/artifactory/main/release/%BOOST_VERSION%/source/%BOOST_ZIP% "%DEPS_DIR%" %BOOST_ZIP%

IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %BOOST_ZIP% "%DEPS_DIR%" "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error

:: Build Boost build script
if not exist "%DEPENDENCY_DIR%\project-config.jam". (
    cd "%DEPS_DIR%"
    IF NOT EXIST "%DEPENDENCY_DIR%\boost.css" GOTO :Error
    cd "%DEPENDENCY_DIR%"
    call cecho.cmd 0 13 "Building Boost build script."
    call bootstrap %BOOST_BOOTSTRAP_VER%
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)

set BOOST_LIBS=--with-system --with-regex --with-thread --with-program_options --with-date_time --with-iostreams --with-filesystem
:: NOTE Boost is fast to build with limited set of libraries so build it always.
cd "%DEPENDENCY_DIR%"
call cecho.cmd 0 13 "Building %DEPENDENCY_NAME% %BOOST_LIBS% Please be patient, this will take a while."
IF EXIST "%DEPENDENCY_DIR%\bin.v2\project-cache.jam" del "%DEPS_DIR%\boost\bin.v2\project-cache.jam"

call .\b2 toolset=%BOOST_TOOLSET% runtime-link=static address-model=%ARCH_BITS% --abbreviate-paths -j%IFCOS_NUM_BUILD_PROCS% ^
    variant=%DEBUG_OR_RELEASE_LOWERCASE% %BOOST_WIN_API% %BOOST_LIBS% stage --stagedir=stage/%GEN_SHORTHAND% 

IF NOT %ERRORLEVEL%==0 GOTO :Error

:JSON
set DEPENDENCY_NAME=JSON for Modern C++ v3.6.1
IF NOT EXIST "%INSTALL_DIR%\json\nlohmann". mkdir "%INSTALL_DIR%\json\nlohmann"
call :DownloadFile https://github.com/nlohmann/json/releases/download/v3.6.1/json.hpp "%INSTALL_DIR%\json\nlohmann" json.hpp

:OpenCOLLADA
:: Note OpenCOLLADA has only Release and Debug builds.
set DEPENDENCY_NAME=OpenCOLLADA
set DEPENDENCY_DIR=%DEPS_DIR%\OpenCOLLADA
:: Use a fixed revision in order to prevent introducing breaking changes
call :GitCloneAndCheckoutRevision https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPENDENCY_DIR%" 064a60b65c2c31b94f013820856bc84fb1937cc6
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"
:: Debug build of OpenCOLLADAValidator fails (https://github.com/KhronosGroup/OpenCOLLADA/issues/377) so
:: so disable it from the build altogether as we have no use for it
findstr #add_subdirectory(COLLADAValidator) CMakeLists.txt>NUL
IF NOT %ERRORLEVEL%==0 git apply --reject --whitespace=fix "%~dp0patches\OpenCOLLADA_CMakeLists.txt.patch"
:: NOTE OpenCOLLADA has been observed to have problems with switching between debug and release builds so
:: uncomment to following line in order to delete the CMakeCache.txt always if experiencing problems.
REM IF EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt". del "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt"
:: NOTE Enforce that the embedded LibXml2 and PCRE are used as there might be problems with arbitrary versions of the libraries.
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\OpenCOLLADA" -DUSE_STATIC_MSVC_RUNTIME=1 -DCMAKE_DEBUG_POSTFIX=d ^
               -DLIBXML2_LIBRARIES="" -DLIBXML2_INCLUDE_DIR="" -DPCRE_INCLUDE_DIR="" -DPCRE_LIBRARIES=""
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM IF NOT EXIST "%DEPS_DIR%\OpenCOLLADA\%BUILD_DIR%\lib\%DEBUG_OR_RELEASE%\OpenCOLLADASaxFrameworkLoader.lib".
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\OPENCOLLADA.sln" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error

if %IFCOS_USE_OCCT%==FALSE goto :OCE
:OCCT
set OCCT_VERSION=7.3.0p3
SET OCCT_VER=V%OCCT_VERSION:.=_%

set OCC_INCLUDE_DIR=%INSTALL_DIR%\opencascade-%OCCT_VERSION%\inc>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
set OCC_LIBRARY_DIR=%INSTALL_DIR%\opencascade-%OCCT_VERSION%\win%ARCH_BITS%\lib>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
echo OCC_INCLUDE_DIR=%OCC_INCLUDE_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
echo OCC_LIBRARY_DIR=%OCC_LIBRARY_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

:: OCCT has many dependencies but FreeType is the only mandatory
set DEPENDENCY_NAME=FreeType
set DEPENDENCY_DIR=%DEPS_DIR%\freetype-2.6.5
set FREETYPE_ZIP=ft265.zip
cd "%DEPS_DIR%"
call :DownloadFile http://download.savannah.gnu.org/releases/freetype/%FREETYPE_ZIP% "%DEPS_DIR%" %FREETYPE_ZIP%
if not %ERRORLEVEL%==0 goto :Error
call :ExtractArchive %FREETYPE_ZIP% "%DEPS_DIR%" "%DEPENDENCY_DIR%"
if not %ERRORLEVEL%==0 goto :Error
cd "%DEPENDENCY_DIR%"
:: NOTE FreeType is built as a static library by default
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\freetype"
if not %ERRORLEVEL%==0 goto :Error
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\freetype.sln" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error 

set DEPENDENCY_NAME=Open CASCADE %OCCT_VERSION%
set DEPENDENCY_DIR=%DEPS_DIR%\occt_git
cd "%DEPS_DIR%"
call :GitCloneAndCheckoutRevision https://git.dev.opencascade.org/repos/occt.git "%DEPENDENCY_DIR%" %OCCT_VER%
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
call :RunCMake -DINSTALL_DIR="%INSTALL_DIR%\opencascade-%OCCT_VERSION%" -DBUILD_LIBRARY_TYPE="Static" -DCMAKE_DEBUG_POSTFIX=d ^
    -DBUILD_MODULE_Draw=0 -D3RDPARTY_FREETYPE_DIR="%INSTALL_DIR%\freetype"
if not %ERRORLEVEL%==0 goto :Error

:: whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
IF %ARCH_BITS%==32 (
	IF %BUILD_CFG%==Release (
		SET COMPILE_WITH_WPO=TRUE
	)
)

call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\OCCT.sln" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error

SET COMPILE_WITH_WPO=FALSE

:: Use a single lib directory for release and debug libraries as is done with OCE
if not exist "%OCC_LIBRARY_DIR%". mkdir "%OCC_LIBRARY_DIR%"
:: NOTE OCCT (at least occt-V7_0_0-9059ca1) directory creation code is hardcoded and doesn't seem handle future VC versions
set OCCT_VC_VER=%VC_VER%
IF %OCCT_VC_VER% GTR 14 (
    set OCCT_VC_VER=14
)
move /y "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\win%ARCH_BITS%\vc%OCCT_VC_VER%\libi\*.*" "%OCC_LIBRARY_DIR%"
move /y "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\win%ARCH_BITS%\vc%OCCT_VC_VER%\libd\*.*" "%OCC_LIBRARY_DIR%"
move /y "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\win%ARCH_BITS%\vc%OCCT_VC_VER%\lib\*.*" "%OCC_LIBRARY_DIR%"
rmdir /s /q "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\win%ARCH_BITS%\vc%OCCT_VC_VER%"
:: Removed unneeded bits
rmdir /s /q "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\data"
rmdir /s /q "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\samples"
del "%INSTALL_DIR%\opencascade-%OCCT_VERSION%\*.bat"

goto :Python

:OCE
set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
echo OCC_INCLUDE_DIR=%OCC_INCLUDE_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
echo OCC_LIBRARY_DIR=%OCC_LIBRARY_DIR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

set DEPENDENCY_NAME=Open CASCADE Community Edition
set DEPENDENCY_DIR=%DEPS_DIR%\oce
set OCE_VERSION=OCE-0.18
call :GitCloneAndCheckoutRevision https://github.com/tpaviot/oce.git "%DEPENDENCY_DIR%" %OCE_VERSION%
IF NOT %ERRORLEVEL%==0 GOTO :Error
:: Use the oce-win-bundle for OCE's dependencies
call :GitCloneOrPullRepository https://github.com/QbProg/oce-win-bundle.git "%DEPENDENCY_DIR%\oce-win-bundle"
IF NOT %ERRORLEVEL%==0 GOTO :Error

cd "%DEPENDENCY_DIR%"
:: NOTE Specify OCE_NO_LIBRARY_VERSION as rc.exe can fail due to long filenames and huge command-line parameter
:: input (more than 32,000 characters). Could maybe try using subst for the build dir to overcome this.
call :RunCMake  -DOCE_BUILD_SHARED_LIB=0 -DOCE_INSTALL_PREFIX="%INSTALL_DIR%\oce" -DOCE_TESTING=0 ^
                -DOCE_NO_LIBRARY_VERSION=1 -DOCE_USE_STATIC_MSVC_RUNTIME=1
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\OCE.sln" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:Python
:: TODO Update to 3.5 when it's released as it will have an option to install debug libraries.
:: NOTE If updating the default Python version, change PY_VER_MAJOR_MINOR accordingly in run-cmake.bat
set PYTHON_VERSION=3.4.3
IF "%IFCOS_USE_PYTHON2%"=="TRUE" set PYTHON_VERSION=2.7.10
set PY_VER_MAJOR_MINOR=%PYTHON_VERSION:~0,3%
set PY_VER_MAJOR_MINOR=%PY_VER_MAJOR_MINOR:.=%
set PYTHONHOME=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%

set DEPENDENCY_NAME=Python %PYTHON_VERSION%
set DEPENDENCY_DIR=N/A
set PYTHON_AMD64_POSTFIX=.amd64
:: NOTE/TODO Beginning from 3.5.0: set PYTHON_AMD64_POSTFIX=-amd64
IF NOT %TARGET_ARCH%==x64 set PYTHON_AMD64_POSTFIX=
set PYTHON_INSTALLER=python-%PYTHON_VERSION%%PYTHON_AMD64_POSTFIX%.msi
:: NOTE/TODO 3.5.0 doesn't use MSI any longer, but exe: set PYTHON_INSTALLER=python-%PYTHON_VERSION%%PYTHON_AMD64_POSTFIX%.exe
IF "%IFCOS_INSTALL_PYTHON%"=="TRUE" (
    REM Store Python versions to BuildDepsCache.txt for run-cmake.bat
    echo PY_VER_MAJOR_MINOR=%PY_VER_MAJOR_MINOR%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"
    echo PYTHONHOME=%PYTHONHOME%>>"%~dp0\%BUILD_DEPS_CACHE_PATH%"

    cd "%DEPS_DIR%"
    call :DownloadFile https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER% "%DEPS_DIR%" %PYTHON_INSTALLER%
    IF NOT %ERRORLEVEL%==0 GOTO :Error
    REM Uninstall if build Rebuild/Clean used
    IF NOT %BUILD_TYPE%==Build (
        call cecho.cmd 0 13 "Uninstalling %DEPENDENCY_NAME%. Please be patient, this will take a while."
        msiexec /x %PYTHON_INSTALLER% /qn
    )

    IF NOT EXIST "%PYTHONHOME%". (
        call cecho.cmd 0 13 "Installing %DEPENDENCY_NAME%. Please be patient, this will take a while."
        msiexec /qn /i %PYTHON_INSTALLER% TARGETDIR="%PYTHONHOME%"
    ) ELSE (
        call cecho.cmd 0 13 "%DEPENDENCY_NAME% already installed. Skipping."
    )
) ELSE (
    call cecho.cmd 0 13 "IFCOS_INSTALL_PYTHON not true, skipping installation of Python."
)

:SWIG
set SWIG_VERSION=3.0.12
set DEPENDENCY_NAME=SWIG %SWIG_VERSION%
set DEPENDENCY_DIR=N/A
set SWIG_ZIP=swigwin-%SWIG_VERSION%.zip
cd "%DEPS_DIR%"
call :DownloadFile https://sourceforge.net/projects/swig/files/swigwin/swigwin-%SWIG_VERSION%/%SWIG_ZIP% "%DEPS_DIR%" %SWIG_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %SWIG_ZIP% "%DEPS_DIR%" "%DEPS_DIR%\swigwin"
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF EXIST "%DEPS_DIR%\swigwin-%SWIG_VERSION%". (
    pushd "%DEPS_DIR%"
    ren swigwin-%SWIG_VERSION% swigwin
    popd
)
IF EXIST "%DEPS_DIR%\swigwin\". robocopy "%DEPS_DIR%\swigwin" "%INSTALL_DIR%\swigwin" /E /IS /MOVE /njh /njs

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
call "%~dp0\utils\cecho.cmd" 0 12 "An error occurred! Aborting!"
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
exit /b %IFCOS_SCRIPT_RET%

::::::::::::::::::::::::::::::::::::: Subroutines :::::::::::::::::::::::::::::::::::::

:: DownloadFile - Downloads a file using PowerShell
:: Params: %1 url, %2 destinationDir, %3 filename
:DownloadFile
pushd "%2"
if not exist "%~3". (
    call cecho.cmd 0 13 "Downloading %DEPENDENCY_NAME% into %~2."
    powershell -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; $webClient = new-object System.Net.WebClient; $webClient.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials; $webClient.DownloadFile('%1', '%3')"
    REM Old wget version in case someone has problem with PowerShell: wget --no-check-certificate %1
) else (
    call cecho.cmd 0 13 "%DEPENDENCY_NAME% already downloaded. Skipping."
)
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: ExtractArchive - Extracts an archive file using 7-zip
:: Params: %1 filename, %2 destinationDir, %3 dirAfterExtraction
:ExtractArchive
if not exist "%~3". (
    call cecho.cmd 0 13 "Extracting %DEPENDENCY_NAME% into %~2."
    7za x %1 -y -o%2 > nul
) else (
    call cecho.cmd 0 13 "%DEPENDENCY_NAME% already extracted into %~3. Skipping."
)
exit /b %ERRORLEVEL%

:: GitCloneOrPullRepository - Clones or pulls (if repository already cloned) a Git repository
:: Params: %1 gitUrl, %2 destDir
:: F.ex. call :GitCloneRepository https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPS_DIR%\OpenCOLLADA\"
:GitCloneOrPullRepository
if not exist "%~2". (
    call cecho.cmd 0 13 "Cloning %DEPENDENCY_NAME% into %~2."
    pushd "%DEPS_DIR%"
    call git clone %1 %2
    set RET=%ERRORLEVEL%
) else (
    call cecho.cmd 0 13 "%DEPENDENCY_NAME% already cloned. Pulling latest changes."
    pushd %2
    call git pull
    set RET=0
)
popd
exit /b %RET%

:: GitCloneAndCheckoutRevision - Clones a Git repository and checks out a specific revision or tag
:: Params: %1 gitUrl, %2 destDir, %3 revision
:: F.ex. call :GitCloneAndCheckoutRevision https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPENDENCY_DIR%" 064a60b65c2c31b94f013820856bc84fb1937cc6
:GitCloneAndCheckoutRevision
if not exist "%~2". (
    call cecho.cmd 0 13 "Cloning %DEPENDENCY_NAME% into %~2."
    pushd "%DEPS_DIR%"
    call git clone %1 %2
    set RET=%ERRORLEVEL%
    if not %RET%==0 exit /b %RET%
    popd
) else (
    call cecho.cmd 0 13 "%DEPENDENCY_NAME% already cloned."
    set RET=0
)
pushd "%2"
call git fetch
call cecho.cmd 0 13 "Checking out %DEPENDENCY_NAME% revision %3."
call git checkout %3
set RET=%ERRORLEVEL%
popd
exit /b %RET%
 
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

IF NOT "%VS_TOOLSET_HOST%"=="" (
    cmake .. -G %GENERATOR% -A %VS_PLATFORM% -T %VS_TOOLSET_HOST% %*
) ELSE (
    cmake .. -G %GENERATOR% -A %VS_PLATFORM% %*
)

set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: TODO add BuildCMakeProject which utilizes cmake --build

:: BuildSolution - Builds/Rebuilds/Cleans a solution using MSBuild
:: Params: %1 solutioName, %2 configuration
:BuildSolution
call cecho.cmd 0 13 "Building %2 %DEPENDENCY_NAME%. Please be patient, this will take a while."

:: whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
IF %COMPILE_WITH_WPO%==FALSE (
	%MSBUILD_CMD% %1 /p:configuration=%2;platform=%VS_PLATFORM%
) ELSE (
	%MSBUILD_CMD% %1 /p:configuration=%2;platform=%VS_PLATFORM%;WholeProgramOptimization=TRUE
)
exit /b %ERRORLEVEL%

:: InstallCMakeProject - Builds the INSTALL project of CMake-based project
:: Params: %1 buildDir, %2 == configuration
:: NOTE the actual install dir is set during cmake run.
:: TODO Utilize cmake --build --target INSTALL
:InstallCMakeProject
pushd %1
call cecho.cmd 0 13 "Installing %2 %DEPENDENCY_NAME%. Please be patient, this will take a while."

:: whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0
IF %COMPILE_WITH_WPO%==FALSE (
	%INSTALL_CMD% INSTALL.%VCPROJ_FILE_EXT% /p:configuration=%2;platform=%VS_PLATFORM%
) ELSE (
	%INSTALL_CMD% INSTALL.%VCPROJ_FILE_EXT% /p:configuration=%2;platform=%VS_PLATFORM%;WholeProgramOptimization=TRUE
)
set RET=%ERRORLEVEL%
popd
exit /b %RET%

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
