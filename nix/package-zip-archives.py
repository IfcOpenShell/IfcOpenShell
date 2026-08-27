#!/usr/bin/env -S uv run --script
# /// script
# ///

import argparse
import logging
import os
import platform
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Literal, NamedTuple


class C:
    GREY = "\033[90m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: C.GREY,
        logging.WARNING: C.YELLOW,
        logging.ERROR: C.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, C.RESET)
        return f"{color}{super().format(record)}{C.RESET}"


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)


def run(
    *cmd: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    stderr: int | None = None,
) -> str:
    logger.debug(f"$ {shlex.join(cmd)}")
    return subprocess.check_output(cmd, cwd=cwd, env=env, stderr=stderr, text=True)


REPO_ROOT = Path(run("git", "-C", str(Path(__file__).parent), "rev-parse", "--show-toplevel").strip())
VERSION = "v" + (REPO_ROOT / "VERSION").read_text().strip()


def get_git_sha() -> str:
    sha = os.getenv("GITHUB_SHA") or run("git", "rev-parse", "HEAD", cwd=REPO_ROOT).strip()
    return sha[:7]


def is_platform(name: Literal["MAC", "LINUX"]) -> bool:
    current = "MAC" if platform.system() == "Darwin" else "LINUX"
    return current == name


def get_install_dir(arch_suffix: str) -> Path:
    if is_platform("MAC"):
        pattern = "Darwin/*/*/install"
    else:
        if "arm64" in arch_suffix:
            pattern = "Linux/aarch64/install"
        else:
            pattern = "Linux/x86_64/install"
    for data in (REPO_ROOT / "build").glob(pattern):
        return data
    raise Exception("No install dir found")


def find_qt_dir(install_root: Path, qt6_version: str) -> Path | None:
    for qt_candidate in install_root.glob(f"qt6-{qt6_version}-*/{qt6_version}/*"):
        if (qt_candidate / "lib").is_dir():
            return qt_candidate
    return None


def ensure_soname_links(dest: Path) -> None:
    """Ensure that all shared libraries in `dest` are present using their SONAMEs (at least as symlinks)."""
    for shared_object in dest.glob("*.so*"):
        if not shared_object.is_file():
            continue
        try:
            readelf_output = run("readelf", "-d", str(shared_object))
        except subprocess.CalledProcessError:
            continue
        match = re.search(r"\(SONAME\).*Library soname: \[(.*)\]", readelf_output)
        if not match:
            continue
        soname = match.group(1)
        soname_path = dest / soname
        if soname_path.exists():
            continue
        soname_path.symlink_to(shared_object.name)


def is_shared_library(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".so", ".dylib", ".dll")) or ".so." in name


def stage_runtime_payload(ifcopenshell_install_dir: Path, dest: Path, *, include_geometry_writers: bool = True) -> None:
    """Copy all libs from `ifcopenshell_install_dir/{bin,lib,lib64}` into `dest`."""
    for runtime_dir_name in ("bin", "lib", "lib64"):
        runtime_dir = ifcopenshell_install_dir / runtime_dir_name
        if not runtime_dir.is_dir():
            continue
        for runtime_file in runtime_dir.rglob("*"):
            if not (runtime_file.is_symlink() or runtime_file.is_file()):
                continue
            if not is_shared_library(runtime_file):
                continue
            if not include_geometry_writers and runtime_file.name.startswith("ifcopenshell.geometry.writer."):
                continue
            shutil.copy(runtime_file, dest / runtime_file.name, follow_symlinks=False)
    if not is_platform("MAC"):
        ensure_soname_links(dest)


def stage_qt_runtime_payload(exe_path: Path, dest: Path, qt_dir: Path | None) -> None:
    """Copy QT libs/plugins from `qt_dir` next to `exe_path`, if it depends on QT."""

    def is_so_file(path: Path) -> bool:
        return (path.is_file() or path.is_symlink()) and ".so" in path.name

    if not qt_dir or not (qt_dir / "lib").is_dir():
        return

    # Skip executables that don't depend on QT (don't have `libQt6` referenced).
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{qt_dir / 'lib'}:{env.get('LD_LIBRARY_PATH', '')}"
    try:
        ldd_output = run("ldd", str(exe_path), env=env)
    except subprocess.CalledProcessError:
        return
    if "libQt6" not in ldd_output:
        return

    # Copy all QT libs to `dest`.
    for lib_file in (qt_dir / "lib").iterdir():
        if is_so_file(lib_file):
            dest_file = dest / lib_file.name
            # Currently we install some qt libs to `install/ifcopenshell/lib` too,
            # so there's a bit of overlap beteen stage_runtime and stage_qt_runtime,
            # hence the skip.
            if dest_file.exists():
                continue
            shutil.copy(lib_file, dest_file, follow_symlinks=False)
    ensure_soname_links(dest)

    # Copy QT plugins.
    plugins_dir = qt_dir / "plugins"
    if plugins_dir.is_dir():
        for plugin_file in plugins_dir.rglob("*"):
            if not is_so_file(plugin_file):
                continue
            dest_plugin_file = dest / "plugins" / plugin_file.relative_to(plugins_dir)
            dest_plugin_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(plugin_file, dest_plugin_file, follow_symlinks=False)

        # Point plugins rpath to `dest`.
        dest_plugins_dir = dest / "plugins"
        if dest_plugins_dir.is_dir():
            for plugin_so in dest_plugins_dir.rglob("*.so*"):
                if plugin_so.is_file():
                    run("patchelf", "--set-rpath", "$ORIGIN/../..:$ORIGIN", str(plugin_so))

    # Non-recursive, set rpath only for top-level libs.
    for lib_so in dest.glob("*.so*"):
        if lib_so.is_file():
            run("patchelf", "--set-rpath", "$ORIGIN", str(lib_so))

    qt_conf_path = dest / "qt.conf"
    qt_conf_path.write_text("[Paths]\nPrefix = .\n")


