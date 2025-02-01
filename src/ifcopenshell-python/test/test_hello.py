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


def test_hello(
    # fixtures
    check: TestCase,
):
    check.assertEqual(1 + 1, 2, "hello world canary test")
