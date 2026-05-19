# IfcViewer cloud connectors

IfcViewer will have the capability to load and save projects and models from a
cloud platform. Later on, there will be other resources stored on cloud
platforms too, such as issues, clash results, and so on, but this behaviour is
not currently designed.

Due to the variety of cloud platforms, the IfcViewer itself will depend on
a "connector" to integrate with each platform. The connector is a separate
application which will communicate to and from the IfcViewer.

The following types of resources may be managed with a connector:

 - Projects (.ifcfed)
 - Models (.ifc, .rdb, .ifcview, .rdbview)
 - Issues (.bcf, not yet supported nor defined)
 - Specifications (.ids, not yet supported nor defined)

## Communication protocol

The IfcViewer launches one connector process per session, on first use, and
keeps it alive for the duration of the session. This allows the connector to
maintain authentication tokens, browse state, in-flight downloads, and caches
in memory across calls without re-authenticating on every request.

Communication is over stdio using newline-delimited JSON-RPC 2.0:

 - Requests and responses are single-line JSON objects on the connector's
   stdin/stdout. Each message is terminated by a single `\n`.
 - The connector must not emit literal newlines inside a JSON message.
 - The connector may write arbitrary diagnostic output to stderr; the IfcViewer
   will not parse it.

The IfcViewer shuts a connector down by closing its stdin. The connector should
exit cleanly. If it does not exit within a few seconds, the IfcViewer will
terminate it.

## Connector scope

The IfcViewer has minimal knowledge about connectors. IfcViewer only knows how
to work with local files. If it detects that a project or model is not local,
it will invoke a connector. The connector's job is to resolve the IfcViewer's
request back into a local file and cloud metadata. The connector must not
modify the file in any way.

A connector will handle anything necessary for the cloud platform (or arbitrary
data source). This includes authentication, browsing files, filters and
searches, selecting or pinning revisions, progress bars, cache,
platform-specific requirements, etc. The connector may or may not display a UI.
This makes connectors very flexible.

A single project may have different resources coming from different connectors.
For example, some models might be on one platform, and some projects hosted on
another platform. The permissions regarding model access can be quite granular
and therefore managed by the platform, and not IfcViewer.

When a connector returns a local file, that file is required to be the sole
child in its directory. This is because there may be adjacent temporary files,
viewer-generated sidecar files, database locks or helpers (e.g. SQLite WAL), or
where filenames are significant (and cannot be renamed to prevent collisions),
or are actually directories containing other files.

The connector is expected to persist this cache until explicitly cleared by a
user, because it will be used directly as a local path by the viewer. If a
connector invalidates a cache, it can simply delete the entire directory. If a
connector resolves to a new version of the file, it can create a fresh
directory (thus all sidecar artefacts will be regenerated if needed). It is not
prescribed how a connector manages cache.

## Resource: Projects

A project is defined using an `.ifcfed` file. The file stores settings (such as
units, home view coordinates, saved searches, etc) and models.

For example:

```json
# project.ifcfed
{
    "created": "2026-04-29T21:22:36Z",
    "modified": "2026-04-29T21:22:36Z",
    "home_view": null,
    "models": ... # see Resources: Models,
    ...
}
```

A project may have a manifest file (with `.manifest` as a suffix), which may
store metadata that a ifcfed was retrieved from a cloud source.

```json
# project.ifcfed.manifest
{
    "connector": "mycompany",
    # Arbitrary connector-specific data
    "version": "2",
    "url": "http://example.com/project.ifcfed",
}
```

## Resource: Models

The list of models is defined in the .ifcfed. Each model may either point to a
local file (via the special "local" connector), or to a cloud file.

Cloud connections may store arbitrary source data as keys. For example, they
might store a revision policy that determines whether the model is pinned to a
particular revision or must always be the latest. This is completely up to the
connector.

Here is an example of how models might be stored in an .ifcfed:

```json
[
    {
        "display_name": "foo.ifc",
        "id": "0503642e-e2f6-4700-87fd-16479542e801",
        "source": {
            "connector": "local",
            "path": "path/to/foo.ifc" # Only for local
        },
    },
    {
        "display_name": "bar.ifc",
        "id": "5fc69e6a-1ff0-4d8a-82c6-2215df53d2ed",
        "source": {
            "connector": "autodesk",
            # Below is arbitrary data depending on the connector
            "version": "1",
            "hub_id": "b.hub123",
            "project_id": "b.project456",
            "item_id": "urn:adsk.wipprod:dm.lineage:abc",
            "version_id": "urn:adsk.wipprod:fs.file:vf.xyz?version=3"
        },
    },
]
```

Note that cloud metadata (filename, cloud ID, revision, date modified, etc) is
not specified nor stored in the .ifcfed. This is to be returned by the
connector when requested.

The IfcViewer will display all returned cloud metadata as simple text strings.
However some keys are treated specially and shown in more places in the
IfcViewer UI for convenience:

 - author
 - revision
 - date

## Open from cloud workflow

This opens a .ifcfed from a cloud platform and constitutes a fresh session.
Note that downloading the latest versions of all models immediately upon open
is not required. At a minimum, only the .ifcfed needs to be opened. It is
perfectly acceptable to give the user choice on whether to download all or some
models, or use cache (even if outdated). The user can always reopen the project
later.

 1. The user presses a button in the IfcViewer UI that says "Open from Cloud"
 2. The user chooses a connector.
 3. The `pull_ifcfed_interactive` method is sent to the connector.
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "pull_ifcfed_interactive" }
    ```
 4. The connector:
    - (Does optional workflow) authenticates, browses projects, filters files, etc
    - The user selects an .ifcfed file from the connector's UI
    - Downloads (or retrieves from cache) the cloud .ifcfed into a connector managed directory
    - The connector returns a path to the .ifcfed. The connector must also create an adjacent .ifcfed.manifest file:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": { "path": "/path/to/project/file.ifcfed" } }
    ```
 5. The IfcViewer loads the `path`. This constitutes a fresh session.
 6. The IfcViewer calls `pull_models`:
    ```json
    { "jsonrpc": "2.0", "id": "1", "method": "pull_models", "params": [
        { "display_name": ..., "id": ..., "source": ..., },
        { "display_name": ..., "id": ..., "source": ..., },
        ...
    ] }
    ```
 7. The connector handles downloading files. It may always check and download the latest version of the file, or be designed to pin to a particular revision, or give the user the option of not downloading a file, etc. or retrieves from its own cache, and returns a path.
    ```json
    { "jsonrpc": "2.0", "id": "1", "result": [
        { "path": "/path/to/foo.ifc" },
        {
            "path": "/path/to/model.ifc", # Used to load the model in IfcViewer
            "metadata": { "revision": "B", "date": "2nd Oct 2025" ...  }, # Optional, used to display stats
        },
        null, # If skipped, error, etc
        { "path": "/path/to/bar.ifc" },
        ...
    ] }
    ```
 8. The IfcViewer may call another connector with more models to be downloaded.
 9. The IfcViewer will load the downloaded models as regular files. Typically this will also result in the IfcViewer reading / writing a cache (e.g. .ifcview) alongside this file, but it is not expected that the connector will know or care about this.

## Sync cloud to local

This refreshes cloud-sourced resources in the currently-open project to their
latest cloud revisions, without prompting the user. It is available whenever
the project has any cloud resources: a `.ifcfed.manifest` adjacent to the
.ifcfed, or one or more models whose `source.connector` is not `local`. The
.ifcfed-refresh phase and the model-refresh phase are independent — only the
first requires a manifest.

 1. The user presses a button in the IfcViewer UI that says "Sync Cloud to Local"
 2. IfcViewer reads the .ifcfed.manifest and invokes the relevant connector with the manifest data with the `pull_ifcfed` method:
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "pull_ifcfed", "params": {
        "connector": "mycompany", "version": "2", "url": ...
    } }
    ```
 3. The connector does what it needs:
    - Authenticates (optional)
    - (Typically without user interaction) finds the .ifcfed on the cloud platform using the ifcfed manifest
    - Downloads (or retrieves from cache) the cloud .ifcfed into a connector managed directory
    - The connector returns a path to the .ifcfed. The connector must also create an adjacent .ifcfed.manifest file:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": { "path": "/path/to/project/file.ifcfed" } }
    ```
 4. Continue with step 5 of the "Open from cloud" workflow.