def check_runtime_dependencies(package_dir: Path) -> None:
    """Check all binaries in `package_dir` and report if they're still missing dependencies or are static."""

    def is_executable_or_so(path: Path) -> bool:
        name = path.name
        return os.access(path, os.X_OK) or name.endswith(".so") or ".so." in name

    missing = False
    env = os.environ.copy()
    env.pop("LD_LIBRARY_PATH", None)

    for binary_file in package_dir.rglob("*"):
        if not binary_file.is_file() or not is_executable_or_so(binary_file):
            continue

        # Skip non-binaries.
        try:
            run("readelf", "-h", str(binary_file), stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            continue

        try:
            ldd_output = run("ldd", str(binary_file), env=env, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.error(f"ldd failed for {binary_file}")
            logger.error(e.output)
            missing = True
            continue

        if "not found" in ldd_output:
            logger.warning(f"Missing runtime dependencies for {binary_file}")
            for line in ldd_output.splitlines():
                if "not found" in line:
                    logger.warning(line)
            missing = True

    # TODO: should error?
    if missing:
        logger.warning("Runtime dependency check found issues; continuing packaging.")


def package_python_wrapper(
    py_dir: Path,
    ifcopenshell_install_dir: Path,
    github_sha: str,
    output_dir: Path,
    arch_suffix: str,
) -> None:
    logger.info(f"Packaging python wrapper '{py_dir.name}'")
    py_version = py_dir.name
    postfix = "" if py_version[-1].isdigit() else py_version[-1]
    # Match and convert `x.y` -> `xy`.
    version_match = re.search(r"[0-9]+\.[0-9]+", py_version)
    assert version_match
    numbers = "".join(version_match.group().split("."))
    py_version_major = f"python-{numbers}{postfix}"

    package_dir = ifcopenshell_install_dir / f".package-{py_version_major}"
    if package_dir.exists():
        # Clean up previous local runs.
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    ifcopenshell_dir = package_dir / "ifcopenshell"
    ifcopenshell_dir.mkdir()
    for item in py_dir.iterdir():
        dest = ifcopenshell_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, symlinks=True)
        else:
            shutil.copy(item, dest, follow_symlinks=False)

    # Cache from test run during build.
    pycache_dir = ifcopenshell_dir / "__pycache__"
    if pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)
    for pyc_file in ifcopenshell_dir.rglob("*.pyc"):
        pyc_file.unlink()

    # TODO: packs qt libs also?
    stage_runtime_payload(ifcopenshell_install_dir, ifcopenshell_dir)

    zip_path = output_dir / f"ifcopenshell-{py_version_major}-{VERSION}-{github_sha}-{arch_suffix}.zip"
    run("zip", "-y", "-r", "-qq", "-1", str(zip_path), "ifcopenshell", cwd=package_dir)
    shutil.rmtree(package_dir)


def is_packageable_executable(path: Path) -> bool:
    if not path.is_file() or not os.access(path, os.X_OK):
        return False
    return not (path.name.lower().endswith(".zip") or is_shared_library(path))


def package_executable(
    exe_path: Path,
    ifcopenshell_install_dir: Path,
    github_sha: str,
    output_dir: Path,
    autodesk_connector_dir: Path,
    qt_dir: Path | None,
    arch_suffix: str,
) -> None:
    exe = exe_path.name
    logger.info(f"Packaging executable '{exe}'")
    package_dir = ifcopenshell_install_dir / f".package-{exe}"
    if package_dir.exists():
        # Clean up previous local runs.
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    shutil.copy(exe_path, package_dir / exe)
    # TODO: kept `is_platform(MAC)` to retain original bash script behaviour,
    # but is this guard needed or it should be always False?
    stage_runtime_payload(ifcopenshell_install_dir, package_dir, include_geometry_writers=is_platform("MAC"))

    # On macOS, rpath is already set at build time via CMake's INSTALL_RPATH, and
    # QT apps are packaged as .app bundles (`package_app_bundle`) instead.
    if not is_platform("MAC"):
        run("patchelf", "--set-rpath", "$ORIGIN", str(package_dir / exe))
        stage_qt_runtime_payload(exe_path, package_dir, qt_dir)

        if exe == "BonsaiViewer":
            connectors_dir = package_dir / "connectors"
            connectors_dir.mkdir()
            shutil.copytree(autodesk_connector_dir, connectors_dir / autodesk_connector_dir.name, symlinks=True)

        check_runtime_dependencies(package_dir)

    zip_path = output_dir / f"{exe}-{VERSION}-{github_sha}-{arch_suffix}.zip"
    run("zip", "-y", "-qq", "-r", str(zip_path), ".", cwd=package_dir)
    shutil.rmtree(package_dir)


