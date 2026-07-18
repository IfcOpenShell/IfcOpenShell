# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Best-effort startup check for a CPU feature required by Bonsai's native
geometry backend. See https://github.com/IfcOpenShell/IfcOpenShell/issues/7458.

Must not import bpy or any ifcopenshell/Bonsai native module, so it stays
importable (and unit testable) on every platform before the risky native
code is ever touched.
"""

from __future__ import annotations

import platform
import subprocess
from typing import Optional

# AVX2 is the only CPU feature currently known to be a real crash risk (GMP,
# linked in by the CGAL geometry backend, historically shipped without
# `--enable-fat`, see nix/build-all.py). Neither CGAL itself nor OpenCASCADE
# nor IfcOpenShell's own C++ code set any -march/-mavx-style compiler flags,
# so AVX2-via-GMP is the only confirmed unconditional ISA requirement today.
REQUIRED_FEATURE = "avx2"

ISSUE_URL = "https://github.com/IfcOpenShell/IfcOpenShell/issues/7458"

# platform.machine() values that mean "this is an x86/x86_64 CPU". AVX2 is
# x86-specific, so anything else (arm64, aarch64, ppc64le, ...) is skipped.
_X86_MACHINES = {"x86_64", "amd64", "i386", "i486", "i586", "i686", "x86"}


def is_x86() -> bool:
    return platform.machine().lower() in _X86_MACHINES


def parse_cpuinfo_flags(cpuinfo_text: str) -> Optional[set[str]]:
    """Parse the flag set out of ``/proc/cpuinfo``-style text.

    Split out from the file read so the parsing itself can be unit tested
    against crafted text without touching the filesystem.
    """
    for line in cpuinfo_text.splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            continue
        if key.strip().lower() in ("flags", "features"):
            return set(value.lower().split())
    return None


def _linux_flags() -> Optional[set[str]]:
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError:
        return None
    return parse_cpuinfo_flags(content)


def _macos_flags() -> Optional[set[str]]:
    """Apple Intel exposes ISA flags via sysctl (Apple Silicon has no such
    keys and is filtered out earlier by is_x86())."""
    flags: set[str] = set()
    found_any = False
    for name in ("machdep.cpu.features", "machdep.cpu.leaf7_features"):
        try:
            result = subprocess.run(
                ["sysctl", "-n", name],
                capture_output=True,
                text=True,
                timeout=2,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode != 0:
            continue
        found_any = True
        flags.update(result.stdout.lower().split())
    return flags if found_any else None


def _windows_has_avx2() -> Optional[bool]:
    """Windows has no /proc/cpuinfo. IsProcessorFeaturePresent with
    PF_AVX2_INSTRUCTIONS_AVAILABLE (40) is the officially documented WinAPI
    call for this, added in the Windows 10 SDK. On editions too old to know
    about the flag it always reports False, indistinguishable from a
    genuinely missing feature; see detect_avx2_support()."""
    try:
        import ctypes

        PF_AVX2_INSTRUCTIONS_AVAILABLE = 40
        return bool(ctypes.windll.kernel32.IsProcessorFeaturePresent(PF_AVX2_INSTRUCTIONS_AVAILABLE))
    except Exception:
        return None


def detect_avx2_support() -> Optional[bool]:
    """True/False if determined with confidence, None if undetermined.

    Only meaningful when is_x86() is True. Returns None (i.e. "don't know")
    whenever a platform-specific lookup fails, so callers can treat unknown
    the same as "don't warn" and never produce a false positive.
    """
    system = platform.system()
    if system == "Linux":
        flags = _linux_flags()
    elif system == "Darwin":
        flags = _macos_flags()
    elif system == "Windows":
        return _windows_has_avx2()
    else:
        return None
    if flags is None:
        return None
    return REQUIRED_FEATURE in flags


def get_cpu_warning() -> Optional[str]:
    """Return a user-facing warning string if this CPU is likely to SIGILL
    Bonsai's CGAL/GMP geometry backend, otherwise None.

    Deliberately conservative: any ambiguity (non-x86, detection failed,
    unsupported platform) resolves to "don't warn".
    """
    if not is_x86():
        return None
    has_feature = detect_avx2_support()
    if has_feature is not False:
        return None
    return (
        "This CPU does not support the AVX2 instruction set. Bonsai's geometry engine "
        "(the CGAL/GMP-based 'Hybrid CGAL-OCC' and 'CGAL' options) can crash Blender "
        "outright with no error message (SIGILL) on such CPUs when opening IFC files. "
        "To avoid this, in the Scene Properties > Bonsai tab > Current Project panel, "
        "enable Advanced and set Geometry Library to 'OpenCASCADE' before loading a project, "
        f"or build IfcOpenShell from source for your CPU. See {ISSUE_URL} for details."
    )
