#!/usr/bin/env -S uv run --script
# /// script
# [tool.ty.environment]
# root = ["."]
# ///

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Literal, NamedTuple

from common import REPO_ROOT, logger, run

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


class RuntimeInfo(NamedTuple):
    runtime_dirs: list[Path]
    qt_dir: Path | None


def find_qt_dir(install_root: Path, qt6_version: str, qt6_install_root: str | None) -> Path | None:
    search_root = Path(qt6_install_root).parent if qt6_install_root else install_root

    for qt_candidate in search_root.glob(f"qt6-{qt6_version}-*/{qt6_version}/*"):
        if (qt_candidate / "lib").is_dir():
            return qt_candidate
    return None


def get_runtime_info(install_root: Path, qt6_version: str) -> RuntimeInfo:
    install_dirs_path = install_root / "install_dirs.json"
    install_dirs: dict[str, str] = json.loads(install_dirs_path.read_text()) if install_dirs_path.is_file() else {}

    # Qt is handled separately via `stage_qt_runtime_payload`.
    qt6_install_root = None
    if "qt6" in install_dirs:
        qt6_install_root = install_dirs.pop("qt6")

    qt_dir_env = os.getenv("QT_DIR")
    qt_dir = Path(qt_dir_env) if qt_dir_env else find_qt_dir(install_root, qt6_version, qt6_install_root)

    if ARGS.shared:
        dependencies_to_stage = set(install_dirs.keys())
    else:
        # OCCT is shared by default (see `build-all.py --occt-static`): a static OCCT gets a
        # private copy in every plug-in and shapes handed between plug-ins are misread.
        # Whatever was built shared is staged; `--occt-shared` additionally insists on it.
        dependencies_to_stage = {
            name for name in ("occt",) if name in install_dirs and "-shared-" in Path(install_dirs[name]).name
        }
        if ARGS.occt_shared:
            assert "occt" in dependencies_to_stage, f"Expected a shared OCCT build, found: {install_dirs.get('occt')}"

    runtime_dirs = []
    for name in sorted(dependencies_to_stage):
        runtime_dir = Path(install_dirs[name])
        if "-shared-" not in runtime_dir.name:
            continue
        runtime_dirs.append(runtime_dir)
    return RuntimeInfo(runtime_dirs, qt_dir)


