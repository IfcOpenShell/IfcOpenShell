# /// script
# [tool.ty.environment]
# root = ["."]
# ///
###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################
#
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

from common import (
    REPO_ROOT,
    SCRIPT_DIR,
    BuildCfg,
    BuildDepsCache,
    BuildType,
    debug_or_release,
    logger,
    require_command,
    run,
    run_streamed,
)
from vs_cfg import CMAKE_GENERATORS, VS_TOOLSET_TO_VS_VER, VsCfgResult, get_vs_var


def build_cfg_marker_filepath(dependency_install_dir: Path, build_cfg: BuildCfg) -> Path:
    return dependency_install_dir / f".{debug_or_release(build_cfg).lower()}_installation"


def is_already_installed(dependency_install_dir: Path, *, expected_build_cfg: BuildCfg | None = None) -> bool:
    if not dependency_install_dir.exists():
        return False

    if expected_build_cfg is not None:
        marker_filepath = build_cfg_marker_filepath(dependency_install_dir, expected_build_cfg)
        if not marker_filepath.exists():
            return False

    logger.info(f"Found existing '{dependency_install_dir}', skipping")
    return True


def mark_installation(installation_dir: Path, build_cfg: BuildCfg) -> None:
    if not installation_dir.exists():
        logger.error(f"Directory '{installation_dir}' does not exist.")
        sys.exit(1)

    marker_filepath = build_cfg_marker_filepath(installation_dir, build_cfg)
    if marker_filepath.exists():
        return

    logger.info(f"Marking installation in '{installation_dir}' with '{marker_filepath.name}'.")
    marker_filepath.touch()


def download_file(log_dependency_name: str, url: str, destination: Path) -> None:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        logger.info(f"{log_dependency_name} already downloaded. Skipping.")
        return

    logger.info(f"Downloading {log_dependency_name} into '{destination.parent}'")
    urlretrieve(url, destination)


def extract_file(log_dependency_name: str, filename: Path, destination_dir: Path, dir_after_extraction: Path) -> None:
    if dir_after_extraction.exists():
        logger.info(f"{log_dependency_name} already extracted into '{dir_after_extraction}'. Skipping.")
        return

    logger.info(f"Extracting {log_dependency_name} into '{destination_dir}' from '{filename}'.")
    sevenzip = require_command("7z")
    subprocess.check_call([sevenzip, "x", "-bso0", "-bsp0", str(filename), f"-o{destination_dir}"])
    # TODO: assert that dir_after_extraction exists


def git_clone_and_checkout_revision(
    log_dependency_name: str,
    git_url: str,
    dest_dir: Path,
    revision: str | None = None,
) -> None:
    if dest_dir.exists():
        logger.info(f"Cloning {log_dependency_name} is already cloned.")
        return

    logger.info(f"Cloning {log_dependency_name} into '{dest_dir}'.")
    run_streamed("git", "clone", git_url, str(dest_dir))

    if revision:
        run_streamed("git", "fetch", cwd=dest_dir)
        logger.info(f"Checking out {log_dependency_name} revision {revision}.")
        run_streamed("git", "reset", "--hard", cwd=dest_dir)
        run_streamed("git", "checkout", revision, cwd=dest_dir)


def run_cmake(
    log_dependency_name: str,
    dependency_dir: Path,
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    *extra_args: str,
    env: dict[str, str] | None = None,
) -> None:
    logger.info(f"Running CMake for {log_dependency_name}.")

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_path.mkdir(parents=True, exist_ok=True)

    # TODO make deleting cache a parameter for this subroutine? We probably want to delete the
    # cache always e.g. when we've had new changes in the repository.
    cmake_cache_path = build_path / "CMakeCache.txt"
    if build_type == "Rebuild" and cmake_cache_path.exists():
        cmake_cache_path.unlink()

    run_streamed(
        "cmake",
        "..",
        "-G",
        vs_cfg_vars.generator.name,
        "-A",
        vs_cfg_vars.vs_platform,
        *extra_args,
        cwd=build_path,
        env=env,
    )


