#!/usr/bin/env python3
# This file was generated with the assistance of an AI coding tool.
"""
Native WASM bootstrap build system for IfcOpenShell.

Builds Emscripten toolchain, third-party dependencies, and IfcOpenShell's
WASM_BUILD target without Pyodide or SWIG.

This is the consolidated entry point: shared utilities live in `nix/core.py`
and dependency build recipes live in `nix/deps.py`. Pinned source versions
and patches live in `nix/sources.lock.json`.

Usage:
    python nix/wasm_native.py <command>

Commands:
    doctor              Check system prerequisites
    bootstrap-toolchain Install pinned emsdk
    fetch               Download + hash-verify all sources
    build-deps          Build dependencies
    configure           Run emcmake cmake configure for IfcOpenShell
    build               Build IfcOpenShell WASM target
    test                Verify artifacts and plugins
    package             Write clean dist directory
    clean               Clean build artifacts
    all                 Full pipeline (default for CI)
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Allow `python nix/wasm_native.py` direct invocation as well as
# `python -m nix.wasm_native`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nix import core, deps  # noqa: E402

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BUILD_ROOT = Path(
    os.environ.get("WASM_NATIVE_BUILD_ROOT", REPO_ROOT / "build" / "wasm-native")
)
CMAKE_DIR = REPO_ROOT / "cmake"

logger = logging.getLogger("wasm-native")


# ──────────────────────────────────────────────────────────────────────────────
# Full native build configuration
# ──────────────────────────────────────────────────────────────────────────────

DEPENDENCIES = (
    "boost",
    "eigen",
    "nlohmann_json",
    "occt",
    "gmp",
    "mpfr",
    "cgal",
    "manifold",
)

CMAKE_FLAGS = {
    "WITH_OPENCASCADE": "ON",
    "WITH_CGAL": "ON",
    "WITH_MANIFOLD": "ON",
    "CGAL_WITH_GMPXX": "Off",
    "GLTF_SUPPORT": "ON",
}

EXPECTED_PLUGINS = {
    "schema": ["ifc2x3", "ifc4", "ifc4x3_add2"],
    "kernel": [
        "passthrough",
        "opencascade",
        "cgal",
        "cgalsimple",
        "manifold",
    ],
    "tree": ["opencascade.brep", "opencascade.trianglebvh"],
    "mapping": ["ifc2x3", "ifc4", "ifc4x3_add2"],
    "document": [
        "xml.ifc2x3",
        "json.ifc2x3",
        "xml.ifc4",
        "json.ifc4",
        "xml.ifc4x3_add2",
        "json.ifc4x3_add2",
    ],
    "geometry_serializer": ["ttl", "obj", "glb", "stp", "igs", "svg"],
}

# Path helpers
# ──────────────────────────────────────────────────────────────────────────────


def toolchain_dir() -> Path:
    return BUILD_ROOT / "toolchain"


def downloads_dir() -> Path:
    return BUILD_ROOT / "downloads"


def src_dir() -> Path:
    return BUILD_ROOT / "src"


def build_subdir() -> Path:
    return BUILD_ROOT / "build"


def prefix_dir() -> Path:
    return BUILD_ROOT / "prefix"


def ifcopenshell_build_dir() -> Path:
    return BUILD_ROOT / "ifcopenshell"


def dist_dir() -> Path:
    return BUILD_ROOT / "dist"


def _resolved_toolchain_dir() -> Path:
    """Return the emsdk toolchain dir, honouring WASM_NATIVE_TOOLCHAIN."""
    external = os.environ.get("WASM_NATIVE_TOOLCHAIN")
    return Path(external) if external else toolchain_dir()


# ──────────────────────────────────────────────────────────────────────────────
# emsdk helpers
# ──────────────────────────────────────────────────────────────────────────────


def emsdk_env() -> dict[str, str]:
    """Return environment variables for emsdk activation.

    Respects WASM_NATIVE_TOOLCHAIN env var to use an externally managed emsdk.
    """
    return core.emsdk_env(_resolved_toolchain_dir())


def emsdk_binaries() -> dict[str, str]:
    """Return paths to key emsdk binaries."""
    return core.emsdk_binaries(_resolved_toolchain_dir())


# ──────────────────────────────────────────────────────────────────────────────
# Subcommands
# ──────────────────────────────────────────────────────────────────────────────


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check system prerequisites."""
    checks = {
        "cmake": "cmake --version",
        "git": "git --version",
        "python3": f"{sys.executable} --version",
        "make": "make --version",
        "patch": "patch --version",
        "tar": "tar --version",
        "unzip": "unzip -v",
    }

    results = {}
    all_ok = True
    for name, cmd in checks.items():
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=10,
            )
            version = (
                result.stdout.strip().split("\n")[0]
                if result.returncode == 0
                else "FAILED"
            )
            results[name] = (result.returncode == 0, version)
            if result.returncode != 0:
                all_ok = False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            results[name] = (False, "NOT FOUND")
            all_ok = False

    print("System Prerequisites Check:")
    print("=" * 60)
    for name, (ok, version) in results.items():
        status = "✓" if ok else "✗"
        print(f"  {status} {name:12s} {version}")

    print()
    if all_ok:
        print("All prerequisites satisfied.")
        return 0
    else:
        print("Some prerequisites are missing. Install them before proceeding.")
        return 1


