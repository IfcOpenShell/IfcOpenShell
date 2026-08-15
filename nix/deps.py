#!/usr/bin/env python3
# This file was generated with the assistance of an AI coding tool.
"""Shared dependency build recipes for WASM targets.

Used by both:
- nix/wasm_native.py (native C-ABI WASM build)
- nix/build-all.py (multi-platform build with -wasm flag)

Each recipe takes `(src, prefix, env, **kwargs)` and:
1. Checks if already built (skips via an install marker)
2. Applies patches listed in `sources.lock.json` via `core.apply_patches_from_lock`
3. Runs configure (emcmake cmake / emconfigure)
4. Runs build (cmake --build / make)
5. Runs install (cmake --build --target install / make install)

All versions and patches come from `nix/sources.lock.json` via
`core.load_lockfile()` — no inline version constants.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Allow `python nix/deps.py` introspection and package import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nix import core  # noqa: E402

# Build root for intermediate build directories. Callers may override
# (e.g. `build-all.py` sets this to its own `DEPS_DIR / "wasm-build"`).
BUILD_ROOT: Path = Path(
    os.environ.get(
        "WASM_NATIVE_BUILD_ROOT",
        str(Path(__file__).resolve().parent.parent / "build" / "wasm-native"),
    )
)


def set_build_root(path: Path) -> None:
    """Override the build root used for intermediate build directories."""
    global BUILD_ROOT
    BUILD_ROOT = Path(path)


def _dep_build_dir(name: str) -> Path:
    """Return the build directory for a dependency."""
    return BUILD_ROOT / "build" / name


def _nproc() -> int:
    return core.build_jobs()


# ──────────────────────────────────────────────────────────────────────────────
# Header-only / cmake-based deps
# ──────────────────────────────────────────────────────────────────────────────


def build_boost(src: Path, prefix: Path, env) -> None:
    """Build Boost with the emscripten bjam toolset.

    Builds a static set of boost libraries (system, program_options, regex,
    thread, date_time, iostreams, filesystem), converts the resulting .bc
    archives to .a via `emar`, and copies headers into `prefix/include/boost`.
    """
    lib_dir = prefix / "lib"
    if lib_dir.exists() and any(lib_dir.glob("*.a")):
        core.logger.info("Boost already built at %s", prefix)
        return

    prefix.mkdir(parents=True, exist_ok=True)

    bootstrap = src / "bootstrap.sh"
    if bootstrap.exists():
        core.run([str(bootstrap)], cwd=src, env=env)

    b2 = src / "b2"
    core.run(
        [
            str(b2),
            "toolset=emscripten",
            "--with-system",
            "--with-program_options",
            "--with-regex",
            "--with-thread",
            "--with-date_time",
            "--with-iostreams",
            "--with-filesystem",
            "link=static",
            "variant=release",
            "threading=single",
            f"--stagedir={prefix}",
            "stage",
            "-s",
            "NO_BZIP2=1",
        ],
        cwd=src,
        env=env,
    )

    if lib_dir.exists():
        for bc_file in lib_dir.glob("*.bc"):
            a_file = bc_file.with_suffix(".a")
            core.run(["emar", "q", str(a_file), str(bc_file)], cwd=src, env=env)

    src_boost = src / "boost"
    include_dir = prefix / "include"
    if src_boost.exists() and not (include_dir / "boost").exists():
        include_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(src_boost), str(include_dir / "boost"))


def build_eigen(src: Path, prefix: Path, env) -> None:
    """Install the Eigen header-only library."""
    if (prefix / "include" / "eigen3").exists():
        core.logger.info("Eigen already installed at %s", prefix)
        return

    build_dir = _dep_build_dir("eigen")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DBUILD_TESTING=OFF",
        ],
        cwd=build_dir,
        env=env,
    )
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_json(src: Path, prefix: Path, env) -> None:
    """Install the nlohmann_json header-only library."""
    if (prefix / "include" / "nlohmann").exists():
        core.logger.info("nlohmann_json already installed at %s", prefix)
        return

    build_dir = _dep_build_dir("nlohmann_json")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DJSON_BuildTests=OFF",
        ],
        cwd=build_dir,
        env=env,
    )
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_occt(src: Path, prefix: Path, env, *, build_type: str = "Release") -> None:
    """Build OpenCASCADE for WASM with -fwasm-exceptions.

    OCCT 7.8 exports package metadata for Release, Debug, and RelWithDebInfo,
    but not MinSizeRel. Use Release metadata with explicit size flags.
    """
    if (prefix / "lib" / "cmake" / "opencascade").exists():
        core.logger.info("OCCT already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("occt", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("occt")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DINSTALL_DIR={prefix}",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            "-DBUILD_LIBRARY_TYPE=Static",
            "-DBUILD_MODULE_Draw=0",
            "-DBUILD_MODULE_DETools=OFF",
            "-DBUILD_RELEASE_DISABLE_EXCEPTIONS=Off",
            "-DCMAKE_CXX_FLAGS=-fwasm-exceptions -sSUPPORT_LONGJMP=wasm",
            "-DCMAKE_C_FLAGS_RELEASE=-Oz -DNDEBUG",
            "-DCMAKE_CXX_FLAGS_RELEASE=-Oz -DNDEBUG",
            "-DUSE_XLIB=OFF",
            "-DUSE_FREETYPE=OFF",
            "-DUSE_OPENGL=OFF",
            "-DUSE_GLES2=OFF",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", "2"], env=env)
    core.run(["cmake", "--install", str(build_dir), "--config", build_type], env=env)


def build_manifold(
    src: Path, prefix: Path, env, *, build_type: str = "MinSizeRel"
) -> None:
    """Build Manifold for WASM."""
    if (prefix / "lib" / "cmake" / "manifold").exists():
        core.logger.info("Manifold already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("manifold", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("manifold")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            "-DMANIFOLD_PAR=OFF",
            "-DMANIFOLD_CROSS_SECTION=OFF",
            "-DMANIFOLD_PYBIND=OFF",
            "-DMANIFOLD_JSBIND=OFF",
            "-DMANIFOLD_CBIND=OFF",
            "-DMANIFOLD_TEST=OFF",
            "-DMANIFOLD_EXPORT=OFF",
            "-DMANIFOLD_DOWNLOADS=OFF",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", "2"], env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


# ──────────────────────────────────────────────────────────────────────────────
# autoconf-based deps
# ──────────────────────────────────────────────────────────────────────────────


def build_gmp(src: Path, prefix: Path, env, *, host_cc_override: bool = False) -> None:
    """Build GMP for WASM via emconfigure.

    On macOS, force the native Apple clang for configure-time helper binaries
    instead of Emscripten's bundled clang. The `HAVE_OBSTACK_VPRINTF` macro is
    disabled in `config.h` after configure (it is not supported under
    emscripten).
    """
    if (prefix / "lib" / "libgmp.a").exists():
        core.logger.info("GMP already built at %s", prefix)
        return

    build_dir = _dep_build_dir("gmp")
    build_dir.mkdir(parents=True, exist_ok=True)

    build_env = dict(env)
    if host_cc_override or platform.system() == "Darwin":
        try:
            native_cc = subprocess.check_output(
                ["xcrun", "--find", "clang"], text=True
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            native_cc = "clang"
        build_env["HOST_CC"] = native_cc
        build_env["CC_FOR_BUILD"] = native_cc
        try:
            sdk_path = subprocess.check_output(
                ["xcrun", "--show-sdk-path"], text=True
            ).strip()
            build_env["CC_FOR_BUILD"] = f"{native_cc} -isysroot {sdk_path}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    core.run(
        [
            "emconfigure",
            str(src / "configure"),
            "--host=wasm32",
            "--disable-assembly",
            "--enable-cxx",
            "--enable-static",
            "--disable-shared",
            "--with-pic",
            f"--prefix={prefix}",
        ],
        cwd=build_dir,
        env=build_env,
    )

    config_h = build_dir / "config.h"
    if config_h.exists():
        content = config_h.read_text()
        content = content.replace("HAVE_OBSTACK_VPRINTF 1", "HAVE_OBSTACK_VPRINTF 0")
        config_h.write_text(content)

    core.run(["make", f"-j{_nproc()}"], cwd=build_dir, env=build_env)
    core.run(["make", "install"], cwd=build_dir, env=build_env)


def build_mpfr(src: Path, prefix: Path, gmp_prefix: Path, env) -> None:
    """Build MPFR for WASM via emconfigure, linking against `gmp_prefix`."""
    if (prefix / "lib" / "libmpfr.a").exists():
        core.logger.info("MPFR already built at %s", prefix)
        return

    build_dir = _dep_build_dir("mpfr")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emconfigure",
            str(src / "configure"),
            "--host=none",
            "--enable-static",
            "--disable-shared",
            "--with-pic",
            f"--with-gmp={gmp_prefix}",
            f"--prefix={prefix}",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["make", f"-j{_nproc()}"], cwd=build_dir, env=env)
    core.run(["make", "install"], cwd=build_dir, env=env)


def build_cgal(
    src: Path,
    prefix: Path,
    gmp_prefix: Path,
    mpfr_prefix: Path,
    env,
    boost_prefix: Optional[Path] = None,
) -> None:
    """Build CGAL for WASM (header-only with GMP/MPFR)."""
    if (prefix / "lib" / "cmake" / "CGAL").exists():
        core.logger.info("CGAL already built at %s", prefix)
        return

    build_dir = _dep_build_dir("cgal")
    build_dir.mkdir(parents=True, exist_ok=True)

    lib_ext = "a"
    cmake_cmd = [
        "emcmake",
        "cmake",
        str(src),
        f"-DCMAKE_INSTALL_PREFIX={prefix}",
        "-DCGAL_HEADER_ONLY=On",
        "-DBUILD_SHARED_LIBS=Off",
        f"-DGMP_LIBRARIES={gmp_prefix}/lib/libgmp.{lib_ext}",
        f"-DGMP_INCLUDE_DIR={gmp_prefix}/include",
        f"-DMPFR_LIBRARIES={mpfr_prefix}/lib/libmpfr.{lib_ext}",
        f"-DMPFR_INCLUDE_DIR={mpfr_prefix}/include",
    ]
    if boost_prefix is not None:
        cmake_cmd.append(f"-DBoost_INCLUDE_DIR={boost_prefix}")

    core.run(cmake_cmd, cwd=build_dir, env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_libxml2(
    src: Path, prefix: Path, env, *, static: bool = True, without_threads: bool = False
) -> None:
    """Build libxml2 for WASM via emconfigure autoconf."""
    if (prefix / "lib" / "libxml2.a").exists() or (
        prefix / "include" / "libxml2"
    ).exists():
        core.logger.info("libxml2 already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("libxml2", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("libxml2")
    build_dir.mkdir(parents=True, exist_ok=True)

    configure_path = src / "configure"
    if not configure_path.exists():
        core.run(["bash", "./autogen.sh"], cwd=src, env=env)

    args = [
        "--without-python",
        "--enable-static" if static else "--disable-static",
        "--disable-shared" if static else "--enable-shared",
        "--without-zlib",
        "--without-iconv",
        "--without-lzma",
    ]
    if without_threads:
        args.append("--without-threads")

    core.run(
        [
            "emconfigure",
            "/bin/sh",
            str(src / "configure"),
            "--host=wasm32",
            *args,
            f"--prefix={prefix}",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["make", f"-j{_nproc()}"], cwd=build_dir, env=env)
    core.run(["make", "install"], cwd=build_dir, env=env)


# ──────────────────────────────────────────────────────────────────────────────
# cmake-based deps (additional, modelled after build-all.py invocations)
# ──────────────────────────────────────────────────────────────────────────────


def build_zstd(src: Path, prefix: Path, env) -> None:
    """Build zstd for WASM (cmake in build/cmake subdir)."""
    if (prefix / "lib" / "libzstd.a").exists() or (
        prefix / "include" / "zstd.h"
    ).exists():
        core.logger.info("zstd already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("zstd", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("zstd")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src / "build" / "cmake"),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DZSTD_BUILD_STATIC=ON",
            "-DZSTD_BUILD_SHARED=OFF",
            "-DCMAKE_INSTALL_LIBDIR=lib",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", str(_nproc())], env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_rocksdb(src: Path, prefix: Path, env, zstd_prefix: Path) -> None:
    """Build RocksDB for WASM with zstd support."""
    if (prefix / "lib" / "librocksdb.a").exists():
        core.logger.info("rocksdb already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("rocksdb", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("rocksdb")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DFAIL_ON_WARNINGS=Off",
            "-DWITH_TESTS=OFF",
            "-DWITH_TOOLS=OFF",
            "-DWITH_GFLAGS=OFF",
            "-DWITH_BENCHMARK_TOOLS=OFF",
            "-DWITH_CORE_TOOLS=OFF",
            "-DROCKSDB_BUILD_SHARED=Off",
            "-DCMAKE_POSITION_INDEPENDENT_CODE=On",
            "-DUSE_RTTI=On",
            "-DWITH_ZSTD=On",
            "-DPORTABLE=1",
            f"-DCMAKE_PREFIX_PATH={zstd_prefix}",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", str(_nproc())], env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_pcre(src: Path, prefix: Path, env) -> None:
    """Build PCRE for WASM via emconfigure autoconf."""
    if (prefix / "lib" / "libpcre.a").exists():
        core.logger.info("pcre already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("pcre", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("pcre")
    build_dir.mkdir(parents=True, exist_ok=True)

    configure_path = src / "configure"
    if not configure_path.exists():
        core.run(["bash", "./autogen.sh"], cwd=src, env=env)

    core.run(
        [
            "emconfigure",
            "/bin/sh",
            str(src / "configure"),
            "--host=wasm32",
            "--enable-static",
            "--disable-shared",
            f"--prefix={prefix}",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["make", f"-j{_nproc()}"], cwd=build_dir, env=env)
    core.run(["make", "install"], cwd=build_dir, env=env)


def build_opencollada(
    src: Path, prefix: Path, env, libxml2_prefix: Path, pcre_prefix: Path
) -> None:
    """Build OpenCOLLADA for WASM via emcmake cmake."""
    if (prefix / "lib" / "libOpenCOLLADAFramework.a").exists() or (
        prefix / "include" / "COLLADABaseUtils"
    ).exists():
        core.logger.info("OpenCOLLADA already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("opencollada", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("opencollada")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            f"-DLIBXML2_INCLUDE_DIR={libxml2_prefix}/include/libxml2",
            f"-DLIBXML2_LIBRARIES={libxml2_prefix}/lib/libxml2.a",
            f"-DPCRE_INCLUDE_DIR={pcre_prefix}/include",
            f"-DPCRE_PCREPOSIX_LIBRARY={pcre_prefix}/lib/libpcreposix.a",
            f"-DPCRE_PCRE_LIBRARY={pcre_prefix}/lib/libpcre.a",
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", str(_nproc())], env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)


def build_swig(src: Path, prefix: Path, env) -> None:
    """Build SWIG for WASM via emcmake cmake."""
    if (prefix / "bin" / "swig").exists():
        core.logger.info("swig already built at %s", prefix)
        return

    lock = core.load_lockfile()
    core.apply_patches_from_lock("swig", lock, src, core.PATCHES_DIR)

    build_dir = _dep_build_dir("swig")
    build_dir.mkdir(parents=True, exist_ok=True)

    core.run(
        [
            "emcmake",
            "cmake",
            str(src),
            "-DWITH_PCRE=OFF",
            f"-DCMAKE_INSTALL_PREFIX={prefix}",
        ],
        cwd=build_dir,
        env=env,
    )

    core.run(["cmake", "--build", str(build_dir), "--parallel", str(_nproc())], env=env)
    core.run(["cmake", "--build", str(build_dir), "--target", "install"], env=env)