def build_cmake_project(
    log_dependency_name: str,
    build_dir: Path,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    logger.info(f"Building {log_dependency_name}. Please be patient, this will take a while.")

    run_streamed("cmake", "--build", ".", "--config", build_cfg, "--", *msbuild_multiproc, cwd=build_dir)


def install_cmake_project(log_dependency_name: str, build_dir: Path, build_cfg: BuildCfg) -> None:
    logger.info(f"Installing {log_dependency_name} ({build_cfg}). Please be patient, this may take a while.")

    run_streamed("cmake", "--install", ".", "--config", build_cfg, cwd=build_dir)


def build_solution(
    log_dependency_name: str,
    msbuild_cmd: tuple[str, ...],
    solution_path: Path,
    build_cfg: BuildCfg,
    vs_platform: str,
    build_type: BuildType,
    target: str | None = None,
    compile_with_wpo: bool = False,
) -> None:
    if target is None:
        msbuild_target = build_type
    elif build_type == "Build":
        msbuild_target = target
    else:
        msbuild_target = f"{target}:{build_type}"

    logger.info(f"Building {msbuild_target} of {log_dependency_name}. Please be patient, this will take a while.")

    # Whole program optimization avoids Visual C++ hanging when compiling 32-bit release OCCT up to version 7.4.0.
    properties = f"configuration={build_cfg};platform={vs_platform}"
    if compile_with_wpo:
        properties += ";WholeProgramOptimization=TRUE"

    run_streamed(*msbuild_cmd, str(solution_path), f"/p:{properties}", f"/t:{msbuild_target}")


def install_json(install_dir: Path) -> None:
    # TODO: sync it with build-all
    JSON_VERSION = "3.6.1"
    DEPENDENCY_NAME = f"json-{JSON_VERSION}"
    download_file(
        DEPENDENCY_NAME,
        f"https://github.com/nlohmann/json/releases/download/v{JSON_VERSION}/json.hpp",
        install_dir / "json" / "nlohmann" / "json.hpp",
    )


def install_nuget(deps_dir: Path) -> Path:
    NUGET_VERSION = "6.14.0"
    DEPENDENCY_NAME = "nuget"

    nuget_in_path = shutil.which("nuget")
    if nuget_in_path:
        logger.info("Found existing nuget in PATH. Skipping.")
        return Path(nuget_in_path)

    nuget_exe = deps_dir / f"nuget-{NUGET_VERSION}" / "nuget.exe"
    download_file(
        DEPENDENCY_NAME,
        f"https://dist.nuget.org/win-x86-commandline/v{NUGET_VERSION}/nuget.exe",
        nuget_exe,
    )
    return nuget_exe


def install_ccache(deps_dir: Path, nuget_exe: Path, build_deps_cache: BuildDepsCache) -> Path:
    CCACHE_VERSION = "4.12.1"
    DEPENDENCY_NAME = "ccache"
    ccache_install_dir = deps_dir / f"{DEPENDENCY_NAME}.{CCACHE_VERSION}" / "tools"

    if shutil.which("ccache"):
        logger.info("Found existing ccache in PATH. Skipping.")
        return ccache_install_dir

    build_deps_cache.add_entry("CCACHE_INSTALL_DIR", str(ccache_install_dir))

    if ccache_install_dir.exists():
        logger.info(f"Found existing '{ccache_install_dir}', skipping")
        return ccache_install_dir

    run(str(nuget_exe), "install", "ccache", "-Version", CCACHE_VERSION, "-OutputDirectory", str(deps_dir))
    return ccache_install_dir


def install_boost(
    vs_cfg_vars: VsCfgResult,
    build_deps_cache: BuildDepsCache,
    build_cfg: BuildCfg,
    ifcos_num_build_procs: int,
    reuse_boost: bool,
) -> None:
    # NOTE Boost < 1.64 doesn't work without tricks if the user has only VS 2017 installed and no earlier versions.
    BOOST_VERSION = "1.92.0"
    DEPENDENCY_NAME = f"Boost {BOOST_VERSION}"

    dependency_dir = vs_cfg_vars.deps_dir / f"boost-{BOOST_VERSION}"
    dependency_install_dir = dependency_dir / "stage" / vs_cfg_vars.gen_shorthand

    # Remove leftover dir from before the switch to the archive's actual top-level folder naming.
    # TODO: remove it a bit later.
    old_dependency_dir = vs_cfg_vars.deps_dir / f"boost_{BOOST_VERSION.replace('.', '_')}"
    if old_dependency_dir.exists():
        logger.info(f"Removing outdated '{old_dependency_dir}'.")
        shutil.rmtree(old_dependency_dir)

    build_deps_cache.add_entry("BOOST_INSTALL_DIR", str(dependency_install_dir))

    # NOTE Boost is fast to build with a limited set of libraries, so it's rebuilt by default.
    if reuse_boost and is_already_installed(dependency_install_dir, expected_build_cfg=build_cfg):
        return

    BOOST_ZIP = f"boost-{BOOST_VERSION}-b2-nodocs.7z"

    download_file(
        DEPENDENCY_NAME,
        f"https://github.com/boostorg/boost/releases/download/boost-{BOOST_VERSION}/{BOOST_ZIP}",
        vs_cfg_vars.deps_dir / BOOST_ZIP,
    )

    extract_file(
        DEPENDENCY_NAME,
        vs_cfg_vars.deps_dir / BOOST_ZIP,
        vs_cfg_vars.deps_dir,
        dependency_dir,
    )

    # Build Boost build script
    if not (dependency_dir / "project-config.jam").exists():
        boost_css = dependency_dir / "boost.css"
        if not boost_css.exists():
            logger.error(f"'{boost_css}' not found.")
            sys.exit(1)
        logger.info("Building Boost build script.")
        run_streamed(
            str(dependency_dir / "bootstrap.bat"), vs_cfg_vars.generator.boost_bootstrap_ver, cwd=dependency_dir
        )

    # TODO: this means that 'arm' and 'win32' platforms are not actually supported
    # and can be dropped.
    if vs_cfg_vars.is_vs_platform("x64"):
        B2_ARCH_FEATURE = "x86"
    elif vs_cfg_vars.is_vs_platform("ARM64"):
        B2_ARCH_FEATURE = "arm"
    else:
        logger.error("Failed to identify architecture")
        sys.exit(1)

    BOOST_LIBS = (
        "--with-system",
        "--with-program_options",
        "--with-regex",
        "--with-thread",
        "--with-date_time",
        "--with-iostreams",
        "--with-filesystem",
    )

    logger.info(f"Building {DEPENDENCY_NAME} {' '.join(BOOST_LIBS)}. Please be patient, this will take a while.")

    project_cache_jam = dependency_dir / "bin.v2" / "project-cache.jam"
    if project_cache_jam.exists():
        project_cache_jam.unlink()

    run_streamed(
        str(dependency_dir / "b2.exe"),
        f"toolset={vs_cfg_vars.boost_toolset}",
        f"architecture={B2_ARCH_FEATURE}",
        f"address-model={vs_cfg_vars.arch_bits}",
        "--abbreviate-paths",
        f"-j{ifcos_num_build_procs}",
        f"variant={debug_or_release(build_cfg).lower()}",
        *BOOST_LIBS,
        "stage",
        f"--stagedir={dependency_install_dir}",
        cwd=dependency_dir,
    )

    mark_installation(dependency_install_dir, build_cfg)


def install_opencollada(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    DEPENDENCY_NAME = "OpenCOLLADA"
    dependency_dir = deps_dir / "OpenCOLLADA"

    # TODO: we probably can install
    # Always clone it, even if it's installed, because it contains xml headers we need.
    # Use a fixed revision in order to prevent introducing breaking changes
    # TODO: commit is almost 3 years behind the latest version used in nix/build-all.py, need to test and bump.
    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://github.com/KhronosGroup/OpenCOLLADA.git",
        dependency_dir,
        "064a60b65c2c31b94f013820856bc84fb1937cc6",
    )

    if is_already_installed(install_dir / DEPENDENCY_NAME, expected_build_cfg=build_cfg):
        return

    # TODO: add git reset and apply patches more cleanly.

    # Debug build of OpenCOLLADAValidator fails (https://github.com/KhronosGroup/OpenCOLLADA/issues/377) so
    # disable it from the build altogether as we have no use for it.
    if "#add_subdirectory(COLLADAValidator)" not in (dependency_dir / "CMakeLists.txt").read_text():
        run_streamed(
            "git",
            "apply",
            "--reject",
            "--whitespace=fix",
            str(SCRIPT_DIR / "patches" / "OpenCOLLADA_CMakeLists.txt.patch"),
            "--ignore-whitespace",
            cwd=dependency_dir,
        )

    # std::tr1::unordered_map was a legacy MSVC compatibility shim kept around through VS2022's STL, but newer
    # toolsets (e.g. VS2026/v145) no longer provide it, breaking the build with error C2039: 'tr1' is not a member of 'std'.
    common_f_write_buffer_flusher = dependency_dir / "common" / "libBuffer" / "include" / "CommonFWriteBufferFlusher.h"
    if (
        "typedef std::unordered_map<MarkId, FilePosType > MarkIdToFilePos;"
        not in common_f_write_buffer_flusher.read_text()
    ):
        run_streamed(
            "git",
            "apply",
            "--reject",
            "--whitespace=fix",
            str(REPO_ROOT / "nix" / "patches" / "opencollada" / "remove_tr1.patch"),
            "--ignore-whitespace",
            cwd=dependency_dir,
        )

    dependency_install_dir = install_dir / DEPENDENCY_NAME

    # TODO: inconsistency with nix/build-all - there we prepare pcre and libxml2 separately,
    # while here we rely on the versions bundled with the OpenCOLLADA repo (Externals/pcre,
    # Externals/LibXML). Worth reconciling at some point.
    #
    # NOTE Enforce that the embedded LibXml2 and PCRE are used as there might be problems with
    # arbitrary versions of the libraries.
    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DUSE_STATIC_MSVC_RUNTIME=0",
        "-DCMAKE_DEBUG_POSTFIX=d",
        "-DLIBXML2_LIBRARIES=",
        "-DLIBXML2_INCLUDE_DIR=",
        "-DPCRE_INCLUDE_DIR=",
        "-DPCRE_LIBRARIES=",
        # OpenCOLLADA is ancient at this point and allows cmake 2.6+, which results in an error
        # in cmake 4, so we override the minimum cmake version.
        "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
    )

    # OpenCOLLADA's vcxproj files only define Debug/Release configurations (no RelWithDebInfo/MinSizeRel).
    debug_or_release_cfg = debug_or_release(build_cfg)
    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, debug_or_release_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, debug_or_release_cfg)

    mark_installation(dependency_install_dir, build_cfg)


