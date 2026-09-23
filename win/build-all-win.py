# /// script
# [tool.ty.environment]
# root = ["."]
# ///
"""
It's not really a full version of nix/build-all.py for Windows,
but serves the similar purpose - build all packages during CI (though by using cmd scripts),
but also archives them to '~/outputs'.
"""

import argparse
import os
import platform
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import NamedTuple
from zipfile import ZipFile

from common import logger, run, run_streamed
from vs_cfg import get_vs_var


class Args(NamedTuple):
    skip_ifcopenshell_build: bool
    skip_executables: bool
    no_zip: bool
    fail_on_missing_deps: bool


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Environment variables:\n"
        "  GITHUB_SHA    commit SHA to use in archive names (default: 'git rev-parse HEAD')",
    )
    parser.add_argument(
        "--skip-ifcopenshell-build",
        action="store_true",
        help="skip building and only archive the results of a previous build",
    )
    parser.add_argument(
        "--skip-executables",
        action="store_true",
        help="skip packaging standalone executables",
    )
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="stage symlinked '.package-*' directories instead of creating zip archives",
    )
    parser.add_argument(
        "--fail-on-missing-deps",
        action="store_true",
        help="exit with an error if any runtime DLL dependencies were not found among candidates",
    )
    namespace = parser.parse_args()
    return Args(
        skip_ifcopenshell_build=namespace.skip_ifcopenshell_build,
        skip_executables=namespace.skip_executables,
        no_zip=namespace.no_zip,
        fail_on_missing_deps=namespace.fail_on_missing_deps,
    )


def is_arm64() -> bool:
    return platform.machine().lower() in ("arm64", "aarch64")


def build_generator() -> str:
    return "vs2022-ARM64" if is_arm64() else "vs2022-x64"


assert Path.cwd() == Path(__file__).parent, "Run this script from the 'win' directory."

PYTHON_VERSIONS = ["3.10.3", "3.11.8", "3.12.1", "3.13.6", "3.14.0", "3.15.0"]
REPO_PATH = Path(__file__).parent.parent
REPO_WIN = REPO_PATH / "win"
OUTPUT_DIR = Path.home() / "output"


def find_install_dir() -> Path:
    arch_install_dir = REPO_PATH / f"_installed-{build_generator()}"
    if arch_install_dir.exists():
        return arch_install_dir

    install_dirs = [d for d in REPO_PATH.iterdir() if d.is_dir() and d.name.startswith("_installed")]
    if not install_dirs:
        raise RuntimeError("Install directory not found.")
    return max(install_dirs, key=lambda d: d.stat().st_mtime)


def find_dumpbin() -> str:
    dumpbin = shutil.which("dumpbin")
    if dumpbin:
        return dumpbin

    arch_dir = "arm64" if is_arm64() else "x64"
    root = Path(get_vs_var("VSINSTALLDIR"))
    tools_version = get_vs_var("VCToolsVersion")
    # Hostx64 tools are present even on the arm, no HostARM64 there.
    dumpbin_path = root / "VC" / "Tools" / "MSVC" / tools_version / "bin" / "Hostx64" / arch_dir / "dumpbin.exe"
    assert dumpbin_path.exists(), f"dumpbin.exe not found at {dumpbin_path}"
    return str(dumpbin_path)


def dumpbin_dependents(file: Path, dumpbin: str) -> set[str]:
    dependent_dll_re = re.compile(r"^\s*([A-Za-z0-9_.+-]+\.dll)\s*$", re.IGNORECASE)
    output = run(dumpbin, "/nologo", "/dependents", str(file))
    return {match.group(1).lower() for line in output.splitlines() if (match := dependent_dll_re.match(line))}


def runtime_candidate_files(install_dir: Path, extra_files: list[Path] | None = None) -> list[Path]:
    candidates = list((install_dir / "bin").glob("*.dll"))
    plugins_dir = install_dir / "plugins"
    if plugins_dir.exists():
        candidates.extend(plugins_dir.rglob("*.dll"))
    if extra_files:
        candidates.extend(extra_files)
    return sorted({file.resolve(): file for file in candidates}.values())


MISSING_DLLS: set[str] = set()


