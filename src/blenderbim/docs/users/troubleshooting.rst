Troubleshooting
===============

The BlenderBIM Add-on is alpha software. There are many bugs! When something
goes wrong, you may see some computer code flash up on your screen. You may
also see an error message:

.. image:: images/error-message.png

**Don't panic!** Click on the button that says **Copy Error Message To
Clipboard**. You will need to paste this text in a bug report.

If you do not have a GitHub account, you will need to sign up to report a bug.
In addition to pasting the error message text, please also describe what you
were doing, and attach your IFC file or screenshots if relevant.

.. container:: blockbutton

    `Report a bug <https://github.com/IfcOpenShell/IfcOpenShell/issues/new>`__

If your issue is particularly complex, you can also chat live with developers
or other powerusers.

.. container:: blockbutton

    `Chat live with a developer <https://osarch.org/chat>`_

Installation issues
-------------------

If you are unable to install the BlenderBIM Add-on, make sure you are using
**Blender 4.1** installed from https://blender.org/ and are installing the
latest version from https://blenderbim.org.

Other common solutions are listed below. If none of these fix the problem, you
can `report a bug <https://github.com/ifcopenshell/ifcopenshell/issues>`_ or
`live chat with a developer <https://osarch.org/chat/>`_.

1. **Some other error prevents me from installing or doing basic functions with
   the add-on. Is it specific to my environment?**

   Try installing and using the BlenderBIM Add-on on a "clean environment". A
   clean environment is a fresh Blender installation with no other add-ons
   enabled with factory settings.

   To quickly test in a clean environment, first :ref:`find your Blender
   configuration folder<installation_location>`.
   Rename the folder from ``X.XX`` to something else like ``X.XX_backup``, then
   restart Blender and try follow the :doc:`installation
   instructions</users/quickstart/installation>` again.

   If this fixes your issue, consider disabling other add-ons one by one until
   you find a conflict as a next step to isolating the issue.

2. **I get an error similar to "ImportError: IfcOpenShell not built for 'linux/64bit/python3.10'"**

   If you are using a Mac, be sure to use the Mac Silicon version if you have a
   newer Mac. The only exception is if you have installed Blender using Steam
   on a Mac, in which case you need to use the Mac Intel download.

   For all other scenarios, check the BlenderBIM Add-on zip file which you
   downloaded. The zip will have either ``py39``, ``py310``, or ``py311`` in
   the name. See the instructions in the :ref:`devs/installation:unstable
   installation` section to check that you have installed the correct version.

3. **I am on Ubuntu and get an error similar to "ImportError:
   /lib/x86_64-linux-gnu/libm.so.6: version GLIBC_2.29 not found"**

   Our latest package which uses IfcOpenShell v0.8.0 is built using Ubuntu 20 LTS.
   If you have an older Ubuntu version, you can either upgrade to 19.10 or above,
   or you'll need to compile IfcOpenShell yourself.

4. **I get an error saying "ModuleNotFoundError: No module named 'numpy'"**"

   If you have installed Blender from another source instead of from
   `Blender.org <https://www.blender.org/download/>`__, such as from your
   distro's package repositories, then you may be missing some modules like
   ``numpy``. Try installing it manually like ``apt install python-numpy``.

Common issues
-------------

1. **I get an error similar to RuntimeError: Instance #1234 not found**

   Blender saves and loads projects to a ``.blend`` file. However. the
   BlenderBIM Add-on works with native IFC, and this means instead of saving
   and loading ``.blend`` files, you should instead save and load the ``.ifc``
   project.

   If you have opened a ``.blend`` file, there is a risk that the contents of
   the ``.blend`` session do not correlate to the contents of the ``.ifc``,
   which can cause this error. Unless you are an advanced user, only save and
   load ``.ifc`` files.