def install_occt(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_deps_cache: BuildDepsCache,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    OCCT_VERSION = "7.8.1"
    OCCT_VER = f"V{OCCT_VERSION.replace('.', '_')}"

    DEPENDENCY_NAME = f"Open CASCADE {OCCT_VERSION}"
    # TODO: `new-layout` suffix can be dropped on the next OCCT version update, it's only needed
    # to separate the legacy layout installation (used by version 7.8.1) from the new one.
    new_layout_suffix = "-new-layout" if OCCT_VERSION == "7.8.1" else ""
    OCCT_DEPENDENCY_INSTALL_NAME = f"opencascade-{OCCT_VERSION}{new_layout_suffix}"
    dependency_install_dir = install_dir / OCCT_DEPENDENCY_INSTALL_NAME

    build_deps_cache.add_entry("OCC_INSTALL_DIR", str(dependency_install_dir))

    if is_already_installed(dependency_install_dir, expected_build_cfg=build_cfg):
        return

    dependency_dir = deps_dir / "occt_git"
    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://github.com/Open-Cascade-SAS/OCCT",
        dependency_dir,
        OCCT_VER,
    )

    # Patching always blindly would trigger a rebuild each time.
    cmake_lists_path = dependency_dir / "CMakeLists.txt"
    # TODO: probably can use `git apply --reverse --check` for better validation.
    if "IfcOpenShell" not in cmake_lists_path.read_text():
        run_streamed(
            "git",
            "apply",
            "--ignore-whitespace",
            str(SCRIPT_DIR / "patches" / f"{OCCT_VER}.patch"),
            cwd=dependency_dir,
        )
        assert "IfcOpenShell" in cmake_lists_path.read_text()

    # TODO: remove CMAKE_DEBUG_POSTFIX setting later.
    # Temporarily explicitly set `CMAKE_DEBUG_POSTFIX` to empty to override it's previously being set to `d`.
    # OCCT don't need it, since it's layout is separating debug and release build by different folders.
    #
    # OCCT 7.8.1 we're using is becoming old and it was targeting cmake 3.1+.
    # To make it buildable on cmake 4, we override policy version, but it may have some quirks in the future
    # and we may consider version bump.
    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DBUILD_LIBRARY_TYPE=Static",
        "-DCMAKE_DEBUG_POSTFIX=",
        "-DBUILD_MODULE_Draw=0",
        "-DBUILD_RELEASE_DISABLE_EXCEPTIONS=OFF",
        "-DUSE_XLIB=OFF",
        "-DUSE_FREETYPE=OFF",
        "-DUSE_OPENGL=OFF",
        "-DUSE_GLES2=OFF",
        "-DBUILD_USE_PCH=ON",
        "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
    )

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)

    # Fix upstream bug in cmake config file with unescaped quotes preventing configuration.
    # The issue is fixed in 7.9.0+.
    # See https://github.com/Open-Cascade-SAS/OCCT/pull/373
    occt_config_cmake = dependency_install_dir / "cmake" / "OpenCASCADEConfig.cmake"
    occt_config_cmake.write_text(re.sub(r'/wd"(\d+)"', r"/wd\1", occt_config_cmake.read_text()))

    mark_installation(dependency_install_dir, build_cfg)


