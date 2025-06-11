# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from functools import reduce
from unittest import TestCase
from pytest import mark
from pytest import fixture
from uuid import uuid4
import string

from ifcopenshell.guid import compress
from ifcopenshell.guid import expand

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="session", autouse=False)
def check() -> TestCase:
    return TestCase()


# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

CHARS_IFC = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_$"
ZERO_16 = "0"
ZERO_64 = CHARS_IFC[0]

# ----------------------------------------------------------------
# ORIGINAL METHODS AND LOCAL CONSTANTS
# ----------------------------------------------------------------

# NOTE: written exactly as in legacy code

chars = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_$"


def legacy_compress(g: str) -> str:
    bs = [int(g[i : i + 2], 16) for i in range(0, len(g), 2)]

    def b64(v, l=4):
        return "".join([chars[(v // (64**i)) % 64] for i in range(l)][::-1])

    return "".join([b64(bs[0], 2)] + [b64((bs[i] << 16) + (bs[i + 1] << 8) + bs[i + 2]) for i in range(1, 16, 3)])


def legacy_expand(g: str) -> str:
    def b64(v):
        return reduce(lambda a, b: a * 64 + b, map(lambda c: chars.index(c), v))

    bs = [b64(g[0:2])]
    for i in range(5):
        d = b64(g[2 + 4 * i : 6 + 4 * i])
        bs += [(d >> (8 * (2 - j))) % 256 for j in range(3)]
    return "".join(["%02x" % b for b in bs])


# ----------------------------------------------------------------
# TESTS - behaviour of compress/expand
# ----------------------------------------------------------------


def test_expand_compress_SIMPLE_CASE(
    # fixtures
    check: TestCase,
):
    uuid_orig = "656d1ed085c54879b99026c1be57e3be"
    guid = compress(uuid_orig)
    uuid = expand(guid)
    check.assertEqual(uuid, uuid_orig, "compression then expansion should recover the original UUID")  # fmt: skip


@mark.parametrize(
    ("uuid_orig",),
    [(f"{n:0x}" * 32,) for n in range(16)],
)
def test_expand_compress_EDGE_CASES(
    # fixtures
    check: TestCase,
    # parameters
    uuid_orig: str,
):
    # check that decoding a compressed UUID works
    guid = compress(uuid_orig)
    uuid = expand(guid)
    check.assertEqual(uuid, uuid_orig, "compression then expansion should recover the original UUID")  # fmt: skip


@mark.skip(f"this can be run manually but should not be part of the CI/CD process")
def test_expand_compress_RANDOM(
    # fixtures
    check: TestCase,
):
    n = 100
    for _ in range(n):
        uuid_orig = uuid4().hex
        guid = compress(uuid_orig)
        uuid = expand(guid)
        check.assertEqual(uuid, uuid_orig, "compression then expansion should recover the original UUID")  # fmt: skip


@mark.parametrize(
    ("pref_hex", "pref_64"),
    [
        (f"{n:02x}", CHARS_IFC[n // 64] + CHARS_IFC[n % 64])
        for n in range(0x100)
    ]
)  # fmt: skip
def test_expand_compress_BEHAVIOUR_OF_PADDING(
    # fixtures
    check: TestCase,
    # parameters
    pref_hex: str,
    pref_64: str,
):
    uuid_special = pref_hex + ZERO_16 * 30
    guid_special = pref_64 + ZERO_64 * 20

    guid = compress(uuid_special)
    uuid = expand(guid_special)

    check.assertEqual(guid, guid_special, "IFC's hex to base64 expansion should isolate first two digits")  # fmt: skip
    check.assertEqual(uuid, uuid_special, "IFC's base64 to hex expansion should isolate first two digits")  # fmt: skip


# ----------------------------------------------------------------
# TESTS - validate behaviour against legacy implementation.
# ----------------------------------------------------------------


def test_compare_with_legacy_SIMPLE_CASE(
    # fixtures
    check: TestCase,
):
    uuid_orig = "656d1ed085c54879b99026c1be57e3be"
    guid = compress(uuid_orig)
    uuid = expand(guid)
    guid_old = legacy_compress(uuid_orig)
    uuid_old = legacy_expand(guid_old)
    check.assertEqual(guid, guid_old, "new compression method should yield the same base64 GUID")  # fmt: skip
    check.assertEqual(uuid, uuid_old, "new expansion method should yield the same hex UUID")  # fmt: skip


@mark.parametrize(
    ("uuid_orig",),
    [(f"{n:0x}" * 32,) for n in range(16)],
)
def test_compare_with_legacy_EDGE_CASES(
    # fixtures
    check: TestCase,
    # parameters
    uuid_orig: str,
):
    guid = compress(uuid_orig)
    uuid = expand(guid)
    guid_old = legacy_compress(uuid_orig)
    uuid_old = legacy_expand(guid_old)
    check.assertEqual(guid, guid_old, "new compression method should yield the same base64 GUID")  # fmt: skip
    check.assertEqual(uuid, uuid_old, "new expansion method should yield the same hex UUID")  # fmt: skip


@mark.skip(f"this can be run manually but should not be part of the CI/CD process")
def test_compare_with_legacy_RANDOM(
    # fixtures
    check: TestCase,
):
    n = 100
    for _ in range(n):
        uuid_orig = uuid4().hex
        guid = compress(uuid_orig)
        uuid = expand(guid)
        guid_old = legacy_compress(uuid_orig)
        uuid_old = legacy_expand(guid_old)
        check.assertEqual(guid, guid_old, "new compression method should yield the same base64 GUID")  # fmt: skip
        check.assertEqual(uuid, uuid_old, "new expansion method should yield the same hex UUID")  # fmt: skip
