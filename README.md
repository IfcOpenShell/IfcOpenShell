IfcOpenShell 
============
IfcOpenShell is an open source ([LGPL]) software library for working with the Industry Foundation Classes ([IFC]) 
file format. Currently supported IFC releases are [IFC2x3 TC1] and [IFC4 Add1].

For more information, see
* [http://ifcopenshell.org](http://ifcopenshell.org)  
* [http://academy.ifcopenshell.org](http://academy.ifcopenshell.org)

[![Build Status](https://api.travis-ci.org/IfcOpenShell/IfcOpenShell.png)](https://api.travis-ci.org/IfcOpenShell/IfcOpenShell)

Prerequisites
-------------
* Git
* CMake (2.6 or newer)
* Windows: [Visual Studio] 2008 or newer with C++ toolset (or [Visual C++ Build Tools]) or [MSYS2] + MinGW
* *nix: GCC 4.7 or newer, or Clang (any version)

Dependencies
-------------
* [Boost](http://www.boost.org/)
* [Open Cascade](http://opencascade.org) - *optional*, but required for building IfcGeom
  ([official](http://www.opencascade.org/getocc/download/loadocc/), "OCCT", or [community edition](https://github.com/tpaviot/oce), "OCE")  
  For converting IFC representation items into BRep solids and tesselated meshes
* [ICU](http://site.icu-project.org/) - *optional*  
  For handling code pages and Unicode in the parser
* [OpenCOLLADA](https://github.com/khronosGroup/OpenCOLLADA/) - *optional*  
  For IfcConvert to be able to write tessellated Collada (.dae) files
* [SWIG](http://www.swig.org/) and [Python](https://www.python.org/) - *optional*  
  For building the IfcOpenShell Python interface and the Blender add-on
* [3ds Max SDK](http://www.autodesk.com/products/3ds-max/free-trial) - *optional*  
  For building the 3ds Max plug-in.
  All recent versions of 3ds Max (2014 and newer) are 64-bit only, so a 64-bit installation is assumed.

Building IfcOpenShell
---------------------

**Note:** The path where the source code is cloned to can contain spaces but non-ASCII characters are very likely to cause problems with the build.

### Compiling on Windows
The preferred way to fetch and build this project's dependencies is to use the build scripts
in win/ folder. **See [win/readme.md] for more information**.

#### Using Visual Studio
Instructions in a nutshell (**assuming Visual Studio 2015 x64 environment variables set**):

    > cd IfcOpenShell\win
    > build-deps.cmd
    > run-cmake.bat

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

The following instructions are for Ubuntu, modify as required for other operating systems. [nix/build-all.sh] script
can be experimented with and studied for pointers for other operating systems, but note that this script is not currently
meant to be used for a typical IfcOpenShell workspace setup.

**1)** Install most of the prerequisites and dependencies:

    $ sudo apt-get install git cmake gcc g++ libboost-all-dev libicu-dev

**2a)** Either use an OCE package from your operating system's software repository

    $ sudo apt-get install liboce-foundation-dev liboce-modeling-dev liboce-ocaf-dev liboce-visualization-dev liboce-ocaf-lite-dev

**2b)** or (if not available, or the latest code is wanted) compile OCE yourself (note that the build takes a long time):

    $ sudo apt-get install libftgl-dev libtbb2 libtbb-dev libgl1-mesa-dev libfreetype6-dev
    $ git clone https://github.com/tpaviot/oce.git
    $ cd oce
    $ mkdir build && cd build
    $ cmake ..
    $ make -j
    $ sudo make install

**2c)** or obtain and compile OCCT from http://www.opencascade.org/getocc/download/loadocc/

**3)** For building IfcConvert with COLLADA (.dae) support (on by default), OpenCOLLADA is needed:

    $ sudo apt-get install libpcre3-dev
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
          -DPCRE_LIBRARY_DIR=/usr/lib/x86_64-linux-gnu/
    $ make -j

If all worked out correctly you can now use IfcOpenShell. See the examples below.

**6)** Install the project if wanted:

    $ sudo make install

Usage examples
--------------

**Invoking IfcConvert from the command line**

    $ wget ftp://ftp.dds.no/pub/ifc/Munkerud/Munkerud_hus6_BE.zip
    $ unzip Munkerud_hus6_BE.zip
    $ ./IfcConvert Munkerud_hus6_BE.ifc
    $ less Munkerud_hus6_BE.obj

**Using the IfcOpenShell Python interface**

    $ wget -O duplex.zip http://projects.buildingsmartalliance.org/files/?artifact_id=4278
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

[LGPL]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/COPYING "LGPL"
[IFC]: http://www.buildingsmart-tech.org/specifications/ifc-overview "IFC"
[IFC2x3 TC1]: http://www.buildingsmart-tech.org/specifications/ifc-releases/ifc2x3-tc1-release "IFC2x3 TC1"
[IFC4 Add1]: http://www.buildingsmart-tech.org/specifications/ifc-releases/ifc4-add1-release "IFC4 Add1"
[Visual Studio]: https://www.visualstudio.com/ "Visual Studio"
[Visual C++ Build Tools]: http://landinghub.visualstudio.com/visual-cpp-build-tools "Visual C++ Build Tools"
[MSYS2]: https://msys2.github.io/ "MSYS2"
[win/readme.md]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/win/readme.md "win/readme.md"
[nix/build-all.sh]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/nix/build-all.sh "nix/build-all.sh"