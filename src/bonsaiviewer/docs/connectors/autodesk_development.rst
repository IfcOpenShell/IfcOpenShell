Autodesk Connector Development
==============================

This page describes building, testing, packaging, and protocol-level debugging
of the Autodesk connector for developers. For end-user install and
configuration see :doc:`autodesk`.

Tech stack
----------

The connector is a single Rust binary at ``src/bonsaiviewer-autodesk/`` in
the IfcOpenShell repository. Key crates:

- **fltk** (``fltk-bundled`` feature) — UI toolkit, statically linked at
  build time, so the produced executable has no system Tcl/Tk, Qt, or GTK
  dependency.
- **ureq** (``tls`` + ``native-certs``) — blocking HTTP client. The
  ``native-certs`` feature pulls the system trust store; no bundled CA file
  or OpenSSL runtime.
- **keyring** (``apple-native`` + ``windows-native`` +
  ``sync-secret-service``) — OS keychain abstraction for OAuth token
  storage.
- **dirs** — platform-specific config / cache / data directories.
- **serde** / ``serde_json`` — JSON-RPC framing and APS response parsing.
- **chrono** — token-expiry math.
- **webbrowser** — opens the system default browser for the OAuth redirect.

Build from source
-----------------

From the repository root:

.. code-block:: bash

   cd src/bonsaiviewer-autodesk
   cargo build --release

The binary lands at ``target/release/bonsaiviewer-autodesk``.

A debug build (``cargo build``) at ``target/debug/bonsaiviewer-autodesk``
is fine for iterating on UI or RPC logic; release-mode strip + LTO is what
the packaging script ships.

Run
---

.. code-block:: bash

   ./target/release/bonsaiviewer-autodesk

The connector launches without configuration. The first interaction should
be to open the settings dialog (either from Bonsai Viewer or via the
``open_settings`` JSON-RPC method below) and configure the APS client ID +
OAuth callback port.

Bonsai Viewer is expected to launch this binary once per session and keep
it alive until shutdown. Closing the connector's standard input triggers a
clean exit.

Test and lint
-------------

The Rust source tree ships unit tests, integration tests under ``tests/``,
and clippy-clean lints. From the connector directory:

.. code-block:: bash

   cargo test --all-features
   cargo clippy --all-targets --all-features -- -D warnings
   cargo fmt --all -- --check

CI runs the same three commands in
``.github/workflows/build-bonsaiviewer-autodesk.yml``.

Protocol probing
----------------

The connector speaks newline-delimited JSON-RPC 2.0 over stdio. For
debugging without Bonsai Viewer in the loop, pipe requests in directly:

.. code-block:: bash

   ./target/release/bonsaiviewer-autodesk <<'EOF'
   {"jsonrpc":"2.0","id":"0","method":"open_settings"}
   {"jsonrpc":"2.0","id":"1","method":"pull_ifcfed_interactive"}
   EOF

Useful methods at a glance:

.. code-block:: json

   {"jsonrpc":"2.0","id":"0","method":"open_settings"}
   {"jsonrpc":"2.0","id":"1","method":"pull_ifcfed_interactive"}
   {"jsonrpc":"2.0","id":"2","method":"pull_models","params":[{"display_name":"foo.ifc","id":"abc","source":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk...","version_id":"latest"}}]}
   {"jsonrpc":"2.0","id":"3","method":"push_ifcfed_interactive","params":{"path":"/tmp/project.ifcfed"}}
   {"jsonrpc":"2.0","id":"4","method":"push_ifcfed","params":{"path":"/tmp/project.ifcfed","manifest":{"connector":"autodesk","hub_id":"b.hub","project_id":"b.proj","item_id":"urn:adsk..."}}}

The cross-connector wire format is defined in :doc:`cloud_sync_protocol`.

Packaging
---------

The connector ships as a folder dropped into the Bonsai Viewer connectors
directory. The folder contains a single statically linked Rust executable
and a JSON manifest — no runtime interpreter, no vendored libraries
directory.

Cargo does not cross-compile out of the box (FLTK in particular wants the
host toolchain), so each operating system and architecture builds its own
package, typically through a CI matrix.

**Output:**

.. code-block:: text

   dist/
     autodesk/
       connector.json
       bonsaiviewer-autodesk[.exe]
     autodesk-<os>-<arch>.zip

The ``autodesk/`` folder is what Bonsai Viewer expects under the
``connectors`` directory bundled next to the viewer executable
(``<application-dir>/connectors/``).

**Build:**

.. code-block:: bash

   cd src/bonsaiviewer-autodesk
   python packaging/build.py

``packaging/build.py`` uses only the Python standard library — no
``pip install`` step — and is a thin wrapper around ``cargo``. It:

1. cleans ``dist/``
2. runs ``cargo build --release``
3. copies ``connector.json`` and the produced binary into ``dist/autodesk/``
4. zips the folder as ``dist/autodesk-<os>-<arch>.zip``

Platform notes
~~~~~~~~~~~~~~

**Linux.** Build on the oldest glibc you intend to support — binaries
built on a newer glibc will not run on older distributions. Ubuntu 22.04
LTS (glibc 2.35) is a reasonable lowest common denominator in 2026. The
runtime keyring backend is Secret Service via the ``keyring`` crate's
``sync-secret-service`` feature (gnome-keyring, KWallet, …). End users
need a Secret Service provider running.

Expected output: ``autodesk-linux-x86_64.zip`` and/or an ARM64 archive.

**macOS.** Each architecture builds separately. To support Apple Silicon
and Intel, build on each architecture and ship two zips, or post-process
with ``lipo`` to produce universal binaries. The runtime keyring backend
is the system Keychain (``keyring`` crate's ``apple-native`` feature). For
distribution outside the developer's machine, codesign the executable and
notarize the bundle — unsigned binaries trigger Gatekeeper warnings.
Codesigning is left to the caller.

Expected output: ``autodesk-macos-arm64.zip`` and/or
``autodesk-macos-x86_64.zip``.

**Windows.** Build with the MSVC toolchain (Rustup default
``-x86_64-pc-windows-msvc`` target). The runtime keyring backend is
Credential Manager (``keyring`` crate's ``windows-native`` feature).

The Rust executable defaults to the Windows console subsystem, which is
appropriate because the connector speaks JSON-RPC over stdio. Bonsai
Viewer must launch it without showing a console window, for example with
Qt's ``QProcess::setCreateProcessArgumentsModifier`` and
``CREATE_NO_WINDOW``.

For distribution, sign the executable with an Authenticode certificate to
avoid SmartScreen warnings. Signing is left to the caller.

Expected output: ``autodesk-windows-x86_64.zip``.

CI
--

``.github/workflows/build-bonsaiviewer-autodesk.yml`` runs ``cargo fmt
--check``, ``cargo clippy -- -D warnings``, and
``cargo test --all-features``, then matrix-builds the four shipping
packages (Linux x86_64, macOS arm64, macOS x86_64, Windows x86_64) and
uploads each ``autodesk-<os>-<arch>.zip`` as an artefact.
