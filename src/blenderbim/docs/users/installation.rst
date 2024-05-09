Installation
============

1. **Download and install Blender**

   Blender is a free and open-source program for 3D authoring. It works on
   Linux, Mac, and Windows. It is developed by the Blender community.

.. container:: blockbutton

    `Download Blender <https://www.blender.org/download/>`__

.. tip::

    No administrator rights on Windows? Choose the "Portable .zip" option when
    downloading from the Blender website.

2. **Download the BlenderBIM Add-on**

   The BlenderBIM Add-on extends Blender with OpenBIM related capabilities.

.. container:: blockbutton

   `Download BlenderBIM Add-on <https://blenderbim.org/download.html>`__

.. warning::

   If you are not using Blender version >=4.1, please follow the **Unstable installation** instructions. :doc:`Read more <../devs/installation>`

3. **Install the BlenderBIM Add-on**

   Open up Blender, and click on ``Edit > Preferences``.

   .. image:: images/install-blenderbim-1.png

   Select the **Add-ons** tab, and press **Install...** on the top right. Navigate
   to the .zip you downloaded in Step 2, and press **Install Add-on**.

   .. image:: images/install-blenderbim-2.png

   .. warning::
   
      You do not need to unzip the add-on file. You should install it as a zipped file.

   You should now see **Import-Export: BlenderBIM** available in your add-ons list. Enable the add-on by pressing the checkbox.

   .. image:: images/install-blenderbim-3.png

All done! Your interface will now look similar to below. If you check the ``File`` menu you should also see an option to ``Open IFC Project``.

.. image:: images/install-blenderbim-4.png

You can enable add-ons permanently by using ``Save User Settings`` from the Addons menu.

.. seealso::

    If you are a poweruser, you may be interested in the **Unstable installation** to help with testing. :doc:`Read more <../devs/installation>`

.. _where is the add-on installed:

Updating
--------

First follow the `Uninstalling`_ section below, then install the latest version.

Uninstalling
------------

Navigate to ``Edit > Preferences > Add-ons``. Due to a limitation in Blender,
you have to **first disable the BlenderBIM Add-on in your Blender preferences**
by pressing the checkbox next to the add-on, then **restart Blender**. It is
critical to follow this sequence of disabling first, and then restarting.

After restarting, you can uninstall the BlenderBIM Add-on by pressing the
``Remove`` button in the Blender preferences window.

Alternatively, you may uninstall manually by deleting the ``blenderbim``
directory in :ref:`your Blender add-ons directory<where is the add-on
installed>`.

.. warning::

    It is important to follow the sequence of disabling, restarting, then removing.
    If you do not restart Blender, the add-on will fail to remove correctly, and you
    will need to uninstall manually.

Where is the add-on installed?
------------------------------

Upon installation, the BlenderBIM Add-on is stored in the
``scripts/addons/blenderbim/`` directory, within your Blender configuration
folder. However, the location of your Blender configuration folder depends on
how you have installed Blender.

If you downloaded Blender as a ``.zip`` file without running an installer, the
BlenderBIM Add-on will be installed in the following directory, where ``X.XX``
is the Blender version:

::

    /path/to/blender/X.XX/scripts/addons/blenderbim/

Otherwise, if you installed Blender using an installation package, the Blender
configuration folder depends on which operating system you use.

On Linux, if you are installing the add-on as a user:

::

    ~/.config/blender/X.XX/scripts/addons/blenderbim/

On Linux, if you are deploying the add-on system-wide (this may also depend on
your Linux distribution):

::

    /usr/share/blender/X.XX/scripts/addons/blenderbim/

On Mac, if you are installing the add-on as a user:

::

    /Users/{YOUR_USER}/Library/Application Support/Blender/X.XX/scripts/addons/blenderbim/

On Mac, if you are deploying the add-on system-wide:

::

    /Library/Application Support/Blender/X.XX/scripts/addons/blenderbim/

On Windows:

::

    C:\Users\{YOUR_USER}\AppData\Roaming\Blender Foundation\X.XX\scripts\addons\blenderbim\
