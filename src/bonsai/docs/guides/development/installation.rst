Installation
============

There are different methods of installation, depending on your situation.

1. :ref:`guides/development/installation:Unstable installation` is recommended
   for power users helping with testing.
2. :ref:`guides/development/installation:Bundling for blender` is recommended for distributing the add-on.
3. :ref:`guides/development/installation:Live development environment` is
   recommended for developers who are actively coding.
4. :ref:`guides/development/installation:Packaged installation` is recommended
   for those who use a package manager.

System requirements
-------------------

Bonsai officially supports all major 64-bit platforms, as well as the Python
version shipped by the Blender Foundation for the most recent three major
Blender versions:

- 64-bit Linux (``linux-x64``)
- 64-bit MacOS Intel (``macos-x64``)
- 64-bit MacOS Silicon (``macos-arm64``)
- 64-bit Windows (``windows-x64``)
- Blender 4.2 with Python 3.11

Due to significant changes in the Blender extensions system, Blender versions
<4.2 are not supported.

Developer builds may exist for different versions of Python but there will be
no guarantee of the uptime or stability of these builds.

Other system specifications match the `Blender Requirements
<https://www.blender.org/download/requirements/>`_ and the `VFX Platform
<https://vfxplatform.com/>`_ standard.

Sometimes, a build may be delayed, or contain broken code. We try to avoid this,
but it happens.

Unstable installation
---------------------

**Unstable installation** is almost the same as **Stable installation**, except
that they are typically updated every day. To install the **Unstable** version:

1. Open up Blender, and click on ``Edit > Preferences``.

   .. image:: /quickstart/images/install-bonsai-1.png

2. Select the **Get Extensions** tab, and press **Allow Online Access**.

   .. image:: /quickstart/images/install-bonsai-2.png

3. Go to the `Bonsai Unstable Repository
   <https://github.com/IfcOpenShell/bonsai_unstable_repo>`__, and drag and drop
   from the appropriate link in the ``ID`` column of the table into Blender
   depending on your operating system.

   .. image:: images/unstable-drag-drop.png

4. Enable **Check for Updates on Startup** to get updates for daily Bonsai
   builds automatically.

   .. image:: images/unstable-auto-update.png

.. tip::

    Instead of drag and drop, you can manually create the repository:

    Open :menuselection:`Topbar --> Edit --> Preferences --> Get Extensions
    --> Repositories (Top Right) --> "+" Icon --> Add Remote Remository`.
    You'll see a window similar to the one above.

    Use as URL:
    ``https://raw.githubusercontent.com/IfcOpenShell/bonsai_unstable_repo/main/index.json``
    and enable **Check for Updates on Startup** if you want them.

5. Search for **Bonsai** in the top left search bar, then press the **Install**
   button.

   .. image:: /quickstart/images/install-bonsai-3.png

.. warning::

   Make sure the extension you install has ``raw.githubusercontent.com`` as
   it's "Repository" (not ``extensions.blender.org``).

   .. image:: images/unstable-repo.png

6. Whenever a new update is available, you'll see it in the bottom right
   :menuselection:`Status Bar`

   .. image:: images/unstable-icon.png

7. To update, click on the update button in :menuselection:`Topbar --> Edit -->
   Preferences --> Get Extensions`.

   .. image:: /guides/images/update.png

8. After an update, be sure to restart.

   .. image:: images/unstable-restart.png

If you wish to install an **Unstable** version offline, you can download a
daily or previous build from the `GitHub releases page
<https://github.com/IfcOpenShell/IfcOpenShell/releases?q=bonsai&expanded=true>`__,
then go to :menuselection:`Topbar --> Edit --> Preferences --> Get Extensions
--> "V" Icon (top right) --> Install from Disk`.

.. tip::

   Installing a previous build is a great way to roll back to previous versions. Uninstall the current version, 
   then install the previous version from your disk. Make the install directory into the repo folder, and you can still 
   update by the click of a button, when you are ready for the latest build.

Bundling for Blender
--------------------

Instead of waiting for an official release on the Bonsai website, it
is possible to make your own Blender add-on from the bleeding edge source code
of Bonsai. Bonsai is coded in Python and doesn't require any
compilation, so this is a relatively easy process.

