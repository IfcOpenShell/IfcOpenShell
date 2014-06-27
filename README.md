IfcOpenShell 
============
open source (LGPL) software library for working with the IFC file format


http://IfcOpenShell.org

About this repository
=====================

This is an initiative to expose the functionality of IfcOpenShell for parsing and writing IFC files to a Python interface. The creation of a topological representation for building elements using Open Cascade is also wrapped by returning a string serialization of the Open Cascade TopoDS_Shape. Using SWIG, a wrapper is obtained for a C++ Class which evaluates its Express attribute names at runtime. The functions created by the SWIG wrapper closely resemble the C++ structure. An additional Python wrapper around these functions is created that is more idiomatic to Python.

The following interactive session illustrates its use:

    >>> import ifc
    >>> f = ifc.open("Duplex_A_20110907_optimized.ifc")
    >>> f.by_type("ifcwall")[:2]
    [#91=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FL9r',#1,'Basic Wall:Interior - Partition (92mm Stud):144586',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5198,#18806,'144586'), #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')]
    >>> wall = _[0]
    >>> brep_data = ifc.create_shape(wall, ifc.SEW_SHELLS)
    >>> len(wall) # number of EXPRESS attributes
    8
    >>> wall.GlobalId
    '2O2Fr$t4X7Zf8NOew3FL9r'
    >>> wall.Name = "My wall"
    >>> wall.NonExistingAttr
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".\ifc.py", line 14, in __getattr__
        except: raise AttributeError("entity instance of type '%s' has no attribute'%s'"%(self.wrapped_data.is_a(), name)) from None
    AttributeError: entity instance of type 'IfcWallStandardCase' has no attribute 'NonExistingAttr'
    >>> wall.GlobalId = 3
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".\ifc.py", line 26, in __setattr__
        self[self.wrapped_data.get_argument_index(key)] = value
      File ".\ifc.py", line 30, in __setitem__
        self.wrapped_data.set_argument(idx, entity_instance.map_value(value))
      File ".\ifc_wrapper.py", line 118, in <lambda>
        set_argument = lambda self,x,y: self._set_argument(x) if y is None else self
    ._set_argument(x,y)
      File ".\ifc_wrapper.py", line 114, in _set_argument
        def _set_argument(self, *args): return _ifc_wrapper.entity_instance__set_argument(self, *args)
    RuntimeError: INT is not a valid type for 'GlobalId'
    >>> f.createIfcCartesianPoint(Coordinates=(1.0,1.5,2.0))
    #27530=IfcCartesianPoint((1.,1.5,2.))
    >>> import uuid
    >>> ifc.guid.compress(uuid.uuid1().hex)
    '3x4C8Q_6qHuv$P$FYkANRX'
    >>> new_guid = _
    >>> owner_hist = f.by_type("IfcOwnerHistory")[0]
    >>> new_wall = f.createIfcWallStandardCase(new_guid, owner_hist, None, None, Tag='my_tag')
    >>> new_wall.ObjectType = ''
    >>> new_wall.ObjectPlacement = new_wall.Representation = None
    >>> f[92]
    #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')
    >>> f['2O2Fr$t4X7Zf8NOew3FLIE']
    #92=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FLIE',#1,'Basic Wall:Interior - Partition (92mm Stud):143921',$,'Basic Wall:Interior - Partition (92mm Stud):128360',#5206,#18805,'143921')
    >>> f.write("out.ifc")


Compiling on Windows
====================
Users are advised to use the Visual Studio .sln file in the win/ folder.
For Windows users a prebuilt Open CASCADE version is available from the
http://opencascade.org website. Download and install this version and
provide the paths to the Open CASCADE header and library files to MS
Visual Studio C++.

For building the Autodesk 3ds Max plugin, the 3ds Max SDK needs to be
installed as well as 3ds Max itself. Please provide the include and
library paths to Visual Studio.

For building the IfcPython wrapper, SWIG needs to be installed. Please
download the latest swigwin version from http://www.swig.org/download.html.
After extracting the .zip file, please add the extracted folder to the PATH
environment variable. Python needs to be installed, please provide the
include and library paths to Visual Studio.



Compiling on *nix
====================
Users are advised to build IfcOpenShell using the cmake file provided in
the cmake/ folder. There might be an Open CASCADE package in your operating
system's software repository. If not, you will need to compile Open 
CASCADE yourself. See http://opencascade.org.

For building the IfcPython wrapper, SWIG and Python development are
required.

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
    $ wget ftp://ftp.dds.no/pub/ifc/Munkerud/Munkerud_hus6_BE.zip
    $ unzip Munkerud_hus6_BE.zip
    $ ./IfcObj Munkerud_hus6_BE.ifc
    $ less Munkerud_hus6_BE.obj


Ubuntu Notes
============

The following sequence of commands has been tested successfully on Ubuntu 14.04.

OCE installation. This step worked OK with cmake 2.8.12.2, gcc 4.8.2, g++ 4.8.2. Also, it might take up to an hour to complete.

    apt-get install git cmake gcc g++ libftgl-dev libtbb2 libtbb-dev libboost-all-dev
    cd /
    mkdir git && cd git
    git clone https://github.com/tpaviot/oce.git
    mkdir oceBuild && cd oceBuild
    cmake ../oce
    make -j4
    sudo make install
    
IfcOpenShell installation. This step worked OK with cmake 2.8.12.2, gcc 4.8.2, g++ 4.8.2.

    apt-get install swig
    cd /git/
    git clone https://github.com/aothms/IfcOpenShell.git
    cd IfcOpenShell/cmake
    mkdir build && cd build
    cmake ../
    make -j4
    
Once done, IfcConvert is to be found in the build folder.
    
