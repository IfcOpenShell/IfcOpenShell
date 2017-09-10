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

:: Print build configuration information

call cecho.cmd 0 10 "Script configuration:"
call cecho.cmd 0 13 "* CMake Generator`t= '`"%GENERATOR%`'`t
echo   - Passed to CMake -G option.
call cecho.cmd 0 13 "* Target Architecture`t= %TARGET_ARCH%"
echo   - Whether were doing 32-bit (x86) or 64-bit (x64) build.
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

call cecho.cmd black cyan "If you are not ready with the above: type n in the prompt below. Build proceeds on all other inputs!"

set /p do_continue="> "
if "%do_continue%"==n goto :Finish

:: Cache last used CMake generator for other scripts to use
if defined GEN_SHORTHAND echo GEN_SHORTHAND=%GEN_SHORTHAND%>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"

echo.
set START_TIME=%TIME%
echo Build started at %START_TIME%.
set BUILD_STARTED=TRUE
echo.

cd "%DEPS_DIR%"

:: Note all of the depedencies have approriate label so that user can easily skip something if wanted
:: by modifying this file and using goto.
:Boost
set BOOST_VERSION=1.63.0
:: DEPENDENCY_NAME is used for logging and DEPENDENCY_DIR for saving from some redundant typing
set DEPENDENCY_NAME=Boost %BOOST_VERSION%
set DEPENDENCY_DIR="%DEPS_DIR%\boost"
:: Version string with underscores instead of dots.
set BOOST_VER=%BOOST_VERSION:.=_%
REM set BOOST_ROOT=%DEPS_DIR%\boost
REM set BOOST_INCLUDEDIR=%DEPS_DIR%\boost
set BOOST_LIBRARYDIR=%DEPS_DIR%\boost\stage\%VS_PLATFORM%\lib
:: NOTE Also zip download exists, if encountering problems with 7z for some reason.
set ZIP_EXT=7z
set BOOST_ZIP=boost_%BOOST_VER%.%ZIP_EXT%

call :DownloadFile http://downloads.sourceforge.net/project/boost/boost/%BOOST_VERSION%/%BOOST_ZIP% "%DEPS_DIR%" %BOOST_ZIP%

IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %BOOST_ZIP% "%DEPS_DIR%" "%DEPS_DIR%\boost"
IF NOT %ERRORLEVEL%==0 GOTO :Error

:: Build Boost build script
if not exist "%DEPS_DIR%\boost\project-config.jam". (
    cd "%DEPS_DIR%"
    ren boost_%BOOST_VER% boost
    IF NOT EXIST "%DEPS_DIR%\boost\boost.css" GOTO :Error
    cd "%DEPS_DIR%\boost"
    call cecho.cmd 0 13 "Building Boost build script."
    call bootstrap msvc
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)

set BOOST_LIBS=--with-system --with-regex --with-thread --with-program_options --with-date_time --with-iostreams --with-filesystem
:: NOTE Boost is fast to build with limited set of libraries so build it always.
cd "%DEPS_DIR%\boost"
call cecho.cmd 0 13 "Building %DEPENDENCY_NAME% %BOOST_LIBS% Please be patient, this will take a while."
IF EXIST "%DEPS_DIR%\boost\bin.v2\project-cache.jam" del "%DEPS_DIR%\boost\bin.v2\project-cache.jam"
call .\b2 toolset=msvc runtime-link=static address-model=%ARCH_BITS% -j%IFCOS_NUM_BUILD_PROCS% ^
    variant=%DEBUG_OR_RELEASE_LOWERCASE% %BOOST_LIBS% stage --stagedir=stage/vs%VS_VER%-%VS_PLATFORM% 
IF NOT %ERRORLEVEL%==0 GOTO :Error

:ICU
set DEPENDENCY_NAME=ICU
set DEPENDENCY_DIR=N/A
set ICU_VER=58.2
set ICU_ZIP=icu-%ICU_VER%-vs%VS_VER%.7z
cd "%DEPS_DIR%"
call :DownloadFile http://www.npcglib.org/~stathis/downloads/%ICU_ZIP% "%DEPS_DIR%" %ICU_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %ICU_ZIP% "%DEPS_DIR%" "%INSTALL_DIR%\icu"
IF NOT %ERRORLEVEL%==0 GOTO :Error
:: Rename lib and bin directories to predictable form
IF EXIST "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%". (
    pushd "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%"
    IF EXIST bin. ren bin bin%ARCH_BITS%"
    IF EXIST lib. ren lib lib%ARCH_BITS%"
    popd
)

