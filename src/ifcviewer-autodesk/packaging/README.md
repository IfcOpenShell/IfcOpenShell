# Packaging the Autodesk connector

The connector is shipped as a self-contained folder ready to drop into the
IfcViewer connectors directory. PyInstaller bundles the Python interpreter,
Qt, and all dependencies so end users do not need Python installed.

PyInstaller does **not** cross-compile. Each OS must build on itself —
typically via a CI matrix.

## Output

```
dist/
  autodesk/                          # the connector folder, ready to install
    connector.json
    ifcviewer-autodesk[.exe]
    _internal/...                    # PyInstaller dependencies (Qt, Python, …)
  autodesk-<os>-<arch>.zip           # the distribution archive
```

The folder is what the IfcViewer expects under
`~/.local/share/IfcOpenShell/IfcViewer/connectors/` (or the OS equivalent).

## Build steps (any OS)

```bash
cd src/ifcviewer-autodesk
python -m venv venv
venv/bin/activate          # or venv\Scripts\activate on Windows
pip install -e ".[build]"
python packaging/build.py
```

The build:

1. cleans `dist/` and `build/`
2. runs PyInstaller against `packaging/ifcviewer-autodesk.spec`
3. renames the produced folder to `autodesk/` and copies `connector.json` into it
4. zips the folder as `autodesk-<os>-<arch>.zip`

The UI is Tcl/Tk via CustomTkinter, which keeps the bundle small. Expect
~50 MB unpacked / ~21 MB zipped per OS. The Python used to run the build
must include `tkinter` — most distribution and python-build-standalone
builds do; on Gentoo make sure `USE="tk"` is set for `dev-lang/python`.

## Per-OS notes

### Linux

- Build on the **oldest glibc** you intend to support. Binaries built on a
  newer glibc will not run on older distributions. Ubuntu 22.04 LTS
  (glibc 2.35) is a reasonable lowest common denominator in 2026.
- The keyring backend used at runtime is `SecretService` (gnome-keyring or
  KWallet); end users need a Secret Service provider running.
- Output: `autodesk-linux-x86_64.zip` (and/or `arm64`).

### macOS

- Each architecture builds separately. To support both Apple Silicon and
  Intel, build on each and ship two zips, or post-process with `lipo` to
  produce universal binaries.
- The keyring backend is the system Keychain.
- For distribution outside the developer's machine you will need to
  **codesign** the executable and Tcl/Tk dylibs, and notarize the bundle.
  Unsigned binaries trigger Gatekeeper warnings. Codesigning is left to the
  caller; the spec's `codesign_identity` field can be wired up.
- Output: `autodesk-macos-arm64.zip` and/or `autodesk-macos-x86_64.zip`.

### Windows

- Build with the Microsoft Visual C++ runtime available (usually present in
  any modern Python distribution).
- The keyring backend is Credential Manager.
- The `.exe` is built with `console=True` because the connector speaks
  JSON-RPC over stdio. The IfcViewer must launch the connector with
  `CREATE_NO_WINDOW` (Qt: `QProcess::setCreateProcessArgumentsModifier`) so
  end users never see a console window flicker.
- For distribution: sign the `.exe` with an Authenticode certificate to
  avoid SmartScreen warnings. Signing is left to the caller.
- Output: `autodesk-windows-x86_64.zip`.

## Installing a built connector

```bash
# Linux
unzip dist/autodesk-linux-x86_64.zip -d ~/.local/share/IfcOpenShell/IfcViewer/connectors/

# macOS
unzip dist/autodesk-macos-arm64.zip -d "~/Library/Application Support/IfcOpenShell/IfcViewer/connectors/"

# Windows (PowerShell)
Expand-Archive dist\autodesk-windows-x86_64.zip -DestinationPath "$env:APPDATA\IfcOpenShell\IfcViewer\connectors\"
```

The IfcViewer picks up the connector on next launch.

## Out of scope here

- Signing / notarization (caller's responsibility per OS)
- CI matrix (project-level concern)
- Auto-update (the IfcViewer or the host installer handles this)
- Universal macOS binaries via `lipo` (post-process step, not part of `build.py`)
