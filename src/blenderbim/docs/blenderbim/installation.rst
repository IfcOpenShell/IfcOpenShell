Installation
============

There are different methods of installation, depending on your situation.

1. **Packaged installation** is recommended for regular users.
2. **Daily build installation** is recommended for power users helping with testing.
3. **Unpackaged installation** is recommended for package managers.
4. **Source installation** is recommended for developers.

Packaged installation
---------------------

The BlenderBIM Add-on is packaged like a regular Blender add-on, so installation
is the same as any other Blender add-on. The full instructions for end-user
installation is available at the `Get BlenderBIM
<https://blenderbim.org/download.html>`__ website. The latest release is
typically updated every few weeks.

Like all Blender add-ons, they can be installed using ``Edit > Preferences >
Addons > Install > Choose Downloaded ZIP > Enable Add-on Checkbox``. You can
enable add-ons permanently by using ``Save User Settings`` from the Addons menu.

If you downloaded Blender as a ``.zip`` file without running an installer, you
will find the BlenderBIM Add-on installed in the following directory, where
``2.XX`` is the Blender version:
::

    /path/to/blender/2.XX/scripts/addons/

Otherwise, if you installed Blender using an installation package, the add-ons
folder depends on which operating system you use. On Linux:
::

    ~/.config/blender/2.XX/scripts/addons/

On Mac:
::

    /Users/{YOUR_USER}/Library/Application Support/Blender/2.XX/

On Windows:
::

    C:\Users\{YOUR_USER}\AppData\Roaming\Blender Foundation\2.XX\scripts\addons

Upon installation, the BlenderBIM Add-on is stored in the ``blenderbim/``
directory.

Daily build installation
------------------------

Daily builds are almost the same as **Packaged installation**, except that they
are typically updated every day. Simply download a daily build from the `Github
releases page <https://github.com/IfcOpenShell/IfcOpenShell/releases>`__, then
follow the same instructions as a packaged installation.

You will need to choose which daily build to download.

- If you are on Blender <2.93, choose py37
- If you are on Blender >=2.93, choose py39
- Choose linux, macos, or win depending on your operating system

Daily builds are not always stable. Sometimes, a build may be delayed, or
contain broken code. We try to avoid this, but it happens.

Unpackaged installation
-----------------------

The BlenderBIM Add-on is fully contained in the ``blenderbim/`` subfolder of the
Blender add-ons directory. This is typically distributed as a zipfile as per
Blender add-on conventions. Within this folder, you'll find the following file
structure:
::

    bim/ (core code)
    libs/ (dependencies)
    __init__.py

This corresponds to the structure found in the source code `here
<https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/blenderbim/blenderbim>`__.

The BlenderBIM Add-on is complex, and requires many dependencies, including
Python modules, binaries, and static assets. These dependencies are bundled with
the add-on for convenience in the **Packaged installation** and **Daily build
installation** methods.

If you choose to install the BlenderBIM Add-on and use your own system
dependencies, the source of truth for how dependencies are bundled are found in
the `Makefile
<https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.6.0/src/blenderbim/Makefile>`__.

Required Python modules to be stored in ``libs/site/packages/`` are:
::

    ifcopenshell
    bcf
    ifcclash
    bimtester
    ifccobie
    ifcdiff
    ifccsv
    ifcpatch
    ifcp6
    pystache
    svgwrite
    dateutil
    isodate
    networkx
    deepdiff
    jsonpickle
    ordered_set
    pyparsing
    xmlschema
    elementpath
    six
    lark-parser
    fcl
    behave
    parse
    parse_type
    xlsxwriter
    odfpy
    defusedxml
    boto3
    botocore
    jmespath
    s3transfer
    ifcjson

Notes:

1. ``ifcopenshell`` almost always requires the latest version due to the fast paced nature of the add-on development.
2. ``fcl`` is not bundled for MacOS, due to lack of maintained community build. This is required for clash detection.
3. ``behave`` requires `patches <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcbimtester/patch>`__.
4. ``ifcjson`` can be found `here <https://github.com/IFCJSON-Team/IFC2JSON_python/tree/master/file_converters>`__.

