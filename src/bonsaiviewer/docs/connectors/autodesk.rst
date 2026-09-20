Autodesk Connector
==================

The Autodesk connector lets Bonsai Viewer open and save projects and models
hosted on Autodesk Forma, APS, and Docs.

Install
-------

The connector ships pre-built next to the Bonsai Viewer executable. There
should be nothing for users to install.

If you do want to manually install a specific version, extract the zip into the
``connectors`` directory beside the Bonsai Viewer executable:

Linux:

.. code-block:: bash

   unzip autodesk-linux-x86_64.zip -d <application-dir>/connectors/

macOS:

.. code-block:: bash

   unzip autodesk-macos-arm64.zip -d "<application-dir>/connectors/"

Windows PowerShell:

.. code-block:: powershell

   Expand-Archive autodesk-windows-x86_64.zip -DestinationPath "<application-dir>\connectors\"

Bonsai Viewer discovers the connector on next launch.

First-run setup
---------------

The first time you sign in, the connector needs an Autodesk APS client ID.
You provide one through the connector's settings dialog.

- **Client ID** — the APS application client ID you created in the Autodesk
  developer portal. Used as the OAuth audience.
- **OAuth callback port** — defaults to ``8080``. The OAuth callback host is
  always ``localhost``. Change this if ``8080`` is already in use on your
  machine.

When you sign in, the connector opens your default browser at the Autodesk
authorization page. After you approve, the redirect lands back at
``http://localhost:<port>/`` and the connector picks up the auth code, then
exchanges it for tokens via PKCE.

Where things are stored
-----------------------

The connector writes three things to disk: a small settings file, a cache
of resolved files, and OAuth tokens.

**Settings** (``settings.json``) — the client ID and OAuth port you set
above:

- Linux: ``~/.config/bonsaiviewer-autodesk/``
- macOS: ``~/Library/Application Support/bonsaiviewer-autodesk/``
- Windows: ``%APPDATA%\bonsaiviewer-autodesk\``

**Cache** — every file you pull from Autodesk lands here under a content-
hashed directory:

.. code-block:: text

   ~/.cache/bonsaiviewer-autodesk/                  (Linux)
   ~/Library/Caches/bonsaiviewer-autodesk/          (macOS)
   %LOCALAPPDATA%\bonsaiviewer-autodesk\Cache\      (Windows)
     ifcfeds/<hash>/<name>.ifcfed[.manifest]
     models/<hash>/<filename>

Each resolved file is the sole child in its directory so Bonsai Viewer can
write sidecar files (``.ifcview``, etc.) next to it without colliding. A
new version of a cloud model lands in a fresh ``models/<hash>/``
directory. Old cache directories can be deleted manually to reclaim disk
space; the connector will re-resolve them on next request.

**OAuth tokens** — stored in your OS keychain, keyed by client ID:

- Linux: Secret Service (gnome-keyring, KWallet, …)
- macOS: Keychain
- Windows: Credential Manager

To fully sign out, use the connector's settings dialog "Sign out" button.
Token removal can also be done from the keychain UI directly if needed.

Connecting through a proxy
--------------------------

The connector uses the host platform's native TLS trust store, so corporate
TLS-intercepting proxies that ship a custom CA work as long as that CA is
installed at the OS level. There is no ``cacerts.pem`` bundled inside the
connector that you would otherwise need to override.

HTTP/SOCKS proxy support is not exposed today. If you need to route through
a proxy, set ``HTTP_PROXY``/``HTTPS_PROXY`` in Bonsai Viewer's launch
environment and check ``ureq``'s upstream documentation for the supported
schemes.

Troubleshooting
---------------

**"Connector not found" on viewer launch.** Confirm the layout under
``<application-dir>/connectors/autodesk/``: it must contain
``connector.json`` and ``bonsaiviewer-autodesk[.exe]`` at the top level.
If you unzipped one level too deep you may have
``connectors/autodesk/autodesk/connector.json`` — flatten it.

**Sign-in browser tab loads, but the redirect never closes the loop.**
Check the OAuth callback port hasn't been changed under you (e.g. by
another local service binding ``8080``). Change the port in the settings
dialog and re-sign-in. Verify ``localhost`` resolves correctly — corporate
DNS occasionally rewrites it.

**Keychain prompt loop on Linux.** A Secret Service provider must be
running; gnome-keyring-daemon or KWallet. Headless servers without one of
those installed will fail token reads.

**Some pulls fail with HTTP 403.** Your APS client ID needs Autodesk Docs
and/or Forma scopes enabled on the developer portal. The connector requests
the union of scopes it knows about, but you must approve them on the
application side.

**Logs.** The connector writes diagnostic lines to its standard error
stream. Bonsai Viewer captures and surfaces these in the cloud-connector
status panel. The level of detail is fixed for now; structured logging is
a future improvement.