def cmd_bootstrap_toolchain(args: argparse.Namespace) -> int:
    """Install pinned emsdk."""
    external = os.environ.get("WASM_NATIVE_TOOLCHAIN")
    if external:
        logger.info("Using external emsdk from WASM_NATIVE_TOOLCHAIN=%s", external)
        emsdk_env_file = Path(external) / "emsdk_env.sh"
        if not emsdk_env_file.exists():
            logger.error("emsdk_env.sh not found at %s", external)
            return 1
        return 0

    lock = core.load_lockfile()
    return core.bootstrap_emsdk(lock, toolchain_dir(), force=args.force)


def cmd_fetch(args: argparse.Namespace) -> int:
    """Download and hash-verify all sources."""
    lock = core.load_lockfile()

    results = core.fetch_sources(lock, DEPENDENCIES, downloads_dir())

    print("\nFetch Results:")
    print("=" * 40)
    for name, status in results.items():
        print(f"  {name:20s} {status}")

    return 0


def cmd_build_deps(args: argparse.Namespace) -> int:
    """Build dependencies."""
    lock = core.load_lockfile()

    # Ensure emsdk is available
    try:
        env = emsdk_env()
    except RuntimeError as e:
        logger.error("%s", e)
        return 1

    # Point shared deps module at our build root so intermediate build dirs
    # land inside build/wasm-native.
    deps.set_build_root(BUILD_ROOT)

    install_prefix = prefix_dir()
    for dep_name in DEPENDENCIES:
        if dep_name not in lock:
            raise KeyError(f"Dependency '{dep_name}' is missing from the lockfile")

        entry = lock[dep_name]
        logger.info("Building %s %s...", dep_name, entry["version"])

        # Fetch (no-op if already downloaded) and extract
        core.fetch_sources(lock, [dep_name], downloads_dir())
        src = core.extract_source(dep_name, lock, src_dir(), downloads_dir())

        if dep_name == "boost":
            deps.build_boost(src, install_prefix / "boost", env)
        elif dep_name == "eigen":
            deps.build_eigen(src, install_prefix / "eigen", env)
        elif dep_name == "nlohmann_json":
            deps.build_json(src, install_prefix / "nlohmann_json", env)
        elif dep_name == "gmp":
            deps.build_gmp(src, install_prefix / "gmp", env)
        elif dep_name == "mpfr":
            gmp_prefix = install_prefix / "gmp"
            deps.build_mpfr(src, install_prefix / "mpfr", gmp_prefix, env)
        elif dep_name == "cgal":
            gmp_prefix = install_prefix / "gmp"
            mpfr_prefix = install_prefix / "mpfr"
            boost_prefix = install_prefix / "boost"
            deps.build_cgal(
                src,
                install_prefix / "cgal",
                gmp_prefix,
                mpfr_prefix,
                env,
                boost_prefix=boost_prefix,
            )
        elif dep_name == "occt":
            deps.build_occt(src, install_prefix / "occt", env)
        elif dep_name == "manifold":
            deps.build_manifold(src, install_prefix / "manifold", env)
        else:
            raise ValueError(f"No build recipe for dependency '{dep_name}'")

    logger.info("All dependencies built.")
    return 0


