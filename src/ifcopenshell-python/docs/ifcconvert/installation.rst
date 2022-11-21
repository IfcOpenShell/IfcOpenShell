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

   +----------------+----------------+----------------+----------------+------------------+
   | Linux 64bit    | Windows 32bit  | Windows 64bit  | MacOS 64bit    | MacOS M1 64bit   |
   +================+================+================+================+==================+
   | build-linux64_ | build-win32_   | build-win64_   | build-macos64_ | build-macosm164_ |
   +----------------+----------------+----------------+----------------+------------------+

.. _build-linux64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-cdde536-linux64.zip
.. _build-win32: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-cdde536-win32.zip
.. _build-win64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-cdde536-win64.zip
.. _build-macos64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-cdde536-macos64.zip
.. _build-macosm164: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-cdde536-macosm164.zip

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

.. code-block::

    $ docker run -it aecgeeks/ifcopenshell IfcConvert

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
