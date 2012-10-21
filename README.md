IfcOpenShell 
============
open source (LGPL) software library for working with the IFC file format


http://IfcOpenShell.org

About this repository
=====================

This is an initiative to expose the functionality of IfcOpenShell for parsing and writing IFC files to a Python interface. The creation of a topological representation for building elements using Open Cascade is also wrapped by returning a string serialization of the Open Cascade TopoDS_Shape. Using SWIG a wrapper is obtained for a C++ Class which evaluates its Express attribute names and indices at runtime. The functions created by the SWIG wrapper closely resemble the C++ structure. The idea is to create an additional wrapper around these function in Python that is more idiomatic to Python.

The following interactive session illustrates its use:

    >>> import IfcImport
    >>> f = IfcImport.open(filename)
    >>> f.by_type("ifcwall")
    [#170=IfcWallStandardCase('0lJANQLbCEHPkU1Xq9w_bk',#13,'Wand-001',$,$,#167,#240,'2F4CA5DA-5653-0E45-9B-9E-061D09EBE96E'), 
    #288=IfcWallStandardCase('1sFBHOg98nGQTuD1XjjAKK',#13,'Wand-002',$,$,#285,#358,'763CB458-A892-3141-A7-78-34186DB4A514')]
    >>> wall = _[0]
    >>> brep_data = IfcImport.create_shape(wall)
    >>> wall.get_argument_count()
    8
    >>> wall.get_argument('GlobalId')
    '0lJANQLbCEHPkU1Xq9w_bk'
    >>> wall.get_argument_index('Name')
    2
    >>> wall.set_argument(2,"John")
    >>> wall.get_argument('Name')
    'John'
    >>> wall.get_argument_index("foo")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "IfcImport.py", line 112, in get_argument_index
        def get_argument_index(self, *args): return _IfcImport.Entity_get_argument_index(self, *args)
    RuntimeError: Argument foo not found on IfcRoot
    >>> wall.set_argument(5,"Hi")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "IfcImport.py", line 114, in set_argument
        def set_argument(self, *args): return _IfcImport.Entity_set_argument(self, *args)
    RuntimeError: STRING is not a valid type for 'ObjectPlacement'
    >>> e = IfcImport.Entity("IfcJohn")
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "IfcImport.py", line 105, in __init__
        this = _IfcImport.new_Entity(*args)
    RuntimeError: Unable to find find keyword in schema
    >>> pnt = IfcImport.Entity("ifccartesianpoint")
    [60478 refs]
    >>> pnt.set_argument(0,IfcImport.Doubles([0,0,0]))
    [60486 refs]
    >>> pnt
    =IfcCartesianPoint((0,0,0))
    >>> f.add(pnt)
    >>> f.write("out.ifc")

**TODO**: By creating an additional wrapper in Python around these methods some syntactic sugar can be added so one is able to say the following instead:

    d = IfcDocument()
    my_wall = d.createIfcWallStandardCase("1$gyu8123...",Representation=my_repr)

With a document specifying a 'catch-all' function that creates the ifc entity based on the method being called, perhaps like so:

    class IfcDocument:
        def create_entity(self,type,*args,**kwargs):
            e = new IfcEntity(type)
            # set all attributes in args and kwargs
            self.add(e)
            return e
        def __getattr__(self,attr):
            if attr[0:5] == 'create': return functools.partial(self.create_entity,attr[5:])
        ...


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
