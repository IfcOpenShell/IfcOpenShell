== Windows Build Tools and Scripts ==

This folder contains build tools and script for automatic building and deployment of IfcOpenShell's
(IFCOS) dependencies.

As a general guideline, .cmd files are non-standalone batch files that need to be run from command
prompt or from other batch file and/or Visual Studio environment variables set and .bat files are
standalone batch files that can be run from File Explorer too.


== Usage Instructions ==

Execute build-deps.cmd to fetch, build and install the dependencies. The batch file will print
requirements for a successful execution. The script allows a few user-configurable build options
which are listed in the usage instructions. Either edit the script file or set these values before
running the script.

build-deps.cmd expects a CMake generator as %1 and a build configuration type as %2. If the parameters
are not provided, the default values are used ("Visual Studio 14 2015 Win64" and RelWithDebInfo respectively).
A build type (Build/Rebuild/Clean) can be provided as %3, if wanted (defaults to Build). See vs-cfg.cmd
if you want to change the defaults. The batch file will create deps\ and deps-vs<VERSION>-<ARCHITECTURE>-installed\
directories to the project root. Note that currently only libraries for one build configuration type
can be installed at a time, so if wanting to switch between release and debug builds, run the build-deps.cmd
again with the appropriate build type as %2.

After the dependencies are build, execute run-cmake.bat. The batch file expects a CMake generator as
%1, or alternatively if more parameters are provided, %* is passed for the CMake inkovation. If no %1
is provided, the same default value as above is used. This batch script will create a folder of form 
build-vs<VERSION>-<ARCHITECTURE> which will contain the solution and project files for Visual Studio.
IMPORTANT: If you wish to use any library from a custom location, modify the paths in run-cmake.bat 
accordingly.

All of the dependencies are build as static libraries against the static run-time allowing the developer
to effortlessly deploy standalone binaries.

You can now build the project using the IfcOpenShell.sln file in the build folder. Build the INSTALL project
if wanted. The project will installed to installed-vs<VERSION>-<ARCHITECTURE> folder in the project's root
folder and the required IfcOpenShell-Python parts are deployed to the <PYTHONPATH>\Lib\site-packages folder.


== Directory Structure ==

|   build-deps.cmd          - Fetches and builds all needed dependencies for IFCOS
|   readme.txt              - This file
|   run-cmake.bat           - Sets environment variables for the dependencies and runs CMake for IFCOS
|   vs-cfg.cmd              - Utility file used by the build scripts
|   BuildDepsCache.txt      - Cache file created by build-deps.cmd
|
+---sln                     - Contains the old Visual Studio solution and project files
\---utils                   - Contains various utilities for the build scripts