If no `.ifcfed.manifest` is present, steps 2–4 are skipped. The .ifcfed on
disk is used as-is, and the IfcViewer continues from step 6 of the
"Open from cloud" workflow (calling `pull_models` for any cloud-sourced models
referenced in the .ifcfed).

Additionally, if the .ifcfed returned in step 3 is unchanged from the one
already loaded (e.g. the connector served a cached copy because the cloud
revision matched), the IfcViewer skips step 5 as well and continues from
step 6, preserving the current session rather than forcing an unnecessary
fresh one. How "unchanged" is determined (byte equality, hash, mtime, etc.)
is left to the IfcViewer.

## Save as to cloud

This pushes a .ifcfed to a fresh location on a cloud platform, chosen by the
user. It is the "Save As" equivalent and is the only way to first establish a
cloud location for a project that does not yet have a `.ifcfed.manifest`.

 1. The user presses a button in the IfcViewer UI that says "Save As to Cloud"
 2. The user chooses a connector.
 3. The `push_ifcfed_interactive` method is called with the path to the .ifcfed. The connector should treat this as a temporary .ifcfed file, as the real project may or may not be actually saved on disk.
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "push_ifcfed_interactive", "params": { "path": "/tmp/path/to/project.ifcfed" } }
    ```
 4. The connector does what it needs:
    - (Does optional workflow) authenticates, browses projects, filters files, etc
    - Selects existing or writes a new name for an .ifcfed file
    - Uploads .ifcfed file to the cloud platform
    - The connector returns a path to the .ifcfed. The connector must also create an adjacent .ifcfed.manifest file:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": { "path": "/path/to/project/file.ifcfed" } }
    ```
 5. The IfcViewer "repoints" to the returned path. It is not necessary to do a full reload as no "changes" are made.

## Save to cloud

This pushes a .ifcfed back to the cloud location it originally came from,
without prompting the user. It is the "Save" equivalent and is only available
when there is a `.ifcfed.manifest` adjacent to the project.

 1. The user presses a button in the IfcViewer UI that says "Save to Cloud"
 2. IfcViewer reads the .ifcfed.manifest and invokes the relevant connector with the `push_ifcfed` method, passing both the local path and the manifest data:
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "push_ifcfed", "params": {
        "path": "/tmp/path/to/project.ifcfed",
        "manifest": { "connector": "mycompany", "version": "2", "url": "..." }
    } }
    ```
 3. The connector does what it needs:
    - Authenticates (optional)
    - (Typically without user interaction) locates the existing .ifcfed on the cloud platform using the manifest data
    - Uploads the .ifcfed, overwriting or creating a new revision as the platform dictates
    - The connector returns a path to the .ifcfed and rewrites the adjacent .ifcfed.manifest if any of its fields have changed (e.g. a new version number):
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": { "path": "/path/to/project/file.ifcfed" } }
    ```
 4. The IfcViewer "repoints" to the returned path. It is not necessary to do a full reload as no "changes" are made.

Conflict resolution for non-interactive push methods (the cloud copy moved on
since the manifest or source was captured, the user lacks write permission,
revision-pinning policies, etc.) is entirely the connector's responsibility.
The connector may silently overwrite, prompt the user, refuse with a JSON-RPC
error, or anything in between. The IfcViewer expresses no opinion. This rule
also applies to `push_model` below.

