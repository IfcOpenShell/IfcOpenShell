.. _blenderbim/installation:

Installation
============

There are different methods of installation, depending on your situation.

1. **Stable installation** is recommended for regular users.
2. **Unstable installation** is recommended for power users helping with testing.
3. **Building from source** is recommended for distributing a build from source.
4. **Live development environment** is recommended for developers who are actively coding.
5. **Distro installation** is recommended for those who use a Linux package manager.

Stable installation
-------------------

The BlenderBIM Add-on is packaged like a regular Blender add-on, so installation
is the same as any other Blender add-on. The full instructions for end-user
installation is available at the `Get BlenderBIM
<https://blenderbim.org/download.html>`__ website. The latest release is
typically updated every few weeks.

Like all Blender add-ons, they can be installed using ``Edit > Preferences >
Addons > Install > Choose Downloaded ZIP > Enable Add-on Checkbox``. You can
enable add-ons permanently by using ``Save User Settings`` from the Addons menu.

Unstable installation
---------------------

**Unstable installation** is almost the same as **Stable installation**, except
that they are typically updated every day. Simply download a daily build from
the `Github releases page
<https://github.com/IfcOpenShell/IfcOpenShell/releases>`__, then follow the same
instructions as a packaged installation.

You will need to choose which build to download.

- If you are on Blender >=3.1, choose py310
- If you are on Blender >=2.93 and <3.1, choose py39
- If you are on Blender <2.93, choose py37
- Choose linux, macos, or win depending on your operating system

Sometimes, a build may be delayed, or contain broken code. We try to avoid this,
but it happens.

Building from source
--------------------

It is possible to run the latest bleeding edge version of BlenderBIM without
having to wait for an official release, since BlenderBIM is coded in Python and
doesn't require any compilation.

Note that the BlenderBIM Add-on does depend on IfcOpenShell, and IfcOpenShell
does require compilation. The following instructions will use a pre-built
IfcOpenShell (using an IfcOpenBot build) for convenience. Instructions on how to
compile IfcOpenShell is out of scope of this document.

You can create your own package by using the Makefile as shown below. You can
choose between a ``PLATFORM`` of ``linux``, ``macos``, and ``win``. You can
choose between a ``PYVERSION`` of ``py39``, ``py37``, or ``py310``.
::

    $ cd src/blenderbim
    $ make dist PLATFORM=linux PYVERSION=py310
    $ ls dist/

This will give you a fully packaged Blender add-on zip that you can distribute
and install.

Live development environment
----------------------------

One option for developers who want to actively develop from source is to follow
the instructions from **Building from source**. However, creating a build,
uninstalling the old add-on, and installing a new build is a slow process.
Although it works, it is very slow, so we do not recommend it.

A more rapid approach is to follow the **Unstable installation** method, as this
provides all dependencies for you out of the box.  Then, we can replace certain
Python files that tend to be updated frequently with those from the Git
repository. We're going to use symlinks (Windows users can use ``mklink``), so
we can code in our Git repository, and see the changes in our Blender
installation (you will need to restart Blender to see changes).

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
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/bim/

    # Replace them with links to the Git repository
    $ ln -s src/blenderbim/blenderbim/bim /path/to/blender/X.XX/scripts/addons/blenderbim/bim

    # Remove the IfcOpenShell dependency Python code
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

    # Replace them with links to the Git repository
    $ ln -s src/ifcopenshell-python/ifcopenshell/api /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ ln -s src/ifcopenshell-python/ifcopenshell/util /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

On Windows:

::

    $ git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    $ cd IfcOpenShell

    # Remove the Blender add-on Python code
    $ rd /S /Q "\path\to\blender\X.XX\scripts\addons\blenderbim\bim\"

    # Replace them with links to the Git repository
    $ mklink /D "\path\to\blender\X.XX\scripts\addons\blenderbim\bim" "src\blenderbim\blenderbim\bim"

    # Remove the IfcOpenShell dependency Python code
    $ rd \S \Q "\path\to\blender\X.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\api"
    $ rd \S \Q "\path\to\blender\X.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\util"

    # Replace them with links to the Git repository
    $ mklink \D "\path\to\blender\X.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\api" "src\ifcopenshell-python\ifcopenshell\api"
    $ mklink \D "\path\to\blender\X.XX\scripts\addons\blenderbim\libs\site\packages\ifcopenshell\util" "src\ifcopenshell-python\ifcopenshell\util"


After you modify your code in the Git repository, you will need to restart
Blender for the changes to take effect. In ``Edit > Preferences > Add-ons`` you
will see that the version number of the BlenderBIM Add-on has changed to
``0.0.999999``, which represents an un-versioned BlenderBIM Add-on.

Distro installation
-------------------

Those on Arch Linux can check out this `AUR package <https://aur.archlinux.org/packages/ifcopenshell-git/>`__.

Tips for package managers
-------------------------

If you are interested in packaging the BlenderBIM Add-on for a packaging
manager, read on.

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
Python modules, binaries, and static assets. When packaged for users, these
dependencies are bundled with the add-on for convenience.

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
    hppfcl
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
2. ``behave`` requires `patches <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcbimtester/patch>`__.
3. ``ifcjson`` can be found `here <https://github.com/IFCJSON-Team/IFC2JSON_python/tree/master/file_converters>`__.

Required static assets are:
::

    bim/data/gantt/jsgantt.js (from jsgantt-improved)
    bim/data/gantt/jsgantt.css (from jsgantt-improved)

Where is the BlenderBIM Add-on installed?
-----------------------------------------

If you downloaded Blender as a ``.zip`` file without running an installer, you
will find the BlenderBIM Add-on installed in the following directory, where
``X.XX`` is the Blender version:
::

    /path/to/blender/X.XX/scripts/addons/

Otherwise, if you installed Blender using an installation package, the add-ons
folder depends on which operating system you use. On Linux:
::

    ~/.config/blender/X.XX/scripts/addons/

On Mac:
::

    /Users/{YOUR_USER}/Library/Application Support/Blender/X.XX/

On Windows:
::

    C:\Users\{YOUR_USER}\AppData\Roaming\Blender Foundation\X.XX\scripts\addons

Upon installation, the BlenderBIM Add-on is stored in the ``blenderbim/``
directory.

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

FAQ
---

1. I get an error similar to "ImportError: IfcOpenShell not built for 'linux/64bit/python3.7'"

Check which BlenderBIM Add-on build you are using. The zip will have either
``py37``, ``py39``, or ``py310`` in the name. See the instructions in the
**Unstable installation** section to check that you have installed the correct
version.

2. I am on Ubuntu and get an error similar to "ImportError: /lib/x86_64-linux-gnu/libm.so.6: version GLIBC_2.29 not found"

Our latest package which uses IfcOpenShell v0.7.0 is built using Ubuntu 20 LTS.
If you have an older Ubuntu version, you can either upgrade to 19.10 or above,
or you'll need to compile IfcOpenShell yourself.
