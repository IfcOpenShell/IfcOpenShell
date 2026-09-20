Installation
============

Bonsai Viewer is a standalone desktop application. It does not require
Blender, Bonsai, or Python to be installed.

1. **Stable** is recommended for most users.
2. **Unstable** is recommended for users wanting the latest features and
   fixes, at the cost of occasional breakage.
3. **Compiling from source** is for developers, see
   :doc:`developer_installation`.

Stable
------

1. Download the release for your operating system.

   +------------------------------+-------------------------------+-------------------------------+
   | Windows                      | Linux                         | MacOS                         |
   +==============================+===============================+===============================+
   | :bonsaiviewer_url:`win64`    | :bonsaiviewer_url:`linux64`   | :bonsaiviewer_url:`macosm164` |
   +------------------------------+-------------------------------+-------------------------------+
   | :bonsaiviewer_url:`win-arm64`| :bonsaiviewer_url:`linuxarm64`|                               |
   +------------------------------+-------------------------------+-------------------------------+

   Only Apple Silicon Macs are supported.

2. Unzip the downloaded file anywhere.
3. Run ``BonsaiViewer`` (``BonsaiViewer.exe`` on Windows, ``BonsaiViewer.app``
   on MacOS).

All releases are listed on the `GitHub releases page
<https://github.com/IfcOpenShell/IfcOpenShell/releases?q=bonsaiviewer&expanded=true>`__.

Unstable
--------

Every build of IfcOpenShell also builds Bonsai Viewer. Open the `IfcOpenShell
Build Service <https://builds.ifcopenshell.org>`__, find the ``BonsaiViewer``
row of the most recent build, and download the zip for your platform. Install
it the same way as a stable release.

The builds are made on demand rather than on a schedule, so the newest build
may be a few days old. Not every build covers every platform, so you may need
to look at an older build for yours.