def install_proj(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    PROJ_VERSION = "9.4.1"

    if is_already_installed(install_dir / f"proj-{PROJ_VERSION}"):
        return

    def install_sqlite3() -> None:
        DEPENDENCY_NAME = "sqlite3"
        SQLITE_VERSION = "3430100"

        (install_dir / "sqlite3" / "lib").mkdir(parents=True, exist_ok=True)
        (install_dir / "sqlite3" / "bin").mkdir(parents=True, exist_ok=True)
        (install_dir / "sqlite3" / "include").mkdir(parents=True, exist_ok=True)

        download_file(
            DEPENDENCY_NAME,
            f"https://www.sqlite.org/2023/sqlite-amalgamation-{SQLITE_VERSION}.zip",
            deps_dir / f"sqlite-amalgamation-{SQLITE_VERSION}.zip",
        )

        extract_file(
            DEPENDENCY_NAME,
            deps_dir / f"sqlite-amalgamation-{SQLITE_VERSION}.zip",
            deps_dir,
            deps_dir / f"sqlite-amalgamation-{SQLITE_VERSION}",
        )

        sqlite_dir = deps_dir / f"sqlite-amalgamation-{SQLITE_VERSION}"
        run("cl", "/c", "sqlite3.c", cwd=sqlite_dir)
        run("lib", f"/OUT:{install_dir / 'sqlite3' / 'lib' / 'sqlite3.lib'}", "sqlite3.obj", cwd=sqlite_dir)
        run(
            "cl",
            "sqlite3.c",
            "shell.c",
            "/link",
            f"/out:{install_dir / 'sqlite3' / 'bin' / 'sqlite3.exe'}",
            cwd=sqlite_dir,
        )
        os.environ["PATH"] += os.pathsep + str(install_dir / "sqlite3" / "bin")
        shutil.copy(sqlite_dir / "sqlite3.h", install_dir / "sqlite3" / "include")

    def _install_proj() -> None:
        DEPENDENCY_NAME = "proj"
        dependency_dir = deps_dir / f"proj-{PROJ_VERSION}"

        download_file(
            DEPENDENCY_NAME,
            f"https://download.osgeo.org/proj/proj-{PROJ_VERSION}.zip",
            deps_dir / f"proj-{PROJ_VERSION}.zip",
        )

        extract_file(
            DEPENDENCY_NAME,
            deps_dir / f"proj-{PROJ_VERSION}.zip",
            deps_dir,
            dependency_dir,
        )

        run_cmake(
            DEPENDENCY_NAME,
            dependency_dir,
            vs_cfg_vars,
            build_type,
            f'-DCMAKE_INSTALL_PREFIX={install_dir / f"proj-{PROJ_VERSION}"}',
            f'-DCMAKE_PREFIX_PATH={install_dir / "sqlite3"}',
            f'-DSQLite3_INCLUDE_DIR={install_dir / "sqlite3" / "include"}',
            f'-DSQLite3_LIBRARY={install_dir / "sqlite3" / "lib" / "sqlite3.lib"}',
            "-DENABLE_TIFF=OFF",
            "-DENABLE_CURL=OFF",
            "-DBUILD_PROJSYNC=OFF",
            "-DBUILD_SHARED_LIBS=OFF",
            "-DBUILD_TESTING=OFF",
        )

        build_path = dependency_dir / vs_cfg_vars.build_dir
        build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
        install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)

    install_sqlite3()
    _install_proj()


def install_mpir(vs_cfg_vars: VsCfgResult, deps_dir: Path, install_dir: Path, build_cfg: BuildCfg) -> None:
    DEPENDENCY_NAME = "mpir"
    # `mpfr` depends on relative path `..\mpir\config.h`, so dependency name should match exactly.
    dependency_dir = deps_dir / "mpir"

    if is_already_installed(install_dir / "mpir"):
        return

    git_clone_and_checkout_revision(DEPENDENCY_NAME, "https://github.com/Andrej730/mpir-vs2026.git", dependency_dir)
    run_streamed("git", "reset", "--hard", cwd=dependency_dir)
    run_streamed("git", "clean", "-fdx", cwd=dependency_dir)

    ucrt_version = get_vs_var("UCRTVersion")
    mpir_patch = (SCRIPT_DIR / "patches" / "mpir.patch").read_text()
    for project_name in ("lib_mpir_cxx", "lib_mpir_gc"):
        patch = mpir_patch.replace("sdk", ucrt_version).replace("fn", project_name)
        logger.info(f"Applying mpir patch for {project_name}.")
        subprocess.run(
            ["git", "apply", "--unidiff-zero", "--ignore-whitespace"],
            input=patch,
            text=True,
            cwd=dependency_dir,
            check=True,
        )

    run_streamed(
        "git",
        "apply",
        str(SCRIPT_DIR / "patches" / "mpir_runtime.patch"),
        "--unidiff-zero",
        "--ignore-whitespace",
        cwd=dependency_dir,
    )

    if vs_cfg_vars.is_vs_platform("ARM64"):
        logger.info("Applying ARM64 patches for mpir.")
        run_streamed(
            "git",
            "apply",
            str(SCRIPT_DIR / "patches" / "mpir-arm64-changes.patch"),
            "--unidiff-zero",
            "--ignore-whitespace",
            cwd=dependency_dir,
        )

    vs_ver_short = str(vs_cfg_vars.generator.vs_ver)[2:]
    msvc_dir = dependency_dir / "msvc" / f"vs{vs_ver_short}"
    # mpir's vcxproj files only define Debug/Release configurations (no RelWithDebInfo/MinSizeRel).
    debug_or_release_cfg = debug_or_release(build_cfg)
    run_streamed(
        str(msvc_dir / "msbuild.bat"), "gc", "LIB", vs_cfg_vars.vs_platform, debug_or_release_cfg, cwd=msvc_dir
    )

    lib_dir = dependency_dir / "lib" / vs_cfg_vars.vs_platform / debug_or_release_cfg
    shutil.copytree(lib_dir, install_dir / "mpir", dirs_exist_ok=True)


