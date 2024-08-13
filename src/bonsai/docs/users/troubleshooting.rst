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
**Blender 4.2** installed from https://blender.org/ and have
:ref:`updated to the latest version <users/quickstart/installation:Updating>`.

Other common solutions are listed below. If none of these fix the problem, you
can `report a bug <https://github.com/ifcopenshell/ifcopenshell/issues>`_ or
`live chat with a developer <https://osarch.org/chat/>`_.

1. **Some other error prevents me from installing or doing basic functions with
   the add-on. Is it specific to my environment?**

   Try installing and using the BlenderBIM Add-on on a "clean environment". A
   clean environment is a fresh Blender installation with no other add-ons
   enabled with factory settings.

   To quickly test in a clean environment, first :ref:`find your Blender
   configuration folder<users/quickstart/installation:Where is the add-on
   installed?>`.  Rename the folder from ``X.XX`` to something else like
   ``X.XX_backup``, then restart Blender and try follow the :doc:`installation
   instructions</users/quickstart/installation>` again.

   If this fixes your issue, consider disabling other add-ons one by one until
   you find a conflict as a next step to isolating the issue.

2. **I am on Ubuntu and get an error similar to "ImportError:
   /lib/x86_64-linux-gnu/libm.so.6: version GLIBC_2.29 not found"**

   Our latest package which uses IfcOpenShell v0.8.0 is built using Ubuntu 20 LTS.
   If you have an older Ubuntu version, you can either upgrade to 19.10 or above,
   or you'll need to compile IfcOpenShell yourself.

3. **I get an error saying "ModuleNotFoundError: No module named 'numpy'"**"

   If you have installed Blender from another source instead of from
   `Blender.org <https://www.blender.org/download/>`__, such as from your
   distro's package repositories, then you may be missing some modules like
   ``numpy``. Try installing it manually like ``apt install python-numpy``.

Saving and loading blend files
------------------------------

The BlenderBIM Add-on transform Blender into a native IFC authoring platform.
This means that you can open and save IFC files directly without using
Blender's ``.blend`` format.

All data about your model is saved in your IFC. No data is stored in the
``.blend`` format. This means that if you save or open a ``.blend`` file, you
are **not** saving and loading your model. At best, you are saving and loading
Blender geometry that represents what the model might've looked at at some
point. At worst, you might be looking at a completely wrong model.

If you continue to open and save ``.blend`` files, you will run the risk of
editing something that doesn't actually exist in your IFC model. This will
create unpredictable, and sometimes unrecoverable errors.

To avoid this issue, only open and save IFCs.
