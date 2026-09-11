Windows Build Tools and Scripts
===============================
This folder contains build tools and script for automatic building and deployment of IfcOpenShell ("IFCOS")
and its dependencies.

As a general guideline, `.cmd` files are non-standalone batch files that need to be run from command prompt or from
another batch file, and/or while the Visual Studio ("MSVC") environment variables set, and `.bat` files are standalone batch
files that can also be invoked e.g. by double-clicking in the File Explorer.

Usage Instructions
------------------
Launch the proper Visual Studio command prompt, cd to the 'win' directory inside the IfcOpenShell directory and execute `python build-deps.py` to fetch, build and install the dependencies. The script will print the requirements for a successful execution. It allows a few user-configurable build options which are listed below (run `python build-deps.py --help` for the full list).

`build-deps.py` expects a CMake generator as the 1st positional argument and a build configuration type (`RelWithDebInfo`, `Release`, `MinSizeRel`, or `Debug`, defaults to `RelWithDebInfo`) as the 2nd. If the generator is not provided, it is deduced from the MSVC environment variables.

User-friendly CMake Visual Studio generator shorthands are supported. They are converted to the appropriate CMake generators and options. Shorthands are indeed the preferable way to specify the generator, since they allow a more accurate platform and toolset configuration. Here are some examples:
```
"vs2019-x86-v141"    => cmake -G "Visual Studio 16 2019" -A Win32 -T v141
"vs2022-x64"         => cmake -G "Visual Studio 17 2022" -A x64
"vs2022-ARM64"       => cmake -G "Visual Studio 17 2022" -A ARM64
```
Of course not all Visual C++ compilers support any platform or toolset, refer to the Visual Studio and CMake documentation for this. If you do not specify a toolset, the compiler will use the default toolset for the version, i.e. vs2019 will use the v142 toolset.

A build type (`Build`, `Rebuild`, or `Clean`, defaults to `Build`) can be provided as the 3rd positional argument.

The script will create `_deps\` and `_deps-vs<VERSION>-<PLATFORM>[-<TOOLSET>]-installed\` directories in the project root. Debug and release builds of the dependencies can co-exist by simply running:
```
> python build-deps.py <GENERATOR> Debug
> python build-deps.py <GENERATOR> <Release|RelWithDebInfo|MinSizeRel>
```

After the dependencies are built, execute `python run-cmake.py`. The script expects a CMake generator as the 1st positional argument, that is interpreted just like the `build-deps.py` script. If a generator is not provided, the generator is read from the BuildDepsCache file. CMake options are passed after `--`:
```
> python run-cmake.py vs2022-x64 -- -DGLTF_SUPPORT=ON
```

**If you wish to use any library from a custom location, modify the paths in `run-cmake.py` accordingly**. The script will create a folder of form `_build-vs<VERSION>-<PLATFORM>[-<TOOLSET>]\` which will contain the solution and project files for MSVC.

Note that building IfcOpenShell as 64-bit is recommended as many of real life IFC files has been observed to take easily more than 2 GBs of RAM while converting.

After this, one can build the project using the `IfcOpenShell.sln` file in the build folder. Build the `INSTALL` project
if wanted. Convenience scripts `python build-ifcopenshell.py` and `python install-ifcopenshell.py` can also be used. The
scripts expect the generator and build configuration type in the same fashion as `build-deps.py` and possible extra
parameters are passed for the `MSBuild` call after `--`. `python run-cmake.py` can also be run without a generator
argument if a BuildDepsCache file exists (the last modified version is used). Running the scripts without extra
parameters reads the build options from an existing CMakeCache.txt.

The project will be installed to `_installed-vs<VERSION>-<ARCHITECTURE>\` folder in the project's root folder and the
required IfcOpenShell-Python parts are deployed to the `<PYTHONHOME>\Lib\site-packages\` folder. The 3ds Max plug-in,
`IfcMax.dli`, needs to be copied manually to the 3ds Max's `plugins` folder.

Using an already existing Python installation
---------------------------------------------

Let's say you have already installed 64-bit Python 3.13 to `C:\Python3`.
Before building the dependencies, disable the script from installing Python:
```
> set IFCOS_INSTALL_PYTHON=FALSE
> python build-deps.py
```

After building the dependencies, append Python installation directory information to the BuildDepsCache file
in `IfcOpenShell\win`:
```
> echo PYTHONHOME=C:\Python3>> BuildDepsCache-x64.txt
```

After this you should be able to run `python run-cmake.py` normally. If using 32-bit Python, the name of the file must be
`BuildDepsCache-x86.txt`.

Directory Structure
------------------
```
..
+---_build-*                        - Created by run-cmake.py, specific for a certain compiler and and target architecture
+---_deps                           - Created by build-deps.py, common for all compilers
+---_deps-*-installed               - Created by build-deps.py, specific for a certain compiler and target architecture
+---_installed-*                    - Created by installing the IFCOS project, specific for a certain compiler and target architecture
\---win
|   build-all.cmd                   - Runs all of the build scripts for IFCOS and it dependencies in a row without pauses
|   build-deps.py                   - Fetches and builds all needed dependencies for IFCOS using MSVC
|   BuildDepsCache-<ARCH>.txt       - Cache file created by build-deps.py
|   build-ifcopenshell.py           - Builds IFCOS using MSVC
|   build-type-cfg.cmd              - Utility file used by the build scripts
|   install-ifcopenshell.py         - Installs/deploys IFCOS using MSVC.
|   readme.md                       - This file
|   run-cmake.py                    - Sets environment variables for the dependencies and runs CMake for IFCOS using MSVC
|   vs-cfg.cmd                      - Utility file used by the build scripts
\---patches                         - Contains patches for the dependencies
\---utils                           - Contains various utilities for the build scripts
```
