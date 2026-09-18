# This file was generated with the assistance of an AI coding tool.
"""Build-time safeguard for the exec bit on the bundled pyradiance binaries.

pyradiance ships its ``bin/`` binaries with the exec bit set inside the wheel.
Bonsai bundles that wheel unchanged, so the packaged artifact is only correct as
long as upstream keeps setting it. If a future pyradiance release (or a new
platform wheel) ever regresses this, a permission-preserving install path (eg. a
distro/AUR package unpacking the wheels system-wide onto a read-only filesystem)
would end up with non-executable binaries and no way to fix them at runtime.

This script fails the build early in that case, in the same spirit as the other
wheel safeguards in the Makefile. It is a read-only check: it never mutates the
wheel.
"""

import glob
import os
import stat
import sys
import zipfile

# Files under bin/ that carry a Windows executable extension do not rely on the
# unix exec bit, so they are not checked.
WINDOWS_EXECUTABLE_SUFFIXES = (".exe", ".bat", ".cmd", ".dll", ".pyd")


def non_executable_binaries(wheel_path: str) -> list[str]:
    offenders = []
    with zipfile.ZipFile(wheel_path) as zip_file:
        for info in zip_file.infolist():
            name = info.filename
            if "/bin/" not in name or name.endswith("/"):
                continue
            if name.lower().endswith(WINDOWS_EXECUTABLE_SUFFIXES):
                continue
            mode = (info.external_attr >> 16) & 0xFFFF
            if not mode & stat.S_IXUSR:
                offenders.append(name)
    return offenders


def main(wheels_dir: str) -> int:
    wheels = glob.glob(os.path.join(wheels_dir, "pyradiance-*.whl"))
    if not wheels:
        print(f"No pyradiance wheel found in '{wheels_dir}'.")
        return 1

    ok = True
    for wheel in wheels:
        offenders = non_executable_binaries(wheel)
        if offenders:
            ok = False
            print(f"pyradiance binaries missing the exec bit in '{os.path.basename(wheel)}':")
            for name in offenders:
                print(f"  {name}")

    if not ok:
        print(
            "Error: bundled pyradiance binaries are not executable. "
            "The packaged extension must ship them with the exec bit set."
        )
        return 1

    print("pyradiance binaries are executable.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_pyradiance_exec_bits.py <wheels_dir>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
