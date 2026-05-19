# `bonsaiviewer-autodesk`

Autodesk Forma (APS / Docs) connector for Bonsai Viewer.

Implements the JSON-RPC connector contract defined in
[`CLOUD_SYNC_PROTOCOL.md`](CLOUD_SYNC_PROTOCOL.md). The connector is a separate
process the viewer launches and speaks to over stdio.

UI is built on **CustomTkinter** (Tcl/Tk under the hood), keeping the
packaged connector around 50 MB unpacked / 21 MB zipped on Linux. The Python
running this code must include `tkinter` (most distribution Python builds do;
on Gentoo make sure `USE="tk"` is set for `dev-lang/python`).

## Install

```bash
cd src/bonsaiviewer-autodesk
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Run

```bash
bonsaiviewer-autodesk
```

The connector launches without any configuration; on first run, invoke
`open_settings` (or, equivalently, set the `APS_CLIENT_ID` env var) to
configure the Autodesk client id.

Then send newline-delimited JSON-RPC 2.0 requests on `stdin`. Examples:

```json
{"jsonrpc":"2.0","id":"0","method":"open_settings"}
{"jsonrpc":"2.0","id":"1","method":"pull_ifcfed_interactive"}
{"jsonrpc":"2.0","id":"2","method":"pull_models","params":[{"display_name":"foo.ifc","id":"abc","source":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk...","version_id":"latest"}}]}
{"jsonrpc":"2.0","id":"3","method":"push_ifcfed_interactive","params":{"path":"/tmp/project.ifcfed"}}
{"jsonrpc":"2.0","id":"4","method":"push_ifcfed","params":{"path":"/tmp/project.ifcfed","manifest":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk..."}}}
```

The viewer is expected to launch this binary once per session and keep it alive
until shutdown; closing the connector's `stdin` triggers a clean exit.

### Configuration

The connector reads the Autodesk client id from two places, in order:

1. The `APS_CLIENT_ID` environment variable (takes precedence — useful for dev
   overrides).
2. `<config dir>/settings.json` (persisted via the settings dialog).

The config directory is platform-specific:

- Linux: `~/.config/bonsaiviewer-autodesk/`
- macOS: `~/Library/Application Support/bonsaiviewer-autodesk/`
- Windows: `%APPDATA%\bonsaiviewer-autodesk\`

OAuth tokens are stored in the OS keychain (Secret Service on Linux, Keychain
on macOS, Credential Manager on Windows), keyed by the client id, so changing
the client id starts a fresh session.

## Cache

The connector owns its own cache. Resolved files live under (Linux):

```
~/.cache/bonsaiviewer-autodesk/
  ifcfeds/<hash>/<name>.ifcfed[.manifest]
  models/<hash>/<filename>
```

Each file is the sole child in its directory so the viewer can write sidecar
files (e.g. `.ifcview`) next to it without colliding. A new resolved version of
a model lands in a fresh `models/<hash>/` directory; the old directory may be
removed manually to clear space.

## Status

What is implemented:

- Strict JSON-RPC 2.0 host over stdio
- APS PKCE sign-in with keyring-backed token store
- Hub / project / folder browsing (Qt UI)
- `pull_ifcfed_interactive`, `pull_ifcfed`, `pull_models`, `pull_models_interactive`
- `push_ifcfed_interactive`, `push_ifcfed`, `push_model_interactive`, `push_model`
- `open_settings` — edit the client id, sign out
- Connector-managed cache with sole-child invariant
- Adjacent `.ifcfed.manifest` written/read alongside `.ifcfed` files

What is intentionally not implemented:

- JSON-RPC notifications for progress streaming (the connector shows its own
  progress dialog instead, per spec)
- Cancellation of in-flight downloads
- Subdirectory upload layouts inside push destinations (one flat file at a time)
