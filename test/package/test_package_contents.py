"""Package tests that fail when a shared library is packaged more than once, or not at all.

A versioned shared library is installed as a chain of symlinks (`libTKernel.so ->
libTKernel.so.7.8 -> libTKernel.so.7.8.1`).  A wheel can't hold symlinks, so a package
that carries the chain ends up with every link as one more full copy of the library:
the OCCT toolkits alone once made the Linux wheel 55 MB larger than it had to be.  The
packaging therefore stages each library once, under the name the loader looks it up by,
and leaves out the dependency libraries that nothing links to.

These tests are meant to run against the *packaged* binaries in the release build
workflows (see run_against_package.py).
"""

import hashlib
import os
from collections import defaultdict
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import pytest

W = ifcopenshell.ifcopenshell_wrapper
PACKAGE_DIR = Path(ifcopenshell.__file__).parent
HERE = os.path.dirname(os.path.abspath(__file__))
# A fixture from the main tree, not from the `test/input` submodule, so a bare checkout works.
FIXTURE = os.environ.get("IFCOPENSHELL_PACKAGE_TEST_FIXTURE") or os.path.join(
    HERE, "..", "..", "src", "ifcopenshell-python", "test", "fixtures", "ColumnPSetsOfSets.ifc"
)


def shared_libraries() -> list[Path]:
    def is_shared_library(path: Path) -> bool:
        name = path.name.lower()
        return name.endswith((".so", ".dylib", ".dll", ".pyd")) or ".so." in name

    return [path for path in PACKAGE_DIR.iterdir() if is_shared_library(path)]


def test_no_symlinked_libraries():
    assert [path.name for path in shared_libraries() if path.is_symlink()] == []


def test_every_library_is_packaged_once():
    names_by_content = defaultdict(list)
    for path in shared_libraries():
        names_by_content[hashlib.sha256(path.read_bytes()).hexdigest()].append(path.name)
    assert [sorted(names) for names in names_by_content.values() if len(names) > 1] == []


@pytest.mark.parametrize("extension", ["stp", "igs"])
def test_opencascade_serializer(extension, tmp_path):
    """Of all plug-ins these two link to the most OCCT toolkits (data exchange pulls in the
    application framework and visualization), so they're the first to miss a left out one."""
    model = ifcopenshell.open(FIXTURE)
    settings = ifcopenshell.geom.settings()
    settings.set("iterator-output", W.NATIVE)
    output = tmp_path / f"out.{extension}"
    serializer = getattr(ifcopenshell.geom.serializers, extension)(str(output), settings)
    serializer.setFile(model)
    serializer.writeHeader()
    it = ifcopenshell.geom.iterator(settings, model)
    assert it.initialize()
    while True:
        serializer.write(it.get())
        if not it.next():
            break
    serializer.finalize()
    assert output.stat().st_size > 0
