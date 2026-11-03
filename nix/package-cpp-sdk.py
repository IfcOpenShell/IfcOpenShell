#!/usr/bin/env python3
"""Stage a relocatable Linux C++ SDK from a build-all.py installation.

Requires Python 3.11+, patchelf, ldd, and RPM. Dependencies must have been built without
--diskcleanup so that their license notices can be included.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# These belong to the host ABI. In particular, never ship a private glibc/loader.
HOST_LIBRARIES = re.compile(r"^(ld-linux[^/]*|lib(c|m|dl|pthread|rt|resolv|util|anl|gcc_s|stdc\+\+)\.so(?:\..*)?)$")


def run(*args, **kwargs):
    return subprocess.check_output(args, text=True, **kwargs).strip()


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def is_elf(path):
    if path.is_symlink() or not path.is_file():
        return False
    with path.open("rb") as stream:
        return stream.read(4) == b"\x7fELF"


def relocate_cmake(root, prefixes):
    """Replace build-machine prefixes even in third-party imported targets.

    Each replacement is relative to the file being evaluated, rather than a
    variable that nested find_dependency() calls could overwrite.
    """
    for path in root.rglob("*.cmake"):
        content = path.read_text()
        for old, new in sorted(prefixes.items(), key=lambda item: -len(str(item[0]))):
            relative = os.path.relpath(new, path.parent).replace(os.sep, "/")
            content = content.replace(str(old), "${CMAKE_CURRENT_LIST_DIR}/" + relative)
        path.write_text(content)


def normalize_boost(prefix):
    # build-all.py uses b2 stage and copies headers next to lib/. Its generated
    # boost_headers config still points back into the Boost source tree.
    # Give the SDK a conventional include/boost tree and repair that config.
    staged_headers = prefix / "boost"
    if staged_headers.is_dir():
        (prefix / "include").mkdir(exist_ok=True)
        shutil.move(staged_headers, prefix / "include" / "boost")
    for config in prefix.rglob("*-config.cmake"):
        original = config.read_text()
        if "get_filename_component(_BOOST_INCLUDEDIR" not in original:
            continue
        content, count = re.subn(
            r'get_filename_component\(_BOOST_INCLUDEDIR\s+"[^"]*"\s+ABSOLUTE\)',
            'get_filename_component(_BOOST_INCLUDEDIR "${CMAKE_CURRENT_LIST_DIR}/../../../include" ABSOLUTE)',
            original,
        )
        if count != 1:
            raise RuntimeError(f"Cannot relocate Boost headers in {config}")
        config.write_text(content)


def configure_package(root, dependencies):
    configs = list(root.glob("lib*/cmake/IfcOpenShell/IfcOpenShellConfig.cmake"))
    if len(configs) != 1:
        raise RuntimeError(f"Expected one IfcOpenShell package config, found {configs}")
    config = configs[0]
    prefix_lines = []
    # Some dependency installers use lib64, which Debian-family CMake does
    # not search by default. Also expose config directories and library dirs
    # explicitly, so the SDK works across Linux distributions.
    package_dirs = set(dependencies)
    library_dirs = set()
    for dependency in dependencies:
        package_dirs.update(
            path.parent for path in dependency.rglob("*.cmake") if path.name.endswith(("Config.cmake", "-config.cmake"))
        )
        library_dirs.update(path for path in (dependency / "lib", dependency / "lib64") if path.is_dir())
    for dependency in sorted(package_dirs):
        relative = os.path.relpath(dependency, config.parent).replace(os.sep, "/")
        prefix_lines.append(f'    "${{CMAKE_CURRENT_LIST_DIR}}/{relative}"')
    library_lines = [
        '    "${CMAKE_CURRENT_LIST_DIR}/' + os.path.relpath(path, config.parent).replace(os.sep, "/") + '"'
        for path in sorted(library_dirs)
    ]
    # The project exports references to OpenCOLLADA::OpenCOLLADA, provided by
    # our FindOpenCOLLADA module rather than OpenCOLLADA's legacy config alone.
    modules = root / "share" / "ifcopenshell" / "cmake"
    modules.mkdir(parents=True)
    for module in (REPO / "cmake" / "FindOpenCOLLADA.cmake", REPO / "cmake" / "utilities.cmake"):
        shutil.copy2(module, modules)
    relative_modules = os.path.relpath(modules, config.parent).replace(os.sep, "/")
    config.write_text(
        "# Locate the development dependencies shipped with this SDK.\n"
        'if(CMAKE_VERSION VERSION_LESS "3.24")\n'
        '    message(FATAL_ERROR "This IfcOpenShell SDK requires CMake 3.24 or newer (LINK_GROUP support).")\n'
        "endif()\n"
        "list(PREPEND CMAKE_PREFIX_PATH\n" + "\n".join(prefix_lines) + "\n)\n"
        "list(PREPEND CMAKE_LIBRARY_PATH\n" + "\n".join(library_lines) + "\n)\n"
        f'list(PREPEND CMAKE_MODULE_PATH "${{CMAKE_CURRENT_LIST_DIR}}/{relative_modules}")\n'
        f'include("${{CMAKE_CURRENT_LIST_DIR}}/{relative_modules}/utilities.cmake")\n' + config.read_text()
    )


def bundle_runtime(root):
    binaries = [path for path in root.rglob("*") if is_elf(path)]
    # Only dynamic objects can be patched (some dependency tools are static).
    binaries = [
        path
        for path in binaries
        if subprocess.run(["patchelf", "--print-rpath", str(path)], capture_output=True).returncode == 0
    ]
    library_dirs = sorted({path.parent for path in binaries if ".so" in path.name})
    library_dirs.append(root / "lib")
    (root / "lib").mkdir(exist_ok=True)

    def patch(path):
        rpath = ":".join("$ORIGIN/" + os.path.relpath(directory, path.parent) for directory in library_dirs)
        run("patchelf", "--set-rpath", rpath, str(path))

    # Remove build paths before resolving dependencies, so ldd cannot silently
    # select the original installation in preference to the staged SDK.
    for path in binaries:
        patch(path)
    env = os.environ.copy()
    env.pop("LD_LIBRARY_PATH", None)
    bundled = {}
    for binary in binaries:
        output = run("ldd", str(binary), env=env)
        if "not found" in output:
            raise RuntimeError(f"Unresolved runtime dependency of {binary}:\n{output}")
        for name, location in re.findall(r"^\s*(\S+) => (/.+?) \(0x[0-9a-fA-F]+\)", output, re.MULTILINE):
            source = Path(location)
            if HOST_LIBRARIES.fullmatch(name) or source.is_relative_to(root):
                continue
            destination = root / "lib" / name
            if destination.exists():
                if sha256(source) != sha256(destination):
                    raise RuntimeError(f"Conflicting runtime libraries: {name}")
                continue
            shutil.copy2(source, destination)
            bundled[name] = source
    # Patch after collecting: otherwise comparisons above see modified bytes.
    for name in bundled:
        patch(root / "lib" / name)
    return bundled


def relocate_system_links(root, libraries):
    # Legacy OCCT targets export bare GL/EGL link items. Bundling their SONAME
    # files suffices at runtime, but -lGL still requires an OS development
    # symlink. Link consumers directly to the bundled versioned libraries.
    link_names = {}
    for soname in libraries:
        match = re.fullmatch(r"lib(.+)\.so(?:\..*)?", soname)
        if match:
            link_names[match[1]] = root / "lib" / soname
    for config in root.rglob("*.cmake"):

        def replace_property(match):
            result = []
            for entry in match[2].split(";"):
                wrapped = entry.startswith("$<LINK_ONLY:") and entry.endswith(">")
                value = entry[len("$<LINK_ONLY:") : -1] if wrapped else entry
                name = value
                if value.startswith("/"):
                    library = re.fullmatch(r"lib(.+)\.so(?:\..*)?", Path(value).name)
                    name = library[1] if library else value
                elif value.startswith("-l"):
                    name = value[2:]
                if name in link_names:
                    relative = os.path.relpath(link_names[name], config.parent).replace(os.sep, "/")
                    value = "${CMAKE_CURRENT_LIST_DIR}/" + relative
                    entry = "$<LINK_ONLY:" + value + ">" if wrapped else value
                result.append(entry)
            return match[1] + ";".join(result) + match[3]

        original = config.read_text()
        content = re.sub(r'(INTERFACE_LINK_LIBRARIES\s+")([^"]*)(")', replace_property, original)
        if content != original:
            config.write_text(content)


def collect_licenses(install, root, runtime):
    destination = root / "licenses"
    destination.mkdir()
    for name in ("COPYING", "COPYING.LESSER"):
        shutil.copy2(REPO / name, destination)
    sources = install.parent / "build"
    notices = 0
    for source in sources.iterdir():
        if not source.is_dir() or source.name == "ifcopenshell":
            continue
        for path in source.iterdir():
            if not re.match(r"(?i)^(licen[cs]e|copying|copyright|notice|authors)", path.name):
                continue
            target = destination / "third-party" / source.name / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.is_dir():
                shutil.copytree(path, target, symlinks=False)
            else:
                shutil.copy2(path, target)
            notices += 1
    if not notices:
        raise RuntimeError("No dependency license notices found; build without --diskcleanup and dependency caches")
    # Runtime libraries taken from the OS carry their distribution's notices.
    packages = {run("rpm", "-qf", "--qf", "%{NAME}", str(path.resolve())) for path in runtime.values()}
    for package in packages:
        paths = run("rpm", "-q", "--licensefiles", package).splitlines()
        for item in paths:
            path = Path(item)
            if path.is_file() and item.startswith("/usr/share/licenses/"):
                target = destination / "system" / path.relative_to("/usr/share/licenses")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--arch", choices=["linux64", "linuxarm64"], required=True)
    args = parser.parse_args()
    install = args.install_dir.resolve()
    version = (REPO / "VERSION").read_text().strip()
    commit = run("git", "rev-parse", "HEAD", cwd=REPO)
    name = f"ifcopenshell-cpp-{version}-{commit[:7]}-{args.arch}"
    root = args.output.resolve() / name
    root.mkdir(parents=True)  # Refuse to reuse a stale staging tree.
    shutil.copytree(install / "ifcopenshell", root, dirs_exist_ok=True, symlinks=False)
    manifest = json.loads((install / "development_install_dirs.json").read_text())
    prefixes = {install / "ifcopenshell": root}
    dependencies = []
    for dependency, location in sorted(manifest.items()):
        source = Path(location).resolve()
        target = root / "third-party" / source.name
        shutil.copytree(source, target, symlinks=False)
        if dependency == "boost":
            normalize_boost(target)
        prefixes[source] = target
        dependencies.append(target)
    relocate_cmake(root, prefixes)
    configure_package(root, dependencies)
    runtime = bundle_runtime(root)
    relocate_system_links(root, runtime)
    collect_licenses(install, root, runtime)
    shutil.copytree(REPO / "src" / "examples", root / "examples")
    shutil.copytree(args.docs, root / "doc" / "html", ignore=shutil.ignore_patterns(".doctrees", ".buildinfo"))
    if not (root / "doc" / "html" / "index.html").is_file():
        raise RuntimeError("Missing C++ documentation index")
    shutil.copy2(REPO / "nix" / "cpp-sdk-README.md", root / "README.md")
    recipe = root / "share" / "ifcopenshell" / "build-recipe"
    recipe.mkdir(parents=True)
    for path in (
        REPO / "nix" / "build-all.py",
        REPO / "nix" / "test-cpp-sdk.sh",
        REPO / ".github" / "workflows" / "build-ifcopenshell-cpp-linux.yml",
    ):
        shutil.copy2(path, recipe)
    metadata = {
        "version": version,
        "commit": commit,
        "architecture": args.arch,
        "configuration": "Release",
        "compiler": run("c++", "--version"),
        "glibc": run("getconf", "GNU_LIBC_VERSION"),
        "dependencies": {key: Path(value).name for key, value in sorted(manifest.items())},
        "bundled_system_libraries": sorted(runtime),
        "source": f"https://github.com/IfcOpenShell/IfcOpenShell/tree/{commit}",
    }
    (root / "build-info.json").write_text(json.dumps(metadata, indent=2) + "\n")
    archive = Path(shutil.make_archive(str(root), "zip", root.parent, root.name))
    digest = sha256(archive)
    archive.with_suffix(".zip.sha256").write_text(f"{digest}  {archive.name}\n")
    print(archive)


if __name__ == "__main__":
    main()
