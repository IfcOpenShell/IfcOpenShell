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
import sys
from pathlib import Path
from typing import Literal, NamedTuple

from common import SCRIPT_DIR, logger, run

ArchBits = Literal[32, 64]
# TODO: according to cmake docs, there's no `ARM` platform, only `ARM64`.
# So it can be deleted?
VsPlatform = Literal["Win32", "x64", "ARM", "ARM64"]
"""Platform names as used by Visual Studio (e.g. `cmake -A`), but fine to use for general platform checks too."""
GeneratorType = Literal["EMPTY", "SHORTHAND", "FULL_NAME"]


class CMakeGeneratorInfo(NamedTuple):
    name: str
    """E.g. "Visual Studio 16 2019"."""
    generator_num: int
    """E.g. 16 for "Visual Studio 16 2019"."""
    vs_ver: int
    """E.g. 2019."""
    vc_ver: str
    """E.g. "14.2"."""
    vs_toolset: str
    """Default toolset for this generator, e.g. "v142".
    See `VsCfgResult.vs_toolset_override` for an explicit override.
    """
    boost_bootstrap_ver: str
    """E.g. "vc142"."""


CMAKE_GENERATORS = {
    "Visual Studio 12 2013": CMakeGeneratorInfo("Visual Studio 12 2013", 12, 2013, "12.0", "v120", "vc120"),
    "Visual Studio 14 2015": CMakeGeneratorInfo("Visual Studio 14 2015", 14, 2015, "14.0", "v140", "vc140"),
    "Visual Studio 15 2017": CMakeGeneratorInfo("Visual Studio 15 2017", 15, 2017, "14.1", "v141", "vc141"),
    "Visual Studio 16 2019": CMakeGeneratorInfo("Visual Studio 16 2019", 16, 2019, "14.2", "v142", "vc142"),
    "Visual Studio 17 2022": CMakeGeneratorInfo("Visual Studio 17 2022", 17, 2022, "14.3", "v143", "vc143"),
    "Visual Studio 18 2026": CMakeGeneratorInfo("Visual Studio 18 2026", 18, 2026, "14.5", "v145", "vc145"),
}


class VsCfgResult(NamedTuple):
    generator: CMakeGeneratorInfo
    vs_platform: VsPlatform
    """E.g. "x64"."""
    vs_toolset_override: str | None
    """E.g. "v142", or None if not explicitly overridden via generator shorthand."""
    arch_bits: ArchBits
    boost_toolset: str
    """E.g. "msvc-14.2"."""
    gen_shorthand: str
    """E.g. "vs2019-x64"."""
    deps_dir: Path
    """E.g. Path("_deps")."""
    install_dir: Path
    """E.g. Path("_deps-vs2019-x64-installed")."""
    build_dir: str
    """E.g. "_build-vs2019-x64"."""
    build_deps_cache_path: Path
    """E.g. Path("BuildDepsCache-x64-v142.txt")."""

    PRINT_VARS_SKIP = {"gen_shorthand", "deps_dir", "install_dir", "build_dir", "build_deps_cache_path"}

    def print_vars(self) -> None:
        fields = [f for f in self._fields if f not in self.PRINT_VARS_SKIP]
        name_width = max(len(f) for f in fields)
        for field in fields:
            logger.info(f"{field.upper():<{name_width}}: [{getattr(self, field)}]")

    def is_vs_platform(self, platform: VsPlatform) -> bool:
        """Compare against `vs_platform`, just to prevent typos."""
        return self.vs_platform == platform

    @property
    def vs_toolset(self) -> str:
        """Effective toolset: `vs_toolset_override` if set, else the generator's default."""
        return self.vs_toolset_override or self.generator.vs_toolset


VS_TOOLSET_TO_VC_VER = {info.vs_toolset: info.vc_ver for info in CMAKE_GENERATORS.values()}
"""E.g. "v142" -> "14.2"."""

VS_TOOLSET_TO_VS_VER = {info.vs_toolset: info.vs_ver for info in CMAKE_GENERATORS.values()}
"""E.g. "v142" -> 2019."""


class VSArchInfo(NamedTuple):
    vs_platform: VsPlatform
    arch_bits: ArchBits


VSCMD_ARG_TGT_ARCH_TO_INFO = {
    "x86": VSArchInfo("Win32", 32),
    "x64": VSArchInfo("x64", 64),
    "arm": VSArchInfo("ARM", 32),
    "arm64": VSArchInfo("ARM64", 64),
}

VS_PLATFORM_TO_INFO = {info.vs_platform: info for info in VSCMD_ARG_TGT_ARCH_TO_INFO.values()}


VSVar = Literal[
    "VSINSTALLDIR",
    "VisualStudioVersion",
    "VSCMD_ARG_TGT_ARCH",
    "UCRTVersion",
]


def get_vs_var(var: VSVar) -> str:
    value = os.getenv(var)
    if value is None:
        logger.error("Visual Studio environment variables not set - cannot proceed.")
        sys.exit(1)
    return value