def is_known_missing_dll(name: str) -> bool:
    known_missing_dlls = {
        "advapi32.dll",
        "authz.dll",
        "bcryptprimitives.dll",
        "d3d11.dll",
        "d3d12.dll",
        "dwmapi.dll",
        "dwrite.dll",
        "dxgi.dll",
        "gdi32.dll",
        "kernel32.dll",
        "mpr.dll",
        "msvcp140.dll",
        "msvcp140_1.dll",
        "msvcp140_2.dll",
        "netapi32.dll",
        "ntdll.dll",
        "ole32.dll",
        "oleaut32.dll",
        "opengl32.dll",
        "rpcrt4.dll",
        "setupapi.dll",
        "shell32.dll",
        "shlwapi.dll",
        "user32.dll",
        "userenv.dll",
        "uxtheme.dll",
        "vcruntime140.dll",
        "vcruntime140_1.dll",
        "version.dll",
        "winmm.dll",
        "ws2_32.dll",
        "wsock32.dll",
    }
    # Provided by the Python interpreter.
    if re.fullmatch(r"python3\d*\.dll", name):
        return True
    # API sets, resolved by the OS loader.
    if name.startswith("api-ms-win-"):
        return True
    return name in known_missing_dlls


def trace_runtime_dependencies(roots: set[Path], candidates: set[Path]) -> set[Path]:
    dumpbin = find_dumpbin()
    lookup = {file.name.lower(): file for file in candidates}
    resolved: set[Path] = set()
    seen: set[Path] = set()
    queue = list(roots)

    while queue:
        file = queue.pop(0)
        file_key = file.resolve()
        if file_key in seen:
            continue
        seen.add(file_key)

        for dependent_name in dumpbin_dependents(file, dumpbin):
            dependent = lookup.get(dependent_name)
            # Not one of our candidates (e.g. system/CRT DLLs).
            if dependent is None:
                if not is_known_missing_dll(dependent_name):
                    MISSING_DLLS.add(dependent_name)
                continue
            # Already queued.
            if dependent in resolved:
                continue
            resolved.add(dependent)
            queue.append(dependent)

    return resolved


def is_geometry_writer(file: Path) -> bool:
    # Per-schema geometry writers ship with the Python package only, not next to the
    # executables. 'ifcopenshell.geometry.writer.' covers the core library, the
    # underscore form covers the per-schema plugins.
    ifc_geometry_writer_prefixes = ("ifcopenshell.geometry.writer.", "ifcopenshell_geometry_writer_")
    return file.name.startswith(ifc_geometry_writer_prefixes)


def collect_ifc_runtime_plugins(dlls: set[Path], dependencies: set[Path]) -> set[Path]:
    """IfcOpenShell plugins are loaded by name at runtime, so dumpbin cannot discover them."""
    # Runtime plugins are canonically prefixed with 'ifcopenshell_' (see
    # decorated_basename() in src/plugin/plugin.cpp and the OUTPUT_NAME properties of
    # the plugin targets, e.g. 'ifcopenshell_parse_schema_ifc${schema}'), while the
    # core shared libraries keep the dotted 'ifcopenshell.' names. Match both so the
    # load-by-name plugins are not silently dropped from the archives.
    ifc_runtime_plugin_prefixes = ("ifcopenshell.", "ifcopenshell_")
    return {
        d for d in (dlls - dependencies) if d.name.startswith(ifc_runtime_plugin_prefixes) and not is_geometry_writer(d)
    }


def is_qt_deployment_dll(file: Path) -> bool:
    qt_deployment_dlls = {
        "dxcompiler.dll",
        "dxil.dll",
        "libegl.dll",
        "libglesv2.dll",
        "opengl32sw.dll",
        "vulkan-1.dll",
    }
    name = file.name.lower()
    return name.startswith("qt") or name.startswith("d3dcompiler_") or name in qt_deployment_dlls


def collect_qt_deployment_files(install_dir: Path) -> dict[str, Path]:
    files = {file.name: file for file in (install_dir / "bin").glob("*.dll") if is_qt_deployment_dll(file)}
    plugins_dir = install_dir / "plugins"
    if plugins_dir.exists():
        for file in plugins_dir.rglob("*.dll"):
            files[file.relative_to(install_dir).as_posix()] = file
    return files


