IfcOpenShell 
============
Open source (LGPL) software library for working with the IFC file format.

[http://ifcopenshell.org](http://ifcopenshell.org)  
[http://academy.ifcopenshell.org](http://academy.ifcopenshell.org)


Prerequisites
=============
* Git, CMake (2.6 or newer), Visual Studio 2008 or newer (Windows), or GCC (*nix, Clang untested).


Dependencies
============
* [Boost](http://www.boost.org/)
* Open Cascade *optional*, but required for building IfcGeom
  [Official](http://www.opencascade.org/getocc/download/loadocc/) or [community edition](https://github.com/tpaviot/oce)  
  For converting IFC representation items into BRep solids and tesselated meshes
* [ICU](http://site.icu-project.org/) *optional*  
  For handling code pages and Unicode in the parser
* [OpenCOLLADA](https://github.com/khronosGroup/OpenCOLLADA/) *optional*  
  For IfcConvert to be able to write tessellated Collada (.dae) files
* [SWIG](http://www.swig.org/), [Python](https://www.python.org/) libraries *optional*  
  For building the IfcOpenShell Python interface and the Blender add-on
* 3ds Max SDK *optional*  
  For building the 3ds Max plug-in


Compiling on Windows
====================
Users are advised to build IfcOpenShell using the CMake file provided in
the cmake/ folder.

The preferred way to fetch and build this project's dependencies is to use the build scripts
in win/ folder. **See [win/readme.md] for more information**. Instructions in a nutshell
(**assuming Visual Studio 2015 x64 environment variables set**):

    > git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    > cd IfcOpenShell\win
    > build-deps.cmd
    > run-cmake.bat

You can now open and build the solution file in Visual Studio:

    > ..\build-vs2015-x64\IfcOpenShell.sln

As the scripts default to using the `RelWithDebInfo` configuration, and a freshly created solution by CMake defaults
to `Debug`, make sure to switch the used build configuration. Build the `INSTALL` project (right-click -> Project
Only) to deploy the headers and binaries into a single location if wanted/needed.

Alternatively, one can use the utility batch files to build and install the project easily from the command-line:

    > build-ifcopenshell.cmd
    > install-ifcopenshell.cmd

Alternatively, the old Visual Studio solution and project files requiring manual work can
be found from the win/sln folder.


Compiling on *nix
=================
Users are advised to build IfcOpenShell using the CMake file provided in
the cmake/ folder. There might be an Open CASCADE package in your operating
system's software repository. If not, you will need to compile Open 
CASCADE yourself. See http://opencascade.org.

For building the IfcPython wrapper, SWIG and Python development are
required.

Additionally, on Ubuntu (and possibly other linux flavors) the following steps
install some of the prerequisites:

    $ sudo apt-get install git swig cmake gcc g++ libftgl-dev libtbb2 libtbb-dev libboost-all-dev libgl1-mesa-dev libfreetype6-dev
    $ git clone https://github.com/tpaviot/oce.git
    $ cd oce
    $ mkdir build && cd build
    $ cmake ..
    $ make
    $ sudo make install   

To build IfcOpenShell please take the following steps:

    $ cd /path/to/IfcOpenShell/cmake
    $ mkdir build
    $ cd build
    Optionally:
        $ OCC_INCLUDE_PATH="/path/to/OpenCASCADE/include"
        $ OCC_LIBRARY_PATH="/path/to/OpenCASCADE/lib"
        $ export OCC_INCLUDE_PATH
        $ export OCC_LIBRARY_PATH
    $ cmake ../
    $ make

If all worked out correctly you can now use IfcOpenShell. For example:

**Invoking IfcConvert from the command line**

    $ wget ftp://ftp.dds.no/pub/ifc/Munkerud/Munkerud_hus6_BE.zip
    $ unzip Munkerud_hus6_BE.zip
    $ ./IfcConvert Munkerud_hus6_BE.ifc
    $ less Munkerud_hus6_BE.obj

Or:

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

[win/readme.md]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/win/readme.md "win/readme.md"