Note that Bonsai depends on IfcOpenShell, and IfcOpenShell does require
compilation. The following instructions will use a pre-built IfcOpenShell
(using an IfcOpenBot build) for convenience. Instructions on how to compile
IfcOpenShell is out of scope of this document.

You can create your own package by using the Makefile as shown below. You can
choose between a ``PLATFORM`` of ``linux``, ``macos``, ``macosm1``, and ``win``.
You can choose between a ``PYVERSION`` of ``py312``, ``py311``, ``py310``, or
``py39``.

.. code-block:: bash

    cd src/bonsai
    make dist PLATFORM=linux PYVERSION=py311
    ls dist/

This will give you a fully packaged Blender add-on zip that you can distribute
and install.

Live development environment
----------------------------

One option for developers who want to actively develop from source is to follow
the instructions from :ref:`guides/development/installation:Bundling for Blender`. However,
creating a build, uninstalling the old add-on, and installing a new build is a
slow process.  Although it works, it is very slow, so we do not recommend it.

A more rapid approach is to follow the
:ref:`guides/development/installation:Unstable installation` method, as this
provides all dependencies for you out of the box.

Once you've done this, you can replace certain Python files that tend to be
updated frequently with those from the Git repository. We're going to use
symbolic links, so we can code in our Git repository, and see the changes in
our Blender installation (you will need to restart Blender to see changes).

For Linux or Mac:

.. literalinclude:: ../../../scripts/installation/dev_environment.sh
   :language: bash
   :caption: dev_environment.sh

Or, if you're on Windows, you can use the batch script below. You need to run
it as an administrator. Before running it follow the instructions descibed
in the `rem` tags.

.. literalinclude:: ../../../scripts/installation/dev_environment.bat
   :language: bat
   :caption: dev_environment.bat

After you modify your code in the Git repository, you will need to restart
Blender for the changes to take effect.

The downside with this approach is that if a new dependency is added, or a
compiled dependency version requirement has changed, or the build system
changes, you'll need to fix your setup manually. But this is relatively rare.
Reviewing the Makefile history, `here <https://github.com/IfcOpenShell/IfcOpenShell/commits/v0.8.0/src/bonsai/Makefile>`__, is one quick way to see if a dependency has changed.  

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
- **Chocolatey on Windows**: `Unstable <https://community.chocolatey.org/packages/bonsai-nightly/>`__.

Tips for package managers
-------------------------

Bonsai is fully contained in the ``bonsai/`` subfolder of the Blender add-ons
directory. This is typically distributed as a zipfile as per Blender add-on
conventions. Within this folder, you'll find the following file structure:

::

    core/ (Blender agnostic core logic)
    tool/ (Blender specific shared functionality)
    bim/ (Blender specific UI)
    libs/ (other assets)
    wheels/ (dependencies)
    __init__.py

This corresponds to the structure found in the source code `here
<https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.8.0/src/bonsai/bonsai>`__.

Bonsai is complex, and requires many dependencies, including Python modules,
binaries, and static assets. When packaged for users, these dependencies are
bundled with the add-on for convenience.

If you choose to install Bonsai and use your own system dependencies, the
source of truth for how dependencies are bundled are found in
the `Makefile
<https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.8.0/src/bonsai/Makefile>`__
in the ``dist`` target.

Add-on compatibility
--------------------

Bonsai is a non-trivial add-on. By turning Blender into a graphical front-end
to a native IFC authoring platform, some fundamental Blender features (such as
hotkeys for basic functionality like object deletion or duplication) have been
patched and many dependencies have been introduced.

Other add-ons may no longer work as intended when Bonsai is enabled, or vice
versa, Bonsai may no longer work as intended when other add-ons are enabled.

Known scenarios which will lead to add-on incompatibility include:

- The add-on also overrides the same hotkeys. For example, if an add-on
  overrides the "X" key to delete an object, you will need to manually trigger
  (either via menu or custom hotkey) the Bonsai equivalent operator
  (e.g. IFC Delete).
- The add-on uses object deletion or duplication macros with dictionary
  override. Note that this is also deprecated in Blender, so the other add-on
  should be updated to fix this.
- The add-on requires a conflicting dependency, or a conflicting version of the
  same dependency. Neither add-on may work simultaneously.
