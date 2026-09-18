Cloud Connector Protocol
========================

Bonsai Viewer can load and save projects and models from cloud platforms
through connectors. A connector is a separate application launched by Bonsai
Viewer. It handles authentication, browsing, downloads, uploads, caching, and
platform-specific behaviour.

The protocol currently covers:

- projects: ``.ifcfed``
- models: ``.ifc``, ``.rdb``, ``.ifcview``, ``.rdbview``

Issues, clash results, specifications, and other resources are not yet defined.

Communication
-------------

Bonsai Viewer launches one connector process per session, on first use, and
keeps it alive for the duration of the session. Communication uses
newline-delimited JSON-RPC 2.0 over standard input and standard output:

- requests and responses are single-line JSON objects
- every message is terminated by a single newline
- the connector must not emit literal newlines inside a JSON message
- diagnostics may be written to standard error

Bonsai Viewer shuts down a connector by closing its standard input. The
connector should exit cleanly. If it does not exit within a few seconds, Bonsai
Viewer may terminate it.

Connector Scope
---------------

Bonsai Viewer only works with local files. If a project or model is not local,
the viewer asks a connector to resolve it. The connector returns a local path
and optional cloud metadata. It must not modify the model file itself.

The connector handles anything specific to the cloud platform or data source:
authentication, browsing, filtering, searches, revision pinning, progress UI,
caches, and platform-specific rules. A connector may show its own UI or run
without UI.

Returned files must be the sole child in their directory. This allows Bonsai
Viewer to write adjacent sidecars, temporary files, database locks, or helper
files without filename collisions. A connector may invalidate cached files by
deleting the whole resolved directory. A new cloud revision should resolve to a
fresh directory.

Projects
--------

A project is an ``.ifcfed`` file. It stores project settings and model entries.

Example project:

.. code-block:: json

   {
       "created": "2026-04-29T21:22:36Z",
       "modified": "2026-04-29T21:22:36Z",
       "home_view": null,
       "models": []
   }

A cloud-sourced project may have an adjacent ``.ifcfed.manifest`` file storing
connector-specific source metadata.

.. code-block:: json

   {
       "connector": "mycompany",
       "version": "2",
       "url": "https://example.com/project.ifcfed"
   }

Models
------

Models are listed in the ``.ifcfed`` file. A model may point to a local path or
to a cloud connector source.

Cloud connector source data is intentionally connector-specific. For example,
a connector may store whether a model is pinned to one revision or should
always resolve to the latest revision.

.. code-block:: json

   [
       {
           "display_name": "foo.ifc",
           "id": "0503642e-e2f6-4700-87fd-16479542e801",
           "source": {
               "connector": "local",
               "path": "path/to/foo.ifc"
           }
       },
       {
           "display_name": "bar.ifc",
           "id": "5fc69e6a-1ff0-4d8a-82c6-2215df53d2ed",
           "source": {
               "connector": "autodesk",
               "version": "1",
               "hub_id": "b.hub123",
               "project_id": "b.project456",
               "item_id": "urn:adsk.wipprod:dm.lineage:abc",
               "version_id": "urn:adsk.wipprod:fs.file:vf.xyz?version=3"
           }
       }
   ]

Cloud metadata such as filename, cloud ID, revision, and date modified is not
specified or stored in the ``.ifcfed``. It is returned by the connector when
requested. Bonsai Viewer displays returned cloud metadata as text. The keys
``author``, ``revision``, and ``date`` may be shown in more prominent UI
locations.

Open from Cloud
---------------

``pull_ifcfed_interactive`` opens an ``.ifcfed`` from a cloud platform and
starts a fresh session.

.. code-block:: json

   { "jsonrpc": "2.0", "id": "0", "method": "pull_ifcfed_interactive" }

The connector authenticates and lets the user browse or choose a project. It
downloads or resolves the ``.ifcfed`` into a connector-managed directory,
creates an adjacent ``.ifcfed.manifest``, and returns the local path:

.. code-block:: json

   { "jsonrpc": "2.0", "id": "0", "result": { "path": "/path/to/project/file.ifcfed" } }

Bonsai Viewer loads the project, then calls ``pull_models`` for cloud-sourced
models referenced by the ``.ifcfed``:

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "1",
       "method": "pull_models",
       "params": [
           { "display_name": "bar.ifc", "id": "...", "source": { "connector": "autodesk" } }
       ]
   }

The connector returns one result per requested model. A result may include
optional metadata. ``null`` means that item was skipped or failed without
aborting the whole batch.

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "1",
       "result": [
           {
               "path": "/path/to/model.ifc",
               "metadata": { "revision": "B", "date": "2nd Oct 2025" }
           },
           null
       ]
   }

Downloading the latest version of every model immediately is not required. A
connector may download the latest file, use a pinned revision, offer the user a
choice, skip a model, or return a cached file. The user can reopen or sync the
project later.

Sync Cloud to Local
-------------------

``pull_ifcfed`` refreshes the cloud-sourced project without prompting the user.
It is available when the project has cloud resources: an adjacent
``.ifcfed.manifest`` for the project itself, one or more cloud-sourced models,
or both.

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "method": "pull_ifcfed",
       "params": {
           "connector": "mycompany",
           "version": "2",
           "url": "https://example.com/project.ifcfed"
       }
   }