IF EXIST "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\". (
    robocopy "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\include" "%INSTALL_DIR%\icu\include" /E /IS /njh /njs
    IF NOT EXIST "%INSTALL_DIR%\icu\lib". mkdir "%INSTALL_DIR%\icu\lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicutest%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icutest%POSTFIX_D%.lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicutu%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icutu%POSTFIX_D%.lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicuuc%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuuc%POSTFIX_D%.lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicudt%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icudt%POSTFIX_D%.lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicuin%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuin%POSTFIX_D%.lib"
    copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicuio%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuio%POSTFIX_D%.lib"
    REM NOTE not available in 58.2 at least, nor needed by us.
    REM copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\sicule%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icule%POSTFIX_D%.lib"
    REM copy /y "%DEPS_DIR%\icu-%ICU_VER%-vs%VS_VER%\lib%ARCH_BITS%\siculx%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\iculx%POSTFIX_D%.lib"
)

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
set OCC_INCLUDE_DIR=%INSTALL_DIR%\opencascade\inc>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
set OCC_LIBRARY_DIR=%INSTALL_DIR%\opencascade\win%ARCH_BITS%\lib>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
echo OCC_INCLUDE_DIR=%OCC_INCLUDE_DIR%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
echo OCC_LIBRARY_DIR=%OCC_LIBRARY_DIR%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
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

set DEPENDENCY_NAME=Open CASCADE 7.1.0
set OCCT_FILENAME=occt-89aebde
set DEPENDENCY_DIR=%DEPS_DIR%\%OCCT_FILENAME%
cd "%DEPS_DIR%"
call :DownloadFile "http://git.dev.opencascade.org/gitweb/?p=occt.git;a=snapshot;h=89aebde;sf=tgz" "%DEPS_DIR%" %OCCT_FILENAME%.tar.gz
if not %ERRORLEVEL%==0 goto :Error

if exist "%DEPS_DIR%\%OCCT_FILENAME%" (
    :: TK: I am having a hard time to reinitialize OCCT, because the directory ends up being recreated by a prior cmake step, even if manually deleted.
    :: Therefore check if the directory contains a full checkout [using a single file as proxy] and delete the directory tree if it is not.
    if not exist "%DEPS_DIR%\%OCCT_FILENAME%\OCCT_LGPL_EXCEPTION.txt". rd /s/q "%DEPS_DIR%\%OCCT_FILENAME%"
)

call :ExtractArchive %OCCT_FILENAME%.tar.gz "%DEPS_DIR%" "%DEPENDENCY_DIR%"
if not %ERRORLEVEL%==0 goto :Error
call :ExtractArchive %OCCT_FILENAME%.tar "%DEPS_DIR%" "%DEPENDENCY_DIR%"
if not %ERRORLEVEL%==0 goto :Error

set DEPENDENCY_NAME=Additional files
:: Somehow these two files are not present in the downloaded
:: snapshot. Path names being too long for gitweb snapshot?
call :DownloadFile "http://git.dev.opencascade.org/gitweb/?p=occt.git;a=blob_plain;hb=89aebdea8d6f4d15cfc50e9458cd8e2e25022326;f=src/RWStepVisual/RWStepVisual_RWCharacterizedObjectAndCharacterizedRepresentationAndDraughtingModelAndRepresentation.cxx" "%OCCT_FILENAME%\src\RWStepVisual" RWStepVisual_RWCharacterizedObjectAndCharacterizedRepresentationAndDraughtingModelAndRepresentation.cxx
if not %ERRORLEVEL%==0 goto :Error
call :DownloadFile "http://git.dev.opencascade.org/gitweb/?p=occt.git;a=blob_plain;hb=89aebdea8d6f4d15cfc50e9458cd8e2e25022326;f=src/RWStepVisual/RWStepVisual_RWCharacterizedObjectAndCharacterizedRepresentationAndDraughtingModelAndRepresentation.hxx" "%OCCT_FILENAME%\src\RWStepVisual" RWStepVisual_RWCharacterizedObjectAndCharacterizedRepresentationAndDraughtingModelAndRepresentation.hxx
if not %ERRORLEVEL%==0 goto :Error
set DEPENDENCY_NAME=Open CASCADE 7.1.0

:: Patching always blindly would trigger a rebuild each time
findstr IfcOpenShell "%DEPENDENCY_DIR%\CMakeLists.txt">NUL
if not %ERRORLEVEL%==0 (
    echo Patching %DEPENDENCY_NAME%'s CMake files
    REM OCCT insists on finding FreeType DLL even if using static FreeType build + define HAVE_NO_DLL
    copy /y "%~dp0patches\89aebde_CMakeLists.txt" "%DEPENDENCY_DIR%\CMakeLists.txt"
    REM Patch OCCT to be built against the static MSVC run-time.
    copy /y "%~dp0patches\89aebde_adm-cmake-occt_defs_flags.cmake" "%DEPENDENCY_DIR%\adm\cmake\occt_defs_flags.cmake"
    REM OCCT tries to deploy PDBs from the bin directory even if static build is used.
    copy /y "%~dp0patches\89aebde_adm-cmake-occt_toolkit.cmake" "%DEPENDENCY_DIR%\adm\cmake\occt_toolkit.cmake"
    REM Patch header file for HAVE_NO_DLL
    copy /y "%~dp0patches\89aebde_Standard_Macro.hxx" "%DEPENDENCY_DIR%\src\Standard\Standard_Macro.hxx"
    REM NOTE If adding a new patch, adjust the checks above and below accordingly
)
findstr IfcOpenShell "%DEPENDENCY_DIR%\CMakeLists.txt">NUL
if not %ERRORLEVEL%==0 goto :Error

