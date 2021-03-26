Installation
============

BlenderBIM is packaged as a Blender add-on, so installation is the same as any
other Blender add-on. The full instructions for end-user installation is
available at the `Get BlenderBIM <https://blenderbim.org/download.html>`_
website.

If you downloaded Blender as a ``.zip`` file without running an installer, you
will find the BlenderBIM plug-in installed in:
::

    /path/to/blender/2.81/scripts/addons/

Otherwise, if you installed Blender using an installation package, the add-ons
folder depends on which operating system you use. On Linux:
::

    ~/.config/blender/2.81/scripts/addons/

On Mac:
::

    /Users/{YOUR_USER}/Library/Application Support/Blender/2.81/

On Windows:
::

    C:\Users\{YOUR_USER}\AppData\Roaming\Blender Foundation\2.81\scripts\addons

Upon installation, a series of files will be created. This is necessary as
BlenderBIM has a variety of complex dependencies. A full list is below:
::

    blenderbim/
    ifcopenshell/
    OCC/
    pystache/
    svgwrite/
    deepdiff/
    jsonpickle/
    lib/ # Note: this only exists on MacOS and Linux
    ordered_set.py
    pyparsing.py

If you are not on Windows, when BlenderBIM first launches, it will create a
bunch of library files in the ``2.81/`` folder too. This is a non-standard
location to place files, but is a hack to allow people to use precompiled builds
from Conda.

If you receive an error when enabling the add-on, you may have installed the
package for the wrong platform.

Updating
--------

It is recommended to uninstall the current BlenderBIM add-on before installing
the latest version to ensure the update goes well.

From Source
-----------

It is possible to run the latest bleeding edge version of BlenderBIM without
having to wait for an official release, since BlenderBIM is coded in Python and
doesn't require any compilation. First, install the latest official release, and
then `download the latest source code
<https://github.com/IfcOpenShell/IfcOpenShell/archive/v0.6.0.zip>`_. If you know
how to use Git, you can also stay up to date like so:
::

    $ git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    $ cd IfcOpenShell
    $ git checkout v0.6.0

Then, just copy the files from the source code's
``src/ifcblenderexport/blenderbim/`` folder and replace the files in your
Blender add-on's ``blenderbim/`` folder.

Restart Blender for the changes to take effect. In ``Edit > Preferences >
Add-ons`` you will see that the version number of BlenderBIM has changed to
``0.0.999999``, which represents an un-versioned BlenderBIM.

Uninstalling
------------

You can remove all of the files added by BlenderBIM in the Blender add-ons
folder and then remove the add-on using the Blender interface through ``Edit >
Preferences > Add-ons`` just like any other add-on.

If you are not on Windows, then ensure that all library files are deleted in the
``2.81/`` directory. Do not delete any of Blender's own folders.