def generate_cmake_flags() -> list[str]:
    """Generate CMake flags for IfcOpenShell WASM build."""
    install_prefix = prefix_dir()

    # Base flags
    flags = [
        "-DWASM_BUILD=ON",
        "-DBUILD_IFCAPI=ON",
        "-DBUILD_IFCGEOM=ON",
        "-DBUILD_IFCPYTHON=OFF",
        "-DBUILD_CONVERT=OFF",
        "-DBUILD_GEOMSERVER=OFF",
        "-DBUILD_EXAMPLES=OFF",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DCOLLADA_SUPPORT=OFF",
        "-DBoost_NO_BOOST_CMAKE=On",
        "-DCMAKE_BUILD_TYPE=MinSizeRel",
        f"-DPYTHON_EXECUTABLE={sys.executable}",
    ]

    for key, value in CMAKE_FLAGS.items():
        flags.append(f"-D{key}={value}")

    prefix_paths = []
    for dep_name in DEPENDENCIES:
        dep_prefix = install_prefix / dep_name
        if dep_prefix.exists():
            prefix_paths.append(str(dep_prefix))

    if prefix_paths:
        root_path = ";".join(prefix_paths)
        flags.append(f"-DCMAKE_FIND_ROOT_PATH={root_path}")
        flags.append("-DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY")
        flags.append("-DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY")
        flags.append("-DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY")
        flags.append("-DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER")

    # OCCT WASM dir
    occt_prefix = install_prefix / "occt"
    if occt_prefix.exists():
        flags.append(f"-DOPENCASCADE_WASM_DIR={occt_prefix}")

    return flags


