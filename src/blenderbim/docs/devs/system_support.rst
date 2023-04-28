System support
==============

The BlenderBIM Add-on officially supports all major 64-bit platforms, as well as
the Python version shipped by the Blender Foundation for the most recent three
major Blender versions:

- 64-bit Linux on Python 3.10
- 64-bit MacOS on Python 3.10
- 64-bit MacOS M1 on Python 3.10
- 64-bit Windows on Python 3.10

Note that developer builds may exist for older versions of Python but there will
be no guarantee of the uptime or stability of these builds.

Other system specifications match the `Blender Requirements
<https://www.blender.org/download/requirements/>`_.

Add-on compatibility
--------------------

The BlenderBIM Add-on is a non-trivial add-on. By turning Blender into a
graphical front-end to a native IFC authoring platform, some fundamental Blender
features (such as object deletion and object duplication) have been patched.

Other add-ons may no longer work as intended when the BlenderBIM Add-on is
enabled, or vice versa, the BlenderBIM Add-on may no longer work as intended
when other add-ons are enabled.

Known scenarios which will lead to add-on incompatibility include:

- The add-on overrides object deletion or duplication
- The add-on uses object deletion or duplication macros with dictionary
  override. Note that this is also deprecated in Blender, so the other add-on
  should be updated to fix this.
