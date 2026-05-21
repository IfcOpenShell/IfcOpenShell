Autodesk Connector
==================

The Autodesk connector integrates Bonsai Viewer with Autodesk Forma, APS, and
Docs. It implements the cloud connector protocol and runs as a separate process
that Bonsai Viewer launches and communicates with over standard input and
standard output.

The connector UI is built with CustomTkinter. The Python runtime used for
development or packaging must include ``tkinter``. On Gentoo, make sure
``dev-lang/python`` is built with ``USE="tk"``.

Install
-------

From the repository root:

.. code-block:: bash

   cd src/bonsaiviewer-autodesk
   python -m venv venv
   source venv/bin/activate
   pip install -e .

Run
---

.. code-block:: bash

   bonsaiviewer-autodesk

The connector launches without configuration. On first run, open the settings
dialog to configure the Autodesk client ID and OAuth callback port.

For direct protocol testing, send newline-delimited JSON-RPC 2.0 requests on
standard input:

.. code-block:: json

   {"jsonrpc":"2.0","id":"0","method":"open_settings"}
   {"jsonrpc":"2.0","id":"1","method":"pull_ifcfed_interactive"}
   {"jsonrpc":"2.0","id":"2","method":"pull_models","params":[{"display_name":"foo.ifc","id":"abc","source":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk...","version_id":"latest"}}]}
   {"jsonrpc":"2.0","id":"3","method":"push_ifcfed_interactive","params":{"path":"/tmp/project.ifcfed"}}
   {"jsonrpc":"2.0","id":"4","method":"push_ifcfed","params":{"path":"/tmp/project.ifcfed","manifest":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk..."}}}

Bonsai Viewer is expected to launch this binary once per session and keep it
alive until shutdown. Closing the connector's standard input triggers a clean
exit.

Configuration
-------------

The connector reads the Autodesk client ID from ``settings.json`` in the
connector config directory, written by the settings dialog.

The OAuth callback host is always ``localhost``. The callback port defaults to
``8080`` and can be changed in the settings dialog.

The config directory is platform-specific:

- Linux: ``~/.config/bonsaiviewer-autodesk/``
- macOS: ``~/Library/Application Support/bonsaiviewer-autodesk/``
- Windows: ``%APPDATA%\bonsaiviewer-autodesk\``

OAuth tokens are stored in the OS keychain, keyed by the client ID. Changing
the client ID starts a fresh sign-in session. The keychain backend is Secret
Service on Linux, Keychain on macOS, and Credential Manager on Windows.

Cache
-----

The connector owns its own cache. On Linux, resolved files live under:

.. code-block:: text

   ~/.cache/bonsaiviewer-autodesk/
     ifcfeds/<hash>/<name>.ifcfed[.manifest]
     models/<hash>/<filename>

Each resolved file is the sole child in its directory so Bonsai Viewer can
write sidecar files, such as ``.ifcview``, next to it without colliding. A new
resolved model version lands in a fresh ``models/<hash>/`` directory. Old cache
directories may be removed manually to clear space.

Status
------

Implemented:

- strict JSON-RPC 2.0 host over stdio
- APS PKCE sign-in with keyring-backed token storage
- hub, project, and folder browsing
- ``pull_ifcfed_interactive``, ``pull_ifcfed``, ``pull_models``, and
  ``pull_models_interactive``
- ``push_ifcfed_interactive``, ``push_ifcfed``,
  ``push_model_interactive``, and ``push_model``
- ``open_settings`` for client ID, callback port, and sign-out
- connector-managed cache with one resolved file per directory
- adjacent ``.ifcfed.manifest`` files written and read alongside
  ``.ifcfed`` files

Not implemented:

- JSON-RPC notifications for progress streaming; the connector shows its own
  progress dialog
- cancellation of in-flight downloads
- subdirectory upload layouts inside push destinations