class VsCfg:
    """Determines the CMake generator, VS platform/toolset, and derived paths for a build.

    Usage: `VsCfg.build(generator, repo_root)`.
    """

    @staticmethod
    def build(generator: str | None, repo_root: Path) -> VsCfgResult:
        generator = generator or ""
        vs_platform: VsPlatform | None = None
        vs_toolset: str | None = None
        boost_toolset_ver: str | None = None

        generator_type = VsCfg._determine_generator_type(generator)
        if generator_type in ("EMPTY", "SHORTHAND"):
            generator, vs_platform, vs_toolset, boost_toolset_ver = VsCfg._parse_generator_shorthand(
                generator, generator_type
            )

        # Just to be double sure.
        assert generator in CMAKE_GENERATORS
        VsCfg._ensure_cmake_supports_generator(generator)

        vs_platform = vs_platform or VsCfg._vs_platform_from_env()
        generator_info = CMAKE_GENERATORS[generator]
        arch_bits = VS_PLATFORM_TO_INFO[vs_platform].arch_bits

        boost_toolset = f"msvc-{boost_toolset_ver or generator_info.vc_ver}"

        gen_shorthand = f"vs{generator_info.vs_ver}-{vs_platform}"
        if vs_toolset is not None:
            gen_shorthand += f"-{vs_toolset}"

        # NOTE For IfcOpenShell we can build all of our deps both x86 and x64 using different VS versions in the same
        # directories so no need for "-{vs_ver}-{vs_platform}" postfix.
        deps_dir = repo_root / "_deps"
        install_dir = repo_root / f"_deps-{gen_shorthand}-installed"
        # build_dir is a relative build directory used for CMake-based projects.
        build_dir = f"_build-{gen_shorthand}"

        if vs_toolset is not None:
            build_deps_cache_path = SCRIPT_DIR / f"BuildDepsCache-{vs_platform}-{vs_toolset}.txt"
        else:
            build_deps_cache_path = SCRIPT_DIR / f"BuildDepsCache-{vs_platform}.txt"

        result = VsCfgResult(
            generator=generator_info,
            vs_platform=vs_platform,
            vs_toolset_override=vs_toolset,
            arch_bits=arch_bits,
            boost_toolset=boost_toolset,
            gen_shorthand=gen_shorthand,
            deps_dir=deps_dir,
            install_dir=install_dir,
            build_dir=build_dir,
            build_deps_cache_path=build_deps_cache_path,
        )
        result.print_vars()
        return result

    @staticmethod
    def _generator_from_visual_studio_version() -> str:
        # E.g. '17.0' -> 17.
        vs_version = get_vs_var("VisualStudioVersion")
        generator_num = int(vs_version.replace(".0", ""))

        for candidate, info in CMAKE_GENERATORS.items():
            if info.generator_num == generator_num:
                logger.info(
                    f"Generator not passed, but VisualStudioVersion={vs_version} environment variable detected:"
                )
                logger.info(f"using '{candidate}' as the generator.")
                return candidate

        logger.error(
            f"Generator is not provided and VisualStudioVersion='{vs_version}' is not supported - cannot proceed."
        )
        sys.exit(1)

    @staticmethod
    def _vs_platform_from_env() -> VsPlatform:
        # Fall back to `VSCMD_ARG_TGT_ARCH`, the command prompt's target platform, set by vsvarsall.
        VSCMD_ARG_TGT_ARCH = get_vs_var("VSCMD_ARG_TGT_ARCH")
        return VSCMD_ARG_TGT_ARCH_TO_INFO[VSCMD_ARG_TGT_ARCH].vs_platform

    @staticmethod
    def _ensure_cmake_supports_generator(generator: str) -> None:
        cmake_help = run("cmake", "--help")
        if generator not in cmake_help:
            logger.error(f"The used CMake version does not support generator '{generator}' - cannot proceed.")
            sys.exit(1)

    @staticmethod
    def _determine_generator_type(generator: str) -> GeneratorType:
        match generator:
            case "":
                return "EMPTY"
            case _ if "vs20" in generator:
                # E.g. 'vs2022-x64'.
                return "SHORTHAND"
            case _:
                if generator not in CMAKE_GENERATORS:
                    supported_generators = ", ".join(repr(g) for g in CMAKE_GENERATORS)
                    logger.error(
                        f"Invalid or unsupported CMake generator string passed: '{generator}' - cannot proceed."
                    )
                    logger.error(f"Supported CMake generator strings: {supported_generators}")
                    sys.exit(1)
                return "FULL_NAME"

    @staticmethod
    def _parse_generator_shorthand(
        generator: str, generator_type: GeneratorType
    ) -> tuple[str, VsPlatform | None, str | None, str | None]:
        # E.g. '2022-x64'.
        gen_shorthand = generator.replace("vs", "")

        vs_platform = None
        vs_toolset = None
        boost_toolset_ver = None

        # Order matters, e.g. "-arm64" also matches "-arm", so it must come last.
        for arch, info in VSCMD_ARG_TGT_ARCH_TO_INFO.items():
            if f"-{arch}" in gen_shorthand.lower():
                vs_platform = info.vs_platform

        for toolset, vc_ver in VS_TOOLSET_TO_VC_VER.items():
            if f"-{toolset}" in gen_shorthand:
                vs_toolset = toolset
                boost_toolset_ver = vc_ver

        vs_ver = gen_shorthand[:4]

        if generator_type == "SHORTHAND":
            for candidate, info in CMAKE_GENERATORS.items():
                if info.vs_ver == int(vs_ver):
                    generator = candidate
                    break
            else:
                supported_generators = ", ".join(repr(g) for g in CMAKE_GENERATORS)
                logger.error(f"Invalid or unsupported CMake generator string passed: '{generator}' - cannot proceed.")
                logger.error(f"Supported CMake generator strings: {supported_generators}")
                sys.exit(1)
        else:
            generator = VsCfg._generator_from_visual_studio_version()

        return generator, vs_platform, vs_toolset, boost_toolset_ver


def vs_cfg(generator: str | None, repo_root: Path) -> VsCfgResult:
    return VsCfg.build(generator, repo_root)