## Add model from cloud

 1. The user presses a button in the IfcViewer UI that says "Add model from cloud"
 2. The user chooses a connector.
 3. The `pull_models_interactive` method is sent to the connector.
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "pull_models_interactive" }
    ```
 4. The connector does what it needs:
    - (Does optional workflow) authenticates, browses projects, filters files, etc
    - Selects a model (.ifc, .ifcview, .rdbview, .rdb, etc)
    - Downloads (or retrieves from cache) the model into a connector managed directory
    - The connector returns a successful result:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": [
        {
            "display_name": "bar.ifc", # Stored in .ifcfed
            "source": { "connector": "autodesk", ...  }, # Stored in .ifcfed
            "path": "/path/to/model.ifc", # Used to load the model in IfcViewer
            "metadata": { "revision": "B", "date": "2nd Oct 2025" ...  }, # Optional, used to display stats
        },
        { ... },
        ...
    ] }
    ```
 5. The IfcViewer updates the .ifcfed models section with new models using the
    "source" and "display\_name" from the provided data. The models are
    immediately loaded from the "path", and the IfcViewer stores the "metadata"
    for display. The path and metadata is never stored in the .ifcfed.

## Save model as to cloud

This pushes a model to a fresh location on a cloud platform, chosen by the
user. It is the "Save As" equivalent and is the only way to first establish a
cloud `source` for a model whose current source is `local`.

 1. The user presses a button in the IfcViewer UI that says "Save Model As to Cloud"
 2. The user chooses a connector.
 3. The `push_model_interactive` method is sent to the connector with a path to the model to be uploaded (typically a file, but RocksDB databases can be a folder).
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "push_model_interactive", "params": { "path": "/tmp/path/to/model.ifc" } }
    ```
 4. The connector does what it needs:
    - (Does optional workflow) authenticates, browses projects, filters files, etc
    - Selects existing or types a new name for the model
    - Uploads the model (only the file in params, though the connector is free to do optional additional work) to the cloud platform
    - The connector returns a successful result:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": {
        "display_name": "bar.ifc", # Stored in .ifcfed
        "path": "/path/to/model.ifc",
        "source": { "connector": "autodesk", ...  }, # Stored in .ifcfed
        "metadata": { "revision": "B", "date": "2nd Oct 2025" ...  }, # Optional, used to display stats
    } }
    ```
 5. The IfcViewer updates the .ifcfed models section with the new model metadata from the provided data.

## Save model to cloud

This pushes a model back to the cloud location it originally came from,
without prompting the user. It is the "Save" equivalent and is only available
for models whose .ifcfed `source` already points at a cloud connector (i.e.
anything other than `local`).

 1. The user presses a button in the IfcViewer UI that says "Save Model to Cloud"
 2. IfcViewer invokes the connector named in the model's `source` with the `push_model` method, passing both the local path and the existing `source` object verbatim:
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "push_model", "params": {
        "path": "/tmp/path/to/model.ifc",
        "source": { "connector": "autodesk", "hub_id": "b.hub123", "item_id": "...", ... }
    } }
    ```
 3. The connector does what it needs:
    - Authenticates (optional)
    - (Typically without user interaction) locates the existing model on the cloud platform using the `source` data
    - Uploads the model, overwriting or creating a new revision as the platform dictates
    - The connector returns a successful result. The returned `source` reflects the just-uploaded revision (e.g. a new `version_id`) and replaces the existing one in the .ifcfed; `display_name` is omitted (the existing one is retained):
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": {
        "source": { "connector": "autodesk", ...  }, # Replaces existing source in .ifcfed
        "metadata": { "revision": "C", "date": "19th May 2026" ...  }, # Optional, used to display stats
    } }
    ```
 4. The IfcViewer replaces the model's `source` in the .ifcfed and refreshes the stored metadata for display.

## Connector settings (optional)

A connector MAY implement an `open_settings` method that the IfcViewer invokes
when the user clicks the connector's settings entry (e.g. a gear icon next to
the connector name). The connector is responsible for the entire settings UI:
credentials, sign-out, default folders, anything connector-specific.

 1. The user clicks the connector's settings entry in the IfcViewer UI.
 2. The IfcViewer sends `open_settings`:
    ```json
    { "jsonrpc": "2.0", "id": "0", "method": "open_settings" }
    ```
 3. The connector shows its own settings dialog. When the user closes it, the
    connector returns:
    ```json
    { "jsonrpc": "2.0", "id": "0", "result": {} }
    ```

