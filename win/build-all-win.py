"""
It's not really a full version of nix/build-all.py for Windows,
but serves the similar purpose - build all packages during CI (though by using cmd scripts),
but also archives them to '~/outputs'.
"""

import os
import platform
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from zipfile import ZipFile


def is_arm64() -> bool:
    arch = os.environ.get("TARGET_ARCH", "").lower()
    if arch in ("arm64", "aarch64"):
        return True
    if arch in ("x64", "amd64", "x86_64"):
        return False
    return platform.machine().lower() in ("arm64", "aarch64")


def build_generator() -> str:
    return "vs2022-ARM64" if is_arm64() else "vs2022-x64"


assert Path.cwd() == Path(__file__).parent, "Run this script from the 'win' directory."

PYTHON_VERSIONS = ["3.10.3", "3.11.8", "3.12.1", "3.13.0", "3.14.0"]
REPO_PATH = Path(__file__).parent.parent
REPO_WIN = REPO_PATH / "win"
# Prebuilt Autodesk connector folder, produced by the connector's packaging
# build.py. The CI workflow builds it before invoking this script; it gets
# bundled next to BonsaiViewer.exe so the viewer can discover it at runtime.
CONNECTOR_DIR = REPO_PATH / "src" / "bonsaiviewer-autodesk" / "dist" / "autodesk"
VERSION = (REPO_PATH / "VERSION").read_text().strip()
if "GITHUB_SHA" in os.environ:
    SHA = os.environ["GITHUB_SHA"][:7]
else:
    SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()[:7]
OUTPUT_DIR = Path.home() / "output"
ZIP_TEMPLATE = f"{{package_name}}-v{VERSION}-{SHA}-{'win-arm64' if is_arm64() else 'win64'}.zip"
DEPENDENT_DLL_RE = re.compile(r"^\s*([A-Za-z0-9_.+-]+\.dll)\s*$", re.IGNORECASE)
QT_DEPLOYMENT_DLLS = {
    "dxcompiler.dll",
    "dxil.dll",
    "libegl.dll",
    "libglesv2.dll",
    "opengl32sw.dll",
    "vulkan-1.dll",
}
QT_CONF = "[Paths]\nPrefix = .\n"


def run(command: list[str]) -> None:
    print("Running:", command)
    subprocess.check_call(command)


def set_env(var_name: str, value: str) -> tuple[str, str | None]:
    """
    :return: Tuple of ``(var_name, old_value)`` to be passed to ``restore_env``.
    """
    old_value = os.getenv(var_name)
    os.environ[var_name] = value
    return var_name, old_value


def restore_env(var_name: str, old_value: str | None) -> None:
    if old_value is None:
        del os.environ[var_name]
    else:
        os.environ[var_name] = old_value


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
    roots = [Path(p) for p in (os.environ.get("VSINSTALLDIR"),) if p]
    roots.extend(
        Path(p)
        for p in (
            r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise",
            r"C:\Program Files\Microsoft Visual Studio\2022\Community",
            r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools",
        )
    )
    for root in roots:
        candidates = sorted((root / "VC" / "Tools" / "MSVC").glob(f"*/bin/Host*/{arch_dir}/dumpbin.exe"))
        if candidates:
            return str(candidates[-1])

    raise RuntimeError("dumpbin.exe not found. Run build-all-win.py from a Visual Studio developer prompt.")


def dumpbin_dependents(file: Path, dumpbin: str) -> set[str]:
    output = subprocess.check_output(
        [dumpbin, "/nologo", "/dependents", str(file)],
        text=True,
        errors="replace",
    )
    return {match.group(1).lower() for line in output.splitlines() if (match := DEPENDENT_DLL_RE.match(line))}


def runtime_candidate_files(install_dir: Path, extra_files: list[Path] | None = None) -> list[Path]:
    candidates = list((install_dir / "bin").glob("*.dll"))
    plugins_dir = install_dir / "plugins"
    if plugins_dir.exists():
        candidates.extend(plugins_dir.rglob("*.dll"))
    if extra_files:
        candidates.extend(extra_files)
    return sorted({file.resolve(): file for file in candidates}.values())


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
            if dependent is None or dependent in resolved:
                continue
            resolved.add(dependent)
            queue.append(dependent)

    return resolved


def is_qt_deployment_dll(file: Path) -> bool:
    name = file.name.lower()
    return name.startswith("qt") or name.startswith("d3dcompiler_") or name in QT_DEPLOYMENT_DLLS


def collect_qt_deployment_files(install_dir: Path) -> dict[str, Path]:
    files = {file.name: file for file in (install_dir / "bin").glob("*.dll") if is_qt_deployment_dll(file)}
    plugins_dir = install_dir / "plugins"
    if plugins_dir.exists():
        for file in plugins_dir.rglob("*.dll"):
            files[file.relative_to(install_dir).as_posix()] = file
    return files