cd "%DEPENDENCY_DIR%"
call :RunCMake -DINSTALL_DIR="%INSTALL_DIR%\opencascade" -DBUILD_LIBRARY_TYPE="Static" -DCMAKE_DEBUG_POSTFIX=d ^
    -DBUILD_MODULE_Draw=0 -D3RDPARTY_FREETYPE_DIR="%INSTALL_DIR%\freetype"
if not %ERRORLEVEL%==0 goto :Error
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\OCCT.sln" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
if not %ERRORLEVEL%==0 goto :Error
:: Use a single lib directory for for release and debug libraries as is done with OCE
if not exist "%OCC_LIBRARY_DIR%". mkdir "%OCC_LIBRARY_DIR%"
:: NOTE OCCT (at least occt-V7_0_0-9059ca1) directory creation code is hardcoded and doesn't seem handle future VC versions
set OCCT_VC_VER=%VC_VER%
IF %OCCT_VC_VER% GTR 14 (
    set OCCT_VC_VER=14
)
move /y "%INSTALL_DIR%\opencascade\win%ARCH_BITS%\vc%OCCT_VC_VER%\libi\*.*" "%OCC_LIBRARY_DIR%"
move /y "%INSTALL_DIR%\opencascade\win%ARCH_BITS%\vc%OCCT_VC_VER%\libd\*.*" "%OCC_LIBRARY_DIR%"
rmdir /s /q "%INSTALL_DIR%\opencascade\win%ARCH_BITS%\vc%OCCT_VC_VER%"
:: Removed unneeded bits
rmdir /s /q "%INSTALL_DIR%\opencascade\data"
rmdir /s /q "%INSTALL_DIR%\opencascade\samples"
del "%INSTALL_DIR%\opencascade\*.bat"

goto :Python

:OCE
set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
echo OCC_INCLUDE_DIR=%OCC_INCLUDE_DIR%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
echo OCC_LIBRARY_DIR=%OCC_LIBRARY_DIR%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"

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
    echo PY_VER_MAJOR_MINOR=%PY_VER_MAJOR_MINOR%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"
    echo PYTHONHOME=%PYTHONHOME%>>"%~dp0\BuildDepsCache-%TARGET_ARCH%.txt"

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
set SWIG_VERSION=3.0.7
set DEPENDENCY_NAME=SWIG %SWIG_VERSION%
set DEPENDENCY_DIR=N/A
set SWIG_ZIP=swigwin-%SWIG_VERSION%.zip
cd "%DEPS_DIR%"
call :DownloadFile http://sourceforge.net/projects/swig/files/swigwin/swigwin-%SWIG_VERSION%/%SWIG_ZIP% "%DEPS_DIR%" %SWIG_ZIP%
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
    powershell -Command "$webClient = new-object System.Net.WebClient; $webClient.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials; $webClient.DownloadFile('%1', '%3')"
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
    7za x %1 -y -o%2
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
cmake .. -G %GENERATOR% %*
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: TODO add BuildCMakeProject which utilizes cmake --build

:: BuildSolution - Builds/Rebuilds/Cleans a solution using MSBuild
:: Params: %1 solutioName, %2 configuration
:BuildSolution
call cecho.cmd 0 13 "Building %2 %DEPENDENCY_NAME%. Please be patient, this will take a while."
%MSBUILD_CMD% %1 /p:configuration=%2;platform=%VS_PLATFORM%
exit /b %ERRORLEVEL%

:: InstallCMakeProject - Builds the INSTALL project of CMake-based project
:: Params: %1 buildDir, %2 == configuration
:: NOTE the actual install dir is set during cmake run.
:: TODO Utilize cmake --build --target INSTALL
:InstallCMakeProject
pushd %1
call cecho.cmd 0 13 "Installing %2 %DEPENDENCY_NAME%. Please be patient, this will take a while."
%INSTALL_CMD% INSTALL.%VCPROJ_FILE_EXT% /p:configuration=%2;platform=%VS_PLATFORM%
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: PrintUsage - Prints usage information
:PrintUsage
call "%~dp0\utils\cecho.cmd" 0 10 "Requirements for a successful execution:"
echo  1. Install PowerShell (preinstalled in Windows ^>= 7) and make sure 'powershell' is accessible from PATH.
echo   - https://support.microsoft.com/en-us/kb/968929
echo  2. Install Git and make sure 'git' is accessible from PATH.
echo   - https://git-for-windows.github.io/
echo  3. Install CMake and make sure 'cmake' is accessible from PATH.
echo   - http://www.cmake.org/
echo  4. Visual Studio 2008 or newer (2013 or newer recommended) with C++ toolset.
echo   - https://www.visualstudio.com/
echo  5. Run this batch script with Visual Studio environment variables set.
echo   - https://msdn.microsoft.com/en-us/library/ms229859(v=vs.110).aspx
echo.
