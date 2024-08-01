Installation
============

There are different methods of installation, depending on your situation.

1. **Pre-built packages** is recommended for users wanting to use the latest IfcOpenShell builds.
2. **Conda** is recommended for developers using Anaconda.
3. **Docker** is recommended for developers using Docker.
4. **Compiling from source** is recommended for developers actively working with the C++ core.
5. **Packaged installation** is recommended for those who use a package manager.

Pre-built packages
------------------

1. Download the appropriate version for your operating system.

   +---------------------------+-------------------------+-------------------------+---------------------------+-----------------------------+
   | Linux 64bit               | Windows 32bit           | Windows 64bit           | MacOS 64bit               | MacOS M1 64bit              |
   +===========================+=========================+=========================+===========================+=============================+
   | :ifcconvert_url:`linux64` | :ifcconvert_url:`win32` | :ifcconvert_url:`win64` | :ifcconvert_url:`macos64` | :ifcconvert_url:`macosm164` |
   +---------------------------+-------------------------+-------------------------+---------------------------+-----------------------------+

2. Unzip the downloaded file and run IfcConvert using the command line.

Conda
-----

.. code-block::

    # To install the latest daily build of IfcOpenShell (recommended)
    conda install -c ifcopenshell -c conda-forge ifcopenshell

.. note::

    Installing IfcConvert from Conda will also install IfcOpenShell-Python.

Docker
------

.. code-block:: bash

    docker run -it aecgeeks/ifcopenshell IfcConvert

.. note::

    Installing IfcConvert from Docker will also install IfcOpenShell-Python.

Compiling from source
---------------------

Advanced developers may want to compile IfcOpenShell. Refer to the
:doc:`IfcOpenShell installation guide <../ifcopenshell/installation>` for
instructions.

Packaged installation
---------------------

- **Arch Linux**: `Direct from Git <https://aur.archlinux.org/packages/ifcopenshell-git/>`__.
