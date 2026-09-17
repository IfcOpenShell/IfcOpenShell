#!/usr/bin/env python3
"""build-all-conan.py

Drop-in replacement for `nix/build-all.py` and `win/build-all.py`, driving
the conan-based build introduced in .conan2/.

It auto-detects the current OS to pick the matching conan host/build
profile from .conan2/profiles/, then runs `conan install` followed by
`conan build`.

Examples
--------
Native build on the current machine:
    python build-all-conan.py

Native build, static libs, Debug:
    python build-all-conan.py --static --build-type Debug

Cross-compile to Raspberry Pi from a Linux host:
    python build-all-conan.py --host-profile raspberrypi_host

Cross-compile to Emscripten:
    python build-all-conan.py --host-profile emscripten_host

Limit parallelism (default: cpu_count - 1, leaving one core free):
    python build-all-conan.py --jobs 4

Pass extra options straight through to conan (e.g. disable a feature):
    python build-all-conan.py -- -o "ifcopenshell/*:with_cgal=False"

By default the script makes sure conan itself is installed and satisfies the
version required by conanfile.py (installing/upgrading it via pip if
needed). Use --skip-conan-setup to skip that check (e.g. if you manage
conan yourself, via pipx or a system package).

It also installs the shared conan configuration (global.conf, remotes.json)
from .conan2/ into the conan home via `conan config install` before doing
anything else. Use --skip-conan-config to skip that, or --conan-config-dir
to point at a different folder.

Finally, it clones EstebanDugueperoux2's conan-center-index fork
(main branch, which carries an opencollada and openusd recipes
not yet merged upstream) and registers it as a conan "local-recipes-index"
remote: a recipe-only source (no prebuilt binaries) that conan builds from
source on demand, resolved like any other remote. Enabled by default
(with-conan-center-index-fork=True); pass --without-conan-center-index-fork to disable it.

When targeting the emscripten_host profile (only), it likewise clones
conan-io/conan-toolchains and registers it as a local-recipes-index
remote. Use --skip-conan-toolchains-remote to skip that, or
--conan-toolchains-repo/--conan-toolchains-remote-name to override it.
"""

from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILES_DIR = REPO_ROOT / ".conan2" / "profiles"
CONANFILE = REPO_ROOT / "conanfile.py"
# Folder holding the shared conan config (global.conf, remotes.json, ...)
# installed into the conan home with `conan config install`.
CONAN_CONFIG_DIR = REPO_ROOT / ".conan2"
# Fallback if conanfile.py's required_conan_version can't be parsed.
DEFAULT_MIN_CONAN_VERSION = "2.1"
# Leave one core free by default so the build doesn't hog the whole machine.
DEFAULT_JOBS = max(1, (os.cpu_count() or 2) - 1)

# Fork/branch carrying an OpenCOLLADA and openusd recipes not yet merged into the
# official conan-center-index. Cloned locally and registered as a
# "local-recipes-index" remote (recipe-only, no binaries) — requires
# conan >= 2.7.
CONAN_CENTER_INDEX_FORK_NAME = "estebandugueperoux2-conan-center-index-fork"
CONAN_CENTER_INDEX_FORK_REPO = "https://github.com/EstebanDugueperoux2/conan-center-index.git"
CONAN_CENTER_INDEX_FORK_BRANCH = "main"
CLONE_DIR = REPO_ROOT / ".conan-recipes" / "conan-center-index"

# conan-io/conan-toolchains carries recipes/toolchains needed for Emscripten
# builds; only relevant (and only registered) when targeting that profile.
CONAN_TOOLCHAINS_REMOTE_NAME = "conan-toolchains"
CONAN_TOOLCHAINS_REPO = "https://github.com/conan-io/conan-toolchains.git"
CONAN_TOOLCHAINS_CLONE_DIR = REPO_ROOT / ".conan-recipes" / "conan-toolchains"
EMSCRIPTEN_PROFILE_NAME = "emscripten_host"

# Map Python's platform.system() to the matching *_host profile shipped in
# .conan2/profiles/. Only "native" targets are auto-detected; cross targets
# (raspberrypi_host, emscripten_host) must be requested explicitly with
# --host-profile since they cannot be inferred from the build machine.
_OS_TO_PROFILE = {
    "Linux": "linux_host",
    "Darwin": "macos_host",
    "Windows": "windows_host",
}


def detect_native_profile() -> str:
    system = platform.system()
    try:
        return _OS_TO_PROFILE[system]
    except KeyError:
        raise SystemExit(
            f"Unsupported/undetected OS '{system}'. "
            f"Pass --host-profile/--build-profile explicitly "
            f"(available: {', '.join(sorted(p.name for p in PROFILES_DIR.iterdir()))})."
        )


