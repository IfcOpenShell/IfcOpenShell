IfcOpenShell 
============
IfcOpenShell is an open source ([LGPL]) software library for working with the Industry Foundation Classes ([IFC]) 
file format. Extensive geometric support is implemented for the IFC releases [IFC2x3 TC1] and [IFC4 Add2 TC1].
Support for parsing is provided for IFC4x1, IFC4x2, and the IFC4x3 release candidates. Extending with support for
arbitrary IFC schemas is possible at compile-time when using C++ and at run-time when using Python.

For more information, see
* [http://ifcopenshell.org](http://ifcopenshell.org)  
* [http://academy.ifcopenshell.org](http://academy.ifcopenshell.org)

| Service                                         | Status                                                                                                                                       |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Anaconda Daily Build                            | [![Anaconda-Server Badge](https://img.shields.io/conda/vn/ifcopenshell/ifcopenshell)](https://anaconda.org/ifcopenshell/ifcopenshell)        |
| Anaconda v0.7.0 Stable                          | [![Anaconda-Server Badge](https://img.shields.io/conda/vn/conda-forge/ifcopenshell)](https://anaconda.org/conda-forge/ifcopenshell)          |
| PyPi Daily Build                                | [![PyPi Badge](https://img.shields.io/pypi/v/ifcopenshell)](https://pypi.org/project/ifcopenshell/)                                          |
| ArchLinux AUR Package                           | [![AUR Badge](https://img.shields.io/aur/version/ifcopenshell-git)](https://aur.archlinux.org/packages/ifcopenshell-git)                     |
| BlenderBIM Add-on Chocolatey (under moderation) | [![Chocolatey Badge](https://img.shields.io/chocolatey/v/blenderbim-nightly)](https://community.chocolatey.org/packages/blenderbim-nightly/) |
| Sponsor development on OpenCollective           | [![Financial Contributors](https://opencollective.com/opensourcebim/tiers/badge.svg)](https://opencollective.com/opensourcebim/)             |
| Docker hub                                      | [![Docker Pulls](https://img.shields.io/docker/pulls/aecgeeks/ifcopenshell)](https://hub.docker.com/r/aecgeeks/ifcopenshell)                 |

Prerequisites
-------------
* Git
* CMake (3.1.3 or newer)
* Windows: [Visual Studio] 2008 to 2019 (2022 not yet supported by dependency CMake) with C++ toolset (or [Visual C++ Build Tools]) or [MSYS2] + MinGW
* *nix: GCC 4.7 or newer, or Clang (any version)

Dependencies
-------------
* [Boost](http://www.boost.org/)
* [Open Cascade](https://dev.opencascade.org/) - *optional*, but required for building IfcGeom
  ([official](https://dev.opencascade.org/release), "OCCT", or [community edition](https://github.com/tpaviot/oce), "OCE")  
  For converting IFC representation items into BRep solids and tessellated meshes
* [OpenCOLLADA](https://github.com/khronosGroup/OpenCOLLADA/) - *optional*  
  For IfcConvert to be able to write tessellated Collada (.dae) files
* [SWIG](http://www.swig.org/) and [Python](https://www.python.org/) - *optional*  
  For building the IfcOpenShell Python interface and the Blender add-on
* [3ds Max SDK](http://www.autodesk.com/products/3ds-max/free-trial) - *optional*  
  For building the 3ds Max plug-in.
  All recent versions of 3ds Max (2014 and newer) are 64-bit only, so a 64-bit installation is assumed.

Building IfcOpenShell
---------------------

Note 1: The path where the source code is cloned to can contain spaces but non-ASCII characters are very likely to cause problems with the build.

Note 2: If you had not used `git clone --recursive https://github.com/IfcOpenShell/IfcOpenshell.git`, update the submodules by running `git submodule init & git submodule update`.

Note 3: Be careful with special characters is the path when using the nix or win build scripts, because the OpenCASCADE build will fail on paths containing ++ and likely other situations.

### Compiling on Windows
The preferred way to fetch and build this project's dependencies is to use the build scripts
in win/ folder. **See [win/readme.md] for more information**.

#### Using Visual Studio
Instructions in a nutshell (**assuming Visual Studio 2015 x64 environment variables set**):

    > cd IfcOpenShell\win
    > build-deps.cmd
    > run-cmake.bat

NB: `build-deps.cmd` need to be ran from the directory containing it, i.e. the `./win` folder.

You can now open and build the solution file in Visual Studio:

    > ..\build-vs2015-x64\IfcOpenShell.sln

As the scripts default to using the `RelWithDebInfo` configuration, and a freshly created solution by CMake defaults
to `Debug`, make sure to switch the used build configuration. Build the `INSTALL` project (right-click -> Project
Only) to deploy the headers and binaries into a single location if wanted/needed.

Alternatively, one can use the utility batch file(s) to build and install the project easily from the command-line
(installing a project will build it also, if required):

    > install-ifcopenshell.bat

#### Using MSYS2 + MinGW

Start the MSYS2 Shell and then:

    $ cd IfcOpenShell/win
    $ ./build-deps.sh
    $ ./run-cmake.sh
    $ ./install-ifcopenshell.sh

#### Using Bash on Ubuntu on Windows

Start Bash on Ubuntu on Windows and follow the instructions below. Compiling on Ubuntu 14.04.4 LTS using GCC 4.8.4
or Clang 3.5 has been confirmed to work.

### Compiling on *nix

The following instructions are for Ubuntu, modify as required for other operating systems. [nix/build-all.py] script
can be experimented with and studied for pointers for other operating systems, but note that this script is not currently
meant to be used for a typical IfcOpenShell workspace setup.

Note 1: It is recommended to use OCCT for IfcOpenShell. You could use OCE as well, but sometimes it may lag behind OCCT and 
therefore not compile with the latest IfcOpenShell.

Note 2: where `make -j` is written, add a number roughly equal to the amount of CPU cores + 1.

**1)** Install most of the prerequisites and dependencies:

    $ sudo apt-get install git cmake gcc g++ libboost-all-dev libcgal-dev

**2a)** Either use an OCCT package from your operating system's software repository

    $ sudo apt-get install libocct-data-exchange-dev libocct-draw-dev libocct-foundation-dev libocct-modeling-algorithms-dev libocct-modeling-data-dev libocct-ocaf-dev libocct-visualization-dev

**2b)** or, if OCCT is not available or the latest code is wanted, obtain and compile OCCT from https://dev.opencascade.org/release

**2c)** or, if you'd like to try using OCE, use the package from your operating system's software repository

    $ sudo apt-get install liboce-foundation-dev liboce-modeling-dev liboce-ocaf-dev liboce-visualization-dev liboce-ocaf-lite-dev

**2d)** or if OCE is not available, or the latest code is wanted, compile OCE yourself (note that the build takes a long time)

    $ sudo apt-get install libftgl-dev libtbb2 libtbb-dev libgl1-mesa-dev libfreetype6-dev
    $ git clone https://github.com/tpaviot/oce.git
    $ cd oce
    $ mkdir build && cd build
    $ cmake ..
    $ make -j
    $ sudo make install

**3)** For building IfcConvert with COLLADA (.dae) support (on by default), OpenCOLLADA is needed:

    $ sudo apt-get install libpcre3-dev libxml2-dev
    $ git clone https://github.com/KhronosGroup/OpenCOLLADA.git
    $ cd OpenCOLLADA
    Using a known good revision, but HEAD should work too:
    $ git checkout 064a60b65c2c31b94f013820856bc84fb1937cc6
    $ mkdir build && cd build
    $ cmake ..
    $ make -j
    $ sudo make install

**4)** For building the IfcPython wrapper (on by default), SWIG and Python development are needed, if not already available:

    $ sudo apt-get install python-all-dev swig

**5)** To build IfcOpenShell please take the following steps. Alternatively use environment variables for setting the
dependencies' paths. `OCC_INCLUDE_DIR` might be needed to set also. `OPENCOLLADA_INCLUDE_DIR` and `OPENCOLLADA_LIBRARY_DIR`
(and potentially `PCRE_LIBRARY_DIR`) are needed if building with COLLADA support. (`-DCOLLADA_SUPPORT=0` disables it).

    $ cd /path/to/IfcOpenShell
    $ mkdir build && cd build
    $ cmake ../cmake -DOCC_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu/ \
          -DOPENCOLLADA_INCLUDE_DIR="/usr/local/include/opencollada" \
          -DOPENCOLLADA_LIBRARY_DIR="/usr/local/lib/opencollada"  \
          -DPCRE_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu/ \
          -DCGAL_INCLUDE_DIR=/usr/include \
          -DGMP_INCLUDE_DIR=/usr/include \
          -DMPFR_INCLUDE_DIR=/usr/include \
          -DGMP_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu \
          -DMPFR_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu \
          -DHDF5_SUPPORT=Off
    $ make -j

If all worked out correctly you can now use IfcOpenShell. See the examples below.

**6)** Install the project if wanted:

    $ sudo make install
    
### Installing on MacOS Using Homebrew

**1)** Install all dependencies using [Homebrew](https://brew.sh/)

```{shell}
$ brew install boost cmake python3 cgal ftgl gmp libaec opencascade swig hdf5 zlib
# homebrew automatically links most libraries, except some keg-only ones
$ brew link zlib --force
```

**2)** Clone the git repo and its submodules
```{shell}
$ git clone --recurse-submodules https://github.com/IfcOpenShell/IfcOpenShell.git 
```
**3)** Build IfcOpenShell with flags for Homebrew dependencies: (``/usr/local/``) for Intel machines with x84_64 architecture,
(``/opt/homebrew/``) for Apple Silicon processors with arm64 architecture.
```{shell}
$ cd /path/to/IfcOpenShell
$ mkdir build && cd build
# set library flags
$ export LDFLAGS="$LDFLAGS -Wl,-flat_namespace,-undefined,suppress"
$ cmake ../cmake
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
$ make -j$(sysctl -n hw.ncpu)
```

Note: Make sure to compile using the XCode provided Apple Clang compiler, installed with `xcode-select --install
`, rather than a ```brew``` installed C/C++ compiler.

Installing IfcOpenShell with Conda
----------------------------------
Another option for building and installing IfcOpenShell is to use the popular
[Anaconda Python Distribution](https://www.anaconda.com/download).
The requirements are spread across a number of channels.
You can add these channels to your configuration, or specify them all on the command line:

    $ conda install -c conda-forge -c oce -c dlr-sc -c ifcopenshell ifcopenshell

Usage examples
--------------

**Invoking IfcConvert from the command line**

    $ wget -O duplex.zip https://portal.nibs.org/files/wl/\?id=4DsTgHFQAcOXzFetxbpRCECPbbfUqpgo
    $ unzip duplex.zip
    $ ./IfcConvert Duplex_A_20110907_optimized.ifc
    $ less Duplex_A_20110907_optimized.obj

**Using the IfcOpenShell Python interface**

    $ wget -O duplex.zip https://portal.nibs.org/files/wl/\?id=4DsTgHFQAcOXzFetxbpRCECPbbfUqpgo
    $ unzip duplex.zip
    $ python
    >>> import ifcopenshell
    >>> f = ifcopenshell.open("Duplex_A_20110907_optimized.ifc")
    >>>
    >>> # Accessing entity instances by type:
    >>> f.by_type("ifcwall")[:2]
    [#91=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FL9r',#1,'Basic Wall:Interior - Partition (92mm Stud):144586',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5198,#18806,'144586'), #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')]
    >>> wall = _[0]
    >>> len(wall) # number of EXPRESS attributes
    8
    >>>
    >>> # Accessing EXPRESS attributes by name:
    >>> wall.GlobalId 
    '2O2Fr$t4X7Zf8NOew3FL9r'
    >>> wall.Name = "My wall"
    >>> wall.NonExistingAttr
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".\ifcopenshell.py", line 14, in __getattr__
        except: raise AttributeError("entity instance of type '%s' has no attribute'%s'"%(self.wrapped_data.is_a(), name)) from None
    AttributeError: entity instance of type 'IfcWallStandardCase' has no attribute 'NonExistingAttr'
    >>> wall.GlobalId = 3
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".\ifcopenshell.py", line 26, in __setattr__
        self[self.wrapped_data.get_argument_index(key)] = value
      File ".\ifcopenshell.py", line 30, in __setitem__
        self.wrapped_data.set_argument(idx, entity_instance.map_value(value))
      File ".\ifc_wrapper.py", line 118, in <lambda>
        set_argument = lambda self,x,y: self._set_argument(x) if y is None else self
    ._set_argument(x,y)
      File ".\ifc_wrapper.py", line 114, in _set_argument
        def _set_argument(self, *args): return _ifc_wrapper.entity_instance__set_argument(self, *args)
    RuntimeError: INT is not a valid type for 'GlobalId'
    >>> # Creating new entity instances
    >>> f.createIfcCartesianPoint(Coordinates=(1.0,1.5,2.0))
    #27530=IfcCartesianPoint((1.,1.5,2.))
    >>> 
    >>> # Working with GlobalId attributes:
    >>> import uuid
    >>> ifcopenshell.guid.compress(uuid.uuid1().hex)
    '3x4C8Q_6qHuv$P$FYkANRX'
    >>> new_guid = _
    >>> owner_hist = f.by_type("IfcOwnerHistory")[0]
    >>> new_wall = f.createIfcWallStandardCase(new_guid, owner_hist, None, None, Tag='my_tag')
    >>> new_wall.ObjectType = ''
    >>> new_wall.ObjectPlacement = new_wall.Representation = None
    >>>
    >>> # Accessing entity instances by instance id or GlobalId:
    >>> f[92]
    #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')
    >>> f['2O2Fr$t4X7Zf8NOew3FLIE']
    #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')
    >>>
    >>> # Writing IFC-SPF files to disk:
    >>> f.write("out.ifc")

Extra tools
-----------

Also available are a series of utilities that are based on or related to IfcOpenShell.

Those marked with an asterisk are part of IfcOpenShell.

| Name                      | License             |
| ------------------------- | ------------------- |
| bcf                       | LGPL-3.0-or-later   |
| blenderbim                | GPL-3.0-or-later    |
| bsdd                      | LGPL-3.0-or-later   |
| ifc2ca                    | LGPL-3.0-or-later   |
| ifc4d                     | LGPL-3.0-or-later   |
| ifc5d                     | LGPL-3.0-or-later   |
| ifcbimtester              | LGPL-3.0-or-later   |
| ifcblender                | LGPL-3.0-or-later\* |
| ifccityjson               | LGPL-3.0-or-later   |
| ifcclash                  | LGPL-3.0-or-later   |
| ifccobie                  | LGPL-3.0-or-later   |
| ifcconvert                | LGPL-3.0-or-later\* |
| ifccsv                    | LGPL-3.0-or-later   |
| ifcdiff                   | LGPL-3.0-or-later   |
| ifcfm                     | LGPL-3.0-or-later   |
| ifcgeom                   | LGPL-3.0-or-later\* |
| ifcgeom\_schema\_agnostic | LGPL-3.0-or-later\* |
| ifcgeomserver             | LGPL-3.0-or-later\* |
| ifcjni                    | LGPL-3.0-or-later\* |
| ifcmax                    | LGPL-3.0-or-later\* |
| ifcopenshell-python       | LGPL-3.0-or-later\* |
| ifcparse                  | LGPL-3.0-or-later\* |
| ifcpatch                  | LGPL-3.0-or-later   |
| ifcsverchok               | GPL-3.0-or-later    |
| ifcwrap                   | LGPL-3.0-or-later\* |
| qtviewer                  | LGPL-3.0-or-later\* |
| serializers               | LGPL-3.0-or-later\* |

[LGPL]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/COPYING.LESSER "LGPL-3.0-or-later"
[IFC]: https://technical.buildingsmart.org/standards/ifc/ "IFC"
[IFC2x3 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ "IFC2x3 TC1"
[IFC4 Add2 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/ "IFC4 Add2 TC1"
[Visual Studio]: https://www.visualstudio.com/ "Visual Studio"
[Visual C++ Build Tools]: http://landinghub.visualstudio.com/visual-cpp-build-tools "Visual C++ Build Tools"
[MSYS2]: https://msys2.github.io/ "MSYS2"
[win/readme.md]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/win/readme.md "win/readme.md"
[nix/build-all.py]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/nix/build-all.py "nix/build-all.py"