The connector returns a local ``.ifcfed`` path and writes a fresh adjacent
manifest. Bonsai Viewer then continues by calling ``pull_models`` for
cloud-sourced models. The project-refresh phase and model-refresh phase are
independent. If no manifest exists, the project refresh phase is skipped and
Bonsai Viewer refreshes only cloud-sourced models.

If the returned ``.ifcfed`` is unchanged from the currently loaded file, Bonsai
Viewer may skip the fresh-session reload and continue to model refresh. How
"unchanged" is determined, such as byte equality, hash, or modified time, is
left to Bonsai Viewer.

Save Projects to Cloud
----------------------

``push_ifcfed_interactive`` is the cloud equivalent of Save As. It pushes an
``.ifcfed`` to a new user-selected cloud location.

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "method": "push_ifcfed_interactive",
       "params": { "path": "/tmp/path/to/project.ifcfed" }
   }

The connector uploads the file, writes an adjacent manifest, and returns the
resolved local path.

``push_ifcfed`` is the cloud equivalent of Save. It pushes back to the existing
cloud location described by the manifest.

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "method": "push_ifcfed",
       "params": {
           "path": "/tmp/path/to/project.ifcfed",
           "manifest": {
               "connector": "mycompany",
               "version": "2",
               "url": "https://example.com/project.ifcfed"
           }
       }
   }

The connector may update the manifest if the cloud platform returns a new
revision or version identifier.

Add and Save Models
-------------------

``pull_models_interactive`` lets the user choose one or more cloud models to
add to the current project.

.. code-block:: json

   { "jsonrpc": "2.0", "id": "0", "method": "pull_models_interactive" }

The connector returns model entries with ``display_name``, ``source``, a local
``path``, and optional metadata:

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "result": [
           {
               "display_name": "bar.ifc",
               "source": { "connector": "autodesk" },
               "path": "/path/to/model.ifc",
               "metadata": { "revision": "B", "date": "2nd Oct 2025" }
           }
       ]
   }

Bonsai Viewer stores ``display_name`` and ``source`` in the ``.ifcfed`` and
loads the model from ``path``. The path and metadata are not stored in the
``.ifcfed``.

``push_model_interactive`` is Save Model As to Cloud:

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "method": "push_model_interactive",
       "params": { "path": "/tmp/path/to/model.ifc" }
   }

``push_model`` saves a model back to the existing cloud location described by
the model's ``source``:

.. code-block:: json

   {
       "jsonrpc": "2.0",
       "id": "0",
       "method": "push_model",
       "params": {
           "path": "/tmp/path/to/model.ifc",
           "source": { "connector": "autodesk", "hub_id": "b.hub123" }
       }
   }

The connector returns an updated ``source`` and optional metadata. Bonsai
Viewer replaces the model's ``source`` in the ``.ifcfed``.

Conflict handling for non-interactive push methods is the connector's
responsibility. The connector may overwrite, prompt, reject with a JSON-RPC
error, or apply a platform-specific policy.

Settings and Errors
-------------------

A connector may implement ``open_settings`` for credentials, sign-out, default
folders, cache management, or other connector-specific settings.

.. code-block:: json

   { "jsonrpc": "2.0", "id": "0", "method": "open_settings" }

If a connector returns JSON-RPC ``Method not found`` with code ``-32601``,
Bonsai Viewer treats it as having no settings UI.

The settings result is currently always an empty object. Future revisions may
add optional fields, such as a refreshed display label for the connector.

The connector owns user-facing error handling. Bonsai Viewer understands only:

- per-item soft failure: ``null`` in a result array
- whole-call hard failure: a JSON-RPC error object

Diagnostic details should be written to standard error for logs.

Permissions
-----------

Permissions are entirely connector-managed. A federation may contain models
from multiple platforms, and some resources may fail while others succeed.
Bonsai Viewer tolerates partial failure and does not require all remote models
to resolve successfully.

Discovery
---------

A connector is shipped as a folder containing a ``connector.json`` manifest and
an executable entry point.

.. code-block:: text

   <connectors-dir>/
     autodesk/
       connector.json
       bonsaiviewer-autodesk
       ...

Example ``connector.json``:

.. code-block:: json

   {
       "id": "autodesk",
       "name": "Autodesk Forma",
       "version": "0.1.0",
       "exec": "./bonsaiviewer-autodesk"
   }

Fields:

- ``id`` is the stable identifier used in ``.ifcfed`` ``source.connector``
  fields and in ``.ifcfed.manifest`` files.
- ``name`` is the human-readable UI label.
- ``version`` is informational.
- ``exec`` is the connector executable. Relative paths are resolved against the
  connector folder. On Windows, Bonsai Viewer also tries ``<exec>.exe`` if the
  path does not exist as written.

Bonsai Viewer scans the ``connectors`` directory bundled alongside the
executable (``<application-dir>/connectors/``).

Every immediate subdirectory containing ``connector.json`` is treated as a
connector. Connectors are launched on demand, not at startup.

If two folders declare the same ``id``, the first one wins and the other is
skipped with a log warning. Malformed manifests or missing executables are
reported when relevant without preventing other connectors from loading.