def resolve_profile(name: str) -> Path:
    profile_path = PROFILES_DIR / name
    if not profile_path.is_file():
        available = ", ".join(sorted(p.name for p in PROFILES_DIR.iterdir() if p.is_file()))
        raise SystemExit(f"Profile '{name}' not found in {PROFILES_DIR} (available: {available})")
    return profile_path


def run(cmd: list[str]) -> None:
    print(f"+ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def _parse_version(text: str) -> tuple[int, ...]:
    match = re.search(r"(\d+(?:\.\d+)+)", text)
    if not match:
        raise ValueError(f"Could not parse a version number out of {text!r}")
    return tuple(int(part) for part in match.group(1).split("."))


def minimum_conan_version() -> str:
    """Read the `>=X.Y` lower bound out of conanfile.py's required_conan_version."""
    if CONANFILE.is_file():
        contents = CONANFILE.read_text(encoding="utf-8")
        match = re.search(r'required_conan_version\s*=\s*["\']>=\s*([\d.]+)', contents)
        if match:
            return match.group(1)
    return DEFAULT_MIN_CONAN_VERSION


def installed_conan_version() -> tuple[int, ...] | None:
    try:
        result = subprocess.run(["conan", "--version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    try:
        return _parse_version(result.stdout)
    except ValueError:
        return None


def ensure_conan_installed(min_version: str) -> None:
    """Install conan via pip if missing, or upgrade it if older than min_version."""
    current = installed_conan_version()
    required = _parse_version(min_version)

    if current is None:
        print(f"conan not found, installing conan>={min_version} via pip...", flush=True)
        run([sys.executable, "-m", "pip", "install", "--upgrade", f"conan>={min_version}"])
        return

    current_str = ".".join(str(part) for part in current)
    if current < required:
        print(
            f"conan {current_str} is older than the required {min_version}, " f"upgrading via pip...",
            flush=True,
        )
        run([sys.executable, "-m", "pip", "install", "--upgrade", f"conan>={min_version}"])
    else:
        print(f"conan {current_str} already satisfies >={min_version}", flush=True)


def ensure_conan_config_installed(config_dir: Path) -> None:
    """Install shared conan config (global.conf, remotes.json, ...) from
    config_dir into the active conan home via `conan config install`."""
    run(["conan", "config", "install", str(config_dir)])


def clone_or_update_repo(repo_url: str, dest: Path, branch: str | None = None) -> None:
    if not shutil.which("git"):
        raise SystemExit(f"git is required to clone {repo_url}, but was not found.")
    if dest.is_dir():
        if branch:
            run(["git", "-C", str(dest), "fetch", "--depth", "1", "origin", branch])
        else:
            run(["git", "-C", str(dest), "fetch", "--depth", "1", "origin"])
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["git", "clone", "--depth", "1"]
        if branch:
            cmd += ["--branch", branch]
        cmd += [repo_url, str(dest)]
        run(cmd)


def ensure_local_recipes_index_remote(
    remote_name: str, repo_url: str, clone_dir: Path, branch: str | None = None
) -> None:
    """Clone a git repo of conan recipes and register it as a recipe-only
    `local-recipes-index` remote (conan builds from source on demand; no
    binaries are ever fetched from it)."""
    print(f"Fetching {repo_url}" + (f"@{branch}" if branch else "") + "...", flush=True)
    clone_or_update_repo(repo_url, clone_dir, branch)

    run(
        [
            "conan",
            "remote",
            "add",
            remote_name,
            str(clone_dir),
            "--type=local-recipes-index",
        ]
    )


def main() -> None:
    native_profile = None
    try:
        native_profile = detect_native_profile()
    except SystemExit:
        # Defer the hard failure until we know the user didn't override both
        # profiles explicitly; argparse defaults below handle that.
        pass

    parser = argparse.ArgumentParser(
        description="Build IfcOpenShell with conan, auto-selecting the profile for the current OS.",
    )
    parser.add_argument(
        "--host-profile",
        default=native_profile,
        help=f"conan host profile name under .conan2/profiles/ (default: auto-detected, "
        f"currently '{native_profile}' on this machine)",
    )
    parser.add_argument(
        "--build-profile",
        default=None,
        help="conan build profile name under .conan2/profiles/ "
        "(default: same as the native profile for this machine; use this to keep "
        "the build machine's toolchain when cross-compiling with --host-profile)",
    )
    parser.add_argument(
        "--build-type",
        default="Release",
        help="CMake build type, forwarded as -s build_type=... (default: Release)",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=DEFAULT_JOBS,
        help=f"Max parallel build jobs, forwarded as -c tools.build:jobs=... "
        f"(default: {DEFAULT_JOBS}, i.e. cpu_count-1 on this machine; use the "
        f"detected cpu_count ({os.cpu_count() or 'unknown'}) to build flat out)",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Build static libraries instead of the default shared build "
        "(note: Qt-based targets like BonsaiViewer don't run when built static)",
    )
    parser.add_argument(
        "--build-missing",
        action="store_true",
        default=True,
        help="Pass --build=missing to 'conan install' (default: on)",
    )
    parser.add_argument(
        "--no-build-missing",
        dest="build_missing",
        action="store_false",
        help="Do not pass --build=missing to 'conan install'",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip 'conan install' and only run 'conan build' (dependencies must already be resolved)",
    )
    parser.add_argument(
        "--skip-conan-setup",
        action="store_true",
        help="Don't check/install/upgrade conan itself before building",
    )
    parser.add_argument(
        "--conan-version",
        default=None,
        help="Minimum conan version to enforce (default: parsed from conanfile.py's "
        "required_conan_version, falling back to " + DEFAULT_MIN_CONAN_VERSION + ")",
    )
    parser.add_argument(
        "--skip-conan-config",
        action="store_true",
        help="Don't run 'conan config install' to apply global.conf/remotes.json before building",
    )
    parser.add_argument(
        "--conan-config-dir",
        default=str(CONAN_CONFIG_DIR),
        help=f"Folder passed to 'conan config install' (global.conf, remotes.json, ...) "
        f"(default: {CONAN_CONFIG_DIR})",
    )
    parser.add_argument(
        "--with-conan-center-index-fork",
        dest="with_conan_center_index_fork",
        action="store_true",
        default=True,
        help="Enable with_collada and register the OpenCOLLADA fork as a local-recipes-index "
        "remote before installing (default: on)",
    )
    parser.add_argument(
        "--without-conan-center-index-fork",
        dest="with_conan_center_index_fork",
        action="store_false",
        help="Disable with_collada and skip registering the OpenCOLLADA fork remote",
    )
    parser.add_argument(
        "--skip-conan-toolchains-remote",
        action="store_true",
        help=f"Don't clone/register the conan-toolchains remote when targeting "
        f"{EMSCRIPTEN_PROFILE_NAME} (use if it's already registered, e.g. by CI)",
    )
    parser.add_argument(
        "--conan-toolchains-remote-name",
        default=CONAN_TOOLCHAINS_REMOTE_NAME,
        help=f"Name to register the conan-toolchains local-recipes-index remote under "
        f"(default: {CONAN_TOOLCHAINS_REMOTE_NAME})",
    )
    parser.add_argument(
        "--conan-toolchains-repo",
        default=CONAN_TOOLCHAINS_REPO,
        help=f"Git URL of the conan-toolchains repo (default: {CONAN_TOOLCHAINS_REPO})",
    )
    parser.add_argument(
        "conan_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments forwarded verbatim to both conan invocations "
        "(prefix with '--' e.g. 'build-all-conan.py -- -o \"*/*:with_cgal=False\"')",
    )
    args = parser.parse_args()

    if not args.skip_conan_setup:
        ensure_conan_installed(args.conan_version or minimum_conan_version())

    if not args.skip_conan_config:
        ensure_conan_config_installed(Path(args.conan_config_dir))

    if not args.host_profile:
        raise SystemExit("Could not auto-detect a profile for this OS; pass --host-profile explicitly.")

    host_profile = resolve_profile(args.host_profile)
    # When cross-compiling, the build profile defaults to the *native*
    # profile of the machine actually running conan (not the host profile).
    build_profile_name = args.build_profile or native_profile or args.host_profile
    build_profile = resolve_profile(build_profile_name)

    extra_args = args.conan_args
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]

    if args.with_conan_center_index_fork:
        ensure_local_recipes_index_remote(
            remote_name=CONAN_CENTER_INDEX_FORK_NAME,
            repo_url=CONAN_CENTER_INDEX_FORK_REPO,
            clone_dir=CLONE_DIR,
            branch=CONAN_CENTER_INDEX_FORK_BRANCH,
        )

    if host_profile.name == EMSCRIPTEN_PROFILE_NAME and not args.skip_conan_toolchains_remote:
        ensure_local_recipes_index_remote(
            remote_name=args.conan_toolchains_remote_name,
            repo_url=args.conan_toolchains_repo,
            clone_dir=CONAN_TOOLCHAINS_CLONE_DIR,
        )

    shared_opt = f"*/*:shared={'False' if args.static else 'True'}"

    common_args = [
        "-pr:h",
        str(host_profile),
        "-pr:b",
        str(build_profile),
        "-s",
        f"build_type={args.build_type}",
        "-o",
        shared_opt,
        "-c",
        f"tools.build:jobs={args.jobs}",
        *extra_args,
    ]

    print(f"Host profile:  {host_profile.name}")
    print(f"Build profile: {build_profile.name}")
    print(f"Build type:    {args.build_type}")
    print(f"Shared:        {not args.static}")
    print(f"Jobs:          {args.jobs}")

    if not args.skip_install:
        install_cmd = ["conan", "install", "."] + common_args
        if args.build_missing:
            install_cmd.append("--build=missing")
        run(install_cmd)

    build_cmd = ["conan", "build", "."] + common_args
    run(build_cmd)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
