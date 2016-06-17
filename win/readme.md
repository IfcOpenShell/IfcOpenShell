Windows Build Tools and Scripts
===============================
This folder contains build tools and script for automatic building and deployment of IfcOpenShell (IFCOS)
and its dependencies.

As a general guideline, `.cmd` files are non-standalone batch files that need to be run from command prompt or from
another batch file, and/or while the Visual Studio environment variables set, and `.bat` files are standalone batch
files that can also be invoked e.g. by double-clicking in the File Explorer.

Usage Instructions
------------------
Execute `build-deps.cmd` to fetch, build and install the dependencies. The batch file will print the requirements for
a successful execution. The script allows a few user-configurable build options which are listed in the usage
instructions. Either edit the script file or set these values before running the script.

`build-deps.cmd` expects a CMake generator as `%1` and a build configuration type (`RelWithDebInfo`, `Release`,
`MinSizeRel`, or `Debug`, defaults to `RelWithDebInfo`) as `%2`. If the generator is not provided, the generator is
deduced from the Visual Studio environment variables. User-friendly VS generator shorthands are supported, e.g.
`vs2013-x86` or `vs2015-x64`, and these are converted to the appropriate CMake ones by the scripts. A build type
(`Build`, `Rebuild`, or `Clean`, defaults to `Build`) can be provided as `%3`. See `vs-cfg.cmd` if you wish to change
the defaults. The batch file will create `deps\` and `deps-vs<VERSION>-<ARCHITECTURE>-installed\` directories to the
project root. Debug and release builds of the depedencies can co-exist by simply running
```
> build-deps.cmd <GENERATOR> Debug
> build-deps.cmd <GENERATOR> <Release|RelWithDebInfo|MinSizeRel>
```

After the dependencies are build, execute `run-cmake.bat`. The batch file expects a CMake generator as `%1` and the
rest of possible parameters are passed as is. If a generator is not provided, the generator is read from the
BuildDepsCache file, or tried to be deduced from the location of `cl.exe`. If passing build options for the script,
the generator must be always passed as the first option:
```
> run-cmake.bat vs2015-x64 -DUSE_IFC4=1 -DBUILD_IFCPYTHON=0
```

**If you wish to use any library from a custom location, modify the paths in `run-cmake.bat` accordingly**. The batch
script will create a folder of form `build-vs<VERSION>-<ARCHITECTURE>\` which will contain the solution and project
files for Visual Studio.

Note that building IfcOpenShell as 64-bit is recommended as many of real life IFC files has been observed to take
easily more than 2 GBs of RAM while converting.

After this, one can build the project using the `IfcOpenShell.sln` file in the build folder. Build the `INSTALL` project
if wanted. Convenience batch files `build-ifcopenshell.bat` and `install-ifcopenshell.bat` can also be used. The batch
files expect `%1` and `%2` in same fashion as above and possible extra parameters are passed for the `MSBuild` call.
`run-cmake.bat`, `build-ifcopenshell.bat`, and `install-ifcopenshell.bat` can also be directly invoked from Filer Explorer
or regular Command Prompt if BuildDepsCache file exists (the last modified version is used). Running the scripts without extra
parameters reads the build options from an existing CMakeCache.txt.

The project will be installed to `installed-vs<VERSION>-<ARCHITECTURE>\` folder in the project's root folder and the
required IfcOpenShell-Python parts are deployed to the `<PYTHONHOME>\Lib\site-packages\` folder. The 3ds Max plug-in,
`IfcMax.dli`, needs to be copied manually to the 3ds Max's `plugins` folder.

**Note:** Currently all of the dependencies are build as static libraries against the static run-time allowing the
developer to effortlessly deploy standalone IFCOS executables.

Using an already existing Python installation
---------------------------------------------

Let's say you have already installed 64-bit Python 3.5.1 to `C:\Python3`.
Before building the dependencies, disable the script from installing Python:
```
> set IFCOS_INSTALL_PYTHON=FALSE
> buid-deps.cmd
```

After building the dependencies, append Python version and installation directory information to the BuildDepsCache file
in `IfcOpenShell\win`:
```
> echo PY_VER_MAJOR_MINOR=35>> BuildDepsCache-x64.txt
> echo PYTHONHOME=C:\Python3>> BuildDepsCache-x64.txt
```

After this you should be able to run `run-cmake.bat` normally. If using 32-bit Python, the name of the file must be
`BuildDepsCache-x86.txt`.

Directory Structure
------------------
```
..
+---build-vs<VER>-<ARCH>            - Created by run-cmake.bat, for a certain VS version and target architecture
+---deps                            - Created by build-deps.cmd, common for all VS versions and target architectures
+---deps-installed-vs<VER>-<ARCH>   - Created by build-deps.cmd,  for a certain VS version and target architecture
+---installed-vs<VER>-<ARCH>        - Created by building the IFCOS's INSTALL project
\---win
|   build-all.cmd                   - Runs all of the build scripts for IFCOS and it dependencies in a row without pauses
|   build-deps.cmd                  - Fetches and builds all needed dependencies for IFCOS
|   BuildDepsCache-<ARCH>.txt       - Cache file created by build-deps.cmd
|   build-ifcopenshell.bat          - Builds IFCOS
|   build-type-cfg.cmd              - Utility file used by the build scripts
|   install-ifcopenshell.bat        - Builds IFCOS's INSTALL project
|   readme.md                       - This file
|   run-cmake.bat                   - Sets environment variables for the dependencies and runs CMake for IFCOS
|   set-python-to-path.bat          - Utility for setting PYTHONHOME (read from BuildDepsCache-<ARCH>.txt) to PATH
|   vs-cfg.cmd                      - Utility file used by the build scripts
\---utils                           - Contains various utilities for the build scripts
```
