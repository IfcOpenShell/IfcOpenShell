Installation
============

There are different methods of installation, depending on your situation.

1. **Packaged installation** is recommended for regular users.
2. **Daily build installation** is recommended for power users helping with testing.
3. **Source installation** is recommended for developers.

Packaged installation
---------------------

IfcSverchok is packaged like a regular Blender add-on, so installation is the
same as any other Blender add-on. `Download IfcSverchok here
<https://github.com/IfcOpenShell/IfcOpenShell/releases/download/ifcsverchok-0.8.1/ifcsverchok-0.8.1.zip>`__.

Like all Blender add-ons, they can be installed using ``Edit > Preferences >
Addons > Install > Choose Downloaded ZIP > Enable Add-on Checkbox``. You can
enable add-ons permanently by using ``Save User Settings`` from the Addons menu.

Before installing, you will also need to `install Bonsai
<https://bonsaibim.org/download.html>`__ and `install Sverchok
<https://github.com/nortikin/sverchok#installation>`__.

If you downloaded Blender as a ``.zip`` file without running an installer, you
will find IfcSverchok installed in the following directory, where ``2.XX`` is
the Blender version:
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

Upon installation, IfcSverchok is stored in the ``ifcsverchok/`` directory.

Daily build installation
------------------------

Daily builds are almost the same as **Packaged installation**, except that they
are typically updated every day. Simply download a daily build from the `Github
releases page <https://github.com/IfcOpenShell/IfcOpenShell/releases>`__, then
follow the same instructions as a packaged installation.

TODO: daily builds not yet available

Daily builds are not always stable. Sometimes, a build may be delayed, or
contain broken code. We try to avoid this, but it happens.

Source installation
-------------------

It is possible to run the latest bleeding edge version of IfcSverchok without
having to wait for an official release, since IfcSverchok is coded in Python and
doesn't require any compilation.

Just symbolically link the IfcSverchok add-on files to your Git repository. If
you're on Windows, use ``mklink`` instead. This allows us to code in our Git
repository, and see the changes in our Blender installation.

.. code-block:: bash

    git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    cd IfcOpenShell

    # Link the repository to blender
    ln -s src/ifcsverchok /path/to/blender/2.XX/scripts/addons/ifcsverchok
    
On Windows:

.. code-block:: bat

    git clone https://github.com/IfcOpenShell/IfcOpenShell.git
    cd IfcOpenShell

    # Link the repository to blender
    mklink /D "\path\to\blender\2.XX\scripts\addons\ifcsverchok" "\path\to\src\ifcsverchok"

After you modify your code in the Git repository, you will need to restart
Blender for the changes to take effect. In ``Edit > Preferences > Add-ons`` you
will see that the version number of IfcSverchok has changed to ``0.0.999999``,
which represents an un-versioned IfcSverchok.

Updating
--------

First uninstall the current IfcSverchok, then install the latest version.

Uninstalling
------------

Navigate to ``Edit > Preferences > Add-ons``, find the IfcSverchok add-on, and
press ``Remove``.

Alternatively, you may uninstall manually by deleting the ``ifcsverchok/``
directory in your Blender add-ons directory.
