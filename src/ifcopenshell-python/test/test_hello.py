# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from unittest import TestCase
from pytest import fixture

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="session", autouse=False)
def check() -> TestCase:
    return TestCase()


# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_expand_compress_SIMPLE_CASE(
    # fixtures
    check: TestCase,
):
    check.assertEqual(0 + 0, 0, "hello world test should not fail")  # fmt: skip
