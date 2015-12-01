Windows Build Tools and Scripts
===============================
This folder contains build tools and script for automatic building and deployment of IfcOpenShell (IFCOS)
and its dependencies.

As a general guideline, `.cmd` files are non-standalone batch files that need to be run from command
prompt or from another batch file, and/or while the Visual Studio environment variables set, and `.bat` files are
standalone batch files that can be run also e.g. from the File Explorer.

Usage Instructions
------------------
Execute `build-deps.cmd` to fetch, build and install the dependencies. The batch file will print
the requirements for a successful execution. The script allows a few user-configurable build options
which are listed in the usage instructions. Either edit the script file or set these values before
running the script.

`build-deps.cmd` expects a CMake generator as `%1` and a build configuration type (`RelWithDebInfo/Release/MinSizeRel/Debug`,
defaults to `RelWithDebInfo`) as `%2`. If the generator is not provided, the generator is deduced from the Visual Studio
environment variables. A build type (`Build/Rebuild/Clean`, defaults to `Build`) can be provided as `%3`. See `vs-cfg.cmd`
if you wish to change the defaults. The batch file will create `deps\` and `deps-vs<VERSION>-<ARCHITECTURE>-installed\`
directories to the project root. Debug and release builds of the depedencies can co-exist by simply running
`build-deps.cmd <GENERATOR> Debug` and `build-deps.cmd <GENERATOR> <Release|RelWithDebInfo|MinSizeRel>`.

After the dependencies are build, execute `run-cmake.bat`. The batch file expects always a CMake generator as `%1`
(if not provided, the same default value as above is used), and the rest of possible parameters are passed as is.
**If you wish to use any library from a custom location, modify the paths in `run-cmake.bat` accordingly**. The batch
script will create a folder of form `build-vs<VERSION>-<ARCHITECTURE>\` which will contain the solution and project
files for Visual Studio.

Note that building IfcOpenShell as 64-bit is recommended as many of real life IFC files has been observed to take
easily more than 2 GBs of RAM while converting.

After this, one can build the project using the `IfcOpenShell.sln` file in the build folder. Build the `INSTALL` project
if wanted. The project will be installed to `installed-vs<VERSION>-<ARCHITECTURE>\` folder in the project's root
folder and the required IfcOpenShell-Python parts are deployed to the `<PYTHONPATH>\Lib\site-packages\` folder.

**Note:** All of the dependencies are build as static libraries against the static run-time allowing the developer
to effortlessly deploy standalone IFCOS binaries.


Directory Structure
------------------
```
..
+---build-vs<VER>-<ARCH>            - Created by run-cmake.bat, for a certain VS version and target architecture
+---deps                            - Created by build-deps.cmd, common for all VS versions and target architectures
+---deps-installed-vs<VER>-<ARCH>   - Created by build-deps.cmd,  for a certain VS version and target architecture
+---installed-vs<VER>-<ARCH>        - Created by building the IFCOS's INSTALL project
\---win
|   build-deps.cmd                  - Fetches and builds all needed dependencies for IFCOS
|   BuildDepsCache-<ARCH>.txt       - Cache file created by build-deps.cmd
|   readme.md                       - This file
|   run-cmake.bat                   - Sets environment variables for the dependencies and runs CMake for IFCOS
|   vs-cfg.cmd                      - Utility file used by the build scripts
+---sln                             - Contains the old Visual Studio solution and project files
\---utils                           - Contains various utilities for the build scripts
```