def build_connector() -> Path:
    connector_repo = REPO_PATH / "src" / "bonsaiviewer-autodesk"
    connector_dir = connector_repo / "dist" / "autodesk"
    run_streamed(sys.executable, str(connector_repo / "packaging" / "build.py"))
    return connector_dir


def collect_connector_files(connector_dir: Path) -> dict[str, Path]:
    """Map the Autodesk connector to ``connectors/autodesk/`` arcnames."""
    files: dict[str, Path] = {}
    for file in connector_dir.rglob("*"):
        if file.is_file():
            arcname = Path("connectors") / "autodesk" / file.relative_to(connector_dir)
            files[arcname.as_posix()] = file
    return files


def write_zip(zip_path: Path, files: dict[str, Path], generated_files: dict[str, str] | None = None) -> None:
    zip_path.parent.mkdir(exist_ok=True)
    with ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for arcname, file in sorted(files.items()):
            zipf.write(file, arcname=arcname)
        for arcname, contents in sorted((generated_files or {}).items()):
            zipf.writestr(arcname, contents)


def stage_symlinks(package_dir: Path, files: dict[str, Path], generated_files: dict[str, str] | None = None) -> None:
    if package_dir.exists():
        # Clean up previous local runs.
        shutil.rmtree(package_dir)
    for arcname, file in files.items():
        if file.is_dir():
            continue
        dest = package_dir / arcname
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(file)
    for arcname, contents in (generated_files or {}).items():
        dest = package_dir / arcname
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(contents)


def build() -> None:
    for python_version in PYTHON_VERSIONS:
        logger.info(f"Building for Python {python_version}...")
        run_streamed(
            *[
                sys.executable,
                str(REPO_WIN / "build-deps.py"),
                build_generator(),
                "Release",
                "-y",
                "--reuse-boost",
                "--use-ninja",
                "--shared",
                "--python-version",
                python_version,
            ]
        )
        run_streamed(
            *[
                sys.executable,
                str(REPO_WIN / "run-cmake.py"),
                build_generator(),
                "--add-commit-sha",
                "--use-ninja",
                "--build-cfg",
                "Release",
                "--",
                "-DENABLE_BUILD_OPTIMIZATIONS=ON",
                "-DGLTF_SUPPORT=ON",
                "-DWITH_PROJ=ON",
                "-DBUILD_EXAMPLES=OFF",
                "-DBUILD_BONSAIVIEWER=ON",
                "-DUSE_CCACHE=ON",
            ]
        )
        run_streamed(*[sys.executable, str(REPO_WIN / "install-ifcopenshell.py"), build_generator(), "Release"])


def archive_executables(zip_template: str, connector_dir: Path, no_zip: bool) -> None:
    install_dir = find_install_dir()

    bin_files = set((install_dir / "bin").iterdir())
    exes = {file for file in bin_files if file.suffix.lower() == ".exe"}
    dlls = {file for file in bin_files if file.suffix.lower() == ".dll"}
    dependencies = trace_runtime_dependencies(exes, dlls)
    ifc_runtime_plugins = collect_ifc_runtime_plugins(dlls, dependencies)
    qt_deployment_files = collect_qt_deployment_files(install_dir)

    for file in sorted(exes):
        files: dict[str, Path] = {file.name: file}
        roots = {file}

        # IfcOpenShell plugins are loaded by name at runtime, so dumpbin cannot discover them.
        # svgfill links its provider plugin directly, so dumpbin can discover that dependency.
        if not file.name.lower().startswith("svgfill"):
            roots.update(ifc_runtime_plugins)
            for plugin in ifc_runtime_plugins:
                files[plugin.name] = plugin

        runtime_dependencies = trace_runtime_dependencies(roots, dlls)
        for dependency in runtime_dependencies:
            files[dependency.name] = dependency

        generated_files = {}
        if any(dependency.name.lower().startswith("qt") for dependency in runtime_dependencies):
            for arcname, dependency in qt_deployment_files.items():
                files[arcname] = dependency
            generated_files["qt.conf"] = "[Paths]\nPrefix = .\n"

        # Bundle the Autodesk connector next to the Bonsai Viewer executable.
        if file.stem == "BonsaiViewer":
            files.update(collect_connector_files(connector_dir))

        if no_zip:
            package_dir = install_dir / f".package-{file.stem}"
            stage_symlinks(package_dir, files, generated_files)
            logger.info(f"{file} -> {package_dir}")
            continue

        zip_name = zip_template.format(package_name=file.stem)
        write_zip(OUTPUT_DIR / zip_name, files, generated_files)
        logger.info(f"{file} -> {zip_name}")


