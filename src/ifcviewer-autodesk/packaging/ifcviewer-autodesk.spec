# PyInstaller spec for the IfcViewer Autodesk connector (Tk + CustomTkinter).
#
# The connector talks JSON-RPC over stdio, so `console=True` is required to
# attach stdin/stdout on Windows. The IfcViewer is expected to spawn the
# connector with the OS's "hide console window" flag on Windows
# (CREATE_NO_WINDOW) so end users never see a console pop up.

from pathlib import Path

PROJECT_ROOT = Path(SPECPATH).resolve().parent

# keyring uses entry points for backends — PyInstaller can't trace them
# without hints. Bundle every backend; the right one is picked at runtime
# per OS.
HIDDEN_IMPORTS = [
    "keyring.backends.SecretService",
    "keyring.backends.macOS",
    "keyring.backends.Windows",
    "keyring.backends.fail",
    "keyring.backends.chainer",
]


a = Analysis(
    [str(PROJECT_ROOT / "ifcviewer_autodesk" / "__main__.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Test / docs.
        "test", "unittest", "pydoc_data",
        # Protocols / formats we never touch. (email, html, http.cookies and
        # http.cookiejar are required by http.server / httpx and must stay.)
        "xmlrpc", "sqlite3", "ftplib", "imaplib", "poplib", "nntplib",
        "smtplib", "telnetlib", "wsgiref",
        # Concurrency we never use (asyncio is needed by httpx → anyio).
        "multiprocessing", "concurrent.futures.process",
        # Build / packaging tools.
        "setuptools", "pip", "distutils", "ensurepip", "lib2to3",
        # Heavy stdlib bits with no callers.
        "decimal", "_decimal",
        # tkinter test modules.
        "tkinter.test", "test.test_tk",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ifcviewer-autodesk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ifcviewer-autodesk",
)
