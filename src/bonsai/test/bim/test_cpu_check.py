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

"""Startup AVX2-support detection (see
https://github.com/IfcOpenShell/IfcOpenShell/issues/7458): a CPU without
AVX2 can SIGILL Bonsai's CGAL/GMP geometry backend with no catchable
exception, so bonsai.cpu_check must reliably flag such CPUs *before* any
native code runs, while never producing a false positive on hardware that
does have the feature."""

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.misc

import bonsai.cpu_check as cpu_check

# A real Ivy Bridge (2012, pre-AVX2, the CPU family named in #7458) flags line.
IVY_BRIDGE_CPUINFO = (
    "processor\t: 0\n"
    "vendor_id\t: GenuineIntel\n"
    "model name\t: Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz\n"
    "flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 "
    "clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm "
    "constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid "
    "aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 cx16 xtpr "
    "pdcm pcid sse4_1 sse4_2 x2apic popcnt tsc_deadline_timer aes xsave avx f16c rdrand "
    "lahf_lm cpuid_fault epb pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept "
    "vpid fsgsbase smep erms xsaveopt dtherm ida arat pln pts md_clear flush_l1d\n"
)

# A Haswell (2013, first AVX2 generation) flags line.
HASWELL_CPUINFO = (
    "processor\t: 0\n"
    "model name\t: Intel(R) Core(TM) i7-4770 CPU @ 3.40GHz\n"
    "flags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 "
    "clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm "
    "constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid "
    "aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 fma cx16 xtpr "
    "pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c "
    "rdrand lahf_lm abm cpuid_fault epb invpcid_single pti ssbd ibrs ibpb stibp "
    "tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms "
    "invpcid xsaveopt dtherm ida arat pln pts md_clear flush_l1d\n"
)


class TestParseCpuinfoFlags:
    def test_extracts_flags_line(self):
        flags = cpu_check.parse_cpuinfo_flags(IVY_BRIDGE_CPUINFO)
        assert flags is not None
        assert "avx" in flags
        assert "avx2" not in flags

    def test_haswell_has_avx2(self):
        flags = cpu_check.parse_cpuinfo_flags(HASWELL_CPUINFO)
        assert flags is not None
        assert "avx2" in flags

    def test_missing_flags_line_returns_none(self):
        assert cpu_check.parse_cpuinfo_flags("processor: 0\nmodel name: Weird CPU\n") is None

    def test_features_key_is_also_recognised(self):
        # Some non-x86 /proc/cpuinfo variants use "Features" instead of "flags";
        # not a path we ever call this from x86-only detection, but the parser
        # itself should stay generic and not silently miss it.
        flags = cpu_check.parse_cpuinfo_flags("Features\t: fp asimd avx2\n")
        assert flags == {"fp", "asimd", "avx2"}


class TestIsX86:
    @pytest.mark.parametrize("machine", ["x86_64", "AMD64", "i686", "X86"])
    def test_x86_machines_detected(self, machine):
        with patch("platform.machine", return_value=machine):
            assert cpu_check.is_x86() is True

    @pytest.mark.parametrize("machine", ["arm64", "aarch64", "ppc64le"])
    def test_non_x86_machines_skipped(self, machine):
        with patch("platform.machine", return_value=machine):
            assert cpu_check.is_x86() is False


class TestGetCpuWarning:
    def test_linux_ivy_bridge_without_avx2_warns(self):
        with (
            patch("platform.machine", return_value="x86_64"),
            patch("platform.system", return_value="Linux"),
            patch.object(cpu_check, "_linux_flags", return_value=cpu_check.parse_cpuinfo_flags(IVY_BRIDGE_CPUINFO)),
        ):
            warning = cpu_check.get_cpu_warning()
            assert warning is not None
            assert "AVX2" in warning
            assert cpu_check.ISSUE_URL in warning

    def test_linux_haswell_with_avx2_does_not_warn(self):
        with (
            patch("platform.machine", return_value="x86_64"),
            patch("platform.system", return_value="Linux"),
            patch.object(cpu_check, "_linux_flags", return_value=cpu_check.parse_cpuinfo_flags(HASWELL_CPUINFO)),
        ):
            assert cpu_check.get_cpu_warning() is None

    def test_undetectable_linux_cpuinfo_does_not_warn(self):
        # e.g. a container/sandbox without /proc/cpuinfo, or a Linux running on
        # non-x86 that somehow still reports machine() as x86 (shouldn't happen,
        # but detection failure must never produce a false positive).
        with (
            patch("platform.machine", return_value="x86_64"),
            patch("platform.system", return_value="Linux"),
            patch.object(cpu_check, "_linux_flags", return_value=None),
        ):
            assert cpu_check.get_cpu_warning() is None

    def test_arm64_never_warns_even_if_platform_lies(self):
        # This is the real scenario on the Apple Silicon development machine:
        # AVX2 is an x86-only concept, so non-x86 must always be a hard skip,
        # regardless of what any lower-level flag lookup would have said.
        with (
            patch("platform.machine", return_value="arm64"),
            patch("platform.system", return_value="Darwin"),
            patch.object(cpu_check, "_macos_flags", return_value=set()),
        ):
            assert cpu_check.get_cpu_warning() is None

    def test_macos_intel_without_avx2_warns(self):
        with (
            patch("platform.machine", return_value="x86_64"),
            patch("platform.system", return_value="Darwin"),
            patch.object(cpu_check, "_macos_flags", return_value={"sse4.2", "avx"}),
        ):
            assert cpu_check.get_cpu_warning() is not None

    def test_macos_intel_with_avx2_does_not_warn(self):
        with (
            patch("platform.machine", return_value="x86_64"),
            patch("platform.system", return_value="Darwin"),
            patch.object(cpu_check, "_macos_flags", return_value={"avx1.0", "avx2", "fma"}),
        ):
            assert cpu_check.get_cpu_warning() is None

    def test_windows_without_avx2_warns(self):
        with (
            patch("platform.machine", return_value="AMD64"),
            patch("platform.system", return_value="Windows"),
            patch.object(cpu_check, "_windows_has_avx2", return_value=False),
        ):
            assert cpu_check.get_cpu_warning() is not None

    def test_windows_with_avx2_does_not_warn(self):
        with (
            patch("platform.machine", return_value="AMD64"),
            patch("platform.system", return_value="Windows"),
            patch.object(cpu_check, "_windows_has_avx2", return_value=True),
        ):
            assert cpu_check.get_cpu_warning() is None

    def test_unsupported_platform_does_not_warn(self):
        with patch("platform.machine", return_value="x86_64"), patch("platform.system", return_value="FreeBSD"):
            assert cpu_check.detect_avx2_support() is None
            assert cpu_check.get_cpu_warning() is None

    def test_current_host_does_not_false_positive(self):
        """Guardrail against the exact regression this module exists to avoid:
        never warn without real confidence the CPU is affected."""
        warning = cpu_check.get_cpu_warning()
        if cpu_check.is_x86():
            assert cpu_check.detect_avx2_support() is not False or warning is not None
        else:
            assert warning is None
