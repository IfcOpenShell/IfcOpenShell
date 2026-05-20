Packaging the Autodesk Connector
================================

The Autodesk connector is shipped as a self-contained folder that can be
dropped into the Bonsai Viewer connectors directory. PyInstaller bundles the
Python interpreter, Qt, and dependencies so end users do not need Python
installed.

PyInstaller does not cross-compile. Each operating system must build its own
package, typically through a CI matrix.

Output
------

.. code-block:: text

   dist/
     autodesk/
       connector.json
       bonsaiviewer-autodesk[.exe]
       _internal/...
     autodesk-<os>-<arch>.zip

The ``autodesk/`` folder is what Bonsai Viewer expects under the
``connectors`` directory bundled next to the viewer executable
(``<application-dir>/connectors/``).

Build
-----

.. code-block:: bash

   cd src/bonsaiviewer-autodesk
   python -m venv venv
   source venv/bin/activate
   pip install -e ".[build]"
   python packaging/build.py

On Windows, activate the virtual environment with
``venv\Scripts\activate``.

The build script:

1. cleans ``dist/`` and ``build/``
2. runs PyInstaller against ``packaging/bonsaiviewer-autodesk.spec``
3. renames the produced folder to ``autodesk/``
4. copies ``connector.json`` into it
5. zips the folder as ``autodesk-<os>-<arch>.zip``

The UI uses Tcl/Tk through CustomTkinter, which keeps the bundle small. Expect
roughly 50 MB unpacked or 21 MB zipped per OS. The Python used to build must
include ``tkinter``.

Linux
-----

Build on the oldest glibc you intend to support. Binaries built on a newer
glibc will not run on older distributions. Ubuntu 22.04 LTS, with glibc 2.35,
is a reasonable lowest common denominator in 2026.

The runtime keyring backend is Secret Service, such as gnome-keyring or
KWallet. End users need a Secret Service provider running.

Expected output: ``autodesk-linux-x86_64.zip`` and/or an ARM64 archive.

macOS
-----

Each architecture builds separately. To support Apple Silicon and Intel, build
on each architecture and ship two zips, or post-process with ``lipo`` to
produce universal binaries.

The runtime keyring backend is the system Keychain. For distribution outside
the developer's machine, codesign the executable and Tcl/Tk dylibs and notarize
the bundle. Unsigned binaries trigger Gatekeeper warnings. Codesigning is left
to the caller; the spec's ``codesign_identity`` field can be wired up.

Expected output: ``autodesk-macos-arm64.zip`` and/or
``autodesk-macos-x86_64.zip``.

Windows
-------

Build with the Microsoft Visual C++ runtime available, which is usually true
for modern Python distributions. The runtime keyring backend is Credential
Manager.

The executable is built with ``console=True`` because the connector speaks
JSON-RPC over stdio. Bonsai Viewer must launch it without showing a console
window, for example with Qt's ``QProcess::setCreateProcessArgumentsModifier``
and ``CREATE_NO_WINDOW``.

For distribution, sign the executable with an Authenticode certificate to avoid
SmartScreen warnings. Signing is left to the caller.

Expected output: ``autodesk-windows-x86_64.zip``.

Install a Built Connector
-------------------------

Extract the zip into the ``connectors`` directory next to the Bonsai Viewer
executable.

Linux:

.. code-block:: bash

   unzip dist/autodesk-linux-x86_64.zip -d <application-dir>/connectors/

macOS:

.. code-block:: bash

   unzip dist/autodesk-macos-arm64.zip -d "<application-dir>/connectors/"

Windows PowerShell:

.. code-block:: powershell

   Expand-Archive dist\autodesk-windows-x86_64.zip -DestinationPath "<application-dir>\connectors\"

Bonsai Viewer discovers the connector on next launch.

Out of Scope
------------

- signing and notarization
- CI matrix setup
- auto-update
- universal macOS binaries via ``lipo``