def install_mpfr(
    vs_cfg_vars: VsCfgResult,
    deps_dir: Path,
    install_dir: Path,
    build_cfg: BuildCfg,
    build_type: BuildType,
    msbuild_cmd: tuple[str, ...],
) -> None:
    DEPENDENCY_NAME = "mpfr"
    dependency_dir = deps_dir / "mpfr"

    if is_already_installed(install_dir / "mpfr"):
        return

    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://github.com/aothms/mpfr.git",
        dependency_dir,
        "2ebbe10fd029a480cf6e8a64c493afa9f3654251",
    )
    run_streamed("git", "reset", "--hard", cwd=dependency_dir)
    run_streamed("git", "clean", "-fdx", cwd=dependency_dir)

    ucrt_version = get_vs_var("UCRTVersion")
    mpfr_patch = (SCRIPT_DIR / "patches" / "mpfr.patch").read_text()
    patch = mpfr_patch.replace("sdk", ucrt_version).replace("fn", "lib_mpfr")
    logger.info("Applying mpfr patch.")
    subprocess.run(
        ["git", "apply", "--unidiff-zero", "--ignore-whitespace"],
        input=patch,
        text=True,
        cwd=dependency_dir,
        check=True,
    )

    run_streamed(
        "git",
        "apply",
        str(SCRIPT_DIR / "patches" / "mpfr_runtime.patch"),
        "--unidiff-zero",
        "--ignore-whitespace",
        cwd=dependency_dir,
    )

    if vs_cfg_vars.is_vs_platform("ARM64"):
        logger.info("Applying ARM64 patches for mpfr.")
        run_streamed(
            "git",
            "apply",
            str(SCRIPT_DIR / "patches" / "mpfr-arm64-changes.patch"),
            "--unidiff-zero",
            "--ignore-whitespace",
            cwd=dependency_dir,
        )

    # mpfr's repo only ships these two prebaked solution folders, regardless of the actual VS version in use.
    if vs_cfg_vars.generator.vs_ver == 2017:
        mpfr_sln_dir = "build.vc15"
        orig_generator = CMAKE_GENERATORS["Visual Studio 15 2017"]
    else:
        mpfr_sln_dir = "build.vs19"
        orig_generator = CMAKE_GENERATORS["Visual Studio 16 2019"]
    orig_platform_toolset = orig_generator.vs_toolset

    target_toolset = vs_cfg_vars.vs_toolset
    for vcxproj in (dependency_dir / mpfr_sln_dir).rglob("*.vcxproj"):
        vcxproj.write_text(vcxproj.read_text().replace(orig_platform_toolset, target_toolset))

    # mpfr's vcxproj files only define Debug/Release configurations (no RelWithDebInfo/MinSizeRel).
    debug_or_release_cfg = debug_or_release(build_cfg)
    build_solution(
        DEPENDENCY_NAME,
        msbuild_cmd,
        dependency_dir / mpfr_sln_dir / "lib_mpfr.sln",
        debug_or_release_cfg,
        vs_cfg_vars.vs_platform,
        build_type,
        target="lib_mpfr",
    )

    # Not all msvc projects in the solution are patched with the right sdk version, so the build
    # can report success even when mpfr.lib itself failed to build.
    lib_dir = dependency_dir / "lib" / vs_cfg_vars.vs_platform / debug_or_release_cfg
    if not (lib_dir / "mpfr.lib").exists():
        logger.error(f"{lib_dir / 'mpfr.lib'} was not built.")
        sys.exit(1)

    shutil.copytree(lib_dir, install_dir / "mpfr", dirs_exist_ok=True)