def cmd_configure(args: argparse.Namespace) -> int:
    """Run emcmake cmake configure for IfcOpenShell."""
    build_dir = ifcopenshell_build_dir()
    build_dir.mkdir(parents=True, exist_ok=True)

    try:
        env = emsdk_env()
    except RuntimeError as e:
        logger.error("%s", e)
        return 1

    cmake_flags = generate_cmake_flags()
    cmake_cmd = ["emcmake", "cmake", str(CMAKE_DIR)] + cmake_flags

    logger.info("Configuring IfcOpenShell...")
    core.run(cmake_cmd, cwd=build_dir, env=env)

    logger.info("Configuration complete. Build directory: %s", build_dir)
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Build IfcOpenShell WASM target."""
    build_dir = ifcopenshell_build_dir()

    if not (build_dir / "CMakeCache.txt").exists():
        logger.error("Build not configured. Run 'configure' first.")
        return 1

    try:
        env = emsdk_env()
    except RuntimeError as e:
        logger.error("%s", e)
        return 1

    nproc = core.build_jobs()
    logger.info("Building IfcOpenShell WASM (jobs=%d)...", nproc)
    core.run(
        [
            "cmake",
            "--build",
            str(build_dir),
            "--target",
            "ifcopenshell_wasm",
            "ifcopenshell_wasm_node",
            "--parallel",
            str(nproc),
        ],
        env=env,
    )

    logger.info("Build complete.")
    return 0


_PLUGIN_KINDS = {
    "schema",
    "kernel",
    "tree",
    "mapping",
    "document",
    "geometry_serializer",
}


def _manifest_errors(manifest: dict[str, Any]) -> list[str]:
    errors = []
    unexpected_kinds = set(manifest) - _PLUGIN_KINDS
    for kind in sorted(unexpected_kinds):
        errors.append(f"Unexpected plugin kind: {kind}")

    for kind in sorted(_PLUGIN_KINDS):
        expected = set(EXPECTED_PLUGINS[kind])
        actual = set(manifest.get(kind, {}))
        for plugin_id in sorted(expected - actual):
            errors.append(f"Missing {kind} plugin: {plugin_id}")
        for plugin_id in sorted(actual - expected):
            errors.append(f"Unexpected {kind} plugin: {plugin_id}")
    return errors


def _manifest_plugin_paths(manifest: dict[str, Any]) -> list[Path]:
    paths = []
    for entries in manifest.values():
        for entry in entries.values():
            path = Path(entry["wasm"])
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Invalid plugin path in manifest: {path}")
            paths.append(path)
    return paths


def cmd_test(args: argparse.Namespace) -> int:
    """Verify artifacts and plugins."""
    build_dir = ifcopenshell_build_dir()

    wasm_dir = build_dir / "ifcwrap" / "wasm"
    plugins_json = wasm_dir / "ifcopenshell_plugins.json"

    if not plugins_json.exists():
        logger.error("Plugin manifest not found: %s", plugins_json)
        return 1

    with open(plugins_json) as f:
        manifest = json.load(f)

    errors = _manifest_errors(manifest)

    if errors:
        logger.error("Test failures:")
        for e in errors:
            logger.error("  - %s", e)
        return 1

    # Verify output artifacts exist
    artifacts = [
        "ifcopenshell_wasm.wasm",
        "ifcopenshell_wasm.mjs",
        "ifcopenshell_wasm.node.mjs",
        "ifcopenshell_api.mjs",
        "ifcopenshell_api.d.ts",
        "ifcopenshell_plugins.json",
    ]
    for name in artifacts:
        artifact_path = wasm_dir / name
        if not artifact_path.exists():
            errors.append(f"Missing artifact: {name}")

    # Verify plugin .wasm files exist
    plugins_dir = wasm_dir / "plugins"
    if plugins_dir.exists():
        expected_files = {
            (wasm_dir / path).resolve() for path in _manifest_plugin_paths(manifest)
        }
        actual_files = {path.resolve() for path in plugins_dir.glob("*.wasm")}
        if actual_files != expected_files:
            for path in sorted(expected_files - actual_files):
                errors.append(f"Missing plugin artifact: {path.name}")
            for path in sorted(actual_files - expected_files):
                errors.append(f"Unexpected plugin artifact: {path.name}")
        logger.info("Found %d plugin .wasm files", len(actual_files))
    else:
        errors.append("plugins/ directory missing")

    if errors:
        logger.error("Artifact verification failures:")
        for e in errors:
            logger.error("  - %s", e)
        return 1

    logger.info("All tests passed.")
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    """Write clean dist directory."""
    build_dir = ifcopenshell_build_dir()
    wasm_dir = build_dir / "ifcwrap" / "wasm"
    out = dist_dir()
    artifacts = [
        "ifcopenshell_wasm.wasm",
        "ifcopenshell_wasm.mjs",
        "ifcopenshell_wasm.node.mjs",
        "ifcopenshell_api.mjs",
        "ifcopenshell_api.d.ts",
        "ifcopenshell_plugins.json",
    ]

    missing = [name for name in artifacts if not (wasm_dir / name).is_file()]
    manifest = {}
    plugin_paths = []
    if not missing:
        with open(wasm_dir / "ifcopenshell_plugins.json") as f:
            manifest = json.load(f)
        manifest_errors = _manifest_errors(manifest)
        if manifest_errors:
            raise ValueError("Plugin manifest mismatch: " + "; ".join(manifest_errors))
        plugin_paths = _manifest_plugin_paths(manifest)
        missing.extend(
            str(path) for path in plugin_paths if not (wasm_dir / path).is_file()
        )
    if missing:
        raise FileNotFoundError(
            f"Cannot package incomplete WASM build; missing: {', '.join(missing)}"
        )

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    for name in artifacts:
        src = wasm_dir / name
        shutil.copy2(src, out / name)
        logger.info("Copied: %s", name)

    for path in plugin_paths:
        destination = out / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wasm_dir / path, destination)
    logger.info("Copied: %d manifest plugin(s)", len(plugin_paths))

    logger.info("Package written to %s", out)
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Clean build artifacts."""
    if BUILD_ROOT.exists():
        logger.info("Removing %s", BUILD_ROOT)
        shutil.rmtree(BUILD_ROOT)
        logger.info("Clean complete.")
    else:
        logger.info("Nothing to clean.")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    """Full pipeline (default for CI)."""
    steps = [
        ("doctor", cmd_doctor),
        ("bootstrap-toolchain", cmd_bootstrap_toolchain),
        ("fetch", cmd_fetch),
        ("build-deps", cmd_build_deps),
        ("configure", cmd_configure),
        ("build", cmd_build),
        ("test", cmd_test),
        ("package", cmd_package),
    ]

    for name, func in steps:
        logger.info("=" * 60)
        logger.info("Step: %s", name)
        logger.info("=" * 60)
        rc = func(args)
        if rc != 0:
            logger.error("Step '%s' failed with exit code %d", name, rc)
            return rc

    logger.info("Full pipeline completed successfully.")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Native WASM bootstrap build system for IfcOpenShell",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force reinstall/overwrite",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    sub.add_parser("doctor", help="Check system prerequisites")
    sub.add_parser("bootstrap-toolchain", help="Install pinned emsdk")
    sub.add_parser("fetch", help="Download + hash-verify all sources")
    sub.add_parser("build-deps", help="Build dependencies")
    sub.add_parser("configure", help="Run emcmake cmake configure")
    sub.add_parser("build", help="Build IfcOpenShell WASM target")
    sub.add_parser("test", help="Verify artifacts and plugins")
    sub.add_parser("package", help="Write clean dist directory")
    sub.add_parser("clean", help="Clean build artifacts")
    sub.add_parser("all", help="Full pipeline (default for CI)")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    commands = {
        "doctor": cmd_doctor,
        "bootstrap-toolchain": cmd_bootstrap_toolchain,
        "fetch": cmd_fetch,
        "build-deps": cmd_build_deps,
        "configure": cmd_configure,
        "build": cmd_build,
        "test": cmd_test,
        "package": cmd_package,
        "clean": cmd_clean,
        "all": cmd_all,
    }

    if not args.command:
        # Default to 'all' for CI
        args.command = "all"

    if args.command not in commands:
        parser.print_help()
        return 1

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
