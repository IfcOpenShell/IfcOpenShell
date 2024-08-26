Installation
============

If you'd like to work with the C++ core of IfcOpenShell, these guides will show
you how to compile and install IfcOpenShell.

.. note::

    It is not necessary to compile IfcOpenShell if you only want to use
    IfcOpenShell-Python, IfcConvert, or the other utilities such as IfcClash or
    IfcDiff. Compilation is only necessary for C++ developers.

    By default, it will compile all available IFC schemas. To reduce compilation time you can specify
    only the schemas you need in `CMakeLists.txt` with `set(SCHEMA_VERSIONS "2x3" "4")`.

You will need:

- `Git <https://git-scm.com/>`__
- `CMake <https://cmake.org/>`__ (3.21 or newer)

IfcOpenShell depends on:

- `Boost <http://www.boost.org/>`__
- `OpenCascade <https://dev.opencascade.org/>`__ - for building IfcGeom For
  converting IFC representation items into BRep solids and tessellated meshes.
  Officially v7.5.0 is supported. Other versions may have unexpected behaviour.
- (Optional) `OpenCOLLADA <https://github.com/khronosGroup/OpenCOLLADA/>`__ -
  for IfcConvert to be able to write tessellated Collada (.dae) files
- (Optional) `SWIG <http://www.swig.org/>`__ and `Python
  <https://www.python.org/>`__ - for building the IfcOpenShell Python interface
  and use in Bonsai
- (Optional) `HDF5 <https://www.hdfgroup.org/solutions/hdf5>`__ - for caching
  geometry using the HDF5 format

Compiling on Linux
------------------

The following instructions are for Ubuntu, modify as required for other
operating systems. GCC (4.7 or newer) or Clang (any version) is required.

.. seealso::

    The `nix/build-all.py <https://github.com/IfcOpenShell/IfcOpenShell/tree/master/nix/build-all.py>`__
    script can be experimented with and studied for pointers for other operating
    systems. Note that this script is not currently meant to be used for a
    typical IfcOpenShell workspace setup.

1. Fetch the latest source code, including all submodules.

   .. code-block:: bash

        git clone --recursive https://github.com/IfcOpenShell/IfcOpenshell.git

   .. warning::

        The path where the source code is cloned to can contain spaces but non-ASCII
        characters are very likely to cause problems with the build.

2. Install basic dependencies:

   .. code-block:: bash

       sudo apt-get install git cmake gcc g++ libboost-all-dev libcgal-dev

   The CGAL version that ships with Ubuntu 20.04 is too old. Users on Ubuntu 20.04 are advised to manually install CGAL 5.3.

3. Install OpenCascade Technology (OCCT).

   .. code-block:: bash

        sudo apt-get install libocct-data-exchange-dev libocct-draw-dev libocct-foundation-dev libocct-modeling-algorithms-dev libocct-modeling-data-dev libocct-ocaf-dev libocct-visualization-dev

   .. seealso::

        If OCCT is not available, an alternative is to `manually compile OCCT
        <https://dev.opencascade.org/release>`__.

   IfcOpenShell 0.8 depends on fairly recent OCCT additions such as the BVH Tree functionality. Users on Ubuntu 20.04 are advised to manually compile and install OCCT 7.7.

   Another alternative is to use OpenCascade Community Edition (OCE), but it may
   lag behind OCCT and is no longer actively maintained so is not recommended.

   .. code-block:: bash

        sudo apt-get install liboce-foundation-dev liboce-modeling-dev liboce-ocaf-dev liboce-visualization-dev liboce-ocaf-lite-dev

   As a final alternative, you may also manually compile OCE:

   .. code-block:: bash

        sudo apt-get install libftgl-dev libtbb2 libtbb-dev libgl1-mesa-dev libfreetype6-dev
        git clone https://github.com/tpaviot/oce.git
        cd oce
        mkdir build && cd build
        cmake ..
        # Replace X with number of CPU cores + 1
        make -j X
        sudo make install

   .. warning::

    Choose one option only between installing OCCT, installing OCE, or
    self-compilation. If you install and compile multiple versions of
    OpenCascade, your system may get confused.


4. For building IfcConvert with COLLADA (.dae) support (ON by default), OpenCOLLADA is needed:

   .. code-block:: bash

        sudo apt-get install libpcre3-dev libxml2-dev
        git clone https://github.com/KhronosGroup/OpenCOLLADA.git
        cd OpenCOLLADA
        # Using a known good revision, but HEAD should work too:
        git checkout 064a60b65c2c31b94f013820856bc84fb1937cc6
        mkdir build && cd build
        cmake ..
        # Replace X with number of CPU cores + 1
        make -j X
        sudo make install

5. For building the IfcPython wrapper (ON by default), SWIG and Python development are needed:

   .. code-block:: bash

        sudo apt-get install python-all-dev swig

6. For building support for HDF5 caching (ON by default), install dependencies:

   .. code-block:: bash

        sudo apt-get install libhdf5-dev libaec-dev zlibc