If the connector returns a JSON-RPC `Method not found` error (code `-32601`),
the IfcViewer should treat that connector as having no settings and hide its
settings entry. There is no other discovery mechanism — the viewer probes by
calling the method when needed.

The connector is free to use this method for things like:

 - Signing in / signing out
 - Setting API keys, client ids, or other credentials
 - Choosing default upload folders or revision policies
 - Clearing the connector's cache

The result object is currently always empty (`{}`); future revisions may add
optional fields (for example a fresh display label for the connector).

### Error Response

The connector owns all user-facing error handling: dialogs, retry prompts,
re-auth flows, logs. The IfcViewer does not interpret or display connector
errors directly.

The protocol expresses only two outcomes:

 - **Per-item soft failure** (one model in a batch failed, others succeeded):
   the connector returns `null` in that slot of the result array. The IfcViewer
   skips it and continues.
 - **Whole-call hard failure** (the connector cannot service the request at
   all): the connector returns a JSON-RPC error object. The IfcViewer aborts
   the operation. The `error.message` may be logged by the IfcViewer for
   diagnostics, but is not shown to the user — the connector is expected to
   have already surfaced the problem in its own UI.

Diagnostic detail (stack traces, codes, retry context) should be written to
stderr, which the IfcViewer captures for logs.

## Permissions

Permissions are completely managed by the connector. For example:

- one Autodesk model resolves successfully
- one Aconex model fails with access denied
- one Dropbox model resolves successfully

The viewer will tolerate partial failure and report skipped resources that the connector cannot resolve. A federation does not need to become all-or-nothing just because some remote models are permission-restricted.

## Connector discovery

A connector is shipped as a folder containing a `connector.json` manifest and
an executable entry point. The IfcViewer discovers connectors by scanning a
small, fixed set of locations for these folders.

### Connector bundle layout

```
<some-connectors-dir>/
  autodesk/                     # folder name is arbitrary; id comes from connector.json
    connector.json              # required, at the folder root
    ifcviewer-autodesk          # the executable (or a wrapper script)
    ...                         # anything else the connector ships
```

### `connector.json`

```json
{
  "id": "autodesk",
  "name": "Autodesk Forma",
  "version": "0.1.0",
  "exec": "./ifcviewer-autodesk"
}
```

 - `id` — stable identifier used in `.ifcfed` `source.connector` fields and in
   `.ifcfed.manifest`. Must be unique across all discovered connectors.
 - `name` — human-readable label shown in the IfcViewer UI.
 - `version` — connector version string; informational only.
 - `exec` — path to the connector executable. Relative paths are resolved
   against the connector folder; absolute paths are used as-is. Bundled
   connectors should use a relative path so the bundle is self-contained.

   On Windows, the IfcViewer will also try `<exec>.exe` if `<exec>` does not
   exist as written.

### Search locations

The IfcViewer scans the **user connectors directory**. The platform's per-user
application data location:

 - Linux: `~/.local/share/IfcOpenShell/IfcViewer/connectors/`
 - macOS: `~/Library/Application Support/IfcOpenShell/IfcViewer/connectors/`
 - Windows: `%APPDATA%\IfcOpenShell\IfcViewer\connectors\`

The IfcViewer looks at every immediate subdirectory and treats it as a
connector iff it contains a `connector.json`. Connectors are launched on
demand when the user invokes a cloud workflow, not at startup.

### Conflicts and errors

 - If two folders declare the same `id`, the one found earlier in directory
   order wins; the loser is skipped and a warning is written to the IfcViewer's
   log.
 - A `connector.json` that is missing, unreadable, malformed, or missing
   required fields causes that folder to be skipped (with a log entry); other
   connectors are unaffected.
 - A connector whose `exec` cannot be resolved or launched is reported to the
   user only when the user actually tries to invoke it.