def archive_python_package(python_version: str, python_path: Path, zip_template: str, no_zip: bool) -> None:
    install_dir = find_install_dir()

    bin_files = set((install_dir / "bin").iterdir())
    exes = {file for file in bin_files if file.suffix.lower() == ".exe"}
    dlls = {file for file in bin_files if file.suffix.lower() == ".dll"}
    dependencies = trace_runtime_dependencies(exes, dlls)
    ifc_runtime_plugins = collect_ifc_runtime_plugins(dlls, dependencies)
    geometry_writing = {f for f in bin_files if is_geometry_writer(f)}

    python_version_major_minor = "".join(python_version.split(".")[:2])
    site_packages = python_path / "Lib" / "site-packages"
    package_path = site_packages / "ifcopenshell"

    # Clean cache.
    for file in package_path.rglob("*.pyc"):
        file.unlink()

    files: dict[str, Path] = {}
    package_binaries = set()
    for file in package_path.rglob("*"):
        arcname = file.relative_to(site_packages)
        files[arcname.as_posix()] = file
        if file.suffix.lower() in (".dll", ".exe", ".pyd"):
            package_binaries.add(file)

    runtime_files = ifc_runtime_plugins | geometry_writing
    runtime_dependencies = trace_runtime_dependencies(package_binaries | runtime_files, dlls | package_binaries)

    # TODO: we're packing plugins twice? Some are already installed into the package dir.
    for file in runtime_files | runtime_dependencies:
        files[f"ifcopenshell/{file.name}"] = file

    if no_zip:
        package_dir = install_dir / f".package-python-{python_version_major_minor}"
        stage_symlinks(package_dir, files)
        logger.info(f"{package_path} -> {package_dir}")
        return

    zip_name = zip_template.format(package_name=f"ifcopenshell-python-{python_version_major_minor}")
    write_zip(OUTPUT_DIR / zip_name, files)
    logger.info(f"{package_path} -> {zip_name}")


def archive_python_packages(zip_template: str, no_zip: bool) -> None:
    deps_path = REPO_PATH / "_deps"
    for d in deps_path.iterdir():
        if d.is_dir() and (d.name.startswith("python.") or d.name.startswith("pythonarm64.")):
            python_version = d.name.partition(".")[2]
            python_path = d / "tools"
            archive_python_package(python_version, python_path, zip_template, no_zip)


def get_zip_template() -> str:
    version = (REPO_PATH / "VERSION").read_text().strip()
    if "GITHUB_SHA" in os.environ:
        sha = os.environ["GITHUB_SHA"]
    else:
        sha = run("git", "rev-parse", "HEAD").strip()
    sha = sha[:7]
    return f"{{package_name}}-v{version}-{sha}-{'win-arm64' if is_arm64() else 'win64'}.zip"


def main() -> None:
    ARGS = parse_args()

    zip_template = get_zip_template()

    logger.info(f"Output directory: {OUTPUT_DIR}")
    if not ARGS.skip_ifcopenshell_build:
        build()
    if not ARGS.skip_executables:
        connector_dir = build_connector()
        archive_executables(zip_template, connector_dir, ARGS.no_zip)
    archive_python_packages(zip_template, ARGS.no_zip)

    if MISSING_DLLS:
        logger.warning("DLLs not found among candidates:")
        for name in sorted(MISSING_DLLS):
            logger.warning(f"  {name}")
        if ARGS.fail_on_missing_deps:
            logger.error("Failing due to missing DLLs (--fail-on-missing-deps).")
            sys.exit(1)


if __name__ == "__main__":
    main()