def collect_connector_files() -> dict[str, Path]:
    """Map the prebuilt Autodesk connector to ``connectors/autodesk/`` arcnames."""
    if not CONNECTOR_DIR.is_dir():
        raise RuntimeError(
            f"Autodesk connector not found at {CONNECTOR_DIR}. Build it first with: "
            "python src/bonsaiviewer-autodesk/packaging/build.py"
        )
    files: dict[str, Path] = {}
    for file in CONNECTOR_DIR.rglob("*"):
        if file.is_file():
            arcname = Path("connectors") / "autodesk" / file.relative_to(CONNECTOR_DIR)
            files[arcname.as_posix()] = file
    return files


def write_zip(zip_path: Path, files: dict[str, Path], generated_files: dict[str, str] | None = None) -> None:
    zip_path.parent.mkdir(exist_ok=True)
    with ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for arcname, file in sorted(files.items()):
            zipf.write(file, arcname=arcname)
        for arcname, contents in sorted((generated_files or {}).items()):
            zipf.writestr(arcname, contents)


def build() -> None:
    for python_version in PYTHON_VERSIONS:
        os.environ["PYTHON_VERSION"] = python_version
        print(f"Building for Python {python_version}...")
        subprocess.run(
            [str(REPO_WIN / "build-deps.cmd"), build_generator(), "Release"],
            check=True,
            text=True,
            input="y\n",
        )
        OLD_ADD_COMMIT_SHA = set_env("ADD_COMMIT_SHA", "ON")
        run(
            [
                str(REPO_WIN / "run-cmake.bat"),
                build_generator(),
                "-DENABLE_BUILD_OPTIMIZATIONS=ON",
                "-DGLTF_SUPPORT=ON",
                "-DBUILD_EXAMPLES=OFF",
                "-DBUILD_BONSAIVIEWER=ON",
            ]
        )
        restore_env(*OLD_ADD_COMMIT_SHA)
        run([str(REPO_WIN / "install-ifcopenshell.bat"), build_generator(), "Release"])


def archive_executables() -> None:
    install_dir = find_install_dir()

    bin_files = set((install_dir / "bin").iterdir())
    exes = {file for file in bin_files if file.suffix.lower() == ".exe"}
    dlls = {file for file in bin_files if file.suffix.lower() == ".dll"}
    dependencies = trace_runtime_dependencies(exes, dlls)
    ifc_runtime_plugins = {
        d
        for d in (set(dlls) - dependencies)
        if d.name.startswith("ifcopenshell.") and not d.name.startswith("ifcopenshell.geometry.writer.")
    }
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
            generated_files["qt.conf"] = QT_CONF

        # Bundle the Autodesk connector next to the Bonsai Viewer executable.
        if file.stem == "BonsaiViewer":
            files.update(collect_connector_files())

        zip_name = ZIP_TEMPLATE.format(package_name=file.stem)
        write_zip(OUTPUT_DIR / zip_name, files, generated_files)
        print(f"{file} -> {zip_name}")


def archive_python_package(python_version: str, python_path: Path) -> None:
    install_dir = find_install_dir()

    bin_files = set((install_dir / "bin").iterdir())
    exes = {file for file in bin_files if file.suffix.lower() == ".exe"}
    dlls = {file for file in bin_files if file.suffix.lower() == ".dll"}
    dependencies = trace_runtime_dependencies(exes, dlls)
    ifc_runtime_plugins = {
        d
        for d in (set(dlls) - dependencies)
        if d.name.startswith("ifcopenshell.") and not d.name.startswith("ifcopenshell.geometry.writer.")
    }
    geometry_writing = {f for f in bin_files if f.name.startswith("ifcopenshell.geometry.writer.")}

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
        files[str(arcname)] = file
        if file.suffix.lower() in (".dll", ".exe", ".pyd"):
            package_binaries.add(file)

    runtime_files = ifc_runtime_plugins | geometry_writing
    runtime_dependencies = trace_runtime_dependencies(package_binaries | runtime_files, dlls | package_binaries)

    for file in runtime_files | runtime_dependencies:
        files[f"ifcopenshell/{file.name}"] = file

    zip_name = ZIP_TEMPLATE.format(package_name=f"ifcopenshell-python-{python_version_major_minor}")
    write_zip(OUTPUT_DIR / zip_name, files)
    print(f"{package_path} -> {zip_name}")


def archive_python_packages() -> None:
    deps_path = REPO_PATH / "_deps"
    python_versions: list[str] = []
    for d in deps_path.iterdir():
        if d.is_dir() and (d.name.startswith("python.") or d.name.startswith("pythonarm64.")):
            python_version = d.name.partition(".")[2]
            python_path = d / "tools"
            archive_python_package(python_version, python_path)
            python_versions.append(d.name.partition(".")[2])


def main() -> None:
    print("Output directory:", OUTPUT_DIR)
    build()
    archive_executables()
    archive_python_packages()


if __name__ == "__main__":
    main()
