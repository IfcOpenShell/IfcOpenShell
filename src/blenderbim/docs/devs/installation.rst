Installation
============

There are different methods of installation, depending on your situation.

1. **Unstable installation** is recommended for power users helping with testing.
2. **Bundling for Blender** is recommended for distributing the add-on.
3. **Live development environment** is recommended for developers who are actively coding.
4. **Packaged installation** is recommended for those who use a package manager.

Unstable installation
---------------------

**Unstable installation** is almost the same as **Stable installation**, except
that they are typically updated every day. Simply download a daily build from
the `Github releases page
<https://github.com/IfcOpenShell/IfcOpenShell/releases>`__, then follow the same
instructions as the **Stable installation**.

You will need to choose which build to download.

- If you are on Blender >=3.1, choose py310
- If you are on Blender >=2.93 and <3.1, choose py39
- If you are on Blender <2.93, choose py37
- Choose ``linux``, ``macos``, ``macosm1`` (for Apple M1 devices), or ``win``
  depending on your operating system

Sometimes, a build may be delayed, or contain broken code. We try to avoid this,
but it happens.

Bundling for Blender
--------------------

Instead of waiting for an official release on the BlenderBIM Add-on website, it
is possible to make your own Blender add-on from the bleeding edge source code
of BlenderBIM. BlenderBIM is coded in Python and doesn't require any
compilation, so this is a relatively easy process.

Note that the BlenderBIM Add-on does depend on IfcOpenShell, and IfcOpenShell
does require compilation. The following instructions will use a pre-built
IfcOpenShell (using an IfcOpenBot build) for convenience. Instructions on how to
compile IfcOpenShell is out of scope of this document.

You can create your own package by using the Makefile as shown below. You can
choose between a ``PLATFORM`` of ``linux``, ``macos``, ``macosm1``, and ``win``.
You can choose between a ``PYVERSION`` of ``py39``, ``py37``, or ``py310``.
::

    $ cd src/blenderbim
    $ make dist PLATFORM=linux PYVERSION=py310
    $ ls dist/

This will give you a fully packaged Blender add-on zip that you can distribute
and install.

Live development environment
----------------------------

One option for developers who want to actively develop from source is to follow
the instructions from **Bundling for Blender**. However, creating a build,
uninstalling the old add-on, and installing a new build is a slow process.
Although it works, it is very slow, so we do not recommend it.

A more rapid approach is to follow the **Unstable installation** method, as this
provides all dependencies for you out of the box.

Once you've done this, you can replace certain Python files that tend to be
updated frequently with those from the Git repository. We're going to use
symlinks (Windows users can use ``mklink``), so we can code in our Git
repository, and see the changes in our Blender installation (you will need to
restart Blender to see changes).

For Linux or Mac:

::

    $ git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    $ cd IfcOpenShell

    # Remove the Blender add-on Python code
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/core/
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/tool/
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/bim/

    # Replace them with links to the Git repository
    $ ln -s src/blenderbim/blenderbim/core /path/to/blender/X.XX/scripts/addons/blenderbim/core
    $ ln -s src/blenderbim/blenderbim/tool /path/to/blender/X.XX/scripts/addons/blenderbim/tool
    $ ln -s src/blenderbim/blenderbim/bim /path/to/blender/X.XX/scripts/addons/blenderbim/bim

    # Remove the IfcOpenShell dependency Python code
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ rm -r /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

    # Replace them with links to the Git repository
    $ ln -s src/ifcopenshell-python/ifcopenshell/api /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/api
    $ ln -s src/ifcopenshell-python/ifcopenshell/util /path/to/blender/X.XX/scripts/addons/blenderbim/libs/site/packages/ifcopenshell/util

    # Manually download some third party dependencies
    $ cd /path/to/blender/X.XX/scripts/addons/blenderbim/bim/data/gantt
    $ wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
    $ wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css
    $ cd /path/to/blender/X.XX/scripts/addons/blenderbim/bim/schema
    $ wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl

Or, if you're on Windows, you can use the batch script below. 
Before running it follow the instructions descibed after `rem` tags.