Required binaries are:
::

    libs/IfcConvert

Required static assets are:
::

    bim/data/gantt/jsgantt.js (from jsgantt-improved)
    bim/data/gantt/jsgantt.css (from jsgantt-improved)

Source installation
-------------------

It is possible to run the latest bleeding edge version of BlenderBIM without
having to wait for an official release, since BlenderBIM is coded in Python and
doesn't require any compilation.

You can create your own package by using the Makefile as shown below. You can
choose between a ``PLATFORM`` of ``linux``, ``macos``, and ``win``. You can
choose between a ``PYVERSION`` of ``py39`` and ``py37``.
::

    $ cd src/blenderbim
    $ make dist PLATFORM=linux PYVERSION=py39
    $ ls dist/

However, creating a build, uninstalling the old add-on, and installing a new
build is a slow process. A more rapid approach is to follow the **Daily build
installation** method, as this provides all dependencies for you out of the box.
Then, we can replace certain Python files that tend to be updated frequently
with those from the Git repository. We're going to use symlinks (Windows user
can use ``mklink``), so we can code in our Git repository, and see the changes
in our Blender installation.

In addition, we're also going to replace the Python code of the IfcOpenShell
dependency with our Git repository, since most of the BlenderBIM Add-on
functionality is agnostic of Blender, and is actually part of IfcOpenShell.
Therefore, we need to keep this dependency highly updated as well.

The downside with this approach is that if a new dependency is added, or a
compiled dependency version requirement has changed, or the build system
changes, you'll need to fix your setup manually. But this is relatively rare.

::

    $ git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    $ cd IfcOpenShell

    # Remove the Blender add-on Python code
    $ rm -r /path/to/blender/2.XX/scripts/addons/blenderbim/bim/

    # Replace them with links to the Git repository
    $ ln -s src/blenderbim/blenderbim/bim /path/to/blender/2.XX/scripts/addons/blenderbim/bim

    # Remove the IfcOpenShell dependency Python code
    $ rm -r /path/to/blender/2.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ rm -r /path/to/blender/2.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

    # Replace them with links to the Git repository
    $ ln -s src/ifcopenshell-python/ifcopenshell/api /path/to/blender/2.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ ln -s src/ifcopenshell-python/ifcopenshell/util /path/to/blender/2.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

On Windows:

::

    $ git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    $ cd IfcOpenShell

    # Remove the Blender add-on Python code
    $ rd /S /Q "\path\to\blender\2.XX\scripts\addons\blenderbim\bim\"

    # Replace them with links to the Git repository
    $ mklink /D "\path\to\blender\2.XX\scripts\addons\blenderbim\bim" "src\blenderbim\blenderbim\bim"

    # Remove the IfcOpenShell dependency Python code
    $ rd \S \Q "\path\to\blender\2.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\api"
    $ rd \S \Q "\path\to\blender\2.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\util"

    # Replace them with links to the Git repository
    $ mklink \D "\path\to\blender\2.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\api" "src\ifcopenshell-python\ifcopenshell\api"
    $ mklink \D "\path\to\blender\2.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\util" "src\ifcopenshell-python\ifcopenshell\util"


After you modify your code in the Git repository, you will need to restart
Blender for the changes to take effect. In ``Edit > Preferences > Add-ons`` you
will see that the version number of BlenderBIM has changed to ``0.0.999999``,
which represents an un-versioned BlenderBIM.

Updating
--------

First uninstall the current BlenderBIM add-on, then install the latest version.

Uninstalling
------------

Navigate to ``Edit > Preferences > Add-ons``. Due to a limitation in Blender,
you have to first disable the BlenderBIM Add-on in your Blender preferences by
pressing the checkbox next to the add-on, then restart Blender. After
restarting, you can uninstall the BlenderBIM Add-on by pressing the ``Remove``
button in the Blender preferences window.

Alternatively, you may uninstall manually by deleting the ``blenderbim/``
directory in your Blender add-ons directory.
