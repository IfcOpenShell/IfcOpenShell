Installation
============

There are different methods of installation, depending on your situation.

1. **Pre-built packages** is recommended for users wanting to use the latest IfcOpenShell builds.
2. **Conda** is recommended for developers using Anaconda.
3. **Compiling from source** is recommended for developers actively working with the C++ core.
4. **Packaged installation** is recommended for those who use a package manager.

Pre-built packages
------------------

1. Download the appropriate version for your operating system.

   +----------------+----------------+----------------+----------------+
   | Linux 64bit    | Windows 32bit  | Windows 64bit  | MacOS 64bit    |
   +================+================+================+================+
   | build-linux64_ | build-win32_   | build-win64_   | build-macos64_ |
   +----------------+----------------+----------------+----------------+

.. _build-linux64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-dc67287-linux64.zip
.. _build-win32: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-dc67287-win32.zip
.. _build-win64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-dc67287-win64.zip
.. _build-macos64: https://s3.amazonaws.com/ifcopenshell-builds/IfcConvert-v0.7.0-dc67287-macos64.zip

.. warning::

   Versions for Mac ARM devices (M1 chip) are not yet available. You are free to
   compile it yourself manually, but this requires a level of technical
   expertise.

2. Unzip the downloaded file and run IfcConvert using the command line.

Conda
-----

.. code-block::

    # To install the latest daily build of IfcOpenShell (recommended)
    conda install -c ifcopenshell -c conda-forge ifcopenshell

.. note::

    Installing IfcConvert from Conda will also install IfcOpenShell-Python.

Compiling from source
---------------------

Advanced developers may want to compile IfcOpenShell. Refer to the
:doc:`IfcOpenShell installation guide <../ifcopenshell/installation>` for
instructions.

Packaged installation
---------------------

- **Arch Linux**: `Direct from Git <https://aur.archlinux.org/packages/ifcopenshell-git/>`__.