7. Compile IfcOpenShell itself.

   .. code-block:: bash

        cd /path/to/IfcOpenShell
        mkdir build && cd build
        # Customise the compile options to suit your environment
        # Check all paths are valid for your environment
        cmake ../cmake \
              -DOCC_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu/ \
              -DOCC_INCLUDE_DIR=/usr/include/opencascade \
              \
              # Optional Collada support
              -DCOLLADA_SUPPORT=On \
              -DOPENCOLLADA_INCLUDE_DIR="/usr/local/include/opencollada" \
              -DOPENCOLLADA_LIBRARY_DIR="/usr/local/lib/opencollada"  \
              -DPCRE_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu/ \
              \
              # Optional HDF5 support
              -DHDF5_SUPPORT=On \
              -DHDF5_LIBRARIES="/usr/local/hdf5/lib/libhdf5_cpp.so;/usr/local/hdf5/lib/libhdf5.so;/usr/lib64/libz.so;/usr/lib64/libsz.so;/usr/lib64/libaec.so" \
              -DHDF5_INCLUDE_DIR="/usr/local/hdf5/include" \
              \
              -DCGAL_INCLUDE_DIR=/usr/include \
              -DGMP_INCLUDE_DIR=/usr/include \
              -DMPFR_INCLUDE_DIR=/usr/include \
              -DGMP_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu \
              -DMPFR_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu \
              -DJSON_INCLUDE_DIR=/usr/include \
              -DEIGEN_DIR=/usr/include/eigen3
        # Replace X with number of CPU cores + 1. Reduce when running out of memory. Compiling the code generated from the schemas is resource intensive.
        make -j X
        # Optionally install to the system
        sudo make install


Compiling on MacOS
------------------

GCC (4.7 or newer) or Clang (any version) is required.

1. Fetch the latest source code, including all submodules.

   .. code-block:: bash

        git clone --recursive https://github.com/IfcOpenShell/IfcOpenshell.git

   .. warning::

        The path where the source code is cloned to can contain spaces but non-ASCII
        characters are very likely to cause problems with the build.

2. Install all dependencies using `Homebrew <https://brew.sh/>`__

   .. code-block:: bash

        brew install boost cmake python3 cgal ftgl gmp libaec opencascade swig hdf5 zlib
        # homebrew automatically links most libraries, except some keg-only ones
        brew link zlib --force

3. Build IfcOpenShell with flags for Homebrew dependencies: (``/usr/local/``) for Intel machines with x84_64 architecture,
(``/opt/homebrew/``) for Apple Silicon processors with arm64 architecture.

   .. code-block:: bash

        cd /path/to/IfcOpenShell
        mkdir build && cd build
        # set library flags
        export LDFLAGS="$LDFLAGS -Wl,-flat_namespace,-undefined,suppress"
        cmake ../cmake \
            -DPYTHON_EXECUTABLE=/opt/homebrew/bin/python3.10 \
            -DPYTHON_LIBRARY=/opt/homebrew/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/lib/libpython3.10.dylib \
            -DPYTHON_INCLUDE_DIR=/opt/homebrew/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/include/python3.10/ \
            -DOCC_LIBRARY_DIR=/opt/homebrew/lib/ \
            -DOCC_INCLUDE_DIR=/opt/homebrew/include/opencascade/ \
            -DCGAL_INCLUDE_DIR=/opt/homebrew/include/ \
            -DGMP_LIBRARY_DIR=/opt/homebrew/lib/ \
            -DMPFR_LIBRARY_DIR=/opt/homebrew/lib/ \
            -DHDF5_LIBRARY_DIR=/opt/homebrew/lib/ \
            -DHDF5_INCLUDE_DIR=/opt/homebrew/include/ \
            -DCOLLADA_SUPPORT=0
        # `sysctl -n hw.ncpu` returns the number of cpu cores on macOS
        make -j$(sysctl -n hw.ncpu)

Compiling on Windows (Visual Studio)
------------------------------------

This is for users of  `Visual Studio <https://www.visualstudio.com/>`__ 2008 to
2022 with C++ toolset, recommend to install the C++ toolset with VisualStudio Installer (or `Visual
C++ Build Tools <http://landinghub.visualstudio.com/visual-cpp-build-tools>`__).

1. Fetch the latest source code, including all submodules.

   .. code-block:: bat

        git clone --recursive https://github.com/IfcOpenShell/IfcOpenshell.git

   .. warning::

        The path where the source code is cloned to can contain spaces but non-ASCII
        characters are very likely to cause problems with the build.

2. Assuming Visual Studio 2015 x64 environment variables set, build dependencies
   and run cmake.

   .. code-block:: bat

        cd IfcOpenShell\win
        build-deps.cmd
        run-cmake.bat

3. Open and build the solution file in Visual Studio:

   .. code-block:: bat

        ..\build-vs2015-x64\IfcOpenShell.sln

   As the scripts default to using the ``RelWithDebInfo`` configuration, and a
   freshly created solution by CMake defaults to ``Debug``, make sure to switch the
   used build configuration. Build the ``INSTALL`` project (right-click -> Project
   Only) to deploy the headers and binaries into a single location if
   wanted/needed.

   Alternatively, one can use the utility batch file(s) to build and install the
   project easily from the command-line (installing a project will build it
   also, if required):

   .. code-block:: bat

        install-ifcopenshell.bat

.. seealso::

    For more information on configuring a Windows compilation see the `Windows
    Readme
    <https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.8.0/win/readme.md>`__.

Compiling on Windows (MSYS2 + MinGW)
------------------------------------

This is for users of `MSYS2 <https://msys2.github.io/>`__ and `MinGW
<https://www.mingw-w64.org/>`__.

1. Fetch the latest source code, including all submodules.

   .. code-block:: bat

        git clone --recursive https://github.com/IfcOpenShell/IfcOpenshell.git

   .. warning::

        The path where the source code is cloned to can contain spaces but non-ASCII
        characters are very likely to cause problems with the build.

2. Start the MSYS2 Shell and then:

   .. code-block:: bat

        cd IfcOpenShell/win
        ./build-deps.sh
        ./run-cmake.sh
        ./install-ifcopenshell.sh

.. seealso::

    For more information on configuring a Windows compilation see the `Windows
    Readme
    <https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.8.0/win/readme.md>`__.

Packaged installation
---------------------

- **Arch Linux**: `Direct from Git <https://aur.archlinux.org/packages/ifcopenshell-git/>`__.
