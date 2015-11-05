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
:: the GENERATOR_DEFAULT will be used for %1 and BUILD_CFG_DEFAULT for %2 (both set in vs-cfg.cmd)
:: Optionally a build type (Build/Rebuild/Clean) can be passed as %3.

@echo off
echo.

set THISDIR=%CD%

:: Enable the delayed environment variable expansion needed in vs-cfg.cmd.
setlocal EnableDelayedExpansion

:: Make sure vcvarsall.bat is called and dev env set is up.
IF "%VSINSTALLDIR%"=="" (
   utils\cecho {0C}Visual Studio environment variables not set - cannot proceed!{# #}{\n}
   GOTO :Error
)

set PROJECT_NAME=IfcOpenShell

utils\cecho {F0}This script fetches and builds all %PROJECT_NAME% dependencies{# #}{\n}
echo.

:: Set up variables depending on the used Visual Studio version
call vs-cfg.cmd %1 %2
IF NOT %ERRORLEVEL%==0 GOTO :Error

set BUILD_TYPE=%3

IF %GENERATOR%=="" (
   cecho {0C}GENERATOR not specified - cannot proceed!{# #}{\n}
   GOTO :Error
)

IF "%BUILD_TYPE%"=="" set BUILD_TYPE=Build

IF NOT "!BUILD_TYPE!"=="Build" IF NOT "!BUILD_TYPE!"=="Rebuild" IF NOT "!BUILD_TYPE!"=="Clean" (
    utils\cecho {0C}Invalid build type passed: !BUILD_TYPE!. Cannot proceed, aborting!{# #}{\n}
    GOTO :Error
)

:: Make sure deps and install folders exists.
IF NOT EXIST %DEPS_DIR%. mkdir %DEPS_DIR%
IF NOT EXIST %INSTALL_DIR%. mkdir %INSTALL_DIR%

:: If we use VS2008, framework path (for MSBuild) may not be correctly set. Manually attempt to add in that case
IF %VS_VER%==2008 set PATH=C:\Windows\Microsoft.NET\Framework\v3.5;%PATH%

:: User-configurable build options
IF "%IFCOS_INSTALL_PYTHON%"=="" set IFCOS_INSTALL_PYTHON=TRUE
IF "%IFCOS_USE_PYTHON2%"=="" set IFCOS_USE_PYTHON2=FALSE
IF "%IFCOS_NUM_BUILD_PROCESSES%"=="" set IFCOS_NUM_BUILD_PROCESSES=%NUMBER_OF_PROCESSORS%

:: For subroutines
set MSBUILD_CMD=MSBuild.exe /nologo /m:%IFCOS_NUM_BUILD_PROCESSES% /t:%BUILD_TYPE%
REM /clp:ErrorsOnly;WarningsOnly
:: Note BUILD_TYPE not passed, Clean e.g. wouldn't delete the installed files.
set INSTALL_CMD=MSBuild.exe /nologo /m:%IFCOS_NUM_BUILD_PROCESSES%
set BUILD_DIR=build-vs%VS_VER%-%TARGET_ARCH%

REM echo.
REM cecho {F0}This script fetches and builds all %PROJECT_NAME% dependencies{# #}{\n}

:: Print build configuration information
echo.
cecho {0A}Script configuration:{# #}{\n}
cecho {0D}  CMake Generator           = %GENERATOR%{# #}{\n}
echo    - Passed to CMake -G option.
cecho {0D}  Target Architecture       = %TARGET_ARCH%{# #}{\n}
echo    - Whether were doing 32-bit (x86) or 64-bit (x64) build.
cecho {0D}  Dependency Directory      = %DEPS_DIR%{# #}{\n}
echo    - The directory where %PROJECT_NAME% dependencies are fetched and built.
cecho {0D}  Installation Directory    = %INSTALL_DIR%{# #}{\n}
echo    - The directory where %PROJECT_NAME% dependencies are installed.
cecho {0D}  Build Config Type         = %BUILD_CFG%{# #}{\n}
echo    - The used build configuration type for the dependencies.
echo      Defaults to RelWithDebInfo if not specified.
IF %BUILD_CFG%==MinSizeRel cecho {0E}     WARNING: MinSizeRel build can suffer from a significant performance loss.{# #}{\n}
cecho {0D}  Build Type                = %BUILD_TYPE%{# #}{\n}
echo    - The used build type for the dependencies (Build, Rebuild, Clean).
echo      Defaults to Build if not specified. Rebuild/Clean also uninstalls Python.
cecho {0D}  IFCOS_INSTALL_PYTHON      = %IFCOS_INSTALL_PYTHON%{# #}{\n}
echo    - Download and install Python.
echo      Set to something other than TRUE if you wish to use an already installed version of Python.
cecho {0D}  IFCOS_USE_PYTHON2         = %IFCOS_USE_PYTHON2%{# #}{\n}
echo    - Use Python 2 instead of 3.
echo      Set to TRUE if you wish to use Python 2 instead of 3. Has no effect if IFCOS_INSTALL_PYTHON is not TRUE.
cecho {0D}  IFCOS_NUM_BUILD_PROCESSES = %IFCOS_NUM_BUILD_PROCESSES%{# #}{\n}
echo    - How many MSBuild.exe processes may be run in parallel.
echo      Defaults to NUMBER_OF_PROCESSORS.
echo.

:: Print script's usage information
cecho {0A}Requirements for a successful execution:{# #}{\n}
echo    1. Install Git and make sure 'git' is accessible from PATH.
echo     - http://code.google.com/p/tortoisegit/
echo    2. Install CMake and make sure 'cmake' is accessible from PATH.
echo     - http://www.cmake.org/
echo    3. Visual Studio 2008 or newer (2013 or newer recommended).
echo    4. Run this batch script with Visual Studio environment variables set.
echo.
REM TODO 3ds Max SDK?

cecho {0E}Warning: You will need roughly 8 GB of disk space to proceed (VS 2015 x64 RelWithDebInfo).{# #}{\n}
echo.

echo If you are not ready with the above, press Ctrl-C to abort!
pause
echo.

cd %DEPS_DIR%

:: Note all of the depedencies have approriate label so that user can easily skip something if wanted
:: by modifying this file and using goto.
:Boost
set BOOST_VERSION=1.59.0
:: DEPENDENCY_NAME is used for logging and DEPENDENCY_DIR for saving from some redundant typing
set DEPENDENCY_NAME=Boost %BOOST_VERSION%
set DEPENDENCY_DIR="%DEPS_DIR%\boost"
:: Version string with underscores instead of dots.
set BOOST_VER=%BOOST_VERSION:.=_%
set BOOST_ROOT=%DEPS_DIR%\boost
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
IF EXIST "%DEPS_DIR%\boost_%BOOST_VER%". (
    cd "%DEPS_DIR%"
    ren boost_%BOOST_VER% boost
    IF NOT EXIST "%DEPS_DIR%\boost\boost.css" GOTO :Error
    cd "%DEPS_DIR%\boost"
    cecho {0D}Building Boost build script.{# #}{\n}
    call bootstrap vc%VC_VER%
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)

set BOOST_LIBS=--with-system --with-regex --with-thread --with-program_options --with-date_time
:: NOTE Boost is fast to build with limited set of libraries so build it always.
cd "%DEPS_DIR%\boost"
cecho {0D}Building %DEPENDENCY_NAME% %BOOST_LIBS% Please be patient, this will take a while.{# #}{\n}
IF EXIST "%DEPS_DIR%\boost\bin.v2\project-cache.jam" del "%DEPS_DIR%\boost\bin.v2\project-cache.jam"
call .\b2 toolset=msvc-%VC_VER%.0 runtime-link=static address-model=%ARCH_BITS% -j%IFCOS_NUM_BUILD_PROCESSES% ^
    variant=%DEBUG_OR_RELEASE_LOWERCASE% %BOOST_LIBS% stage --stagedir=stage/vs%VS_VER%-%VS_PLATFORM% 
IF NOT %ERRORLEVEL%==0 GOTO :Error

:ICU
set DEPENDENCY_NAME=ICU
set DEPENDENCY_DIR=N/A
set ICU_ZIP=icu-55.1-vs%VS_VER%.7z
cd "%DEPS_DIR%"
call :DownloadFile http://www.npcglib.org/~stathis/downloads/%ICU_ZIP% "%DEPS_DIR%" %ICU_ZIP%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :ExtractArchive %ICU_ZIP% "%DEPS_DIR%" "%INSTALL_DIR%\icu"
IF NOT %ERRORLEVEL%==0 GOTO :Error
:: Rename lib and bin directories to predictable form
IF EXIST "%DEPS_DIR%\icu-55.1-vs%VS_VER%". (
    pushd "%DEPS_DIR%\icu-55.1-vs%VS_VER%"
    IF EXIST bin. ren bin bin%ARCH_BITS%"
    IF EXIST lib. ren lib lib%ARCH_BITS%"
    popd
)

IF EXIST "%DEPS_DIR%\icu-55.1-vs%VS_VER%\". (
    robocopy "%DEPS_DIR%\icu-55.1-vs%VS_VER%\include" "%INSTALL_DIR%\icu\include" /E /IS /njh /njs
    IF NOT EXIST "%INSTALL_DIR%\icu\lib". mkdir "%INSTALL_DIR%\icu\lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicutest%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icutest.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicutu%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icutu.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicuuc%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuuc.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicudt%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icudt.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicuin%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuin.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicuio%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icuio.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\sicule%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\icule.lib"
    copy /y "%DEPS_DIR%\icu-55.1-vs%VS_VER%\lib%ARCH_BITS%\siculx%POSTFIX_D%.lib" "%INSTALL_DIR%\icu\lib\iculx.lib"
)

:OpenCOLLADA
:: Note OpenCOLLADA has only Release and Debug builds.
set DEPENDENCY_NAME=OpenCOLLADA
set DEPENDENCY_DIR=%DEPS_DIR%\OpenCOLLADA
call :GitCloneOrPullRepository https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
cd "%DEPENDENCY_DIR%"
:: NOTE OpenCOLLADA has been observed to have problems with switching between debug and release builds so
:: uncomment to following line in order to delete the CMakeCache.txt always if experiencing problems.
REM IF EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt". del "%DEPENDENCY_DIR%\%BUILD_DIR%\CMakeCache.txt"
call :RunCMake -DCMAKE_INSTALL_PREFIX="%INSTALL_DIR%\OpenCOLLADA" -DUSE_STATIC_MSVC_RUNTIME=1
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM TODO OpenCOLLADA takes a long time to build; build only if needed
REM IF NOT EXIST "%DEPS_DIR%\OpenCOLLADA\%BUILD_DIR%\lib\%DEBUG_OR_RELEASE%\OpenCOLLADASaxFrameworkLoader.lib".
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\OPENCOLLADA.sln" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %DEBUG_OR_RELEASE%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:oce-win-bundle
set DEPENDENCY_NAME=oce-win-bundle
set DEPENDENCY_DIR=%DEPS_DIR%\oce-win-bundle
:: TODO Temporarily use our own repo until the upstream is fixed
REM call :GitCloneOrPullRepository https://github.com/QbProg/oce-win-bundle.git "%DEPENDENCY_DIR%"
call :GitCloneOrPullRepository https://github.com/Tridify/oce-win-bundle.git "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF NOT EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%". (
    cd "%DEPENDENCY_DIR%"
    call git branch msvc-enhancements origin/msvc-enhancements
    IF NOT %ERRORLEVEL%==0 GOTO :Error
    call git checkout msvc-enhancements
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)
cd "%DEPENDENCY_DIR%"
call :RunCMake -DOCE_WIN_BUNDLE_INSTALL_DIR="%INSTALL_DIR%\oce-win-bundle" -DBUNDLE_USE_STATIC_MSVC_RUNTIME=1
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM IF NOT EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%\FreeImage.cmake\%BUILD_CFG%\FreeImage.dll"
call :BuildSolution "%DEPENDENCY_DIR%\%BUILD_DIR%\oce-win-bundle.sln" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call :InstallCMakeProject "%DEPENDENCY_DIR%\%BUILD_DIR%" %BUILD_CFG%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:OCE
set DEPENDENCY_NAME=Open CASCADE Community Edition
set DEPENDENCY_DIR=%DEPS_DIR%\oce
:: TODO Temporarily use our own repo until the upstream has static VC runtime option
REM call :GitCloneOrPullRepository https://github.com/tpaviot/oce.git "%DEPENDENCY_DIR%"
call :GitCloneOrPullRepository https://github.com/Tridify/oce.git "%DEPENDENCY_DIR%"
IF NOT %ERRORLEVEL%==0 GOTO :Error
IF NOT EXIST "%DEPENDENCY_DIR%\%BUILD_DIR%". (
    cd "%DEPENDENCY_DIR%"
    call git branch temp-vs-static-lib-build-fixes origin/temp-vs-static-lib-build-fixes
    IF NOT %ERRORLEVEL%==0 GOTO :Error
    call git checkout temp-vs-static-lib-build-fixes
    IF NOT %ERRORLEVEL%==0 GOTO :Error
)
cd "%DEPENDENCY_DIR%"
set OCE_BUNDLE_ROOT_PATH="%INSTALL_DIR%\oce-win-bundle"
REM -DOCE_USE_BUNDLE_SOURCE=1 REM set OCE_BUNDLE_ROOT_PATH=%DEPS_DIR%\oce-win-bundle
:: NOTE Specify OCE_NO_LIBRARY_VERSION as rc.exe can fail due to long filenames and huge command-line parameter
:: input (more than 32,000 characters). Could maybe try using subst for the build dir to overcome this.
call :RunCMake  -DOCE_BUILD_SHARED_LIB=0 -DOCE_USE_BUNDLE=1 -DOCE_BUNDLE_ROOT_PATH="%OCE_BUNDLE_ROOT_PATH%" ^
                -DOCE_INSTALL_PREFIX="%INSTALL_DIR%\oce" -DOCE_TESTING=0 -DOCE_NO_LIBRARY_VERSION=1 ^
                -DOCE_USE_STATIC_MSVC_RUNTIME=1
IF NOT %ERRORLEVEL%==0 GOTO :Error
REM TODO OCE takes a long time to build; build only if needed
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
set PYTHONPATH=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%

set DEPENDENCY_NAME=Python %PYTHON_VERSION%
set DEPENDENCY_DIR=N/A
set PYTHON_AMD64_POSTFIX=.amd64
:: NOTE/TODO Beginning from 3.5.0: set PYTHON_AMD64_POSTFIX=-amd64
IF NOT %TARGET_ARCH%==x64 set PYTHON_AMD64_POSTFIX=
set PYTHON_INSTALLER=python-%PYTHON_VERSION%%PYTHON_AMD64_POSTFIX%.msi
:: NOTE/TODO 3.5.0 doesn't use MSI any longer, but exe: set PYTHON_INSTALLER=python-%PYTHON_VERSION%%PYTHON_AMD64_POSTFIX%.exe
IF "%IFCOS_INSTALL_PYTHON%"=="TRUE" (
    REM Store Python versions to BuildDepsCache.txt for run-cmake.bat
    echo PY_VER_MAJOR_MINOR=%PY_VER_MAJOR_MINOR%>"%THISDIR%\BuildDepsCache.txt"
    echo PYTHONPATH=%PYTHONPATH%>>"%THISDIR%\BuildDepsCache.txt"

    cd "%DEPS_DIR%"
    call :DownloadFile https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER% "%DEPS_DIR%" %PYTHON_INSTALLER%
    IF NOT %ERRORLEVEL%==0 GOTO :Error
    REM Uninstall if build Rebuild/Clean used
    IF NOT %BUILD_TYPE%==Build (
        cecho {0D}Uninstalling %DEPENDENCY_NAME%. Please be patient, this will take a while.{# #}{\n}
        msiexec /x %PYTHON_INSTALLER% /qn
    )

    IF NOT EXIST "%PYTHONPATH%". (
        cecho {0D}Installing %DEPENDENCY_NAME%. Please be patient, this will take a while.{# #}{\n}
        msiexec /qn /i %PYTHON_INSTALLER% TARGETDIR="%PYTHONPATH%"
    ) ELSE (
        cecho {0D}%DEPENDENCY_NAME% already installed. Skipping.{# #}{\n}
    )
) ELSE (
    cecho {0D}IFCOS_INSTALL_PYTHON not true, skipping installation of Python.{# #}{\n}
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
    pushd %DEPS%
    ren swigwin-%SWIG_VERSION% swigwin
    popd
)
IF EXIST "%DEPS_DIR%\swigwin\". robocopy "%DEPS_DIR%\swigwin" "%INSTALL_DIR%\swigwin" /E /IS /MOVE /njh /njs

:Successful
echo.
%TOOLS%\utils\cecho {0A}%PROJECT_NAME% dependencies built.{# #}{\n}
goto :Finish

:Error
echo.
%TOOLS%\utils\cecho {0C}An error occurred! Aborting!{# #}{\n}
goto :Finish

:Finish
set PATH=%ORIGINAL_PATH%
cd %TOOLS%
endlocal
goto :EOF

::::::::::::::::::::::::::::::::::::: Subroutines :::::::::::::::::::::::::::::::::::::

:: DownloadFile - Downloads a file using wget
:: Params: %1 url, %2 destinationDir, %3 filename
:DownloadFile
pushd %2
IF NOT EXIST "%3". (
    cecho {0D}Downloading %DEPENDENCY_NAME% into %2.{# #}{\n}
    wget --no-check-certificate %1
) ELSE (
    cecho {0D}%DEPENDENCY_NAME% already downloaded. Skipping.{# #}{\n}
)
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: ExtractArchive - Extracts an archive file using 7-zip
:: Params: %1 filename, %2 destinationDir, %3 dirAfterExtraction
:ExtractArchive
IF NOT EXIST "%3". (
    cecho {0D}Extracting %DEPENDENCY_NAME% into %2.{# #}{\n}
    7za x %1 -y -o%2
) ELSE (
    cecho {0D}%DEPENDENCY_NAME% already extracted into %3. Skipping.{# #}{\n}
)
exit /b %ERRORLEVEL%

:: GitCloneOrPullRepository - Clones or pulls (if repository already cloned) a Git repository
:: Params: %1 gitUrl, %2 destDir
:: F.ex. call :GitCloneRepository https://github.com/KhronosGroup/OpenCOLLADA.git "%DEPS_DIR%\OpenCOLLADA\"
:GitCloneOrPullRepository
IF NOT EXIST %2. (
    cecho {0D}Cloning %DEPENDENCY_NAME% into %2.{# #}{\n}
    pushd "%DEPS_DIR%"
    call git clone %1 %2
) ELSE (
    cecho {0D}%DEPENDENCY_NAME% already cloned. Pulling latest changes.{# #}{\n}
    pushd %2
    call git pull
)
set RET=%ERRORLEVEL%
popd
exit /b %RET%

:: RunCMake - Runs CMake for a CMake-based project
:: Params: %* cmakeOptions
:: NOTE cd to root CMakeLists.txt folder before calling this if the CMakeLists.txt is not in the repo root.
:RunCMake
cecho {0D}Running CMake for %DEPENDENCY_NAME%.{# #}{\n}
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

:: BuildSolution - Builds/Rebuilds/Cleans a solution using MSBuild
:: Params: %1 solutioName, %2 configuration
:BuildSolution
cecho {0D}%BUILD_TYPE%ing %2 %DEPENDENCY_NAME%. Please be patient, this will take a while.{# #}{\n}
%MSBUILD_CMD% %1 /p:configuration=%2;platform=%VS_PLATFORM%
exit /b %ERRORLEVEL%

:: InstallCMakeProject - Builds the INSTALL project of CMake-based project
:: Params: %1 buildDir, %2 == configuration
:: NOTE the actual install dir is set during cmake run.
:InstallCMakeProject
pushd %1
cecho {0D}Installing %2 %DEPENDENCY_NAME%. Please be patient, this will take a while.{# #}{\n}
%INSTALL_CMD% INSTALL.%VCPROJ_FILE_EXT% /p:configuration=%2;platform=%VS_PLATFORM%
set RET=%ERRORLEVEL%
popd
exit /b %RET%