def install_qt6(
    vs_cfg_vars: VsCfgResult,
    build_deps_cache: BuildDepsCache,
    build_cfg: BuildCfg,
    ifcos_install_qt6: bool,
    pythonhome: Path | None,
) -> None:
    DEPENDENCY_NAME = "qt6"
    QT6_VERSION = os.getenv("QT6_VERSION")
    if QT6_VERSION:
        logger.info(f"Using overridden QT6_VERSION: '{QT6_VERSION}'")
    else:
        QT6_VERSION = "6.8.3"

    build_deps_cache.add_entry("QT6_VERSION", QT6_VERSION)

    vs_toolset = vs_cfg_vars.vs_toolset
    QT6_MSVC_YEAR = VS_TOOLSET_TO_VS_VER[vs_toolset]
    # Qt has not published prebuilt msvc2026 binaries yet (aqt only lists win64_msvc2022_64 as of
    # Qt 6.7-6.10). The v14x MSVC toolsets share a stable ABI/CRT, so fall back to the msvc2022
    # binaries until Qt ships msvc2026 ones. Revisit once `aqt list-qt windows desktop --arch <ver>`
    # shows a msvc2026 entry.
    if QT6_MSVC_YEAR == 2026:
        QT6_MSVC_YEAR = 2022

    QT6_CROSS_COMPILING = False
    QT6_HOST_ARCH = None
    QT6_HOST_INSTALL_SUFFIX = None
    if vs_cfg_vars.is_vs_platform("x64"):
        QT6_ARCH = f"win64_msvc{QT6_MSVC_YEAR}_64"
        QT6_INSTALL_SUFFIX = f"msvc{QT6_MSVC_YEAR}_64"
    elif vs_cfg_vars.is_vs_platform("ARM64"):
        QT6_CROSS_COMPILING = True
        QT6_ARCH = f"win64_msvc{QT6_MSVC_YEAR}_arm64_cross_compiled"
        QT6_INSTALL_SUFFIX = f"msvc{QT6_MSVC_YEAR}_arm64"
        # Qt publishes Windows ARM64 packages as cross-compiled Qt. Even on the
        # windows-11-arm runner, Qt CMake requires host tools such as moc/rcc.
        # Use the x64 host tools; Windows 11 on Arm runs them through x64
        # emulation while cl.exe still builds ARM64 binaries against target Qt.
        QT6_HOST_ARCH = f"win64_msvc{QT6_MSVC_YEAR}_64"
        QT6_HOST_INSTALL_SUFFIX = f"msvc{QT6_MSVC_YEAR}_64"
    else:
        logger.error(
            f"Automatic Qt6 installation is only supported for x64 and arm64 builds, "
            f"got '{vs_cfg_vars.vs_platform}'."
        )
        sys.exit(1)

    DEPENDENCY_INSTALL_NAME = f"qt6-{QT6_VERSION}-{QT6_INSTALL_SUFFIX}"
    QT6_AQT_OUTPUT_DIR = vs_cfg_vars.install_dir / DEPENDENCY_INSTALL_NAME
    QT6_INSTALL_DIR = QT6_AQT_OUTPUT_DIR / QT6_VERSION / QT6_INSTALL_SUFFIX
    QT_DIR = QT6_INSTALL_DIR

    QT6_HOST_AQT_OUTPUT_DIR = None
    QT6_HOST_INSTALL_DIR = None
    QT_HOST_PATH = None
    if QT6_CROSS_COMPILING:
        assert QT6_HOST_INSTALL_SUFFIX is not None
        QT6_HOST_AQT_OUTPUT_DIR = vs_cfg_vars.install_dir / f"qt6-{QT6_VERSION}-{QT6_HOST_INSTALL_SUFFIX}"
        QT6_HOST_INSTALL_DIR = QT6_HOST_AQT_OUTPUT_DIR / QT6_VERSION / QT6_HOST_INSTALL_SUFFIX
        QT_HOST_PATH = QT6_HOST_INSTALL_DIR

    QT6_CONFIG_DLL = "Qt6Cored.dll" if debug_or_release(build_cfg) == "Debug" else "Qt6Core.dll"

    if not ifcos_install_qt6:
        logger.info("IFCOS_INSTALL_QT6 not 'TRUE', skipping installation of Qt6.")
        return

    build_deps_cache.add_entry("QT6_INSTALL_DIR", str(QT6_INSTALL_DIR))
    build_deps_cache.add_entry("QT_DIR", str(QT_DIR))
    if QT6_CROSS_COMPILING:
        assert QT6_HOST_INSTALL_DIR is not None
        assert QT_HOST_PATH is not None
        build_deps_cache.add_entry("QT6_HOST_INSTALL_DIR", str(QT6_HOST_INSTALL_DIR))
        build_deps_cache.add_entry("QT_HOST_PATH", str(QT_HOST_PATH))

    QT6_TARGET_EXPECTED_FILES = [
        QT6_INSTALL_DIR / "lib" / "cmake" / "Qt6" / "Qt6Config.cmake",
        QT6_INSTALL_DIR / "bin" / QT6_CONFIG_DLL,
        QT6_INSTALL_DIR / "lib" / "cmake" / "Qt6Svg" / "Qt6SvgConfig.cmake",
    ]
    QT6_TARGET_INSTALLED = all(path.exists() for path in QT6_TARGET_EXPECTED_FILES)

    QT6_HOST_EXPECTED_FILES = None
    QT6_HOST_INSTALLED = True
    if QT6_CROSS_COMPILING:
        assert QT6_HOST_INSTALL_DIR is not None
        QT6_HOST_EXPECTED_FILES = [
            QT6_HOST_INSTALL_DIR / "lib" / "cmake" / "Qt6" / "Qt6Config.cmake",
            QT6_HOST_INSTALL_DIR / "bin" / "moc.exe",
            QT6_HOST_INSTALL_DIR / "bin" / "rcc.exe",
            QT6_HOST_INSTALL_DIR / "lib" / "cmake" / "Qt6Svg" / "Qt6SvgConfig.cmake",
        ]
        QT6_HOST_INSTALLED = all(path.exists() for path in QT6_HOST_EXPECTED_FILES)

    if QT6_TARGET_INSTALLED and QT6_HOST_INSTALLED:
        logger.info(f"Found existing '{QT6_INSTALL_DIR}' for {build_cfg}, skipping")
        if QT6_CROSS_COMPILING:
            logger.info(f"Found existing Qt host tools at '{QT6_HOST_INSTALL_DIR}', skipping")
        mark_installation(QT6_INSTALL_DIR, build_cfg)
        return

    if pythonhome is not None and (pythonhome / "python.exe").exists():
        AQT_PYTHON = str(pythonhome / "python.exe")
    else:
        AQT_PYTHON = require_command("python")

    run_streamed(AQT_PYTHON, "-m", "pip", "install", "--upgrade", "aqtinstall")

    def aqt_install_qt(arch: str, output_dir: Path) -> None:
        run_streamed(
            AQT_PYTHON,
            "-m",
            "aqt",
            "install-qt",
            "windows",
            "desktop",
            QT6_VERSION,
            arch,
            "-O",
            str(output_dir),
            "--archives",
            "qtbase",
            "qtsvg",
        )

    if not QT6_TARGET_INSTALLED:
        # Keep the install lean by filtering archives: qtbase provides
        # Core/Gui/Widgets (and the Qt6::CorePrivate target), qtsvg provides
        # Qt6::Svg. Both are base-Qt archives, not add-on modules.
        aqt_install_qt(QT6_ARCH, QT6_AQT_OUTPUT_DIR)

    if QT6_CROSS_COMPILING and not QT6_HOST_INSTALLED:
        assert QT6_HOST_ARCH is not None
        assert QT6_HOST_AQT_OUTPUT_DIR is not None
        # windeployqt runs from the host Qt when cross-compiling ARM64, so the
        # host Qt needs qtsvg too to deploy the Bonsai Viewer's Qt6Svg dependency.
        aqt_install_qt(QT6_HOST_ARCH, QT6_HOST_AQT_OUTPUT_DIR)

    def require_exists(label: str, path: Path) -> None:
        if not path.exists():
            logger.error(f"{label} did not produce '{path.name}' at '{path.parent}'.")
            sys.exit(1)

    for path in QT6_TARGET_EXPECTED_FILES:
        require_exists("Qt6 installation", path)

    if QT6_CROSS_COMPILING:
        assert QT6_HOST_EXPECTED_FILES is not None
        for path in QT6_HOST_EXPECTED_FILES:
            require_exists("Qt6 host installation", path)

    # TODO: check if it's actually needed, since we don't use check it.
    mark_installation(QT6_INSTALL_DIR, build_cfg)