def package_app_bundle(
    app_path: Path,
    install_root: Path,
    github_sha: str,
    output_dir: Path,
    autodesk_connector_dir: Path,
    arch_suffix: str,
) -> None:
    """Zip a `.app` bundle (e.g. BonsaiViewer.app) living at the install-prefix root.

    Their install rule uses `BUNDLE DESTINATION "."` - that's the layout Qt's
    macdeployqt expects. macdeployqt has already embedded the Qt frameworks
    inside each bundle during install/strip, so the only thing left to stage
    is the connector.
    """
    app = app_path.stem
    logger.info(f"Packaging app bundle '{app}'")

    if app == "BonsaiViewer":
        # ConnectorDiscovery looks in applicationDirPath()/connectors,
        # which for a bundle is Contents/MacOS.
        connectors_dir = app_path / "Contents" / "MacOS" / "connectors"
        connectors_dir.mkdir(parents=True)
        shutil.copytree(autodesk_connector_dir, connectors_dir / autodesk_connector_dir.name, symlinks=True)

    zip_path = output_dir / f"{app}-{VERSION}-{github_sha}-{arch_suffix}.zip"
    run("zip", "-qq", "-r", str(zip_path), app_path.name, cwd=install_root)


ARCH_SUFFIXES = ("linux64", "linuxarm64", "macosm164")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class Args(NamedTuple):
    arch_suffix: str
    log_level: str


ARGS: Args


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("arch_suffix", choices=ARCH_SUFFIXES, help="Zip filename suffix.")
    # TODO: relax default to INFO once things get more stable.
    parser.add_argument("--log-level", default="DEBUG", choices=LOG_LEVELS, help="Logging verbosity.")
    args = parser.parse_args()

    global ARGS
    ARGS = Args(arch_suffix=args.arch_suffix, log_level=args.log_level)
    logger.setLevel(ARGS.log_level)

    # bonsaiviewer-autodesk is now a Rust connector. packaging/build.py
    # invokes `cargo build --release` and stages the binary +
    # connector.json into dist/autodesk/. Same on-disk shape as the
    # old PyInstaller flow so the symlink + zip steps below
    # continue to work unchanged.
    run("uv", "run", str(REPO_ROOT / "src/bonsaiviewer-autodesk/packaging/build.py"))
    autodesk_connector_dir = REPO_ROOT / "src/bonsaiviewer-autodesk/dist/autodesk"
    assert autodesk_connector_dir.is_dir()

    # Locate the ifcopenshell install dir and stage QT6 alongside the zip output.
    install_root = get_install_dir(ARGS.arch_suffix)
    ifcopenshell_install_dir = install_root / "ifcopenshell"

    output_dir = Path.home() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    qt6_version = os.getenv("QT6_VERSION", "6.8.3")
    qt_dir_env = os.getenv("QT_DIR")
    qt_dir = Path(qt_dir_env) if qt_dir_env else find_qt_dir(install_root, qt6_version)

    # Iterate over all built Python wrappers in `install/ifcopenshell/python-x.y.z`
    # and zip them, bundling all dynamic libs from `lib`.
    github_sha = get_git_sha()
    for py_dir in sorted(ifcopenshell_install_dir.glob("python-*")):
        package_python_wrapper(py_dir, ifcopenshell_install_dir, github_sha, output_dir, ARGS.arch_suffix)

    # Iterate over all executables in `install/ifcopenshell/bin` and zip them.
    # Each zip bundles dynamic libs from `lib` and also qt libs.
    bin_dir = ifcopenshell_install_dir / "bin"
    for exe_path in sorted(bin_dir.iterdir()):
        if is_packageable_executable(exe_path):
            package_executable(
                exe_path,
                ifcopenshell_install_dir,
                github_sha,
                output_dir,
                autodesk_connector_dir,
                qt_dir,
                ARGS.arch_suffix,
            )

    if is_platform("MAC"):
        for app_path in sorted(install_root.glob("*.app")):
            package_app_bundle(app_path, install_root, github_sha, output_dir, autodesk_connector_dir, ARGS.arch_suffix)


if __name__ == "__main__":
    main()