def get_soname(shared_object: Path) -> str | None:
    """Name the dynamic loader looks `shared_object` up by: its SONAME, on macOS its install name.

    `None` for binaries that don't have one (e.g. Python extension modules).
    """
    try:
        if is_platform("MAC"):
            # Prints the binary's path, followed by its install name if it has one.
            lines = run("otool", "-D", str(shared_object), stderr=subprocess.DEVNULL).splitlines()
            return lines[1].strip().rsplit("/", 1)[-1] if len(lines) > 1 else None
        readelf_output = run("readelf", "-d", str(shared_object), stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    match = re.search(r"\(SONAME\).*Library soname: \[(.*)\]", readelf_output)
    return match.group(1) if match else None


def get_needed_libraries(binary: Path) -> list[str]:
    """File names of the shared libraries `binary` is linked to."""
    try:
        if is_platform("MAC"):
            lines = run("otool", "-L", str(binary), stderr=subprocess.DEVNULL).splitlines()[1:]
            return [line.strip().split(" (")[0].rsplit("/", 1)[-1] for line in lines if line.strip()]
        readelf_output = run("readelf", "-d", str(binary), stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return []  # Not a binary.
    return re.findall(r"\(NEEDED\).*Shared library: \[(.*)\]", readelf_output)


def ensure_soname_links(paths: list[Path]) -> None:
    """Ensure that all shared libraries in `paths` are present using their SONAMEs (at least as symlinks)."""
    for shared_object in paths:
        if not shared_object.is_file():
            continue
        soname = get_soname(shared_object)
        if not soname:
            continue
        soname_path = shared_object.parent / soname
        if soname_path.exists():
            continue
        soname_path.symlink_to(shared_object.name)


def is_shared_library(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith((".so", ".dylib", ".dll")) or ".so." in name


def mac_rpaths(binary: Path) -> list[str]:
    """LC_RPATH entries of a Mach-O binary."""
    output = run("otool", "-l", str(binary))
    return re.findall(r"cmd LC_RPATH\n\s+cmdsize \d+\n\s+path (\S+)", output)


def mac_add_rpath(binary: Path, rpath: str) -> None:
    """Add `rpath` to `binary` and re-sign it: editing a Mach-O invalidates its signature,
    and arm64 macOS refuses to load an unsigned or mis-signed image."""
    if rpath in mac_rpaths(binary):
        return
    run("install_name_tool", "-add_rpath", rpath, str(binary))
    run("codesign", "--force", "--sign", "-", str(binary))


def mac_fix_rpaths(package_dir: Path, executables: tuple[Path, ...] = ()) -> None:
    """Make every shared library in `package_dir` resolve its @rpath dependencies next to itself.

    With CREATE_BUNDLE the plug-ins and core dylibs get no LC_RPATH from CMake at all;
    only the Python wrapper carries `@loader_path`. That is enough when the plug-in is
    dlopen'd through the wrapper (dyld accumulates rpaths along the load chain) but not
    for IfcConvert & co, whose plug-ins would otherwise fail to find OCCT and each other.
    """
    for binary in package_dir.rglob("*"):
        if not binary.is_file() or binary.is_symlink() or not is_shared_library(binary):
            continue
        mac_add_rpath(binary, "@loader_path")
    for exe in executables:
        mac_add_rpath(exe, "@executable_path")


def stage_runtime_payload(install_dir: Path, dest: Path, *, include_geometry_writers: bool = True) -> list[Path]:
    """Copy all libs from `install_dir/{bin,lib,lib64}` into `dest` and return where they ended up.

    Every library is staged once, under the name the dynamic loader looks it up by (see `get_soname`).
    The `libX.so -> libX.so.1 -> libX.so.1.2.3` chain of symlinks a versioned library is installed
    with is not reproduced: the other names only serve the linker, and since a wheel can't hold
    symlinks, each of them ends up there as one more full copy of the library.
    """
    staged_files = []
    copied_files = []
    for runtime_dir_name in ("bin", "lib", "lib64"):
        runtime_dir = install_dir / runtime_dir_name
        if not runtime_dir.is_dir():
            continue
        for runtime_file in runtime_dir.rglob("*"):
            if runtime_file.is_symlink() or not runtime_file.is_file():
                continue
            if not is_shared_library(runtime_file):
                continue
            if not include_geometry_writers and runtime_file.name.startswith("ifcopenshell.geometry.writer."):
                continue
            dest_file = dest / (get_soname(runtime_file) or runtime_file.name)
            staged_files.append(dest_file)
            # Currently there's an overlap between dependencies installations.
            # E.g. libraries from occt are installed to both `ifcopenshell/lib`
            # (as part of `ifcopenshell_deploy_qt_runtime`)
            # and to `occt-shared/lib`. So we skip previously installed binaries.
            if dest_file.exists():
                continue
            shutil.copy(runtime_file, dest_file)
            copied_files.append(dest_file)
    for lib in copied_files:
        if is_platform("MAC"):
            mac_add_rpath(lib, "@loader_path")
        else:
            run("patchelf", "--set-rpath", "$ORIGIN", str(lib))
    return staged_files


def prune_unused_libraries(package_dir: Path, candidates: list[Path]) -> None:
    """Remove the `candidates` that no other binary in `package_dir` is linked to, directly or indirectly.

    A dependency installs all of its libraries, of which IfcOpenShell typically uses only a part
    (e.g. about half of the OCCT toolkits).
    """
    unused = {candidate.name: candidate for candidate in candidates}
    queue = [
        path
        for path in package_dir.rglob("*")
        if path.is_file() and path.name not in unused and (is_shared_library(path) or os.access(path, os.X_OK))
    ]
    while queue:
        for needed in get_needed_libraries(queue.pop()):
            if needed in unused:
                queue.append(unused.pop(needed))
    for path in unused.values():
        logger.debug(f"Not packaging '{path.name}': nothing links to it")
        path.unlink()


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
    qt_lib_files = []
    for lib_file in (qt_dir / "lib").iterdir():
        if is_so_file(lib_file):
            dest_file = dest / lib_file.name
            qt_lib_files.append(dest_file)
            shutil.copy(lib_file, dest_file, follow_symlinks=False)
    ensure_soname_links(qt_lib_files)

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
    for lib_so in qt_lib_files:
        if lib_so.is_file():
            run("patchelf", "--set-rpath", "$ORIGIN", str(lib_so))

    qt_conf_path = dest / "qt.conf"
    qt_conf_path.write_text("[Paths]\nPrefix = .\n")


KNOWN_EXCEPTIONS = frozenset(
    (
        # Optional Qt SQL driver plugins we don't ship the client libs for.
        "libqsqlpsql.so",
        "libqsqlmysql.so",
        "libqsqlmimer.so",
        "libqsqlodbc.so",
    )
)


HAS_MISSING_DEPENDENCIES = False


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
            is_known = binary_file.name in KNOWN_EXCEPTIONS
            log = logger.debug if is_known else logger.warning
            log(f"Missing runtime dependencies for {binary_file}")
            for line in ldd_output.splitlines():
                if "not found" in line:
                    log(line)
            if not is_known:
                missing = True

    if missing:
        global HAS_MISSING_DEPENDENCIES
        HAS_MISSING_DEPENDENCIES = True
        logger.warning("Runtime dependency check found issues; continuing packaging.")


MAC_SYSTEM_LIBRARY_PREFIXES = ("/usr/lib/", "/System/")


def check_runtime_dependencies_mac(package_dir: Path) -> None:
    """macOS counterpart of `check_runtime_dependencies`, based on `otool -L`.

    Every `@rpath/` dependency must be present in `package_dir` (all staged binaries carry
    an `@loader_path` rpath, see `mac_fix_rpaths`), and no dependency may point at an
    absolute path outside the system frameworks, since that would only resolve on the
    build machine.
    """
    missing = False
    staged = {p.name for p in package_dir.rglob("*") if is_shared_library(p)}
    for binary_file in package_dir.rglob("*"):
        if not binary_file.is_file() or binary_file.is_symlink():
            continue
        if not (is_shared_library(binary_file) or os.access(binary_file, os.X_OK)):
            continue
        try:
            otool_output = run("otool", "-L", str(binary_file), stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            continue  # Not a Mach-O file.
        problems = []
        for line in otool_output.splitlines()[1:]:
            dependency = line.strip().split(" (")[0]
            if not dependency:
                continue
            if dependency.startswith(MAC_SYSTEM_LIBRARY_PREFIXES):
                continue
            if dependency.startswith(("@rpath/", "@loader_path/", "@executable_path/")):
                if dependency.split("/", 1)[1] not in staged:
                    problems.append(f"{dependency} => not found")
            elif dependency.startswith("/"):
                problems.append(f"{dependency} => absolute path outside the package")
        if problems:
            logger.warning(f"Missing runtime dependencies for {binary_file}")
            for problem in problems:
                logger.warning(problem)
            missing = True

    if missing:
        global HAS_MISSING_DEPENDENCIES
        HAS_MISSING_DEPENDENCIES = True
        logger.warning("Runtime dependency check found issues; continuing packaging.")


def package_python_wrapper(
    py_dir: Path,
    ifcopenshell_install_dir: Path,
    github_sha: str,
    output_dir: Path,
    arch_suffix: str,
    runtime_dirs: list[Path],
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

    if not is_platform("MAC"):
        for lib_so in ifcopenshell_dir.glob("*.so*"):
            if lib_so.is_file():
                run("patchelf", "--set-rpath", "$ORIGIN", str(lib_so))

    # Cache from test run during build.
    pycache_dir = ifcopenshell_dir / "__pycache__"
    if pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)
    for pyc_file in ifcopenshell_dir.rglob("*.pyc"):
        pyc_file.unlink()

    stage_runtime_payload(ifcopenshell_install_dir, ifcopenshell_dir)

    dependency_libs = []
    for runtime_dir in runtime_dirs:
        dependency_libs += stage_runtime_payload(runtime_dir, ifcopenshell_dir)
    prune_unused_libraries(ifcopenshell_dir, dependency_libs)

    if is_platform("MAC"):
        mac_fix_rpaths(ifcopenshell_dir)
        check_runtime_dependencies_mac(ifcopenshell_dir)
    else:
        check_runtime_dependencies(ifcopenshell_dir)

    if ARGS.no_zip:
        return
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
    runtime_dirs: list[Path],
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

    dependency_libs = []
    for runtime_dir in runtime_dirs:
        dependency_libs += stage_runtime_payload(runtime_dir, package_dir)
    prune_unused_libraries(package_dir, dependency_libs)

    # On macOS QT apps are packaged as .app bundles (`package_app_bundle`) instead,
    # and the flat executables get their rpaths patched below.
    if is_platform("MAC"):
        mac_fix_rpaths(package_dir, executables=(package_dir / exe,))
        check_runtime_dependencies_mac(package_dir)
    else:
        run("patchelf", "--set-rpath", "$ORIGIN", str(package_dir / exe))
        stage_qt_runtime_payload(exe_path, package_dir, qt_dir)

        if exe == "BonsaiViewer":
            connectors_dir = package_dir / "connectors"
            connectors_dir.mkdir()
            shutil.copytree(autodesk_connector_dir, connectors_dir / autodesk_connector_dir.name, symlinks=True)

        check_runtime_dependencies(package_dir)

    if ARGS.no_zip:
        return
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

    if ARGS.no_zip:
        return
    zip_path = output_dir / f"{app}-{VERSION}-{github_sha}-{arch_suffix}.zip"
    run("zip", "-qq", "-r", str(zip_path), app_path.name, cwd=install_root)


ARCH_SUFFIXES = ("linux64", "linuxarm64", "macosm164")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class Args(NamedTuple):
    arch_suffix: str
    log_level: str
    occt_shared: bool
    shared: bool
    no_zip: bool
    fail_on_missing_deps: bool
    no_executables: bool


ARGS: Args


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("arch_suffix", choices=ARCH_SUFFIXES, help="Zip filename suffix.")
    # TODO: relax default to INFO once things get more stable.
    parser.add_argument("--log-level", default="DEBUG", choices=LOG_LEVELS, help="Logging verbosity.")
    parser.add_argument(
        "--occt-shared",
        action="store_true",
        help="Insist that OCCT was built as shared libraries (the default; a shared OCCT is always staged).",
    )
    parser.add_argument("--shared", action="store_true", help="Build was made with shared libraries.")
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help=(
            "Stage packages but skip creating zip archives and don't clean up the staged "
            "directories, useful for local debugging."
        ),
    )
    parser.add_argument(
        "--fail-on-missing-deps",
        action="store_true",
        help="Exit with an error at the end if any packaged binary has missing runtime dependencies.",
    )
    parser.add_argument(
        "--no-executables",
        action="store_true",
        help="Skip packaging standalone executables; only Python wrappers get zipped.",
    )
    args = parser.parse_args()

    global ARGS
    ARGS = Args(
        arch_suffix=args.arch_suffix,
        log_level=args.log_level,
        occt_shared=args.occt_shared,
        shared=args.shared,
        no_zip=args.no_zip,
        fail_on_missing_deps=args.fail_on_missing_deps,
        no_executables=args.no_executables,
    )
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
    runtime_dirs, qt_dir = get_runtime_info(install_root, qt6_version)

    # Iterate over all built Python wrappers in `install/ifcopenshell/python-x.y.z`
    # and zip them, bundling all dynamic libs from `lib`.
    github_sha = get_git_sha()
    for py_dir in sorted(ifcopenshell_install_dir.glob("python-*")):
        package_python_wrapper(py_dir, ifcopenshell_install_dir, github_sha, output_dir, ARGS.arch_suffix, runtime_dirs)

    # Iterate over all executables in `install/ifcopenshell/bin` and zip them.
    # Each zip bundles dynamic libs from `lib` and also qt libs.
    bin_dir = ifcopenshell_install_dir / "bin"
    for exe_path in [] if ARGS.no_executables else sorted(bin_dir.iterdir()):
        if is_packageable_executable(exe_path):
            package_executable(
                exe_path,
                ifcopenshell_install_dir,
                github_sha,
                output_dir,
                autodesk_connector_dir,
                qt_dir,
                runtime_dirs,
                ARGS.arch_suffix,
            )

    if not ARGS.no_executables and is_platform("MAC"):
        for app_path in sorted(ifcopenshell_install_dir.glob("*.app")):
            package_app_bundle(
                app_path, ifcopenshell_install_dir, github_sha, output_dir, autodesk_connector_dir, ARGS.arch_suffix
            )

    if ARGS.fail_on_missing_deps and HAS_MISSING_DEPENDENCIES:
        raise Exception("Runtime dependency check found issues; see warnings above.")


if __name__ == "__main__":
    main()