def install_python(
    vs_cfg_vars: VsCfgResult, ifcos_install_python: bool, build_deps_cache: BuildDepsCache, nuget_exe: Path
) -> Path | None:
    """Returns PYTHONHOME, or None if IFCOS_INSTALL_PYTHON is not set."""
    PYTHON_VERSION = os.getenv("PYTHON_VERSION")
    if PYTHON_VERSION:
        logger.info(f"Using overridden PYTHON_VERSION: '{PYTHON_VERSION}'")
    else:
        PYTHON_VERSION = "3.11.7"

    if not ifcos_install_python:
        logger.info("IFCOS_INSTALL_PYTHON not 'TRUE', skipping installation of Python.")
        return None

    if not vs_cfg_vars.is_vs_platform("ARM64") and not vs_cfg_vars.is_vs_platform("x64"):
        # nuget doesn't support providing architecture for packages.
        logger.error("Automatic installation of Python for x86 builds is not supported,")
        logger.error(f"please install Python {PYTHON_VERSION} manually and ensure that it is available in PATH.")
        logger.error(f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}.exe")
        sys.exit(1)

    if vs_cfg_vars.is_vs_platform("ARM64"):
        PYTHONHOME = vs_cfg_vars.deps_dir / f"pythonarm64.{PYTHON_VERSION}" / "tools"
    else:
        PYTHONHOME = vs_cfg_vars.deps_dir / f"python.{PYTHON_VERSION}" / "tools"

    build_deps_cache.add_entry("PYTHONHOME", str(PYTHONHOME))

    if PYTHONHOME.exists():
        logger.info(f"Found existing '{PYTHONHOME}', skipping installation.")
        return PYTHONHOME

    nuget_package = "pythonarm64" if vs_cfg_vars.is_vs_platform("ARM64") else "Python"
    run(
        str(nuget_exe),
        "install",
        nuget_package,
        "-Version",
        PYTHON_VERSION,
        "-OutputDirectory",
        str(vs_cfg_vars.deps_dir),
    )

    return PYTHONHOME


def install_swig(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_deps_cache: BuildDepsCache,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    SWIG_VERSION = "4.4.1"
    DEPENDENCY_NAME = "SWIG"
    dependency_dir = vs_cfg_vars.deps_dir / f"swig-{SWIG_VERSION}"
    dependency_install_dir = vs_cfg_vars.install_dir / f"swig-{SWIG_VERSION}"

    build_deps_cache.add_entry("SWIG_INSTALL_DIR", str(dependency_install_dir))

    if is_already_installed(dependency_install_dir):
        return

    WIN_FLEX_BISON = "win_flex_bison-2.5.25"

    def install_bison() -> None:
        DEPENDENCY_NAME = "win_flex_bison"
        WIN_FLEX_BISON_ZIP = f"{WIN_FLEX_BISON}.zip"

        download_file(
            DEPENDENCY_NAME,
            f"https://github.com/lexxmark/winflexbison/releases/download/v2.5.25/{WIN_FLEX_BISON_ZIP}",
            vs_cfg_vars.deps_dir / WIN_FLEX_BISON_ZIP,
        )

        extract_file(
            DEPENDENCY_NAME,
            vs_cfg_vars.deps_dir / WIN_FLEX_BISON_ZIP,
            vs_cfg_vars.deps_dir / WIN_FLEX_BISON,
            vs_cfg_vars.deps_dir / WIN_FLEX_BISON,
        )

    install_bison()

    SWIG_ZIP = f"swig-{SWIG_VERSION}.zip"
    download_file(
        DEPENDENCY_NAME,
        f"https://github.com/swig/swig/archive/refs/tags/v{SWIG_VERSION}.zip",
        vs_cfg_vars.deps_dir / SWIG_ZIP,
    )

    extract_file(
        DEPENDENCY_NAME,
        vs_cfg_vars.deps_dir / SWIG_ZIP,
        vs_cfg_vars.deps_dir,
        dependency_dir,
    )

    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DWITH_PCRE=OFF",
        f"-DBISON_EXECUTABLE={vs_cfg_vars.deps_dir / WIN_FLEX_BISON / 'win_bison.exe'}",
    )

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, "Release", msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, "Release")


def install_cgal(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    # TODO: bump to v5.6.3 to match nix/build-all.py.
    # TODO: add CGAL_VERSION to the install path during the next version bump.
    CGAL_VERSION = "5.5.5"
    DEPENDENCY_NAME = "cgal"
    dependency_dir = deps_dir / "cgal"
    dependency_install_dir = install_dir / "cgal"

    if is_already_installed(dependency_install_dir):
        return

    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://github.com/CGAL/cgal.git",
        dependency_dir,
        f"v{CGAL_VERSION}",
    )

    run_streamed("git", "reset", "--hard", cwd=dependency_dir)
    run_streamed(
        "git",
        "apply",
        "--ignore-whitespace",
        str(SCRIPT_DIR / "patches" / "cgal_no_zlib.patch"),
        cwd=dependency_dir,
    )

    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
    )

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)


