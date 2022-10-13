Installation
============

There are different methods of installation, depending on your situation.

1. **Pre-built packages** is recommended for users wanting to use the latest IfcOpenShell builds.
2. **PyPI** is recommended for developers using Pip.
3. **Conda** is recommended for developers using Anaconda.
4. **Docker** is recommended for developers using Docker.
5. **Using the BlenderBIM Add-on** is recommended for non-developers wanting a graphical interface.
6. **Compiling from source** is recommended for developers actively working with the C++ core.

Pre-built packages
------------------

1. Choose which version to download based on your operating system, Python
   version, and computer architecture.

   +-------------+----------------+----------------+----------------+----------------+-----------------+
   |             | Linux 64bit    | Windows 32bit  | Windows 64bit  | MacOS 64bit    | MacOS M1 64bit  |
   +=============+================+================+================+================+=================+
   | Python 3.6  | py36-linux64_  | py36-win32_    | py36-win64_    | py36-macos64_  | N/A             |
   +-------------+----------------+----------------+----------------+----------------+-----------------+
   | Python 3.7  | py37-linux64_  | py37-win32_    | py37-win64_    | py37-macos64_  | py37-macosm164_ |
   +-------------+----------------+----------------+----------------+----------------+-----------------+
   | Python 3.8  | py38-linux64_  | py38-win32_    | py38-win64_    | py38-macos64_  | py38-macosm164_ |
   +-------------+----------------+----------------+----------------+----------------+-----------------+
   | Python 3.9  | py39-linux64_  | py39-win32_    | py39-win64_    | py39-macos64_  | py39-macosm164_ |
   +-------------+----------------+----------------+----------------+----------------+-----------------+
   | Python 3.10 | py31-linux64_  | py31-win32_    | py31-win64_    | py31-macos64_  | py31-macosm164_ |
   +-------------+----------------+----------------+----------------+----------------+-----------------+

.. _py36-linux64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-36-v0.7.0-fa6bbf2-linux64.zip
.. _py37-linux64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-37-v0.7.0-fa6bbf2-linux64.zip
.. _py38-linux64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-38-v0.7.0-fa6bbf2-linux64.zip
.. _py39-linux64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-39-v0.7.0-fa6bbf2-linux64.zip
.. _py31-linux64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-31-v0.7.0-fa6bbf2-linux64.zip
.. _py36-win32: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-36-v0.7.0-fa6bbf2-win64.zip
.. _py37-win32: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-37-v0.7.0-fa6bbf2-win64.zip
.. _py38-win32: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-38-v0.7.0-fa6bbf2-win64.zip
.. _py39-win32: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-39-v0.7.0-fa6bbf2-win64.zip
.. _py31-win32: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-31-v0.7.0-fa6bbf2-win64.zip
.. _py36-win64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-36-v0.7.0-fa6bbf2-win64.zip
.. _py37-win64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-37-v0.7.0-fa6bbf2-win64.zip
.. _py38-win64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-38-v0.7.0-fa6bbf2-win64.zip
.. _py39-win64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-39-v0.7.0-fa6bbf2-win64.zip
.. _py31-win64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-31-v0.7.0-fa6bbf2-win64.zip
.. _py36-macos64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-36-v0.7.0-fa6bbf2-macos64.zip
.. _py37-macos64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-37-v0.7.0-fa6bbf2-macos64.zip
.. _py38-macos64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-38-v0.7.0-fa6bbf2-macos64.zip
.. _py39-macos64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-39-v0.7.0-fa6bbf2-macos64.zip
.. _py31-macos64: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-31-v0.7.0-fa6bbf2-macos64.zip
.. _py37-macosm164: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-37-v0.7.0-fa6bbf2-macosm164.zip
.. _py38-macosm164: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-38-v0.7.0-fa6bbf2-macosm164.zip
.. _py39-macosm164: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-39-v0.7.0-fa6bbf2-macosm164.zip
.. _py31-macosm164: https://s3.amazonaws.com/ifcopenshell-builds/ifcopenshell-python-31-v0.7.0-fa6bbf2-macosm164.zip

2. Unzip the downloaded file and copy the ``ifcopenshell`` directory into your
   Python path. If you're not sure where your Python path is, run the following
   code in Python:

   .. code-block:: python

      import sys
      print(sys.path)

   This will give you a list of possible directories that you can install the
   IfcOpenShell module into. Most commonly, you will want to copy the
   ``ifcopenshell`` directory into one of these called ``site-packages``.

3. Test importing the module in a Python session or script to make sure it works.

   .. code-block:: python

      import ifcopenshell
      print(ifcopenshell.version)
      model = ifcopenshell.file()

PyPI
----

.. code-block::

    pip install ifcopenshell

Conda
-----

.. code-block::

    # To install the latest daily build of IfcOpenShell (recommended)
    conda install -c ifcopenshell -c conda-forge ifcopenshell
    # Alteratively, to install an older, stable version
    conda install -c conda-forge ifcopenshell

.. note::

    Installing IfcOpenShell from Conda will also install IfcConvert.

.. warning::

    Conda builds are not yet available for Mac ARM devices (M1 chip). Instead,
    please follow the instructions for the Pre-built packages or PyPI sections
    above.

Docker
------

.. code-block::

    $ docker run -it aecgeeks/ifcopenshell python3 -c 'import ifcopenshell; print(ifcopenshell.version)'

.. note::

    Installing IfcOpenShell from Docker will also install IfcConvert.

Using the BlenderBIM Add-on
---------------------------

The BlenderBIM Add-on is a Blender based graphical interface to IfcOpenShell.
Other than providing a graphical IFC authoring platform, it also comes with
IfcOpenShell, its utilities, and a Python shell built-in. This means you don't
need to install Python first, and you also can compare your IfcOpenShell
scripting to what you see with a visual model viewer, or use a graphical
interface to access the IfcOpenShell utilities.

1. Install the BlenderBIM Add-on by following the `BlenderBIM Add-on
   installation documentation
   <https://blenderbim.org/docs/users/installation.html>`_.

2. Launch Blender. On the top left of the Viewport panel, click the **Editor
   Type** icon to change the viewport into a **Python Console**.

   .. image:: blenderbim-python-console-1.png

3. Make sure you can import IfcOpenShell successfully with the following script.

   .. image:: blenderbim-python-console-2.png

.. tip::

   Before changing the **Editor Type** to a **Python Console**, you can click on
   the ``View > Area > Vertical Split`` menu which will divide your viewport.
   This allows you to write scripts next to the 3D view of a model.

Blender also comes with a text editor so you can write longer scripts.  Instead
of choosing the **Python Console**, choose the **Text Editor**.

.. image:: blenderbim-text-editor-1.png

You can now create a new text file for your script by clicking ``Text > New``,
and run your script using the **Text > Run Script** menu or by clicking on the
**Play Icon**.

.. image:: blenderbim-text-editor-2.png

.. seealso::

   You may be interested in learning how to graphically explore an IFC model in
   Blender.  This can help when learning how to write scripts as you can double
   check the results of your scripts with what you see in the graphical
   interface. `Read more
   <https://blenderbim.org/docs/users/exploring_an_ifc_model.html>`_.


Compiling from source
---------------------

Advanced developers may want to compile IfcOpenShell. Refer to the
:doc:`IfcOpenShell installation guide <../ifcopenshell/installation>` for
instructions.
