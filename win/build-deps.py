# This file was generated with the assistance of an AI coding tool.
"""Install Windows build dependencies with Conan."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from common import REPO_ROOT, BuildDepsCache, logger
from vs_cfg import vs_cfg

MSVC_VERSIONS = {
    "v140": "190",
    "v141": "191",
    "v142": "192",
    "v143": "193",
    "v145": "195",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generator", nargs="?", help="Visual Studio generator shorthand, e.g. vs2022-x64")
    parser.add_argument("build_cfg", nargs="?", default="Release")
    parser.add_argument("build_type", nargs="?", default="Build")
    parser.add_argument("--generator", dest="generator_flag")
    parser.add_argument("--build-cfg", default=None)
    parser.add_argument("--build-type", dest="build_type_flag", default=None)
    parser.add_argument("--install-python", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--install-qt6", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--num-build-procs", type=int)
    parser.add_argument("--reuse-boost", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.generator = args.generator or args.generator_flag
    args.build_cfg = args.build_cfg_flag or args.build_cfg
    args.build_type = args.build_type_flag or args.build_type
    return args


def conan_setting_arch(vs_platform: str) -> str:
    return {"Win32": "x86", "x64": "x86_64", "ARM": "armv7", "ARM64": "armv8"}[vs_platform]


def main() -> None:
    args = parse_args()
    generator = args.generator or os.getenv("GEN_SHORTHAND")
    if not generator:
        raise SystemExit("A Visual Studio generator is required, e.g. vs2022-x64")

    cfg = vs_cfg(generator, REPO_ROOT)
    cache = BuildDepsCache(cfg)
    cache.add_entry("GEN_SHORTHAND", cfg.gen_shorthand)

    conan = shutil.which("conan") or shutil.which("conan.exe")
    if not conan:
        raise SystemExit("Conan was not found in PATH.")

    output_dir = cfg.install_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        conan,
        "install",
        str(REPO_ROOT),
        "--output-folder",
        str(output_dir),
        "--build=missing",
        "-s",
        "os=Windows",
        "-s",
        "arch=" + conan_setting_arch(cfg.vs_platform),
        "-s",
        "compiler=msvc",
        "-s",
        "compiler.version=" + MSVC_VERSIONS[cfg.vs_toolset],
        "-s",
        "compiler.runtime=dynamic",
        "-s",
        "build_type=" + args.build_cfg,
        "-o",
        "build_bonsaiviewer=True",
        "-o",
        "with_rocksdb=True",
        "-o",
        "with_hdf5=True",
        "-o",
        f"with_ifcpython={args.install_python}",
    ]
    logger.info("Installing Windows dependencies with Conan")
    subprocess.run(command, cwd=REPO_ROOT, check=True)

    toolchain = output_dir / "generators" / "conan_toolchain.cmake"
    if not toolchain.is_file():
        raise RuntimeError(f"Conan did not generate {toolchain}")
    cache.add_entry("CONAN_TOOLCHAIN_FILE", str(toolchain))
    cache.add_entry("CONAN_INSTALL_DIR", str(output_dir))
    cache.add_entry("BOOST_INSTALL_DIR", str(output_dir))
    cache.add_entry("OCC_INSTALL_DIR", str(output_dir))
    cache.add_entry("CGAL_INSTALL_DIR", str(output_dir))
    cache.add_entry("EIGEN_DIR", str(output_dir))
    cache.add_entry("ROCKSDB_INSTALL_DIR", str(output_dir))
    cache.add_entry("ZSTD_INSTALL_DIR", str(output_dir))
    cache.add_entry("MANIFOLD_INSTALL_PATH", str(output_dir))
    cache.add_entry("SWIG_INSTALL_DIR", str(output_dir))
    cache.add_entry("PYTHONHOME", str(Path(sys.executable).parent))


if __name__ == "__main__":
    main()