def install_eigen(vs_cfg_vars: VsCfgResult) -> None:
    install_dir = vs_cfg_vars.install_dir

    # TODO: bump to 3.4.0 to match nix/build-all.py.
    # TODO: add EIGEN_VERSION to the install path during the next version bump.
    EIGEN_VERSION = "3.3.9"
    DEPENDENCY_NAME = "Eigen"
    dependency_dir = install_dir / DEPENDENCY_NAME

    if is_already_installed(dependency_dir):
        return

    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://gitlab.com/libeigen/eigen.git",
        dependency_dir,
        EIGEN_VERSION,
    )


def install_zstd(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    ZSTD_VERSION = "1.5.7"
    DEPENDENCY_NAME = "zstd"
    dependency_dir = deps_dir / f"{DEPENDENCY_NAME}-{ZSTD_VERSION}"
    dependency_install_dir = install_dir / DEPENDENCY_NAME

    if is_already_installed(dependency_install_dir):
        return

    ZSTD_ZIP = f"zstd-{ZSTD_VERSION}.zip"
    download_file(
        DEPENDENCY_NAME,
        f"https://github.com/facebook/zstd/archive/refs/tags/v{ZSTD_VERSION}.zip",
        deps_dir / ZSTD_ZIP,
    )

    extract_file(
        DEPENDENCY_NAME,
        deps_dir / ZSTD_ZIP,
        deps_dir,
        dependency_dir,
    )

    cmake_source_dir = dependency_dir / "build" / "cmake"
    run_cmake(
        DEPENDENCY_NAME,
        cmake_source_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DZSTD_BUILD_STATIC=ON",
        "-DZSTD_BUILD_SHARED=OFF",
    )

    build_path = cmake_source_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)


def install_rocksdb(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    # TODO: bump to 10.4.2 to match nix/build-all.py.
    ROCKSDB_VERSION = "9.11.2"
    DEPENDENCY_NAME = "rocksdb"
    dependency_dir = deps_dir / f"{DEPENDENCY_NAME}-{ROCKSDB_VERSION}"
    dependency_install_dir = install_dir / DEPENDENCY_NAME

    if is_already_installed(dependency_install_dir, expected_build_cfg=build_cfg):
        return

    ROCKSDB_ZIP = f"rocksdb-{ROCKSDB_VERSION}.zip"
    download_file(
        DEPENDENCY_NAME,
        f"https://github.com/facebook/rocksdb/archive/refs/tags/v{ROCKSDB_VERSION}.zip",
        deps_dir / ROCKSDB_ZIP,
    )

    extract_file(
        DEPENDENCY_NAME,
        deps_dir / ROCKSDB_ZIP,
        deps_dir,
        dependency_dir,
    )

    # see rocksdb/thirdparty.inc
    # providing package is not supported on Windows.
    # ZSTD_INCLUDE / ZSTD_LIB_DEBUG / ZSTD_LIB_RELEASE must be env vars - as cmake -D args they have no effect on MSVC.
    zstd_include = install_dir / "zstd" / "include"
    zstd_lib = install_dir / "zstd" / "lib" / "zstd_static.lib"

    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DROCKSDB_INSTALL_ON_WINDOWS=ON",
        "-DFAIL_ON_WARNINGS=OFF",
        "-DWITH_TESTS=OFF",
        "-DWITH_TOOLS=OFF",
        "-DWITH_BENCHMARK_TOOLS=OFF",
        "-DWITH_CORE_TOOLS=OFF",
        "-DROCKSDB_BUILD_SHARED=OFF",
        "-DWITH_ZSTD=ON",
        "-DPORTABLE=1",
        "-DCMAKE_DEBUG_POSTFIX=_d",
        env={
            "ZSTD_INCLUDE": str(zstd_include),
            "ZSTD_LIB_DEBUG": str(zstd_lib),
            "ZSTD_LIB_RELEASE": str(zstd_lib),
        },
    )

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)
    mark_installation(dependency_install_dir, build_cfg)


def install_manifold(
    vs_cfg_vars: VsCfgResult,
    build_type: BuildType,
    build_deps_cache: BuildDepsCache,
    build_cfg: BuildCfg,
    msbuild_multiproc: tuple[str, ...],
) -> None:
    deps_dir = vs_cfg_vars.deps_dir
    install_dir = vs_cfg_vars.install_dir

    MANIFOLD_VERSION = "3.2.1"
    DEPENDENCY_NAME = "manifold"
    dependency_dir = deps_dir / f"{DEPENDENCY_NAME}-{MANIFOLD_VERSION}"
    dependency_install_dir = install_dir / f"{DEPENDENCY_NAME}-{MANIFOLD_VERSION}"

    # TODO: test whether manifold links the debug CRT for Debug builds and needs separate
    # Release/Debug install dirs instead of sharing one.
    build_deps_cache.add_entry("MANIFOLD_INSTALL_PATH", str(dependency_install_dir))

    if is_already_installed(dependency_install_dir):
        return

    git_clone_and_checkout_revision(
        DEPENDENCY_NAME,
        "https://github.com/elalish/manifold.git",
        dependency_dir,
        f"v{MANIFOLD_VERSION}",
    )

    run_cmake(
        DEPENDENCY_NAME,
        dependency_dir,
        vs_cfg_vars,
        build_type,
        f"-DCMAKE_INSTALL_PREFIX={dependency_install_dir}",
        "-DBUILD_SHARED_LIBS=OFF",
        "-DMANIFOLD_PAR=OFF",
        "-DMANIFOLD_CROSS_SECTION=OFF",
        "-DMANIFOLD_PYBIND=OFF",
        "-DMANIFOLD_JSBIND=OFF",
        "-DMANIFOLD_CBIND=OFF",
        "-DMANIFOLD_TEST=OFF",
        "-DMANIFOLD_EXPORT=OFF",
        "-DMANIFOLD_DOWNLOADS=OFF",
    )

    build_path = dependency_dir / vs_cfg_vars.build_dir
    build_cmake_project(DEPENDENCY_NAME, build_path, build_cfg, msbuild_multiproc)
    install_cmake_project(DEPENDENCY_NAME, build_path, build_cfg)