.. code-block:: bat

    @echo off

    rem SETUP BLENDER-BIM LIVE DEVELOPMENT ENVIRONMENT
    rem Setup blenderbim addon location below (probably just need to change "x.x" for your Blender version).
    rem Put the script to the folder where IfcOpenShell git repository is located
    rem (script will try to clone IfcOpenShell.git if it's not present).
    SET blenderbim=%appdata%\Blender Foundation\Blender\x.x\scripts\addons\blenderbim

    git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    cd IfcOpenShell

    echo Removing the Blender add-on Python code...
    rd /S /Q "%blenderbim%\core\"
    rd /S /Q "%blenderbim%\tool\"
    rd /S /Q "%blenderbim%\bim\"


    echo Replacing them with links to the Git repository...
    mklink /D "%blenderbim%\core" "%cd%\src\blenderbim\blenderbim\core"
    mklink /D "%blenderbim%\tool" "%cd%\src\blenderbim\blenderbim\tool"
    mklink /D "%blenderbim%\bim" "%cd%\src\blenderbim\blenderbim\bim"


    echo Remove the IfcOpenShell dependency Python code...
    rd /S /Q "%blenderbim%\libs\site\packages\ifcopenshell\api"
    rd /S /Q "%blenderbim%\libs\site\packages\ifcopenshell\util"


    echo Replacing them with links to the Git repository...
    mklink /D "%blenderbim%\libs\site\packages\ifcopenshell\api" "%cd%\src\ifcopenshell-python\ifcopenshell\api"
    mklink /D "%blenderbim%\libs\site\packages\ifcopenshell\util" "%cd%\src\ifcopenshell-python\ifcopenshell\util"


    echo Manually downloading some third party dependencies...
    curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js -o "%blenderbim%\bim\data\gantt\jsgantt.js"
    curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css -o "%blenderbim%\bim\data\gantt\jsgantt.css"
    curl -L https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl -o "%blenderbim%\bim\schema\Brick.ttl"

    pause

After you modify your code in the Git repository, you will need to restart
Blender for the changes to take effect.

The downside with this approach is that if a new dependency is added, or a
compiled dependency version requirement has changed, or the build system
changes, you'll need to fix your setup manually. But this is relatively rare.

.. seealso::

    There is a `useful Blender Addon
    <https://blenderartists.org/uploads/short-url/yto1sjw7pqDRVNQzpVLmn51PEDN.zip>`__
    (see `forum thread
    <https://blenderartists.org/t/reboot-blender-addon/640465/13>`__) that adds
    a Reboot button in File menu.  In this way, it's possible to directly
    restart Blender and test the modified source code.  There is also a VS Code
    add-on called `Blender Development
    <https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development>`__
    that has a similar functionality.


Packaged installation
---------------------

- **Arch Linux**: `Direct from Git <https://aur.archlinux.org/packages/ifcopenshell-git/>`__.
- **Chocolatey on Windows**: `Unstable <https://community.chocolatey.org/packages/blenderbim-nightly/>`__.

Tips for package managers
-------------------------

If you are interested in packaging the BlenderBIM Add-on for a packaging
manager, read on.

The BlenderBIM Add-on is fully contained in the ``blenderbim/`` subfolder of the
Blender add-ons directory. This is typically distributed as a zipfile as per
Blender add-on conventions. Within this folder, you'll find the following file
structure:
::

    core/ (Blender agnostic core code)
    tool/ (Blender specific logic)
    bim/ (Blender specific UI)
    libs/ (dependencies)
    __init__.py

This corresponds to the structure found in the source code `here
<https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.7.0/src/blenderbim/blenderbim>`__.

The BlenderBIM Add-on is complex, and requires many dependencies, including
Python modules, binaries, and static assets. When packaged for users, these
dependencies are bundled with the add-on for convenience.

If you choose to install the BlenderBIM Add-on and use your own system
dependencies, the source of truth for how dependencies are bundled are found in
the `Makefile
<https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.7.0/src/blenderbim/Makefile>`__.

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
2. ``behave`` requires `patches <https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.7.0/src/ifcbimtester/patch>`__.
3. ``ifcjson`` can be found `here <https://github.com/IFCJSON-Team/IFC2JSON_python/tree/master/file_converters>`__.

Required static assets are:
::

    bim/data/gantt/jsgantt.js (from jsgantt-improved)
    bim/data/gantt/jsgantt.css (from jsgantt-improved)
